#!/usr/bin/env python3
"""Complete-paid-profile discovery on a frozen PR120 exported word.

This is a discovery tool, not an accepted conditional exponent certificate.
PR120 / eumemic supplies the immutable scalar DAG, original saturated placement,
and exact F2 helpers; PR110 / Avi Eisenberg supplies the deferred-word compiler.
Only placement changes. The original source snapshot is an explicit CLI input.
Prepared with OpenAI assistance.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import heapq
import importlib.util
import json
import math
from pathlib import Path
import resource
import time


def require(value, message):
    if not value:
        raise ValueError(message)


def read_module(source):
    path = source / "research/deferred-replayed/complex_deferred.py"
    spec = importlib.util.spec_from_file_location("pinned_complex_deferred", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Instance:
    def __init__(self, word, module, saving):
        self.w, self.a, self.saving = word, module, saving
        self.h, self.m = word["h"], word["m"]
        self.reach = {int(s): ts for s, ts in word["reach"].items()}
        self.U = {int(s): tuple(B) for s, B in word["U"].items()}
        self.first = word["first_node"]
        self.r = [len(self.U[x]) for x in self.first]
        touched = set(word["centre_roles"])
        for i in word["phase1"]:
            op = word["ops"][i]
            if op[0] in ("add", "copy"):
                touched.update(op[1:3])
        blocked = touched | set(word["reach_all"])
        from itertools import combinations
        self.masks = [sum(1 << i for i in T) for T in combinations(range(self.h), 3)]
        cand = {}
        for s in range(word["R"]):
            if s in blocked:
                continue
            X = module.restrict(self.U[self.first[s]], [self.masks[t] for t in self.reach[s]])
            if X and module.nondeg(X):
                cand[s] = module.sat_basis(X)
        self.cand = cand
        self.incidence = defaultdict(set)
        for s in cand:
            for t in self.reach[s]:
                self.incidence[t].add(s)
        # expm1 keeps small differences accurate; linear rank mass cancels.
        self.power = [0.0] + [t * math.expm1(-saving * math.log(t)) for t in range(1, self.m + 1)]

    def feasible(self, s, placed, by_target):
        a = self.a
        X, changed = self.cand[s], True
        while changed and X:
            changed = False
            for t in sorted(self.reach[s]):
                for w in by_target.get(t, ()):
                    B = placed[w]
                    if ((len(B) >= len(X) and not a.sat_contained(X, B))
                            or (len(B) < len(X) and not a.sat_contained(B, X))):
                        X = a.sat_cap(X, B)
                        changed = True
                    if not X:
                        break
                if not X:
                    break
            if X and not a.sat_nondeg(X):
                before = X
                X = a.sat_nonsingular_part(X)
                require(a.sat_contained(X, before) and a.sat_nondeg(X), "bad extracted complement")
                require(len(X) < len(before), "degenerate extraction did not shrink")
                changed = True
        return X

    def cost(self, s, X, levels):
        d, r, e, f = len(X), self.r[s], self.m - self.h, self.power
        delta = f[r - d] + f[e + d] - f[r] - f[e]
        for t in self.reach[s]:
            ds = levels.get(t, {})
            if d in ds:
                continue
            lower = max((z for z in ds if z < d), default=0)
            upper = min((z for z in ds if z > d), default=self.h - 1)
            delta += f[d - lower] + f[upper - d] - f[upper - lower]
        return delta

    def validate(self, placed):
        a = self.a
        by_target = defaultdict(list)
        for s, X in placed.items():
            require(s in self.cand, "ineligible role")
            require(a.sat_nondeg(X), "degenerate deferral")
            require(a.sat_contained(X, self.cand[s]), "frame outside eligible subspace")
            require(a.sat_contained(X, a.sat_basis(self.U[self.first[s]])), "frame outside entrance")
            require(all(not a.sat_dot(x, self.masks[t]) for x in X for t in self.reach[s]), "target orthogonality")
            for t in self.reach[s]:
                by_target[t].append(s)
        for t, ss in by_target.items():
            ss.sort(key=lambda s: (len(placed[s]), s))
            require(all(a.sat_contained(placed[x], placed[y]) for x, y in zip(ss, ss[1:])), f"target nesting {t}")
        return {"eligible_roles": len(self.cand), "placed_roles": len(placed),
                "nondegeneracy": True, "start_containment": True,
                "target_orthogonality": True, "target_nesting": True,
                "arithmetic": "exact F2 via pinned source helpers; not a full signed replay"}

    def histogram(self, placed):
        w, h, m, v = self.w, self.h, self.m, self.w["v"]
        root_roles = {int(s): j for s, j in w["role_root"].items()}
        z = Counter()
        for s in range(w["R"]):
            ds = [len(placed.get(s, ())), len(self.U[self.first[s]])]
            ds.extend(len(self.U[x]) for x in w["holds"][s][1:])
            if s in root_roles:
                ds.append(h - 1)
            ds.append(h)
            require(all(a <= b for a, b in zip(ds, ds[1:])), "role dimensions not nested")
            for a, b in zip(ds[:-1], ds[1:-1]):
                if b > a:
                    z[b - a] += 2 * v
            if s in root_roles and w["roots"][root_roles[s]]["kind"] == "centre":
                z[h - 1] += 2 * v
            z[h - ds[-2]] += 2 * v
            z[m - h + ds[0]] += 2 * v
        levels = defaultdict(set)
        for s, X in placed.items():
            for t in self.reach[s]:
                levels[t].add(len(X))
        for t in range(v):
            ds = sorted(levels[t] | {0, h - 1})
            for a, b in zip(ds, ds[1:]):
                z[b - a] += 2 * v
        z[h - 1] += 2 * w["N"]
        z[(h - 1) ** 2] += 2 * w["N"]
        z[1] += w["N"]
        z.pop(0, None)
        require(sum(t * count for t, count in z.items()) == w["s"], "rank mass differs")
        require(all(0 < t < m for t in z), "noncontracting child")
        return dict(sorted(z.items()))

    def moments(self, rows):
        def moment(s):
            return math.fsum(count * t / (self.m * self.w["W"]) * math.exp(s * math.log(self.m / t))
                             for t, count in rows.items())
        lo, hi = 0.0, 0.01
        for _ in range(55):
            mid = (lo + hi) / 2
            if moment(mid) < 1:
                lo = mid
            else:
                hi = mid
        return {"common_trial_s": self.saving, "common_trial_H": moment(self.saving),
                "research_target_s": 0.00012, "research_target_H": moment(0.00012),
                "discovery_root": (lo + hi) / 2, "arithmetic": "binary64, discovery only"}


def select(instance, variant):
    cand, reach = instance.cand, instance.reach
    if variant == "control":
        return instance.a.saturated_placement(cand, reach), {"policy": "unchanged saturated placement"}
    placed, by_target, levels = {}, defaultdict(list), defaultdict(Counter)

    def add(s, X):
        placed[s] = X
        for t in reach[s]:
            by_target[t].append(s)
            levels[t][len(X)] += 1

    if variant in ("static_cost", "cost_density"):
        def priority(s):
            delta = instance.cost(s, cand[s], {})
            if variant == "cost_density":
                neighbors = set().union(*(instance.incidence[t] for t in reach[s]))
                delta /= max(1, len(neighbors))
            return (delta, -len(cand[s]), s)
        for s in sorted(cand, key=priority):
            X = instance.feasible(s, placed, by_target)
            if X:
                add(s, X)
        return placed, {"policy": variant, "actual_downstream_target_cost": True}

    require(variant == "dynamic_cost", "unknown policy")
    pending = set(cand)
    versions, frames, heap = Counter(), {}, []
    updates = 0

    def refresh(s):
        nonlocal updates
        X = instance.feasible(s, placed, by_target)
        frames[s] = X
        versions[s] += 1
        updates += 1
        if X:
            heapq.heappush(heap, (instance.cost(s, X, levels), -len(X), s, versions[s]))

    for s in sorted(pending):
        refresh(s)
    while heap:
        delta, _, s, version = heapq.heappop(heap)
        if s not in pending or version != versions[s]:
            continue
        pending.remove(s)
        add(s, frames[s])
        affected = set().union(*(instance.incidence[t] for t in reach[s])) & pending
        for other in sorted(affected):
            refresh(other)
    return placed, {"policy": variant, "exact_incremental_complete_profile_cost": True,
                    "affected_role_refreshes": updates, "remaining_infeasible_roles": len(pending)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--word", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--variant", choices=["control", "static_cost", "cost_density", "dynamic_cost"], required=True)
    parser.add_argument("--trial", type=float, default=109140237 / 10**12)
    args = parser.parse_args()
    require(not args.output.exists(), "attempt output already exists")
    args.output.mkdir(parents=True)
    started = time.monotonic()
    word = json.loads(args.word.read_text())
    instance = Instance(word, read_module(args.source), args.trial)
    original = {int(s): instance.a.sat_basis(X) for s, X in word["placed"].items()}
    require(instance.histogram(original) == {int(t): c for t, c in word["rows"].items()}, "independent ledger differs from exported control")
    placed, policy = select(instance, args.variant)
    checks = instance.validate(placed)
    rows = instance.histogram(placed)
    schedule = {"placed": {str(s): list(X) for s, X in sorted(placed.items())},
                "deferred": sorted(placed, key=lambda s: (len(placed[s]), s))}
    schedule_bytes = (json.dumps(schedule, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (args.output / "schedule.json").write_bytes(schedule_bytes)
    result = {"status": "DISCOVERY", "variant": args.variant, "policy": policy,
              "word_sha256": hashlib.sha256(args.word.read_bytes()).hexdigest(),
              "schedule_sha256": hashlib.sha256(schedule_bytes).hexdigest(),
              "local_validity": checks, "m": instance.m, "W": word["W"], "rank_mass": word["s"],
              "max_child": max(rows), "deferred_dims": dict(sorted(Counter(map(len, placed.values())).items())),
              "histogram": rows, "moments": instance.moments(rows),
              "changed_frames": sum(original.get(s) != placed.get(s) for s in set(original) | set(placed)),
              "wall_seconds": time.monotonic() - started,
              "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "source_snapshot": args.source.name,
              "exclusions": ["full signed/reflected replay", "rigorous moment enclosure", "assembly certificate", "accepted final kappa"]}
    (args.output / "profile.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("variant", "wall_seconds", "changed_frames", "moments")}), flush=True)


if __name__ == "__main__":
    main()
