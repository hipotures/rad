#!/usr/bin/env python3
"""Exact one-child screen for right-conditioned Gaussian-dyadic frames.

Every nonzero wrapper must be a unit of Z[i,1/2], namely i^s(1+i)^e.
The retained normal form charges row and column scalings explicitly. It
does not supply a fixed-tape router, a physical scalar word or an exponent.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from time import perf_counter

from lagrangian_phase_screen import basis, distance, graph_frames
from nonlinear_common_frame_screen import (N, SIZE, I, add, mul, normalize,
    compose, inverse, graph_operator, clifford_representatives, unit)


def gaussian_unit(value, denominator):
    """Return (valuation at 1+i, fourth-root exponent), or reject."""
    a, b = value
    norm = a*a+b*b
    if not norm or norm & (norm-1):
        return None
    power = norm.bit_length()-1
    for _ in range(power):
        if (a+b) & 1 or (b-a) & 1:
            return None
        a, b = (a+b)//2, (b-a)//2
    roots = ((1, 0), (0, 1), (-1, 0), (0, -1))
    if (a, b) not in roots:
        return None
    # 2^(-d) = i^d (1+i)^(-2d).
    return power-2*denominator, (roots.index((a, b))+denominator) % 4


def unit_value(exponent, phase):
    value = (1, 0)
    for _ in range(abs(exponent)):
        value = mul(value, (1, 1) if exponent >= 0 else (1, -1))
    return unit(value, phase), max(0, -exponent)


def diagonal(weights):
    values = [unit_value(*weight) for weight in weights]
    denominator = max(d for _, d in values)
    rows = [[(0, 0)]*SIZE for _ in range(SIZE)]
    for j, (value, d) in enumerate(values):
        rows[j][j] = tuple(x << (denominator-d) for x in value)
    return normalize(rows, denominator)


def ratio_unit(value, reference, value_denominator, reference_denominator):
    left = gaussian_unit(value, value_denominator)
    right = gaussian_unit(reference, reference_denominator)
    if left is None or right is None:
        return None
    return left[0]-right[0], (left[1]-right[1]) % 4


def reconstruct(normal_form):
    entries = []
    for block in normal_form['blocks']:
        rank = block['rank']
        for a, b in product(range(1 << rank), repeat=2):
            # C^r[a,b] = (1+i)^r i^(-popcount(a xor b))/2^r.
            exponent = -rank
            phase = rank-(a ^ b).bit_count()
            for weight in (block['output_scales'][a], block['input_scales'][b]):
                exponent += weight[0]
                phase += weight[1]
            value, denominator = unit_value(exponent, phase % 4)
            entries.append((block['output_addresses'][a], block['input_addresses'][b],
                            value, denominator))
    denominator = max(d for _, _, _, d in entries)
    rows = [[(0, 0)]*SIZE for _ in range(SIZE)]
    for a, b, value, d in entries:
        rows[a][b] = tuple(x << (denominator-d) for x in value)
    return normalize(rows, denominator)


def classify(operator, retain=False):
    """Recognize disjoint Walsh blocks with paid Gaussian-dyadic units."""
    rows, denominator = operator
    supports = [tuple(j for j, value in enumerate(row) if value != (0, 0))
                for row in rows]
    if any(not support for support in supports):
        return None, 'zero-row'
    groups = {support: tuple(i for i, other in enumerate(supports) if other == support)
              for support in set(supports)}
    if any(set(a) & set(b) for a, b in product(groups, repeat=2) if a != b):
        return None, 'overlapping-supports'
    blocks = []
    for columns, row_ids in sorted(groups.items()):
        volume = len(columns)
        if len(row_ids) != volume or volume & (volume-1):
            return None, 'non-dyadic-block-size'
        rank = volume.bit_length()-1
        a0, b0 = row_ids[0], columns[0]
        patterns = {}
        for a in row_ids:
            pattern = 0
            for j, b in enumerate(columns):
                if gaussian_unit(rows[a][b], denominator) is None:
                    return None, 'nonunit-Gaussian-entry'
                num = mul(rows[a][b], rows[a0][b0])
                ref = mul(rows[a][b0], rows[a0][b])
                if num == (-ref[0], -ref[1]):
                    pattern |= 1 << j
                elif num != ref:
                    return None, 'non-real-dephased-block'
            if pattern in patterns:
                return None, 'duplicate-dephased-row'
            patterns[pattern] = a
        row_basis = basis(tuple(patterns))
        if len(row_basis) != rank or len(patterns) != 1 << rank:
            return None, 'non-Walsh-row-group'
        labels = {}
        for x in range(1 << rank):
            pattern = 0
            for j, v in enumerate(row_basis):
                if x >> j & 1:
                    pattern ^= v
            if pattern not in patterns:
                return None, 'non-Walsh-row-group'
            labels[pattern] = x
        inputs = [None]*volume
        outputs = [None]*volume
        qin = [None]*volume
        qout = [None]*volume
        for pattern, a in patterns.items():
            label = labels[pattern]
            outputs[label] = a
            weight = gaussian_unit(rows[a][b0], denominator)
            # Reference C[label,0] has exponent -r and phase r-wt(label).
            qout[label] = (weight[0]+rank,
                          (weight[1]-rank+label.bit_count()) % 4)
        for j, b in enumerate(columns):
            label = sum(((pattern >> j) & 1) << k
                        for k, pattern in enumerate(row_basis))
            if inputs[label] is not None:
                return None, 'bad-Walsh-coordinates'
            inputs[label] = b
            weight = ratio_unit(rows[a0][b], rows[a0][b0], denominator, denominator)
            qin[label] = (weight[0], (weight[1]+label.bit_count()) % 4)
        blocks.append(dict(rank=rank, volume_records=volume,
            input_addresses=inputs, output_addresses=outputs,
            input_scales=qin, output_scales=qout))
    normal_form = dict(blocks=blocks,
        average_rank=str(Q(sum((1 << block['rank'])*block['rank'] for block in blocks), SIZE)),
        maximum_absolute_wrapper_valuation=max(abs(weight[0]) for block in blocks
            for side in ('input_scales', 'output_scales') for weight in block[side]))
    assert reconstruct(normal_form) == operator
    return normal_form if retain else Q(normal_form['average_rank']), 'exact-conditioned-blocks'


def weights_for(family, exponent, phase):
    def predicate(x):
        if family == 'singleton':
            return x == 7
        if family == 'pair-control':
            return x & 3 == 3
        if family == 'parity':
            return x.bit_count() & 1
        if family == 'bit':
            return x & 1
        raise ValueError('Unknown family')
    return [(exponent, phase) if predicate(x) else (0, 0) for x in range(SIZE)]


def screen(family):
    started = perf_counter()
    reps = clifford_representatives()
    graphs = graph_frames(N)
    endpoints = [graph_operator(code) for code in range(64)]
    baseline = [[Q(distance(lag, graph, N)) for graph in graphs] for lag, _, _ in reps]
    # Four nonunitary Gaussian-dyadic units, with literal dyadic inverses.
    parameters = [(1, 0), (-1, 0), (2, 3), (-2, 1)]
    reasons = Counter()
    profiles = Counter()
    dominance = []
    unresolved = []
    digest = sha256()
    complete_candidates = []
    for exponent, phase in parameters:
        weights = weights_for(family, exponent, phase)
        D = diagonal(weights)
        Dinv = diagonal([(-e, (-s) % 4) for e, s in weights])
        assert compose(D, Dinv) == I == compose(Dinv, D)
        for candidate, (lag, F, word) in enumerate(reps):
            Fconditioned = compose(F, D)
            Fconditioned_inverse = compose(Dinv, inverse(F))
            assert compose(Fconditioned, Fconditioned_inverse) == I
            costs = []
            for code, endpoint in enumerate(endpoints):
                edge = compose(Fconditioned, inverse(endpoint))
                cost, reason = classify(edge)
                reasons[reason] += 1
                costs.append(cost)
                if cost is not None:
                    normal_form, _ = classify(edge, True)
                    profile = tuple(sorted((block['rank'], block['volume_records'])
                                           for block in normal_form['blocks']))
                    profiles[profile] += 1
                digest.update(f'{exponent},{phase}:{candidate},{code}:{cost},{reason};'.encode())
            valid = [code for code, cost in enumerate(costs) if cost is not None]
            dominator = next((j for j, old in enumerate(baseline)
                             if all(old[code] <= costs[code] for code in valid)), None)
            item = dict(parent_clifford_candidate=candidate,
                conditioning_exponent=exponent, conditioning_phase=phase,
                admitted_graph_codes=valid, average_ranks=[str(costs[code]) for code in valid])
            if dominator is None:
                unresolved.append(item)
                if len(complete_candidates) < 8:
                    complete_candidates.append(dict(**item, parent_lagrangian=lag,
                        parent_clifford_word=word, literal_conditioning_weights=weights,
                        edges=[classify(compose(Fconditioned, inverse(endpoints[code])), True)[0]
                               for code in valid]))
            else:
                dominance.append(dict(**item, dominating_clifford_candidate=dominator,
                    dominating_ranks=[int(baseline[dominator][code]) for code in valid]))
    return dict(status='EXACT FINITE CONDITIONED-COMMON-FRAME SCREEN', family=family,
        right_conditionings=[dict(exponent=e, phase=s) for e, s in parameters],
        complete_edge_cases=4*135*64, candidate_count=4*135,
        edge_classification=dict(reasons),
        block_profiles=[dict(profile=p, count=n) for p, n in sorted(profiles.items())],
        dominated_candidates=len(dominance), unresolved_candidates=unresolved,
        componentwise_dominance_certificates=dominance,
        unresolved_literal_normal_forms=complete_candidates,
        result_sha256=digest.hexdigest(), elapsed_seconds=perf_counter()-started,
        scope='Exact finite arrays and charged Gaussian-dyadic unit wrappers. Volume-weighted ranks are proxies, not finite tensor moments. Common-frame gates, tensor-column compilation, routing, complete dirty chronology, precision transfer and exponent remain open.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--family', choices=('singleton', 'pair-control', 'parity', 'bit'), required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('Use a fresh attempt path')
    result = screen(a.family)
    result['source_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in
        ('componentwise_dominance_certificates', 'unresolved_literal_normal_forms',
         'unresolved_candidates')}), flush=True)


if __name__ == '__main__':
    main()
