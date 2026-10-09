#!/usr/bin/env python3
"""Fixed-order two-scan response spans with singular diagonal coefficients.

Responses may be summed through one arbitrary dirty helper, so the one-bank
determinant/unit restriction does not apply. Small modular capacity tests and
exact rational witnesses remain separate. No native endpoint is assumed.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import time

import ordered_scan_products as S


def shear(x, f):
    return x ^ ((x & 1)*((1 << f)-2))


def generators(f):
    n = 1 << f
    named = [(name, kind, S.ordered_scan(order, kind))
             for name, order in [('natural', tuple(range(n))),
                                 ('complement-shear', tuple(shear(x, f) for x in range(n)))]
             for kind in ('prefix', 'difference')]
    result = []
    for (ln, lk, left), (rn, rk, right) in product(named, repeat=2):
        for k in range(n):
            column = tuple(int(left[i][k])*int(right[k][j]) for i in range(n) for j in range(n))
            result.append(((ln, lk, rn, rk, k), column))
    return result


def finite_span(columns, target, prime):
    basis = {}
    for column in columns:
        vector = {i: x % prime for i, x in enumerate(column) if x % prime}
        while vector:
            pivot = min(vector)
            if pivot not in basis:
                inverse = pow(vector[pivot], -1, prime)
                basis[pivot] = {i: inverse*x % prime for i, x in vector.items()}
                break
            multiple = vector[pivot]
            for i, x in basis[pivot].items():
                value = (vector.get(i, 0)-multiple*x) % prime
                if value:
                    vector[i] = value
                else:
                    vector.pop(i, None)
    residual = {i: x % prime for i, x in enumerate(target) if x % prime}
    while residual:
        pivot = min(residual)
        if pivot not in basis:
            break
        multiple = residual[pivot]
        for i, x in basis[pivot].items():
            value = (residual.get(i, 0)-multiple*x) % prime
            if value:
                residual[i] = value
            else:
                residual.pop(i, None)
    return {'prime': prime, 'response_span_rank': len(basis),
            'target_in_field_span': not residual,
            'exact_nonzero_remainder_pivot': min(residual) if residual else None,
            'Gaussian_dyadic_coefficient_exclusion_if_negative': prime == 3 and bool(residual)}


def rational_witness(columns, target):
    nvars = len(columns)
    rows = [list(map(Q, row)) for row in zip(*columns)]
    rows = [row+[Q(value)] for row, value in zip(rows, target)]
    pivots = []
    for column in range(nvars):
        found = next((i for i in range(len(pivots), len(rows)) if rows[i][column]), None)
        if found is None:
            continue
        r = len(pivots)
        rows[r], rows[found] = rows[found], rows[r]
        divisor = rows[r][column]
        rows[r] = [x/divisor for x in rows[r]]
        for i, row in enumerate(rows):
            if i != r and row[column]:
                multiple = row[column]
                rows[i] = [a-multiple*b for a, b in zip(row, rows[r])]
        pivots.append(column)
    if any(not any(row[:-1]) and row[-1] for row in rows):
        return None
    coefficients = [Q(0)]*nvars
    for i, pivot in enumerate(pivots):
        coefficients[pivot] = rows[i][-1]
    actual = tuple(sum(a*x for a, x in zip(coefficients, row)) for row in zip(*columns))
    if actual != tuple(target):
        raise AssertionError('The complete rational response identity failed')
    return tuple(coefficients)


def operator_times(matrix, values):
    return tuple(sum(Q(x)*v for x, v in zip(row, values)) for row in matrix)


def response_groups(f, named, coefficients):
    n = 1 << f
    groups = {}
    for (ln, lk, rn, rk, k), c in zip(named, coefficients):
        if c:
            key = (ln, lk, rn, rk)
            groups.setdefault(key, [Q(0)]*n)[k] += c
    result = []
    for (ln, lk, rn, rk), diagonal in groups.items():
        lo = tuple(range(n)) if ln == 'natural' else tuple(shear(x, f) for x in range(n))
        ro = tuple(range(n)) if rn == 'natural' else tuple(shear(x, f) for x in range(n))
        left, right = S.ordered_scan(lo, lk), S.ordered_scan(ro, rk)
        left = tuple(tuple(Q(x)*diagonal[j] for j, x in enumerate(row)) for row in left)
        result.append(((ln, lk, rn, rk), diagonal, left, right))
    return result


def literal_commutator(groups, x, y, dirty, invert=False):
    for unused, diagonal, B, A in reversed(groups) if invert else groups:
        delta = operator_times(A, x)
        if not invert:
            dirty = tuple(a+b for a, b in zip(dirty, delta))
            y = tuple(a+b for a, b in zip(y, operator_times(B, dirty)))
            dirty = tuple(a-b for a, b in zip(dirty, delta))
            y = tuple(a-b for a, b in zip(y, operator_times(B, dirty)))
        else:
            y = tuple(a+b for a, b in zip(y, operator_times(B, dirty)))
            dirty = tuple(a+b for a, b in zip(dirty, delta))
            y = tuple(a-b for a, b in zip(y, operator_times(B, dirty)))
            dirty = tuple(a-b for a, b in zip(dirty, delta))
    return x, y, dirty


def probe(f):
    started = time.monotonic()
    n = 1 << f
    entries = generators(f)
    named, columns = zip(*entries)
    target_matrix = S.zeta(f)
    target = tuple(x for row in target_matrix for x in row)
    finite = [finite_span(columns, target, p) for p in (3, 5)]
    receipt = {'f': f, 'N': n, 'response_families': 16,
               'coefficient_variables': len(columns), 'full_operator_entries': n*n,
               'finite_capacity': finite,
               'outside_diagonal_gauges_or_other_orders_not_searched': True,
               'seconds': 0}
    if f <= 3:
        coefficients = rational_witness(columns, target)
        if coefficients is None:
            receipt['rational_status'] = 'EXACT RATIONAL/COMPLEX SPAN EXCLUSION'
        else:
            groups = response_groups(f, named, coefficients)
            zero = (Q(0),)*n
            for column in range(3*n):
                values = [Q(0)]*(3*n)
                values[column] = 1
                x, y, dirty = tuple(values[:n]), tuple(values[n:2*n]), tuple(values[2*n:])
                expected = (x, tuple(a+b for a, b in zip(y, operator_times(target_matrix, x))), dirty)
                actual = literal_commutator(groups, x, y, dirty)
                if actual != expected or literal_commutator(groups, *actual, invert=True) != (x, y, dirty):
                    raise AssertionError('The complete arbitrary-dirty response word or inverse failed')
            powers_two = all(c.denominator & (c.denominator-1) == 0 for c in coefficients)
            receipt.update(rational_status='EXACT COMPLETE RATIONAL RESPONSE SUM',
                           dyadic_coefficients_in_this_witness=powers_two,
                           nonzero_response_groups=len(groups),
                           response_coefficients=[{'scans': list(key), 'diagonal': S.R.encoded([diag])[0]}
                                                  for key, diag, unused, unused2 in groups],
                           complete_dirty_forward_inverse_columns=3*n,
                           abstract_additive_scan_shears=4*len(groups),
                           nonzero_diagonal_coefficients=sum(c != 0 for c in coefficients),
                           native_additive_scan_and_buffer_endpoints_not_supplied=True)
    receipt['seconds'] = time.monotonic()-started
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('Positive workers required')
    sources = [Path(__file__).resolve(), Path(S.__file__).resolve(), Path(S.R.__file__).resolve()]
    hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in sources}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'protocol.json').write_text(json.dumps({
        'started_utc': datetime.now(timezone.utc).isoformat(), 'workers': args.workers,
        'standard_library_only': True, 'source_closure': hashes, 'f_tasks': [2, 3, 4, 5],
        'coefficient_scope': 'Arbitrary zero/nonunit response diagonals; Gaussian dyadic span negative via real-part reduction modulo3',
        'no_native_or_supplier_or_exponent_claim': True}, indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, (2, 3, 4, 5)))
    if hashes != {p.name: sha256(p.read_bytes()).hexdigest() for p in sources}:
        raise AssertionError('The source closure changed')
    receipt = {'status': 'PASS SINGULAR TWO-SCAN RESPONSE CAPACITY DISCRIMINATOR',
               'rows': rows, 'finite_and_rational_scopes_separate': True,
               'no_native_or_multiplier_exponent_claim': True}
    (args.output/'certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'status': receipt['status'], 'widths': [r['f'] for r in rows],
                      'F3_target_in_span': [r['finite_capacity'][0]['target_in_field_span'] for r in rows]}, sort_keys=True))


if __name__ == '__main__':
    main()
