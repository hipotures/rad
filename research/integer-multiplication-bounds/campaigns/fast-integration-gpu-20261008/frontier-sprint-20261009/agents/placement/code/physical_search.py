#!/usr/bin/env python3
"""Bounded complete-moment frame moves on a pinned paired-cube physical word.

The scalar DAG, selected gauges, slot pairs, compensation deadlines, binary
supplier, and assembly are frozen. A move changes the common frame at one
operation or a connected set of equal-frame operations. The exact permitted
interval is lower=span(values,incoming frames), upper=intersection(outgoing
frames). All moved operations receive the same endpoint frame. The complete
physical ledger is independently recomputed, and the upstream physical checker
is run on every final candidate. Numerical moments are discovery-only.

Original physical compiler: eumemic, with Anthropic Claude assistance; signed
word and selected module: icekylinx; inherited Apache-2.0. New search prepared
with OpenAI assistance.
"""
import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import importlib
import json
import math
from pathlib import Path
import random
import resource
import sys
import time


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Physical:
    def __init__(self, source, export, trial):
        sys.path.insert(0, str(source / "scripts"))
        self.compiler = importlib.import_module("paired_cube_physical")
        module = importlib.import_module("paired_cube.frames")
        self.basis, self.perp, self.contained = module.basis, module.perp, module.contained
        self.source, self.export = source, export
        self.g, self.witness, self.word = [json.loads((export / name).read_text())
                                          for name in ("graph.json", "frames.json", "selection.json")]
        self.record = json.loads((source / "certificates/paired-cube-complex-input.json").read_text())
        self.reference = json.loads((source / "certificates/paired-cube-physical-input.json").read_text())
        pair_payload = json.loads((source / "references/paired-cube/physical/pairs.json").read_text())
        self.pairs = pair_payload["pairs"] if isinstance(pair_payload, dict) else pair_payload
        g, word, h, R = self.g, self.word, self.g["h"], self.record["R"]
        self.h, self.R, self.m, self.v = h, R, 3 * h, g["v"]
        self.ops = [tuple(o) for o in word["ops"]]
        self.original = [self.perp(tuple(self.witness["annihilators"][x]), h) for _, _, x in self.ops]
        self.frames = list(self.original)
        frame_payload = json.loads((source / "references/paired-cube/physical/frames.json").read_text())
        for i, F in (frame_payload["frames"] if isinstance(frame_payload, dict) else frame_payload):
            self.frames[i] = tuple(F)
        self.initial = list(self.frames)
        args = [None] + [None if a is None else (a[0] + 1, a[1] + 1) for a in g["args"]]
        self.spans = [()] * len(args)
        for x in range(1, len(args)):
            self.spans[x] = ((g["inputs"][x - 1],) if args[x] is None
                             else self.basis(self.spans[args[x][0]] + self.spans[args[x][1]]))
        self.sources = {int(x): s for x, s in word["sources"].items()}
        start = [()] * R
        for x, s in self.sources.items():
            start[s] = (g["inputs"][x - 1],)
        self.gauges = {}
        for z in word["selected"]:
            self.gauges[z["role"]] = self.perp(tuple(z["annihilator"]), h)
            start[z["role"]] = self.gauges[z["role"]]
        rootframe, self.rootkind = {}, {}
        for r, s in zip(g["roots"], word["rootroles"]):
            rootframe[s] = (self.spans[r["node"] + 1] if r["kind"] == "center"
                            else self.perp(self.basis(g["inputs"][t] for t in r["targets"]), h))
            self.rootkind[s] = r["kind"]
        self.rootframe = rootframe
        self.donors = {int(a): int(b) for a, b, _ in self.pairs}
        self.merged = {int(b) for _, b, _ in self.pairs}
        role_ops = defaultdict(list)
        for i, (a, b, _) in enumerate(self.ops):
            role_ops[a].append(i)
            role_ops[b].append(i)
        self.role_ops = role_ops
        self.fixed = []
        self.edges = []
        self.incoming, self.outgoing = defaultdict(list), defaultdict(list)
        self.neighbors = defaultdict(set)
        full = self.basis(1 << i for i in range(h))

        def fixed(F):
            self.fixed.append(F)
            return -len(self.fixed)

        for s in range(R):
            seq = [fixed(start[s])] + role_ops[s]
            if s in rootframe:
                seq.append(fixed(rootframe[s]))
            seq.append(fixed(self.gauges[self.donors[s]] if s in self.donors else full))
            for a, b in zip(seq, seq[1:]):
                self.edges.append((a, b))
                if b >= 0:
                    self.incoming[b].append(a)
                if a >= 0:
                    self.outgoing[a].append(b)
                if a >= 0 and b >= 0:
                    self.neighbors[a].add(b)
                    self.neighbors[b].add(a)
        self.trial = trial
        self.f = [0.] + [r * math.expm1(trial * math.log(self.m / r)) for r in range(1, self.m + 1)]
        self.initial_histogram = self.histogram()
        require(self.initial_histogram == {int(r): c for r, c in self.reference["child_histogram"].items()},
                "complete independent control histogram differs from pinned certificate")

    def frame(self, index):
        return self.frames[index] if index >= 0 else self.fixed[-index - 1]

    @lru_cache(maxsize=100000)
    def cap(self, A, B):
        return self.perp(self.basis(self.perp(A, self.h) + self.perp(B, self.h)), self.h)

    def boundary(self, group):
        inside = set(group)
        inc = [(a, b) for b in group for a in self.incoming[b] if a not in inside]
        out = [(a, b) for a in group for b in self.outgoing[a] if b not in inside]
        return inc, out

    def endpoints(self, group):
        require(len({self.frames[i] for i in group}) == 1, "joint group frames differ")
        inc, out = self.boundary(group)
        lower = self.basis(tuple(x for i in group for x in self.spans[self.ops[i][2]])
                           + tuple(x for a, _ in inc for x in self.frame(a)))
        upper = self.basis(1 << i for i in range(self.h))
        for _, b in out:
            upper = self.cap(upper, self.frame(b))
        current = self.frames[group[0]]
        require(self.contained(lower, current) and self.contained(current, upper), "current frame outside feasible interval")
        return lower, upper, inc, out

    def change(self, group):
        lower, upper, inc, out = self.endpoints(group)
        old = self.frames[group[0]]

        def cost(F):
            d = len(F)
            return math.fsum([self.f[d - len(self.frame(a))] for a, _ in inc]
                             + [self.f[len(self.frame(b)) - d] for _, b in out])

        options = [lower, upper]
        best = min(options, key=lambda F: (cost(F), len(F), F))
        delta = cost(best) - cost(old)
        if delta < -1e-12:
            for i in group:
                self.frames[i] = best
            return {"ops": list(group), "old_rank": len(old), "new_rank": len(best),
                    "delta_excess_local": delta}
        return None

    def validate(self):
        for i, (_, _, x) in enumerate(self.ops):
            require(self.contained(self.spans[x], self.frames[i]), f"value span {i}")
        for a, b in self.edges:
            require(self.contained(self.frame(a), self.frame(b)), f"chain edge {a},{b}")
        return {"value_spans": True, "all_role_chain_edges_and_pair_handoffs": True,
                "arithmetic": "exact F2; pinned helper routines"}

    def histogram(self):
        local = Counter()
        for s in self.sources.values():
            local[1] += 1
        for a, b in self.edges:
            r = len(self.frame(b)) - len(self.frame(a))
            require(r >= 0, "negative edge width")
            if r:
                local[r] += 1
        for s, kind in self.rootkind.items():
            if kind == "center":
                local[len(self.rootframe[s])] += 1
        children = Counter({r: 3 * c for r, c in local.items()})
        for key in ("source_data_histogram", "target_data_histogram"):
            children.update({int(r): 3 * c for r, c in self.record[key].items() if int(r)})
        tails = Counter(len(F) for s, F in self.gauges.items() if s not in self.merged)
        children.update({3 * d: c for d, c in tails.items() if d})
        children[2] += 2 * self.v
        self.local_histogram = local
        require(sum(r * c for r, c in children.items()) == self.reference["rank_per_vertex"], "complete rank mass")
        return dict(sorted(children.items()))

    def moments(self, histogram):
        W = self.reference["W_per_vertex"]
        def H(s):
            return math.fsum(c * r * math.exp(s * math.log(self.m / r)) for r, c in histogram.items()) / (self.m * W)
        lo, hi = 0., 0.01
        for _ in range(60):
            mid = (lo + hi) / 2
            if H(mid) < 1:
                lo = mid
            else:
                hi = mid
        return {"common_trial_s": self.trial, "H": H(self.trial),
                "discovery_complex_root": (lo + hi) / 2, "arithmetic": "binary64 discovery only"}

    def groups(self, policy, rng):
        n = len(self.ops)
        if policy == "singletons":
            return [(i,) for i in range(n)]
        if policy == "pairs":
            return [(i, j) for i in range(n) for j in sorted(self.neighbors[i])
                    if i < j and self.frames[i] == self.frames[j]]
        visited, groups = set(), []
        for i in range(n):
            if i in visited:
                continue
            visited.add(i)
            group, stack = [i], [i]
            while stack:
                x = stack.pop()
                for j in sorted(self.neighbors[x]):
                    if j not in visited and self.frames[j] == self.frames[i]:
                        visited.add(j)
                        group.append(j)
                        stack.append(j)
            groups.append(tuple(sorted(group)))
        return groups


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--export", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--variant", choices=["control", "singletons", "pairs", "components"], required=True)
    p.add_argument("--passes", type=int, default=3)
    p.add_argument("--seed", type=int, default=20261009)
    p.add_argument("--trial", type=float, default=5885669 / 10**10)
    p.add_argument("--skip-replay", action="store_true")
    args = p.parse_args()
    require(not args.output.exists(), "attempt output already exists")
    args.output.mkdir(parents=True)
    start = time.monotonic()
    model = Physical(args.source.resolve(), args.export.resolve(), args.trial)
    rng = random.Random(args.seed)
    moves, passes = [], []
    if args.variant != "control":
        for k in range(args.passes):
            groups = model.groups(args.variant, rng)
            if k % 2:
                groups.reverse()
            before = len(moves)
            for group in groups:
                # An overlapping earlier pair move may have changed a member.
                if len({model.frames[i] for i in group}) != 1:
                    continue
                change = model.change(group)
                if change:
                    moves.append(change)
            passes.append({"pass": k, "groups": len(groups), "accepted_moves": len(moves) - before})
            print(json.dumps(passes[-1]), flush=True)
            if len(moves) == before:
                break
    local = model.validate()
    hist = model.histogram()
    changed = [[i, list(F)] for i, F in enumerate(model.frames) if F != model.original[i]]
    frames_path = args.output / "frames.json"
    frames_path.write_text(json.dumps(changed, separators=(",", ":")) + "\n")
    (args.output / "moves.json").write_text(json.dumps(moves, separators=(",", ":")) + "\n")
    upstream = None
    if not args.skip_replay:
        upstream = model.compiler.physical(model.g, model.witness, model.word, model.record, changed, model.pairs)
        require({int(r): c for r, c in upstream["child_histogram"].items()} == hist, "upstream complete histogram disagrees")
        (args.output / "physical-profile.json").write_text(json.dumps(upstream, indent=2, sort_keys=True) + "\n")
    result = {"status": "DISCOVERY", "variant": args.variant, "seed": args.seed, "passes": passes,
              "m": model.m, "W_per_vertex": model.reference["W_per_vertex"],
              "rank_per_vertex": model.reference["rank_per_vertex"], "max_child": max(hist),
              "moves": len(moves), "frames_changed_from_public": sum(a != b for a, b in zip(model.frames, model.initial)),
              "frames_sha256": sha(frames_path), "histogram": hist, "moments": model.moments(hist),
              "control_moments": model.moments(model.initial_histogram), "local_checks": local,
              "upstream_physical_replay": upstream is not None, "wall_seconds": time.monotonic() - start,
              "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "source_snapshot": args.source.name,
              "export_sha256": {name: sha(args.export / name) for name in ("graph.json", "frames.json", "selection.json")},
              "exclusions": ["independent signed/reflected audit", "rigorous moments", "assembly certificate", "accepted final kappa"]}
    (args.output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("variant", "moves", "frames_changed_from_public", "moments", "wall_seconds")}), flush=True)


if __name__ == "__main__":
    main()
