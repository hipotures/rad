"""Held-out verification of a submitted candidate (admin only; never available to the editor).

    python -m wse.heldout --session S --out-dir <run dir> [--episodes 1000] [--control-seeds 3]

Test seeds: a base drawn with `secrets` AFTER submission (disjoint range >= 2e9; development seeds are < 1e9), written
to protocol.json before any test rollout. All arms play the same seeds (paired):
  gold          unchanged Gold
  candidate     the submitted patch
  flip          Gold - delta (same edit locations and size, opposite direction)
  permuted_i    the same delta values moved to random positions inside the same tensors (per tensor, same count;
                positions exclude the candidate's own edited entries when the tensor has room)
  gaussian_i    random positions (same count per tensor) with Gaussian deltas scaled to the same per-tensor L2
Controls are naive non-agent edits of matched size; they test whether the edit's location/direction matter.
"""
import argparse
import json
import secrets
import time
from pathlib import Path

import numpy as np

from . import minatar_eval as M
from . import patch
from .lab import jload, sdir, weights_of


def controls(gold, cand, n_seeds):
    out = {"flip": {k: gold[k] - (cand[k] - gold[k]) for k in gold}}
    for s in range(n_seeds):
        rng = np.random.default_rng([2026, s])
        perm, gau = {}, {}
        for k in gold:
            g, d = gold[k].astype(np.float64), (cand[k].astype(np.float64) - gold[k].astype(np.float64))
            idx = np.flatnonzero(d)
            if idx.size == 0:
                perm[k] = gold[k].copy()
                gau[k] = gold[k].copy()
                continue
            # positions outside the candidate's own edited entries when the tensor has room (else anywhere)
            pool = np.setdiff1d(np.arange(g.size), idx) if g.size - idx.size >= idx.size else np.arange(g.size)
            pos = rng.choice(pool, idx.size, replace=False)
            p = g.reshape(-1).copy()
            p[pos] += d.reshape(-1)[idx]
            perm[k] = p.reshape(g.shape).astype(np.float32)
            pos2 = rng.choice(pool, idx.size, replace=False)
            z = rng.standard_normal(idx.size)
            z *= np.linalg.norm(d) / np.linalg.norm(z)
            q = g.reshape(-1).copy()
            q[pos2] += z
            gau[k] = q.reshape(g.shape).astype(np.float32)
        out[f"permuted_{s}"] = perm
        out[f"gaussian_{s}"] = gau
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--episodes", type=int, default=1000)
    ap.add_argument("--control-seeds", type=int, default=3)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--raw-dir", required=True, help="disk directory for per-episode records (packed as evidence later)")
    a = ap.parse_args(argv)
    cfg = jload(sdir(a.session) / "config.json")
    st = jload(sdir(a.session) / "state.json")
    pid = st["submitted"]
    assert pid, "nothing submitted"
    out = Path(a.out_dir)
    (out / "results").mkdir(parents=True, exist_ok=True)
    proto_p = out / "protocol.json"
    assert not (out / "results" / "heldout.json").exists(), "held-out result exists; never overwritten"
    base = 2_000_000_000 + secrets.randbelow(100_000_000)
    rec = patch.load_patch(pid)
    proto = {"session": a.session, "submitted_patch": pid, "patch_delta_sha256": rec["delta_sha256"],
             "gold_id": cfg["gold_id"], "game": cfg["game"], "episodes": a.episodes, "test_seed_base": base,
             "test_seeds": [base, base + a.episodes - 1], "seed_drawn_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "submitted_utc": st.get("submitted_utc"), "control_seeds": a.control_seeds,
             "dev_seed_range": [cfg["dev_seed_base"], cfg["dev_seed_base"] + 10_000 * (cfg["budgets"]["dev_passes"] + 1)]}
    proto_p.write_text(json.dumps(proto, indent=1))
    gold = weights_of(cfg, "gold")
    cand = weights_of(cfg, pid)
    arms = {"gold": gold, "candidate": cand, **controls(gold, cand, a.control_seeds)}
    seeds = range(base, base + a.episodes)
    res, eps = {"protocol": proto, "arms": {}}, {}
    for name, w in arms.items():
        s, e = M.evaluate(cfg["game"], w, seeds, workers=a.workers)
        eps[name] = e
        delta = {k: int((w[k] != gold[k]).sum()) for k in gold}
        res["arms"][name] = {"summary": s, "changed_entries": sum(delta.values()),
                             "delta_l2": float(np.sqrt(sum(((w[k].astype(np.float64) - gold[k]) ** 2).sum() for k in gold)))}
        if name != "gold":
            res["arms"][name]["paired_vs_gold"] = M.paired(eps["gold"], e)
        print(name, json.dumps(res["arms"][name]["summary"]), json.dumps(res["arms"][name].get("paired_vs_gold")))
    ctrl = [k for k in arms if k not in ("gold", "candidate")]
    res["candidate_vs_controls"] = {k: M.paired(eps[k], eps["candidate"]) for k in ctrl}
    best = max(ctrl, key=lambda k: res["arms"][k]["summary"]["mean"])
    res["best_control"] = best
    c = res["arms"]["candidate"]["paired_vs_gold"]
    res["verdict"] = {
        "candidate_beats_gold_ci95": c["ci95_bootstrap"][0] > 0,
        "candidate_beats_best_control_ci95": res["candidate_vs_controls"][best]["ci95_bootstrap"][0] > 0,
    }
    (out / "results" / "heldout.json").write_text(json.dumps(res, indent=1))
    Path(a.raw_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(a.raw_dir) / "heldout_episodes.json", "w") as f:
        json.dump({k: [{x: e[x] for x in ("seed", "score", "length", "truncated")} for e in v] for k, v in eps.items()}, f)
    print(json.dumps(res["verdict"]))


if __name__ == "__main__":
    main()
