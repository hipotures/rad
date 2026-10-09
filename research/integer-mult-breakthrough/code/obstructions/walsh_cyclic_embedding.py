#!/usr/bin/env python3
"""Exact controls for a scoped full-volume cyclic convolution obstruction.

The analytical proof allows arbitrary nonzero input/output diagonal factors.
It excludes one complete cyclic or negacyclic convolution at the same dimension,
not multiple convolutions, restrictions, extensions or the nonzero field core.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import permutations
import json
from math import lcm
from pathlib import Path
import time


def rank(columns):
    pivots = {}
    for vector in columns:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot in pivots:
                vector ^= pivots[pivot]
            else:
                pivots[pivot] = vector
                break
    return len(pivots)


def linear_table(columns):
    table = [0] * (1 << len(columns))
    for x in range(1, len(table)):
        bit = x & -x
        table[x] = table[x ^ bit] ^ columns[bit.bit_length() - 1]
    return table


def cycle_type(perm):
    visited = set()
    lengths = []
    for start in range(len(perm)):
        if start in visited:
            continue
        vertex, length = start, 0
        while vertex not in visited:
            visited.add(vertex)
            length += 1
            vertex = perm[vertex]
        if vertex != start:
            raise AssertionError('A claimed address map is not a permutation')
        lengths.append(length)
    return tuple(sorted(lengths))


def hadamard(x, y):
    return -1 if (x & y).bit_count() & 1 else 1


def affine_columns(perm, bits):
    origin = perm[0]
    columns = tuple(perm[1 << j] ^ origin for j in range(bits))
    table = linear_table(columns)
    return columns if all(perm[x] == table[x] ^ origin for x in range(len(perm))) else None


def automorphism_control(table, bits):
    size = len(table)
    inverse = [0] * size
    for x, y in enumerate(table):
        inverse[y] = x
    # Columns of A^{-T} are obtained from rows of A^{-1}.
    dual = tuple(sum(((inverse[1 << k] >> j) & 1) << k
                     for k in range(bits)) for j in range(bits))
    dual_table = linear_table(dual)
    b, c = size - 1, 1
    coefficients = 0
    for x in range(size):
        row = hadamard(table[x], c)
        for y in range(size):
            col = hadamard(b, dual_table[y] ^ c)
            actual = row * col * hadamard(table[x] ^ b, dual_table[y] ^ c)
            if actual != hadamard(x, y):
                raise AssertionError('An affine signed operator automorphism failed')
            coefficients += 1
    return coefficients


def probe(bits):
    started = time.monotonic()
    size = 1 << bits
    order_bound = 1 << bits.bit_length()  # ceil(log2(bits+1))
    counts, orders = Counter(), Counter()
    invertible, coefficient_controls = 0, 0
    # Enumerate each binary matrix exactly once through its ordered columns.
    for packed in range(1 << (bits * bits)):
        columns = tuple((packed >> (bits * j)) & (size - 1) for j in range(bits))
        if rank(columns) != bits:
            continue
        table = linear_table(columns)
        invertible += 1
        # Complete operator controls for a deterministic sample of matrices;
        # every affine permutation below is still included in cycle enumeration.
        if invertible <= 64:
            coefficient_controls += automorphism_control(table, bits)
        for offset in range(size):
            perm = tuple(y ^ offset for y in table)
            shape = cycle_type(perm)
            counts[shape] += 1
            order = lcm(*shape)
            orders[order] += 1
            if order & (order - 1) == 0 and order > order_bound:
                raise AssertionError('The augmented unipotent order bound failed')
    expected = 1
    for j in range(bits):
        expected *= size - (1 << j)
    if invertible != expected or sum(counts.values()) != size * expected:
        raise AssertionError('The complete GL/AGL enumeration omitted an address map')
    full_cycles = counts[(size,)]
    if bits >= 3 and full_cycles:
        raise AssertionError('A prohibited full cyclic affine permutation exists')
    increment = tuple((x + 1) % size for x in range(size))
    if (affine_columns(increment, bits) is not None) != (bits <= 2):
        raise AssertionError('The binary increment negative control changed scope')
    return dict(bits=bits, size=size, invertible_linear_maps=invertible,
                affine_maps=size * invertible, complete_full_cycle_count=full_cycles,
                permutation_order_counts={str(k): v for k, v in sorted(orders.items())},
                maximum_power_two_order=max(k for k in orders if k & (k - 1) == 0),
                augmented_unipotent_order_bound=order_bound,
                operator_coefficients_checked=coefficient_controls,
                increment_is_affine=bits <= 2, seconds=time.monotonic() - started)


def four_coordinate_positive_control():
    first_row = (1, 1, 1, -1)
    cyclic = [[first_row[(y - x) % 4] for y in range(4)] for x in range(4)]
    for rows in permutations(range(4)):
        for cols in permutations(range(4)):
            col_signs = [cyclic[0][y] * hadamard(rows[0], cols[y]) for y in range(4)]
            row_signs = [cyclic[x][0] * hadamard(rows[x], cols[0]) * col_signs[0]
                         for x in range(4)]
            if all(row_signs[x] * col_signs[y] * hadamard(rows[x], cols[y]) == cyclic[x][y]
                   for x in range(4) for y in range(4)):
                return dict(status='PASS FOUR-COORDINATE CYCLIC EXCEPTION',
                            first_row=first_row, rows=rows, cols=cols,
                            row_signs=row_signs, col_signs=col_signs)
    raise AssertionError('The dimension-four cyclic positive control was lost')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or args.output and args.output.exists():
        raise ValueError('Positive workers and a fresh optional output are required')
    source = Path(__file__).resolve()
    digest = sha256(source.read_bytes()).hexdigest()
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    workers=args.workers, source_sha256=digest, seed=None,
                    input='Exhaustive binary matrix and offset generator; exact signed Walsh characters',
                    scope='Finite controls for a separately written all-size monomial/cyclic obstruction')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, [1, 2, 3] if args.bounded else [1, 2, 3, 4]))
    exception = four_coordinate_positive_control()
    if sha256(source.read_bytes()).hexdigest() != digest:
        raise ValueError('Source changed during exact enumeration')
    summary = dict(status='PASS SCOPED CYCLIC EMBEDDING CONTROLS', cases=rows,
                   four_coordinate_exception=exception,
                   no_single_full_cyclic_or_negacyclic_embedding_for_bits_at_least_three=True,
                   complete_native_route=False, new_multiplier_exponent=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'], dimensions=len(rows),
                         affine_maps=sum(r['affine_maps'] for r in rows))))


if __name__ == '__main__':
    main()
