#!/usr/bin/env python3
"""Retain one paid total root to make synchronized five-cube centers dyadic.

Every root, including the total root, has its own arbitrary dirty seed. The
shared helper schedule and complete copied-root interface are imported only
from frozen authored sources. Literal small operator and exact finite scalar/
moment tests do not supply global cap formation or the completed master.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

import synchronized_pair_centers as base
import synchronized_center_budget as budget


def geometry(p):
    old = base.geometry(p)
    h, v, q = (old[k] for k in ('h', 'original_sources', 'pair_center_roots'))
    histogram = Counter(old['complete_one_core_center_child_profile'])
    for stage in old['rank_growth_stages']:
        histogram[stage['new_dimension'] - stage['old_dimension']] += 1
    histogram[h] += 1
    R, loss = v + q + 1, (q + 1) * h
    if budget.side.rank(histogram) != h * R + loss:
        raise AssertionError('The independent total seed, growth or full copy was omitted')
    adapted = dict(old)
    adapted.update(pair_center_roots=q + 1, all_center_auxiliary_roles=R,
                   complete_one_core_center_child_profile=dict(histogram),
                   complete_one_core_rank=budget.side.rank(histogram),
                   copied_full_center_loss=loss)
    return adapted, {'p': p, 'h': h, 'v': v, 'pair_roots': q, 'total_roots': 1,
                     'all_roots': q + 1, 'source_helpers': v, 'center_roles': R,
                     'loss_per_core': loss, 'complete_one_core_child_profile': dict(histogram),
                     'rank_per_core': budget.side.rank(histogram),
                     'source_to_root_sum_gates_per_M_pass': 11 * v,
                     'four_conservative_M_passes': 44 * v,
                     'nonzero_decoder_reads_per_target_per_sign': 5 * h - 19,
                     'complete_signed_decoder_reads': 2 * (5 * h - 19) * v,
                     'complete_full_copy_calls_per_core': q + 1,
                     'scalar_decoder_denominator_bits': 5,
                     'odd_divisor5_interface_required': False,
                     'total_dirty_seed_is_independent': True,
                     'source_root_relation_is_signal_only': 'sum pair signals=10*total signal; independent dirty root seeds do not satisfy this relation',
                     'proper_copy_width': h, 'proper_only_under_master_width': 3 * h,
                     'scope': 'Exact shared helper/root geometry. Complete native copy/erase, cap formation and source/K/master splice remain separate.'}


def scalar_decoder(p, complete=False):
    labels = base.paired.labels(p, 5)
    h = 2 * p
    targets = labels if complete else labels[:32]
    pairs = [tuple(combinations([i for i in range(h) if S >> i & 1], 2)) for S in labels]
    checked = 0
    for T in targets:
        for S, incident in zip(labels, pairs):
            # Thirty-two times alpha is 2 when both points occur, -3 when
            # exactly one occurs, and zero otherwise. The total contributes12.
            numerator = 12 + sum(8 * bool(T >> i & 1 and T >> j & 1)
                                 - 3 * ((T >> i & 1) + (T >> j & 1))
                                 for i, j in incident)
            overlap = (T & S).bit_count()
            if numerator != 4 * (overlap - 1) * (overlap - 3):
                raise AssertionError('Paid total/pair dyadic decoder differs from f5')
            checked += 1
    T = labels[0]
    touched = [(i, j) for i in range(h) for j in range(i + 1, h)
               if i // 2 != j // 2 and (T >> i & 1 or T >> j & 1)]
    if len(touched) + 1 != 5 * h - 19:
        raise AssertionError('Sparse dyadic pair/total scatter count changed')
    return {'p': p, 'exact_central_entries_checked': checked, 'complete_central_matrix': complete,
            'pair_coefficients': ['1/16', '-3/32', '0'], 'total_coefficient': '3/8',
            'maximum_denominator_bits': 5, 'new_odd_divisor': None,
            'nonzero_reads_per_target': len(touched) + 1,
            'proof': 'sum pairs gives8*binom(overlap,2)-12*overlap; the paid total adds12, producing4*(overlap-1)*(overlap-3) over32'}


def toy_word():
    h, labels = 3, [1, 7, 2]
    n, q = 3, 3
    incidence = [[1, 1, 0], [0, 1, 1], [1, 1, 1]]
    decoder = [[Q(1, 4), Q(3, 8), Q(3, 8)],
               [Q(-1, 2), Q(1, 8), Q(3, 8)],
               [Q(3, 4), Q(-1, 4), Q(3, 8)]]
    G, R = 2 * n, 3 * n
    full = base.frames.basis(1 << i for i in range(h))
    current = [base.frames.basis((label,)) for label in labels] + [()] * (2 * n + q)
    initial, events = list(current), []

    def move(role, E):
        E = base.frames.basis(E)
        if current[role] != E:
            events.append({'kind': 'frame', 'role': role,
                           'from': list(current[role]), 'to': list(E)})
            current[role] = E

    def add(target, source, coefficient):
        if not coefficient:
            return
        if current[target] != current[source]:
            raise AssertionError('Total-root scalar mixer uses unequal actual frames')
        events.append({'kind': 'add', 'target': target, 'source': source,
                       'coefficient': str(coefficient)})

    def mix(sign):
        for feature in range(q):
            for source in range(n):
                add(R + feature, G + source, sign * incidence[feature][source])

    def read(sign, root_full, stage):
        if any(current[n + t] for t in range(n)):
            raise AssertionError('Total-root read lacks common identity target cut')
        for feature in range(q):
            if current[R + feature] != (full if root_full else ()):
                raise AssertionError('A total/pair copy starts in the wrong actual frame')
            events.append({'kind': 'copy-transform-read-discard', 'root': R + feature,
                           'root_at_full': root_full, 'sign': sign, 'stage': stage,
                           'decoder': [(n + t, str(decoder[t][feature])) for t in range(n)]})

    mix(1); read(-1, False, 'early old scatter'); mix(-1)
    for source, label in enumerate(labels):
        move(G + source, (label,)); add(G + source, source, 1)
    E = ()
    for source, label in enumerate(labels):
        E = base.frames.basis(E + (label,))
        for feature in range(q):
            move(R + feature, E)
        move(G + source, E)
        for feature in range(q):
            add(R + feature, G + source, incidence[feature][source])
        move(G + source, full)
    read(1, True, 'paid full center scatter'); mix(-1)
    for source in range(n):
        move(source, full); add(G + source, source, -1)
    for target, label in enumerate(labels):
        move(n + target, base.frames.perpendicular((label,), h))
    return events, {'h': h, 'labels': labels, 'n': n, 'q': q, 'roles': 3 * n + q,
                    'incidence': incidence, 'decoder': decoder,
                    'initial_subspaces': initial, 'final_subspaces': current}


def literal_total_toy():
    events, meta = toy_word()
    h, roles, size = 3, meta['roles'], 8
    virtual = [[[(Q((13 * role + 7 * a + 3 * field) % 29 - 14, 8),
                  Q((11 * role + 5 * a + 7 * field) % 31 - 15, 16))
                 for field in range(4)] for a in range(size)] for role in range(roles)]
    initial = [base.apply_frame(E, h, 1, row)
               for E, row in zip(meta['initial_subspaces'], virtual)]
    actual, copies = base.execute(events, initial, h, 1)
    expected = base.expected_toy(meta, virtual, 1)
    if actual != expected:
        raise AssertionError('The independent total dirty seed/ancestor response failed')
    restored, reverse_copies = base.execute(events, actual, h, 1, reverse=True)
    if restored != initial:
        raise AssertionError('A total-root/source/helper field did not restore')
    checked = 0
    for role in range(roles):
        for address in range(size):
            x = [[[(Q(0), Q(0)) for field in range(4)] for a in range(size)]
                 for unused in range(roles)]
            x[role][address][0] = (Q(1), Q(0))
            v = [base.apply_frame(E, h, 1, row, inverse=True)
                 for E, row in zip(meta['initial_subspaces'], x)]
            out, unused = base.execute(events, x, h, 1)
            if out != base.expected_toy(meta, v, 1):
                raise AssertionError('An independent physical total-root column failed')
            checked += 1
    without_total_old = [event for event in events
                         if not (event.get('stage') == 'early old scatter' and
                                 event.get('root') == 3 * meta['n'] + 2)]
    broken, unused = base.execute(without_total_old, initial, h, 1)
    if broken == expected:
        raise AssertionError('Independent total dirty seed was silently substituted')
    return {'kind': 'literal independent-total-root component', 'h': h,
            'Gaussian_fields': 4, 'complete_physical_input_columns': checked,
            'dense_real_imag_components_forward_and_reverse': 2 * 8 * roles * size,
            'all_permanent_roles': roles, 'total_seed_independent_of_pair_seeds': True,
            'missing_total_old_response_rejected': True,
            'copy_disposal_is_semantic_not_native_tape_erasure': True,
            'complete_copy_volume': copies, 'reverse_copy_volume': reverse_copies,
            'events': events,
            'scope': 'Generic h3 pair/total dirty word, not a weight-five scalar decoder or complete side/master. The actual five-cube decoder is tested separately.'}


def paired_probe(p):
    geometry_input, geometry_report = geometry(p)
    cap = budget.side.raw_cap_profile(p)
    minimum = budget.REPORTED_KAPPA / (1 - budget.REPORTED_KAPPA)
    tests = [('required inherited component', Q(20, 189981)),
             ('dated comparator necessary limit as beta tends to zero', minimum),
             ('larger component target', Q(1, 1000))]
    rows = []
    for closed in (False, True):
        for split in (False, True):
            fixed = budget.fixed_profile(geometry_input, split_targets=split, closed_original=closed)
            rows.append({'center_read': fixed['center_read'], 'target_clock': fixed['target_clock'],
                         'complete_fixed_child_profile': dict(fixed['fixed_child_profile']),
                         'W_without_side_roles': fixed['W_without_side_roles'],
                         'deficit': fixed['deficit'], 'center_loss_per_core': fixed['center_loss'],
                         'threshold_tests': [{'name': name, 'b': str(b),
                                              'stock_models': budget.side.floor_evidence(fixed, cap, b)}
                                             for name, b in tests],
                         'hypothetical_cap_root': budget.cap_model_bracket(fixed, cap)})
    return {'kind': 'paired dyadic-total center and cap model',
            'geometry': geometry_report, 'decoder': scalar_decoder(p, complete=(p == 7)),
            'cap_stock': budget.side.characteristic.serializable(cap), 'rows': rows,
            'scope': 'Paid total-root center fixes the new odd5 denominator only. Cap formation/global readout and full current-source/K/master/native programs are not supplied.'}


def run(task):
    return literal_total_toy() if task == 'toy' else paired_probe(task)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker required')
    directory = Path(__file__).resolve().parent
    names = ['synchronized_dyadic_total_centers.py', 'synchronized_center_budget.py',
             'synchronized_pair_centers.py', 'canonical_subspace_frames.py',
             'paired_five_cube_discriminator.py', 'scalable_subspace_interfaces.py',
             'paired_cap_side_budget.py', 'paired_five_complete_baseline.py', 'characteristic.py']
    paths = [directory / name for name in names]
    frozen = {path: path.read_bytes() for path in paths}
    started, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    tasks = ['toy', 9] if args.bounded else ['toy', 7, 9, 12]
    if args.workers == 1:
        rows = [run(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
            rows = list(pool.map(run, tasks))
    if any(path.read_bytes() != contents for path, contents in frozen.items()):
        raise AssertionError('The effective paid total-root closure changed')
    result = {'status': 'PASS paid dyadic total-root component and finite cap-model moments',
              'started_utc': started, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'workers': args.workers,
              'source_sha256': {path.name: sha256(contents).hexdigest() for path, contents in frozen.items()},
              'cases': rows,
              'scope': 'Finite physical total-root toy, exact five-cube scalar decoder and conditional full-histogram cap capacity. No paid global cap aggregation, complete native master or kappa.'}
    result = budget.side.characteristic.serializable(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'cases': ['toy' if 'decoder' not in row else row['geometry']['p'] for row in rows]}), flush=True)


if __name__ == '__main__':
    main()
