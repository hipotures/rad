#!/usr/bin/env python3
"""Bounded transitive carrier-frame joins/meets with complete paid pricing.

Global min/max frames are computed from the fixed incoming/outgoing boundaries
and operation value spaces. A seed moves to one transitive endpoint; joins are
propagated to successors, or meets to predecessors, only where nesting would
otherwise fail. The affected operations may retain different frames. Every
affected paid edge, with its actual multiplicity, is priced and checked exactly.
The frozen scalar word, gauges, aliases and read deadlines are unchanged.
Numerical moments remain DISCOVERY. Prepared with OpenAI assistance.
"""
import argparse
from collections import Counter, deque
from fractions import Fraction
import json
import math
from pathlib import Path
import random
import resource
import sys
import time

from physical_frontier import Frontier
from physical_search import require, sha


class Closure(Frontier):
    def global_bounds(self):
        n = len(self.ops)
        full = self.basis(1 << i for i in range(self.h))
        self.global_lower = [()] * n
        self.global_upper = [full] * n
        for i in range(n):
            require(all(a < i for a in self.incoming[i]), "nonchronological predecessor")
            self.global_lower[i] = self.basis(self.spans[self.ops[i][2]] + tuple(
                x for a in self.incoming[i]
                for x in (self.global_lower[a] if a >= 0 else self.frame(a))))
        for i in reversed(range(n)):
            F = full
            for b in self.outgoing[i]:
                require(b < 0 or b > i, "nonchronological successor")
                F = self.cap(F, self.global_upper[b] if b >= 0 else self.frame(b))
            self.global_upper[i] = F
        for i in range(n):
            require(self.contained(self.global_lower[i], self.frames[i])
                    and self.contained(self.frames[i], self.global_upper[i]), "global interval excludes current frame")
        self.edge_multiplicity = Counter(self.edges)

    def proposal(self, seed, direction, max_nodes):
        goal = self.global_upper[seed] if direction == "raise" else self.global_lower[seed]
        if goal == self.frames[seed]:
            return None, "at_endpoint"
        changed, queue = {seed: goal}, deque([seed])
        while queue:
            i = queue.popleft()
            F = changed[i]
            if direction == "raise":
                for b in self.outgoing[i]:
                    old = changed.get(b, self.frame(b))
                    if self.contained(F, old):
                        continue
                    require(b >= 0, "raised frame crosses fixed boundary")
                    new = self.basis(old + F)
                    require(self.contained(new, self.global_upper[b]), "raise escapes global bound")
                    changed[b] = new
                    queue.append(b)
            else:
                for a in self.incoming[i]:
                    old = changed.get(a, self.frame(a))
                    if self.contained(old, F):
                        continue
                    require(a >= 0, "lowered frame crosses fixed boundary")
                    new = self.cap(old, F)
                    require(self.contained(self.global_lower[a], new), "lower escapes global bound")
                    changed[a] = new
                    queue.append(a)
            if len(changed) > max_nodes:
                return None, "size_bound"
        affected = set()
        for i in changed:
            affected.update((a, i) for a in self.incoming[i])
            affected.update((i, b) for b in self.outgoing[i])

        def candidate_frame(i):
            return changed.get(i, self.frame(i))

        for i, F in changed.items():
            require(self.contained(self.spans[self.ops[i][2]], F), "proposal loses value span")
        for a, b in affected:
            require(self.contained(candidate_frame(a), candidate_frame(b)), "proposal chain is not nested")
        old = math.fsum(self.edge_multiplicity[a, b] * self.f[len(self.frame(b)) - len(self.frame(a))]
                        for a, b in affected)
        new = math.fsum(self.edge_multiplicity[a, b] * self.f[len(candidate_frame(b)) - len(candidate_frame(a))]
                        for a, b in affected)
        delta = new - old
        if delta >= -1e-12:
            return None, "no_gain"
        return {"seed": seed, "direction": direction, "delta_excess_local": delta,
                "frames": [[i, list(F)] for i, F in sorted(changed.items())],
                "affected_edge_occurrences": sum(self.edge_multiplicity[e] for e in affected)}, "accepted"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--start-frames", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--direction", choices=["raise", "lower"], required=True)
    parser.add_argument("--seed", type=int, default=20261009)
    parser.add_argument("--seed-limit", type=int, default=8000)
    parser.add_argument("--max-nodes", type=int, default=256)
    parser.add_argument("--passes", type=int, default=2)
    parser.add_argument("--trial", type=Fraction, default=Fraction(617042388, 10**12))
    args = parser.parse_args()
    require(not sys.flags.optimize, "assertion-disabled execution is unsupported")
    require(not args.output.exists(), "attempt output already exists")
    require(0 < args.trial < 1 and args.seed_limit > 0 and args.max_nodes > 0 and args.passes > 0, "invalid settings")
    args.output.mkdir(parents=True)
    started = time.monotonic()
    model = Closure(args.source.resolve(), args.export.resolve(), float(args.trial))
    payload = json.loads(args.start_frames.read_text())
    rows = payload["frames"] if isinstance(payload, dict) else payload
    model.frames = list(model.original)
    seen = set()
    for i, F in rows:
        require(type(i) is int and 0 <= i < len(model.ops) and i not in seen, "invalid or duplicate operation index")
        require(all(type(x) is int and 0 < x < 1 << model.h for x in F), "invalid frame vector")
        require(model.basis(F) == tuple(F) != model.original[i], "noncanonical or unmoved frame")
        seen.add(i)
        model.frames[i] = tuple(F)
    model.validate()
    start_histogram = model.histogram()
    initial_frames = list(model.frames)
    model.global_bounds()
    rng = random.Random(args.seed)
    moves, passes = [], []
    for k in range(args.passes):
        seeds = list(range(len(model.ops)))
        rng.shuffle(seeds)
        if args.direction == "raise":
            seeds.sort(key=lambda i: -(len(model.global_upper[i]) - len(model.frames[i])))
        else:
            seeds.sort(key=lambda i: -(len(model.frames[i]) - len(model.global_lower[i])))
        seeds = seeds[:args.seed_limit]
        counts = Counter()
        for i in seeds:
            plan, status = model.proposal(i, args.direction, args.max_nodes)
            counts[status] += 1
            if plan:
                for j, F in plan["frames"]:
                    model.frames[j] = tuple(F)
                moves.append(plan)
        passes.append({"pass": k, "seeds": len(seeds), **dict(counts)})
        print(json.dumps(passes[-1]), flush=True)
        if not counts["accepted"]:
            break
    local = model.validate()
    histogram = model.histogram()
    require(model.moments(histogram)["H"] <= model.moments(start_histogram)["H"] + 5e-15, "complete trial worsened")
    changed = [[i, list(F)] for i, F in enumerate(model.frames) if F != model.original[i]]
    frames_path = args.output / "frames.json"
    frames_path.write_text(json.dumps(changed, separators=(",", ":")) + "\n")
    (args.output / "moves.json").write_text(json.dumps(moves, separators=(",", ":")) + "\n")
    physical = model.compiler.physical(model.g, model.witness, model.word, model.record, changed, model.pairs)
    require({int(r): c for r, c in physical["child_histogram"].items()} == histogram, "complete histogram disagrees")
    (args.output / "physical-profile.json").write_text(json.dumps(physical, indent=2, sort_keys=True) + "\n")
    result = {"status": "DISCOVERY", "direction": args.direction, "seed": args.seed,
              "seed_limit": args.seed_limit, "max_nodes": args.max_nodes, "requested_passes": args.passes,
              "trial_exact": str(args.trial), "passes": passes, "moves": len(moves),
              "frames_changed_from_start": sum(a != b for a, b in zip(initial_frames, model.frames)),
              "frames_changed_from_public": sum(a != b for a, b in zip(model.initial, model.frames)),
              "m": model.m, "W_per_vertex": model.reference["W_per_vertex"],
              "rank_per_vertex": model.reference["rank_per_vertex"], "max_child": max(histogram),
              "histogram": histogram, "moments": model.moments(histogram),
              "start_moments": model.moments(start_histogram), "local_checks": local,
              "upstream_physical_replay": True, "context_sha256": sha(args.context),
              "source_context": json.loads(args.context.read_text()), "frames_sha256": sha(frames_path),
              "start_frames_sha256": sha(args.start_frames),
              "global_bound_rank_histogram": dict(Counter((len(a), len(b)) for a, b in
                                                          zip(model.global_lower, model.global_upper))),
              "search_sha256": {name: sha(Path(__file__).parent / name) for name in
                                ("physical_search.py", "physical_exchanges.py", "physical_frontier.py", "physical_closure.py")},
              "wall_seconds": time.monotonic() - started, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "exclusions": ["independent signed/reflected audit", "rigorous moments", "assembly certificate", "accepted final kappa"]}
    result["global_bound_rank_histogram"] = {str(k): v for k, v in result["global_bound_rank_histogram"].items()}
    (args.output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("direction", "moves", "frames_changed_from_start", "moments", "wall_seconds")}), flush=True)


if __name__ == "__main__":
    main()
