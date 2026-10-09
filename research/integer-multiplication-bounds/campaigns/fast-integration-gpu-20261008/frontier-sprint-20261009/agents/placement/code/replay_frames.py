#!/usr/bin/env python3
"""Replay an explicit frame fixture without modifying its pinned source tree.

This invokes the inherited physical checker and independently recounts its
complete histogram through the placement ledger. It is not the independent
signed/reflected reviewer or an all-size theorem checker.
"""
import argparse
import json
from pathlib import Path
import sys

from physical_search import Physical, require, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--frames", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, "assertion-disabled execution is unsupported")
    require(not args.output.exists(), "output already exists")
    model = Physical(args.source.resolve(), args.export.resolve(), 5885669 / 10**10)
    payload = json.loads(args.frames.read_text())
    changed = payload["frames"] if isinstance(payload, dict) else payload
    require(isinstance(changed, list), "frames must be a list")
    model.frames = list(model.original)
    seen = set()
    for row in changed:
        require(isinstance(row, list) and len(row) == 2, "invalid frame row")
        i, F = row
        require(type(i) is int and 0 <= i < len(model.ops) and i not in seen, "invalid or duplicate operation index")
        require(isinstance(F, list) and all(type(x) is int and 0 < x < 1 << model.h for x in F), "invalid frame vector")
        require(model.basis(F) == tuple(F) != model.original[i], "noncanonical or unmoved frame")
        seen.add(i)
        model.frames[i] = tuple(F)
    local = model.validate()
    histogram = model.histogram()
    physical = model.compiler.physical(model.g, model.witness, model.word, model.record, changed, model.pairs)
    require({int(r): c for r, c in physical["child_histogram"].items()} == histogram, "histogram disagreement")
    result = {"status": "INHERITED_PHYSICAL_REPLAY", "frames_sha256": sha(args.frames),
              "checks": local, "physical": physical,
              "exclusions": ["independent reflected geometry", "rigorous moments", "assembly", "all-size hypotheses"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "changed_operation_frames": len(changed),
                      "rank_per_vertex": physical["rank_per_vertex"], "W_per_vertex": physical["W_per_vertex"]}))


if __name__ == "__main__":
    main()
