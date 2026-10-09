#!/usr/bin/env python3
"""Exact low-sector decoder rank and a simultaneous exclusive-pivot boundary.

The rank bound constrains one common-zero commuting target-cut packet.
It is not a bound on temporal reuse, arbitrary target-bank operations or
source/dirty helper stock. No actual-row-only inverse is inferred at j0/j1.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

import paired_cap_dirty_completion as algebra


def retained_rows(rows):
    echelon, selected = [], []
    for index, original in enumerate(rows):
        value = list(original)
        for pivot, row in echelon:
            c = value[pivot]
            value = [a - c * b for a, b in zip(value, row)]
        pivot = next((i for i, v in enumerate(value) if v), None)
        if pivot is not None:
            c = value[pivot]
            echelon.append((pivot, [v / c for v in value]))
            selected.append(index)
    return selected


def walsh(values):
    values = list(values)
    step = 1
    while step < len(values):
        for first in range(0, len(values), 2 * step):
            for offset in range(step):
                i, j = first + offset, first + offset + step
                x, y = values[i], values[j]
                values[i], values[j] = x + y, x - y
        step *= 2
    return values


def require_low(values):
    transformed = walsh(values)
    if any(v for char, v in enumerate(transformed) if char.bit_count() > 2):
        raise AssertionError('A target decoder column contains a high-sector character')
    return {char.bit_count() for char, value in enumerate(transformed) if value}


def parity_decoders(j):
    n = 1 << j
    matrix = [[-algebra.central(j - (u ^ t).bit_count()) for u in range(n)]
              for t in range(n)]
    columns = []
    for p in range(2):
        indices = [t for t in range(n) if t.bit_count() % 2 == p]
        if not indices:
            continue
        selected = [indices[i] for i in retained_rows([matrix[t] for t in indices])]
        roots = [matrix[t] for t in selected]
        decoder = {t: algebra.solve_decoder(roots, matrix[t]) for t in indices}
        for r in range(len(roots)):
            column = [decoder[t][r] if t in decoder else Q(0) for t in range(n)]
            if any(v.denominator != 1 for v in column):
                raise AssertionError('A k5 actual-row target decoder has a noninteger coefficient')
            columns.append(column)
    return columns


def probe(p):
    minimum_j = max(0, 10 - p)
    all_columns, degree_set, per_j = [], set(), []
    incidences = 0
    for j in range(minimum_j, 5):
        decoders = parity_decoders(j)
        for J in combinations(range(5), j):
            for column in decoders:
                full = [column[sum(((selector >> pair) & 1) << i for i, pair in enumerate(J))]
                        for selector in range(32)]
                degree_set |= require_low(full)
                all_columns.append(full)
        source_cube_multiplicity = comb(p - 5, 5 - j)
        count = comb(5, j) * len(decoders)
        incidences += count * source_cube_multiplicity
        per_j.append({'j': j, 'J_subsets': comb(5, j),
                      'decoder_channels_per_J': len(decoders),
                      'other_source_cube_choices_per_J': source_cube_multiplicity,
                      'unique_J_decoder_patterns': count,
                      'actual_channel_target_cube_incidences': count * source_cube_multiplicity})
    rank = len(retained_rows(all_columns))
    expected = 10 if p == 6 else 15 if p == 7 else 16
    if rank != expected or rank != sum(comb(5, a) for a in degree_set):
        raise AssertionError('Exact decoder rank does not fill the predicted low sector')
    high = [Q((-1) ** ((selector & 7).bit_count())) for selector in range(32)]
    try:
        require_low(high)
    except AssertionError:
        negative = True
    else:
        raise AssertionError('A corrupted degree-three decoder column was accepted')
    # A cross-pivot-zero packet yields a nonzero diagonal minor, so its
    # cardinality cannot exceed this exact rank. Duplicate columns cannot
    # claim separate simultaneous pivots regardless of the source role IDs.
    sample = all_columns[0]
    pivot = next(t for t, value in enumerate(sample) if value)
    if not sample[pivot]:
        raise AssertionError('The duplicate-channel obstruction has no diagonal witness')
    return {'pair_count': p, 'available_j': list(range(minimum_j, 5)),
            'per_overlap_block': per_j,
            'unique_J_decoder_patterns': len(all_columns),
            'actual_channel_target_cube_incidences': incidences,
            'exact_per_target_cube_decoder_rank': rank,
            'nonzero_character_degrees': sorted(degree_set),
            'simultaneous_exclusive_pivot_upper_bound_per_target_cube': rank,
            'global_target_cube_count': comb(p, 5),
            'original_target_banks': 32 * comb(p, 5),
            'global_same_cut_rank_upper_bound': rank * comb(p, 5),
            'degree_three_corruption_rejected': negative,
            'duplicate_column_cross_pivot_nonzero_witness': {'target_selector': pivot, 'coefficient': str(sample[pivot])},
            'no_nonunit_actual_row_inverse_inferred': True,
            'maximum_pivot_packet_constructed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    paths = [Path(__file__).resolve(), Path(algebra.__file__).resolve()]
    frozen = {p: p.read_bytes() for p in paths}
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    rows = [probe(p) for p in (6, 7, 8, 9, 12)]
    if any(p.read_bytes() != value for p, value in frozen.items()):
        raise AssertionError('Effective source closure changed')
    result = {'status': 'PASS exact target-sector ranks and scoped common-cut pivot bound',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer,
              'source_sha256': {p.name: sha256(b).hexdigest() for p, b in frozen.items()},
              'cases': rows,
              'scope': 'Exact decoder-column ranks and a diagonal-minor upper bound for one common-zero exclusive-pivot cut. No optimum matching, temporal reuse, source bank compression, native compiler or exponent.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'ranks': [row['exact_per_target_cube_decoder_rank'] for row in rows],
                      'incidences': [row['actual_channel_target_cube_incidences'] for row in rows]}), flush=True)


if __name__ == '__main__':
    main()
