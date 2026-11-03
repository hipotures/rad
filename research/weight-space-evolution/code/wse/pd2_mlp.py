"""Phase D benchmark v2, families F1-F3: MLP classifiers with varied architecture and injected, invertible defects.

Every instance is deterministic from its seed. The clean network is trained here with plain numpy full-batch Adam
(target construction only; editors and their outputs never use gradients). The clean network is the recovery
reference: every defect is an exact (or float-rounding-exact) invertible transformation, and the oracle edit that
inverts it is generated with the instance and must reach recovery >= 0.95 or the draw is rejected.

Architecture per instance: inputs in {16, 20, 24}, 2 or 3 ReLU hidden layers with widths in {24, 32, 48}, classes in
{5, 6, 8}; tensors W1, b1, ..., Wn, bn (Wk: [in, out]); logits = h_{n-1} @ Wn + bn.
Data: class-conditional Gaussian mixtures (2 blobs per class) under a random linear warp; train 3,000, probe 256,
test 3,000 (independent draws).

Subtypes (core = dev/select/test splits; held-out = transfer split only):
  F1 dead/disabled units   core: dead_bias (unit killed or partially suppressed through its bias),
                                 in_scale (incoming weights and bias scaled by 1/m: unit fires as often but weakly),
                                 out_mute (outgoing row scaled by 1/m: unit computes normally but is ignored),
                                 mixed (2-4 defects of the three kinds, possibly in different layers)
                           held-out: sign_flip (incoming weights and bias negated: unit fires on the complement)
  F2 output mapping        core: out_perm (permutation of output classes: swap, 3-cycle, double swap, 4-cycle),
                                 out_perm_w (permutation of output weight columns only; biases stay),
                                 hidden_swap (two last-hidden units' outgoing rows exchanged)
                           held-out: in_swap (two input features' rows of W1 exchanged)
  F3 bias/activation       core: out_bias (one output bias raised; v1 F3 kept), out_bias_pair (one raised, one
                                 lowered), hidden_bias (1-3 hidden units' biases raised: always-on units),
                                 logit_scale (one class's output column and bias multiplied by m)
                           held-out: layer_bias (a whole hidden layer's bias vector shifted by one constant)
"""
import numpy as np

SUBTYPES = {"F1": (["dead_bias", "in_scale", "out_mute", "mixed"], ["sign_flip"]),
            "F2": (["out_perm", "out_perm_w", "hidden_swap"], ["in_swap"]),
            "F3": (["out_bias", "out_bias_pair", "hidden_bias", "logit_scale"], ["layer_bias"])}
MIN_GAP, MIN_CEIL, MIN_ORACLE = 0.10, 0.60, 0.95
LIMITS = {"max_statements": 16, "max_entries": 512}


# ------------------------------------------------------------------------------------------------ network
def n_layers(w):
    return sum(1 for k in w if k.startswith("W"))


def forward(w, x, hidden=False):
    hs, h = [], x
    L = n_layers(w)
    for i in range(1, L):
        h = np.maximum(0, h @ w[f"W{i}"] + w[f"b{i}"])
        hs.append(h)
    z = h @ w[f"W{L}"] + w[f"b{L}"]
    return (z, hs) if hidden else z


def accuracy(w, x, y):
    return float((forward(w, x).argmax(1) == y).mean())


def make_arch(rng):
    d_in = int(rng.choice([16, 20, 24]))
    hid = [int(rng.choice([24, 32, 48])) for _ in range(int(rng.choice([2, 3])))]
    return {"d_in": d_in, "hidden": hid, "classes": int(rng.choice([5, 6, 8]))}


def make_data(rng, arch):
    d, c = arch["d_in"], arch["classes"]
    centers = rng.normal(0, 1.0, (c, 2, d)) * rng.uniform(0.65, 0.9)
    warp = np.eye(d) + rng.normal(0, 0.25, (d, d))

    def draw(n):
        y = rng.integers(0, c, n)
        x = (centers[y, rng.integers(0, 2, n)] + rng.normal(0, 1.0, (n, d))) @ warp
        return x.astype(np.float32), y
    return draw(3000), draw(256), draw(3000)


def train(rng, arch, x, y, steps=800, lr=0.01):
    """Full-batch Adam on cross-entropy (target construction only)."""
    sizes = [arch["d_in"], *arch["hidden"], arch["classes"]]
    L = len(sizes) - 1
    w = {}
    for i in range(1, L + 1):
        w[f"W{i}"] = rng.normal(0, np.sqrt((1 if i == L else 2) / sizes[i - 1]), (sizes[i - 1], sizes[i]))
        w[f"b{i}"] = np.zeros(sizes[i])
    m = {k: np.zeros_like(v) for k, v in w.items()}
    v2 = {k: np.zeros_like(v) for k, v in w.items()}
    x = x.astype(np.float64)
    oh = np.eye(sizes[-1])[y]
    for t in range(1, steps + 1):
        acts = [x]
        for i in range(1, L):
            acts.append(np.maximum(0, acts[-1] @ w[f"W{i}"] + w[f"b{i}"]))
        z = acts[-1] @ w[f"W{L}"] + w[f"b{L}"]
        p = np.exp(z - z.max(1, keepdims=True))
        p /= p.sum(1, keepdims=True)
        dz = (p - oh) / len(x)
        g = {}
        for i in range(L, 0, -1):
            g[f"W{i}"], g[f"b{i}"] = acts[i - 1].T @ dz, dz.sum(0)
            if i > 1:
                dz = (dz @ w[f"W{i}"].T) * (acts[i - 1] > 0)
        for k in w:
            m[k] = 0.9 * m[k] + 0.1 * g[k]
            v2[k] = 0.999 * v2[k] + 0.001 * g[k] ** 2
            w[k] -= lr * (m[k] / (1 - 0.9 ** t)) / (np.sqrt(v2[k] / (1 - 0.999 ** t)) + 1e-8)
    return {k: v.astype(np.float32) for k, v in w.items()}


# ------------------------------------------------------------------------------------------------ defects
def _f(v):
    return f"{v:.6g}"


def unit_importance(w, xp, layer):
    """Fraction of probe predictions changed when hidden unit j of `layer` is silenced (its outgoing row zeroed)."""
    base = forward(w, xp).argmax(1)
    out = []
    for j in range(w[f"b{layer}"].shape[0]):
        t = dict(w)
        t[f"W{layer + 1}"] = w[f"W{layer + 1}"].copy()
        t[f"W{layer + 1}"][j] = 0
        out.append(float((forward(t, xp).argmax(1) != base).mean()))
    return np.array(out)


def _pick_units(rng, w, xp, layer, k, used):
    imp = unit_importance(w, xp, layer)
    order = [int(u) for u in np.argsort(imp)[::-1] if (layer, int(u)) not in used][:12]
    return sorted(int(u) for u in rng.choice(order, size=min(k, len(order)), replace=False))


def _unit_defect(rng, d, w, xp, kind, layer, j):
    """Apply one unit defect in place on d; return (truth, oracle statements)."""
    Wi, bi, Wo = f"W{layer}", f"b{layer}", f"W{layer + 1}"
    if kind == "dead_bias":
        pre = xp.astype(np.float64)
        for i in range(1, layer):
            pre = np.maximum(0, pre @ w[f"W{i}"] + w[f"b{i}"])
        a = pre @ w[Wi][:, j]                      # pre-activation without bias
        if rng.random() < 0.5:                     # full kill
            nb = -float(np.round(np.abs(a).max() * rng.uniform(1.5, 3.0) + 1, 2))
        else:                                      # partial: unit active on only 2-8% of probe inputs
            nb = -float(np.round(np.quantile(a, 1 - rng.uniform(0.02, 0.08)), 3))
        orig = round(float(w[bi][j]), 4)          # oracle restores the bias to 4 decimals (acceptance re-checks)
        d[bi][j] = nb
        return ({"kind": kind, "layer": layer, "unit": j, "orig_bias": float(w[bi][j]), "new_bias": nb},
                [f"{bi}[{j}] = {orig}"])
    if kind in ("in_scale", "sign_flip"):
        m = -1 if kind == "sign_flip" else int(rng.choice([5, 8, 10, 16, 20]))
        d[Wi][:, j] = d[Wi][:, j] * np.float32(1 / m)
        d[bi][j] = d[bi][j] * np.float32(1 / m)
        return ({"kind": kind, "layer": layer, "unit": j, "factor": 1 / m},
                [f"{Wi}[:, {j}] *= {m}", f"{bi}[{j}] *= {m}"])
    if kind == "out_mute":
        m = int(rng.choice([5, 8, 10, 16, 20]))
        d[Wo][j, :] = d[Wo][j, :] * np.float32(1 / m)
        return ({"kind": kind, "layer": layer, "unit": j, "factor": 1 / m}, [f"{Wo}[{j}, :] *= {m}"])
    raise ValueError(kind)


def _perm_swaps(perm):
    """Transpositions (a, b) that turn the permuted order back into identity (applied sequentially)."""
    p, sw = list(perm), []
    for i in range(len(p)):
        while p[i] != i:
            j = p[i]
            p[i], p[j] = p[j], p[i]
            sw.append((i, j))
    return sw


def damage(fam, sub, rng, w, data):
    """Return (damaged weights, truth, oracle edit text)."""
    (xp, yp) = data["probe"]
    L = n_layers(w)
    d = {k: v.copy() for k, v in w.items()}
    Wo, bo = f"W{L}", f"b{L}"
    C = w[bo].shape[0]
    truth, ora = [], []
    if fam == "F1":
        if sub == "mixed":
            n = int(rng.integers(2, 5))
            kinds = [str(rng.choice(["dead_bias", "in_scale", "out_mute"])) for _ in range(n)]
            if len(set(kinds)) == 1:
                kinds[0] = [k for k in ("dead_bias", "in_scale", "out_mute") if k != kinds[1]][int(rng.integers(2))]
        else:
            kinds = [sub] * (int(rng.integers(2, 5)) if sub == "out_mute" else int(rng.integers(1, 4)))
        used = set()
        for kind in kinds:
            layer = int(rng.integers(1, L))
            j = _pick_units(rng, w, xp, layer, 1, used)[0]
            used.add((layer, j))
            t, o = _unit_defect(rng, d, w, xp, kind, layer, j)
            truth.append(t)
            ora += o
    elif fam == "F2":
        if sub in ("out_perm", "out_perm_w"):
            kind = str(rng.choice(["swap", "cycle3", "double_swap", "cycle4"] if C >= 4 else ["swap", "cycle3"]))
            cls = [int(c) for c in rng.choice(C, {"swap": 2, "cycle3": 3, "double_swap": 4, "cycle4": 4}[kind], replace=False)]
            perm = list(range(C))
            if kind == "double_swap":
                perm[cls[0]], perm[cls[1]] = cls[1], cls[0]
                perm[cls[2]], perm[cls[3]] = cls[3], cls[2]
            else:
                for i, c in enumerate(cls):
                    perm[c] = cls[(i + 1) % len(cls)]
            d[Wo] = w[Wo][:, perm].copy()
            if sub == "out_perm":
                d[bo] = w[bo][perm].copy()
            for a, b in _perm_swaps(perm):
                ora.append(f"swap {Wo}[:, {a}] {Wo}[:, {b}]")
                if sub == "out_perm":
                    ora.append(f"swap {bo}[{a}] {bo}[{b}]")
            truth.append({"kind": kind, "perm": perm, "bias_permuted": sub == "out_perm"})
        elif sub == "hidden_swap":
            i, j = _pick_units(rng, w, xp, L - 1, 2, set())
            d[Wo][[i, j]] = w[Wo][[j, i]]
            truth.append({"rows": [i, j]})
            ora.append(f"swap {Wo}[{i}, :] {Wo}[{j}, :]")
        elif sub == "in_swap":
            imp = np.abs(w["W1"]).sum(1)
            i, j = sorted(int(u) for u in rng.choice(np.argsort(imp)[::-1][:8], 2, replace=False))
            d["W1"][[i, j]] = w["W1"][[j, i]]
            truth.append({"rows": [i, j]})
            ora.append(f"swap W1[{i}, :] W1[{j}, :]")
    elif fam == "F3":
        z, hs = forward(w, xp, True)
        if sub in ("out_bias", "out_bias_pair"):
            c = int(rng.integers(0, C))
            s = round(float(np.percentile(z.max(1) - z[:, c], rng.uniform(40, 80))), 2)
            d[bo][c] += np.float32(s)
            truth.append({"class": c, "shift": s})
            ora.append(f"{bo}[{c}] -= {s}")
            if sub == "out_bias_pair":
                c2 = int(rng.choice([k for k in range(C) if k != c]))
                s2 = round(float(z[:, c2].std() * rng.uniform(1.0, 2.5)), 2)
                d[bo][c2] -= np.float32(s2)
                truth.append({"class": c2, "shift": -s2})
                ora.append(f"{bo}[{c2}] += {s2}")
        elif sub == "hidden_bias":
            layer = int(rng.integers(1, L))
            units = _pick_units(rng, w, xp, layer, int(rng.integers(1, 4)), set())
            pre = xp.astype(np.float64)
            for i in range(1, layer):
                pre = np.maximum(0, pre @ w[f"W{i}"] + w[f"b{i}"])
            pre = pre @ w[f"W{layer}"] + w[f"b{layer}"]
            for u in units:
                s = round(float(pre[:, u].std() * rng.uniform(3, 6)), 2)
                d[f"b{layer}"][u] += np.float32(s)
                truth.append({"layer": layer, "unit": u, "shift": s})
                ora.append(f"b{layer}[{u}] -= {s}")
        elif sub == "logit_scale":
            c = int(rng.integers(0, C))
            m = int(rng.choice([2, 4]))
            s = round(float(np.percentile(z.max(1) - z[:, c], rng.uniform(15, 40))), 2)
            d[Wo][:, c] *= np.float32(m)
            d[bo][c] += np.float32(s)
            truth.append({"class": c, "factor": m, "shift": s})
            ora += [f"{Wo}[:, {c}] *= {1 / m}", f"{bo}[{c}] -= {s}"]
        elif sub == "layer_bias":
            layer = int(rng.integers(1, L))
            pre = hs[layer - 1]
            s = round(float(pre.std() * rng.uniform(1.0, 2.5)) * float(rng.choice([-1, 1])), 2)
            d[f"b{layer}"] += np.float32(s)
            truth.append({"layer": layer, "shift": s})
            ora.append(f"b{layer}[:] -= {s}" if s > 0 else f"b{layer}[:] += {-s}")
    else:
        raise ValueError(fam)
    return d, truth, "\n".join(ora)


# ------------------------------------------------------------------------------------------------ instance API
def build(fam, sub, seed):
    """Build one accepted instance (resampling the defect draw up to 30 times). Returns dict or raises."""
    from . import edit_dsl as E
    rng = np.random.default_rng(seed)
    for attempt in range(6):
        arch = make_arch(rng)
        (xtr, ytr), (xp, yp), (xte, yte) = make_data(rng, arch)
        clean = train(rng, arch, xtr, ytr)
        ceil = accuracy(clean, xte, yte)
        if ceil >= MIN_CEIL:
            break
    else:
        raise RuntimeError("no trainable data draw")
    data = {"probe": (xp, yp), "test": (xte, yte)}
    for tries in range(30):
        dmg, truth, ora = damage(fam, sub, rng, clean, data)
        dacc = accuracy(dmg, xte, yte)
        if ceil - dacc < MIN_GAP:
            continue
        r = E.run(dmg, ora, **LIMITS)
        if not r["valid"]:
            raise RuntimeError(f"oracle edit invalid: {r['error']}")
        rec = (accuracy(r["edited"], xte, yte) - dacc) / (ceil - dacc)
        if rec >= MIN_ORACLE:
            return {"arch": arch, "clean": clean, "damaged": dmg, "truth": truth, "oracle": ora, "data": data,
                    "ceiling": ceil, "damaged_metric": dacc, "oracle_recovery": rec, "draws": tries + 1,
                    "metric": "test accuracy"}
    raise RuntimeError("no accepted defect draw")


def metric(inst, weights, which="test"):
    x, y = inst["data"][which]
    return accuracy(weights, x, y)


def describe(inst):
    a = inst["arch"]
    sizes = [a["d_in"], *a["hidden"], a["classes"]]
    L = len(sizes) - 1
    parts = [f"x ({sizes[0]} inputs)"]
    for i in range(1, L):
        prev = "x" if i == 1 else f"h{i - 1}"
        parts.append(f"h{i} = relu({prev} @ W{i} + b{i}) ({sizes[i]} units)")
    parts.append(f"logits = h{L - 1} @ W{L} + b{L} ({sizes[-1]} classes); prediction = argmax(logits)")
    shapes = ", ".join(f"W{i} {sizes[i - 1]}x{sizes[i]}, b{i} {sizes[i]}" for i in range(1, L + 1))
    return "NETWORK (MLP classifier): " + " -> ".join(parts) + f".\nSHAPES: {shapes}."


def _fmt(v, nd=2):
    return " ".join(f"{x:.{nd}f}" for x in np.asarray(v).ravel())


def probe_text(inst, weights=None):
    w = weights if weights is not None else inst["damaged"]
    xp, yp = inst["data"]["probe"]
    z, hs = forward(w, xp, True)
    pred = z.argmax(1)
    C = z.shape[1]
    L = n_layers(w)
    lines = [describe(inst), "TENSOR STATS (mean / std / min / max):"]
    for i in range(1, L + 1):
        for k in (f"W{i}", f"b{i}"):
            t = w[k]
            lines.append(f"  {k}: {t.mean():.3f} / {t.std():.3f} / {t.min():.3f} / {t.max():.3f}")
    for i in range(1, L + 1):
        lines.append(f"b{i} = [{_fmt(w[f'b{i}'])}]")
    lines.append(f"PROBES on {len(yp)} labelled inputs:")
    lines.append(f"  accuracy = {(pred == yp).mean():.3f}")
    for i, h in enumerate(hs, 1):
        lines.append(f"  h{i} fraction of inputs where each unit is active (>0): [{_fmt((h > 0).mean(0))}]")
        lines.append(f"  h{i} mean activation per unit: [{_fmt(h.mean(0))}]")
    lines += [f"  true class counts      : {np.bincount(yp, minlength=C).tolist()}",
              f"  predicted class counts : {np.bincount(pred, minlength=C).tolist()}",
              "  confusion matrix (row = true class, column = predicted class):"]
    cm = np.zeros((C, C), int)
    np.add.at(cm, (yp, pred), 1)
    lines += [f"    {r}: {cm[r].tolist()}" for r in range(C)]
    lines.append("  mean logits per true class: " + "; ".join(
        f"{c}: [{_fmt(z[yp == c].mean(0), 1)}]" for c in range(C) if (yp == c).any()))
    return "\n".join(lines)


def probe_feedback(inst, weights):
    """Short report returned after a budgeted diagnostic probe pass (probe set only)."""
    xp, yp = inst["data"]["probe"]
    pred = forward(weights, xp).argmax(1)
    C = len(np.bincount(yp))
    return (f"probe accuracy after your edit = {(pred == yp).mean():.3f} (before: "
            f"{(forward(inst['damaged'], xp).argmax(1) == yp).mean():.3f}); predicted class counts after edit: "
            f"{np.bincount(pred, minlength=C).tolist()}")


# ------------------------------------------------------------------------------------------------ T0 / T1 material
def distractors(inst, rng):
    """Three wrong but plausible complete edits: same form at wrong targets (2) and a different-subtype repair."""
    fam, sub = inst["family"], inst["subtype"]
    w, L = inst["damaged"], n_layers(inst["damaged"])
    out = []
    from .pd2_bench import retarget
    for _ in range(40):
        cand = retarget(inst, inst["oracle"], rng)
        if cand != inst["oracle"] and cand not in out:
            out.append(cand)
        if len(out) == 2:
            break
    Wo, bo = f"W{L}", f"b{L}"
    C = w[bo].shape[0]
    a, b = (int(x) for x in rng.choice(C, 2, replace=False))
    layer = int(rng.integers(1, L))
    u = int(rng.integers(0, w[f"b{layer}"].shape[0]))
    pool = {"F1": f"swap {Wo}[:, {a}] {Wo}[:, {b}]\nswap {bo}[{a}] {bo}[{b}]",
            "F2": f"{bo}[{a}] -= {abs(float(rng.normal(3, 1))):.2f}",
            "F3": f"W{layer}[:, {u}] *= 10\nb{layer}[{u}] *= 10"}
    out.append(pool[fam])
    while len(out) < 3:
        out.append(f"{bo}[{int(rng.integers(0, C))}] += {abs(float(rng.normal(2, 1))):.2f}")
    return out[:3]


SUBTYPE_TEXT = {
    "dead_bias": "some hidden units are (almost) never active because their bias was set to a large negative value; "
                 "restore each such bias", "in_scale": "some hidden units' incoming weight column and bias were divided "
                 "by a constant (the unit fires as often as before but much more weakly); multiply them back",
    "out_mute": "some hidden units' outgoing weight rows were divided by a constant; multiply them back",
    "mixed": "several hidden-unit defects of different kinds (dead bias, scaled incoming weights, scaled outgoing rows)",
    "sign_flip": "some hidden units' incoming weights and bias were negated; negate them back",
    "out_perm": "the output classes were permuted (columns of the last weight matrix and entries of the last bias)",
    "out_perm_w": "the columns of the last weight matrix were permuted (the last bias was not changed)",
    "hidden_swap": "two rows of the last weight matrix (outgoing weights of two last-layer hidden units) were exchanged",
    "in_swap": "two rows of W1 (two input features) were exchanged",
    "out_bias": "one output bias was increased, so that class is over-predicted",
    "out_bias_pair": "one output bias was increased and another one decreased",
    "hidden_bias": "the biases of some hidden units were increased by large amounts",
    "logit_scale": "one class's output column and output bias were multiplied by a constant",
    "layer_bias": "the bias vector of one hidden layer was shifted by a constant"}


def template(inst):
    """T1 edit template: the oracle edit with every number replaced by '?' (structure and tensor names kept)."""
    import re
    return re.sub(r"(?<![A-Za-z_])(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?", "?", inst["oracle"])


# ------------------------------------------------------------------------------------------------ baselines
def simple_heuristic_edits(inst):
    """v1 three-rule heuristic generalized to any depth: dead units -> layer-median bias; swap the most confused
    output pair; lower the most over-predicted class's bias."""
    w = inst["damaged"]
    xp, yp = inst["data"]["probe"]
    z, hs = forward(w, xp, True)
    pred = z.argmax(1)
    L = n_layers(w)
    C = z.shape[1]
    out = []
    lines = []
    for i, h in enumerate(hs, 1):
        dead = np.flatnonzero((h > 0).mean(0) == 0)
        if len(dead):
            med = float(np.median(np.delete(w[f"b{i}"], dead)))
            lines += [f"b{i}[{int(u)}] = {med:.4f}" for u in dead]
    if lines:
        out.append("\n".join(lines[:16]))
    cm = np.zeros((C, C), int)
    np.add.at(cm, (yp, pred), 1)
    off = cm + cm.T
    np.fill_diagonal(off, 0)
    a, b = np.unravel_index(off.argmax(), off.shape)
    out.append(f"swap W{L}[:, {a}] W{L}[:, {b}]\nswap b{L}[{a}] b{L}[{b}]")
    over = np.bincount(pred, minlength=C) - np.bincount(yp, minlength=C)
    c = int(over.argmax())
    out.append(f"b{L}[{c}] -= {float(np.percentile(np.abs(z[:, c] - np.sort(z, 1)[:, -2]), 50)):.2f}")
    return out


def improved_heuristic_edits(inst):
    """Larger rule library from probes and tensor statistics (still non-agent): everything in the simple set plus
    near-dead units (rate < 10%) to median bias, Hungarian assignment of predicted to true classes (any permutation,
    with and without biases), norm outliers of incoming columns / outgoing rows rescaled to the layer median,
    per-class bias corrections to match predicted to true counts, and unit bias outliers to the layer median."""
    from scipy.optimize import linear_sum_assignment
    w = inst["damaged"]
    xp, yp = inst["data"]["probe"]
    z, hs = forward(w, xp, True)
    pred = z.argmax(1)
    L = n_layers(w)
    C = z.shape[1]
    out = list(simple_heuristic_edits(inst))
    lines = []
    for i, h in enumerate(hs, 1):
        rate = (h > 0).mean(0)
        low = np.flatnonzero(rate < 0.10)
        if len(low):
            med = float(np.median(w[f"b{i}"]))
            lines += [f"b{i}[{int(u)}] = {med:.4f}" for u in low]
    if lines:
        out.append("\n".join(lines[:16]))
    cm = np.zeros((C, C), int)
    np.add.at(cm, (yp, pred), 1)
    r, c = linear_sum_assignment(-cm)                 # true r -> predicted c
    perm = [int(x) for x in c]                        # damaged column perm[t] carries class t
    if perm != list(range(C)):
        cur = list(range(C))                          # build swaps that move column perm[t] to t
        lw, lb = [], []
        pos = {v: v for v in range(C)}
        arr = list(range(C))
        for t in range(C):
            src = arr.index(perm[t])
            if src != t:
                arr[src], arr[t] = arr[t], arr[src]
                lw.append(f"swap W{L}[:, {t}] W{L}[:, {src}]")
                lb.append(f"swap b{L}[{t}] b{L}[{src}]")
        out.append("\n".join(lw))
        out.append("\n".join(x for p in zip(lw, lb) for x in p))
        del cur, pos
    for i in range(1, L + 1):                         # norm outliers
        if i < L:
            cn = np.linalg.norm(w[f"W{i}"], axis=0)
            med = np.median(cn)
            lo = np.flatnonzero(cn < med / 3)
            st = []
            for u in lo[:8]:
                f = float(med / max(cn[u], 1e-6))
                st += [f"W{i}[:, {int(u)}] *= {f:.4f}", f"b{i}[{int(u)}] *= {f:.4f}"]
            if st:
                out.append("\n".join(st[:16]))
        if i > 1:
            rn = np.linalg.norm(w[f"W{i}"], axis=1)
            med = np.median(rn)
            lo = np.flatnonzero(rn < med / 3)
            if len(lo):
                out.append("\n".join(f"W{i}[{int(u)}, :] *= {float(med / max(rn[u], 1e-6)):.4f}" for u in lo[:16]))
    # output column scale outliers
    cn = np.linalg.norm(w[f"W{L}"], axis=0)
    med = np.median(cn)
    hi = np.flatnonzero(cn > 1.6 * med)
    if len(hi):
        out.append("\n".join(f"W{L}[:, {int(k)}] *= {float(med / cn[k]):.4f}\nb{L}[{int(k)}] *= {float(med / cn[k]):.4f}"
                             for k in hi[:8]))
    # count-matching output bias correction (iterative, on probes)
    b = w[f"b{L}"].astype(np.float64).copy()
    zz = z - w[f"b{L}"]
    for _ in range(50):
        p = (zz + b).argmax(1)
        diff = np.bincount(p, minlength=C) - np.bincount(yp, minlength=C)
        if np.abs(diff).max() <= 2:
            break
        b -= 0.05 * np.sign(diff) * np.abs(zz).mean()
    delta = b - w[f"b{L}"]
    if np.abs(delta).max() > 1e-6:
        out.append("\n".join(f"b{L}[{k}] += {delta[k]:.4f}" for k in range(C) if abs(delta[k]) > 1e-6))
    # hidden bias outliers (always-on units) -> median
    for i, h in enumerate(hs, 1):
        bb = w[f"b{i}"]
        mad = np.median(np.abs(bb - np.median(bb))) + 1e-6
        hi = np.flatnonzero(np.abs(bb - np.median(bb)) > 6 * mad)
        if 0 < len(hi) <= 8:
            out.append("\n".join(f"b{i}[{int(u)}] = {float(np.median(bb)):.4f}" for u in hi))
        rate = (h > 0).mean(0)
        if (rate > 0.999).all() or (rate < 0.02).mean() > 0.5:   # whole-layer shift
            pass
    # whole-layer bias shift: re-centre so the median unit is active on ~50% of inputs
    for i, h in enumerate(hs, 1):
        rate = (h > 0).mean(0)
        if np.median(rate) > 0.9 or np.median(rate) < 0.1:
            pre = h  # post-ReLU; approximate shift from bias median of activity
            s = float(np.median(w[f"b{i}"]))
            out.append(f"b{i}[:] -= {s:.4f}")
    return out
