#!/usr/bin/env python3
"""Direct complete-moment frame search on a literal terminal-sink stage.

Build physical X/Y/auxiliary register chains for the actual substituted word.
The sink's writes use its target pivot instead of an auxiliary slot; its pre/post
shears and literal cleanup are included. Price that full histogram directly.
Every final plan receives the pinned body checker and the complete upstream sink
gate, including forward/reflected frame scans and dirty replay. No body-root
estimate, profile splice or ledger subtraction chooses the candidate.
Terminal sinks are jamesyc's PR166 mechanism, independently integrated by
eumemic with Anthropic Claude assistance. This search is prepared with OpenAI
assistance and preserves the inherited Apache-2.0 attribution.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import random
import resource
import sys
import time

from physical_closure import Closure
from physical_search import Physical, require, sha


class Sinks(Closure):
    def __init__(self, source, export, trial, sinks, sink_reference):
        self.literal_ready = False
        super().__init__(source, export, trial)
        self.body_reference = self.reference
        self.sinks = dict(sinks)
        require(len(self.sinks) == len(sinks) > 0, "duplicate or empty sinks")
        self.reference = sink_reference
        require(self.reference["sinks"] == len(sinks), "sink count differs")
        require(self.reference["sink_substitution"]["sinks"] == sinks, "sink identity differs")
        require(self.reference["R"] == self.R and self.reference["pairs"] == len(self.pairs), "sink body identity differs")
        self.literal_chains()
        require(self.reference["W_per_vertex"] == self.literal_registers ==
                self.body_reference["W_per_vertex"] - len(sinks), "sink width differs from literal register count")
        require(self.reference["physical_R"] == self.body_reference["physical_R"] - len(sinks)
                and self.reference["m"] == self.m, "sink physical dimensions differ")
        self.literal_ready = True
        self.validate()
        self.initial_histogram = self.histogram()
        require(self.initial_histogram == {int(r): n for r, n in self.reference["child_histogram"].items()},
                "direct complete sink control histogram differs")

    def literal_chains(self):
        h, v = self.h, self.v
        full = self.basis(1 << i for i in range(h))
        phase = sorted(self.word["phase1"])
        pset = set(phase)
        self.operation_order = phase + [i for i in range(len(self.ops)) if i not in pset]
        position = {i: k for k, i in enumerate(self.operation_order)}
        merged = {int(b): int(a) for a, b, _ in self.pairs}
        deadlines = {int(b): t for _, b, t in self.pairs}
        live = sorted(set(range(self.R)) - set(merged))
        slot = {s: k for k, s in enumerate(live)}
        aux = lambda s: 2 * v + slot[merged.get(s, s)]
        removed = {aux(s) for s in self.sinks}
        fixed_lookup = {}
        self.fixed, self.edges = [], []
        self.incoming, self.outgoing = defaultdict(list), defaultdict(list)
        self.neighbors = defaultdict(set)

        def fixed(F):
            if F not in fixed_lookup:
                self.fixed.append(F)
                fixed_lookup[F] = -len(self.fixed)
            return fixed_lookup[F]

        zero, full_id = fixed(()), fixed(full)
        current, final = {}, {}
        for t, q in enumerate(self.g["inputs"]):
            current[t], current[v + t] = fixed((q,)), zero
            final[t], final[v + t] = full_id, fixed(self.perp((q,), h))
        for s in live:
            r = aux(s)
            if r not in removed:
                current[r], final[r] = fixed(self.gauges.get(s, ())), full_id

        def promote(r, goal):
            require(r not in removed and r in current, "deleted or unknown literal port")
            before = current[r]
            if before != goal:
                self.edges.append((before, goal))
                if goal >= 0:
                    self.incoming[goal].append(before)
                if before >= 0:
                    self.outgoing[before].append(goal)
                if before >= 0 and goal >= 0:
                    self.neighbors[before].add(goal)
                    self.neighbors[goal].add(before)
            current[r] = goal

        selected = [z["role"] for z in self.word["selected"]]
        selected_by_role = {z["role"]: z for z in self.word["selected"]}
        rest = [i for i in range(len(self.ops)) if i not in pset]
        reads = defaultdict(list)
        first_read = {}
        for s in reversed(selected):
            when = deadlines.get(s)
            when = rest[0] if when is None else when
            require(when not in pset, "deferred read in phase one")
            reads[when].append(s)
            for t in selected_by_role[s]["targets"]:
                first_read[t] = min(first_read.get(t, 1 << 60), position[when])
        root_by_role = {s: r for s, r in zip(self.word["rootroles"], self.g["roots"])}
        self.sink_targets, sink_writes, last_write = {}, {}, {}
        require(all(ca == 1 for ca, _ in self.word["opcoeff"]), "sink stage requires shear operations")
        for s, pivot in self.sinks.items():
            require(type(s) is int and 0 <= s < self.R and type(pivot) is int and 0 <= pivot < v,
                    "illegal sink/pivot index")
            require(s not in merged and s not in set(merged.values()) and s not in self.gauges
                    and s not in self.sources.values(), "sink is paired, gauged or injected")
            root = root_by_role.get(s)
            require(root is not None and root["kind"] == "side" and len(set(root["coefficients"])) == 1,
                    "sink lacks one uniform side root")
            writes = [i for i, (a, _, _) in enumerate(self.ops) if a == s]
            require(writes and not any(b == s for _, b, _ in self.ops), "sink is not destination-only")
            require(all(i not in pset for i in writes), "sink write in phase one")
            require(pivot in root["targets"] and first_read.get(pivot, 1 << 60) > max(position[i] for i in writes),
                    "sink pivot corrected before last write")
            self.sink_targets[s] = root["targets"]
            for i in writes:
                sink_writes[i] = s
            last_write[max(writes, key=position.get)] = s
        targets = [t for group in self.sink_targets.values() for t in group]
        require(len(targets) == len(set(targets)), "sink target groups overlap")
        self.stage_extra = Counter()

        # Time-zero response reads have zero frame on both banks. Their Y
        # promotions remain zero; only nongauged auxiliary ports need recording.
        for s in range(self.R):
            if s not in self.gauges and s not in self.sinks:
                promote(aux(s), zero)
        for x, s in sorted(self.sources.items()):
            F = fixed((self.g["inputs"][x - 1],))
            promote(aux(s), F)
            promote(x - 1, F)
        for i in phase:
            a, b, _ = self.ops[i]
            promote(aux(a), i)
            promote(aux(b), i)
        for s, kind in self.rootkind.items():
            if kind == "center":
                F = self.rootframe[s]
                promote(aux(s), fixed(F))
                self.stage_extra[len(F)] += 1
        # Copied-center scatter is at Y frame zero. The sink pre-shears follow
        # that scatter, also at zero; neither changes any positive-rank bill.
        for s, group in self.sink_targets.items():
            pivot = self.sinks[s]
            for t in group:
                if t != pivot:
                    promote(v + t, zero)
                    promote(v + pivot, zero)
        inverse_ops = list(phase)
        for i in rest:
            for s in reads.get(i, ()):
                F = fixed(self.gauges[s])
                promote(aux(s), F)
                for t in selected_by_role[s]["targets"]:
                    promote(v + t, F)
            a, b, _ = self.ops[i]
            if i in sink_writes:
                s = sink_writes[i]
                promote(v + self.sinks[s], i)
                promote(aux(b), i)
            else:
                promote(aux(a), i)
                promote(aux(b), i)
                inverse_ops.append(i)
            if i in last_write:
                s = last_write[i]
                F = fixed(self.rootframe[s])
                for t in self.sink_targets[s]:
                    if t != self.sinks[s]:
                        promote(v + t, F)
                        promote(v + self.sinks[s], F)
        for s, root in zip(self.word["rootroles"], self.g["roots"]):
            if root["kind"] == "side" and s not in self.sinks:
                F = fixed(self.rootframe[s])
                promote(aux(s), F)
                for t in root["targets"]:
                    promote(v + t, F)
        # Original X transform and diagonal adapters, then literal full-frame
        # inverse cleanup. These are static frames on this exact source word.
        for start in range(0, v, 8):
            qs = self.g["inputs"][start:start + 8]
            for parity in (0, 1):
                S = [k for k in range(8) if k.bit_count() % 2 == parity]
                F = fixed(self.basis(qs[k] for k in S))
                for k in S:
                    promote(start + k, F)
                for k in S:
                    t = k ^ 7
                    G = fixed(self.perp((qs[t],), h))
                    promote(v + start + t, G)
                    promote(start + k, G)
                for k in S:
                    promote(start + k, full_id)
        for i in reversed(inverse_ops):
            a, b, _ = self.ops[i]
            promote(aux(a), full_id)
            promote(aux(b), full_id)
        for x, s in sorted(self.sources.items(), reverse=True):
            promote(aux(s), full_id)
            promote(x - 1, full_id)
        for r, F in final.items():
            promote(r, F)
        self.literal_registers = len(current)

    def histogram(self):
        if not self.literal_ready:
            return Physical.histogram(self)
        stage = Counter(self.stage_extra)
        for a, b in self.edges:
            r = len(self.frame(b)) - len(self.frame(a))
            require(r >= 0, "negative literal frame width")
            if r:
                stage[r] += 1
        children = Counter({r: 3 * n for r, n in stage.items() if r})
        tails = Counter(len(F) for s, F in self.gauges.items() if s not in self.merged)
        children.update({3 * r: n for r, n in tails.items() if r})
        children[2] += 2 * self.v
        require(sum(r * n for r, n in children.items()) == self.reference["rank_per_vertex"], "complete sink rank mass")
        return dict(sorted(children.items()))

    def global_bounds(self):
        full = self.basis(1 << i for i in range(self.h))
        self.global_lower = [()] * len(self.ops)
        self.global_upper = [full] * len(self.ops)
        position = {i: k for k, i in enumerate(self.operation_order)}
        for i in self.operation_order:
            require(all(a < 0 or position[a] < position[i] for a in self.incoming[i]), "nonchronological literal predecessor")
            self.global_lower[i] = self.basis(self.spans[self.ops[i][2]] + tuple(
                x for a in self.incoming[i] for x in (self.global_lower[a] if a >= 0 else self.frame(a))))
        for i in reversed(self.operation_order):
            F = full
            for b in self.outgoing[i]:
                require(b < 0 or position[b] > position[i], "nonchronological literal successor")
                F = self.cap(F, self.global_upper[b] if b >= 0 else self.frame(b))
            self.global_upper[i] = F
        for i in range(len(self.ops)):
            require(self.contained(self.global_lower[i], self.frames[i]) and
                    self.contained(self.frames[i], self.global_upper[i]), "literal global interval excludes current frame")
        self.edge_multiplicity = Counter(self.edges)


def main():
    parser = argparse.ArgumentParser()
    for name in ("source", "export", "context", "sinks", "sink-profile", "sink-protocol", "sink-gate", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--variant", choices=["control", "components", "op-pairs", "global-lower", "global-raise"], required=True)
    parser.add_argument("--start-frames", type=Path)
    parser.add_argument("--passes", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261009)
    parser.add_argument("--max-nodes", type=int, default=256)
    parser.add_argument("--trial", type=Fraction, default=Fraction(655831073, 10**12))
    args = parser.parse_args()
    require(not sys.flags.optimize, "assertion-disabled execution is unsupported")
    require(not args.output.exists(), "sink attempt already exists")
    require(args.passes > 0 and args.max_nodes > 0 and 0 < args.trial < 1, "invalid sink search settings")
    context = json.loads(args.context.read_text())
    protocol = json.loads(args.sink_protocol.read_text())
    require(context["source_commit"] == protocol["source_head"], "sink/body source heads differ")
    for name, pin in protocol["body_input_pins"].items():
        if name != "baseline.json":
            require(pin["sha256"] == context["input_sha256"][name.removesuffix(".json")], "sink/body input pin differs")
    require(sha(args.sinks) == protocol["input_pins"]["sinks.json"]["sha256"] and
            sha(args.sink_profile) == protocol["input_pins"]["profile.json"]["sha256"], "sink input pin differs")
    require(sha(args.sink_gate) == protocol["source_pins"]["research/terminal-sinks/sinks_gate.py"], "sink source gate pin differs")
    for name, digest in context["source_sha256"].items():
        require(sha(args.source / name) == digest, "body source pin differs")
    for name, digest in context["derived_sha256"].items():
        require(sha(args.context.parent / name) == digest, "body derived input pin differs")
    args.output.mkdir(parents=True)
    started = time.monotonic()
    payload = json.loads(args.sinks.read_text())
    sinks = payload["sinks"] if isinstance(payload, dict) else payload
    model = Sinks(args.source.resolve(), args.export.resolve(), float(args.trial), sinks,
                  json.loads(args.sink_profile.read_text()))
    if args.start_frames:
        model.frames = list(model.original)
        payload = json.loads(args.start_frames.read_text())
        payload = payload["frames"] if isinstance(payload, dict) else payload
        seen = set()
        for i, F in payload:
            require(type(i) is int and 0 <= i < len(model.ops) and i not in seen, "invalid sink start operation")
            require(all(type(x) is int and 0 < x < 1 << model.h for x in F), "invalid sink start vector")
            require(model.basis(F) == tuple(F) != model.original[i], "noncanonical or unmoved sink start frame")
            seen.add(i)
            model.frames[i] = tuple(F)
    model.validate()
    before_frames, before_histogram = list(model.frames), model.histogram()
    rng, moves, passes = random.Random(args.seed), [], []
    if args.variant.startswith("global"):
        model.global_bounds()
    for k in range(args.passes if args.variant != "control" else 0):
        counts = Counter()
        if args.variant.startswith("global"):
            direction = args.variant.split("-")[1]
            seeds = list(range(len(model.ops)))
            rng.shuffle(seeds)
            seeds.sort(key=lambda i: -(len(model.global_upper[i]) - len(model.frames[i]) if direction == "raise"
                                      else len(model.frames[i]) - len(model.global_lower[i])))
            for i in seeds:
                plan, status = model.proposal(i, direction, args.max_nodes)
                counts[status] += 1
                if plan:
                    for j, F in plan["frames"]:
                        model.frames[j] = tuple(F)
                    moves.append(plan)
            count = len(seeds)
        else:
            groups = model.exchange_groups(args.variant, rng, args.max_nodes)
            if k % 2:
                groups.reverse()
            for group in groups:
                plan, status = model.collapse(group)
                counts[status] += 1
                if plan:
                    moves.append(plan)
            count = len(groups)
        passes.append({"pass": k, "candidates": count, **dict(counts)})
        print(json.dumps(passes[-1]), flush=True)
        if not counts["accepted"]:
            break
    checks, histogram = model.validate(), model.histogram()
    changed = [[i, list(F)] for i, F in enumerate(model.frames) if F != model.original[i]]
    frame_path = args.output / "frames.json"
    frame_path.write_text(json.dumps(changed, separators=(",", ":")) + "\n")
    (args.output / "moves.json").write_text(json.dumps(moves, separators=(",", ":")) + "\n")
    body = model.compiler.physical(model.g, model.witness, model.word, model.record, changed, model.pairs)
    spec = importlib.util.spec_from_file_location("pinned_sink_gate", args.sink_gate.resolve())
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    physical = gate.sinks_record(model.g, model.witness, model.word, model.record, changed, model.pairs, sinks, body)
    require({int(r): n for r, n in physical["child_histogram"].items()} == histogram, "complete literal/sink-gate histogram differs")
    require(physical["W_per_vertex"] == model.reference["W_per_vertex"] and
            physical["rank_per_vertex"] == model.reference["rank_per_vertex"], "complete sink width/rank differs")
    require(model.moments(histogram)["H"] <= model.moments(before_histogram)["H"] + 5e-15, "full sink moment worsened")
    for name, data in (("body-profile.json", body), ("sink-profile.json", physical)):
        (args.output / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    result = {"status": "DISCOVERY_COMPLETE_SUBSTITUTED_SINK_WORD", "variant": args.variant,
              "seed": args.seed, "requested_passes": args.passes, "max_nodes": args.max_nodes,
              "trial_exact": str(args.trial), "moves": len(moves), "passes": passes,
              "frames_changed_from_start": sum(a != b for a, b in zip(before_frames, model.frames)),
              "frames_sha256": sha(frame_path), "start_frames_sha256": sha(args.start_frames) if args.start_frames else None,
              "m": model.m, "W_per_vertex": physical["W_per_vertex"], "rank_per_vertex": physical["rank_per_vertex"],
              "physical_roles": physical["physical_R"], "sinks": len(sinks), "max_child": max(histogram),
              "literal_registers": model.literal_registers, "literal_frame_edges": len(model.edges),
              "histogram": histogram, "moments": model.moments(histogram), "start_moments": model.moments(before_histogram),
              "local_checks": checks, "full_body_and_sink_replay": True,
              "context_sha256": sha(args.context), "source_context": json.loads(args.context.read_text()),
              "sink_pins": {name: sha(path) for name, path in (("sinks", args.sinks), ("reference", args.sink_profile),
                                                            ("protocol", args.sink_protocol), ("gate", args.sink_gate))},
              "search_sha256": {name: sha(Path(__file__).parent / name) for name in
                                ("physical_search.py", "physical_exchanges.py", "physical_frontier.py", "physical_closure.py", "physical_sinks.py")},
              "wall_seconds": time.monotonic() - started, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "scope": "One exact substituted sink stage, fixed body DAG/word/gauges/aliases/sinks. Direct complete paid register-chain pricing and actual upstream forward/reflected sink gate. Independent exact signed operator, geometric review, rigorous moments, ordinary conversion and assembly remain separate."}
    (args.output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("variant", "moves", "moments", "wall_seconds")}), flush=True)


if __name__ == "__main__":
    main()
