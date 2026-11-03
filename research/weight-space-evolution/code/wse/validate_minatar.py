"""Validate the MinAtar evaluator against upstream exp5 published scores (eval/minatar_eval.json, `hand` entries).

    python -m wse.validate_minatar --exp5 <upstream exp5_write_from_scratch> --games seaquest,asterix \
        --episodes 1000 --seed-base 0 --out <results.json>

Different episode seeds than upstream (their seeds are not published), so agreement is statistical: |z| of the
difference of means using both standard errors.
"""
import argparse
import json
import platform
from pathlib import Path

import numpy as np

from . import minatar_eval as M
from .tensors import npz_load, sha256_file


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp5", required=True)
    ap.add_argument("--games", default="seaquest,asterix")
    ap.add_argument("--episodes", type=int, default=1000)
    ap.add_argument("--seed-base", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    pub = json.load(open(Path(a.exp5) / "eval/minatar_eval.json"))
    import minatar
    res = {"protocol": "minatar 1.0.15, sticky 0.1, softmax sampling, 10k step cap", "episodes": a.episodes,
           "seed_base": a.seed_base, "python": platform.python_version(), "numpy": np.__version__,
           "minatar_version": getattr(minatar, "__version__", "1.0.15 (pip pin)"), "games": {}}
    for g in a.games.split(","):
        f = Path(a.exp5) / f"networks/{g}/hand.npz"
        w = M.from_exp5(npz_load(f))
        s, eps = M.evaluate(g, w, range(a.seed_base, a.seed_base + a.episodes), workers=a.workers)
        p = pub[g]["hand"]
        z = (s["mean"] - p["mean"]) / np.hypot(s["se"], p["se"])
        res["games"][g] = {"network": str(f.name), "network_sha256": sha256_file(f), "ours": s, "published": p,
                           "z_vs_published": float(z), "consistent_at_3se": bool(abs(z) < 3)}
        print(g, json.dumps(res["games"][g]))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
