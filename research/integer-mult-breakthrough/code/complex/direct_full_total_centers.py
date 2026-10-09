#!/usr/bin/env python3
"""Literal direct-full synchronized total/pair centers and exact model bill.

All roots jump to the same full actual frame. All source helpers are copied
at their original odd lines, then advanced to full before any late M writes.
Original sources remain at their lines until later cleanup. The temporary
copy/native and cap/master contracts remain explicitly conditional.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

import synchronized_dyadic_total_centers as total


base, budget = total.base, total.budget


def toy_word():
    original, meta = total.toy_word()
    n, q, h = meta['n'], meta['q'], meta['h']
    G, R = 2 * n, 3 * n
    full = base.frames.basis(1 << i for i in range(h))
    last_injection = max(i for i, event in enumerate(original)
                         if event['kind'] == 'add' and event['target'] == G + n - 1
                         and event['source'] == n - 1 and Q(event['coefficient']) == 1)
    first_copy = next(i for i, event in enumerate(original)
                      if event.get('stage') == 'paid full center scatter')
    middle = [{'kind': 'frame', 'role': R + feature, 'from': [], 'to': list(full)}
              for feature in range(q)]
    middle.extend({'kind': 'frame', 'role': G + source,
                   'from': list(base.frames.basis((label,))), 'to': list(full)}
                  for source, label in enumerate(meta['labels']))
    middle.extend({'kind': 'add', 'target': R + feature, 'source': G + source,
                   'coefficient': str(meta['incidence'][feature][source])}
                  for feature in range(q) for source in range(n)
                  if meta['incidence'][feature][source])
    events = original[:last_injection + 1] + middle + original[first_copy:]
    current = list(meta['initial_subspaces'])
    for event in events:
        if event['kind'] == 'frame':
            role = event['role']
            if current[role] != tuple(event['from']):
                raise AssertionError('Direct-full frame starts from a wrong actual anchor')
            current[role] = tuple(event['to'])
        elif event['kind'] == 'add':
            if current[event['target']] != current[event['source']]:
                raise AssertionError('Direct-full M/source gate has unequal actual representatives')
        else:
            if current[event['root']] != (full if event['root_at_full'] else ()):
                raise AssertionError('Direct-full copy has the wrong actual input frame')
            if any(current[target] for target, c in event['decoder'] if Q(c)):
                raise AssertionError('Direct-full scatter target has left the common zero cut')
    if current != meta['final_subspaces']:
        raise AssertionError('Direct-full chronology changed an original endpoint')
    return events, meta


def physical_toy():
    events, meta = toy_word()
    h, roles, size = meta['h'], meta['roles'], 8
    virtual = [[[(Q((13 * role + 7 * a + 3 * field) % 29 - 14, 8),
                  Q((11 * role + 5 * a + 7 * field) % 31 - 15, 16))
                 for field in range(4)] for a in range(size)] for role in range(roles)]
    initial = [base.apply_frame(E, h, 1, row)
               for E, row in zip(meta['initial_subspaces'], virtual)]
    actual, volume = base.execute(events, initial, h, 1)
    if actual != base.expected_toy(meta, virtual, 1):
        raise AssertionError('Direct-full old/new root/helper dirty fields differ')
    restored, reverse_volume = base.execute(events, actual, h, 1, reverse=True)
    if restored != initial:
        raise AssertionError('Direct-full actual inverse failed')
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
                raise AssertionError('An independent direct-full physical column failed')
            checked += 1
    negative, unused = base.execute(events, initial, h, 1, negative='missing_copy_transform')
    if negative == actual:
        raise AssertionError('The paid full-copy transform was omitted invisibly')
    return {'kind': 'literal direct-full center component',
            'h': h, 'Gaussian_fields': 4, 'complete_physical_input_columns': checked,
            'complete_dirty_payload_components_forward_and_reverse': 2 * 8 * roles * size,
            'missing_copy_transform_rejected': True,
            'owned_copy_volume': volume, 'reverse_copy_volume': reverse_volume,
            'scalar_and_frame_events': events,
            'scope': 'Complete finite actual Gaussian component. Copy disposal is semantic; native tape and complete source/K/side/master remain conditional.'}


def geometry(p):
    h, v, q = 2 * p, 32 * comb(p, 5), 2 * p * (p - 1) + 1
    R, loss = v + q, q * h
    histogram = Counter({1: v, h - 1: v, h: 2 * q})
    if budget.side.rank(histogram) != h * R + loss:
        raise AssertionError('A helper traversal, full root or copy was omitted')
    full = base.frames.basis(1 << i for i in range(h))
    S = sum(1 << (2 * i) for i in range(5))
    images, normals = 0, []
    for E, F in (((S,), full), ((), full), (full, ())):
        normal = base.interfaces.compile_interface(E, F, h)
        literal = base.interfaces.inverse_word(base.interfaces.literal_word(E, h)) + base.interfaces.literal_word(F, h)
        images += base.interfaces.assert_complete_tableau(normal, literal)
        normals.append(normal)
    return {'p': p, 'h': h, 'original_sources': v, 'pair_center_roots': q,
            'all_center_auxiliary_roles': R, 'copied_full_center_loss': loss,
            'complete_one_core_center_child_profile': dict(histogram),
            'complete_one_core_rank': budget.side.rank(histogram),
            'representative_normal_forms': normals,
            'actual_interface_Pauli_images_checked': images,
            'helper_line_weight': 5,
            'helper_scope': 'One representative odd weight-five line/full quotient bound; all source labels are coordinate permutations, not individually materialized Gaussian interfaces',
            'every_M_gate_at_identical_actual_full_frame': True,
            'original_sources_stay_at_lines_until_other_work': True,
            'scope': 'Exact direct-full center stock/profile and representative physical interfaces; native complete-copy and full side/master still conditional'}


def paired_probe(p):
    geo = geometry(p)
    cap = budget.side.raw_cap_profile(p)
    minimum = budget.REPORTED_KAPPA / (1 - budget.REPORTED_KAPPA)
    rows = []
    for closed in (False, True):
        for split in (False, True):
            fixed = budget.fixed_profile(geo, split_targets=split, closed_original=closed)
            rows.append({'center_read': fixed['center_read'], 'target_clock': fixed['target_clock'],
                         'fixed_first_moment_deficit': fixed['deficit'],
                         'complete_fixed_child_profile': dict(fixed['fixed_child_profile']),
                         'W_without_side_roles': fixed['W_without_side_roles'],
                         'tests': [{'b': str(b), 'stock_models': budget.side.floor_evidence(fixed, cap, b)}
                                   for b in (Q(20, 189981), minimum, Q(1, 1000))],
                         'hypothetical_cap_root': budget.cap_model_bracket(fixed, cap)})
    return {'kind': 'direct-full paired total/pair center and cap model',
            'geometry': geo, 'rows': rows,
            'scope': 'Complete exact center/data profiles with declared cap stock/bucket/readout model. Source formation, global cut, native implementation and exponent not supplied.'}


def run(task):
    return physical_toy() if task == 'toy' else paired_probe(task)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker required')
    directory = Path(__file__).resolve().parent
    names = ['direct_full_total_centers.py', 'synchronized_dyadic_total_centers.py',
             'synchronized_center_budget.py', 'synchronized_pair_centers.py',
             'canonical_subspace_frames.py', 'paired_five_cube_discriminator.py',
             'scalable_subspace_interfaces.py', 'paired_cap_side_budget.py',
             'paired_five_complete_baseline.py', 'characteristic.py']
    frozen = {directory / name: (directory / name).read_bytes() for name in names}
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    tasks = ['toy', 9] if args.bounded else ['toy', 9, 12]
    if args.workers == 1:
        rows = [run(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
            rows = list(pool.map(run, tasks))
    if any(path.read_bytes() != contents for path, contents in frozen.items()):
        raise AssertionError('The direct-full source closure changed')
    result = {'status': 'PASS literal direct-full center word and complete finite cap-model bill',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'workers': args.workers,
              'source_sha256': {path.name: sha256(contents).hexdigest() for path, contents in frozen.items()},
              'cases': rows, 'scope': 'Exact finite center word and hypothetical cap capacity only; no complete native source/K/side/master or kappa'}
    result = budget.side.characteristic.serializable(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds']}), flush=True)


if __name__ == '__main__':
    main()
