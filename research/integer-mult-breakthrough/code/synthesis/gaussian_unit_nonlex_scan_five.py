#!/usr/bin/env python3
"""Small modulo-five screen of Gaussian-unit high-flux scan candidates.

The homomorphism Z[i,1/2] -> F5 sends i to2 and every Gaussian-dyadic
unit to a nonzero element. An exhaustive negative excludes such unit
diagonals only for the stated orders/types. Finite positives do not lift
automatically. Arbitrary invertible complex scales are outside this screen.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import time

import ordered_scan_products as S

PRIME = 5


def kernel(rows, n):
    rows = [[int(x) % PRIME for x in row] for row in rows
            if any(int(x) % PRIME for x in row)]
    pivots = []
    for column in range(n):
        found = next((i for i in range(len(pivots), len(rows)) if rows[i][column]), None)
        if found is None:
            continue
        r = len(pivots)
        rows[r], rows[found] = rows[found], rows[r]
        inverse = pow(rows[r][column], -1, PRIME)
        rows[r] = [inverse*x % PRIME for x in rows[r]]
        for i, row in enumerate(rows):
            if i != r and row[column]:
                coefficient = row[column]
                rows[i] = [(a-coefficient*b) % PRIME for a, b in zip(row, rows[r])]
        pivots.append(column)
    basis = []
    for free in range(n):
        if free not in pivots:
            vector = [0]*n
            vector[free] = 1
            for i, pivot in enumerate(pivots):
                vector[pivot] = -rows[i][free] % PRIME
            basis.append(tuple(vector))
    return tuple(basis)


def normalized_vectors(rows, basis, n):
    pivot = next((i for i, row in enumerate(basis) if row[0]), None)
    if pivot is None:
        return
    scale = pow(basis[pivot][0], -1, PRIME)
    base = tuple(scale*x % PRIME for x in basis[pivot])
    directions = [tuple((x-direction[0]*y) % PRIME for x, y in zip(direction, base))
                  for i, direction in enumerate(basis) if i != pivot]
    if PRIME**len(directions) <= (PRIME-1)**(n-1):
        for coefficients in product(range(PRIME), repeat=len(directions)):
            vector = tuple((base[k]+sum(c*d[k] for c, d in zip(coefficients, directions))) % PRIME
                           for k in range(n))
            if all(vector):
                yield vector
    else:
        for tail in product(range(1, PRIME), repeat=n-1):
            vector = (1,)+tail
            if all(sum(a*b for a, b in zip(row, vector)) % PRIME == 0 for row in rows):
                yield vector


def evaluate(tensor, diagonal):
    return tuple(tuple(sum(int(c)*b for c, b in zip(entry, diagonal)) % PRIME
                       for entry in row) for row in tensor)


def gauges(matrix, target):
    n = len(matrix)
    if any((matrix[i][j] == 0) != (target[i][j] == 0)
           for i in range(n) for j in range(n)):
        return None
    a = tuple(pow(matrix[i][0], -1, PRIME) for i in range(n))
    d = tuple(pow(a[j]*matrix[j][j] % PRIME, -1, PRIME) for j in range(n))
    if any(a[i]*matrix[i][j]*d[j] % PRIME != target[i][j]
           for i in range(n) for j in range(n)):
        return None
    return a, d


def shear(x, f):
    return x ^ ((x & 1)*((1 << f)-2))


def probe(task):
    f, order_names, kinds = task
    started = time.monotonic()
    n = 1 << f
    orders = [tuple(range(n)) if name == 'natural'
              else tuple(shear(x, f) for x in range(n)) for name in order_names]
    scans = [S.ordered_scan(order, kind) for order, kind in zip(orders, kinds)]
    first = S.coefficient_tensor(scans[0], scans[1])
    target = S.zeta(f)
    zeros = [(i, j) for i in range(n) for j in range(n) if not target[i][j]]
    left_assignments = right_candidates = 0
    found = None
    for tail in product(range(1, PRIME), repeat=n-1):
        b = (1,)+tail
        left_assignments += 1
        middle = evaluate(first, b)
        last = S.coefficient_tensor(middle, scans[2])
        constraints = [last[i][j] for i, j in zeros]
        basis = kernel(constraints, n)
        for c in normalized_vectors(constraints, basis, n):
            right_candidates += 1
            actual = evaluate(last, c)
            repaired = gauges(actual, target)
            if repaired is not None:
                found = {'middle_diagonals': [b, c], 'outer_gauges': repaired,
                         'complete_field_matrix': actual,
                         'characteristic_zero_lift_not_asserted': True}
                break
        if found:
            break
    if found is None and left_assignments != (PRIME-1)**(n-1):
        raise AssertionError('An exhaustive negative skipped nonzero left diagonals')
    return {'f': f, 'order_names': order_names, 'kinds': kinds,
            'status': 'FINITE F5 CANDIDATE' if found else 'EXACT F5 UNIT-DIAGONAL EXCLUSION',
            'normalized_left_assignments': left_assignments,
            'nonzero_right_candidates': right_candidates, 'witness': found,
            'seconds': time.monotonic()-started,
            'chosen_order_and_Gaussian_unit_scope_only': True}


def controls():
    # Complete unit images: i->2 and (1+i)->3; 2 is invertible modulo5.
    if (2*2+1) % PRIME or {pow(3, k, PRIME) for k in range(4)} != {1, 2, 3, 4}:
        raise AssertionError('The Gaussian-unit reduction control failed')
    rows = ((1, 2, 0), (0, 1, 3))
    basis = kernel(rows, 3)
    vectors = list(normalized_vectors(rows, basis, 3))
    if vectors != [(1, 2, 1)]:
        raise AssertionError('The nonbinary kernel normalization failed')
    if list(normalized_vectors(((1, 0, 0),), kernel(((1, 0, 0),), 3), 3)):
        raise AssertionError('A forced-zero diagonal was accepted as a unit')
    positive = probe((2, ('natural',)*3, ('prefix',)*3))
    if positive['witness'] is None:
        raise AssertionError('The retained exact dyadic three-prefix example did not reduce modulo5')
    bad = [list(row) for row in positive['witness']['complete_field_matrix']]
    bad[0][1] = 1
    if gauges(bad, S.zeta(2)) is not None:
        raise AssertionError('A forbidden target response passed the complete matrix control')
    return {'unit_homomorphism_and_all_images_checked': True,
            'normalized_kernel_and_forced_zero_controls': True,
            'positive_Z2_reduction': positive,
            'corrupted_required_zero_rejected': True}


def tasks():
    return [(3, orders, kinds) for orders in
            [('natural', 'complement-shear', 'natural'),
             ('complement-shear', 'natural', 'complement-shear')]
            for kinds in [('prefix', 'difference', 'prefix'),
                          ('difference', 'prefix', 'difference')]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('Positive workers required')
    args.output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__).resolve(), Path(S.__file__).resolve(), Path(S.R.__file__).resolve()]
    hashes = {path.name: sha256(path.read_bytes()).hexdigest() for path in sources}
    protocol = {'started_utc': datetime.now(timezone.utc).isoformat(),
                'workers': args.workers, 'standard_library_only': True,
                'prime': PRIME, 'selected_tasks': tasks(), 'source_closure': hashes,
                'Gaussian_units_reduce_with_i_to2': True,
                'no_arbitrary_nonunit_complex_gauge_or_native_claim': True}
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, tasks()))
    control = controls()
    if hashes != {path.name: sha256(path.read_bytes()).hexdigest() for path in sources}:
        raise AssertionError('The source closure changed')
    receipt = {'status': 'PASS BOUNDED GAUSSIAN-UNIT HIGH-FLUX SCREEN',
               'rows': rows, 'controls': control,
               'finite_positive_does_not_automatically_lift': True,
               'no_native_or_multiplier_exponent_claim': True}
    (args.output/'certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'status': receipt['status'], 'cases': len(rows),
                      'excluded': sum(row['witness'] is None for row in rows),
                      'left_assignments': sum(row['normalized_left_assignments'] for row in rows)}, sort_keys=True))


if __name__ == '__main__':
    main()
