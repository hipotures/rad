"""Discriminating probe of run-to-run variation of sampled outputs in one vLLM engine (vLLM environment).

    python -m wse.determinism_probe --engine-json '{...}' --out <json>

Sequence in one engine: S, S, S (prefix cache reset before each), G, S, G, S (no reset in between), and finally
S after reset. S = sampled case (144 Phase D v1 prompts, n = 4, seed 0, 256 tokens), G = greedy case (64 tokens).
If S hashes differ only when preceded by G without a reset, prefix-cache state (not timing) drives the variation.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wse import work_root  # noqa: E402
from wse.swap_engine import PersistentEngine  # noqa: E402
from wse.swap_test import build_cases, run_cases  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine-json", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    gold = str(work_root() / "derived/qwen3.5-0.8B-text-gold")
    eng = PersistentEngine(gold, json.loads(a.engine_json), mode="direct", name="detprobe")
    cases = build_cases(gold, "full")
    G = {"greedy": cases["greedy"]}
    S = {"sampled": cases["sampled"]}
    log = []
    for step, (lab, reset) in enumerate([("S", 1), ("S", 1), ("S", 1), ("G", 1), ("S", 0), ("G", 0), ("S", 0), ("S", 1)]):
        if reset:
            assert eng.llm.reset_prefix_cache()
        r = run_cases(eng, G if lab == "G" else S, reset=False)
        c = list(r.values())[0]
        log.append({"step": step, "case": lab, "reset_before": bool(reset), "sha256": c["sha256"][:16],
                    "per_request": c["per_request"]})
        print(step, lab, reset, c["sha256"][:16], flush=True)
    Path(a.out).write_text(json.dumps({"engine": eng.kw, "log": log}))
    eng.shutdown()
    os._exit(0)


if __name__ == "__main__":
    main()
