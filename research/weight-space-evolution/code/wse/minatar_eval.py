"""Forward-pass/evaluation service for the 600-32-32-6 tanh MinAtar policies of upstream exp5.

Protocol (matches upstream exp5 scoring): official MinAtar 1.0.15 game, sticky actions 0.1 (MinAtar's own wrapper,
difficulty ramping on), actions sampled from softmax(logits), episodes cut at 10,000 steps, mean score per episode.
Observation: 10x10x6 binary grid, input index (row*10+col)*6+channel, channels built from the game's own channels as
stated in the upstream exp5 prompts (OBS_MAP).

Determinism: an episode is fully determined by (weights, seed): the environment RNG is seeded with `seed`, the
policy's action sampling uses an independent numpy Generator seeded with (seed, 1). Gold and candidates evaluated on the
same seeds are therefore paired.
"""
import multiprocessing as mp
import time

import numpy as np

# game -> list of (output channel, [game channel names]); from exp5 runs/<game>/message.txt "How the 6 channels are built"
OBS_MAP = {
    "seaquest": [(0, ["sub_front", "sub_back"]), (1, ["enemy_fish", "enemy_sub", "enemy_bullet"]),
                 (2, ["enemy_fish", "enemy_sub", "diver"]), (3, ["friendly_bullet"]), (4, ["trail", "sub_back"]),
                 (5, ["oxygen_guage", "diver_guage"])],
    "asterix": [(0, ["player"]), (1, ["enemy"]), (2, ["gold"]), (4, ["trail"])],
    "breakout": [(0, ["paddle"]), (2, ["brick"]), (3, ["ball"]), (4, ["trail"])],
}
NAMES = ("W1", "b1", "W2", "b2", "W3", "b3")
SHAPES = {"W1": (600, 32), "b1": (32,), "W2": (32, 32), "b2": (32,), "W3": (32, 6), "b3": (6,)}
MAX_STEPS = 10_000
EXP5_KEYS = {"actor/dense1/kernel": "W1", "actor/dense1/bias": "b1", "actor/dense2/kernel": "W2",
             "actor/dense2/bias": "b2", "actor/logits/kernel": "W3", "actor/logits/bias": "b3"}


def from_exp5(tensors):
    """Upstream exp5 hand.npz keys -> W1..b3 (values unchanged, float32)."""
    return {EXP5_KEYS[k]: np.asarray(v, dtype=np.float32) for k, (_, v) in tensors.items()}


def obs_builder(game, channels):
    src = []
    for out_c, names in OBS_MAP[game]:
        for n in names:
            src.append((out_c, channels[n]))

    def build(state):
        o = np.zeros((10, 10, 6), dtype=np.float32)
        for out_c, gc in src:
            o[:, :, out_c] = np.maximum(o[:, :, out_c], state[:, :, gc])
        return o.reshape(-1)
    return build


def policy_logits(w, x):
    h1 = np.tanh(x @ w["W1"] + w["b1"])
    h2 = np.tanh(h1 @ w["W2"] + w["b2"])
    return h2 @ w["W3"] + w["b3"]


def _trace_row(env, a, r):
    e = env.env
    row = {"a": int(a), "r": float(r)}
    for k in ("sub_x", "sub_y", "oxygen", "diver_count", "surface", "sub_or"):
        if hasattr(e, k):
            v = getattr(e, k)
            row[k] = v if isinstance(v, (int, float, bool)) else int(v)
    return row


def run_batch(args):
    """Run episodes for `seeds` in lockstep (batched MLP). Returns list of dicts."""
    game, weights, seeds, trace_seeds, max_steps = args
    from minatar import Environment
    w = {k: np.asarray(weights[k], dtype=np.float64) for k in NAMES}
    envs, rngs = [], []
    for s in seeds:
        env = Environment(game, sticky_action_prob=0.1)
        env.seed(int(s))
        env.reset()
        envs.append(env)
        rngs.append(np.random.default_rng([int(s), 1]))
    build = obs_builder(game, envs[0].env.channels)
    n = len(seeds)
    score = np.zeros(n)
    length = np.zeros(n, dtype=np.int64)
    alive = np.ones(n, dtype=bool)
    actions = np.zeros((n, 6), dtype=np.int64)
    traces = {int(s): [] for s in trace_seeds}
    t = 0
    while alive.any() and t < max_steps:
        idx = np.flatnonzero(alive)
        x = np.stack([build(envs[i].state()) for i in idx]).astype(np.float64)
        lg = policy_logits(w, x)
        lg = lg - lg.max(1, keepdims=True)
        p = np.exp(lg)
        p /= p.sum(1, keepdims=True)
        for j, i in enumerate(idx):
            a = int(min(np.searchsorted(np.cumsum(p[j]), rngs[i].random(), side="right"), 5))
            r, term = envs[i].act(a)
            score[i] += r
            length[i] += 1
            actions[i, a] += 1
            if int(seeds[i]) in traces:
                traces[int(seeds[i])].append(_trace_row(envs[i], a, r))
            if term:
                alive[i] = False
        t += 1
    out = []
    for i, s in enumerate(seeds):
        d = {"seed": int(s), "score": float(score[i]), "length": int(length[i]), "truncated": bool(alive[i]),
             "action_counts": actions[i].tolist()}
        if int(s) in traces:
            d["trace"] = traces[int(s)]
        out.append(d)
    return out


def evaluate(game, weights, seeds, trace_seeds=(), workers=6, chunk=25, max_steps=MAX_STEPS):
    """Evaluate one policy on the given seeds. Returns (summary, per-episode list in seed order)."""
    for k in NAMES:
        a = np.asarray(weights[k])
        assert a.shape == SHAPES[k] and np.isfinite(a).all(), k
    seeds = [int(s) for s in seeds]
    jobs = [(game, {k: np.asarray(weights[k]) for k in NAMES}, seeds[i:i + chunk],
             [s for s in trace_seeds if s in seeds[i:i + chunk]], max_steps) for i in range(0, len(seeds), chunk)]
    t0 = time.time()
    if workers > 1 and len(jobs) > 1:
        with mp.get_context("spawn").Pool(min(workers, len(jobs))) as pool:
            parts = pool.map(run_batch, jobs)
    else:
        parts = [run_batch(j) for j in jobs]
    eps = [e for p in parts for e in p]
    sc = np.array([e["score"] for e in eps])
    summary = {"episodes": len(eps), "mean": float(sc.mean()), "se": float(sc.std(ddof=1) / np.sqrt(len(sc))) if len(sc) > 1 else None,
               "max": float(sc.max()), "mean_length": float(np.mean([e["length"] for e in eps])),
               "truncated": int(sum(e["truncated"] for e in eps)), "wall_s": round(time.time() - t0, 2),
               "steps": int(sum(e["length"] for e in eps))}
    return summary, eps


def paired(gold_eps, cand_eps):
    g = np.array([e["score"] for e in gold_eps])
    c = np.array([e["score"] for e in cand_eps])
    assert [e["seed"] for e in gold_eps] == [e["seed"] for e in cand_eps]
    d = c - g
    rng = np.random.default_rng(12345)
    boots = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)])
    return {"n": int(len(d)), "mean_diff": float(d.mean()), "se_diff": float(d.std(ddof=1) / np.sqrt(len(d))),
            "ci95_bootstrap": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
            "cand_better": int((d > 0).sum()), "cand_worse": int((d < 0).sum()), "ties": int((d == 0).sum())}
