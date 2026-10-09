#!/usr/bin/env python3
"""Exact controls for a scoped prefix-affine Singer routing obstruction.

This is a mathematical discriminator, not a tape-time lower bound or a
paid implementation of the multiplicative finite-field permutation.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time


def multiply(a, b, polynomial, degree):
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a >> degree:
            a ^= polynomial
    return out


def primitive_cycle(degree):
    """Full nonzero cycle certifies both field and primitive element."""
    capacity = 1 << degree
    for polynomial in range(capacity | 1, capacity << 1, 2):
        values = []
        seen = set()
        a = 1
        while a and a not in seen:
            seen.add(a)
            values.append(a)
            a = multiply(a, 2, polynomial, degree)
        if len(values) == capacity - 1 and a == 1:
            if seen != set(range(1, capacity)):
                raise AssertionError("The purported primitive cycle is incomplete")
            return polynomial, values
    raise AssertionError("No primitive cycle found in bounded exhaustive search")


def xor_all(values):
    out = 0
    for value in values:
        out ^= value
    return out


def affine_witness(mapping, start, width):
    """Check all vertices, keeping an explicit failed affine equation."""
    origin = mapping[start]
    deltas = [mapping[start + (1 << j)] ^ origin for j in range(width)]
    for i in range(1 << width):
        predicted = origin ^ xor_all(deltas[j] for j in range(width) if i >> j & 1)
        if mapping[start + i] != predicted:
            return dict(input=start + i, actual=mapping[start + i],
                        affine_prediction=predicted, start=start, width=width)
    return None


def cube_vertices(base, bits):
    return [base | sum(1 << bit for j, bit in enumerate(bits) if mask >> j & 1)
            for mask in range(1 << len(bits))]


def check(degree):
    started = time.perf_counter()
    polynomial, powers = primitive_cycle(degree)
    capacity = 1 << degree
    mapping = powers + [0]
    inverse = [0] * capacity
    for i, value in enumerate(mapping):
        inverse[value] = i
    if any(mapping[inverse[x]] != x or inverse[mapping[x]] != x for x in range(capacity)):
        raise AssertionError("Finite routing permutation or inverse is incorrect")

    prefix = []
    failures = []
    for width in range(2, degree + 1):
        rejected = 0
        for start in range(0, capacity, 1 << width):
            witness = affine_witness(mapping, start, width)
            if witness:
                rejected += 1
                if start == capacity - (1 << width):
                    failures.append(witness)
        expected = capacity >> width
        if degree >= 3 and rejected != expected:
            raise AssertionError("A full aligned prefix chunk escaped the obstruction")
        if degree == 2 and rejected:
            raise AssertionError("The degree-two positive boundary was lost")
        prefix.append(dict(width=width, complete_chunks=expected, non_affine_chunks=rejected))

    checked_cubes = 0
    cube_digest = sha256()
    for bits in combinations(range(degree), 2):
        mask = sum(1 << bit for bit in bits)
        for base in range(capacity):
            if base & mask:
                continue
            vertices = cube_vertices(base, bits)
            if capacity - 1 in vertices:
                continue
            actual = xor_all(mapping[i] for i in vertices)
            expected = powers[base]
            for bit in bits:
                expected = multiply(expected, 1 ^ powers[1 << bit], polynomial, degree)
            if actual != expected or not actual:
                raise AssertionError("Nonexceptional binary cube product formula failed")
            checked_cubes += 1
            cube_digest.update(f'{base},{bits}:{actual};'.encode())

    final_four = xor_all(mapping[-4:])
    analytic_four = multiply(powers[-3], 1 ^ powers[1] ^ powers[2], polynomial, degree)
    if final_four != analytic_four:
        raise AssertionError("The separately charged zero-border cube formula failed")
    if (final_four == 0) != (degree == 2):
        raise AssertionError("The primitive-order-three exceptional boundary failed")
    # Checking just the XOR of the whole field would falsely suggest affinity.
    if xor_all(mapping) != 0 or (degree >= 3 and affine_witness(mapping, 0, degree) is None):
        raise AssertionError("The whole-field parity false-positive control failed")

    # A reference payload oracle and its inverse: no operational cost is inferred.
    records = [(i + 1, -(3 * i + 1)) for i in range(capacity)]
    routed = [None] * capacity
    for i, record in enumerate(records):
        routed[mapping[i]] = record
    restored = [routed[mapping[i]] for i in range(capacity)]
    if restored != records:
        raise AssertionError("Complete reference payload inverse failed")
    first_bad = affine_witness(mapping, 0, 2)
    if degree >= 3:
        if first_bad is None or records[first_bad['input']] == records[0]:
            raise AssertionError("The unpaid local-affine payload corruption lost its witness")
    return dict(degree=degree, capacity=capacity, primitive_polynomial=polynomial,
                complete_nonzero_cycle=capacity-1, prefix_chunks=prefix,
                final_chunk_witnesses=failures, nonexceptional_two_cubes=checked_cubes,
                cube_sha256=cube_digest.hexdigest(), final_four_xor=final_four,
                primitive_order_three_boundary=(degree == 2),
                complete_payload_records=capacity,
                false_whole_cube_affinity_rejected=(degree >= 3),
                unpaid_affine_payload_witness=first_bad,
                seconds=time.perf_counter()-started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError('Invalid worker count')
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh output path')
    degrees = [2, 3, 4] if args.bounded else [2, 3, 6, 8, 10, 12]
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        outcomes = list(pool.map(check, degrees))
    result = dict(status='PASS EXACT PREFIX-AFFINE ROUTING CONTROLS',
                  recorded_utc=datetime.now(timezone.utc).isoformat(),
                  workers=args.workers, degrees=degrees, cases=outcomes,
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  seconds=time.perf_counter()-started,
                  scope='Nonzero-power ordering with zero last cannot map any aligned binary prefix chunk of size at least four affinely at degree at least three. This does not exclude nonlinear guarded routing, other orderings or all tape algorithms. Reference payload movement is an oracle, not a paid program.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as f:
            f.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'workers', 'seconds', 'scope')}))


if __name__ == '__main__':
    main()
