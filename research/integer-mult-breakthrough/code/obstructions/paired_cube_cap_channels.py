#!/usr/bin/env python3
"""Exact cap-compatible row bases for cross-cube majority side blocks.

The output counts algebraic channels, not physical roles or scalar gates.
Every selected row keeps its literal source support and target-cap flag.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb, factorial, prod
from pathlib import Path
import time

import odd_cube_clifford_boundary as O


def central(k, overlap):
    r = (k - 1) // 2
    return Q(prod(overlap - (2 * i + 1) for i in range(r)),
             (1 << r) * factorial(r))


def binary_rank(values):
    pivots = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def echelon(rows):
    """Retain actual independent rows and their exact normalized provenance."""
    basis, selected = [], []
    for index, original in rows:
        value = list(original)
        coefficients = {index: Q(1)}
        for pivot, row, provenance in basis:
            factor = value[pivot]
            if factor:
                value = [a - factor * b for a, b in zip(value, row)]
                for key, coefficient in provenance.items():
                    coefficients[key] = coefficients.get(key, Q(0)) - factor * coefficient
        pivot = next((i for i, v in enumerate(value) if v), None)
        if pivot is not None:
            scale = value[pivot]
            basis.append((pivot, [v / scale for v in value],
                          {key: v / scale for key, v in coefficients.items() if v}))
            selected.append(index)
    return basis, selected


def reconstruct(original, basis, rows):
    remaining = list(original)
    weights = {}
    for pivot, row, provenance in basis:
        factor = remaining[pivot]
        if factor:
            remaining = [a - factor * b for a, b in zip(remaining, row)]
            for index, coefficient in provenance.items():
                weights[index] = weights.get(index, Q(0)) + factor * coefficient
    if any(remaining):
        raise AssertionError('An actual target row is outside its retained parity basis')
    decoded = [sum(coefficient * rows[index][j] for index, coefficient in weights.items())
               for j in range(len(original))]
    if decoded != original:
        raise AssertionError('Exact selected-row reconstruction changed a coefficient')
    return {index: v for index, v in weights.items() if v}


def source_label(k, selector):
    return sum(1 << (2 * i + ((selector >> i) & 1)) for i in range(k))


def target_label(k, j, selector):
    return (sum(1 << (2 * i + ((selector >> i) & 1)) for i in range(j))
            + sum(1 << (2 * k + 2 * i) for i in range(k - j)))


def probe(k):
    if k < 3 or not k & 1:
        raise ValueError('Require an odd cube dimension at least three')
    r, denominator = (k - 1) // 2, 1 << (k - 1)
    for overlap in range(k + 1):
        direct = Q(O.low_walsh_sum(k, r, k - overlap), denominator)
        if central(k, overlap) != direct:
            raise AssertionError('The odd-root polynomial differs from the full cube projector')
    labels = [source_label(k, u) for u in range(1 << k)]
    global_rows, summaries = [], []
    global_character_weights = set()
    selected_total = raw_total = coefficient_entries = 0
    max_decoder_denominator = 1
    for j in range(k):
        size = 1 << j
        rows = [[central(k, j - (u ^ t).bit_count()) for u in range(size)]
                for t in range(size)]
        spectrum = O.walsh(rows[0])
        nonzero_weights = {a.bit_count() for a, value in enumerate(spectrum) if value}
        if any(weight > r for weight in nonzero_weights):
            raise AssertionError('A side row contains a high-degree selector character')
        global_character_weights.update(nonzero_weights)
        global_rows.extend([[row[u & (size - 1)] for u in range(1 << k)] for row in rows])
        parity_bases, selected = {}, []
        for parity in range(2):
            candidates = [(t, rows[t]) for t in range(size) if t.bit_count() % 2 == parity]
            basis, indices = echelon(candidates)
            parity_bases[parity] = (basis, indices)
            selected.extend(indices)
        support_frames = {}
        for t, row in enumerate(rows):
            basis, indices = parity_bases[t.bit_count() % 2]
            decoder = reconstruct(row, basis, rows)
            max_decoder_denominator = max(max_decoder_denominator,
                                          *(c.denominator for c in decoder.values()))
            target = target_label(k, j, t)
            support = [label for u, label in enumerate(labels) if row[u & (size - 1)]]
            if any((label & target).bit_count() & 1 for label in support):
                raise AssertionError('A nonzero literal source lies outside the target cap')
            rank = binary_rank(support)
            if rank != (k + 1 if j == 0 else k):
                raise AssertionError('Complete literal source-support frame rank changed')
            support_frames[t.bit_count() % 2] = rank
            # A selected row may only be used at a target with the same cap flag.
            for index in decoder:
                if index.bit_count() % 2 != t.bit_count() % 2:
                    raise AssertionError('The decoder silently crossed an incompatible parity cap')
            coefficient_entries += size
        # Complete binary source labels justify the physical cap, not its rank alone.
        if j:
            bad = next(label for label in labels if (label & target_label(k, j, 0)).bit_count() & 1)
            if binary_rank(labels) != k + 1 or not bad:
                raise AssertionError('The full-cube cap violation control is absent')
        rank = len(selected)
        full_basis, unused = echelon(list(enumerate(rows)))
        if rank != len(full_basis):
            raise AssertionError('Separate cap bases lost or duplicated algebraic rank')
        multiplicity = comb(k, j)
        raw_total += multiplicity * size
        selected_total += multiplicity * rank
        summaries.append({'overlap_pairs': j, 'equivalent_J_subsets': multiplicity,
                          'raw_target_patterns': size, 'exact_row_rank': rank,
                          'parity_row_ranks': [len(parity_bases[p][1]) for p in range(2)],
                          'nonzero_Walsh_character_weights': sorted(nonzero_weights),
                          'selected_actual_patterns': sorted(selected),
                          'complete_support_frame_ranks': support_frames})
    global_basis, unused = echelon(list(enumerate(global_rows)))
    if len(global_basis) > 1 << (k - 1):
        raise AssertionError('The side channels exceed the low-Walsh dimension')
    # Translating all target patterns spans every nonzero Fourier character.
    # Permuting J over all j-subsets then spans every mask of each such weight.
    joint_rank = sum(comb(k, weight) for weight in global_character_weights)
    if joint_rank != 1 << (k - 1):
        raise AssertionError('All cap blocks must jointly retain the complete low-degree sector')
    return {'cube_dimension': k, 'source_banks_per_cube': 1 << k,
            'overlap_blocks': summaries, 'raw_channels_per_cube': raw_total,
            'independent_cap_channels_per_cube': selected_total,
            'global_low_channel_rank_for_retained_J_representatives': len(global_basis),
            'exact_joint_rank_after_all_J_permutations': joint_rank,
            'selected_channel_ratio': str(Q(selected_total, 1 << k)),
            'complete_reconstructed_matrix_entries': coefficient_entries,
            'maximum_reconstruction_coefficient_denominator': max_decoder_denominator,
            'full_cube_frame_rank': k + 1,
            'full_cube_frame_target_cap_violation_rejected': True,
            'physical_channel_stock_or_word_certified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker required')
    dimensions = [3, 5] if args.bounded else [3, 5, 7]
    paths = [Path(__file__).resolve(), Path(O.__file__).resolve()]
    hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    if args.workers == 1:
        rows = list(map(probe, dimensions))
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(dimensions))) as pool:
            rows = list(pool.map(probe, dimensions))
    if hashes != {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}:
        raise AssertionError('Effective source closure changed')
    result = {'status': 'PASS EXACT CAP-COMPATIBLE CHANNEL BASES',
              'started_utc': start, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'elapsed_seconds': time.perf_counter() - timer,
              'workers_requested': args.workers, 'bounded': args.bounded,
              'source_closure': hashes, 'cases': rows,
              'scope': 'Algebraic actual-row bases and literal binary target caps only; no physical word, native cost or exponent'}
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'certificate.json').write_text(encoded, encoding='utf-8')
    print(encoded, end='')


if __name__ == '__main__':
    main()
