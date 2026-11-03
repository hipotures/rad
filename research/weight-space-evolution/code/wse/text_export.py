"""Text-only Qwen3.5-0.8B export, as used by upstream exp8 for evaluation (Qwen3_5ForCausalLM).

    python -m wse.text_export --gold-id <id> [--patch-id <id>] --hf-dir <dir with tokenizer files> \
        --text-config-dir <upstream exp8_math/base_model/Qwen3.5-0.8B-text> --out <dir>

Keeps only model.language_model.* tensors (names unchanged, per upstream README), with an optional WSE patch chain
applied; vision tower and MTP head are dropped. Config/generation config/chat template come from the upstream
text-only export description; tokenizer files from the pinned Gold revision.
"""
import argparse
import json
import shutil
from pathlib import Path

from . import patch, registry
from .tensors import sha256_array, sha256_file, st_header, st_save


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold-id", required=True)
    ap.add_argument("--patch-id")
    ap.add_argument("--hf-dir", required=True)
    ap.add_argument("--text-config-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    gm = registry.manifest(a.gold_id)
    head, _ = st_header(registry.gold_dir(a.gold_id) / gm["file"])
    names = sorted(k for k in head if k.startswith("model.language_model."))
    tensors = patch.materialize(a.gold_id, a.patch_id, names)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    st_save(out / "model.safetensors", tensors, {"format": "pt"})
    for f in ("config.json", "generation_config.json", "chat_template.jinja", "tokenizer_config.json"):
        shutil.copyfile(Path(a.text_config_dir) / f, out / f)
    for f in ("tokenizer.json", "vocab.json", "merges.txt"):
        shutil.copyfile(Path(a.hf_dir) / f, out / f)
    rec = {"gold_id": a.gold_id, "patch_id": a.patch_id, "tensors": len(names),
           "model_sha256": sha256_file(out / "model.safetensors"),
           "tensor_sha256": {k: sha256_array(v[1]) for k, v in tensors.items()
                             if a.patch_id and k in {t["name"] for t in patch.load_patch(a.patch_id)["tensors"]}}}
    (out / "wse_export.json").write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec, indent=1))


if __name__ == "__main__":
    main()
