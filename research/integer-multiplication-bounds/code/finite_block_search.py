#!/usr/bin/env python3
"""Exact experiments with cancellation-free weighted block recursions.

The reference is CrocSwap/integer-mult-bounds at
bcd4ebde8692383539f8a48734e5fbf3a18a32c2. Its original scripts are imported
read-only from an explicitly supplied checkout. Every experiment checks the
complete formal support map. Exploratory scores do not certify multiplication.
"""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import sys
import time


def install_reference(path: str) -> None:
    sys.path.insert(0, str(Path(path).resolve() / "scripts"))


def make_block_class():
    from exclusion_circuit import ExclusionCircuit

    class BlockCircuit(ExclusionCircuit):
        """Weighted exclusion through arbitrary bounded blocks.

        Between-block exclusions use the disjoint far/strip/cross partition.
        Two excluded points in one block use its surviving internal graph and
        outgoing edges, plus the coarse single-block exclusion. No cancellation
        is permitted at any node.
        """

        def __init__(self, n, sizes=(2,), base=4, combine=0, singleton=None):
            self.sizes = tuple(sizes)
            self.base = base
            self.combine = combine
            self.singleton = singleton
            super().__init__(n)

        def pair(self, points):
            return self.block(
                points,
                {(a, b): self.variables[a, b] for a, b in combinations(points, 2)},
                {a: 0 for a in points},
                0,
            )

        def block(self, points, edges, weights, depth):
            def e(a, b):
                return edges[tuple(sorted((a, b)))]

            def direct(omit=()):
                omitted = set(omit)
                return self.total(
                    [z for p, z in edges.items() if not omitted.intersection(p)]
                    + [z for p, z in weights.items() if p not in omitted]
                )

            if len(points) <= self.base:
                return (
                    direct(),
                    {a: direct((a,)) for a in points},
                    {(a, b): direct((a, b)) for a, b in combinations(points, 2)},
                )
            size = self.sizes[min(depth, len(self.sizes) - 1)]
            assert size >= 2
            if depth == 0 and self.singleton is not None:
                assert size == 2 and len(points) % 2 == 1
                place = 2 * self.singleton
                assert 0 <= place < len(points)
                groups = (
                    [points[i : i + 2] for i in range(0, place, 2)]
                    + [points[place : place + 1]]
                    + [points[i : i + 2] for i in range(place + 1, len(points), 2)]
                )
            else:
                groups = [points[i : i + size] for i in range(0, len(points), size)]
            ng = len(groups)
            coarse = {
                (i, j): self.total([e(a, b) for a in groups[i] for b in groups[j]])
                for i, j in combinations(range(ng), 2)
            }
            coarse_weights = {
                i: self.total(
                    [weights[a] for a in g] + [e(a, b) for a, b in combinations(g, 2)]
                )
                for i, g in enumerate(groups)
            }
            total, outside, far = self.block(
                list(range(ng)), coarse, coarse_weights, depth + 1
            )
            strips, all_strips = {}, {}
            for i, g in enumerate(groups):
                other = [j for j in range(ng) if j != i]
                for a in g:
                    surviving = [u for u in g if u != a]
                    carry = self.total(
                        [weights[u] for u in surviving]
                        + [e(u, v) for u, v in combinations(surviving, 2)]
                    )
                    vals = [
                        self.total([e(u, v) for u in surviving for v in groups[j]])
                        for j in other
                    ]
                    st, one, _ = self.vector([carry] + vals, False)
                    strips[a] = {j: z for j, z in zip(other, one[1:])}
                    all_strips[a] = st
            single = {
                a: self.add(outside[i], all_strips[a])
                for i, g in enumerate(groups)
                for a in g
            }
            out = {}
            for i, g in enumerate(groups):
                for a, b in combinations(g, 2):
                    surviving = [u for u in g if u not in (a, b)]
                    own = self.total(
                        [weights[u] for u in surviving]
                        + [e(u, v) for u, v in combinations(surviving, 2)]
                        + [
                            self.total(
                                [e(u, v) for v in points if v not in g]
                            )
                            for u in surviving
                        ]
                    )
                    out[a, b] = self.add(outside[i], own)
            for i, j in combinations(range(ng), 2):
                for a in groups[i]:
                    left = self.add(far[i, j], strips[a][j])
                    for b in groups[j]:
                        cross = self.total(
                            [
                                e(u, v)
                                for u in groups[i]
                                if u != a
                                for v in groups[j]
                                if v != b
                            ]
                        )
                        if self.combine == 0:
                            value = self.add(left, self.add(strips[b][i], cross))
                        elif self.combine == 1:
                            value = self.total([far[i, j], strips[a][j], strips[b][i], cross])
                        else:
                            value = self.add(
                                self.add(far[i, j], cross),
                                self.add(strips[a][j], strips[b][i]),
                            )
                        out[tuple(sorted((a, b)))] = value
            return total, single, out

    return BlockCircuit


class GroupUnion:
    """Global common-point graph with configurable group point order.

    Adapted from the pinned reference's SharedPointCircuit. Local maps are
    imported; global equalities, both frame directions, and independent small
    support expansions are checked here. A shared multi-group sum is a pair
    star, so its core and union determine its exact support.
    """

    def __init__(self, h, local_factory, ordering="natural", seed=0, common_aware=False):
        assert h >= 6 and h != 9
        self.h = h
        self.inputs = list(combinations(range(h), 3))
        self.variables = {t: i + 1 for i, t in enumerate(self.inputs)}
        self.args = [None] * (len(self.inputs) + 1)
        self.core = [0] + [sum(1 << i for i in t) for t in self.inputs]
        self.union = list(self.core)
        self.provenance = [None] * len(self.args)
        self.points = []
        rng = random.Random(seed)
        for i in range(h):
            points = [j for j in range(h) if j != i]
            if ordering == "paired":
                assert h % 2 == 0
                points = [
                    j for j in range(h) if j // 2 != i // 2
                ] + [i ^ 1]
            elif ordering == "cyclic":
                points = [(i + k) % h for k in range(1, h)]
            elif ordering == "random":
                rng.shuffle(points)
            elif ordering not in ("natural", "gap"):
                raise ValueError(ordering)
            self.points.append(points)
        self.locals = [
            local_factory(h - 1, i) if common_aware else local_factory(h - 1)
            for i in range(h)
        ]
        self.pair_ids = [
            {
                tuple(sorted(points[k] for k in pair)): i + 1
                for i, pair in enumerate(local.inputs)
            }
            for points, local in zip(self.points, self.locals)
        ]
        lookup = {}
        self.outputs = {}
        self.merged = 0
        for common in range(h):
            local = self.locals[common]
            local.verify()
            mapping = {}
            for node in sorted(local.active):
                if local.args[node] is None:
                    a, b = local.inputs[node - 1]
                    t = tuple(sorted((common, self.points[common][a], self.points[common][b])))
                    mapping[node] = self.variables[t]
                    continue
                a, b = (mapping[x] for x in local.args[node])
                core = self.core[a] & self.core[b]
                union = self.union[a] | self.union[b]
                assert core & (1 << common)
                key = (core, union)
                if core.bit_count() >= 2 and key in lookup:
                    mapping[node] = lookup[key]
                    self.merged += 1
                    continue
                new = len(self.args)
                mapping[node] = new
                self.args.append((a, b))
                self.core.append(core)
                self.union.append(union)
                self.provenance.append((common, node))
                if core.bit_count() >= 2:
                    lookup[key] = new
            for pair, node in sorted(local.outputs.items()):
                t = tuple(sorted((common, *(self.points[common][x] for x in pair))))
                self.outputs[common, t] = mapping[node]
        self.active = set()
        stack = list(self.outputs.values())
        while stack:
            n = stack.pop()
            if n in self.active:
                continue
            self.active.add(n)
            if self.args[n]:
                stack.extend(self.args[n])
        self.additions = sum(self.args[n] is not None for n in self.active)

    @lru_cache(maxsize=16384)
    def support_in(self, node, common):
        assert self.core[node] & (1 << common)
        if self.args[node] is None:
            pair = tuple(x for x in self.inputs[node - 1] if x != common)
            return 1 << (self.pair_ids[common][pair] - 1)
        old, local = self.provenance[node]
        if old == common:
            return self.locals[old].support[local]
        assert self.core[node].bit_count() == 2
        fixed = self.core[node] & ~(1 << common)
        other = fixed.bit_length() - 1
        remaining = self.union[node] & ~self.core[node]
        answer = 0
        while remaining:
            bit = remaining & -remaining
            remaining -= bit
            pair = tuple(sorted((other, bit.bit_length() - 1)))
            answer |= 1 << (self.pair_ids[common][pair] - 1)
        return answer

    def contained(self, a, b):
        common = (self.core[b] & -self.core[b]).bit_length() - 1
        return bool(self.core[a] & (1 << common)) and not (
            self.support_in(a, common) & ~self.support_in(b, common)
        )

    def verify(self):
        digest = sha256()
        for node in sorted(self.active):
            if self.args[node]:
                a, b = self.args[node]
                common, local = self.provenance[node]
                assert a < node and b < node
                A, B = self.support_in(a, common), self.support_in(b, common)
                assert not A & B
                assert A | B == self.locals[common].support[local]
                assert self.core[node] == self.core[a] & self.core[b]
                assert self.union[node] == self.union[a] | self.union[b]
            assert self.core[node]
            digest.update(json.dumps((node, self.args[node], self.provenance[node]), separators=(",", ":")).encode() + b"\n")
        for (common, target), node in sorted(self.outputs.items()):
            excluded = tuple(sorted(self.points[common].index(x) for x in target if x != common))
            local = self.locals[common]
            assert self.support_in(node, common) == local.support[local.outputs[excluded]]
            digest.update(json.dumps((common, target, node), separators=(",", ":")).encode() + b"\n")
        return {
            "h": self.h,
            "inputs": len(self.inputs),
            "partial_outputs": len(self.outputs),
            "additions": self.additions,
            "roles": self.additions + len(self.outputs),
            "merged_additions": self.merged,
            "all_additions_disjoint": True,
            "all_partial_outputs_exact": True,
            "every_node_has_common_point": True,
            "circuit_sha256": digest.hexdigest(),
        }

    def compile(self):
        from exclusion_circuit import ExclusionCircuit
        return ExclusionCircuit.compile(self)

    def verify_frames(self):
        code = self.compile()
        frames = [0] * code["roles"]
        for triple, slot in code["sources"].items():
            frames[slot] = self.variables[triple]
        for node, ins, outs in code["gates"]:
            for slot in set(ins + outs):
                assert not frames[slot] or self.contained(frames[slot], node)
                frames[slot] = node
        for target, slot in code["outputs"].items():
            assert frames[slot] == self.outputs[target]
        reverse = [0] * code["roles"]
        for target, slot in code["outputs"].items():
            reverse[slot] = self.outputs[target]
        for node, ins, outs in reversed(code["gates"]):
            for slot in set(ins + outs):
                assert not reverse[slot] or self.contained(node, reverse[slot])
                reverse[slot] = node
        for triple, slot in code["sources"].items():
            assert reverse[slot] == self.variables[triple]
        return {
            "roles": code["roles"],
            "forward_frames_nested": True,
            "reverse_complement_frames_nested": True,
            "nondegeneracy": "Every source span has a common point; its complement is nondegenerate.",
        }

    def program(self):
        code = self.compile()
        index = {t: i for i, t in enumerate(self.inputs)}
        return {
            "triples": self.inputs,
            "roles": code["roles"],
            "gates": [(ins, outs) for _, ins, outs in code["gates"]],
            "sources": [(index[t], slot) for t, slot in code["sources"].items()],
            "outputs": [(index[t], slot) for (_, t), slot in code["outputs"].items()],
        }

    def verify_small_expansion(self):
        support = [0] * len(self.args)
        for n in sorted(self.active):
            if self.args[n]:
                a, b = self.args[n]
                assert not support[a] & support[b]
                support[n] = support[a] | support[b]
            else:
                support[n] = 1 << (n - 1)
        for (common, target), n in self.outputs.items():
            expected = sum(
                1 << i
                for i, t in enumerate(self.inputs)
                if set(t).intersection(target) == {common}
            )
            assert support[n] == expected
        return {"independent_expansion": True, "all_output_coefficients_exact": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--n", type=int, default=49)
    parser.add_argument("--sizes", default="2")
    parser.add_argument("--base", type=int, default=4)
    parser.add_argument("--combine", type=int, default=0)
    parser.add_argument("--global-h", type=int)
    parser.add_argument("--ordering", default="natural")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--frames", action="store_true")
    parser.add_argument("--small", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    install_reference(args.reference)
    cls = make_block_class()
    sizes = tuple(int(x) for x in args.sizes.split(","))
    factory = lambda n: cls(n, sizes, args.base, args.combine)
    start = time.monotonic()
    result = {"settings": vars(args), "reference_commit": "bcd4ebde8692383539f8a48734e5fbf3a18a32c2"}
    if args.global_h:
        if args.ordering == "gap":
            factory = lambda n, common: cls(n, sizes, args.base, args.combine, common//2)
        c = GroupUnion(args.global_h, factory, args.ordering, args.seed, args.ordering == "gap")
        result["global"] = c.verify()
        result["local"] = c.locals[0].verify()
        if args.frames:
            result["frames"] = c.verify_frames()
        if args.small:
            result["independent"] = c.verify_small_expansion()
            from dag_network import exact_invocation, shared_scalar_model
            program = c.program()
            result["dirty_scratch"] = [exact_invocation(args.global_h, inverse, program) for inverse in (False, True)]
            result["three_stage"] = shared_scalar_model(args.global_h, args.seed, program)
    else:
        c = factory(args.n)
        result["local"] = c.verify()
        if args.frames:
            result["embedding"] = c.verify_embedding()
    result["elapsed_seconds"] = time.monotonic() - start
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
