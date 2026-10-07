#!/usr/bin/env python3
"""Generate the three permitted formal Phase-3 retrieval/throughput prompts."""

import json
from pathlib import Path


ROOT = Path("/srv/ai/benchmarks/qwen38-flash-next-phase3-iq4xs-20260830-080504")
OUT = ROOT / "prompts" / "formal-32k-64k-128k.json"


def make_prompt(lane, filler_count):
    first = filler_count // 2
    second = filler_count - first
    nonce = f"PHASE3-{lane}-20260830-UNIQUE"
    prompt = (
        f"This is a deterministic long-context retrieval test with nonce {nonce}. "
        f"Remember BEGIN_{lane}=CITRUS-{lane}-17. "
        + "alpha " * first
        + f"Remember MIDDLE_{lane}=COBALT-{lane}-29. "
        + "alpha " * second
        + f"Remember END_{lane}=JASPER-{lane}-43. "
        + "Return exactly one compact JSON object with keys begin, middle, end and their remembered values."
    )
    return {
        "id": f"formal-{lane.lower()}",
        "lane": lane,
        "filler_tokens_requested": filler_count,
        "prompt": prompt,
        "n_predict": 512,
        "body": {"ignore_eos": True},
        "expected_values": [f"CITRUS-{lane}-17", f"COBALT-{lane}-29", f"JASPER-{lane}-43"],
    }


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps([
    make_prompt("32K", 31700),
    make_prompt("64K", 64300),
    make_prompt("128K", 122800),
], indent=2), encoding="utf-8")
print(OUT)
