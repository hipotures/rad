#!/usr/bin/env python3
"""Exact minimal nondegenerate completion inside a rational future cap.

The constructor works for any symmetric rational form in characteristic zero.
The signature of I-J/9 bounds every rational radical by one when h>9.
Odd local-ring projector/prime/routing costs are separate obligations.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random
import time


def rref(rows, width):
    matrix = [list(map(Q, row)) for row in rows]
    if any(len(row) != width for row in matrix):
        raise ValueError('Rational frame rows have inconsistent width')
    pivot, pivots = 0, []
    for column in range(width):
        source = next((i for i in range(pivot, len(matrix)) if matrix[i][column]), None)
        if source is None:
            continue
        matrix[pivot], matrix[source] = matrix[source], matrix[pivot]
        scale = matrix[pivot][column]
        matrix[pivot] = [x / scale for x in matrix[pivot]]
        for i in range(len(matrix)):
            if i != pivot and matrix[i][column]:
                factor = matrix[i][column]
                matrix[i] = [x - factor * y for x, y in zip(matrix[i], matrix[pivot])]
        pivots.append(column)
        pivot += 1
        if pivot == len(matrix):
            break
    return tuple(tuple(row) for row in matrix[:pivot]), tuple(pivots)


def kernel(rows, width):
    rows, pivots = rref(rows, width)
    result = []
    for free in range(width):
        if free in pivots:
            continue
        value = [Q(0)] * width
        value[free] = Q(1)
        for row, pivot in zip(rows, pivots):
            value[pivot] = -row[free]
        result.append(tuple(value))
    return tuple(result)


def combine(coefficients, rows, width):
    return tuple(sum((coefficient * row[j] for coefficient, row in zip(coefficients, rows)), Q(0))
                 for j in range(width))


def form(h):
    return tuple(tuple(Q(i == j) - Q(1, 9) for j in range(h)) for i in range(h))


def pairing(a, b, G):
    return sum((x * sum((entry * y for entry, y in zip(row, b)), Q(0))
                for x, row in zip(a, G)), Q(0))


def gram(rows, G):
    return tuple(tuple(pairing(a, b, G) for b in rows) for a in rows)


def contained(V, U, h):
    annihilator = kernel(U, h)
    return all(sum((a * b for a, b in zip(x, y)), Q(0)) == 0
               for x in V for y in annihilator)


def radical(V, G):
    h = len(G)
    return rref([combine(c, V, h) for c in kernel(gram(V, G), len(V))], h)[0]


def orthogonal_split(V, G):
    """Return a diagonal nonsingular part and the exact radical of V."""
    h = len(G)
    remaining, unused = rref(V, h)
    nondegenerate = []
    while remaining:
        vector = next((x for x in remaining if pairing(x, x, G)), None)
        if vector is None:
            pair = next(((a, b) for i, a in enumerate(remaining)
                         for b in remaining[i + 1:] if pairing(a, b, G)), None)
            if pair is None:
                break
            vector = tuple(a + b for a, b in zip(*pair))
        norm = pairing(vector, vector, G)
        if not norm:
            raise AssertionError('Characteristic-zero polarization failed')
        nondegenerate.append(vector)
        remaining, unused = rref([tuple(a - pairing(x, vector, G) * b / norm
                                       for a, b in zip(x, vector)) for x in remaining], h)
    return tuple(nondegenerate), remaining


def solve(rows, rhs, width):
    """A rational solution, with free coordinates zero, or None."""
    augmented, pivots = rref([tuple(row) + (value,) for row, value in zip(rows, rhs)], width + 1)
    if width in pivots:
        return None
    value = [Q(0)] * width
    for row, pivot in zip(augmented, pivots):
        value[pivot] = row[-1]
    return tuple(value)


def complete(V, U, G):
    """Minimal F, V<=F<=U, nondegenerate; or an exact radical-cap obstruction."""
    h = len(G)
    if any(len(row) != h for row in G) or any(G[i][j] != G[j][i] for i in range(h) for j in range(h)):
        raise ValueError('A symmetric rational ambient form is required')
    V, unused = rref(V, h)
    U, unused = rref(U, h)
    if not contained(V, U, h):
        raise ValueError('The required lower span lies outside the future cap')
    N, R = orthogonal_split(V, G)
    response = tuple(tuple(pairing(r, u, G) for u in U) for r in R)
    rank = len(rref(response, len(U))[0])
    if rank < len(R):
        relation = kernel(tuple(zip(*response)), len(R))[0]
        obstruction = combine(relation, R, h)
        if not any(obstruction) or not all(pairing(obstruction, u, G) == 0 for u in U):
            raise AssertionError('The exact future-radical obstruction failed')
        return dict(status='NO NONDEGENERATE COMPLETION INSIDE CAP', lower=V, upper=U,
                    lower_radical=R, obstruction=obstruction, minimal_dimension=None)
    extra = []
    for i in range(len(R)):
        rhs = tuple(Q(i == j) for j in range(len(R)))
        coefficients = solve(response, rhs, len(U))
        if coefficients is None:
            raise AssertionError('Independent radical responses had no dual solution')
        vector = combine(coefficients, U, h)
        for n in N:
            factor = pairing(vector, n, G) / pairing(n, n, G)
            vector = tuple(a - factor * b for a, b in zip(vector, n))
        extra.append(vector)
    F, unused = rref(list(V) + extra, h)
    target = len(V) + len(R)
    if len(F) != target or radical(F, G) or not contained(F, U, h):
        raise AssertionError('The exact minimum-dimension completion failed')
    return dict(status='EXACT MINIMAL NONDEGENERATE COMPLETION', lower=V, upper=U,
                lower_radical=R, added_vectors=tuple(extra), completion=F,
                minimal_dimension=target)


def encoded(value):
    if isinstance(value, Q):
        return [value.numerator, value.denominator]
    if isinstance(value, dict):
        return {key: encoded(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [encoded(item) for item in value]
    return value


def probe(task):
    h, seed = task
    started, G = time.monotonic(), form(h)
    unit = [tuple(Q(i == j) for j in range(h)) for i in range(h)]
    triples = [tuple(Q(3 * k <= j < 3 * k + 3) for j in range(h)) for k in range(3)]
    target = (0, 3, 6)
    covector = tuple(Q(3 * (j in target) - 1) for j in range(h))
    one_cap = kernel((covector,), h)
    positive = complete(triples, one_cap, G)
    if positive['minimal_dimension'] != 4 or len(positive['lower_radical']) != 1:
        raise AssertionError('The explicit three-disjoint-triple completion did not cost exactly one')
    covectors = [tuple(Q(3 * (j in (a, b, c)) - 1) for j in range(h))
                 for a in range(3) for b in range(3, 6) for c in range(6, 9)]
    joint_cap = kernel(covectors, h)
    negative = complete(triples, joint_cap, G)
    if negative['minimal_dimension'] is not None:
        raise AssertionError('The shared radical of the 27-target cap was silently completed')
    rng = random.Random(seed)
    checked = 0
    for dimension in range(1, 7):
        rows = [unit[0]] if dimension == 1 else triples[:]
        if dimension > 3:
            rows += [tuple(Q(rng.randrange(-2, 3)) if j < 9 else Q(0) for j in range(h))
                     for unused in range(dimension - 3)]
        result = complete(rows, unit, G)
        d = len(rref(rows, h)[0])
        if result['minimal_dimension'] not in (d, d + 1):
            raise AssertionError('A rational Lorentz subspace required more than one extra dimension')
        checked += 1
    return dict(status='PASS EXACT RATIONAL COMPLETION CONTROLS', h=h, seed=seed,
                arbitrary_radical_cases=checked, positive=encoded(positive),
                negative=encoded(negative), signature_bound_scope='Rational h>9 only',
                odd_local_ring_compatibility_not_assumed=True,
                native_primitive_or_exponent=False, seconds=time.monotonic() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('A positive worker count is required')
    args.output.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).resolve()
    digest = sha256(source.read_bytes()).hexdigest()
    tasks = [(10, 20261009141), (12, 20261009142), (24, 20261009143), (48, 20261009144)]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_sha256=digest,
                    tasks=tasks, workers=args.workers, stdlib_only=True,
                    scope='Exact rational constructive completion and future-cap obstruction; no modular/native/exponent claim')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, tasks))
    if sha256(source.read_bytes()).hexdigest() != digest:
        raise AssertionError('The exact constructor source changed during execution')
    (args.output / 'certificate.json').write_text(json.dumps(dict(cases=rows), indent=2) + '\n')
    print(json.dumps(dict(status='PASS EXACT RATIONAL FRAME COMPLETION', dimensions=[row['h'] for row in rows],
                         minimal_extension=1, cap_obstructions=4)))


if __name__ == '__main__':
    main()
