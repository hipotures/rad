#!/usr/bin/env python3
"""Monotone whole intersection-one sums through paired block contraction.

This is a scalar/role proxy until nondegenerate nested rational frames are
constructed. It differs from the earlier full-pair-only aggregation and
from the cancellation-based incidence formula. Every formal coefficient,
physical addition/copy and small dirty scalar shear is checked exactly.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

from finite_complex_blocks import BlockSideCircuit, physical_map
from downstream_complex_circuit import masks
from downstream_gaussian import require


class IntersectionCircuit(BlockSideCircuit):
    def __init__(self, h):
        require(h >= 6 and h % 2 == 0, 'Use an even ground')
        self.h, self.block, self.base, self.association = h, 2, 4, 'balanced'
        self.inputs = list(combinations(range(h), 3))
        self.variables = {t: i+1 for i, t in enumerate(self.inputs)}
        self.support = [0]+[1 << i for i in range(len(self.inputs))]
        self.args = [None]*len(self.support)
        self.union = [0]+[masks(t) for t in self.inputs]
        self.core = list(self.union)
        self.family = ['zero']+['input']*len(self.inputs)
        self.lookup = {(None, support): i for i, support in enumerate(self.support)}
        self.namespace = 'B'
        self.special = {}
        groups = [list(range(i, i+2)) for i in range(0, h, 2)]
        group_of = {vertex: group for group, points in enumerate(groups) for vertex in points}
        components = defaultdict(lambda: defaultdict(list))
        for triple in self.inputs:
            for size in range(1, 4):
                for selected in combinations(triple, size):
                    touched = {group_of[v] for v in selected}
                    rest = [v for v in triple if v not in selected]
                    if any(group_of[v] in touched for v in rest):
                        continue
                    outside = tuple(sorted({group_of[v] for v in rest}))
                    components[selected][outside].append(self.variables[triple])
        answers = {}
        for selected, pieces in components.items():
            selected_groups = {group_of[v] for v in selected}
            other = [g for g in range(len(groups)) if g not in selected_groups]
            induced = {edge: self.total(values) for edge, values in pieces.items()}
            answers[selected] = self.hyper(other, induced, 3-len(selected), 3-len(selected_groups))
        self.outputs = {}
        for target in self.inputs:
            touched = {group_of[v] for v in target}
            nearby = sorted(v for g in touched for v in groups[g])
            values = []
            for size in range(1, 4):
                for selected in combinations(nearby, size):
                    if len(set(selected) & set(target)) != 1:
                        continue
                    table = answers.get(selected)
                    if table is None:
                        continue
                    outside = tuple(sorted(touched-{group_of[v] for v in selected}))
                    values.append(table[outside])
            self.outputs['B', target] = self.total(values)
        self.active = set()
        stack = list(self.outputs.values())
        while stack:
            node = stack.pop()
            if not node or node in self.active:
                continue
            self.active.add(node)
            if self.args[node]:
                stack.extend(self.args[node])
        self.additions = sum(self.args[node] is not None for node in self.active)

    def verify(self):
        stripe = [0]*self.h
        for i, triple in enumerate(self.inputs):
            for vertex in triple:
                stripe[vertex] |= 1 << i
        digest = sha256()
        for node in sorted(self.active):
            if self.args[node]:
                a, b = self.args[node]
                require(a < node and b < node and not self.support[a] & self.support[b], 'Formal disjoint DAG failed')
                require(self.support[node] == self.support[a] | self.support[b], 'Formal coefficient union failed')
            digest.update(f'{node}:{self.args[node]}\n'.encode())
        for (_, target), node in sorted(self.outputs.items()):
            a, b, c = target
            expected = ((stripe[a] & ~stripe[b] & ~stripe[c]) |
                        (stripe[b] & ~stripe[a] & ~stripe[c]) |
                        (stripe[c] & ~stripe[a] & ~stripe[b]))
            require(self.support[node] == expected, 'Whole intersection-one map failed')
            require(expected.bit_count() == 3*comb(self.h-3, 2), 'Intersection-one support count failed')
            digest.update(f'{target}:{node}\n'.encode())
        target_core = {node: (1 << self.h)-1 for node in self.active}
        for (_, target), node in self.outputs.items():
            target_core[node] &= masks(target)
        for node in sorted(self.active, reverse=True):
            if self.args[node]:
                for child in self.args[node]:
                    target_core[child] &= target_core[node]
        zero_core = [node for node in self.active if not self.core[node]]
        return dict(inputs=len(self.inputs), outputs=len(self.outputs), additions=self.additions,
                    unframed_physical_roles=self.additions+len(self.outputs),
                    all_additions_disjoint=True, all_whole_coefficients_exact=True,
                    nonzero_side_coefficients=len(self.inputs)*3*comb(self.h-3, 2),
                    core_zero_nodes=len(zero_core),
                    core_zero_nodes_without_shared_physical_target=sum(not target_core[n] for n in zero_core),
                    circuit_sha256=digest.hexdigest())


def dirty_checks(circuit, code):
    h, v, roles = circuit.h, len(circuit.inputs), code['roles']
    from downstream_complex_circuit import mixer

    def invoke(x, y, scratch, center):
        def inject():
            for i, target in enumerate(circuit.inputs):
                y[i] ^= scratch[code['outputs']['B', target]]

        def scatter():
            for i, target in enumerate(circuit.inputs):
                for vertex in target:
                    y[i] ^= center[vertex]

        def copy():
            for i, target in enumerate(circuit.inputs):
                scratch[code['sources'][target]] ^= x[i]

        def gather():
            for i, target in enumerate(circuit.inputs):
                for vertex in target:
                    center[vertex] ^= x[i]

        def mix(inverse=False):
            gates = reversed(code['gates']) if inverse else code['gates']
            for _, inputs, outputs in gates:
                if inverse:
                    for slot in outputs[1:]:
                        scratch[slot] ^= scratch[inputs[0]]
                    for slot in inputs[1:]:
                        scratch[inputs[0]] ^= scratch[slot]
                else:
                    for slot in inputs[1:]:
                        scratch[inputs[0]] ^= scratch[slot]
                    for slot in outputs[1:]:
                        scratch[slot] ^= scratch[inputs[0]]

        mix(); inject(); mix(True); scatter(); copy(); gather(); scatter()
        mix(); inject(); mix(True); gather(); copy()

    for coordinate in range(v+roles+h):
        x, y, scratch, center = [0]*v, [0]*v, [0]*roles, [0]*h
        if coordinate < v:
            x[coordinate] = 1
        elif coordinate < v+roles:
            scratch[coordinate-v] = 1
        else:
            center[coordinate-v-roles] = 1
        before = scratch[:], center[:]
        invoke(x, y, scratch, center)
        require(y == x and (scratch, center) == before, 'Complete dirty scalar basis failed')
    return dict(exact_dirty_basis_vectors=v+roles+h, scalar_identity_and_dirty_restoration=True,
                scope='Binary scalar shear only; rational nondegenerate-frame transfer not established')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h', type=int, nargs='+', default=[8, 12])
    ap.add_argument('--dirty-h8', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    start = time.monotonic(); result = dict(campaign_id='20261007T222521Z',
        started_utc=datetime.now(timezone.utc).isoformat(), source_sha256={name:
            sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in [Path(__file__).name, 'finite_complex_blocks.py', 'downstream_complex_circuit.py']}, rows=[])
    for h in args.h:
        at = time.monotonic(); circuit = IntersectionCircuit(h); logical = circuit.verify(); code = circuit.compile()
        row = dict(h=h, logical=logical, physical=physical_map(circuit, code),
            scope='Exploratory monotone whole-map and physical-role proxy; no nested rational-frame witness or transferred bound')
        if args.dirty_h8 and h == 8:
            row['dirty'] = dirty_checks(circuit, code)
        row['elapsed_seconds'] = time.monotonic()-at; result['rows'].append(row)
        result['elapsed_seconds'] = time.monotonic()-start
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        print(json.dumps(dict(h=h, roles=code['roles'], core_zero_nodes=logical['core_zero_nodes'], seconds=row['elapsed_seconds'])), flush=True)
    result['status'] = 'Terminal PASS scalar/physical proxy only'
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
