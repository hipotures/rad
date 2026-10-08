#!/usr/bin/env python3
"""Exact alternating-residual Gaussian phase / one-child Clifford controls.

An alternating nondegenerate binary subspace has an even-rank real Gauss
kernel. A symplectic Walsh factor can be expressed through ONE ordinary
even-dimensional C tensor, unit phases, and paired coordinate exchanges.
This source checks the algebra; finite network and tape transfer are separate.
"""

import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import time


def dot(a, b):
    return (a & b).bit_count() & 1


def embedded(alpha, basis):
    out = 0
    for i, v in enumerate(basis):
        if (alpha >> i) & 1:
            out ^= v
    return out


def pair_swap(alpha, r):
    assert r % 2 == 0
    out = 0
    for k in range(0, r, 2):
        out |= ((alpha >> k) & 1) << (k + 1)
        out |= ((alpha >> (k + 1)) & 1) << k
    return out


def projector(z, basis):
    # In the retained symplectic basis the inverse Gram is the same J.
    coefficients = sum(dot(z, v) << i for i, v in enumerate(basis))
    return embedded(pair_swap(coefficients, len(basis)), basis)


def q(alpha, basis):
    weight = embedded(alpha, basis).bit_count()
    assert weight % 2 == 0
    return (weight // 2) & 1


def unit(value, exponent):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def multiply(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def c_numerator(alpha, beta, rank):
    out = (1, 0)
    distance = (alpha ^ beta).bit_count()
    for _ in range(rank - distance):
        out = multiply(out, (1, 1))
    for _ in range(distance):
        out = multiply(out, (1, -1))
    return out


def case(n, basis, columns=1):
    r = len(basis)
    assert r > 0 and r % 2 == 0 and r <= n
    assert all(v.bit_count() % 2 == 0 and 0 < v < 1 << n for v in basis)
    assert all(dot(u, v) == int(j == (i ^ 1))
               for i, u in enumerate(basis) for j, v in enumerate(basis))
    assert len({embedded(a, basis) for a in range(1 << r)}) == 1 << r
    values = [q(a, basis) for a in range(1 << r)]
    gauss = sum((-1) ** v for v in values)
    assert abs(gauss) == 1 << (r // 2)
    sign = int(gauss < 0)
    # Explicit ambient Fourier sums give the original C_E operator.
    phase = [(-1) ** ((projector(z, basis).bit_count() // 2) & 1)
             for z in range(1 << n)]
    reference = {}
    for a, b in product(range(1 << r), repeat=2):
        difference = embedded(a ^ b, basis)
        coefficient = sum((-1 if dot(difference, z) else 1) * phase[z]
                          for z in range(1 << n))
        assert coefficient * (1 << (r // 2)) == ((-1) ** (sign + q(a ^ b, basis))) * (1 << n)
        reference[a, b] = coefficient
    rf = r * columns
    digest = sha256()
    entries = 0
    for alpha, beta in product(range(1 << rf), repeat=2):
        ja = 0
        qsum = 0
        reference_product = 1
        for c in range(columns):
            aa, bb = (alpha >> (c * r)) & ((1 << r) - 1), (beta >> (c * r)) & ((1 << r) - 1)
            ja |= pair_swap(bb, r) << (c * r)
            qsum += q(aa, basis) + q(bb, basis)
            reference_product *= reference[aa, bb]
        # H_rf = i^(-rf/2) S C_rf S. J is a pair permutation.
        actual = unit(c_numerator(alpha, ja, rf),
                      alpha.bit_count() + ja.bit_count() - rf // 2 +
                      2 * (columns * sign + qsum))
        assert actual[1] == 0
        assert actual[0] * (1 << (n * columns)) == reference_product * (1 << rf)
        # A separate direct bilinear Walsh coefficient.
        expected_sign = (-1) ** (columns * sign + qsum + dot(alpha, ja))
        assert actual[0] == expected_sign * (1 << (rf // 2))
        digest.update(f'{alpha},{beta}:{actual[0]},{actual[1]};'.encode())
        entries += 1
    return {'ambient_dimension': n, 'basis_masks': basis, 'rank': r, 'columns': columns,
            'arf_sign': sign, 'exact_matrix_entries': entries,
            'coefficient_table_sha256': digest.hexdigest(),
            'ordinary_child_selected_bits': rf, 'extra_recursive_children': 0,
            'only_gaussian_unit_phases': True, 'maximum_absolute_coefficient': f'1/{1 << (rf // 2)}'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists(), 'Use a fresh output path'
    started = time.monotonic()
    rows = []
    seen = set()
    # Exhaust every alternating plane, independent of its chosen basis.
    for n in range(3, 8):
        even = [v for v in range(1, 1 << n) if v.bit_count() % 2 == 0]
        for u, v in product(even, repeat=2):
            if dot(u, v) != 1:
                continue
            identity = (n, tuple(sorted((u, v, u ^ v))))
            if identity in seen:
                continue
            seen.add(identity)
            rows.append(case(n, [u, v]))
    rng = random.Random(109)
    for n, rank, columns in ((6, 4, 1), (7, 4, 1), (8, 4, 1), (9, 6, 1), (3, 2, 2), (6, 4, 2)):
        basis = []
        for k in range(rank // 2):
            basis += [3 << (3 * k), 5 << (3 * k)]
        for _ in range(3):
            for _ in range(5):
                even = rng.randrange(1 << n)
                if even.bit_count() % 2:
                    even ^= 1
                basis = [v ^ (even if dot(v, even) else 0) for v in basis]
            rows.append(case(n, basis, columns))
    # Omitting the Gauss/Arf sign gives a concrete wrong kernel entry.
    basis = [3, 5]
    assert sum((-1) ** q(x, basis) for x in range(4)) == -2
    result = {'status': 'PASS exact alternating-phase algebra; network/tape transfer pending',
              'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'seed': 109, 'cases': rows, 'complete_plane_spaces': len(seen),
              'matrix_entries': sum(x['exact_matrix_entries'] for x in rows),
              'missing_arf_sign_counterexample': {'basis': basis, 'row': 0, 'column': 0,
                  'correct': '-1/2', 'without_arf_phase': '1/2'},
              'elapsed_seconds': time.monotonic() - started}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'cases'}), flush=True)


if __name__ == '__main__':
    main()
