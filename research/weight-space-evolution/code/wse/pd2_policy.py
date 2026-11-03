"""Phase D benchmark v2, family F4: MinAtar policy networks (upstream exp5 hand networks, read-only Gold) with injected
behavioural defects. wse environment (needs MinAtar).

Reference networks: Seaquest and Asterix `hand.npz` (600-32-32-6 tanh), registered read-only, scored with the
validated Phase C evaluator (wse.minatar_eval.run_batch: official MinAtar 1.0.15, sticky actions 0.1, softmax
sampling, paired seeds). Benchmark metric: mean episode score over the instance's fixed test seeds (300 episodes,
episodes cut at 3,000 steps); probe metric: 100 different seeds. Clean, damaged and edited networks are scored on the
same seeds (paired), so the oracle inverse edit reproduces the clean episodes exactly up to float rounding.

Subtypes (core): action_suppress (one used action's logit bias lowered: the policy almost never takes it),
action_swap (two actions' output columns and biases exchanged), unit_mute (2-4 hidden units' outgoing rows divided by
m), unit_saturate (1-3 hidden units' biases shifted so tanh saturates). Held-out: input_blind (the W1 rows of one or two
grid rows divided by m: the policy is nearly blind to that part of the screen).
"""
import multiprocessing as mp

import numpy as np

from . import minatar_eval as ME
from . import registry

SUBTYPES = {"F4": (["action_suppress", "action_swap", "unit_mute", "unit_saturate"], ["input_blind"])}
GAMES = ("seaquest", "asterix")
ACTIONS = ["noop", "left", "up", "right", "down", "fire"]
MAX_STEPS = 3000
N_TEST, N_PROBE = 300, 100
LIMITS = {"max_statements": 16, "max_entries": 4096}
CHANNEL_TEXT = {g: "; ".join(f"c{c}: " + "+".join(n) for c, n in ME.OBS_MAP[g]) for g in ME.OBS_MAP}
_POOL = None


def pool():
    global _POOL
    if _POOL is None:
        _POOL = mp.get_context("fork").Pool(16)
    return _POOL


def gold_id(game):
    return f"minatar-{game}-exp5-hand@4d09ba6"


def clean_weights(game):
    return {k: np.array(a, dtype=np.float32) for k, (dt, a) in registry.load(gold_id(game)).items()}


def episodes(game, w, seeds, chunk=10):
    jobs = [(game, {k: np.asarray(w[k]) for k in ME.NAMES}, list(seeds[i:i + chunk]), [], MAX_STEPS)
            for i in range(0, len(seeds), chunk)]
    eps = [e for part in pool().map(ME.run_batch, jobs) for e in part]
    return eps


def mean_score(game, w, seeds):
    return float(np.mean([e["score"] for e in episodes(game, w, seeds)]))


def states(game, w, seeds, every=8, cap=1500):
    """Observations visited by policy w on a few seeds (every k-th step), for activation probes."""
    from minatar import Environment
    xs = []
    for s in seeds:
        env = Environment(game, sticky_action_prob=0.1)
        env.seed(int(s))
        env.reset()
        build = ME.obs_builder(game, env.env.channels)
        rng = np.random.default_rng([int(s), 1])
        for t in range(MAX_STEPS):
            x = build(env.state())
            if t % every == 0:
                xs.append(x)
            lg = ME.policy_logits(w, x[None].astype(np.float64))[0]
            p = np.exp(lg - lg.max())
            p /= p.sum()
            a = int(min(np.searchsorted(np.cumsum(p), rng.random(), side="right"), 5))
            _, term = env.act(a)
            if term:
                break
    xs = np.array(xs[:cap], dtype=np.float64)
    return xs


def damage(sub, rng, w, usage):
    d = {k: v.copy() for k, v in w.items()}
    truth, ora = [], []
    used = [a for a in range(6) if usage[a] >= 0.08]
    if sub == "action_suppress":
        a = int(rng.choice(used))
        s = round(float(rng.uniform(6, 12)), 2)
        d["b3"][a] -= np.float32(s)
        truth.append({"action": a, "shift": -s})
        ora.append(f"b3[{a}] += {s}")
    elif sub == "action_swap":
        a, b = sorted(int(x) for x in rng.choice(used if len(used) >= 2 else range(6), 2, replace=False))
        d["W3"][:, [a, b]] = w["W3"][:, [b, a]]
        d["b3"][[a, b]] = w["b3"][[b, a]]
        truth.append({"actions": [a, b]})
        ora += [f"swap W3[:, {a}] W3[:, {b}]", f"swap b3[{a}] b3[{b}]"]
    elif sub == "unit_mute":
        layer = int(rng.choice([1, 2]))
        Wn = f"W{layer + 1}"
        norms = np.linalg.norm(w[Wn], axis=1)
        units = sorted(int(u) for u in rng.choice(np.argsort(norms)[::-1][:10], int(rng.integers(2, 5)), replace=False))
        for u in units:
            m = int(rng.choice([5, 8, 10, 16, 20]))
            d[Wn][u, :] *= np.float32(1 / m)
            truth.append({"layer": layer, "unit": u, "factor": 1 / m})
            ora.append(f"{Wn}[{u}, :] *= {m}")
    elif sub == "unit_saturate":
        layer = int(rng.choice([1, 2]))
        Wn = f"W{layer + 1}"
        norms = np.linalg.norm(w[Wn], axis=1)
        units = sorted(int(u) for u in rng.choice(np.argsort(norms)[::-1][:10], int(rng.integers(1, 4)), replace=False))
        for u in units:
            s = round(float(rng.uniform(3, 6)) * float(rng.choice([-1, 1])), 2)
            d[f"b{layer}"][u] += np.float32(s)
            truth.append({"layer": layer, "unit": u, "shift": s})
            ora.append(f"b{layer}[{u}] -= {s}" if s > 0 else f"b{layer}[{u}] += {-s}")
    elif sub == "input_blind":
        rows = sorted(int(r) for r in rng.choice(10, int(rng.integers(1, 3)), replace=False))
        m = int(rng.choice([10, 20]))
        for r in rows:
            d["W1"][r * 60:(r + 1) * 60, :] *= np.float32(1 / m)
            truth.append({"grid_row": r, "factor": 1 / m})
            ora.append(f"W1[{r * 60}:{(r + 1) * 60}, :] *= {m}")
    else:
        raise ValueError(sub)
    return d, truth, "\n".join(ora)


def build(fam, sub, seed):
    from . import edit_dsl as E
    assert fam == "F4"
    rng = np.random.default_rng(seed)
    game = str(rng.choice(GAMES))
    clean = clean_weights(game)
    seeds = rng.choice(10 ** 8, N_TEST + N_PROBE, replace=False)
    test, probe = [int(s) for s in seeds[:N_TEST]], [int(s) for s in seeds[N_TEST:]]
    ceil = mean_score(game, clean, test)
    ce = episodes(game, clean, probe)
    usage = np.sum([e["action_counts"] for e in ce], 0)
    usage = usage / usage.sum()
    for tries in range(12):
        dmg, truth, ora = damage(sub, rng, clean, usage)
        dm = mean_score(game, dmg, test)
        if ceil - dm < max(0.35 * ceil, 8.0):
            continue
        r = E.run(dmg, ora, **LIMITS)
        assert r["valid"], r["error"]
        rec = (mean_score(game, r["edited"], test) - dm) / (ceil - dm)
        if rec >= 0.9:
            return {"arch": {"game": game}, "clean": clean, "damaged": dmg, "truth": truth, "oracle": ora,
                    "data": {"game": game, "test": test, "probe": probe}, "ceiling": ceil, "damaged_metric": dm,
                    "oracle_recovery": rec, "draws": tries + 1, "metric": f"mean {game} score, {N_TEST} paired episodes"}
    raise RuntimeError("no accepted defect draw")


def metric(inst, weights, which="test"):
    return mean_score(inst["data"]["game"], weights, inst["data"][which])


def _fmt(v, nd=2):
    return " ".join(f"{x:.{nd}f}" for x in np.asarray(v).ravel())


def describe(inst):
    g = inst["data"]["game"]
    return (f"NETWORK (MinAtar {g} policy): x (600 binary inputs = 10x10 grid x 6 channels, index (row*10+col)*6+channel)"
            f" -> h1 = tanh(x @ W1 + b1) (32 units) -> h2 = tanh(h1 @ W2 + b2) (32 units) -> logits = h2 @ W3 + b3 "
            f"(6 actions: {', '.join(f'{i} {a}' for i, a in enumerate(ACTIONS))}); the action is sampled from "
            f"softmax(logits); sticky actions 0.1. Score = game reward per episode.\nCHANNELS: {CHANNEL_TEXT[g]}.\n"
            "SHAPES: W1 600x32, b1 32, W2 32x32, b2 32, W3 32x6, b3 6.")


def _episode_summary(game, w, seeds):
    eps = episodes(game, w, seeds)
    ac = np.sum([e["action_counts"] for e in eps], 0)
    return (f"mean score = {np.mean([e['score'] for e in eps]):.2f} over {len(eps)} episodes, mean length = "
            f"{np.mean([e['length'] for e in eps]):.0f} steps; action frequencies: "
            + ", ".join(f"{ACTIONS[a]} {ac[a] / ac.sum():.3f}" for a in range(6)))


def probe_text(inst, weights=None):
    w = weights if weights is not None else inst["damaged"]
    g = inst["data"]["game"]
    lines = [describe(inst), "TENSOR STATS (mean / std / min / max):"]
    for k in ME.NAMES:
        t = w[k]
        lines.append(f"  {k}: {t.mean():.3f} / {t.std():.3f} / {t.min():.3f} / {t.max():.3f}")
    lines += [f"b1 = [{_fmt(w['b1'])}]", f"b2 = [{_fmt(w['b2'])}]", f"b3 = [{_fmt(w['b3'])}]",
              "W3 rows (h2 unit -> 6 action logits): " + "; ".join(f"{i}: [{_fmt(w['W3'][i], 1)}]" for i in range(32))]
    lines.append(f"PROBES on {len(inst['data']['probe'])} fixed-seed episodes: " + _episode_summary(g, w, inst["data"]["probe"]))
    x = states(g, w, inst["data"]["probe"][:6])
    h1 = np.tanh(x @ w["W1"] + w["b1"])
    h2 = np.tanh(h1 @ w["W2"] + w["b2"])
    lg = h2 @ w["W3"] + w["b3"]
    p = np.exp(lg - lg.max(1, keepdims=True))
    p /= p.sum(1, keepdims=True)
    lines += [f"  on {len(x)} visited states: mean action probabilities [{_fmt(p.mean(0), 3)}]",
              f"  h1 mean activation per unit: [{_fmt(h1.mean(0))}]",
              f"  h1 fraction saturated (|h| > 0.95) per unit: [{_fmt((np.abs(h1) > 0.95).mean(0))}]",
              f"  h2 mean activation per unit: [{_fmt(h2.mean(0))}]",
              f"  h2 fraction saturated (|h| > 0.95) per unit: [{_fmt((np.abs(h2) > 0.95).mean(0))}]",
              "  mean |W1| per grid row (rows 0-9, top to bottom): [" +
              _fmt([np.abs(w['W1'][r * 60:(r + 1) * 60]).mean() for r in range(10)], 3) + "]"]
    return "\n".join(lines)


def probe_feedback(inst, weights):
    g = inst["data"]["game"]
    return "after your edit, probe episodes: " + _episode_summary(g, weights, inst["data"]["probe"])


def distractors(inst, rng):
    """Three distinct wrong edits of the F4 defect forms at random targets."""
    out = []
    while len(out) < 3:
        k = int(rng.integers(0, 4))
        if k == 0:
            c = f"b3[{int(rng.integers(0, 6))}] += {round(float(rng.uniform(6, 12)), 2)}"
        elif k == 1:
            a, b = sorted(int(x) for x in rng.choice(6, 2, replace=False))
            c = f"swap W3[:, {a}] W3[:, {b}]\nswap b3[{a}] b3[{b}]"
        elif k == 2:
            c = f"W{int(rng.choice([2, 3]))}[{int(rng.integers(0, 32))}, :] *= {int(rng.choice([5, 10, 20]))}"
        else:
            c = f"b{int(rng.choice([1, 2]))}[{int(rng.integers(0, 32))}] -= {round(float(rng.uniform(3, 6)), 2)}"
        if c != inst["oracle"] and c not in out:
            out.append(c)
    return out


SUBTYPE_TEXT = {"action_suppress": "one action's output bias was lowered, so the policy almost never takes it",
                "action_swap": "two actions' output columns and output biases were exchanged",
                "unit_mute": "some hidden units' outgoing weight rows were divided by a constant",
                "unit_saturate": "some hidden units' biases were shifted so that the unit is saturated (tanh near +-1)",
                "input_blind": "the W1 rows for one or two grid rows (60 consecutive input rows each) were divided by a "
                               "constant, so the policy barely sees that part of the screen"}


def template(inst):
    import re
    return re.sub(r"(?<![A-Za-z_])(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?", "?", inst["oracle"])


def _saturated(w, x):
    h1 = np.tanh(x @ w["W1"] + w["b1"])
    h2 = np.tanh(h1 @ w["W2"] + w["b2"])
    return h1, h2


def simple_heuristic_edits(inst):
    """Non-agent rules: saturated units -> layer-median bias; least-used action's bias -> median of b3."""
    w = inst["damaged"]
    g = inst["data"]["game"]
    x = states(g, w, inst["data"]["probe"][:4])
    h1, h2 = _saturated(w, x)
    out, lines = [], []
    for k, h in ((1, h1), (2, h2)):
        sat = np.flatnonzero((np.abs(h) > 0.99).mean(0) > 0.95)
        med = float(np.median(w[f"b{k}"]))
        lines += [f"b{k}[{int(u)}] = {med:.4f}" for u in sat[:8]]
    if lines:
        out.append("\n".join(lines))
    a = int(np.argmin(w["b3"]))
    out.append(f"b3[{a}] = {float(np.median(w['b3'])):.4f}")
    return out


def improved_heuristic_edits(inst):
    """Simple rules + low-norm outgoing rows rescaled to the median norm, low-|W1| grid rows rescaled, every action
    pair swap (15 candidates) and each action's bias raised to the maximum of b3."""
    w = inst["damaged"]
    out = list(simple_heuristic_edits(inst))
    for Wn in ("W2", "W3"):
        rn = np.linalg.norm(w[Wn], axis=1)
        med = np.median(rn)
        lo = np.flatnonzero(rn < med / 3)
        if len(lo):
            out.append("\n".join(f"{Wn}[{int(u)}, :] *= {float(med / max(rn[u], 1e-6)):.3f}" for u in lo[:16]))
    gr = np.array([np.abs(w["W1"][r * 60:(r + 1) * 60]).mean() for r in range(10)])
    lo = np.flatnonzero((gr < np.median(gr) / 3) & (gr > 1e-6))
    if len(lo):
        out.append("\n".join(f"W1[{r * 60}:{(r + 1) * 60}, :] *= {float(np.median(gr) / gr[r]):.3f}" for r in lo))
    for a in range(6):
        for b in range(a + 1, 6):
            out.append(f"swap W3[:, {a}] W3[:, {b}]\nswap b3[{a}] b3[{b}]")
    for a in range(6):
        if w["b3"][a] < w["b3"].max() - 1:
            out.append(f"b3[{a}] = {float(w['b3'].max()):.4f}")
    return out
