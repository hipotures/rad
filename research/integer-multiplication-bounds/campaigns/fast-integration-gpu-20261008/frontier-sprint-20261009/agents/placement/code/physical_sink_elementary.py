#!/usr/bin/env python3
"""Bounded one-dimensional joins/meets on complete literal sink chains.

An endpoint exchange can propagate through a large carrier component. Here a
seed adds or removes one quotient direction, and nesting repairs propagate only
the resulting joins or intersections. Every changed paid edge is priced with
its actual multiplicity. Canonical quotient basis directions are a bounded
discriminator, not an exhaustive orientation search. Scalar word, gauges,
aliases, compensated read times and terminal sinks stay fixed.
Inherited source attribution is recorded in physical_sinks.py. Prepared with
OpenAI assistance. Binary64 moments are discovery only.
"""
import argparse
from collections import Counter, deque
from fractions import Fraction
import importlib.util
import json
import math
from pathlib import Path
import random
import resource
import sys
import time

from physical_sinks import Sinks
from physical_search import require, sha


class Elementary(Sinks):
    def goals(self, seed, direction, cap):
        current = self.frames[seed]
        if direction == "raise":
            candidates = {self.basis(current + (x,)) for x in self.global_upper[seed]
                          if not self.contained((x,), current)}
        else:
            lower = self.global_lower[seed]
            span, extras = lower, []
            for x in current:
                if not self.contained((x,), span):
                    extras.append(x)
                    span = self.basis(span + (x,))
            require(span == current, "quotient supplement does not span seed")
            candidates = {self.basis(lower + tuple(extras[:j] + extras[j + 1:]))
                          for j in range(len(extras))}
        goals = sorted(candidates)
        for goal in goals:
            require(abs(len(goal) - len(current)) == 1, "elementary goal has wrong rank")
            require(self.contained(self.global_lower[seed], goal) and
                    self.contained(goal, self.global_upper[seed]), "elementary goal escapes seed interval")
        if len(goals) > cap:
            positions = [j * (len(goals) - 1) // (cap - 1) for j in range(cap)] if cap > 1 else [0]
            goals = [goals[j] for j in positions]
        return goals

    def proposal_goal(self, seed, direction, goal, max_nodes):
        changed, queue = {seed: goal}, deque([seed])
        while queue:
            i = queue.popleft()
            F = changed[i]
            boundary = self.outgoing[i] if direction == "raise" else self.incoming[i]
            for j in boundary:
                old = changed.get(j, self.frame(j))
                compatible = self.contained(F, old) if direction == "raise" else self.contained(old, F)
                if compatible:
                    continue
                require(j >= 0, "elementary proposal crosses fixed boundary")
                new = self.basis(old + F) if direction == "raise" else self.cap(old, F)
                require(self.contained(self.global_lower[j], new) and
                        self.contained(new, self.global_upper[j]), "propagation escapes global interval")
                changed[j] = new
                queue.append(j)
            if len(changed) > max_nodes:
                return None, "size_bound"
        affected = set()
        for i in changed:
            affected.update((a, i) for a in self.incoming[i])
            affected.update((i, b) for b in self.outgoing[i])

        def candidate_frame(i):
            return changed.get(i, self.frame(i))

        for i, F in changed.items():
            require(self.contained(self.spans[self.ops[i][2]], F), "elementary move loses value span")
        for a, b in affected:
            require(self.contained(candidate_frame(a), candidate_frame(b)), "elementary move loses chain nesting")
        old = math.fsum(self.edge_multiplicity[a, b] * self.f[len(self.frame(b)) - len(self.frame(a))]
                        for a, b in affected)
        new = math.fsum(self.edge_multiplicity[a, b] * self.f[len(candidate_frame(b)) - len(candidate_frame(a))]
                        for a, b in affected)
        delta = new - old
        if delta >= -1e-12:
            return None, "no_gain"
        return {"seed": seed, "direction": direction, "goal": list(goal),
                "delta_excess_local": delta,
                "frames": [[i, list(F)] for i, F in sorted(changed.items())],
                "affected_edge_occurrences": sum(self.edge_multiplicity[e] for e in affected)}, "accepted"


def main():
    parser = argparse.ArgumentParser()
    for name in ("source", "export", "context", "sinks", "sink-profile", "sink-protocol", "sink-gate",
                 "start-frames", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--variant", choices=["control", "raise", "lower", "mixed"], required=True)
    parser.add_argument("--passes", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261009)
    parser.add_argument("--max-nodes", type=int, default=256)
    parser.add_argument("--seed-limit", type=int, default=8192)
    parser.add_argument("--goal-limit", type=int, default=4)
    parser.add_argument("--trial", type=Fraction, default=Fraction(655861417, 10**12))
    args = parser.parse_args()
    require(not sys.flags.optimize, "assertion-disabled execution is unsupported")
    require(not args.output.exists(), "elementary attempt already exists")
    require(min(args.passes, args.max_nodes, args.seed_limit, args.goal_limit) > 0 and
            0 < args.trial < 1, "invalid elementary search settings")
    context, protocol = [json.loads(p.read_text()) for p in (args.context, args.sink_protocol)]
    require(context["source_commit"] == protocol["source_head"], "sink/body source heads differ")
    for name, pin in protocol["body_input_pins"].items():
        if name != "baseline.json":
            require(pin["sha256"] == context["input_sha256"][name.removesuffix(".json")], "sink/body input pin differs")
    require(sha(args.sinks) == protocol["input_pins"]["sinks.json"]["sha256"] and
            sha(args.sink_profile) == protocol["input_pins"]["profile.json"]["sha256"], "sink input pin differs")
    require(sha(args.sink_gate) == protocol["source_pins"]["research/terminal-sinks/sinks_gate.py"], "sink gate pin differs")
    for name, digest in context["source_sha256"].items():
        require(sha(args.source / name) == digest, "body source pin differs")
    for name, digest in context["derived_sha256"].items():
        require(sha(args.context.parent / name) == digest, "derived body input pin differs")
    args.output.mkdir(parents=True)
    started = time.monotonic()
    payload = json.loads(args.sinks.read_text())
    sinks = payload["sinks"] if isinstance(payload, dict) else payload
    model = Elementary(args.source.resolve(), args.export.resolve(), float(args.trial), sinks,
                       json.loads(args.sink_profile.read_text()))
    model.frames = list(model.original)
    payload = json.loads(args.start_frames.read_text())
    rows = payload["frames"] if isinstance(payload, dict) else payload
    seen = set()
    for i, F in rows:
        require(type(i) is int and 0 <= i < len(model.ops) and i not in seen, "invalid start operation")
        require(all(type(x) is int and 0 < x < 1 << model.h for x in F), "invalid start frame vector")
        require(model.basis(F) == tuple(F) != model.original[i], "noncanonical or unmoved start frame")
        seen.add(i)
        model.frames[i] = tuple(F)
    model.validate()
    before_frames, before_histogram = list(model.frames), model.histogram()
    model.global_bounds()
    rng, moves, passes = random.Random(args.seed), [], []
    directions = ["raise", "lower"] if args.variant == "mixed" else [args.variant]
    for k in range(args.passes if args.variant != "control" else 0):
        counts = Counter()
        seeds = list(range(len(model.ops)))
        rng.shuffle(seeds)
        seeds.sort(key=lambda i: -max((len(model.global_upper[i]) - len(model.frames[i]) if d == "raise"
                                      else len(model.frames[i]) - len(model.global_lower[i])) for d in directions))
        seeds = seeds[:args.seed_limit]
        for i in seeds:
            plans = []
            for direction in directions:
                goals = model.goals(i, direction, args.goal_limit)
                counts["goals"] += len(goals)
                if not goals:
                    counts["at_endpoint"] += 1
                for goal in goals:
                    plan, status = model.proposal_goal(i, direction, goal, args.max_nodes)
                    counts[status] += 1
                    if plan:
                        plans.append(plan)
            if plans:
                plan = min(plans, key=lambda p: (p["delta_excess_local"], p["direction"], p["goal"]))
                for j, F in plan["frames"]:
                    model.frames[j] = tuple(F)
                moves.append(plan)
                counts["committed"] += 1
        passes.append({"pass": k, "seeds": len(seeds), **dict(counts)})
        print(json.dumps(passes[-1]), flush=True)
        if not counts["committed"]:
            break
    checks, histogram = model.validate(), model.histogram()
    changed = [[i, list(F)] for i, F in enumerate(model.frames) if F != model.original[i]]
    frame_path = args.output / "frames.json"
    frame_path.write_text(json.dumps(changed, separators=(",", ":")) + "\n")
    (args.output / "moves.json").write_text(json.dumps(moves, separators=(",", ":")) + "\n")
    body = model.compiler.physical(model.g, model.witness, model.word, model.record, changed, model.pairs)
    spec = importlib.util.spec_from_file_location("pinned_elementary_sink_gate", args.sink_gate.resolve())
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    physical = gate.sinks_record(model.g, model.witness, model.word, model.record, changed, model.pairs, sinks, body)
    require({int(r): n for r, n in physical["child_histogram"].items()} == histogram, "full elementary sink histogram differs")
    require(physical["W_per_vertex"] == model.reference["W_per_vertex"] and
            physical["rank_per_vertex"] == model.reference["rank_per_vertex"], "complete sink width/rank differs")
    require(model.moments(histogram)["H"] <= model.moments(before_histogram)["H"] + 5e-15, "full moment worsened")
    for name, data in (("body-profile.json", body), ("sink-profile.json", physical)):
        (args.output / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    result = {"status": "DISCOVERY_COMPLETE_SUBSTITUTED_SINK_WORD", "method": "elementary-transitive",
              "variant": args.variant, "seed": args.seed, "requested_passes": args.passes,
              "max_nodes": args.max_nodes, "seed_limit": args.seed_limit, "goal_limit": args.goal_limit,
              "trial_exact": str(args.trial), "moves": len(moves), "passes": passes,
              "frames_changed_from_start": sum(a != b for a, b in zip(before_frames, model.frames)),
              "frames_sha256": sha(frame_path), "start_frames_sha256": sha(args.start_frames),
              "m": model.m, "W_per_vertex": physical["W_per_vertex"], "rank_per_vertex": physical["rank_per_vertex"],
              "physical_roles": physical["physical_R"], "sinks": len(sinks), "max_child": max(histogram),
              "literal_registers": model.literal_registers, "literal_frame_edges": len(model.edges),
              "histogram": histogram, "moments": model.moments(histogram), "start_moments": model.moments(before_histogram),
              "local_checks": checks, "full_body_and_sink_replay": True,
              "context_sha256": sha(args.context), "source_context": context,
              "sink_pins": {name: sha(path) for name, path in (("sinks", args.sinks), ("reference", args.sink_profile),
                                                            ("protocol", args.sink_protocol), ("gate", args.sink_gate))},
              "search_sha256": {name: sha(Path(__file__).parent / name) for name in
                                ("physical_search.py", "physical_exchanges.py", "physical_frontier.py", "physical_closure.py",
                                 "physical_sinks.py", "physical_sink_elementary.py")},
              "wall_seconds": time.monotonic() - started, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "scope": "Bounded canonical quotient directions on one complete literal sink word. Fixed DAG/gauges/aliases/read times/sinks; native complete forward/reflected replay passes. Independent exact arithmetic, operator and geometry reviews remain separate."}
    (args.output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("variant", "moves", "moments", "wall_seconds")}), flush=True)


if __name__ == "__main__":
    main()
