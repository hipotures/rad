"""Export compact, Git-friendly copies of WSE patches (admin): patch.json + sparse delta vs Gold.

    python -m wse.export_patches --out DIR PATCH_ID [PATCH_ID ...]

The delta lists, per tensor, flat indices of changed entries and their new values (float32 Gold networks).
"""
import argparse
import json
import shutil
from pathlib import Path

import numpy as np

from . import patch, work_root


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("ids", nargs="+")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for pid in a.ids:
        meta = json.loads((work_root() / "patches" / pid / "patch.json").read_text())
        gold = patch.materialize(meta["gold_id"], None)
        cand = patch.materialize(meta["gold_id"], pid)
        delta = {}
        for name, (_, v) in cand.items():
            g = np.asarray(gold[name][1]).ravel()
            c = np.asarray(v).ravel()
            idx = np.flatnonzero(g != c)
            if idx.size:
                delta[name] = {"flat_indices": idx.tolist(), "new_values": c[idx].astype(float).tolist()}
        shutil.copyfile(work_root() / "patches" / pid / "patch.json", out / f"{pid}.json")
        (out / f"{pid}.delta.json").write_text(json.dumps(delta))
        print(pid, sum(len(d["flat_indices"]) for d in delta.values()), meta["changed_entries_total"])


if __name__ == "__main__":
    main()
