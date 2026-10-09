#!/usr/bin/env python3
"""Exact auxiliary sensitivity controls for scaled Gaussian product recovery.

Complete rational coefficient multiplication is a reference oracle. Native
layout, a faster supplier, the previous integer multiplier and the outer
integer assembly are separate obligations, not certified by this checker.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import time


ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def scale(a, c):
    return a[0]*c, a[1]*c


def conj(a):
    return a[0], -a[1]


def c_matrix(s):
    alpha = (Fraction(1, 2), Fraction(1, 2))
    beta = conj(alpha)
    n = 1 << s
    return [[tensor_entry(alpha, beta, i ^ j, s) for j in range(n)] for i in range(n)]


def tensor_entry(alpha, beta, differing_bits, s):
    value = ONE
    for bit in range(s):
        value = mul(value, beta if differing_bits & (1 << bit) else alpha)
    return value


def adjoint(matrix):
    return [[conj(matrix[j][i]) for j in range(len(matrix))] for i in range(len(matrix))]


def transform(matrix, records):
    result = []
    for row in matrix:
        polynomial = []
        for degree in range(len(records[0])):
            value = ZERO
            for coefficient, record in zip(row, records):
                value = add(value, mul(coefficient, record[degree]))
            polynomial.append(value)
        result.append(polynomial)
    return result


def polynomial_product(left, right):
    r = len(left)
    result = [ZERO for _ in range(r)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            degree = (i+j) % r
            result[degree] = add(result[degree], scale(mul(a, b), -1 if i+j >= r else 1))
    return result


def product(left, right):
    return [polynomial_product(a, b) for a, b in zip(left, right)]


def norm_squared(records):
    return sum(z[0]*z[0]+z[1]*z[1] for row in records for z in row)


def l1_bound(records):
    return sum(abs(z[0])+abs(z[1]) for row in records for z in row)


def ceil_log2(integer):
    if integer < 1:
        raise ValueError('A positive integer bound is required')
    return (integer-1).bit_length()


def perturb(records, grid, phase):
    """An adversarial admitted endpoint error; not a native rounded program."""
    step = Fraction(1, 1 << grid)
    return [[(z[0]+step*(-1 if (i+k+phase) % 2 else 1),
              z[1]+step*(-1 if (2*i+k+phase) % 3 else 1))
             for k, z in enumerate(row)] for i, row in enumerate(records)]


def difference(left, right):
    return [[add(a, scale(b, -1)) for a, b in zip(x, y)] for x, y in zip(left, right)]


def rounded_scaled(records, multiplier):
    return [[(round(z[0]*multiplier), round(z[1]*multiplier)) for z in row] for row in records]


def unitarity_certificate(matrix):
    n = len(matrix)
    inverse = adjoint(matrix)
    for i in range(n):
        for j in range(n):
            value = ZERO
            for k in range(n):
                value = add(value, mul(inverse[i][k], matrix[k][j]))
            if value != (ONE if i == j else ZERO):
                raise AssertionError('Every exact Gram coefficient must be retained')
    return n*n


def probe(task):
    s, r = task
    n = 1 << s
    matrix = c_matrix(s)
    inverse = adjoint(matrix)
    gram = unitarity_certificate(matrix)
    fields = []
    for field in range(4):
        a = [[(Fraction((11*i+3*k+5*field) % 17-8),
               Fraction((7*i+k+2*field) % 13-6)) for k in range(r)] for i in range(n)]
        b = [[(Fraction((5*i+9*k+field) % 19-9),
               Fraction((i+7*k+3*field) % 11-5)) for k in range(r)] for i in range(n)]
        target = transform(inverse, product(transform(matrix, a), transform(matrix, b)))
        scaled_target = [[scale(z, n) for z in row] for row in target]
        if any(z[j].denominator != 1 for row in scaled_target for z in row for j in (0, 1)):
            raise AssertionError('The required2^s Gaussian integer recovery scale must be exact')
        a1, b1 = l1_bound(a), l1_bound(b)
        allowance = r*(a1+b1+1)
        if allowance.denominator != 1:
            raise AssertionError('Integer-input L1 bounds must be integral')
        t = s+ceil_log2(int(allowance))+4
        q = t+ceil_log2(2*n*r)
        qi = s+4+ceil_log2(2*n*r)
        eps, epsi = Fraction(1, 1 << t), Fraction(1, 1 << (s+4))
        exact_a, exact_b = transform(matrix, a), transform(matrix, b)
        approx_a, approx_b = perturb(exact_a, q, field), perturb(exact_b, q, field+1)
        if max(norm_squared(difference(approx_a, exact_a)),
               norm_squared(difference(approx_b, exact_b))) > eps*eps:
            raise AssertionError('Every admitted forward endpoint error must meet the contract')
        approx_target = perturb(transform(inverse, product(approx_a, approx_b)), qi, field+2)
        bound = n*(r*(a1*eps+b1*eps+eps*eps)+epsi)
        actual_squared = n*n*norm_squared(difference(approx_target, target))
        if bound > Fraction(1, 8) or actual_squared > bound*bound:
            raise AssertionError('The conservative whole-coefficient error allowance must hold')
        wanted = [[(int(z[0]), int(z[1])) for z in row] for row in scaled_target]
        recovered = rounded_scaled(approx_target, n)
        if recovered != wanted:
            raise AssertionError('Every scaled Gaussian integer coefficient must recover exactly')
        fields.append(dict(field=field, l1_input_bounds=[str(a1), str(b1)],
                           sufficient_forward_precision=t, injection_grid=q,
                           inverse_injection_grid=qi, scaled_error_norm_squared=str(actual_squared),
                           scaled_error_norm_upper=str(bound), complete_scaled_targets=wanted,
                           exact_coefficient_recovery=True))
    return dict(selected_axes=s, polynomial_degree=r, records=n,
                exact_gram_entries=gram, complete_gaussian_fields=4,
                complete_recovered_coefficients=4*n*r, recovery_multiplier=n,
                fields=fields, forward_and_inverse_errors_nonzero=True,
                scope='Exact complete scaled-coefficient recovery with admitted endpoint errors; '
                      'rational polynomial products are a reference oracle, not a native algorithm.')


def negative_controls():
    matrix = c_matrix(1)
    a = [[ONE], [ZERO]]
    target = transform(adjoint(matrix), product(transform(matrix, a), transform(matrix, a)))
    expected = rounded_scaled(target, 2)
    if not any(z[j].denominator != 1 for row in target for z in row for j in (0, 1)):
        raise AssertionError('The fixture must need its nontrivial coefficient scale')
    if rounded_scaled(target, 1) == expected:
        raise AssertionError('Omitting the coefficient scale must corrupt recovery')
    coarse = [[(Fraction(round(z[0])), Fraction(round(z[1]))) for z in row]
              for row in transform(matrix, a)]
    bad = transform(adjoint(matrix), product(coarse, coarse))
    if rounded_scaled(bad, 2) == expected:
        raise AssertionError('Zero fractional precision must fail the explicit unit fixture')
    without_inverse = product(transform(matrix, a), transform(matrix, a))
    if rounded_scaled(without_inverse, 2) == expected:
        raise AssertionError('The complete inverse cannot be skipped')
    return dict(omitted_scale_rejected=True, coarse_rounding_rejected=True,
                skipped_inverse_rejected=True, unit_fixture_exact_scaled_output=expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('A positive worker count is required')
    source = Path(__file__)
    before = sha256(source.read_bytes()).hexdigest()
    axes = [1, 2] if args.bounded else [1, 2, 4]
    degrees = [1, 2] if args.bounded else [1, 2, 4]
    tasks = [(s, r) for s in axes for r in degrees]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_sha256=before,
                    workers=args.workers, tasks=tasks, seed=None, stdlib_only=True,
                    hypothesis='A complete forward/product/inverse error ledger permits exact '
                               'Gaussian coefficient recovery without preserving the exact trajectory grid.',
                    maximum_records=1 << max(axes), maximum_degree=max(degrees),
                    error_model='Explicit nonzero adversarial admitted endpoint perturbations',
                    polynomial_product_model='Complete exact rational negacyclic reference oracle',
                    scope='Conditional sensitivity and exact finite scaled coefficient controls; '
                          'not a native multiplier or old full integer assembly recovery.')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    if args.workers == 1:
        cases = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, tasks))
    negatives = negative_controls()
    if sha256(source.read_bytes()).hexdigest() != before:
        raise AssertionError('The frozen scientific source changed during execution')
    summary = dict(status='PASS EXACT SCALED GAUSSIAN PRODUCT COEFFICIENT RECOVERY',
                   completed_utc=datetime.now(timezone.utc).isoformat(), source_sha256=before,
                   seconds=time.monotonic()-started, cases=cases, negative_controls=negatives,
                   all_fields_and_coefficients_retained=True,
                   scope=protocol['scope'], external_integer_multiplier_executed=False,
                   native_layout_verified=False, new_exponent=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(dict(status=summary['status'], cases=len(cases),
                          exact_gram_entries=sum(c['exact_gram_entries'] for c in cases),
                          recovered_gaussian_coefficients=sum(c['complete_recovered_coefficients']
                                                              for c in cases),
                          seconds=summary['seconds'])), flush=True)


if __name__ == '__main__':
    main()
