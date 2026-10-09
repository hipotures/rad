#!/usr/bin/env python3
"""Complete synchronized-center/data moments with declared cap stock models.

The center histogram is reconstructed from the frozen source chronology.
The retained cap stock and its bucket/cap/full pieces are optimistic inputs,
not a supplied global side word. Copying/erasure remains a native contract.
Both paid complete-copy and closed-original-center alternatives are charged.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import synchronized_pair_centers as center
import paired_cap_side_budget as side


REPORTED_KAPPA = Q(6558894, 10 ** 10)


def fixed_profile(geometry, split_targets=False, closed_original=False):
    p, h, v, q, R = (geometry[k] for k in
                      ('p', 'h', 'original_sources', 'pair_center_roots',
                       'all_center_auxiliary_roles'))
    m = 3 * h
    local = Counter(geometry['complete_one_core_center_child_profile'])
    # A complete owned copy pays one width-h call, without moving its root.
    # Lowering and returning the actual original root instead pays two such
    # calls. This second model uses no semantic copy/disposal saving.
    if closed_original:
        local[h] += q
    loss = q * h * (2 if closed_original else 1)
    if side.rank(local) != h * R + loss:
        raise AssertionError('Synchronized root/copy/closed-return profile mismatch')
    sources = Counter({4: v, h - 6: v, 1: v})
    targets = Counter({5: v, h - 6: v}) if split_targets else Counter({h - 1: v})
    children = Counter()
    for row in (local, sources, targets):
        for width, count in row.items():
            if width:
                children[width] += 3 * count
    children[2] += 2 * v
    W = 2 * v + R
    deficit = 2 * v - 3 * loss
    if side.rank(children) != m * W - deficit:
        raise AssertionError('Complete synchronized center/data rank telescope failed')
    if not all(0 < width < m and count > 0 for width, count in children.items()):
        raise AssertionError('A full center copy became an improper master child')
    return {'p': p, 'h': h, 'v': v, 'm': m, 'q': q,
            'center_roles': R, 'center_loss': loss,
            'center_read': 'closed original full -> zero -> full' if closed_original
                           else 'complete owned copy full -> zero, original retained at full',
            'center_child_profile_one_core': dict(local),
            'W_without_side_roles': W, 'fixed_child_profile': children,
            'fixed_rank': side.rank(children), 'deficit': deficit,
            'target_clock': 'zero -> U5 -> target kernel' if split_targets
                            else 'optimistic single target-kernel child'}


def profile_with_side(fixed, histogram, R):
    children = Counter(fixed['fixed_child_profile'])
    children.update(histogram)
    W = fixed['W_without_side_roles'] + R
    if side.rank(children) != fixed['m'] * W - fixed['deficit']:
        raise AssertionError('A complete retained side role lost its rank endpoint')
    return {'m': fixed['m'], 'W': W, 'child_multiplicities': dict(children),
            'complete_rank': side.rank(children), 'deficit': fixed['deficit']}


def cap_model_bracket(fixed, cap):
    profile = profile_with_side(fixed, cap['three_core_optimistic_raw_cap_profile'],
                                cap['retained_aggregate_and_kernel_roles'])
    if fixed['deficit'] <= 0:
        return {'status': 'No positive root; complete first moment at least one',
                'profile': profile}
    bracket = side.characteristic.rational_root_bracket(profile)
    return {'status': 'Exact finite root bracket of a hypothetical cap model only',
            'profile': profile, 'bracket': bracket}


def levels(bounded):
    minimum = REPORTED_KAPPA / (1 - REPORTED_KAPPA)
    tests = [('required inherited component for kappa at least 1e-4, beta=1/20',
              Q(20, 189981)),
             ('reported comparator necessary boundary as beta tends to zero', minimum),
             ('larger complex component target', Q(1, 1000))]
    if not bounded:
        tests.extend([
            ('direct component target 1e-4', Q(1, 10000)),
            ('reported comparator necessary boundary at beta=1/20', minimum * Q(20, 19)),
            ('explicit approximate comparator', Q(65632, 10 ** 8))])
    return tests


def probe(task):
    p, bounded = task
    geometry = center.geometry(p)
    cap = side.raw_cap_profile(p)
    rows = []
    for closed_original in (False, True):
        for split_targets in (False, True):
            fixed = fixed_profile(geometry, split_targets, closed_original)
            rows.append({'center_read': fixed['center_read'],
                         'target_clock': fixed['target_clock'],
                         'center_roles': fixed['center_roles'],
                         'paid_center_loss_per_core': fixed['center_loss'],
                         'complete_one_core_center_child_profile': fixed['center_child_profile_one_core'],
                         'W_without_side_roles': fixed['W_without_side_roles'],
                         'complete_fixed_profile_without_side_roles': dict(fixed['fixed_child_profile']),
                         'three_core_deficit': fixed['deficit'],
                         'tests': [{'comparison': name,
                                    'budget': side.budget(fixed, b),
                                    'stock_models': side.floor_evidence(fixed, cap, b)}
                                   for name, b in levels(bounded)],
                         'hypothetical_complete_raw_cap_root': cap_model_bracket(fixed, cap)})
    # Omission of the h-copy call must expose exactly qh missing rank.
    corrupt = Counter(geometry['complete_one_core_center_child_profile'])
    corrupt[2 * p] -= geometry['pair_center_roots']
    if side.rank(corrupt) != geometry['complete_one_core_rank'] - geometry['copied_full_center_loss']:
        raise AssertionError('The copy omission negative did not change the paid rank')
    return {'p': p, 'h': 2 * p, 'v': geometry['original_sources'], 'm': 6 * p,
            'center_geometry': {
                'persistent_source_helpers': geometry['persistent_source_copy_helpers'],
                'persistent_roots': geometry['pair_center_roots'],
                'source_injection_and_uninjection_gates': geometry['helper_source_injection_and_subtraction_gates'],
                'four_conservative_center_M_passes': geometry['conservative_four_M_and_inverse_passes'],
                'two_complete_center_scatters': geometry['two_signed_center_scatters'],
                'root_growth_actual_interface_Pauli_images_checked': geometry['root_growth_actual_interface_Pauli_images_checked'],
                'individual_full_gaussian_helper_interfaces_replayed': False},
            'retained_cap_stock_model': side.characteristic.serializable(cap),
            'rows': rows, 'omitted_complete_copy_rank_negative_rejected': True,
            'scope': 'Complete center/data histograms with explicitly hypothetical cap formation/chronology and retained role stock. A below-one moment and its exact root are not an attained native primitive or kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker is required')
    paths = [Path(__file__).resolve(), Path(center.__file__).resolve(),
             Path(center.frames.__file__).resolve(), Path(center.paired.__file__).resolve(),
             Path(center.interfaces.__file__).resolve(), Path(side.__file__).resolve(),
             Path(side.baseline.__file__).resolve(), Path(side.characteristic.__file__).resolve()]
    frozen = {path: path.read_bytes() for path in paths}
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    tasks = [(9, True)] if args.bounded else [(9, False), (12, False)]
    if args.workers == 1:
        rows = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
            rows = list(pool.map(probe, tasks))
    if any(path.read_bytes() != value for path, value in frozen.items()):
        raise AssertionError('The effective synchronized-center/exact-moment source closure changed')
    result = {'status': 'PASS exact synchronized-center complete cap-model moments',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'workers': args.workers,
              'source_sha256': {path.name: sha256(value).hexdigest() for path, value in frozen.items()},
              'reported_comparison_kappa': str(REPORTED_KAPPA),
              'comparison_provenance': 'Coordinator-provided dated reported decimal only; upstream exponent is not adopted here',
              'assembly_scope': 'Inherited a<(1-beta)b and kappa<a/(1+a) necessary boundaries only; all-size transfer remains conditional',
              'cases': rows,
              'scope': 'Finite exact characteristic arithmetic using a new paid center histogram. Copy/erase native implementation, full cap aggregation and cross-cap continuation, fixed odd-divisor5 bridge, complete primitive and exponent are not supplied.'}
    result = side.characteristic.serializable(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'pair_counts': [row['p'] for row in rows]}), flush=True)


if __name__ == '__main__':
    main()
