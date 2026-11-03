"""Phase D target networks, families F1-F3: small MLP classifiers with an injected, measurable defect.

    python -m wse.targets generate --family F2 --split dev --n 64 --out <dir>      (admin)

Targets are benchmark items. Per the Phase D design they may be built by ordinary means: the base classifier is trained
here with plain numpy full-batch Adam on synthetic data. Only the *editors* and their outputs are restricted to direct
weight edits. Everything is deterministic from (family, split, index): seed = hash of those fields.

Network: x (20) -> relu(x W1 + b1) (32) -> relu(h1 W2 + b2) (24) -> h2 W3 + b3 (6 logits); 1,644 parameters.
Data: 6 classes, each a mixture of 2 Gaussian blobs in 20-d with a random linear warp; train 3,000, probe 192,
test 3,000 (disjoint draws).

Defects (applied to a copy of the trained net; the clean net is kept only for the ceiling):
  F1 dead-units   : k in {2..4} of the most important first-layer units (largest probe-set accuracy drop when
                    ablated alone) killed with b1[j] = -40 (ReLU never fires).
  F2 swap-output  : two output classes a, b swapped (columns a, b of W3 and entries a, b of b3).
  F3 bias-shift   : one output bias b3[c] += s, with s = a random 40-80th percentile of the probe-set margin
                    (max logit - logit c), rounded to 0.01 (class c over-predicted).
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

D_IN, H1, H2, N_CLS = 20, 32, 24, 6
SHAPES = {"W1": (D_IN, H1), "b1": (H1,), "W2": (H1, H2), "b2": (H2,), "W3": (H2, N_CLS), "b3": (N_CLS,)}
FAMILIES = ("F1", "F2", "F3")
SPLIT_CODE = {"dev": 1, "test": 2, "pilot": 3}


def seed_of(family, split, index):
    h = hashlib.sha256(f"wse-target/{family}/{split}/{index}".encode()).digest()
    return int.from_bytes(h[:8], "little")


def forward(w, x, return_hidden=False):
    h1 = np.maximum(0, x @ w["W1"] + w["b1"])
    h2 = np.maximum(0, h1 @ w["W2"] + w["b2"])
    z = h2 @ w["W3"] + w["b3"]
    return (z, h1, h2) if return_hidden else z


def accuracy(w, x, y):
    return float((forward(w, x).argmax(1) == y).mean())


def make_data(rng):
    centers = rng.normal(0, 1.0, (N_CLS, 2, D_IN)) * 0.75
    warp = np.eye(D_IN) + rng.normal(0, 0.25, (D_IN, D_IN))

    def draw(n):
        y = rng.integers(0, N_CLS, n)
        c = centers[y, rng.integers(0, 2, n)]
        x = (c + rng.normal(0, 1.0, (n, D_IN))) @ warp
        return x.astype(np.float32), y

    return draw(3000), draw(192), draw(3000)


def train(rng, x, y, steps=600, lr=0.01):
    """Plain full-batch Adam on cross-entropy (target construction only; never used on editor outputs)."""
    w = {"W1": rng.normal(0, np.sqrt(2 / D_IN), SHAPES["W1"]), "b1": np.zeros(H1),
         "W2": rng.normal(0, np.sqrt(2 / H1), SHAPES["W2"]), "b2": np.zeros(H2),
         "W3": rng.normal(0, np.sqrt(1 / H2), SHAPES["W3"]), "b3": np.zeros(N_CLS)}
    w = {k: v.astype(np.float64) for k, v in w.items()}
    m = {k: np.zeros_like(v) for k, v in w.items()}
    v2 = {k: np.zeros_like(v) for k, v in w.items()}
    x = x.astype(np.float64)
    oh = np.eye(N_CLS)[y]
    for t in range(1, steps + 1):
        z, h1, h2 = forward(w, x, True)
        p = np.exp(z - z.max(1, keepdims=True))
        p /= p.sum(1, keepdims=True)
        dz = (p - oh) / len(x)
        g = {"W3": h2.T @ dz, "b3": dz.sum(0)}
        dh2 = (dz @ w["W3"].T) * (h2 > 0)
        g["W2"], g["b2"] = h1.T @ dh2, dh2.sum(0)
        dh1 = (dh2 @ w["W2"].T) * (h1 > 0)
        g["W1"], g["b1"] = x.T @ dh1, dh1.sum(0)
        for k in w:
            m[k] = 0.9 * m[k] + 0.1 * g[k]
            v2[k] = 0.999 * v2[k] + 0.001 * g[k] ** 2
            w[k] -= lr * (m[k] / (1 - 0.9 ** t)) / (np.sqrt(v2[k] / (1 - 0.999 ** t)) + 1e-8)
    return {k: v.astype(np.float32) for k, v in w.items()}


def damage(family, rng, w, xp):
    d = {k: v.copy() for k, v in w.items()}
    if family == "F1":
        base = (forward(w, xp).argmax(1))
        drop = []
        for u in range(H1):
            t = {kk: vv.copy() for kk, vv in w.items()}
            t["b1"][u] = -40.0
            drop.append(float((forward(t, xp).argmax(1) != base).mean()))
        k = int(rng.integers(2, 5))
        top = np.argsort(drop)[::-1][:8]
        units = sorted(int(u) for u in rng.choice(top, size=k, replace=False))
        d["b1"][units] = -40.0
        truth = {"units": units, "original_b1": [float(w["b1"][u]) for u in units]}
    elif family == "F2":
        a, b = sorted(int(c) for c in rng.choice(N_CLS, 2, replace=False))
        d["W3"][:, [a, b]] = d["W3"][:, [b, a]]
        d["b3"][[a, b]] = d["b3"][[b, a]]
        truth = {"classes": [a, b]}
    elif family == "F3":
        c = int(rng.integers(0, N_CLS))
        z = forward(w, xp)
        s = round(float(np.percentile(z.max(1) - z[:, c], rng.uniform(40, 80))), 2)
        d["b3"][c] += s
        truth = {"class": c, "shift": s}
    else:
        raise ValueError(family)
    return d, truth


def build(family, split, index):
    seed = seed_of(family, split, index)
    rng = np.random.default_rng(seed)
    (xtr, ytr), (xp, yp), (xte, yte) = make_data(rng)
    clean = train(rng, xtr, ytr)
    damaged, truth = damage(family, rng, clean, xp)
    return {"id": f"{family}-{split}-{index:04d}", "family": family, "split": split, "index": index, "seed": seed,
            "clean": clean, "damaged": damaged, "truth": truth, "probe": (xp, yp), "test": (xte, yte),
            "ceiling": accuracy(clean, xte, yte), "damaged_acc": accuracy(damaged, xte, yte)}


def score(inst, weights):
    """Held-out score of an edited copy: accuracy on the instance's test set, and recovery toward the ceiling."""
    xte, yte = inst["test"]
    acc = accuracy(weights, xte, yte)
    gap = inst["ceiling"] - inst["damaged_acc"]
    return {"acc": acc, "delta": acc - inst["damaged_acc"], "recovery": (acc - inst["damaged_acc"]) / gap if gap > 1e-9 else None}


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    g = sp.add_parser("generate")
    g.add_argument("--family", choices=FAMILIES, required=True)
    g.add_argument("--split", choices=list(SPLIT_CODE), required=True)
    g.add_argument("--n", type=int, required=True)
    g.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(a.n):
        inst = build(a.family, a.split, i)
        np.savez(out / f"{inst['id']}.npz", **{f"clean_{k}": v for k, v in inst["clean"].items()},
                 **{f"damaged_{k}": v for k, v in inst["damaged"].items()})
        rows.append({k: inst[k] for k in ("id", "family", "split", "index", "seed", "truth", "ceiling", "damaged_acc")})
        print(json.dumps(rows[-1]))
    (out / f"manifest-{a.family}-{a.split}.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
