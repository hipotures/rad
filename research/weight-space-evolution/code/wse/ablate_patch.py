"""Operator post-hoc ablation: build a patch keeping only some tensors of an existing patch (admin, not an editor tool).

    python -m wse.ablate_patch PATCH_ID --keep W1 [b1 ...] --rationale "..."

The new patch is parented to Gold (not to PATCH_ID) and labelled as an operator ablation in its metadata.
"""
import argparse
import json

from . import patch, work_root


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("patch_id")
    ap.add_argument("--keep", nargs="+", required=True)
    ap.add_argument("--rationale", required=True)
    a = ap.parse_args(argv)
    meta = json.loads((work_root() / "patches" / a.patch_id / "patch.json").read_text())
    src = patch.materialize(meta["gold_id"], a.patch_id)
    edits = {k: v[1].copy() for k, v in src.items() if k in a.keep}
    edited = {t["name"] for t in meta["tensors"]}
    assert set(a.keep) <= edited, (a.keep, edited)
    p = patch.create(meta["gold_id"], edits, meta["policy"],
                     {"method": "operator post-hoc ablation", "source_patch": a.patch_id, "kept_tensors": a.keep,
                      "rationale": a.rationale})
    print(json.dumps({"patch_id": p["patch_id"], "changed_entries_total": p["changed_entries_total"]}))


if __name__ == "__main__":
    main()
