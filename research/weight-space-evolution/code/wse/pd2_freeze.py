"""Freeze the Phase D v2 protocol: apply the pre-registered cell acceptance rule (protocol_v2_draft.json) to the
pilot results and write protocol_v2_frozen.json plus split manifests (wse environment).

    python -m wse.pd2_freeze --pilot <runs/.../results/editor_results_pilot.json> --out-dir configs/phaseD_v2
"""
import argparse
import hashlib
import json
from pathlib import Path

from . import pd2_bench as B


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out_dir)
    draft = json.loads((out / "protocol_v2_draft.json").read_text())
    R = json.loads(Path(a.pilot).read_text())
    E0 = R["editors"]["E0"]["cells"]
    cells = {}
    for fam in ("F1", "F2", "F3", "F4"):
        bl = R["baselines"][fam]
        for t in ("T0", "T1", "T2", "T2P"):
            c = E0[f"{fam}/{t}"]
            crit = {"oracle>=0.90": bl["oracle"] >= 0.90, "simple_heuristic<=0.60": bl["heuristic_simple"] <= 0.60,
                    "E0<=0.80": c["mean_recovery"] <= 0.80, "E0_valid>=0.50": c["valid_rate"] >= 0.50}
            if t == "T0":
                crit["t0_chance<=0.40"] = bl["t0_chance"] <= 0.40
            cells[f"{fam}/{t}"] = {"accepted": all(crit.values()), "criteria": crit, "floor": c["mean_recovery"] <= 0.02,
                                   "E0_mean_recovery": c["mean_recovery"], "E0_valid_rate": c["valid_rate"],
                                   "oracle": bl["oracle"], "heuristic_simple": bl["heuristic_simple"],
                                   "heuristic_improved": bl["heuristic_improved"], "t0_chance": bl["t0_chance"]}
    manifests = {}
    (out / "manifests").mkdir(exist_ok=True)
    for split in ("pilot", "dev", "select", "test", "transfer"):
        rows = B.manifest(split)
        body = {"version": B.VERSION, "split": split, "n": len(rows), "aggregate": B.aggregate(rows)}
        full = json.dumps(rows, sort_keys=True).encode()
        body["manifest_sha256"] = hashlib.sha256(full).hexdigest()
        if split in B.PUBLIC_SPLITS:
            body["instances"] = rows
        else:
            (B.bench_dir() / f"manifest-{split}.json").write_bytes(full)
            body["note"] = "held-out split: per-instance manifest kept in work/ (secret); only aggregates and its hash are public"
        (out / "manifests" / f"{split}.json").write_text(json.dumps(body, indent=1))
        manifests[split] = {"n": len(rows), "manifest_sha256": body["manifest_sha256"]}
    frozen = dict(draft)
    frozen["status"] = "FROZEN 2026-11-03 after the v2 Gold/p50c pilot; any change requires a new benchmark version"
    frozen["salt_sha256"] = B.salt_commitment()
    frozen["manifests"] = manifests
    frozen["cells"] = cells
    frozen["primary_cells"] = sorted(k for k, v in cells.items() if v["accepted"])
    frozen["excluded_cells"] = sorted(k for k, v in cells.items() if not v["accepted"])
    frozen["pilot_results"] = "runs/20261103T-phaseD-v2-pilot/results/editor_results_pilot.json"
    (out / "protocol_v2_frozen.json").write_text(json.dumps(frozen, indent=1))
    print("primary:", frozen["primary_cells"])
    print("excluded:", {k: [c for c, ok in cells[k]["criteria"].items() if not ok] for k in frozen["excluded_cells"]})
    print(manifests)


if __name__ == "__main__":
    main()
