#!/usr/bin/env python3
"""Import-free rational completion and odd-ring geometry controls.

The actual primitive, address permutation, scalar word and native transfer are
not supplied. Exact projector identities certify geometry only. This source
independently constructs the four-direction example rather than importing its
producer's rational completion algorithm.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import time


Q = Fraction


def transpose(a):
    return [list(row) for row in zip(*a)]


def multiply(a, b, modulus=None):
    if not a or not b or len(a[0]) != len(b):
        raise ValueError('Nonempty conformable matrices are required')
    bt = transpose(b)
    result = [[sum(x * y for x, y in zip(row, column)) for column in bt] for row in a]
    return [[x % modulus for x in row] for row in result] if modulus else result


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def inverse(a, modulus=None):
    n = len(a)
    if not n or any(len(row) != n for row in a):
        raise ValueError('A nonempty square matrix is required')
    matrix = [[Q(x) for x in row] + [Q(int(i == j)) for j in range(n)]
              for i, row in enumerate(a)] if modulus is None else [
                  [x % modulus for x in row] + [int(i == j) for j in range(n)]
                  for i, row in enumerate(a)]
    for j in range(n):
        if modulus is None:
            pivot = next((i for i in range(j, n) if matrix[i][j]), None)
        else:
            pivot = next((i for i in range(j, n) if matrix[i][j] % (modulus_prime(modulus))), None)
        if pivot is None:
            raise ValueError('The matrix has no invertible pivot')
        matrix[j], matrix[pivot] = matrix[pivot], matrix[j]
        scale = 1 / matrix[j][j] if modulus is None else pow(matrix[j][j], -1, modulus)
        matrix[j] = [x * scale for x in matrix[j]]
        if modulus:
            matrix[j] = [x % modulus for x in matrix[j]]
        for i in range(n):
            if i != j:
                coefficient = matrix[i][j]
                matrix[i] = [x - coefficient * y for x, y in zip(matrix[i], matrix[j])]
                if modulus:
                    matrix[i] = [x % modulus for x in matrix[i]]
    return [row[n:] for row in matrix]


def modulus_prime(modulus):
    for p in range(2, modulus + 1):
        if modulus % p == 0:
            while modulus % p == 0:
                modulus //= p
            if modulus != 1:
                raise ValueError('Only prime-power moduli are accepted')
            return p
    raise ValueError('A prime power larger than one is required')


def determinant(a):
    matrix = [[Q(x) for x in row] for row in a]
    result = Q(1)
    for j in range(len(matrix)):
        pivot = next((i for i in range(j, len(matrix)) if matrix[i][j]), None)
        if pivot is None:
            return Q(0)
        if pivot != j:
            matrix[j], matrix[pivot] = matrix[pivot], matrix[j]
            result = -result
        value = matrix[j][j]
        result *= value
        for i in range(j + 1, len(matrix)):
            factor = matrix[i][j] / value
            matrix[i] = [x - factor * y for x, y in zip(matrix[i], matrix[j])]
    return result


def rank_mod(a, p):
    matrix = [[x % p for x in row] for row in a]
    rank = 0
    for j in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][j]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = pow(matrix[rank][j], -1, p)
        matrix[rank] = [x * scale % p for x in matrix[rank]]
        for i in range(len(matrix)):
            if i != rank:
                coefficient = matrix[i][j]
                matrix[i] = [(x - coefficient * y) % p for x, y in zip(matrix[i], matrix[rank])]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def form(h, modulus=None):
    one_ninth = Q(1, 9) if modulus is None else pow(9, -1, modulus)
    result = [[int(i == j) - one_ninth for j in range(h)] for i in range(h)]
    return [[x % modulus for x in row] for row in result] if modulus else result


def gram(rows, g, modulus=None):
    return multiply(multiply(rows, g, modulus), transpose(rows), modulus)


def basis(h):
    if h < 10:
        raise ValueError('The four-direction example requires h>=10')
    triples = [[int(3 * k <= j < 3 * k + 3) for j in range(h)] for k in range(3)]
    target = [int(j in (0, 3, 6)) for j in range(h)]
    extra = [target[j] + 6 * int(j == 9) for j in range(h)]
    return triples, target, extra


def projector(rows, g, modulus=None):
    b = transpose(rows)
    return multiply(multiply(b, inverse(gram(rows, g, modulus), modulus), modulus),
                    multiply(rows, g, modulus), modulus)


def reduce_rational(a, modulus):
    return [[(Q(x).numerator * pow(Q(x).denominator, -1, modulus)) % modulus
             for x in row] for row in a]


def require(condition, reason):
    if not condition:
        raise AssertionError(reason)


def finite_ring_counterexample(h, exponent):
    """A rational-positive span becomes a large isotropic span at p=5."""
    modulus = 5 ** exponent
    square_root = next(i for i in range(modulus) if (i * i + 1) % modulus == 0)
    r = h // 4
    isotropic, duals = [], []
    for j in range(r):
        row = [0] * h
        row[4*j:4*j+4] = [1, -1, square_root, -square_root]
        isotropic.append(row)
        duals.append([int(i == 4 * j) for i in range(h)])
    g = form(h, modulus)
    zero = [[0] * r for unused in range(r)]
    require(gram(isotropic, g, modulus) == zero, 'Every isotropic radical direction must be retained')
    require(multiply(multiply(isotropic, g, modulus), transpose(duals), modulus) == identity(r),
            'The finite-ring dual pairing must be the identity')
    completed_gram = gram(isotropic + duals, g, modulus)
    inverse(completed_gram, modulus)
    require(rank_mod(isotropic, 5) == r, 'The radical is a free rank-r module')
    require(determinant(gram(isotropic, form(h))) != 0,
            'The same integer vectors have a nondegenerate rational lower span')
    forbidden_projector = False
    try:
        reduce_rational(projector(isotropic, form(h)), modulus)
    except ValueError:
        forbidden_projector = True
    require(forbidden_projector, 'The bad-prime rational projector cannot be reduced as a unit interface')
    return dict(prime=5, exponent=exponent, radical_rank=r, minimum_finite_completion_dimension=2*r,
                rational_minimum_dimension=r, literal_dual_completion_dimension=2*r,
                rational_projector_reduction_rejected=True,
                scope='Counterexample to importing the rational Lorentz bound into arbitrary odd-ring spans')


def probe(h):
    started = time.monotonic()
    triples, target, extra = basis(h)
    completed = triples + [extra]
    g = form(h)
    actual_gram = gram(completed, g)
    expected_gram = [[2, -1, -1, -2], [-1, 2, -1, -2], [-1, -1, 2, -2], [-2, -2, -2, 30]]
    require(actual_gram == expected_gram and determinant(actual_gram) == -108,
            'The integer four-direction Gram matrix must be independent of h')
    covector = [3 * x - 1 for x in target]
    require(all(sum(x*y for x, y in zip(row, covector)) == 0 for row in completed),
            'Every completed direction must lie in the future cap')
    radical = [sum(row[j] for row in triples) for j in range(h)]
    require(gram(triples, g) == [[3 * int(i == j) - 1 for j in range(3)] for i in range(3)],
            'The rational lower radical must be the all-three-triples line')
    require(sum(x*y for x, y in zip(multiply([radical], g)[0], extra)) == -6,
            'The added direction must pair nontrivially with the lower radical')
    rational_projector = projector(completed, g)
    checks, rejected = [], []
    for p in (2, 3, 5, 7, 11, 13, 17):
        if p in (2, 3) or (h - 9) % p == 0:
            rejected.append(dict(prime=p, reason=('outside odd domain' if p == 2 else
                'form/Gram denominator' if p == 3 else 'singular full ambient form')))
            continue
        for exponent in (1, 2, 3):
            modulus = p ** exponent
            gm = form(h, modulus)
            pf = projector(completed, gm, modulus)
            require(pf == reduce_rational(rational_projector, modulus),
                    'Rational and odd-ring projectors must agree at good primes')
            require(multiply(pf, pf, modulus) == pf, 'The complete projector must be idempotent')
            require(multiply(transpose(pf), gm, modulus) == multiply(gm, pf, modulus),
                    'The complete projector must be G-self-adjoint')
            require(multiply(pf, transpose(completed), modulus) ==
                    [[x % modulus for x in row] for row in transpose(completed)],
                    'The projector must fix every completion basis direction')
            # U=T-perp; <T,T>=2, so its complete projector has denominator six.
            pu = [[(int(i == j) - target[i] * covector[j] * pow(6, -1, modulus)) % modulus
                   for j in range(h)] for i in range(h)]
            require(multiply(pu, pu, modulus) == pu, 'The cap projector must be idempotent')
            require(multiply(pf, pu, modulus) == pf == multiply(pu, pf, modulus),
                    'Both chronological nesting products must agree')
            reflection = [[(int(i == j) - 2 * pf[i][j]) % modulus for j in range(h)] for i in range(h)]
            require(multiply(reflection, reflection, modulus) == identity(h),
                    'The associated full-module reflection must be an involution')
            require(multiply(multiply(transpose(reflection), gm, modulus), reflection, modulus) == gm,
                    'The associated full-module reflection must preserve the complete form')
            checks.append(dict(prime=p, exponent=exponent, full_coordinate_entries=h*h,
                               projector_rank=4, complete_module_geometry=True))
    # For all 27 caps, constant entries within each triple and zero outside sum
    # make the lower radical orthogonal to the entire cap. The following exact
    # coordinate spanning set binds that argument without importing its producer.
    joint_cap_basis = triples + [[int(j == i) - int(j == 9) for j in range(h)] for i in range(10, h)]
    all_caps = [[3 * int(j in (a, b, c)) - 1 for j in range(h)]
                for a in range(3) for b in range(3, 6) for c in range(6, 9)]
    require(all(sum(x*y for x, y in zip(row, cap)) == 0
                for row in joint_cap_basis for cap in all_caps), 'The exact joint-cap basis must satisfy every cap')
    require(all(sum(x*y for x, y in zip(multiply([radical], g)[0], row)) == 0
                for row in joint_cap_basis), 'The retained radical must obstruct every containing completion')
    counterexamples = [finite_ring_counterexample(h, exponent) for exponent in (1, 2, 3)]
    return dict(status='PASS EXACT RATIONAL AND ODD-RING GEOMETRY', h=h,
                rational_minimal_dimension=4, rational_Gram_determinant=-108,
                verified_good_prime_powers=checks, excluded_prime_examples=rejected,
                joint_cap_dimension=h-7, joint_cap_obstruction=True,
                finite_ring_counterexamples=counterexamples,
                geometric_proof_only=True, native_or_exponent_claim=False,
                seconds=time.monotonic()-started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    require(args.workers > 0, 'A positive worker count is required')
    source = Path(__file__).resolve()
    digest = sha256(source.read_bytes()).hexdigest()
    tasks = (10,) if args.bounded else (10, 12, 24, 48)
    started = datetime.now(timezone.utc).isoformat()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(dict(started_utc=started,
            source_sha256=digest, tasks=tasks, workers=args.workers, bounded=args.bounded,
            imports='Python standard library only',
            scope='Exact independent geometry and bad-prime controls; no physical primitive or native exponent'), indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, tasks))
    require(sha256(source.read_bytes()).hexdigest() == digest, 'The source must remain unchanged during execution')
    summary = dict(status='PASS EXACT RATIONAL COMPLETION MODULAR REVIEW', dimensions=list(tasks),
                   cases=len(rows), good_prime_power_cases=sum(len(row['verified_good_prime_powers']) for row in rows),
                   finite_ring_negative_cases=sum(len(row['finite_ring_counterexamples']) for row in rows),
                   all_coordinate_entries=sum(sum(case['full_coordinate_entries'] for case in row['verified_good_prime_powers']) for row in rows),
                   geometry_only=True, native_or_exponent=False)
    if args.output:
        (args.output / 'certificate.json').write_text(json.dumps(dict(summary=summary, cases=rows), indent=2)+'\n')
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
