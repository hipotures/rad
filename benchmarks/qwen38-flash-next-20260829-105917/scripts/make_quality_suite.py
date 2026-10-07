#!/usr/bin/env python3
"""Generate the deterministic quality/correctness request suite."""

import json
from pathlib import Path


out = Path("/srv/ai/benchmarks/qwen38-flash-next-20260829-105917/prompts/quality-suite.json")
needle = "NEEDLE-CODE-7F3A9C"
records = [
    {
        "id": "coding",
        "n_predict": 700,
        "prompt": (
            "Implement Python function `merge_intervals(items)` where items is an iterable of integer "
            "pairs. Normalize reversed endpoints, merge overlapping and directly adjacent closed intervals, "
            "return sorted tuples, do not mutate input, and raise ValueError for a pair not of length two. "
            "Return only one fenced Python code block containing the function and any imports."
        ),
    },
    {
        "id": "reasoning",
        "n_predict": 500,
        "prompt": (
            "A box contains 3 red and 2 blue balls. Draw two without replacement. Given that at least one "
            "drawn ball is red, compute the probability both are red. Explain using exact counts, then end "
            "with exactly `ANSWER: p/q` in lowest terms."
        ),
    },
    {
        "id": "structured_json",
        "n_predict": 220,
        "prompt": (
            "Return only strict JSON, with no code fence or commentary. It must have exactly these keys in "
            "this order: `status`, `values`, `meta`. status is string `ok`; values is array [2,3,5,7]; meta "
            "is an object with exactly `count`:4 and `all_prime`:true."
        ),
    },
    {
        "id": "instruction_following",
        "n_predict": 120,
        "prompt": (
            "Write exactly three lines. Line 1 must be `ALPHA`. Line 2 must contain exactly five lowercase "
            "words separated by single spaces. Line 3 must be `OMEGA`. Do not add punctuation or blank lines."
        ),
    },
]

# Repetitive but position-addressable text gives a real ~32k-token retrieval test without external data.
paragraphs = []
for i in range(1, 1601):
    value = needle if i == 1273 else f"record-{i:04d}-ordinary"
    paragraphs.append(f"[{i:04d}] archive entry value={value}; category=blue; checksum=stable.")
long_prompt = (
    "The following archive has numbered entries. Find the unique value beginning with NEEDLE-CODE. "
    "Ignore all ordinary values. Return exactly the value and nothing else.\n\n"
    + "\n".join(paragraphs)
)
records.append({"id": "long_context_approx_32k", "n_predict": 40, "prompt": long_prompt})
out.write_text(json.dumps(records, indent=2), encoding="utf-8")
print(out, out.stat().st_size, needle)
