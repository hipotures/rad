#!/usr/bin/env python3
"""Independent synchronized-center profile and dirty-echo discriminator.

Producer sources are not imported. The complete child histogram is rebuilt
from paired source labels and a stated three-core master ledger. Exact moment
bounds certify only this finite hypothetical profile. Native complete-copy
disposal, side formation and a canonical full primitive are not supplied.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb, factorial
from pathlib import Path
import time


def require(value, message):
    if not value:
        raise ValueError(message)


def rank(histogram):
    return sum(int(width) * count for width, count in histogram.items())


def rebuild(pair_count, split_targets, closed_original):
    h = 2 * pair_count
    labels = [sum(1 << (2 * coordinate + (choices >> j & 1))
                  for j, coordinate in enumerate(chosen))
              for chosen in combinations(range(pair_count), 5)
              for choices in range(32)]
    v, q = len(labels), 2 * pair_count * (pair_count - 1)
    local = Counter({1: v})  # Each original source is copied into one helper.
    pivots = {}
    growth_dimensions = []
    for label in labels:
        reduced = label
        while reduced:
            bit = reduced.bit_length() - 1
            if bit in pivots:
                reduced ^= pivots[bit]
            else:
                pivots[bit] = reduced
                growth_dimensions.append(len(pivots))
                local[1] += q  # All q roots grow together by one direction.
                break
        current_dimension = len(pivots)
        # The helper's source line is contained in the growing common frame.
        if current_dimension > 1:
            local[current_dimension - 1] += 1
        if current_dimension < h:
            local[h - current_dimension] += 1
    require(len(pivots) == h, 'Paired source labels do not span the full ambient space')
    local[h] += q * (2 if closed_original else 1)
    R_center = v + q
    loss = q * h * (2 if closed_original else 1)
    require(rank(local) == h * R_center + loss, 'Center roles or copy return lost rank')
    complete = Counter({r: 3 * count for r, count in local.items()})
    for width in (4, h - 6, 1):
        complete[width] += 3 * v
    for width in ((5, h - 6) if split_targets else (h - 1,)):
        complete[width] += 3 * v
    complete[2] += 2 * v  # Separate data correction calls.
    R_side = 0
    cap_blocks = []
    for overlap in range(max(0, 10 - pair_count), 5):
        raw_roles = comb(pair_count, 5) * comb(5, overlap) * (1 << overlap)
        cap_dimension = 6 if overlap == 0 else 5
        bucket_dimension = 6 - overlap
        pieces = [bucket_dimension, cap_dimension - bucket_dimension, h - cap_dimension]
        for width in pieces:
            if width:
                complete[width] += 3 * raw_roles
        R_side += raw_roles
        cap_blocks.append({'overlap': overlap, 'roles_including_kernel_parking': raw_roles,
                           'one_core_pieces': [x for x in pieces if x]})
    W = 2 * v + R_center + R_side
    deficit = 2 * v - 3 * loss
    require(rank(complete) == 3 * h * W - deficit, 'Full master rank telescope failed')
    require(all(0 < r < 3 * h and n > 0 for r, n in complete.items()),
            'Improper child or missing stock')
    return {'pair_count': pair_count, 'h': h, 'v': v, 'q': q,
            'center_roles': R_center, 'side_roles': R_side, 'W': W, 'm': 3 * h,
            'center_loss': loss, 'deficit': deficit,
            'split_targets': split_targets, 'closed_original': closed_original,
            'root_growth_dimensions': growth_dimensions,
            'center_histogram': dict(local), 'child_multiplicities': dict(complete),
            'cap_blocks': cap_blocks}


def logarithm_bounds(x, terms=36):
    """Outward rational bounds for log(x), with x >= 1."""
    require(x >= 1, 'Invalid logarithm argument')
    exponent = 0
    while x >= 2:
        x /= 2
        exponent += 1

    def near_one(argument):
        z = (argument - 1) / (argument + 1)
        low = 2 * sum((z ** (2 * j + 1) / (2 * j + 1)
                       for j in range(terms)), Q(0))
        tail = 2 * z ** (2 * terms + 1) / ((2 * terms + 1) * (1 - z * z))
        return low, low + tail

    lo2, hi2 = near_one(Q(2))
    lo, hi = near_one(x)
    low, high = lo + exponent * lo2, hi + exponent * hi2
    grid = 1 << 256
    return (Q(low.numerator * grid // low.denominator, grid),
            Q(-(-high.numerator * grid // high.denominator), grid))


def exponential_bounds(lo, hi, terms=14):
    require(0 <= lo <= hi and hi < 1, 'Exponential range exceeds this certificate')
    low = sum((lo ** j / factorial(j) for j in range(terms + 1)), Q(0))
    high = sum((hi ** j / factorial(j) for j in range(terms + 1)), Q(0))
    first_omitted = hi ** (terms + 1) / factorial(terms + 1)
    return low, high + first_omitted / (1 - hi / (terms + 2))


def moment(profile, saving):
    low = high = Q(0)
    for width, count in profile['child_multiplicities'].items():
        lo, hi = logarithm_bounds(Q(profile['m'], int(width)))
        exp_lo, exp_hi = exponential_bounds(saving * lo, saving * hi)
        coefficient = Q(count * int(width), profile['m'] * profile['W'])
        low += coefficient * exp_lo
        high += coefficient * exp_hi
    grid = 1 << 192
    return (Q(low.numerator * grid // low.denominator, grid),
            Q(-(-high.numerator * grid // high.denominator), grid))


def dirty_echo():
    """Scalar current-source contract only, independent of address frames."""
    A = [[1, 1, 0], [0, 1, 1]]
    D = [[Q(1, 4), Q(3, 8)], [Q(-1, 2), Q(1, 8)], [Q(3, 4), Q(-1, 4)]]
    checked = 0
    rejected_old = False
    for component in range(8):
        source = [Q((7 * j + 3 * component) % 19 - 9, 8) for j in range(3)]
        helper = [Q((11 * j + 5 * component) % 23 - 11, 16) for j in range(3)]
        roots = [Q((13 * j + component) % 29 - 14, 32) for j in range(2)]
        targets = [Q(j - component, 8) for j in range(3)]
        old = [roots[a] + sum(A[a][j] * helper[j] for j in range(3))
               for a in range(2)]
        injected = [helper[j] + source[j] for j in range(3)]
        new = [roots[a] + sum(A[a][j] * injected[j] for j in range(3))
               for a in range(2)]
        actual = [targets[t] + sum(D[t][a] * (new[a] - old[a]) for a in range(2))
                  for t in range(3)]
        expected = [targets[t] + sum(D[t][a] * A[a][j] * source[j]
                                     for a in range(2) for j in range(3))
                    for t in range(3)]
        require(actual == expected, 'Complete old-root/helper response did not cancel')
        restored_roots = [new[a] - sum(A[a][j] * injected[j] for j in range(3))
                          for a in range(2)]
        restored_helpers = [injected[j] - source[j] for j in range(3)]
        require(restored_roots == roots and restored_helpers == helper,
                'Permanent arbitrary-dirty roots or helpers did not restore')
        omitted = [targets[t] + sum(D[t][a] * new[a] for a in range(2))
                   for t in range(3)]
        rejected_old |= omitted != expected
        checked += 3 + 2 + 3
    require(rejected_old, 'The omitted current old-response negative has no witness')
    return {'scalar_real_imaginary_components_checked': checked,
            'all_eight_complete_Gaussian_components_retained': True,
            'omitted_old_root_and_source_helper_response_rejected': rejected_old,
            'scope': 'Scalar dirty echo; no literal Gaussian address frame or native copy replay'}


def check_case(row):
    pair_count, split = row['pair_count'], row['split_targets']
    results = []
    for reference in row['models']:
        profile = rebuild(pair_count, split, reference['closed_original'])
        expected = {int(k): n for k, n in reference['child_multiplicities'].items()}
        require(profile['child_multiplicities'] == expected,
                'Independent child ledger disagrees with retained producer evidence')
        for key in ('W', 'm', 'deficit'):
            require(profile[key] == reference[key], 'Retained '+key+' mismatch')
        at_target = moment(profile, Q(1, 1000))
        if reference['closed_original'] or pair_count == 9:
            require(at_target[0] > 1, 'Retained exclusion at b=1e-3 did not replay')
        else:
            require(at_target[1] < 1, 'Copied-center hypothetical model lost target slack')
        bracket = reference.get('root_bracket')
        bounds = None
        if bracket:
            below = moment(profile, Q(bracket['lower']))
            above = moment(profile, Q(bracket['upper']))
            require(below[1] < 1 < above[0], 'Retained finite root bracket is not rigorous')
            bounds = {'lower': bracket['lower'], 'upper': bracket['upper'],
                      'lower_moment_upper': str(below[1]), 'upper_moment_lower': str(above[0])}
        omitted = dict(profile)
        omitted['child_multiplicities'] = dict(profile['child_multiplicities'])
        omitted['child_multiplicities'][profile['h']] -= 3 * profile['q']
        require(rank(omitted['child_multiplicities']) != profile['m'] * profile['W'] - profile['deficit'],
                'A free full-root copy failed to corrupt the complete rank telescope')
        results.append({'reconstructed_profile': profile,
                        'moment_at_b_1e_minus3': [str(x) for x in at_target],
                        'retained_root_bracket_independently_verified': bounds,
                        'omitted_complete_copy_rank_negative_rejected': True})
    return {'pair_count': pair_count, 'split_targets': split, 'models': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    require(args.workers > 0, 'At least one worker is required')
    source_path = Path(__file__).resolve()
    frozen_source, frozen_input = source_path.read_bytes(), args.input.read_bytes()
    fixture = json.loads(frozen_input)
    tasks = fixture['cases']
    if args.bounded:
        tasks = [row for row in tasks if row['pair_count'] == 12 and row['split_targets']]
    require(tasks, 'No complete target case was selected')
    start, clock = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    if args.workers == 1:
        rows = [check_case(row) for row in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
            rows = list(pool.map(check_case, tasks))
    echo = dirty_echo()
    require(source_path.read_bytes() == frozen_source and args.input.read_bytes() == frozen_input,
            'Immutable source or input changed during review')
    result = {'status': 'PASS independent finite synchronized-center ledger and moments',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - clock, 'workers': args.workers,
              'source_sha256': sha256(frozen_source).hexdigest(),
              'input_sha256': sha256(frozen_input).hexdigest(), 'cases': rows, 'dirty_echo': echo,
              'scope': 'Exact finite hypothetical profile and scalar dirty echo. Native copying/erasure, physical side formation, common-target chronology, canonical primitive and all-size exponent remain open.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'reviewed_cases': len(rows)}), flush=True)


if __name__ == '__main__':
    main()
