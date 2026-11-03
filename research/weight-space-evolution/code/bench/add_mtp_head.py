"""Derive '<text export>+MTP': the unchanged text-only export plus the Gold checkpoint's own MTP head (mtp.* tensors),
so vLLM's MTP speculative decoding (method "mtp", Qwen3_5MTP drafter) can be benchmarked on the same backbone weights.

    python -m bench.add_mtp_head --text-dir <work/derived/qwen3.5-0.8B-text-gold> \
        --gold-st <work/gold/qwen3.5-0.8B@2fc0636/weights.safetensors> --out <work/derived/qwen3.5-0.8B-text-gold-mtp>

The backbone file is hard-linked (byte-identical, same sha256); mtp.* tensors are copied byte-for-byte from the Gold
safetensors into model-mtp.safetensors; an index maps every tensor. The main model ignores mtp.* (vLLM WeightsMapper),
so target-model outputs are those of the text export. Note: a WSE patch never touches the MTP head, so for patched
candidates the drafter is Gold's (acceptance may differ; outputs are still verified by the target model).
"""
import argparse
import hashlib
import json
import os
import shutil
import struct
from pathlib import Path


def header(p):
    with open(p, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        return json.loads(f.read(n)), 8 + n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-dir", required=True)
    ap.add_argument("--gold-st", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    src, out = Path(a.text_dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=False)
    for f in src.iterdir():
        if f.name == "model.safetensors":
            os.link(f, out / f.name)
        else:
            shutil.copyfile(f, out / f.name)
    h, off = header(a.gold_st)
    names = sorted(k for k in h if k.startswith("mtp."))
    new_h, data, pos = {"__metadata__": {"format": "pt"}}, [], 0
    with open(a.gold_st, "rb") as f:
        for k in names:
            s, e = h[k]["data_offsets"]
            f.seek(off + s)
            b = f.read(e - s)
            new_h[k] = {"dtype": h[k]["dtype"], "shape": h[k]["shape"], "data_offsets": [pos, pos + len(b)]}
            data.append(b)
            pos += len(b)
    hb = json.dumps(new_h, separators=(",", ":")).encode()
    hb += b" " * (-len(hb) % 8)
    with open(out / "model-mtp.safetensors", "wb") as f:
        f.write(struct.pack("<Q", len(hb)) + hb)
        for b in data:
            f.write(b)
    main_h, _ = header(src / "model.safetensors")
    wm = {k: "model.safetensors" for k in main_h if k != "__metadata__"}
    wm.update({k: "model-mtp.safetensors" for k in names})
    (out / "model.safetensors.index.json").write_text(json.dumps({"metadata": {}, "weight_map": wm}, indent=1))
    sha = hashlib.sha256(open(out / "model-mtp.safetensors", "rb").read()).hexdigest()
    rec = {"source_text_export": str(src.name), "mtp_tensors": len(names), "mtp_bytes": pos,
           "model_mtp_sha256": sha, "backbone_hardlinked": True}
    (out / "wse_mtp_head.json").write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
