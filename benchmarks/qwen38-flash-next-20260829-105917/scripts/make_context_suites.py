#!/usr/bin/env python3
"""Generate deterministic context-occupancy request suites for server benchmarks."""

import json
from pathlib import Path


ROOT = Path("/srv/ai/benchmarks/qwen38-flash-next-20260829-105917")
PROMPTS = ROOT / "prompts"


def prompt(words: int) -> str:
    # ` alpha` is intentionally simple and close to one token on Qwen tokenizers.
    body = " alpha" * max(1, words - 24)
    return (
        "Retain the marker NEEDLE-7429. Read all filler, then state only "
        "NEEDLE-7429. Filler follows:" + body + " End marker NEEDLE-7429."
    )


def write(name: str, sizes: list[int], n_predict: int) -> None:
    rows = [{"id": f"approx_{size}", "prompt": prompt(size),
             "n_predict": n_predict} for size in sizes]
    (PROMPTS / name).write_text(json.dumps(rows), encoding="utf-8")


write("screen-512-8192.json", [512, 8192], 256)
write("medium-32k-64k.json", [32768, 65536], 128)
write("long-100k-120k.json", [102400, 122880], 128)
