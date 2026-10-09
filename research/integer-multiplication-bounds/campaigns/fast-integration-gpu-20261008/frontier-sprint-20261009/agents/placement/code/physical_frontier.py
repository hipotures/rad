#!/usr/bin/env python3
"""Bounded connected frame exchanges against an exact complex trial target.

The pinned scalar DAG, gauges, aliases and compensation deadlines are fixed.
Every group receives one common endpoint frame only when its exact legal
interval is nonempty. The complete paid histogram is recounted and passed to
the inherited physical checker. Floating moments and rankings are DISCOVERY.
Prepared with OpenAI assistance; inherited Apache-2.0 attribution is retained.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import itertools
import json
import math
from pathlib import Path
import random
import resource
import sys
import time

from physical_exchanges import Exchanges
from physical_search import require, sha


class Frontier(Exchanges):
    def plan(self, group):
        inside = set(group)
        inc, out = self.boundary(group)
        lower = self.basis(tuple(x for i in group for x in self.spans[self.ops[i][2]])
                           + tuple(x for a, _ in inc for x in self.frame(a)))
        upper = self.basis(1 << i for i in range(self.h))
        for _, b in out:
            upper = self.cap(upper, self.frame(b))
        if not self.contained(lower, upper):
            return None, "infeasible"
        internal = [(a, b) for a in group for b in self.outgoing[a] if b in inside]
        old = math.fsum(self.f[len(self.frame(b)) - len(self.frame(a))] for a, b in inc + internal + out)

        def cost(F):
            d = len(F)
            return math.fsum([self.f[d - len(self.frame(a))] for a, _ in inc]
                             + [self.f[len(self.frame(b)) - d] for _, b in out])

        frame = min((lower, upper), key=lambda F: (cost(F), len(F), F))
        delta = cost(frame) - old
        if delta >= -1e-12:
            return None, "no_gain"
        return {"ops": list(group), "frame": list(frame), "old_ranks": [len(self.frames[i]) for i in group],
                "new_rank": len(frame), "delta_excess_local": delta, "internal_edges": len(internal)}, "accepted"

    def commit(self, plan):
        for i in plan["ops"]:
            self.frames[i] = tuple(plan["frame"])

    def larger_groups(self, policy, rng, max_nodes, group_limit):
        if policy == "singletons":
            return [(i,) for i in range(len(self.ops))], False
        if policy == "op-triples":
            groups = set()
            for i in range(len(self.ops)):
                for a, b in itertools.combinations(sorted(self.neighbors[i]), 2):
                    groups.add(tuple(sorted((i, a, b))))
            groups = sorted(groups)
        else:
            blocks = self.groups("components", rng)
            owner = {i: k for k, group in enumerate(blocks) for i in group}
            neighbors = defaultdict(set)
            for i in range(len(self.ops)):
                for j in self.neighbors[i]:
                    a, b = owner[i], owner[j]
                    if a != b:
                        neighbors[a].add(b)
            triples = set()
            for center in range(len(blocks)):
                for a, b in itertools.combinations(sorted(neighbors[center]), 2):
                    if len(blocks[center]) + len(blocks[a]) + len(blocks[b]) <= max_nodes:
                        triples.add(tuple(sorted((center, a, b))))
            groups = [tuple(sorted(blocks[a] + blocks[b] + blocks[c])) for a, b, c in sorted(triples)]
        truncated = len(groups) > group_limit
        if truncated:
            # Spread a bounded sample throughout the chronological index space.
            rng.shuffle(groups)
            groups = groups[:group_limit]
            groups.sort()
        return groups, truncated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--start-frames", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--policy", choices=["control", "singletons", "op-triples", "component-triples"], required=True)
    parser.add_argument("--order", choices=["alternating", "random", "gain-first"], default="alternating")
    parser.add_argument("--passes", type=int, default=3)
    parser.add_argument("--max-nodes", type=int, default=512)
    parser.add_argument("--group-limit", type=int, default=200000)
    parser.add_argument("--seed", type=int, default=20261009)
    parser.add_argument("--trial", type=Fraction, default=Fraction(594625849, 10**12))
    args = parser.parse_args()
    require(not sys.flags.optimize, "assertion-disabled execution is unsupported")
    require(not args.output.exists(), "attempt output already exists")
    require(0 < args.trial < 1 and args.passes > 0 and args.group_limit > 0, "invalid settings")
    args.output.mkdir(parents=True)
    started = time.monotonic()
    model = Frontier(args.source.resolve(), args.export.resolve(), float(args.trial))
    payload = json.loads(args.start_frames.read_text())
    changed = payload["frames"] if isinstance(payload, dict) else payload
    model.frames = list(model.original)
    seen = set()
    for i, F in changed:
        require(type(i) is int and 0 <= i < len(model.ops) and i not in seen, "invalid or duplicate operation index")
        require(all(type(x) is int and 0 < x < 1 << model.h for x in F), "invalid frame vector")
        require(model.basis(F) == tuple(F) != model.original[i], "noncanonical or unmoved frame")
        seen.add(i)
        model.frames[i] = tuple(F)
    model.validate()
    initial_frames = list(model.frames)
    start_histogram = model.histogram()
    rng = random.Random(args.seed)
    moves, passes = [], []
    if args.policy != "control":
        for k in range(args.passes):
            groups, truncated = model.larger_groups(args.policy, rng, args.max_nodes, args.group_limit)
            screened = None
            if args.order == "gain-first":
                plans = [model.plan(group)[0] for group in groups]
                screened = sum(plan is not None for plan in plans)
                groups = [tuple(plan["ops"]) for plan in sorted((p for p in plans if p is not None),
                                                               key=lambda p: (p["delta_excess_local"], p["ops"]))]
            elif args.order == "random":
                rng.shuffle(groups)
            elif k % 2:
                groups.reverse()
            counts = Counter()
            for group in groups:
                plan, status = model.plan(group)
                counts[status] += 1
                if plan:
                    model.commit(plan)
                    moves.append(plan)
            passes.append({"pass": k, "evaluated_groups": len(groups), "group_limit_truncated": truncated,
                           "screened_improving_groups": screened, **dict(counts)})
            print(json.dumps(passes[-1]), flush=True)
            if not counts["accepted"]:
                break
    local = model.validate()
    histogram = model.histogram()
    changed = [[i, list(F)] for i, F in enumerate(model.frames) if F != model.original[i]]
    frames_path = args.output / "frames.json"
    frames_path.write_text(json.dumps(changed, separators=(",", ":")) + "\n")
    (args.output / "moves.json").write_text(json.dumps(moves, separators=(",", ":")) + "\n")
    physical = model.compiler.physical(model.g, model.witness, model.word, model.record, changed, model.pairs)
    require({int(r): c for r, c in physical["child_histogram"].items()} == histogram, "complete histogram disagrees")
    (args.output / "physical-profile.json").write_text(json.dumps(physical, indent=2, sort_keys=True) + "\n")
    result = {"status": "DISCOVERY", "policy": args.policy, "order": args.order, "seed": args.seed,
              "requested_passes": args.passes, "max_nodes": args.max_nodes, "group_limit": args.group_limit,
              "trial_exact": str(args.trial), "passes": passes, "moves": len(moves),
              "m": model.m, "W_per_vertex": model.reference["W_per_vertex"],
              "rank_per_vertex": model.reference["rank_per_vertex"], "max_child": max(histogram),
              "frames_changed_from_start": sum(a != b for a, b in zip(initial_frames, model.frames)),
              "frames_changed_from_public": sum(a != b for a, b in zip(model.initial, model.frames)),
              "histogram": histogram, "start_moments": model.moments(start_histogram),
              "moments": model.moments(histogram), "local_checks": local, "upstream_physical_replay": True,
              "frames_sha256": sha(frames_path), "start_frames_sha256": sha(args.start_frames),
              "source_snapshot": args.source.name,
              "source_sha256": {name: sha(args.source / name) for name in
                                ("scripts/paired_cube_physical.py", "scripts/paired_cube/frames.py",
                                 "certificates/paired-cube-complex-input.json", "certificates/paired-cube-physical-input.json",
                                 "references/paired-cube/physical/frames.json", "references/paired-cube/physical/pairs.json")},
              "export_sha256": {name: sha(args.export / name) for name in ("graph.json", "frames.json", "selection.json")},
              "search_sha256": {name: sha(Path(__file__).parent / name) for name in
                                ("physical_search.py", "physical_exchanges.py", "physical_frontier.py")},
              "wall_seconds": time.monotonic() - started, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "exclusions": ["independent signed/reflected audit", "rigorous moments", "assembly certificate", "accepted final kappa"]}
    (args.output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("policy", "moves", "frames_changed_from_start", "moments", "wall_seconds")}), flush=True)


if __name__ == "__main__":
    main()
