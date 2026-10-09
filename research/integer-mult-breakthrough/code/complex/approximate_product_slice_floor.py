#!/usr/bin/env python3
"""Exact controls for a coefficient-robust direct product wire floor.

Every input/output basis slice of q_s is H/D for a signed Hadamard H.
An entrywise Gaussian L1 error smaller than 1/D^2 preserves slice rank.
The analytical implication concerns fixed separable bilinear formulas;
shared circuits, input-dependent rounding and native costs remain outside.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import time


SOURCE = (((1, 1), (-1, 1)), ((1, -1), (1, 1)))
OUTPUT = (((1, 1), (1, -1)), ((-1, 1), (1, 1)))
SEED = 202610090550


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def exact_div(a, b):
    if b == (0, 0):
        raise AssertionError('Gaussian fraction-free divisor is zero')
    numerator = mul(a, (b[0], -b[1]))
    norm = b[0] * b[0] + b[1] * b[1]
    if numerator[0] % norm or numerator[1] % norm:
        raise AssertionError('Gaussian Bareiss division was not exact')
    return (numerator[0] // norm, numerator[1] // norm)


def determinant(matrix):
    n = len(matrix)
    a = [list(row) for row in matrix]
    previous = (1, 0)
    sign = 1
    for k in range(n - 1):
        pivot_row = next((j for j in range(k, n) if a[j][k] != (0, 0)), None)
        if pivot_row is None:
            return (0, 0)
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = exact_div(sub(mul(pivot, a[i][j]),
                                        mul(a[i][k], a[k][j])), previous)
            a[i][k] = (0, 0)
        previous = pivot
    return (sign * a[-1][-1][0], sign * a[-1][-1][1])


def tensor_slice(s, coordinate, family):
    local = SOURCE if family != 'output' else OUTPUT
    # Rows/columns are little-endian coordinates. Local factors are direct
    # two-by-two slice matrices, independent of the producer's parity formula.
    D = 1 << s
    return [[product_sign(local[(coordinate >> j) & 1][(row >> j) & 1][(col >> j) & 1]
                          for j in range(s))
             for col in range(D)] for row in range(D)]


def product_sign(values):
    result = 1
    for value in values:
        result *= value
    return result


def gram_control(h):
    D = len(h)
    negative = [sum(1 << j for j, value in enumerate(row) if value < 0) for row in h]
    for i, left in enumerate(negative):
        for j, right in enumerate(negative):
            if D - 2 * (left ^ right).bit_count() != (D if i == j else 0):
                raise AssertionError('literal slice lost its signed Hadamard Gram')


def probe(task):
    s, family = task
    D = 1 << s
    family_index = ('left_input', 'right_input', 'output').index(family)
    coordinate = (D // 3 + family_index) % D
    h = tensor_slice(s, coordinate, family)
    gram_control(h)
    rng = random.Random(SEED + 100 * s + family_index)
    delta = [[(rng.choice((-1, 1)), rng.choice((-1, 1))) for _ in range(D)]
             for _ in range(D)]
    # M=H/D and E=delta/(4D^2), so each coefficient's complex L1 error
    # is exactly 1/(2D^2). The inverse of M is H^T without an extra scale.
    denominator = 4 * D * D
    inverse_error = [[tuple(sum(h[k][i] * delta[k][j][part] for k in range(D))
                            for part in range(2)) for j in range(D)] for i in range(D)]
    row_norm_numerators = [sum(abs(value[0]) + abs(value[1]) for value in row)
                           for row in inverse_error]
    if max(row_norm_numerators) * 2 > denominator:
        raise AssertionError('inverse-error row norm exceeded the universal half bound')
    perturbed_numerator = [[add((4 * D * h[i][j], 0), delta[i][j])
                           for j in range(D)] for i in range(D)]
    det = determinant(perturbed_numerator)
    if det == (0, 0):
        raise AssertionError('small coefficient perturbation made a slice singular')
    # At error 1/D the all-zero slice is a genuine low-accuracy counterexample.
    if determinant([[(0, 0)] * D for _ in range(D)]) != (0, 0):
        raise AssertionError('zero-slice low-accuracy negative was not singular')
    if determinant([[(h[i][j], 0) for j in range(D)] for i in range(D)]) == (0, 0):
        raise AssertionError('unperturbed literal slice determinant is zero')
    return dict(packet_axes=s, dimension=D, family=family, coordinate=coordinate,
                seed=SEED + 100 * s + family_index,
                perturbation_grid_bits=2 * s + 2,
                coefficient_L1_error=dict(numerator=1, denominator=2 * D * D),
                inverse_error_L1_row_norm=dict(numerator=max(row_norm_numerators),
                                               denominator=denominator),
                universal_row_norm_at_most_half=True,
                perturbed_clear_denominator=denominator,
                perturbed_integer_determinant=[str(det[0]), str(det[1])],
                perturbed_slice_rank=D, exact_gaussian_divisions=True,
                low_accuracy_zero_slice=dict(coefficient_error_denominator=D,
                                              slice_rank=0),
                scope='A seeded complete perturbed slice is verified exactly. All-coordinate/all-perturbation rank preservation is the analytical norm lemma, not a finite enumeration.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    source = sha256(Path(__file__).read_bytes()).hexdigest()
    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    widths = [1, 2] if args.bounded else [1, 2, 4, 6]
    tasks = [(s, family) for s in widths for family in ('left_input', 'right_input', 'output')]
    if args.workers == 1:
        cases = list(map(probe, tasks))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, tasks))
    if sha256(Path(__file__).read_bytes()).hexdigest() != source:
        raise AssertionError('source changed during the run')
    result = dict(status='PASS EXACT COEFFICIENT-ROBUST PRODUCT SLICE CONTROLS',
                  source_sha256=source, started_utc=started_utc,
                  completed_utc=datetime.now(timezone.utc).isoformat(),
                  workers=args.workers, bounded=args.bounded, cases=cases,
                  seconds=time.monotonic() - started,
                  scope='Fixed bilinear coefficient approximation and direct rank-one form incidences; not input-dependent rounding, shared circuit time, native implementation or a new kappa.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], cases=len(cases),
                          largest_slice=max(c['dimension'] for c in cases),
                          seconds=result['seconds'])), flush=True)


if __name__ == '__main__':
    main()
