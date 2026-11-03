"""Register an upstream exp5 hand-written MinAtar network as read-only Gold (keys renamed to W1..b3, values unchanged).

    python -m wse.register_minatar --exp5 <upstream exp5_write_from_scratch> --game seaquest
"""
import argparse
import json
from pathlib import Path

import numpy as np

from . import minatar_eval as M
from . import registry, work_root
from .tensors import npz_load, sha256_file

UPSTREAM = {"repo": "https://github.com/RikiyaT/lm_understand-logs", "commit": "4d09ba6d6a7e891dd8063974dfe81b3d78e3494f",
            "license": "CC BY 4.0 (networks)"}


def gold_id(game):
    return f"minatar-{game}-exp5-hand@4d09ba6"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp5", required=True)
    ap.add_argument("--game", default="seaquest")
    a = ap.parse_args(argv)
    src = Path(a.exp5) / f"networks/{a.game}/hand.npz"
    w = M.from_exp5(npz_load(src))
    d = work_root() / "derived" / f"minatar-{a.game}-hand"
    d.mkdir(parents=True, exist_ok=True)
    f = d / "weights.npz"
    if not f.exists():
        np.savez(f, **w)
    man = registry.register(gold_id(a.game), f, {**UPSTREAM, "path": f"exp5_write_from_scratch/networks/{a.game}/hand.npz",
                                                  "source_sha256": sha256_file(src), "key_map": M.EXP5_KEYS})
    print(json.dumps({"gold_id": man["gold_id"], "file_sha256": man["file_sha256"], "verify": registry.verify(man["gold_id"])}))


if __name__ == "__main__":
    main()
