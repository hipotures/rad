#!/usr/bin/env python3
"""Exact block-contraction alternatives for the complex D/E side circuit.

The immutable binary-frame checker and bank-matching certificate are reused.
Only the disjoint-sum contraction blocks and sum association are changed.
Larger blocks require components containing several surviving vertices in
one touched block; omitting those components gives an incorrect map.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import time
from unittest.mock import patch

import downstream_complex_certificate as certificate
from downstream_complex_circuit import TripleSideCircuit, scalar_checks
from downstream_gaussian import check_sources, require
from downstream_parameter_optimum import as_strings


class BlockSideCircuit(TripleSideCircuit):
    """Weighted deletion contraction with explicit surviving-block subsets."""

    def __init__(self, h, block=2, association='balanced', seed=109, base=4):
        require(block >= 2 and base >= 3, 'Invalid contraction configuration')
        self.block = block
        self.association = association
        self.seed = seed
        self.base = base
        self.rng = random.Random(seed)
        super().__init__(h)

    def total(self, values):
        values = [x for x in values if x]
        if self.association == 'size':
            values.sort(key=lambda x: (self.support[x].bit_count(), self.support[x]))
        elif self.association == 'size-desc':
            values.sort(key=lambda x: (-self.support[x].bit_count(), self.support[x]))
        elif self.association == 'lex':
            values.sort(key=lambda x: self.support[x])
        elif self.association == 'shuffle':
            self.rng.shuffle(values)
        else:
            require(self.association == 'balanced', 'Unknown sum association')

        def combine(items):
            if not items:
                return 0
            if len(items) == 1:
                return items[0]
            middle = len(items)//2
            return self.add(combine(items[:middle]), combine(items[middle:]))

        return combine(values)

    def hyper(self, points, terms, k, queries=None):
        # Edge degree and query size separate for blocks larger than two:
        # selecting two survivors in one block lowers degree by two, but
        # removes only one block from the outside deletion query.
        queries = k if queries is None else queries
        # Preserve the exact original node identities in the baseline control.
        if self.block == 2 and self.base == 4 and queries == k:
            return super().hyper(points, terms, k)
        if queries == 0:
            return {(): self.total(list(terms.values()))}
        if k == 0:
            value = self.total(list(terms.values()))
            return {omit: value for size in range(queries+1) for omit in combinations(points, size)}
        if k == queries == 1:
            values = [terms.get((i,), 0) for i in points] + [terms.get((), 0)]
            total, one = self.vector(values)
            return {(): total, **{(i,): value for i, value in zip(points, one)}}
        if len(points) <= self.base:
            return {omit: self.total([value for edge, value in terms.items()
                                     if not set(edge) & set(omit)])
                    for size in range(queries+1) for omit in combinations(points, size)}

        groups = [points[i:i+self.block] for i in range(0, len(points), self.block)]
        require(len(groups) < len(points), 'Contraction did not shrink the ground')
        group_of = {v: i for i, group in enumerate(groups) for v in group}
        coarse_lists = defaultdict(list)
        components = defaultdict(lambda: defaultdict(list))
        for edge, value in terms.items():
            coarse_lists[tuple(sorted({group_of[v] for v in edge}))].append(value)
            for size in range(1, len(edge)+1):
                for selected in combinations(edge, size):
                    touched = {group_of[v] for v in selected}
                    if len(touched) > queries:
                        continue
                    rest = [v for v in edge if v not in selected]
                    if any(group_of[v] in touched for v in rest):
                        continue
                    # A touched output block omits at least one vertex. A
                    # selected subset equal to an entire block is never used.
                    if any(all(v in selected for v in groups[g]) for g in touched):
                        continue
                    outside = tuple(sorted({group_of[v] for v in rest}))
                    components[selected][outside].append(value)

        coarse = {edge: self.total(values) for edge, values in coarse_lists.items()}
        coarse_answers = self.hyper(list(range(len(groups))), coarse, k, queries)
        component_answers = {}
        for selected, pieces in components.items():
            touched = {group_of[v] for v in selected}
            other = [g for g in range(len(groups)) if g not in touched]
            induced = {edge: self.total(values) for edge, values in pieces.items()}
            component_answers[selected] = self.hyper(other, induced, k-len(selected), queries-len(touched))

        answers = {}
        for size in range(queries+1):
            for omit in combinations(points, size):
                touched = {group_of[v] for v in omit}
                survivors = sorted(v for g in touched for v in groups[g] if v not in omit)
                values = [coarse_answers[tuple(sorted(touched))]]
                for count in range(1, min(k, len(survivors))+1):
                    for selected in combinations(survivors, count):
                        table = component_answers.get(selected)
                        if table is not None:
                            outside = tuple(sorted(touched-{group_of[v] for v in selected}))
                            values.append(table[outside])
                answers[omit] = self.total(values)
        return answers


def physical_map(circuit, code):
    """Reconstruct every physical union and fresh copy using exact bitsets."""
    values = [0]*code['roles']
    additions = copies = 0
    for node, inputs, outputs in code['gates']:
        if circuit.args[node] is None:
            require(len(inputs) == 1 and values[inputs[0]] == 0, 'Source role is not fresh')
            values[inputs[0]] = circuit.support[node]
        else:
            require(len(inputs) == 2, 'Addition arity changed')
            a, b = circuit.args[node]
            require(values[inputs[0]] == circuit.support[a]
                    and values[inputs[1]] == circuit.support[b], 'Physical input coefficient mismatch')
            require(not values[inputs[0]] & values[inputs[1]], 'Physical formal summands overlap')
            values[inputs[0]] |= values[inputs[1]]
            additions += 1
        require(values[inputs[0]] == circuit.support[node], 'Physical pivot coefficient mismatch')
        for slot in outputs[1:]:
            require(values[slot] == 0, 'Physical copy destination is not fresh')
            values[slot] = values[inputs[0]]
            copies += 1
    for target, slot in code['outputs'].items():
        require(values[slot] == circuit.support[circuit.outputs[target]], 'Physical output map mismatch')
    return dict(all_physical_coefficients_exact=True, physical_additions=additions,
                physical_copies=copies, designated_outputs=len(code['outputs']))


def evaluate(h, block, association, seed, base, dirty=False, exchange=False):
    start = time.monotonic()
    configured = lambda ground: BlockSideCircuit(ground, block, association, seed, base)
    with patch.object(certificate, 'TripleSideCircuit', configured):
        result = certificate.case(h, [5] if exchange else [])
    circuit = configured(h)
    code = circuit.compile()
    result['physical'] = physical_map(circuit, code)
    if dirty:
        result['dirty'] = scalar_checks(circuit, code, all_basis=(h == 8))
    result['configuration'] = dict(h=h, block=block, association=association, seed=seed, base=base)
    result['elapsed_seconds_with_physical'] = time.monotonic()-start
    result['scientific_scope'] = ('Exact disjoint scalar DAG, physical coefficient replay, unchanged binary '
        'frame residuals, terminal complements, full-bank matching and guard counts. '
        'Dirty and three-stage controls are explicit when requested; compact analytic transfer is separate.')
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream', type=Path, required=True)
    ap.add_argument('--h', type=int, nargs='+', required=True)
    ap.add_argument('--blocks', type=int, nargs='+', default=[2, 3, 4])
    ap.add_argument('--associations', nargs='+', default=['balanced'])
    ap.add_argument('--seed', type=int, default=109)
    ap.add_argument('--base', type=int, default=4)
    ap.add_argument('--dirty', action='store_true')
    ap.add_argument('--exchange-h8', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    names = [Path(__file__).name, 'downstream_complex_certificate.py', 'downstream_complex_circuit.py',
             'downstream_gaussian.py', 'downstream_parameter_optimum.py']
    result = dict(campaign_id='20261007T222521Z', started_utc=datetime.now(timezone.utc).isoformat(),
        campaign_deadline='2026-10-08T08:25:21Z', provenance=check_sources(args.upstream),
        source_sha256={name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
        settings={k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}, rows=[])
    start = time.monotonic()
    for h in args.h:
        for block in args.blocks:
            for association in args.associations:
                row = evaluate(h, block, association, args.seed, args.base, args.dirty,
                               exchange=args.exchange_h8 and h == 8)
                result['rows'].append(row)
                result['elapsed_seconds'] = time.monotonic()-start
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True)+'\n')
                print(json.dumps(dict(h=h, block=block, association=association,
                    roles=row['logical']['baseline_physical_roles'], status='PASS',
                    seconds=row['elapsed_seconds_with_physical'])), flush=True)
    result['status'] = 'Terminal PASS'
    result['completed_utc'] = datetime.now(timezone.utc).isoformat()
    args.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
