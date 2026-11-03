"""Phase D benchmark v2, family F5 (held-out transfer family): small algorithmic transformers with injected defects.

Each instance is an independently trained 1-layer transformer (torch, CPU, target construction only; editors never use
gradients). Scoring uses an exact numpy re-implementation of the same forward pass.

Model: h0 = E[x] + P (T x 32); bidirectional 2-head self-attention (head h uses columns 16h:16h+16 of Wq/Wk/Wv and rows
16h:16h+16 of Wo), h1 = h0 + attn; h2 = h1 + relu(h1 @ W1 + b1) @ W2 + b2 (64 hidden); logits = h2 @ U + bU.
Tasks: modadd (input [a, b, '='], p in {17, 19, 23}; output (a + b) mod p at the last position) and reverse (5 tokens
over 8 symbols; position i outputs x[4 - i]; exact match = all positions). Probe set: 64 (modadd) / 128 (reverse)
inputs; test set: all other modadd pairs / 2,048 other sequences. Metric: exact-match accuracy on the test set.

Subtypes: head_mute (one head's Wo rows divided by m), qk_flatten (one head's Wq columns divided by m: near-uniform
attention), mlp_mute (4-10 MLP neurons' W2 rows divided by m), unembed_swap (two output tokens' U columns and bU entries
exchanged), embed_swap (two input tokens' E rows exchanged), pos_swap (two positions' P rows exchanged; reverse only). mlp_mute uses modadd only (the
reverse task is solved by attention alone, so muting MLP neurons does not damage it).
"""
import numpy as np

SUBTYPES = {"F5": ([], ["head_mute", "qk_flatten", "mlp_mute", "unembed_swap", "embed_swap", "pos_swap"])}
D, DH, NH, DM = 32, 16, 2, 64
LIMITS = {"max_statements": 16, "max_entries": 1024}
NAMES = ("E", "P", "Wq", "Wk", "Wv", "Wo", "W1", "b1", "W2", "b2", "U", "bU")


def forward(w, x, attn=False):
    """x: int array [N, T] -> logits [N, T, Vout] (and attention [N, H, T, T])."""
    h0 = w["E"][x] + w["P"][None, : x.shape[1]]
    q, k, v = h0 @ w["Wq"], h0 @ w["Wk"], h0 @ w["Wv"]
    outs, atts = [], []
    for h in range(NH):
        s = slice(h * DH, (h + 1) * DH)
        a = q[..., s] @ np.swapaxes(k[..., s], 1, 2) / np.sqrt(DH)
        a = np.exp(a - a.max(-1, keepdims=True))
        a /= a.sum(-1, keepdims=True)
        atts.append(a)
        outs.append(a @ v[..., s])
    h1 = h0 + np.concatenate(outs, -1) @ w["Wo"]
    m = np.maximum(0, h1 @ w["W1"] + w["b1"])
    h2 = h1 + m @ w["W2"] + w["b2"]
    z = h2 @ w["U"] + w["bU"]
    return (z, np.stack(atts, 1), m) if attn else z


def task_data(rng, task):
    if task["name"] == "modadd":
        p = task["p"]
        a, b = np.meshgrid(np.arange(p), np.arange(p), indexing="ij")
        x = np.stack([a.ravel(), b.ravel(), np.full(p * p, p)], 1)
        y = (a.ravel() + b.ravel()) % p
        perm = rng.permutation(p * p)
        pr, te = perm[:64], perm[64:]
        return {"train": (x, y), "probe": (x[pr], y[pr]), "test": (x[te], y[te])}
    L, V = 5, 8
    allx = rng.choice(V ** L, 2048 + 128, replace=False)
    xs = np.stack([(allx // V ** i) % V for i in range(L)], 1)
    return {"probe": (xs[:128], xs[:128, ::-1].copy()), "test": (xs[128:], xs[128:, ::-1].copy())}


def accuracy(w, task, x, y):
    z = forward(w, x)
    if task["name"] == "modadd":
        return float((z[:, -1].argmax(-1) == y).mean())
    return float((z.argmax(-1) == y).all(1).mean())


def train(seed, task, data, steps=4000):
    import torch
    torch.manual_seed(seed % 2 ** 31)
    torch.set_num_threads(1)
    vin, vout, T = ((task["p"] + 1, task["p"], 3) if task["name"] == "modadd" else (8, 8, 5))
    g = torch.Generator().manual_seed(seed % 2 ** 31)

    def P(*s, sc=None):
        return torch.nn.Parameter(torch.randn(*s, generator=g) * (sc if sc is not None else 1 / np.sqrt(s[0])))
    w = {"E": P(vin, D, sc=0.5), "P": P(T, D, sc=0.5), "Wq": P(D, D), "Wk": P(D, D), "Wv": P(D, D), "Wo": P(D, D),
         "W1": P(D, DM), "b1": torch.nn.Parameter(torch.zeros(DM)), "W2": P(DM, D),
         "b2": torch.nn.Parameter(torch.zeros(D)), "U": P(D, vout), "bU": torch.nn.Parameter(torch.zeros(vout))}
    opt = torch.optim.AdamW(w.values(), lr=3e-3, weight_decay=1e-4)
    rs = np.random.default_rng(seed)

    def fwd(x):
        h0 = w["E"][x] + w["P"][None, : x.shape[1]]
        q, k, v = h0 @ w["Wq"], h0 @ w["Wk"], h0 @ w["Wv"]
        outs = []
        for h in range(NH):
            s = slice(h * DH, (h + 1) * DH)
            a = torch.softmax(q[..., s] @ k[..., s].transpose(1, 2) / np.sqrt(DH), -1)
            outs.append(a @ v[..., s])
        h1 = h0 + torch.cat(outs, -1) @ w["Wo"]
        h2 = h1 + torch.relu(h1 @ w["W1"] + w["b1"]) @ w["W2"] + w["b2"]
        return h2 @ w["U"] + w["bU"]
    for t in range(steps):
        if task["name"] == "modadd":
            x, y = (torch.as_tensor(a) for a in data["train"])
            loss = torch.nn.functional.cross_entropy(fwd(x)[:, -1], y)
        else:
            xs = rs.integers(0, 8, (512, 5))
            x, y = torch.as_tensor(xs), torch.as_tensor(xs[:, ::-1].copy())
            loss = torch.nn.functional.cross_entropy(fwd(x).reshape(-1, vout), y.reshape(-1))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if t % 250 == 249:
            ww = {k: v.detach().numpy().astype(np.float32) for k, v in w.items()}
            if accuracy(ww, task, *data["test"]) >= 0.995:
                break
    return {k: v.detach().numpy().astype(np.float32).copy() for k, v in w.items()}


def damage(sub, rng, w, task, data):
    d = {k: v.copy() for k, v in w.items()}
    truth, ora = [], []
    if sub == "head_mute":
        h, m = int(rng.integers(0, NH)), int(rng.choice([10, 20]))
        d["Wo"][h * DH:(h + 1) * DH] *= np.float32(1 / m)
        truth.append({"head": h, "factor": 1 / m})
        ora.append(f"Wo[{h * DH}:{(h + 1) * DH}, :] *= {m}")
    elif sub == "qk_flatten":
        h, m = int(rng.integers(0, NH)), int(rng.choice([10, 20]))
        d["Wq"][:, h * DH:(h + 1) * DH] *= np.float32(1 / m)
        truth.append({"head": h, "factor": 1 / m})
        ora.append(f"Wq[:, {h * DH}:{(h + 1) * DH}] *= {m}")
    elif sub == "mlp_mute":
        x, y = data["probe"]
        _, _, mm = forward(w, x, True)
        imp = (mm.mean(axis=tuple(range(mm.ndim - 1)))) * np.linalg.norm(w["W2"], axis=1)
        units = sorted(int(u) for u in rng.choice(np.argsort(imp)[::-1][:16], int(rng.integers(4, 11)), replace=False))
        for u in units:
            m = int(rng.choice([8, 10, 16, 20]))
            d["W2"][u] *= np.float32(1 / m)
            truth.append({"neuron": u, "factor": 1 / m})
            ora.append(f"W2[{u}, :] *= {m}")
    elif sub == "unembed_swap":
        V = w["U"].shape[1]
        a, b = sorted(int(t) for t in rng.choice(V, 2, replace=False))
        d["U"][:, [a, b]] = w["U"][:, [b, a]]
        d["bU"][[a, b]] = w["bU"][[b, a]]
        truth.append({"tokens": [a, b]})
        ora += [f"swap U[:, {a}] U[:, {b}]", f"swap bU[{a}] bU[{b}]"]
    elif sub == "embed_swap":
        V = w["E"].shape[0] - (1 if task["name"] == "modadd" else 0)
        a, b = sorted(int(t) for t in rng.choice(V, 2, replace=False))
        d["E"][[a, b]] = w["E"][[b, a]]
        truth.append({"tokens": [a, b]})
        ora.append(f"swap E[{a}, :] E[{b}, :]")
    elif sub == "pos_swap":
        a, b = sorted(int(t) for t in rng.choice(w["P"].shape[0], 2, replace=False))
        d["P"][[a, b]] = w["P"][[b, a]]
        truth.append({"positions": [a, b]})
        ora.append(f"swap P[{a}, :] P[{b}, :]")
    return d, truth, "\n".join(ora)


def build(fam, sub, seed):
    from . import edit_dsl as E
    assert fam == "F5"
    rng = np.random.default_rng(seed)
    r = rng.random()
    task = ({"name": "reverse"} if sub == "pos_swap" or (sub != "mlp_mute" and r < 0.5)
            else {"name": "modadd", "p": int(rng.choice([17, 19, 23]))})
    data = task_data(rng, task)
    clean = train(seed, task, data)
    ceil = accuracy(clean, task, *data["test"])
    if ceil < 0.95:
        raise RuntimeError(f"training reached only {ceil:.3f}")
    for tries in range(20):
        dmg, truth, ora = damage(sub, rng, clean, task, data)
        dm = accuracy(dmg, task, *data["test"])
        if ceil - dm < 0.15:
            continue
        r = E.run(dmg, ora, **LIMITS)
        assert r["valid"], r["error"]
        rec = (accuracy(r["edited"], task, *data["test"]) - dm) / (ceil - dm)
        if rec >= 0.95:
            return {"arch": {"task": task}, "clean": clean, "damaged": dmg, "truth": truth, "oracle": ora,
                    "data": {"task": task, **{k: v for k, v in data.items() if k != "train"}}, "ceiling": ceil,
                    "damaged_metric": dm, "oracle_recovery": rec, "draws": tries + 1, "metric": "test exact match"}
    raise RuntimeError("no accepted defect draw")


def metric(inst, weights, which="test"):
    return accuracy(weights, inst["data"]["task"], *inst["data"][which])


def _fmt(v, nd=2):
    return " ".join(f"{x:.{nd}f}" for x in np.asarray(v).ravel())


def describe(inst):
    t = inst["data"]["task"]
    if t["name"] == "modadd":
        p = t["p"]
        task = (f"TASK: modular addition mod {p}. Input tokens [a, b, '='] with a, b in 0..{p - 1} (token {p} is '='); "
                f"the output at the last position must be (a + b) mod {p} (output tokens 0..{p - 1}).")
        vin, vout, T = p + 1, p, 3
    else:
        task = ("TASK: reverse a sequence. Input: 5 tokens over symbols 0..7; output position i must be input token "
                "4 - i (exact match requires all 5 positions).")
        vin, vout, T = 8, 8, 5
    return (task + f"\nNETWORK (1-layer transformer, d = 32): h0 = E[x] + P; 2-head bidirectional self-attention "
            f"(head h uses columns 16h:16h+16 of Wq, Wk, Wv and rows 16h:16h+16 of Wo; softmax(q k^T / 4)); "
            f"h1 = h0 + concat(heads) @ Wo; h2 = h1 + relu(h1 @ W1 + b1) @ W2 + b2 (64 MLP neurons); "
            f"logits = h2 @ U + bU.\nSHAPES: E {vin}x32, P {T}x32, Wq/Wk/Wv/Wo 32x32, W1 32x64, b1 64, W2 64x32, "
            f"b2 32, U 32x{vout}, bU {vout}.")


def probe_text(inst, weights=None):
    w = weights if weights is not None else inst["damaged"]
    t = inst["data"]["task"]
    x, y = inst["data"]["probe"]
    z, att, m = forward(w, x, True)
    lines = [describe(inst), "TENSOR STATS (mean / std / min / max) and row/column norms:"]
    for k in NAMES:
        a = w[k]
        lines.append(f"  {k}: {a.mean():.3f} / {a.std():.3f} / {a.min():.3f} / {a.max():.3f}")
    lines += [f"  row norms of E: [{_fmt(np.linalg.norm(w['E'], axis=1))}]",
              f"  row norms of P: [{_fmt(np.linalg.norm(w['P'], axis=1))}]",
              f"  per-head norms of Wq columns / Wo rows: " + ", ".join(
                  f"head {h}: {np.linalg.norm(w['Wq'][:, h * DH:(h + 1) * DH]):.2f} / "
                  f"{np.linalg.norm(w['Wo'][h * DH:(h + 1) * DH]):.2f}" for h in range(NH)),
              f"  column norms of U: [{_fmt(np.linalg.norm(w['U'], axis=0))}]", f"  bU = [{_fmt(w['bU'])}]",
              f"PROBES on {len(x)} inputs:", f"  exact-match accuracy = {metric(inst, w, 'probe'):.3f}"]
    for h in range(NH):
        lines.append(f"  head {h} mean attention (rows = query position): " + "; ".join(
            f"[{_fmt(r)}]" for r in att[:, h].mean(0)))
    lines.append(f"  MLP neuron activation rate: [{_fmt((m > 0).mean(axis=(0, 1)))}]")
    if t["name"] == "modadd":
        pred = z[:, -1].argmax(-1)
        pairs = {}
        for a, b in zip(y, pred):
            if a != b:
                pairs[(int(a), int(b))] = pairs.get((int(a), int(b)), 0) + 1
        top = sorted(pairs.items(), key=lambda kv: -kv[1])[:10]
        lines.append("  most frequent errors (true -> predicted: count): " + ", ".join(f"{a}->{b}: {c}" for (a, b), c in top))
        tok_err = {}
        for (a, b), r in zip(x[:, :2], pred != y):
            for tkn in (int(a), int(b)):
                tok_err.setdefault(tkn, []).append(bool(r))
        lines.append("  error rate by input token value: " + ", ".join(
            f"{k}: {np.mean(v):.2f}" for k, v in sorted(tok_err.items())))
    else:
        pred = z.argmax(-1)
        lines.append(f"  accuracy per output position: [{_fmt((pred == y).mean(0))}]")
        cm = np.zeros((8, 8), int)
        np.add.at(cm, (y.ravel(), pred.ravel()), 1)
        lines.append("  confusion over all positions (row = true symbol): " + "; ".join(f"{r}: {cm[r].tolist()}" for r in range(8)))
    return "\n".join(lines)


def probe_feedback(inst, weights):
    return (f"probe exact-match accuracy after your edit = {metric(inst, weights, 'probe'):.3f} (before: "
            f"{metric(inst, inst['damaged'], 'probe'):.3f})")


def distractors(inst, rng):
    w = inst["damaged"]
    V = w["U"].shape[1]
    out = []
    pool = [lambda: f"Wo[{(h := int(rng.integers(0, 2))) * 16}:{h * 16 + 16}, :] *= 10",
            lambda: f"Wq[:, {(h := int(rng.integers(0, 2))) * 16}:{h * 16 + 16}] *= 10",
            lambda: "\n".join(f"W2[{int(u)}, :] *= 10" for u in rng.choice(64, 3, replace=False)),
            lambda: (lambda a, b: f"swap U[:, {a}] U[:, {b}]\nswap bU[{a}] bU[{b}]")(*sorted(int(t) for t in rng.choice(V, 2, replace=False))),
            lambda: (lambda a, b: f"swap E[{a}, :] E[{b}, :]")(*sorted(int(t) for t in rng.choice(min(V, w['E'].shape[0]), 2, replace=False)))]
    for _ in range(30):
        c = pool[int(rng.integers(len(pool)))]()
        if c != inst["oracle"] and c not in out:
            out.append(c)
        if len(out) == 3:
            break
    return out


SUBTYPE_TEXT = {"head_mute": "one attention head's output rows of Wo were divided by a constant",
                "qk_flatten": "one attention head's query columns of Wq were divided by a constant (attention is nearly uniform)",
                "mlp_mute": "some MLP neurons' outgoing rows of W2 were divided by a constant",
                "unembed_swap": "two output tokens' columns of U and entries of bU were exchanged",
                "embed_swap": "two input tokens' rows of E were exchanged",
                "pos_swap": "two rows of the positional embedding P were exchanged"}


def template(inst):
    import re
    return re.sub(r"(?<![A-Za-z_])(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?", "?", inst["oracle"])


def simple_heuristic_edits(inst):
    """Analogue of the v1 rules: swap the most confused output pair; raise the most under-predicted token's bU."""
    w = inst["damaged"]
    x, y = inst["data"]["probe"]
    z = forward(w, x)
    pred = (z[:, -1] if inst["data"]["task"]["name"] == "modadd" else z).argmax(-1).ravel()
    yy = y.ravel()
    V = w["U"].shape[1]
    cm = np.zeros((V, V), int)
    np.add.at(cm, (yy, pred), 1)
    off = cm + cm.T
    np.fill_diagonal(off, 0)
    a, b = sorted(int(t) for t in np.unravel_index(off.argmax(), off.shape))
    under = np.bincount(yy, minlength=V) - np.bincount(pred, minlength=V)
    c = int(under.argmax())
    return [f"swap U[:, {a}] U[:, {b}]\nswap bU[{a}] bU[{b}]", f"bU[{c}] += 1.0"]


def improved_heuristic_edits(inst):
    """Simple rules + per-head Wo/Wq norm outliers rescaled to the other head's norm, low-norm W2 rows rescaled to the
    median, the most confused pair as an E-row swap, and all P-row swaps."""
    w = inst["damaged"]
    out = list(simple_heuristic_edits(inst))
    for nm, sl in (("Wo", lambda h: (slice(h * 16, h * 16 + 16), slice(None))), ("Wq", lambda h: (slice(None), slice(h * 16, h * 16 + 16)))):
        n = [np.linalg.norm(w[nm][sl(h)]) for h in range(NH)]
        lo = int(np.argmin(n))
        if n[lo] < max(n) / 3:
            f = max(n) / n[lo]
            out.append(f"{nm}[{lo * 16}:{lo * 16 + 16}, :] *= {f:.3f}" if nm == "Wo" else f"{nm}[:, {lo * 16}:{lo * 16 + 16}] *= {f:.3f}")
    rn = np.linalg.norm(w["W2"], axis=1)
    lo = np.flatnonzero(rn < np.median(rn) / 3)
    if len(lo):
        out.append("\n".join(f"W2[{int(u)}, :] *= {float(np.median(rn) / max(rn[u], 1e-6)):.3f}" for u in lo[:16]))
    s = out[0].splitlines()[0]
    import re
    a, b = (int(v) for v in re.findall(r"U\[:, (\d+)\]", s))
    if a < w["E"].shape[0] and b < w["E"].shape[0]:
        out.append(f"swap E[{a}, :] E[{b}, :]")
    T = w["P"].shape[0]
    for i in range(T):
        for j in range(i + 1, T):
            out.append(f"swap P[{i}, :] P[{j}, :]")
    return out
