#!/usr/bin/env python3
"""Exact two ordered-scan products, with invertible diagonal gauges.

The only searched unknown is the middle diagonal. Necessary zero-pattern
conditions are exact rational linear equations, hence also apply over C.
No native routing bill or borrowed-bank/projection semantics are assumed.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import time

import rational_frame_completion as R


def zeta(f, inverse=False):
    size = 1 << f
    return tuple(tuple(((-1) ** ((i ^ j).bit_count()) if inverse else 1)
                       if (i & j) == j else 0 for j in range(size))
                 for i in range(size))


def ordered_scan(order, kind):
    n = len(order)
    if sorted(order) != list(range(n)) or kind not in ('prefix', 'difference'):
        raise ValueError('A complete order and prefix/difference kind are required')
    positions = [0] * n
    for position, address in enumerate(order):
        positions[address] = position
    if kind == 'prefix':
        return tuple(tuple(int(positions[j] <= positions[i]) for j in range(n)) for i in range(n))
    result = [[0] * n for unused in range(n)]
    for position, address in enumerate(order):
        result[address][address] = 1
        if position:
            result[address][order[position - 1]] = -1
    return tuple(tuple(row) for row in result)


def multiply(a, b):
    columns = tuple(zip(*b))
    return tuple(tuple(sum(x * y for x, y in zip(row, column)) for column in columns) for row in a)


def coefficient_tensor(first, second):
    n = len(first)
    return tuple(tuple(tuple(first[i][k] * second[k][j] for k in range(n)) for j in range(n))
                 for i in range(n))


def evaluate(tensor, middle):
    return tuple(tuple(sum(c * b for c, b in zip(entry, middle)) for entry in row) for row in tensor)


def response(functional, nullspace):
    return tuple(sum(a * b for a, b in zip(functional, direction)) for direction in nullspace)


def zero_pattern(first, second, target):
    """Exact necessary equations and a rational forced-zero certificate."""
    n = len(first)
    tensor = coefficient_tensor(first, second)
    constraints = [tensor[i][j] for i in range(n) for j in range(n) if target[i][j] == 0]
    nullspace = R.kernel(constraints, n)
    # A zero middle diagonal destroys invertibility. The basis check is exact.
    for k in range(n):
        if all(direction[k] == 0 for direction in nullspace):
            return dict(status='EXACT ZERO-PATTERN OBSTRUCTION', dimension=len(nullspace),
                        reason='forced_zero_middle_diagonal', witness=[k],
                        nullspace=R.encoded(nullspace)), tensor, nullspace
    for i in range(n):
        for j in range(n):
            if target[i][j] and not any(response(tensor[i][j], nullspace)):
                return dict(status='EXACT ZERO-PATTERN OBSTRUCTION', dimension=len(nullspace),
                            reason='forced_zero_required_target_entry', witness=[i, j],
                            nullspace=R.encoded(nullspace)), tensor, nullspace
    return dict(status='ZERO-PATTERN NECESSARY TEST SURVIVES', dimension=len(nullspace)), tensor, nullspace


def gauged_zeta(matrix, target):
    """Find the uniquely normalized external row/column gauges, if they fit."""
    n = len(matrix)
    if any((matrix[i][j] == 0) != (target[i][j] == 0) for i in range(n) for j in range(n)):
        return None
    # All target column-zero entries and diagonal entries are one.
    row = tuple(matrix[i][0] for i in range(n))
    column = tuple(matrix[j][j] / row[j] for j in range(n))
    if any(matrix[i][j] != row[i] * column[j] * target[i][j] for i in range(n) for j in range(n)):
        return None
    return row, column


def probe_order(task):
    first_order = tuple(task)
    started = time.monotonic()
    target = zeta(2)
    rows = []
    for second_order in permutations(range(4)):
        for kinds in (('prefix', 'difference'), ('difference', 'prefix')):
            first, second = [ordered_scan(order, kind) for order, kind in zip((first_order, second_order), kinds)]
            evidence, tensor, nullspace = zero_pattern(first, second, target)
            row = dict(first_order=first_order, second_order=second_order, kinds=kinds, **evidence)
            # This bounded rational discovery is not an exhaustive nonlinear
            # gauge proof. Its exact successes must replay the complete matrix.
            if evidence['status'] != 'EXACT ZERO-PATTERN OBSTRUCTION':
                found = None
                for coefficients in product((-2, -1, 1, 2), repeat=len(nullspace)):
                    middle = tuple(sum(c * direction[k] for c, direction in zip(coefficients, nullspace)) for k in range(4))
                    if not all(middle):
                        continue
                    matrix = evaluate(tensor, middle)
                    gauges = gauged_zeta(matrix, target)
                    if gauges is not None:
                        found = dict(middle=R.encoded([middle])[0], row=R.encoded([gauges[0]])[0],
                                     column=R.encoded([gauges[1]])[0])
                        break
                row.update(status='EXACT RATIONAL GAUGE FACTORIZATION' if found else 'UNRESOLVED GAUGE COMPATIBILITY',
                           witness_gauges=found, bounded_discovery_coefficient_values=[-2, -1, 1, 2])
            rows.append(row)
    return dict(first_order=first_order, rows=rows, seconds=time.monotonic() - started)


def interval_blocks(bits):
    return sum(bit and (i == 0 or not bits[i - 1]) for i, bit in enumerate(bits))


def structural_controls():
    sizes = []
    for f in range(1, 8):
        Z, mobius = zeta(f), zeta(f, inverse=True)
        size = 1 << f
        if multiply(Z, mobius) != tuple(tuple(int(i == j) for j in range(size)) for i in range(size)):
            raise AssertionError('The exact complete Mobius inverse failed')
        if max(sum(entry != 0 for entry in row) for row in mobius) != size:
            raise AssertionError('The inverse full-row support witness failed')
        if max(sum(entry != 0 for entry in row) for row in Z) != size:
            raise AssertionError('The forward full-row support witness failed')
        sizes.append(dict(f=f, target_full_row_support=size, two_sparse_scan_bound=4,
                          all_prefix_or_all_difference_two_scan_excluded=f >= 3,
                          coordinate_filter_patterns=size, interval_pattern_bound=2*f+1,
                          mixed_two_scan_interval_excluded=f >= 3))
    # Arbitrary signed/cancelling rational middle coefficients still yield
    # at most one interval. This checks both orientations and reversed orders.
    interval_cases = 0
    for first_order in permutations(range(4)):
        for second_order in permutations(range(4)):
            L, D = ordered_scan(first_order, 'prefix'), ordered_scan(second_order, 'difference')
            tensor = coefficient_tensor(L, D)
            matrix = evaluate(tensor, (Q(1), Q(-2), Q(1), Q(3)))
            for j in range(4):
                if interval_blocks([matrix[i][j] != 0 for i in first_order]) > 1:
                    raise AssertionError('The mixed column interval lemma failed')
                interval_cases += 1
            tensor = coefficient_tensor(ordered_scan(first_order, 'difference'), ordered_scan(second_order, 'prefix'))
            matrix = evaluate(tensor, (Q(1), Q(-2), Q(1), Q(3)))
            for i in range(4):
                if interval_blocks([matrix[i][j] != 0 for j in second_order]) > 1:
                    raise AssertionError('The mixed row interval lemma failed')
                interval_cases += 1
    L, D = ordered_scan((0, 2, 1, 3), 'prefix'), ordered_scan((0, 2, 1, 3), 'difference')
    if multiply(L, D) != tuple(tuple(int(i == j) for j in range(4)) for i in range(4)):
        raise AssertionError('The literal ordered scan inverse failed')
    bad_D = tuple(tuple(abs(entry) for entry in row) for row in D)
    if multiply(L, bad_D) == multiply(L, D):
        raise AssertionError('Omitted difference sign escaped the inverse control')
    # Deliberately corrupt a proven zero-pattern kernel and recheck all equations.
    evidence, tensor, nullspace = zero_pattern(L, ordered_scan((3, 1, 2, 0), 'difference'), zeta(2))
    if not nullspace:
        raise AssertionError('The kernel corruption control requires a nonempty kernel')
    wrong = tuple(Q(i == 0) for i in range(4))
    constraints = [tensor[i][j] for i in range(4) for j in range(4) if zeta(2)[i][j] == 0]
    if all(sum(a * b for a, b in zip(row, wrong)) == 0 for row in constraints):
        # Choose a nonzero constraint explicitly rather than assume an index.
        witness = next(row for row in constraints if any(row))
        wrong = tuple(Q(i == next(k for k, entry in enumerate(witness) if entry)) for i in range(4))
    if all(sum(a * b for a, b in zip(row, wrong)) == 0 for row in constraints):
        raise AssertionError('Corrupt zero-pattern direction was accepted')
    return dict(status='PASS ORDERED SCAN STRUCTURAL CONTROLS', sizes=sizes,
                mixed_interval_support_cases=interval_cases,
                negative_controls=['omitted_difference_sign', 'corrupt_zero_pattern_direction'],
                scope='Exact algebraic one-bank scans only; no native routing or dirty-bank projection')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('Positive workers required')
    sources = (Path(__file__).resolve(), Path(R.__file__).resolve())
    hashes = {path.name: sha256(path.read_bytes()).hexdigest() for path in sources}
    args.output.mkdir(parents=True, exist_ok=False)
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_closure=hashes,
                    workers=args.workers, stdlib_only=True, complete_permutations=24,
                    f=2, middle_diagonal_invertible=True, external_row_column_gauges_invertible=True,
                    full_field_scope='Q-linear zero-pattern obstructions also hold over Q(i) and C',
                    discovery_scope='Bounded rational gauge choices for surviving necessary tests only',
                    native_or_supplier_claim=False)
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        groups = list(pool.map(probe_order, permutations(range(4))))
    controls = structural_controls()
    if hashes != {path.name: sha256(path.read_bytes()).hexdigest() for path in sources}:
        raise AssertionError('The effective source closure changed')
    rows = [row for group in groups for row in group['rows']]
    counts = dict(Counter(row['status'] for row in rows))
    certificate = dict(status='PASS TWO-SCAN NECESSARY PATTERN DISCRIMINATOR', counts=counts,
                       complete_mixed_order_cases=len(rows), structural=controls, groups=groups,
                       unrestricted_three_scan_or_dirty_bank_models_not_excluded=True)
    (args.output / 'certificate.json').write_text(json.dumps(certificate, indent=2) + '\n')
    print(json.dumps(dict(status=certificate['status'], counts=counts,
                         complete_mixed_order_cases=len(rows), interval_controls=controls['mixed_interval_support_cases']), sort_keys=True))


if __name__ == '__main__':
    main()
