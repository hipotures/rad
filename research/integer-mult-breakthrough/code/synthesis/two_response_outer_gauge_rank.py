#!/usr/bin/env python3
"""Rank-three target versus rank-two fixed two-response subblocks.

For N>=32, all natural/complement-shear two-scan response sums have
row-plus-column separable restrictions at rows9,11,13/columns0,2,4.
Common invertible outside diagonals cannot change rank two to rank three.
This does not cover independent gauges per summand or different orders.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

ROWS, COLUMNS = (9, 11, 13), (0, 2, 4)
SCANS = tuple(product(('natural', 'complement-shear'), ('prefix', 'difference')))


def position(x, n, order):
    return x if order == 'natural' else x ^ ((x & 1)*(n-2))


def entry(row, col, n, order, kind):
    r, c = position(row, n, order), position(col, n, order)
    return int(r >= c) if kind == 'prefix' else int(row == col)-int(r == c+1)


def det3(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))


def probe(f):
    if f < 5:
        raise ValueError('The uniform subblock obstruction requires f>=5')
    n = 1 << f
    left_bound = set(range(8, 14)) | {n-10, n-12, n-14}
    right_bound = set(range(6)) | {n-1, n-3, n-5}
    if left_bound & right_bound:
        raise AssertionError('The stated whole support bounds are not disjoint')
    checks = 0
    for scan in SCANS:
        for row in ROWS[1:]:
            actual = {k for k in range(n) if entry(row, k, n, *scan) != entry(ROWS[0], k, n, *scan)}
            if not actual <= left_bound:
                raise AssertionError('A complete left row difference leaves the support bound')
        for col in COLUMNS[1:]:
            actual = {k for k in range(n) if entry(k, col, n, *scan) != entry(k, COLUMNS[0], n, *scan)}
            if not actual <= right_bound:
                raise AssertionError('A complete right column difference leaves the support bound')
    for left, right in product(SCANS, repeat=2):
        for k in range(n):
            a = [[entry(row, k, n, *left)*entry(k, col, n, *right)
                  for col in COLUMNS] for row in ROWS]
            if any(a[i][j]-a[i][0]-a[0][j]+a[0][0]
                   for i in (1, 2) for j in (1, 2)):
                raise AssertionError('A response coefficient violates the complete separability equations')
            checks += 4
    target = [[int((col & row) == col) for col in COLUMNS] for row in ROWS]
    if det3(target) != 1:
        raise AssertionError('The complete fixed-label target minor lost rank three')
    left_gauge, right_gauge = (1, -2, 4), (2, 1, -1)
    changed = [[left_gauge[i]*x*right_gauge[j] for j, x in enumerate(row)]
               for i, row in enumerate(target)]
    if det3(changed) != det3(target)*(-8)*(-2):
        raise AssertionError('Common nonzero diagonal gauges changed the minor rank')
    singular = [row[:] for row in target]
    singular[0] = [0, 0, 0]
    if det3(singular) != 0:
        raise AssertionError('The zero outside-gauge scope negative did not discriminate')
    return {'f': f, 'N': n, 'rows': ROWS, 'columns': COLUMNS,
            'complete_generator_separability_equations': checks,
            'left_support_bound': sorted(left_bound), 'right_support_bound': sorted(right_bound),
            'all_response_sums_subblock_rank_at_most': 2,
            'target_minor_determinant': 1,
            'common_nonzero_outside_diagonal_rank_preserved': True,
            'zero_outside_gauge_scope_control': True}


def threshold_control():
    n = 16
    if not any((entry(row, k, n, *left)-entry(ROWS[0], k, n, *left))
               *(entry(k, col, n, *right)-entry(k, COLUMNS[0], n, *right))
               for left, right in product(SCANS, repeat=2)
               for row in ROWS[1:] for col in COLUMNS[1:] for k in range(n)):
        raise AssertionError('The invalid f4 extension did not discriminate')
    return {'invalid_f4_extension_rejected': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('Positive workers required')
    if args.output and args.output.exists():
        raise FileExistsError('A fresh optional output file is required')
    source = Path(__file__).resolve()
    original = sha256(source.read_bytes()).hexdigest()
    tasks = (5, 6) if args.bounded else (5, 6, 7, 10)
    protocol = {'started_utc': datetime.now(timezone.utc).isoformat(),
                'source_sha256': original, 'workers': args.workers,
                'standard_library_only': True, 'f_tasks': tasks}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, tasks))
    if sha256(source.read_bytes()).hexdigest() != original:
        raise AssertionError('The source changed during verification')
    receipt = {'status': 'PASS COMMON-OUTER-GAUGE TWO-RESPONSE RANK CONTROLS',
               'protocol': protocol, 'rows': rows, 'threshold_control': threshold_control(),
               'written_all_size_proof_not_formally_verified': True,
               'no_native_or_multiplier_exponent_claim': True}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'status': receipt['status'], 'widths': tasks,
                      'exact_generator_equations': sum(row['complete_generator_separability_equations']
                                                       for row in rows)}, sort_keys=True))


if __name__ == '__main__':
    main()
