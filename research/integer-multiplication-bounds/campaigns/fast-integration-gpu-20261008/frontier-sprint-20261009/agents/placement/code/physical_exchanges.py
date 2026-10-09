#!/usr/bin/env python3
"""Continue complete-moment placement with explicit joint frame collapses.

Uses the immutable paired-cube source through physical_search.Physical. Unlike
that search's equal-frame blocks, a group may have unequal current frames. The
common replacement is feasible only when span(values, external predecessors)
is contained in every external successor. Every affected paid transition,
including internal transitions removed by a collapse, is priced. Final profiles
are independently recounted and checked by the inherited physical compiler.

The output remains DISCOVERY until a separate signed/reflected audit, rigorous
moment enclosure, and complete assembly certificate have been performed.
Prepared with OpenAI assistance; inherited source attribution is unchanged.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
import resource
import time

from physical_search import Physical, require, sha


class Exchanges(Physical):
    def collapse(self, group):
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
        affected = inc + internal + out
        old = sum(self.f[len(self.frame(b)) - len(self.frame(a))] for a, b in affected)

        def cost(F):
            d = len(F)
            return sum(self.f[d - len(self.frame(a))] for a, _ in inc) + \
                sum(self.f[len(self.frame(b)) - d] for _, b in out)

        best = min((lower, upper), key=lambda F: (cost(F), len(F), F))
        delta = cost(best) - old
        if delta >= -1e-12:
            return None, "no_gain"
        old_ranks = [len(self.frames[i]) for i in group]
        for i in group:
            self.frames[i] = best
        return {"ops": list(group), "old_ranks": old_ranks, "new_rank": len(best),
                "delta_excess_local": delta, "internal_edges": len(internal)}, "accepted"

    def exchange_groups(self, policy, rng, max_nodes):
        if policy == "components":
            return self.groups("components", rng)
        if policy == "op-pairs":
            return [(i, j) for i in range(len(self.ops)) for j in sorted(self.neighbors[i]) if i < j]
        blocks = self.groups("components", rng)
        owner = {i: k for k, group in enumerate(blocks) for i in group}
        links = set()
        for i in range(len(self.ops)):
            for j in self.neighbors[i]:
                a, b = owner[i], owner[j]
                if a != b:
                    links.add(tuple(sorted((a, b))))
        return [tuple(sorted(blocks[a] + blocks[b])) for a, b in sorted(links)
                if len(blocks[a]) + len(blocks[b]) <= max_nodes]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--start-frames", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--policy", choices=["components", "op-pairs", "component-pairs"], required=True)
    parser.add_argument("--order", choices=["alternating", "reverse", "random", "largest-first"], default="alternating")
    parser.add_argument("--seed", type=int, default=20261009)
    parser.add_argument("--passes", type=int, default=6)
    parser.add_argument("--max-nodes", type=int, default=256)
    parser.add_argument("--trial", type=float, default=5885669 / 10**10)
    args = parser.parse_args()
    require(not args.output.exists(), "attempt output already exists")
    args.output.mkdir(parents=True)
    started = time.monotonic()
    model = Exchanges(args.source.resolve(), args.export.resolve(), args.trial)
    if args.start_frames:
        model.frames = list(model.original)
        payload = json.loads(args.start_frames.read_text())
        seen = set()
        for i, F in payload:
            require(type(i) is int and 0 <= i < len(model.ops) and i not in seen, "invalid start operation")
            require(model.basis(F) == tuple(F), "noncanonical start frame")
            seen.add(i)
            model.frames[i] = tuple(F)
    model.validate()
    start_histogram = model.histogram()
    initial_frames = list(model.frames)
    moves, passes = [], []
    rng = random.Random(args.seed)
    for k in range(args.passes):
        groups = model.exchange_groups(args.policy, rng, args.max_nodes)
        if args.order == "random":
            rng.shuffle(groups)
        elif args.order == "largest-first":
            groups.sort(key=lambda group: (-len(group), group))
        elif args.order == "reverse" or args.order == "alternating" and k % 2:
            groups.reverse()
        counts = Counter()
        for group in groups:
            change, status = model.collapse(group)
            counts[status] += 1
            if change:
                moves.append(change)
        passes.append({"pass": k, "groups": len(groups), **dict(counts)})
        print(json.dumps(passes[-1]), flush=True)
        if not counts["accepted"]:
            break
    local = model.validate()
    histogram = model.histogram()
    changed = [[i, list(F)] for i, F in enumerate(model.frames) if F != model.original[i]]
    frames_path = args.output / "frames.json"
    frames_path.write_text(json.dumps(changed, separators=(",", ":")) + "\n")
    (args.output / "moves.json").write_text(json.dumps(moves, separators=(",", ":")) + "\n")
    upstream = model.compiler.physical(model.g, model.witness, model.word, model.record, changed, model.pairs)
    require({int(r): c for r, c in upstream["child_histogram"].items()} == histogram, "complete histogram disagrees")
    (args.output / "physical-profile.json").write_text(json.dumps(upstream, indent=2, sort_keys=True) + "\n")
    result = {"status": "DISCOVERY", "policy": args.policy, "order": args.order,
              "seed": args.seed, "max_nodes": args.max_nodes, "passes": passes,
              "moves": len(moves), "frames_changed_from_start": sum(a != b for a, b in zip(initial_frames, model.frames)),
              "frames_changed_from_public": sum(a != b for a, b in zip(model.initial, model.frames)),
              "m": model.m, "W_per_vertex": model.reference["W_per_vertex"],
              "rank_per_vertex": model.reference["rank_per_vertex"], "max_child": max(histogram),
              "histogram": histogram, "moments": model.moments(histogram),
              "start_moments": model.moments(start_histogram), "control_moments": model.moments(model.initial_histogram),
              "local_checks": local, "upstream_physical_replay": True,
              "frames_sha256": sha(frames_path), "source_snapshot": args.source.name,
              "source_sha256": {name: sha(args.source / name) for name in
                                ("scripts/paired_cube_physical.py", "scripts/paired_cube/frames.py",
                                 "certificates/paired-cube-complex-input.json", "certificates/paired-cube-physical-input.json",
                                 "references/paired-cube/physical/frames.json", "references/paired-cube/physical/pairs.json")},
              "export_sha256": {name: sha(args.export / name) for name in ("graph.json", "frames.json", "selection.json")},
              "search_sha256": {name: sha(Path(__file__).parent / name) for name in ("physical_search.py", "physical_exchanges.py")},
              "start_frames_sha256": sha(args.start_frames) if args.start_frames else None,
              "wall_seconds": time.monotonic() - started,
              "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "exclusions": ["independent signed/reflected audit", "rigorous moments", "assembly certificate", "accepted final kappa"]}
    (args.output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("policy", "order", "moves", "frames_changed_from_start", "moments", "wall_seconds")}), flush=True)


if __name__ == "__main__":
    main()
