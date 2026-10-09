#!/usr/bin/env python3
"""Exact image/kernel flag completion beyond self-adjoint rational frames.

Attained minimum and maximum ranks are constructed, including nested endpoint
projectors. The D(P) identities are algebraic address-operator controls, not a
claim of a paid native supplier or a better multiplier exponent.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random
import time

import rational_frame_completion as R


def span(rows, n):
    return R.rref(rows, n)[0]


def intersect(a, b, n):
    return R.kernel(list(R.kernel(a, n)) + list(R.kernel(b, n)), n)


def image(matrix):
    return span(tuple(zip(*matrix)), len(matrix))


def apply(matrix, vector):
    return tuple(sum((a * b for a, b in zip(row, vector)), Q(0)) for row in matrix)


def identity(n):
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def multiply(a, b):
    columns = tuple(zip(*b))
    return tuple(tuple(sum((x * y for x, y in zip(row, column)), Q(0)) for column in columns) for row in a)


def invert(matrix):
    n = len(matrix)
    reduced, pivots = R.rref([tuple(row) + identity(n)[i] for i, row in enumerate(matrix)], 2 * n)
    if len(reduced) != n or pivots != tuple(range(n)):
        raise ValueError('The complete image/kernel basis is singular')
    return tuple(tuple(row[n:]) for row in reduced)


def projector(F, K, n):
    F, K = span(F, n), span(K, n)
    if len(F) + len(K) != n or len(span(list(F) + list(K), n)) != n:
        raise ValueError('A direct image/kernel decomposition is required')
    basis = list(F) + list(K)
    coordinate_inverse = invert(tuple(zip(*basis)))
    P = tuple(tuple(sum((F[k][i] * coordinate_inverse[k][j] for k in range(len(F))), Q(0))
                    for j in range(n)) for i in range(n))
    if multiply(P, P) != P or image(P) != F or span(R.kernel(P, n), n) != K:
        raise AssertionError('The exact image/kernel projector failed')
    return P


def complement(required, excluded, upper, n):
    """A complement to excluded inside upper that contains required."""
    required, excluded, upper = span(required, n), span(excluded, n), span(upper, n)
    if (intersect(required, excluded, n) or not R.contained(required, upper, n)
            or not R.contained(excluded, upper, n)):
        raise ValueError('The required complement flags are inconsistent')
    selected = list(required)
    combined = span(list(selected) + list(excluded), n)
    for row in upper:
        extended = span(list(combined) + [row], n)
        if len(extended) > len(combined):
            selected.append(row)
            combined = extended
    result = span(selected, n)
    if (intersect(result, excluded, n) or len(result) + len(excluded) != len(upper)
            or not R.contained(required, result, n)):
        raise AssertionError('The exact containing complement failed')
    return result


def complete_flags(V, U, K0, K1, n):
    """V<=imP<=U and K0<=kerP<=K1, or an exact obstruction witness."""
    V, U, K0, K1 = [span(rows, n) for rows in (V, U, K0, K1)]
    if not R.contained(V, U, n) or not R.contained(K0, K1, n):
        raise ValueError('The fixed image and kernel flags must be nested')
    conflict = intersect(V, K0, n)
    if conflict:
        return dict(status='IMPOSSIBLE IMAGE/KERNEL CONFLICT', witness=conflict[0])
    ambient_span = span(list(U) + list(K1), n)
    if len(ambient_span) != n:
        return dict(status='IMPOSSIBLE UPPER IMAGE/LOWER COVECTOR COVERAGE',
                    witness=R.kernel(ambient_span, n)[0])
    A = R.kernel(K1, n)
    responses = span([apply(A, row) for row in V], len(A))
    rank_cross = len(responses)
    minimum_image = list(V)
    for row in U:
        extended = span(list(responses) + [apply(A, row)], len(A))
        if len(extended) > len(responses):
            minimum_image.append(row)
            responses = extended
    minimum_image = span(minimum_image, n)
    minimal_rank = len(V) + len(A) - rank_cross
    if len(minimum_image) != minimal_rank or intersect(minimum_image, K0, n):
        raise AssertionError('The exact minimum flag image failed')
    maximum_image = complement(minimum_image, intersect(U, K0, n), U, n)
    maximal_rank = len(U) - len(intersect(U, K0, n))
    maximum_kernel = complement(K0, intersect(maximum_image, K1, n), K1, n)
    # Choose the minimum kernel to CONTAIN the maximum kernel. Together with
    # image nesting this makes the attained endpoint projectors commute.
    extra = complement([], intersect(minimum_image, K1, n), intersect(maximum_image, K1, n), n)
    minimum_kernel = span(list(maximum_kernel) + list(extra), n)
    P = projector(minimum_image, minimum_kernel, n)
    Qmax = projector(maximum_image, maximum_kernel, n)
    if multiply(P, Qmax) != P or multiply(Qmax, P) != P:
        raise AssertionError('Nested attained endpoint projectors failed')
    for im, ker, pi in [(minimum_image, minimum_kernel, P), (maximum_image, maximum_kernel, Qmax)]:
        if (not R.contained(V, im, n) or not R.contained(im, U, n)
                or not R.contained(K0, ker, n) or not R.contained(ker, K1, n)
                or any(apply(pi, v) != v for v in V) or any(any(apply(pi, k)) for k in K0)):
            raise AssertionError('The complete four flag obligations failed')
    return dict(status='EXACT NESTED IDEMPOTENT FLAG ENDPOINTS', dimension=n,
                lower_image_dimension=len(V), lower_covector_dimension=len(A), cross_rank=rank_cross,
                minimum_rank=minimal_rank, maximum_rank=maximal_rank,
                minimum_image=minimum_image, minimum_kernel=minimum_kernel, minimum_projector=P,
                maximum_image=maximum_image, maximum_kernel=maximum_kernel, maximum_projector=Qmax)


def swap_block(P):
    n = len(P)
    I = identity(n)
    return tuple(tuple(I[i][j] - P[i][j] for j in range(n)) + tuple(P[i]) for i in range(n)) + \
           tuple(tuple(P[i]) + tuple(I[i][j] - P[i][j] for j in range(n)) for i in range(n))


def subtract(a, b):
    return tuple(tuple(x - y for x, y in zip(row_a, row_b)) for row_a, row_b in zip(a, b))


def check_endpoint_operator(result):
    n = result['dimension']
    P, Qmax = result['minimum_projector'], result['maximum_projector']
    delta = subtract(Qmax, P)
    if multiply(delta, delta) != delta or len(image(delta)) != result['maximum_rank'] - result['minimum_rank']:
        raise AssertionError('The nested difference projector rank failed')
    DP, DQ = swap_block(P), swap_block(Qmax)
    if multiply(DP, DP) != identity(2 * n) or multiply(DQ, DQ) != identity(2 * n):
        raise AssertionError('The complete swap-block involution failed')
    if multiply(DQ, DP) != swap_block(delta):
        raise AssertionError('The exact one-difference swap-block identity failed')
    return dict(delta_rank=len(image(delta)), complete_D_squared_identity=True,
                complete_relative_D_identity=True, child_width_or_native_route_not_asserted=True)


def good_reduction(matrix, modulus):
    if any(gcd(entry.denominator, modulus) != 1 for row in matrix for entry in row):
        return None
    return tuple(tuple(entry.numerator * pow(entry.denominator, -1, modulus) % modulus for entry in row) for row in matrix)


def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def orthogonal_complement(rows, G):
    return R.kernel([apply(G, row) for row in rows], len(G))


def probe(task):
    n, seed = task
    started, rng = time.monotonic(), random.Random(seed)
    base = [list(row) for row in identity(n)]
    for unused in range(4 * n):
        a, b = rng.sample(range(n), 2)
        coefficient = rng.choice((-2, -1, 1, 2))
        base[a] = [x + coefficient * y for x, y in zip(base[a], base[b])]
    split = n // 2
    actual_image, actual_kernel = base[:split], base[split:]
    cases = []
    modular_controls = 0
    for trial in range(6):
        V = actual_image[:trial % (split + 1)]
        U = actual_image + actual_kernel[:trial % (len(actual_kernel) + 1)]
        K0 = actual_kernel[:(trial + 1) % (len(actual_kernel) + 1)]
        K1 = actual_kernel + actual_image[-(trial % (split + 1)):] if trial % (split + 1) else actual_kernel
        result = complete_flags(V, U, K0, K1, n)
        if result['status'] != 'EXACT NESTED IDEMPOTENT FLAG ENDPOINTS':
            raise AssertionError('Existing splitter became an impossible flag instance')
        control = check_endpoint_operator(result)
        for modulus in (5, 25, 7, 49, 11, 121):
            reduced = good_reduction(swap_block(result['minimum_projector']), modulus)
            if reduced is None:
                continue
            product = multiply(reduced, reduced)
            if any((entry - int(i == j)) % modulus for i, row in enumerate(product) for j, entry in enumerate(row)):
                raise AssertionError('Good-prime complete address involution failed')
            modular_controls += 1
        cases.append(dict(minimum_rank=result['minimum_rank'], maximum_rank=result['maximum_rank'],
                          lower_image_dimension=result['lower_image_dimension'],
                          lower_covector_dimension=result['lower_covector_dimension'],
                          cross_rank=result['cross_rank'], operator=control))
    return dict(status='PASS EXACT GENERAL FLAG CONSTRUCTOR', n=n, seed=seed, cases=cases,
                good_prime_power_complete_matrix_controls=modular_controls,
                native_or_multiplier_claim=False, seconds=time.monotonic() - started)


def static_paired_control():
    n, G = 10, R.form(10)
    V = [tuple(Q(3 * i <= j < 3 * i + 3) for j in range(n)) for i in range(3)]
    U = R.kernel([tuple(Q(3 * (j in (0, 3, 6)) - 1) for j in range(n))], n)
    result = complete_flags(V, U, orthogonal_complement(U, G), orthogonal_complement(V, G), n)
    if (result['minimum_rank'], result['maximum_rank']) != (4, 9):
        raise AssertionError('General flags incorrectly beat the paired-G radical bound')
    check_endpoint_operator(result)
    conflict = complete_flags([identity(3)[0]], identity(3), [identity(3)[0]], identity(3), 3)
    cover = complete_flags([], [identity(3)[0]], [], [identity(3)[0], identity(3)[1]], 3)
    if conflict['status'] != 'IMPOSSIBLE IMAGE/KERNEL CONFLICT' or cover['status'] != 'IMPOSSIBLE UPPER IMAGE/LOWER COVECTOR COVERAGE':
        raise AssertionError('The exact flag obstruction was missed')
    invalid_rejected = False
    try:
        complete_flags([identity(3)[0]], [identity(3)[1]], [], identity(3), 3)
    except ValueError:
        invalid_rejected = True
    if not invalid_rejected:
        raise AssertionError('Inconsistent fixed flag input accepted')
    return dict(status='PASS PAIRED-G STATIC NO-RANK-ESCAPE CONTROL', minimum_rank=4, maximum_rank=9,
                radical_dimension=1, negative_controls=['image_kernel_conflict', 'missing_covector_coverage', 'inconsistent_fixed_flags'],
                minimum_projector_G_self_adjoint=multiply(tuple(zip(*result['minimum_projector'])), G) == multiply(G, result['minimum_projector']),
                dropping_self_adjointness_does_not_lower_this_static_cut=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('Positive workers required')
    sources = [Path(__file__).resolve(), Path(R.__file__).resolve()]
    hashes = {path.name: sha256(path.read_bytes()).hexdigest() for path in sources}
    args.output.mkdir(parents=True, exist_ok=False)
    tasks = [(4, 20261009171), (6, 20261009172), (10, 20261009173), (12, 20261009174)]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_closure=hashes,
                    tasks=tasks, workers=args.workers, stdlib_only=True,
                    scope='General rational image/kernel flags and exact algebraic D operators; no native or exponent')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, tasks))
    static = static_paired_control()
    if hashes != {path.name: sha256(path.read_bytes()).hexdigest() for path in sources}:
        raise AssertionError('The flag constructor closure changed')
    receipt = dict(status='PASS GENERAL IDEMPOTENT FLAG AND STATIC OBSTRUCTION CONTROLS', cases=rows, static=static)
    (args.output / 'certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(status=receipt['status'], dimensions=[row['n'] for row in rows],
                         exact_flag_cases=sum(len(row['cases']) for row in rows),
                         good_prime_power_matrix_controls=sum(row['good_prime_power_complete_matrix_controls'] for row in rows),
                         paired_G_static_minimum=static['minimum_rank']), sort_keys=True))


if __name__ == '__main__':
    main()
