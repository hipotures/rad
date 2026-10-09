#!/usr/bin/env python3
"""Four-entry obstruction for sums of fixed high-flux two-scan responses.

Every response S diag(w) T with S,T natural/complement-shear prefix or
difference has zero functional at rows5,7/columns0,2 for N>=16. Zeta's
functional is1. Written proof covers all complex coefficients, including
singular diagonals; the finite integer generator check is not formal proof.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def position(x, n, name):
    return x if name == 'natural' else x ^ ((x & 1)*(n-2))


def scan_entry(row, col, n, name, kind):
    pr, pc = position(row, n, name), position(col, n, name)
    if kind == 'prefix':
        return int(pr >= pc)
    return int(row == col)-int(pr == pc+1)


CELLS = ((5, 0, 1), (5, 2, -1), (7, 0, -1), (7, 2, 1))
SCANS = tuple(product(('natural', 'complement-shear'), ('prefix', 'difference')))


def generator_functional(n, left, right, k, cells=CELLS):
    return sum(sign*scan_entry(row, k, n, *left)*scan_entry(k, col, n, *right)
               for row, col, sign in cells)


def probe(f):
    if f < 4:
        raise ValueError('The all-size obstruction requires f>=4')
    n = 1 << f
    checks = 0
    for left, right in product(SCANS, repeat=2):
        for k in range(n):
            if generator_functional(n, left, right, k):
                raise AssertionError('A complete weighted response generator violates the separator')
            checks += 1
    target = sum(sign*int((col & row) == col) for row, col, sign in CELLS)
    if target != 1:
        raise AssertionError('The fixed-label zeta separator stopped discriminating')
    wrong = tuple((row, col, -sign if (row, col) == (7, 2) else sign)
                  for row, col, sign in CELLS)
    if not any(generator_functional(n, left, right, k, wrong)
               for left, right in product(SCANS, repeat=2) for k in range(n)):
        raise AssertionError('The changed functional negative did not discriminate')
    return {'f': f, 'N': n, 'all_complete_generator_coefficients_checked': checks,
            'all_responses_functional': 0, 'target_functional': target,
            'changed_functional_rejected': True,
            'arbitrary_sum_and_complex_middle_coefficients_in_written_scope': True,
            'outside_diagonal_gauges_or_other_orders_not_excluded': True}


def small_width_escape():
    n = 8
    found = next(((left, right, k, generator_functional(n, left, right, k))
                  for left, right in product(SCANS, repeat=2) for k in range(n)
                  if generator_functional(n, left, right, k)), None)
    if found is None:
        raise AssertionError('The f3 positive-scope boundary ceased to discriminate')
    return {'f': 3, 'one_response_outside_zero_functional': found,
            'invalid_f3_extension_rejected': True}


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
    tasks = (4, 5) if args.bounded else (4, 5, 6, 8, 10)
    protocol = {'started_utc': datetime.now(timezone.utc).isoformat(),
                'source_sha256': original, 'workers': args.workers,
                'standard_library_only': True, 'f_tasks': tasks}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, tasks))
    controls = small_width_escape()
    if sha256(source.read_bytes()).hexdigest() != original:
        raise AssertionError('The source changed during verification')
    receipt = {'status': 'PASS FOUR-ENTRY TWO-SCAN RESPONSE OBSTRUCTION',
               'protocol': protocol, 'rows': rows, 'controls': controls,
               'written_all_size_proof_not_formally_verified': True,
               'no_native_or_multiplier_exponent_claim': True}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'status': receipt['status'], 'widths': tasks,
                      'exact_generator_checks': sum(row['all_complete_generator_coefficients_checked']
                                                    for row in rows)}, sort_keys=True))


if __name__ == '__main__':
    main()
