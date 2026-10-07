#!/usr/bin/env python3
"""Exact finite tree-projection circuit adapted from Kaski et al. (2012).

Source: Fast Monotone Summation over Disjoint Sets, arXiv:1208.0554v1,
Lemmas 1, 3 and 4. Inputs and outputs have fixed cardinalities. Inactive
leaves in the enclosing binary tree are omitted, and identical supports are
interned. This is a literature-derived comparison, not a novelty claim.
No third-party dependency is required. Original reference files are read-only.
"""

import argparse
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
import time


class TreeProjectionCircuit:
    def __init__(self, n, p=2, q=2, intersection=0, order=None):
        self.n, self.p, self.q, self.intersection = n, p, q, intersection
        self.order = list(range(n)) if order is None else list(order)
        assert sorted(self.order) == list(range(n))
        self.inputs = list(combinations(range(n), p))
        self.variables = {s: i + 1 for i, s in enumerate(self.inputs)}
        self.support = [0] + [1 << i for i in range(len(self.inputs))]
        self.args = [None] * len(self.support)
        self.lookup = {s: i for i, s in enumerate(self.support)}
        self.height = (n - 1).bit_length()
        leaf = {x: i for i, x in enumerate(self.order)}
        projected = [set() for _ in range(self.height + 1)]
        refinements = [{} for _ in range(self.height)]
        self.base = {}
        for source, node in self.variables.items():
            patterns = [tuple(sorted({leaf[x] >> (self.height - level)
                                      for x in source}))
                        for level in range(self.height + 1)]
            for level, pattern in enumerate(patterns):
                projected[level].add(pattern)
                if level < self.height:
                    refinements[level].setdefault(pattern, set()).add(patterns[level + 1])
            self.base[patterns[-1]] = (sum(1 << x for x in source), node)
        self.refinements = [{w: sorted(zs) for w, zs in level.items()}
                            for level in refinements]
        self.spans = []
        for level, patterns in enumerate(projected):
            self.spans.append({w: sum(1 << x for x in range(n)
                                     if leaf[x] >> (self.height - level) in w)
                               for w in patterns})

        @lru_cache(None)
        def nucleate(level, pattern, active):
            active &= self.spans[level][pattern]
            if level == self.height:
                source_mask, node = self.base[pattern]
                return node if (active & source_mask).bit_count() == intersection else 0
            children = [nucleate(level + 1, z, active & self.spans[level + 1][z])
                        for z in self.refinements[level][pattern]]
            return self.total([x for x in children if x])

        self.outputs = {target: nucleate(0, (0,), sum(1 << x for x in target))
                        for target in combinations(range(n), q)}
        self.state_count = nucleate.cache_info().currsize
        self.active = set()
        todo = list(self.outputs.values())
        while todo:
            node = todo.pop()
            if not node or node in self.active:
                continue
            self.active.add(node)
            if self.args[node]:
                todo.extend(self.args[node])
        self.additions = sum(self.args[node] is not None for node in self.active)

    def add(self, a, b):
        if not a:
            return b
        if not b:
            return a
        assert not self.support[a] & self.support[b], 'Source regions must be disjoint'
        support = self.support[a] | self.support[b]
        if support in self.lookup:
            return self.lookup[support]
        node = len(self.support)
        self.support.append(support)
        self.args.append((a, b))
        self.lookup[support] = node
        return node

    def total(self, nodes):
        if not nodes:
            return 0
        if len(nodes) == 1:
            return nodes[0]
        middle = len(nodes) // 2
        return self.add(self.total(nodes[:middle]), self.total(nodes[middle:]))

    def verify(self):
        digest = sha256()
        for node in sorted(self.active):
            args = self.args[node]
            if args:
                a, b = args
                assert a < node and b < node
                assert not self.support[a] & self.support[b]
                assert self.support[node] == self.support[a] | self.support[b]
            digest.update(json.dumps((node, args), separators=(',', ':')).encode() + b'\n')
        for target, node in self.outputs.items():
            target_set = set(target)
            expected = sum(1 << i for i, source in enumerate(self.inputs)
                           if len(target_set.intersection(source)) == self.intersection)
            assert self.support[node] == expected, target
            digest.update(json.dumps((target, node), separators=(',', ':')).encode() + b'\n')
        return dict(n=self.n, p=self.p, q=self.q, intersection=self.intersection,
                    inputs=len(self.inputs), outputs=len(self.outputs),
                    additions=self.additions, roles=self.additions + len(self.outputs),
                    nonzero_coefficients=sum(self.support[node].bit_count()
                                             for node in self.outputs.values()),
                    states=self.state_count, created_nodes=len(self.args) - 1,
                    all_output_supports_exact=True, all_additions_disjoint=True,
                    circuit_sha256=digest.hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', type=int, nargs='+', default=[7, 15, 25, 49])
    parser.add_argument('--p', type=int, default=2)
    parser.add_argument('--q', type=int, default=2)
    parser.add_argument('--intersection', type=int, default=0)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    reference = None
    if args.reference is not None:
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(args.reference / 'scripts'))
        from paired_exclusion_circuit import PairedExclusionCircuit
        reference = PairedExclusionCircuit
    results = []
    for n in args.sizes:
        started = time.monotonic()
        c = TreeProjectionCircuit(n, args.p, args.q, args.intersection)
        item = c.verify()
        item['wall_seconds'] = time.monotonic() - started
        if reference and (args.p, args.q, args.intersection) == (2, 2, 0):
            baseline = reference(n)
            item['paired_additions'] = baseline.additions
            item['paired_roles'] = baseline.additions + len(baseline.outputs)
        results.append(item)
        print(json.dumps(item, sort_keys=True), flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
