#!/usr/bin/env python3
"""Exact weighted dirty-target absorption of three destination-only cap sinks.

This is a local adaptation of the pinned PR166 compiler lemma. All n4/n8
basis banks and their kernel parking remain. Only three extra destination-only
sink copies disappear. Shared nonpivot targets are permitted because every
pivot is exclusive, all cuts use identical actual frames, and no producer
operation reads a target bank. No complete global native supplier is asserted.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import paired_cap_dirty_completion as component


def add(word, target, source, coefficient):
    if coefficient:
        word.append(('add', target, source, Q(coefficient)))


def block_word(j, variant='new', negative=None, correction=False):
    case = component.probe((j, 0))
    n, N = case['original_complete_banks_retained'], 16
    matrix = [[Q(v) for v in row] for row in case['completion_matrix']]
    forward = component.compile_word(matrix)
    inverse = component.invert_word(forward)
    rows = [[Q(v) for v in row] for row in case['full_target_decoder']]
    outside = 1 << (5 - j)
    decoder = [row for row in rows for unused in range(outside)]
    pivots = [next(t for t, row in enumerate(decoder)
                   if row[r] and all(not row[q] for q in range(3) if q != r))
              for r in range(3)]
    if len(set(pivots)) != 3:
        raise AssertionError('The channel pivots are not independent target coordinates')
    for r, pivot in enumerate(pivots):
        if decoder[pivot][r] not in (Q(1), Q(-1)):
            raise AssertionError('A pivot requires a new nonunit coefficient divisor')
    signal_start, sinks_start = n + N, 2 * n + N
    slots = sinks_start + (3 if variant == 'old' else 0)
    word, cuts = [], []
    # Existing expanded old-response columns are evaluated before the common
    # zero cut. Only deleted independent sink columns are omitted in 'new'.
    word.extend(forward)
    if variant == 'old':
        for r in range(3):
            add(word, sinks_start + r, r, 1)
        for t, row in enumerate(decoder):
            for r, coefficient in enumerate(row):
                add(word, n + t, sinks_start + r, -coefficient)
        for r in range(3):
            add(word, sinks_start + r, r, -1)
    elif negative != 'dropped_ancestor_old_response':
        for t, row in enumerate(decoder):
            for r, coefficient in enumerate(row):
                add(word, n + t, r, -coefficient)
    word.extend(inverse)
    if variant == 'new':
        for r, pivot in enumerate(pivots):
            if negative == 'missing_pre_cut' and r == 0:
                continue
            for t, row in enumerate(decoder):
                if t != pivot:
                    add(word, n + t, n + pivot, -row[r] / decoder[pivot][r])
        cuts.append({'stage': 'pre', 'actual_common_frame': 'F0=identity',
                     'pivot_coordinates': pivots,
                     'shared_destinations_are_nonpivots': True})
    # Optional independent corrections occur while nonpivots are encoded.
    correction_target = next(t for t, row in enumerate(decoder)
                             if t not in pivots and sum(bool(v) for v in row) == 3)
    if correction:
        add(word, n + correction_target, signal_start, Q(3, 4))
    if negative == 'early_pivot_correction':
        add(word, n + pivots[0], signal_start, Q(3, 4))
    for i in range(n):
        add(word, i, signal_start + i, 1)
    # The source/control roles then enter the actual common cap F_U, dimU=5.
    word.extend(forward)
    if variant == 'old':
        for r in range(3):
            add(word, sinks_start + r, r, 1)
        for t, row in enumerate(decoder):
            for r, coefficient in enumerate(row):
                add(word, n + t, sinks_start + r, coefficient)
        # Every independent sink is restored at full before the basis inverse.
        for r in range(3):
            add(word, sinks_start + r, r, -1)
    else:
        for r, pivot in enumerate(pivots):
            add(word, n + pivot, r, decoder[pivot][r])
            if negative == 'missing_post_cut' and r == 0:
                continue
            for t, row in enumerate(decoder):
                if t != pivot:
                    add(word, n + t, n + pivot, row[r] / decoder[pivot][r])
        cuts.append({'stage': 'producer and post', 'actual_common_frame': 'same F_U on all operands',
                     'common_label_dimension': 5,
                     'pivot_unchanged_by_other_channels': True})
    # Inputs are still retained: full-frame literal inverse, then source
    # uninject. The replacement never drops an active or parked basis bank.
    word.extend(inverse)
    for i in range(n):
        add(word, i, signal_start + i, -1)
    return word, {'source_basis_banks': n, 'target_banks': N,
                  'retained_kernel_banks': n - 3, 'read_only_signal_banks': n,
                  'extra_destination_only_sink_banks': 3 if variant == 'old' else 0,
                  'slots': slots, 'pivot_targets': pivots, 'decoder': decoder,
                  'basis_matrix': matrix, 'correction_target': correction_target,
                  'cuts': cuts}


def expected_matrix(meta, correction=False, early=False):
    n, N, total = meta['source_basis_banks'], meta['target_banks'], meta['slots']
    result = component.identity(total)
    signal_map = component.product(meta['decoder'], meta['basis_matrix'][:3])
    for t, row in enumerate(signal_map):
        for s, c in enumerate(row):
            result[n + t][n + N + s] += c
    if correction:
        result[n + meta['correction_target']][n + N] += Q(3, 4)
    if early:
        result[n + meta['pivot_targets'][0]][n + N] += Q(3, 4)
    return result


def exact_payload(word, total):
    values = [[Q((-1) ** (i + a) * (7 * i + 3 * a + 2), 1 << ((i + 2 * a) % 4))
               for a in range(8)] for i in range(total)]
    before = [list(row) for row in values]
    for gate in word:
        component.apply_gate(values, gate)
    for gate in component.invert_word(word):
        component.apply_gate(values, gate)
    if values != before:
        raise AssertionError('Complete new chronological inverse failed on four Gaussian fields')
    return total * 16


def probe(j):
    old, oldmeta = block_word(j, 'old')
    new, meta = block_word(j)
    old_matrix, new_matrix = component.word_matrix(oldmeta['slots'], old), component.word_matrix(meta['slots'], new)
    if old_matrix != expected_matrix(oldmeta) or new_matrix != expected_matrix(meta):
        raise AssertionError('Original or substituted complete scalar word changed an independent input column')
    if [row[:meta['slots']] for row in old_matrix[:meta['slots']]] != new_matrix:
        raise AssertionError('Retained source/dirty/target columns changed after sink deletion')
    if any(old_matrix[t][s] for t in range(meta['slots'])
           for s in range(meta['slots'], oldmeta['slots'])):
        raise AssertionError('Deleted independent sink inputs leaked to retained outputs')
    corrected, cmeta = block_word(j, correction=True)
    if component.word_matrix(cmeta['slots'], corrected) != expected_matrix(cmeta, correction=True):
        raise AssertionError('Intervening independent nonpivot correction was not preserved')
    negatives = {}
    for negative in ['dropped_ancestor_old_response', 'missing_pre_cut',
                     'missing_post_cut', 'early_pivot_correction']:
        word, nmeta = block_word(j, negative=negative)
        reference = expected_matrix(nmeta, early=negative == 'early_pivot_correction')
        if component.word_matrix(nmeta['slots'], word) == reference:
            raise AssertionError('An invalid target cut or old-response column change was accepted')
        negatives[negative] = True
    n, N = meta['source_basis_banks'], meta['target_banks']
    original_roles, new_roles = n + 3 + N, n + N
    h = 2 * (5 + 5 - j)
    # Only declared source/control helpers and targets are included. Signal
    # input/aggregate/native bills are unchanged and remain an external contract.
    old_profile = {5: n + 3 + N, h - 5: n + 3, h - 6: N}
    new_profile = {5: n + N, h - 5: n, h - 6: N}
    old_rank = sum(r * count for r, count in old_profile.items())
    new_rank = sum(r * count for r, count in new_profile.items())
    if old_rank - new_rank != 3 * h or original_roles - new_roles != 3:
        raise AssertionError('Sink absorption omitted a prefix, target entrance or helper endpoint')
    return {'j': j, 'h': h, 'target_parity': 0,
            'complete_old_input_coordinates': oldmeta['slots'],
            'complete_new_input_coordinates': meta['slots'],
            'all_old_matrix_entries_checked': oldmeta['slots'] ** 2,
            'all_new_matrix_entries_checked': meta['slots'] ** 2,
            'all_original_basis_and_kernel_banks_retained': n,
            'retained_kernel_banks': n - 3,
            'removed_destination_only_sink_copies': 3,
            'exclusive_pivot_targets': meta['pivot_targets'],
            'shared_nonpivot_targets': [t for t, row in enumerate(meta['decoder'])
                                       if sum(bool(c) for c in row) > 1],
            'new_target_read_coefficients': [[str(c) for c in row] for row in meta['decoder']],
            'old_complete_scalar_gate_count': len(old),
            'new_complete_scalar_gate_count': len(new),
            'new_prefix_bill_with_all_coefficient_products': component.prefix_bill(meta['slots'], new),
            'inverse_prefix_bill': component.prefix_bill(meta['slots'], component.invert_word(new)),
            'four_field_original_and_inverse_components_checked': exact_payload(new, meta['slots']),
            'independent_nonpivot_correction_preserved': True,
            'negative_controls': negatives,
            'old_local_positive_child_profile': old_profile,
            'new_local_positive_child_profile': new_profile,
            'one_core_rank_change': new_rank - old_rank,
            'local_stock_role_change': -3,
            'three_core_rank_change': -9 * h,
            'three_core_stock_capacity_change': -9 * h,
            'rank_deficit_change': 0,
            'cut_frame_contract': meta['cuts'],
            'all_forward_and_reverse_scalar_operations': component.serialized_word(new),
            'global_pivot_deadline_and_source_aggregation_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker required')
    paths = [Path(__file__).resolve(), Path(component.__file__).resolve()]
    frozen = {p: p.read_bytes() for p in paths}
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    if args.workers == 1:
        rows = [probe(j) for j in (3, 4)]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, 2)) as pool:
            rows = list(pool.map(probe, (3, 4)))
    if any(p.read_bytes() != b for p, b in frozen.items()):
        raise AssertionError('Effective source closure changed')
    result = {'status': 'PASS exact weighted dirty-target absorption and both cut corrections',
              'started_utc': start, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'workers': args.workers,
              'source_sha256': {p.name: sha256(b).hexdigest() for p, b in frozen.items()},
              'cases': rows,
              'source_attribution': {'primary': 'https://github.com/CrocSwap/integer-mult-bounds/pull/166',
                  'head': '4dbc2af5f223a0fbf22542c9d6c3f71442b6a3a6',
                  'proof_sha256': '36f5b7ffb9b6454b38d2c6f8934ca1c370512f1315220c129daf2f6c9fd2e8a6',
                  'scalar_antecedent': 'Dumas and Grenet, In-place accumulation of fast multiplication formulae, arXiv:2307.12712'},
              'scope': 'Exact local dirty scalar words and retained-column checks, with declared identical frame cuts and paid sink/target deltas. Original n4/n8 basis banks remain; global pivot deadlines, complete Gaussian/native compiler, guards and a recurrence remain open.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'gate_counts': [(r['old_complete_scalar_gate_count'], r['new_complete_scalar_gate_count']) for r in rows],
                      'rank_changes': [r['one_core_rank_change'] for r in rows]}), flush=True)


if __name__ == '__main__':
    main()
