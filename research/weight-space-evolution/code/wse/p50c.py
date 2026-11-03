"""Phase A: rebuild the published exp8 Qwen3.5-0.8B edits (p50c by default) from public Gold weights.

    python -m wse.p50c --gold-file <model.safetensors> --edit-dir <upstream exp8_math/runs/p50c/edit> \
        --out <results.json> [--write-checkpoint <dir> --hf-dir <dir with config/tokenizer>]

Independent of upstream apply_edit.py: parses the upstream edit format (sparse idx/val or low-rank factors + fixups),
checks the Gold tensor hash the edit was made on, rebuilds each tensor, checks the evaluated-checkpoint hash, counts
affected entries/columns/rows, then stores the result as a WSE patch (lineage: gold -> patch) and optionally writes
a full candidate checkpoint (Gold file with only those tensors replaced) for forward-pass evaluation.
"""
import argparse
import json
import os
import shutil
import time
from pathlib import Path

import numpy as np

from . import patch, registry
from .tensors import (bf16_bits_to_f32, f32_to_bf16_bits, sha256_array, sha256_file, st_header, st_load,
                      st_save)

QWEN_SOURCE = {"repo": "Qwen/Qwen3.5-0.8B", "revision": "2fc06364715b967f1860aea9cf38778875588b17",
               "file": "model.safetensors-00001-of-00001.safetensors",
               "lfs_sha256": "04b1c301231dd422b8860db31311ab2721511346a32cb1e079c4c4e5f1fe4696",
               "license": "apache-2.0"}
GOLD_ID = "qwen3.5-0.8B@2fc0636"


def rebuild(base_bits, t, z, i):
    if t["form"] == "lowrank":
        w = bf16_bits_to_f32(base_bits).astype(np.float64)
        a, b = z[f"t{i}_a"], z[f"t{i}_b"]
        for k in range(a.shape[1]):
            w = w + np.outer(a[:, k], b[k])
        e = f32_to_bf16_bits(w.astype(np.float32)).reshape(-1)
    elif t["form"] == "sparse":
        e = base_bits.copy().reshape(-1)
    else:
        raise ValueError(t["form"])
    e[z[f"t{i}_idx"]] = z[f"t{i}_val"]
    return e.reshape(base_bits.shape)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold-file", required=True)
    ap.add_argument("--edit-dir", required=True)
    ap.add_argument("--run-name", default="p50c")
    ap.add_argument("--out", required=True)
    ap.add_argument("--write-checkpoint")
    ap.add_argument("--hf-dir")
    a = ap.parse_args(argv)
    t0 = time.time()
    res = {"run": a.run_name, "gold_source": QWEN_SOURCE, "checks": {}}
    fsha = sha256_file(a.gold_file)
    res["checks"]["gold_file_sha256_matches_hf_lfs"] = fsha == QWEN_SOURCE["lfs_sha256"]
    assert res["checks"]["gold_file_sha256_matches_hf_lfs"], fsha
    head, _ = st_header(a.gold_file)
    lm = [k for k in head if k.startswith("model.language_model.")]
    res["gold_tensor_count"] = len(head) - ("__metadata__" in head)
    res["gold_language_model_tensors"] = len(lm)
    gm = registry.register(GOLD_ID, a.gold_file, QWEN_SOURCE, link=True)
    res["gold_registered"] = {"gold_id": GOLD_ID, "tensors": len(gm["tensors"]), "readonly_verified": registry.verify(GOLD_ID)}

    man = json.load(open(Path(a.edit_dir) / "manifest.json"))
    res["upstream_manifest_sha256"] = sha256_file(Path(a.edit_dir) / "manifest.json")
    res["upstream_edit_npz_sha256"] = sha256_file(Path(a.edit_dir) / "edit.npz")
    names = [t["name"] for t in man["tensors"]]
    gold = registry.load(GOLD_ID, names)
    proposed, per = {}, []
    with np.load(Path(a.edit_dir) / "edit.npz", allow_pickle=False) as z:
        for i, t in enumerate(man["tensors"]):
            dt, b = gold[t["name"]]
            assert dt == "BF16" and list(b.shape) == t["shape"], (t["name"], dt, b.shape)
            base_ok = sha256_array(b) == t["base_sha256"]
            e = rebuild(b, t, z, i)
            edited_ok = sha256_array(e) == t["edited_sha256"]
            mask = e != b
            d = bf16_bits_to_f32(e).astype(np.float64) - bf16_bits_to_f32(b).astype(np.float64)
            # Direction check: is the column-wise change rank-1-like (one shared direction)?
            cols = np.flatnonzero(mask.any(0))
            sv = np.linalg.svd(d[:, cols], compute_uv=False) if cols.size else np.zeros(1)
            rec = {"name": t["name"], "shape": t["shape"], "form": t["form"], "base_sha256_ok": base_ok,
                   "edited_sha256_ok": edited_ok,
                   "changed_entries": int(mask.sum()), "manifest_changed_entries": t["changed_entries"],
                   "changed_columns": int(mask.any(0).sum()), "changed_rows": int(mask.any(1).sum()),
                   "changed_column_indices": cols.tolist() if cols.size <= 256 else f"{cols.size} columns (list omitted)",
                   "relative_change": float(np.linalg.norm(d) / np.linalg.norm(bf16_bits_to_f32(b).astype(np.float64))),
                   "manifest_relative_change": t.get("relative_change"),
                   "delta_top_singular_values": [float(x) for x in sv[:4]],
                   "delta_rank1_energy_share": float(sv[0] ** 2 / max((sv ** 2).sum(), 1e-30))}
            per.append(rec)
            proposed[t["name"]] = e
    res["tensors"] = per
    res["checks"]["all_base_hashes_ok"] = all(r["base_sha256_ok"] for r in per)
    res["checks"]["all_edited_hashes_ok"] = all(r["edited_sha256_ok"] for r in per)
    res["checks"]["changed_entries_match_manifest"] = all(r["changed_entries"] == r["manifest_changed_entries"] for r in per)
    res["changed_entries_total"] = sum(r["changed_entries"] for r in per)
    res["touched_columns_x_rows"] = sum(r["changed_columns"] * r["shape"][0] for r in per)
    policy = {"allowed_tensors": names, "max_abs_value": 1e4, "max_changed_entries": 10 ** 9,
              "forbid_uniform_scale": True}
    prec = patch.create(GOLD_ID, proposed, policy,
                        meta={"method": f"import of upstream exp8 {a.run_name} edit (gpt-6-astra)",
                              "source": "github.com/RikiyaT/lm_understand-logs@4d09ba6d6a7e891dd8063974dfe81b3d78e3494f",
                              "author": "upstream", "rationale": "Phase A reconstruction"})
    rebuilt = patch.materialize(GOLD_ID, prec["patch_id"], names)
    res["wse_patch"] = {"patch_id": prec["patch_id"], "delta_sha256": prec["delta_sha256"],
                        "roundtrip_hashes_ok": all(sha256_array(rebuilt[t["name"]][1]) == t["edited_sha256"]
                                                   for t in man["tensors"])}
    if a.write_checkpoint:
        out = Path(a.write_checkpoint)
        out.mkdir(parents=True, exist_ok=True)
        full = st_load(registry.gold_dir(GOLD_ID) / gm["file"])
        full = {k: v for k, v in full.items()}
        for k, (dt, arr) in rebuilt.items():
            full[k] = (dt, arr)
        ck = out / QWEN_SOURCE["file"]
        st_save(ck, full, {"format": "pt"})
        for f in os.listdir(a.hf_dir):
            if not f.endswith(".safetensors") and (Path(a.hf_dir) / f).is_file():
                shutil.copyfile(Path(a.hf_dir) / f, out / f)
        chk = st_load(ck, names)
        res["candidate_checkpoint"] = {"file_sha256": sha256_file(ck), "edited_tensor_hashes_ok": all(
            sha256_array(chk[t["name"]][1]) == t["edited_sha256"] for t in man["tensors"])}
        other = st_load(ck, [n for n in lm[:50] if n not in names])
        g2 = registry.load(GOLD_ID, list(other))
        res["candidate_checkpoint"]["sampled_untouched_tensors_identical"] = all(
            np.array_equal(other[k][1], g2[k][1]) for k in other)
    res["gold_verify_after"] = registry.verify(GOLD_ID)
    res["wall_s"] = round(time.time() - t0, 1)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "tensors"}, indent=1))
    for r in per:
        print(r["name"], {k: r[k] for k in ("changed_entries", "changed_columns", "changed_rows", "relative_change",
                                            "base_sha256_ok", "edited_sha256_ok", "delta_rank1_energy_share")})


if __name__ == "__main__":
    main()
