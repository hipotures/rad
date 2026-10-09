#!/usr/bin/env python3
"""Reproduce exact feasible-frame rank intervals for equal-frame components."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import random


def main():
    parser = argparse.ArgumentParser()
    for key in ("source", "export", "placement-code", "output"):
        parser.add_argument("--" + key, type=Path, required=True)
    parser.add_argument("--frames", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("output already exists")
    spec = importlib.util.spec_from_file_location("interval_search", args.placement_code)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    model = module.Physical(args.source.resolve(), args.export.resolve(), 0.0005885669)
    if args.frames:
        model.frames = list(model.original)
        for index, rows in json.loads(args.frames.read_text()):
            model.frames[index] = tuple(rows)
        model.validate()
    results = {}
    for policy in ("singletons", "components"):
        intervals, strict = Counter(), []
        groups = model.groups(policy, random.Random(20261009))
        for group in groups:
            lower, upper, _, _ = model.endpoints(group)
            ranks = len(lower), len(model.frames[group[0]]), len(upper)
            intervals[ranks] += 1
            if ranks[0] < ranks[1] < ranks[2]:
                strict.append({"group": group, "ranks": ranks,
                    "lower": lower, "current": model.frames[group[0]], "upper": upper})
        results[policy] = {"groups": len(groups), "strict_interior": strict,
                            "rank_intervals": [[*ranks, count] for ranks, count in sorted(intervals.items())]}
    results["frames_sha256"] = hashlib.sha256(args.frames.read_bytes()).hexdigest() if args.frames else None
    args.output.write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
    print(json.dumps({policy: {"groups": results[policy]["groups"],
        "strict_interior_groups": [entry["group"] for entry in results[policy]["strict_interior"]]}
        for policy in ("singletons", "components")}),flush=True)


if __name__ == "__main__":
    main()
