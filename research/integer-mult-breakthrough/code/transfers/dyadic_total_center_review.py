#!/usr/bin/env python3
"""Independent paid-total center decoder, dirty echo and complete moments.

No producer module is imported. The previous independent exact profile/log
checker is pinned as a dependency. Compact producer data is used only as a
comparison target. Native copies, side formation and full assembly are open.
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

from synchronized_center_review import moment, rank, rebuild, require


def profile(pair_count, direct, closed):
    old = rebuild(pair_count, True, closed)
    h, v, q = old['h'], old['v'], old['q'] + 1
    growing = Counter(old['center_histogram'])
    growing[1] += h  # The independently dirty total grows at every rank step.
    growing[h] += 2 if closed else 1  # Its complete read/return, besides growth.
    local = Counter({1: v, h - 1: v, h: q * (3 if closed else 2)}) if direct else growing
    loss = q * h * (2 if closed else 1)
    require(rank(local) == h * (v + q) + loss, 'Total root growth/read rank lost')
    whole = Counter(old['child_multiplicities'])
    whole.subtract({r: 3 * count for r, count in old['center_histogram'].items()})
    whole.update({r: 3 * count for r, count in local.items()})
    whole = Counter({r: count for r, count in whole.items() if count})
    W, deficit = old['W'] + 1, 2 * v - 3 * loss
    require(all(count > 0 and 0 < r < old['m'] for r, count in whole.items()),
            'A role, zero-width edge or proper master child was miscounted')
    require(rank(whole) == old['m'] * W - deficit, 'Three-core telescope failed')
    return {'pair_count': pair_count, 'h': h, 'v': v, 'q_including_total': q,
            'center_roles': v + q, 'side_roles': old['side_roles'],
            'W': W, 'm': old['m'], 'deficit': deficit, 'center_loss': loss,
            'direct_full': direct, 'closed_original': closed,
            'center_histogram': dict(local), 'growing_total_histogram': dict(growing),
            'child_multiplicities': dict(whole), 'cap_blocks': old['cap_blocks']}


def five_cube_decoder_and_echo():
    # All 32 source/target labels of one five-pair cube; every pair root and
    # one genuinely independent total root have their own dirty seed.
    h = 10
    labels = [sum(1 << (2 * j + ((choice >> j) & 1)) for j in range(5))
              for choice in range(32)]
    pairs = [(i, j) for i in range(h) for j in range(i + 1, h) if i // 2 != j // 2]
    A = [[int(S >> i & 1 and S >> j & 1) for S in labels] for i, j in pairs]
    A.append([1] * len(labels))
    D = [[Q(int(T >> i & 1 and T >> j & 1), 4)
          - Q(3 * ((T >> i & 1) + (T >> j & 1)), 32) for i, j in pairs]
         + [Q(3, 8)] for T in labels]
    central = []
    checked = 0
    for T, row in zip(labels, D):
        require(sum(bool(c) for c in row) == 5 * h - 19, 'Sparse read count lost a root')
        output = []
        for source, S in enumerate(labels):
            coefficient = sum((row[j] * A[j][source] for j in range(len(A))), Q(0))
            t = (T & S).bit_count()
            require(coefficient == Q((t - 1) * (t - 3), 8), 'Dyadic Newton decoder failed')
            output.append(coefficient)
            checked += 1
        central.append(output)
    require(all(c.denominator <= 32 and (32 % c.denominator == 0) for row in D for c in row),
            'The paid total decoder introduced an odd divisor')
    old_response_negative = relation_negative = False
    dirty_values = 0
    for component in range(8):
        x = [Q((7 * j + 3 * component) % 31 - 15, 8) for j in range(32)]
        g = [Q((11 * j + 5 * component) % 37 - 18, 16) for j in range(32)]
        z = [Q((13 * j + 7 * component) % 41 - 20, 32) for j in range(len(A))]
        y = [Q((17 * j + 11 * component) % 43 - 21, 8) for j in range(32)]
        signal = lambda vector: [sum((a * v for a, v in zip(row, vector)), Q(0)) for row in A]
        old = [seed + value for seed, value in zip(z, signal(g))]
        g_new = [a + b for a, b in zip(g, x)]
        new = [seed + value for seed, value in zip(z, signal(g_new))]
        actual = [initial + sum((d * (b - a) for d, a, b in zip(row, old, new)), Q(0))
                  for initial, row in zip(y, D)]
        expected = [initial + sum((c * value for c, value in zip(row, x)), Q(0))
                    for initial, row in zip(y, central)]
        require(actual == expected, 'Old root/helper response failed with independent total seed')
        require([value - total for value, total in zip(new, signal(g_new))] == z,
                'Permanent pair/total dirty roots did not restore')
        require([a - b for a, b in zip(g_new, x)] == g, 'Source helper did not restore')
        broken = [initial + sum((d * b for d, b in zip(row, new)), Q(0))
                  for initial, row in zip(y, D)]
        old_response_negative |= broken != expected
        # sum(pair signals)=10*total signal holds only for signal columns;
        # substituting a relation among the arbitrary dirty seeds is invalid.
        relation_negative |= sum(z[:-1], Q(0)) != 10 * z[-1]
        dirty_values += len(x) + len(g) + len(z) + len(y)
    require(old_response_negative and relation_negative, 'Dirty-root negatives lacked witnesses')
    return {'complete_five_cube_central_entries': checked, 'independent_roots': len(A),
            'eight_Gaussian_real_imag_components': 8, 'scalar_values_checked': dirty_values,
            'maximum_decoder_denominator_bits': 5, 'nonzero_reads_per_target': 5 * h - 19,
            'missing_old_response_negative_rejected': old_response_negative,
            'dirty_total_relation_negative_rejected': relation_negative,
            'scope': 'Independent scalar identity and complete dirty echo; no actual Gaussian address frame replay'}


def review(row):
    value = profile(row['pair_count'], row['direct_full'], row['closed_original'])
    retained = row['profile']
    for key in ('W', 'm', 'deficit'):
        require(value[key] == retained[key], 'Retained '+key+' mismatch')
    require(value['child_multiplicities'] == {int(r): n for r, n in retained['child_multiplicities'].items()},
            'Independent complete child histogram disagrees with compact evidence')
    at_target = moment(value, Q(1, 1000))
    passes = row['pair_count'] == 12 and not row['closed_original']
    require(at_target[1] < 1 if passes else at_target[0] > 1,
            'The declared hypothetical target/control outcome did not reproduce')
    bracket = row.get('root_bracket')
    certificate = None
    if bracket:
        below = moment(value, Q(bracket['lower']))
        above = moment(value, Q(bracket['upper']))
        require(below[1] < 1 < above[0], 'Finite exact characteristic root is not bracketed')
        certificate = {'lower': bracket['lower'], 'upper': bracket['upper'],
                       'lower_moment_upper': str(below[1]), 'upper_moment_lower': str(above[0])}
    # Every positive subdivision of a traversal has larger p-power cost than
    # its concentrated sum. At p=1 ranks agree; the general proof is recorded
    # separately, while this finite check binds the exact full profiles.
    concentrated = profile(row['pair_count'], True, row['closed_original'])
    growing = profile(row['pair_count'], False, row['closed_original'])
    concentration_gap = [str(moment(growing, Q(1, 1000))[0]
                             - moment(concentrated, Q(1, 1000))[1])]
    require(Q(concentration_gap[0]) > 0, 'Direct-full concentration failed its exact finite comparison')
    missing = Counter(value['child_multiplicities'])
    missing[value['h']] -= 3 * value['q_including_total']
    require(rank(missing) != value['m'] * value['W'] - value['deficit'],
            'An omitted complete center read was invisible to rank accounting')
    return {'reconstructed_profile': value, 'moment_at_b_1e_minus3': [str(x) for x in at_target],
            'retained_root_bracket': certificate, 'strict_growing_minus_direct_moment_lower': concentration_gap[0],
            'omitted_complete_copy_rank_negative_rejected': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    require(args.workers > 0, 'At least one worker is required')
    source = Path(__file__).resolve()
    helper = source.with_name('synchronized_center_review.py')
    frozen = {path: path.read_bytes() for path in (source, helper, args.input)}
    fixture = json.loads(frozen[args.input])
    tasks = [row for row in fixture['cases'] if not args.bounded or row['pair_count'] == 12]
    start, clock = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    if args.workers == 1:
        rows = [review(row) for row in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
            rows = list(pool.map(review, tasks))
    scalar = five_cube_decoder_and_echo()
    require(all(path.read_bytes() == payload for path, payload in frozen.items()),
            'Review source/helper/input changed during the run')
    result = {'status': 'PASS independent paid-total decoder/dirty echo and complete finite center moments',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - clock, 'workers': args.workers,
              'source_sha256': {str(path): sha256(payload).hexdigest() for path, payload in frozen.items()},
              'scalar_review': scalar, 'cases': rows,
              'scope': 'Exact independent scalar and hypothetical moment certificates; producer address frames reviewed from source only; no native side/master or kappa'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds']}), flush=True)


if __name__ == '__main__':
    main()
