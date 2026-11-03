"""Joint held-out comparison of several submitted candidates on ONE fresh, shared seed set (admin only).

    python -m wse.compare_candidates --sessions S1 S2 ... --out-dir <run dir> --raw-dir <dir> [--episodes 2000]

Seeds: base drawn with `secrets` at run time (>= 3e9, disjoint from dev < 1e9 and per-session held-out [2e9, 2.1e9)),
recorded in protocol.json before any rollout. Every candidate and Gold play the same seeds (paired). Sessions that submitted the same patch id share one arm. Reports each
candidate vs Gold, pairwise candidate differences, and Holm-adjusted two-sided p-values (normal approximation) for the
candidate-vs-Gold tests.
"""
import argparse
import json
import math
import secrets
import time
from pathlib import Path

import numpy as np

from . import minatar_eval as M
from .lab import jload, sdir, weights_of


def p_two_sided(mean, se):
    if not se:
        return 1.0 if mean == 0 else 0.0
    return math.erfc(abs(mean / se) / math.sqrt(2))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", nargs="+", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--raw-dir", required=True)
    ap.add_argument("--episodes", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--extra-patches", nargs="*", default=[],
                    help="additional (non-submitted, e.g. post-hoc ablation) patch ids; labelled in protocol.json")
    a = ap.parse_args(argv)
    out = Path(a.out_dir)
    (out / "results").mkdir(parents=True, exist_ok=True)
    assert not (out / "results" / "comparison.json").exists(), "never overwritten"
    cfgs = {s: jload(sdir(s) / "config.json") for s in a.sessions}
    sts = {s: jload(sdir(s) / "state.json") for s in a.sessions}
    games = {(c["game"], c["gold_id"]) for c in cfgs.values()}
    assert len(games) == 1, games
    cands = {}                                   # one arm per distinct submitted patch id; sessions recorded
    for s in a.sessions:
        if sts[s]["submitted"]:
            cands.setdefault(sts[s]["submitted"], []).append(s)
    for pid in a.extra_patches:
        cands.setdefault(pid, []).append("extra (not a submission)")
    base = 3_000_000_000 + secrets.randbelow(100_000_000)
    proto = {"sessions": a.sessions, "candidates": cands, "episodes": a.episodes, "seed_base": base,
             "seed_drawn_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "game": next(iter(games))[0],
             "gold_id": next(iter(games))[1]}
    (out / "protocol.json").write_text(json.dumps(proto, indent=1))
    cfg0 = next(iter(cfgs.values()))
    seeds = range(base, base + a.episodes)
    eps, res = {}, {"protocol": proto, "arms": {}}
    for name in ["gold", *cands]:
        s, e = M.evaluate(cfg0["game"], weights_of(cfg0, name), seeds, workers=a.workers)
        eps[name] = e
        res["arms"][name] = {"patch_id": name, "sessions": cands.get(name, []), "summary": s}
        print(name, json.dumps(s))
    names = list(cands)
    vs = {n: M.paired(eps["gold"], eps[n]) for n in names}
    ps = [p_two_sided(vs[n]["mean_diff"], vs[n]["se_diff"]) for n in names]
    for n, p, q in zip(names, ps, holm(ps)):
        vs[n].update(p_two_sided=p, p_holm=q)
    res["vs_gold"] = vs
    res["pairwise"] = {f"{x}-{y}": M.paired(eps[y], eps[x]) for i, x in enumerate(names) for y in names[i + 1:]}
    (out / "results" / "comparison.json").write_text(json.dumps(res, indent=1))
    Path(a.raw_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(a.raw_dir) / "comparison_episodes.json", "w") as f:
        json.dump({k: [{x: e[x] for x in ("seed", "score", "length")} for e in v] for k, v in eps.items()}, f)
    print(json.dumps({n: {k: vs[n][k] for k in ("mean_diff", "se_diff", "p_holm")} for n in names}, indent=1))


if __name__ == "__main__":
    main()
