#!/usr/bin/env python3
"""Target-level side capacity with the actual paid five-cube center profile.

The center and original data profiles are immutable completed-baseline inputs.
Side profiles are optimistic sensitivity models, not attained circuits. The
ideal per-role moment is a necessary floor for serial geodesic side roles
whose positive child widths are at most h-1. All row stock is counted.
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

import paired_five_complete_baseline as baseline
import characteristic


def enclosure(histogram, m, W, b):
    return characteristic.moment_interval(
        {'m': m, 'W': W, 'child_multiplicities': histogram}, b)


def rank(histogram):
    return sum(width * count for width, count in histogram.items())


def serialize_interval(pair):
    return {'lower': str(pair[0]), 'upper': str(pair[1])}


def fixed_profile(p, split_targets=False):
    h, v, m = 2 * p, 32 * comb(p, 5), 6 * p
    center = baseline.center_tree(p)
    sources = Counter({4: v, h - 6: v, 1: v})
    targets = Counter({5: v, h - 6: v}) if split_targets else Counter({h - 1: v})
    children = Counter()
    for row in (Counter(center['local_histogram']), sources, targets):
        for width, count in row.items():
            if width:
                children[width] += 3 * count
    children[2] += 2 * v
    W = 2 * v + center['roles']
    deficit = 2 * v - 3 * center['copied_loss']
    if rank(children) != m * W - deficit:
        raise AssertionError('Actual center/source/target fixed profile lost a child')
    return {'p': p, 'h': h, 'v': v, 'm': m, 'center': center,
            'W_without_side_roles': W, 'fixed_child_profile': children,
            'fixed_rank': rank(children), 'deficit': deficit,
            'target_clock': '0 -> U5 -> target-kernel' if split_targets else 'optimistic one target-kernel child'}


def raw_cap_profile(p):
    cubes, h = comb(p, 5), 2 * p
    side = Counter()
    blocks = []
    raw = live = 0
    for j in range(max(0, 10 - p), 5):
        patterns = comb(5, j) * (1 << j)
        rank_j = sum(comb(j, a) for a in range(max(0, j - 2), min(j, 2) + 1))
        readable = comb(5, j) * rank_j
        cap, bucket = (6 if j == 0 else 5), 6 - j
        # The input aggregate has its complete literal bucket frame. Its
        # formation from original line sources is NOT supplied by this model.
        # Every original raw coordinate and parked kernel is still counted.
        pieces = [bucket] + ([cap - bucket] if cap > bucket else []) + [h - cap]
        for width in pieces:
            side[width] += 3 * patterns * cubes
        raw += patterns
        live += readable
        blocks.append({'j': j, 'raw_patterns_per_cube': patterns,
                       'readable_channels_per_cube': readable,
                       'retained_kernel_patterns_per_cube': patterns - readable,
                       'input_bucket_rank': bucket, 'common_cap_rank': cap,
                       'one_core_optimistic_role_child_pieces': pieces})
    R = raw * cubes
    if rank(side) != 3 * h * R:
        raise AssertionError('A raw cap coordinate or its full-frame return was omitted')
    leaves_per_source = sum(comb(5, j) for j in range(max(0, 10 - p), 5))
    return {'blocks': blocks, 'retained_aggregate_and_kernel_roles': R,
            'live_roles': live * cubes, 'parked_roles': (raw - live) * cubes,
            'raw_roles_per_original_source': Q(raw, 32),
            'literal_independent_copy_tree_roles': leaves_per_source * 32 * cubes,
            'literal_copy_tree_roles_per_source': leaves_per_source,
            'three_core_optimistic_raw_cap_profile': side,
            'aggregate_formation_and_birth_reuse_verified': False}


def budget(fixed, b):
    h, m, v, W0 = (fixed[k] for k in ('h', 'm', 'v', 'W_without_side_roles'))
    fixed_lo, fixed_hi = enclosure(fixed['fixed_child_profile'], m, 1, b)
    margin_lo, margin_hi = Q(W0) - fixed_hi, Q(W0) - fixed_lo
    # Concavity and positive integer widths <=h-1 minimize a total-h
    # geodesic role at pieces (h-1,1). Moving scalar stock does not avoid
    # counting its full ambient endpoint or give a clean helper for free.
    ideal = Counter({h - 1: 3, 1: 3})
    per_lo, per_hi = enclosure(ideal, m, 1, b)
    excess_lo, excess_hi = per_lo - 1, per_hi - 1
    if excess_lo <= 0:
        raise AssertionError('The ideal side role must have positive subunit-moment excess')
    if margin_hi < 0:
        necessary = None
        status = 'NO nonnegative side stock can fit this fixed profile'
    else:
        necessary = margin_hi / excess_lo
        status = 'Optimistic necessary stock ceiling only'
    return {'b': str(b), 'fixed_unnormalized_moment': serialize_interval((fixed_lo, fixed_hi)),
            'unnormalized_slack_for_side': serialize_interval((margin_lo, margin_hi)),
            'ideal_three_core_geodesic_profile_per_side_role': dict(ideal),
            'ideal_side_excess_per_role': serialize_interval((excess_lo, excess_hi)),
            'necessary_R_side_strict_upper_bound': None if necessary is None else str(necessary),
            'necessary_R_side_per_v_upper_bound': None if necessary is None else str(necessary / v),
            'status': status}


def floor_evidence(fixed, cap, b):
    h, m, v, W0 = (fixed[k] for k in ('h', 'm', 'v', 'W_without_side_roles'))
    ideal = Counter({h - 1: 3, 1: 3})
    scenarios = []
    for label, R, side in (
        ('no side stock', 0, Counter()),
        ('independent retained cap aggregates/kernels, ideal two-piece floor',
         cap['retained_aggregate_and_kernel_roles'], ideal),
        ('literal independent source-copy tree stock, ideal two-piece floor',
         cap['literal_independent_copy_tree_roles'], ideal)):
        children = Counter(fixed['fixed_child_profile'])
        for width, count in side.items():
            children[width] += R * count
        interval = enclosure(children, m, W0 + R, b)
        if rank(children) != m * (W0 + R) - fixed['deficit']:
            raise AssertionError('Sensitivity stock/profile rank telescope failed')
        scenarios.append({'scenario': label, 'side_roles': R, 'side_roles_per_v': str(Q(R, v)),
                          'complete_moment_interval': serialize_interval(interval),
                          'classification': 'excluded even by optimistic floor' if interval[0] >= 1
                                            else 'necessary floor permits; no attained chronology'})
    actual_cap = Counter(fixed['fixed_child_profile'])
    actual_cap.update(cap['three_core_optimistic_raw_cap_profile'])
    R = cap['retained_aggregate_and_kernel_roles']
    interval = enclosure(actual_cap, m, W0 + R, b)
    scenarios.append({'scenario': 'retained raw cap stock with literal bucket/common-cap/full pieces',
                      'side_roles': R, 'side_roles_per_v': str(Q(R, v)),
                      'complete_moment_interval': serialize_interval(interval),
                      'classification': 'excluded under this optimistic cap model' if interval[0] >= 1
                                        else 'optimistic model below1; aggregation/global chronology not supplied'})
    return scenarios


def probe(p):
    rows = []
    cap = raw_cap_profile(p)
    for split in (False, True):
        fixed = fixed_profile(p, split)
        targets = (Q(1, 10000), Q(20, 189981), Q(1, 1000))
        moments = [{'budget': budget(fixed, b), 'stock_models': floor_evidence(fixed, cap, b)}
                   for b in targets]
        rows.append({'target_clock': fixed['target_clock'],
                     'actual_center_roles': fixed['center']['roles'],
                     'actual_copied_center_loss': fixed['center']['copied_loss'],
                     'actual_center_child_profile_one_core': dict(fixed['center']['local_histogram']),
                     'complete_fixed_profile_without_side_roles': dict(fixed['fixed_child_profile']),
                     'W_without_side_roles': fixed['W_without_side_roles'],
                     'fixed_first_moment_deficit': fixed['deficit'], 'target_levels': moments})
    if p == 7 and any(r['fixed_first_moment_deficit'] >= 0 for r in rows):
        raise AssertionError('The preserved seven-pair first-moment failure disappeared')
    corrupted = Counter(cap['three_core_optimistic_raw_cap_profile'])
    largest = max(corrupted)
    corrupted[largest] -= 1
    if rank(corrupted) == 3 * (2 * p) * cap['retained_aggregate_and_kernel_roles']:
        raise AssertionError('Omitted full endpoint failed to change the paid rank')
    return {'p': p, 'h': 2 * p, 'v': 32 * comb(p, 5), 'm': 6 * p,
            'cap_stock_models': characteristic.serializable(cap), 'rows': rows,
            'omitted_endpoint_negative_rejected': True,
            'scope': 'Actual inherited centers and source bill, with optimistic explicitly stated side-role and target-clock models. Neither a stock ceiling nor a below1 hypothetical profile supplies aggregate formation, cross-cap chronology, native execution or a kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker is required')
    paths = [Path(__file__).resolve(), Path(baseline.__file__).resolve(),
             Path(baseline.scalar.__file__).resolve(), Path(characteristic.__file__).resolve()]
    frozen = {p: p.read_bytes() for p in paths}
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    ps = (9,) if args.bounded else (7, 9, 12)
    if args.workers == 1:
        rows = [probe(p) for p in ps]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(ps))) as pool:
            rows = list(pool.map(probe, ps))
    if any(p.read_bytes() != b for p, b in frozen.items()):
        raise AssertionError('Effective actual-center/exact-moment closure changed')
    result = {'status': 'PASS exact actual-center side-budget discriminator',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'workers': args.workers,
              'source_sha256': {p.name: sha256(b).hexdigest() for p, b in frozen.items()},
              'cases': rows,
              'scope': 'Rigorous moments and necessary ceilings of declared optimistic paid stock profiles. No attained aggregate birth, whole Gaussian side/master supplier, native recurrence or exponent.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'cases': [r['p'] for r in rows]}), flush=True)


if __name__ == '__main__':
    main()
