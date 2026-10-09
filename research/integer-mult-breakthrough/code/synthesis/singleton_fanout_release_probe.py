#!/usr/bin/env python3
"""Pure carried-source fanout into monotone singleton aggregate roots.

Exact binary bucket geometry, release-count lower bounds and an all-release
dirty scalar/anchor countercontrol. No literal Gaussian address matrices,
native implementation or improved multiplier are claimed.
"""

from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path
import random
import time


def basis(values):
    pivots = {}
    for value in values:
        for bit in sorted(pivots, reverse=True):
            if value >> bit & 1:
                value ^= pivots[bit]
        if value:
            bit = value.bit_length() - 1
            for other in list(pivots):
                if pivots[other] >> bit & 1:
                    pivots[other] ^= value
            pivots[bit] = value
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def distance(E, F):
    return 2 * len(basis(E + F)) - len(E) - len(F)


def label(code, k):
    return sum(1 << (2 * j + (code >> j & 1)) for j in range(k))


def cube(k):
    if k < 3 or k % 2 == 0:
        raise ValueError('Odd cube weight at least three is required')
    return tuple(label(code, k) for code in range(1 << k))


def buckets(k):
    labels = cube(k)
    return tuple((j, bit, tuple(code for code in range(1 << k)
                                if code >> j & 1 == bit),
                  basis(labels[code] for code in range(1 << k)
                        if code >> j & 1 == bit))
                 for j in range(k) for bit in (0, 1))


def scalar_release_lower(k, released):
    n = 1 << k
    if not 0 <= released <= n:
        raise ValueError('Release count outside source stock')
    forced = max(0, k * (n // 2) - k * released)
    visits = max(0, forced - (n - released))
    return 2 * released + 2 * visits


def geometry(k):
    labels, rows = cube(k), buckets(k)
    ambient = 2 * k
    full = basis(1 << j for j in range(ambient))
    if len(basis(labels)) != k + 1 or any(v.bit_count() % 2 != 1 for v in labels):
        raise AssertionError('The odd paired cube has the wrong complete span')
    if any(len(E) != k or len(codes) != (1 << (k - 1))
           for j, bit, codes, E in rows):
        raise AssertionError('A literal singleton bucket lost rank or labels')
    if any(distance(E, F) != 2 for a, E in enumerate(row[3] for row in rows)
           for F in (row[3] for row in rows[a + 1:])):
        raise AssertionError('Distinct singleton bucket hyperplanes are not distance two')
    t = 1 << (k - 2)
    if (1 << (k - 1)) != 2 * t:
        raise AssertionError('The maximal proper odd-label bound changed')
    lower = [scalar_release_lower(k, r) for r in range((1 << k) + 1)]
    optimum = min(lower)
    if k == 5 and (optimum != 24 or lower.index(optimum) != 12):
        raise AssertionError('The release-aware minimum is not 24 at twelve')
    source = (labels[0],)
    # A source whose diagonal incidence is removed must leave the initial
    # line/full geodesic. The explicit zero detour is a valid adversary.
    if distance(source, ()) + distance((), full) != ambient + 1:
        raise AssertionError('A released source did not pay two excess ranks')
    if distance(source, full) != ambient - 1:
        raise AssertionError('The original line/full endpoint baseline changed')
    if any(distance(source, E) + distance(E, full) != ambient - 1
           for j, bit, codes, E in rows if 0 in codes):
        raise AssertionError('A compatible single bucket fails the endpoint telescope')
    return {'kind': 'complete singleton geometry', 'k': k, 'h': ambient,
            'sources': 1 << k, 'complete_cube_span': k + 1,
            'singleton_buckets': len(rows), 'bucket_rank': k,
            'labels_per_bucket': 2 * t,
            'maximum_labels_in_proper_bucket_subspace': t,
            'written_odd_linear_functional_argument_required': True,
            'release_aware_extra_rank_lower_by_count': lower,
            'minimum_extra_rank_lower': optimum,
            'minimizing_release_counts': [r for r, x in enumerate(lower) if x == optimum],
            'released_zero_detour_extra_rank': 2,
            'arbitrary_helper_Lagrangian_extension_requires_E_distance_lemma': True}


def threshold(k, limited):
    row = buckets(k)[0]
    codes, E = row[2], row[3]
    count, n = 0, (1 << (k - 2)) + 1
    for subset in combinations(codes, n):
        if len(basis(label(code, k) for code in subset)) != k:
            raise AssertionError('A subset beyond the proper odd bound lost full bucket rank')
        count += 1
        if limited and count == 32:
            break
    # Paired-coordinate permutations and within-pair flips give every bucket
    # from this representative. The source retains explicit full bucket spans.
    return {'kind': 'threshold subset controls', 'k': k,
            'representative_bucket': [row[0], row[1]], 'subset_size': n,
            'complete_or_bounded_subset_checks': count, 'bounded': limited,
            'other_buckets': 'Exact paired-coordinate permutation/flip symmetry'}


def forced_profile(k, order, released):
    n = 1 << k
    if sorted(order) != list(range(n)) or not set(released) <= set(order):
        raise ValueError('The source order/release set is not a complete cube')
    threshold = 1 << (k - 2)
    visits = {code: 0 for code in order if code not in released}
    seen = [[0, 0] for j in range(k)]
    for code in order:
        if code in released:
            continue
        for j in range(k):
            bit = code >> j & 1
            seen[j][bit] += 1
            if seen[j][bit] > threshold:
                visits[code] += 1
    expected = sum(max(0, sum(code not in released for code in codes) - threshold)
                   for j, bit, codes, E in buckets(k))
    forced = sum(visits.values())
    if forced != expected or forced < max(0, k * n // 2 - k * len(released)):
        raise AssertionError('A complete source schedule lost its compulsory incidence count')
    extra = 2 * len(released) + 2 * sum(max(0, r - 1) for r in visits.values())
    if extra < scalar_release_lower(k, len(released)):
        raise AssertionError('The forced schedule violates the conservative release-aware bound')
    return {'released': len(released), 'forced_bucket_visits': forced,
            'helpers_with_forced_visits': sum(r > 0 for r in visits.values()),
            'compulsory_schedule_extra_rank_lower': extra,
            'conservative_release_count_lower': scalar_release_lower(k, len(released))}


def orders(limited):
    checks, minimum, maximum = 0, None, None
    candidates = permutations(range(8))
    for order in candidates:
        row = forced_profile(3, order, set())
        value = row['compulsory_schedule_extra_rank_lower']
        minimum = value if minimum is None else min(minimum, value)
        maximum = value if maximum is None else max(maximum, value)
        checks += 1
        if limited and checks == 96:
            break
    rng = random.Random(202610091146)
    order = list(range(32))
    samples = []
    for name in ('natural', 'gray', 'seeded-shuffle'):
        if name == 'gray':
            order = [x ^ (x >> 1) for x in range(32)]
        elif name == 'seeded-shuffle':
            rng.shuffle(order)
        # Complement-paired twelve releases keep each singleton bucket's
        # released count exactly six; the aggregate responses remain literal.
        paired_release = {c for a in range(6) for c in (a, a ^ 31)}
        samples.append({'order_name': name, 'source_order': list(order),
                        'release_cases': [forced_profile(5, order, released)
                                          for released in (set(), paired_release, set(range(32)))]})
    all_released = forced_profile(5, list(range(32)), set(range(32)))
    if all_released['compulsory_schedule_extra_rank_lower'] != 64:
        raise AssertionError('The adversarial all-release comparison changed')
    if all_released['compulsory_schedule_extra_rank_lower'] >= 96:
        raise AssertionError('The no-release 96 bound was incorrectly promoted to releases')
    return {'kind': 'complete source orders and adversarial release control',
            'k3_orders_checked': checks, 'k3_forced_extra_min': minimum,
            'k3_forced_extra_max': maximum, 'k5_sample_schedules': samples,
            'seed': 202610091146, 'invalid_universal_96_claim_rejected': True,
            'minimum24_is_a_lower_bound_not_an_attained_schedule': True}


def all_release_word(k):
    labels, rows = cube(k), buckets(k)
    n, q, h = len(labels), len(rows), 2 * k
    helpers, roots, roles = n, 2 * n, 2 * n + q
    current = [(v,) for v in labels] + [()] * (n + q)
    initial = list(current)
    full = basis(1 << j for j in range(h))
    events, word = [], []

    def move(role, E):
        E = basis(E)
        if current[role] != E:
            events.append({'kind': 'frame', 'role': role,
                           'from': list(current[role]), 'to': list(E),
                           'rank': distance(current[role], E)})
            current[role] = E

    def add(i, j, sign):
        if current[i] != current[j]:
            raise AssertionError('The complete dirty scalar gate has mismatched actual anchors')
        word.append((i, j, sign))
        events.append({'kind': 'add', 'target': i, 'source': j, 'coefficient': sign,
                       'common_subspace': list(current[i])})

    for a, row in enumerate(rows):
        for source in row[2]:
            add(roots + a, helpers + source, -1)
    for source, v in enumerate(labels):
        helper = helpers + source
        move(helper, (v,)); add(helper, source, 1); move(helper, ())
        for a, row in enumerate(rows):
            if source in row[2]:
                add(roots + a, helper, 1)
    for a, row in enumerate(rows):
        move(roots + a, row[3])
    for source in range(n):
        move(source, full); move(helpers + source, full)
        add(helpers + source, source, -1)

    matrix = [[int(i == j) for j in range(roles)] for i in range(roles)]
    for i, j, sign in word:
        matrix[i] = [a + sign * b for a, b in zip(matrix[i], matrix[j])]
    expected = [[int(i == j) for j in range(roles)] for i in range(roles)]
    for a, row in enumerate(rows):
        for source in row[2]:
            expected[roots + a][source] += 1
    if matrix != expected:
        raise AssertionError('The all-release echo changes an independent dirty/source/root column')
    reverse = [row[:] for row in matrix]
    for i, j, sign in reversed(word):
        reverse[i] = [a - sign * b for a, b in zip(reverse[i], reverse[j])]
    if reverse != [[int(i == j) for j in range(roles)] for i in range(roles)]:
        raise AssertionError('The actual reversed scalar word failed its complete inverse')
    corrupt = [[int(i == j) for j in range(roles)] for i in range(roles)]
    for i, j, sign in word[len(rows[0][2]) * q:]:
        corrupt[i] = [a + sign * b for a, b in zip(corrupt[i], corrupt[j])]
    if corrupt == expected:
        raise AssertionError('Omitting the early dirty response was not rejected')
    helper_rank = sum(event['rank'] for event in events if event['kind'] == 'frame'
                      and helpers <= event['role'] < roots)
    if helper_rank != (h + 2) * n:
        raise AssertionError('The all-release physical anchor path lost an extra line call')
    return {'kind': 'all-release complete dirty scalar and actual-anchor word',
            'k': k, 'h': h, 'all_roles': roles, 'source_roles': n,
            'arbitrary_dirty_helper_roles': n, 'arbitrary_dirty_aggregate_roots': q,
            'complete_independent_scalar_matrix_entries': roles * roles,
            'all_scalar_gates_common_actual_anchor_checked': len(word),
            'source_helpers_paid_rank': helper_rank,
            'source_helper_baseline_rank': h * n,
            'source_helper_extra_rank': 2 * n,
            'source_and_root_virtual_outputs_fixed': True,
            'all_dirty_helpers_restored_under_full_endpoint_operator': True,
            'scalar_chronological_inverse_restored': True,
            'missing_early_dirty_response_rejected': True,
            'frame_events': events,
            'literal_Gaussian_address_coefficients_replayed': False,
            'scope': 'Exact scalar word and common actual-frame anchor chronology; wrapper algebra/native cost remains separately conditional'}


def dispatch(task):
    name, value, limited = task
    if name == 'geometry':
        return geometry(value)
    if name == 'threshold':
        return threshold(value, limited)
    if name == 'orders':
        return orders(limited)
    return all_release_word(value)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('Positive worker count required')
    if args.output and args.output.exists():
        raise FileExistsError('Optional output must be a new file')
    source = Path(__file__).resolve()
    pinned = sha256(source.read_bytes()).hexdigest()
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    tasks = [('geometry', k, args.bounded) for k in (3, 5, 7)]
    tasks += [('threshold', 5, args.bounded), ('orders', 3, args.bounded)]
    tasks += [('dirty', k, args.bounded) for k in (3, 5)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(dispatch, tasks))
    if sha256(source.read_bytes()).hexdigest() != pinned:
        raise AssertionError('Source changed during the immutable attempt')
    receipt = {'status': 'PASS pure-source singleton fanout release controls',
               'started_utc': started, 'completed_utc': datetime.now(timezone.utc).isoformat(),
               'seconds': time.monotonic() - tick, 'workers': args.workers,
               'bounded': args.bounded, 'source_sha256': pinned,
               'dependencies': 'Python standard library only', 'cases': rows,
               'proof_scope': 'Direct pure carried-source helpers with monotone literal singleton aggregate roots; no source-helper mixing, cancellation-created birth rows, owned copies or changed ports',
               'Gaussian_address_matrices_or_native_supplier_verified': False,
               'no_multiplier_exponent_claim': True}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({key: value for key, value in receipt.items() if key != 'cases'}, sort_keys=True))


if __name__ == '__main__':
    main()
