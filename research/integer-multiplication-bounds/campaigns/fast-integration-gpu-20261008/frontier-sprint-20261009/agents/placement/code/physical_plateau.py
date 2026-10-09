#!/usr/bin/env python3
"""Exact histogram-preserving endpoint escapes followed by paid frame descent.

A neutral move is admitted only when every affected positive-rank transition
has the same rank multiset before and after. Thus its complete child histogram
is unchanged exactly, even though the explicit legal carrier frames differ.
The frozen producer, gauges, alias pairs and read chronology do not change.
All final candidates pass the complete inherited physical checker. Numerical
screening remains DISCOVERY until independently certified.
Prepared with OpenAI assistance; inherited source attribution is unchanged.
"""
import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import random
import resource
import sys
import time

from physical_frontier import Frontier
from physical_search import require, sha


class Plateau(Frontier):
    def neutral(self, group, direction):
        if len({self.frames[i] for i in group}) != 1:
            return None
        lower, upper, inc, out = self.endpoints(group)
        current = self.frames[group[0]]
        frame = upper if direction == "raise" else lower
        if frame == current:
            return None
        inside = set(group)
        internal = [(a, b) for a in group for b in self.outgoing[a] if b in inside]
        old = Counter(len(self.frame(b)) - len(self.frame(a)) for a, b in inc + internal + out)
        d = len(frame)
        new = Counter([d - len(self.frame(a)) for a, _ in inc]
                      + [len(self.frame(b)) - d for _, b in out])
        old.pop(0, None)
        new.pop(0, None)
        if old != new:
            return None
        return {"kind": "exact_histogram_neutral", "ops": list(group), "frame": list(frame),
                "old_rank": len(current), "new_rank": d, "direction": direction,
                "affected_positive_rank_histogram": dict(sorted(old.items()))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variant", choices=["strict-pairs", "raise-neutral", "lower-neutral"], required=True)
    parser.add_argument("--cycles", type=int, default=2)
    parser.add_argument("--neutral-budget", type=int, default=600)
    parser.add_argument("--strict-passes", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261009)
    parser.add_argument("--trial", type=Fraction, default=Fraction(616113761, 10**12))
    args = parser.parse_args()
    require(not sys.flags.optimize, "assertion-disabled execution is unsupported")
    require(not args.output.exists(), "attempt output already exists")
    require(0 < args.trial < 1 and args.cycles > 0 and args.strict_passes > 0 and args.neutral_budget > 0, "invalid settings")
    args.output.mkdir(parents=True)
    started = time.monotonic()
    model = Plateau(args.source.resolve(), args.export.resolve(), float(args.trial))
    context = json.loads(args.context.read_text())
    before = model.histogram()
    initial_frames = list(model.frames)
    rng = random.Random(args.seed)
    moves, cycles = [], []
    for cycle in range(args.cycles):
        neutral_count = 0
        if args.variant != "strict-pairs":
            direction = "raise" if args.variant == "raise-neutral" else "lower"
            histogram = model.histogram()
            groups = model.groups("components", rng)
            rng.shuffle(groups)
            for group in groups:
                plan = model.neutral(group, direction)
                if plan:
                    model.commit(plan)
                    moves.append(plan)
                    neutral_count += 1
                if neutral_count >= args.neutral_budget:
                    break
            require(model.histogram() == histogram, "neutral phase changed the complete paid histogram")
            model.validate()
        passes = []
        policy = "op-pairs" if args.variant == "strict-pairs" else "components"
        for k in range(args.strict_passes):
            groups = model.exchange_groups(policy, rng, 512)
            if k % 2:
                groups.reverse()
            counts = Counter()
            for group in groups:
                plan, status = model.plan(group)
                counts[status] += 1
                if plan:
                    model.commit(plan)
                    plan["kind"] = "strict_complete_moment_improvement"
                    moves.append(plan)
            passes.append({"pass": k, "groups": len(groups), **dict(counts)})
            if not counts["accepted"]:
                break
        row = {"cycle": cycle, "exact_neutral_moves": neutral_count,
               "neutral_full_histogram_unchanged": True, "strict_policy": policy, "passes": passes}
        cycles.append(row)
        print(json.dumps(row), flush=True)
        if not neutral_count and not sum(p.get("accepted", 0) for p in passes):
            break
    local = model.validate()
    histogram = model.histogram()
    require(model.moments(histogram)["H"] <= model.moments(before)["H"] + 5e-15, "complete trial moment worsened")
    changed = [[i, list(F)] for i, F in enumerate(model.frames) if F != model.original[i]]
    frames_path = args.output / "frames.json"
    frames_path.write_text(json.dumps(changed, separators=(",", ":")) + "\n")
    (args.output / "moves.json").write_text(json.dumps(moves, separators=(",", ":")) + "\n")
    physical = model.compiler.physical(model.g, model.witness, model.word, model.record, changed, model.pairs)
    require({int(r): c for r, c in physical["child_histogram"].items()} == histogram, "complete histogram disagrees")
    (args.output / "physical-profile.json").write_text(json.dumps(physical, indent=2, sort_keys=True) + "\n")
    result = {"status": "DISCOVERY", "variant": args.variant, "seed": args.seed, "trial_exact": str(args.trial),
              "requested_cycles": args.cycles, "neutral_budget": args.neutral_budget, "strict_passes": args.strict_passes,
              "cycles": cycles, "moves": len(moves),
              "neutral_moves": sum(m["kind"] == "exact_histogram_neutral" for m in moves),
              "strict_moves": sum(m["kind"] == "strict_complete_moment_improvement" for m in moves),
              "frames_changed_from_public": sum(a != b for a, b in zip(initial_frames, model.frames)),
              "m": model.m, "W_per_vertex": model.reference["W_per_vertex"],
              "rank_per_vertex": model.reference["rank_per_vertex"], "max_child": max(histogram),
              "histogram": histogram, "moments": model.moments(histogram), "control_moments": model.moments(before),
              "local_checks": local, "upstream_physical_replay": True, "source_context": context,
              "context_sha256": sha(args.context), "frames_sha256": sha(frames_path),
              "source_sha256": {name: sha(args.source / name) for name in
                                ("scripts/paired_cube_physical.py", "scripts/paired_cube/frames.py",
                                 "certificates/paired-cube-complex-input.json", "certificates/paired-cube-physical-input.json",
                                 "references/paired-cube/physical/frames.json", "references/paired-cube/physical/pairs.json")},
              "export_sha256": {name: sha(args.export / name) for name in ("graph.json", "frames.json", "selection.json")},
              "search_sha256": {name: sha(Path(__file__).parent / name) for name in
                                ("physical_search.py", "physical_exchanges.py", "physical_frontier.py", "physical_plateau.py")},
              "wall_seconds": time.monotonic() - started, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "exclusions": ["independent signed/reflected audit", "rigorous moments", "assembly certificate", "accepted final kappa"]}
    (args.output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("variant", "neutral_moves", "strict_moves", "frames_changed_from_public", "moments", "wall_seconds")}), flush=True)


if __name__ == "__main__":
    main()
