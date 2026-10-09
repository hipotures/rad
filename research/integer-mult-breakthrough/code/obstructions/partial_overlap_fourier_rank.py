#!/usr/bin/env python3
"""Exact odd-cube response ranks and a separable complete-copy discriminator.

The rank formula is over Q/C. The rank charge is conditional on a narrowly
stated scalar-row query interface; it is not a general circuit lower bound.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from math import comb, factorial
from pathlib import Path
import json
import time


def value(k, r):
    t = (k - 1) // 2
    answer = Q(1, factorial(t))
    for a in range(t):
        answer *= Q(r - 1 - 2 * a, 2)
    return answer


def walsh(values):
    out = list(values)
    width = 1
    while width < len(out):
        for start in range(0, len(out), 2 * width):
            for a in range(width):
                u, v = out[start + a], out[start + a + width]
                out[start + a], out[start + a + width] = u + v, u - v
        width *= 2
    return out


def matrix_rank(rows):
    """Independent rational elimination for small parity-block controls."""
    basis = {}
    for original in rows:
        row = list(original)
        for pivot, previous in sorted(basis.items()):
            factor = row[pivot]
            if factor:
                row = [a - factor * b for a, b in zip(row, previous)]
        pivot = next((a for a, v in enumerate(row) if v), None)
        if pivot is not None:
            scale = row[pivot]
            basis[pivot] = [a / scale for a in row]
    return len(basis)


def response(k, j):
    t = (k - 1) // 2
    kernel = [value(k, j - z.bit_count()) for z in range(1 << j)]
    eigenvalues = walsh(kernel)
    degree_values = {}
    for mask, actual in enumerate(eigenvalues):
        degree = mask.bit_count()
        difference = t - degree
        expected = Q(0)
        if 0 <= difference <= k - j - 1:
            expected = Q(2 ** j, 2 ** (k - 1)) * (-1) ** difference * comb(k - j - 1, difference)
        assert actual == expected, (k, j, mask, actual, expected)
        degree_values[degree] = str(expected)
    low, high = max(0, j - t), min(t, j)
    rank = sum(comb(j, a) for a in range(low, high + 1))
    assert rank == sum(bool(a) for a in eigenvalues)
    inverse = [a / (1 << j) for a in walsh(eigenvalues)]
    assert inverse == kernel
    parity_checks = []
    if j:
        assert rank % 2 == 0
        # Odd intersections vanish. Translating one bit swaps the two equal
        # parity blocks, so their ranks are equal without a large elimination.
        assert all(not a for z, a in enumerate(kernel) if (j - z.bit_count()) & 1)
        for parity in [0, 1]:
            labels = [a for a in range(1 << j) if a.bit_count() % 2 == parity]
            columns = [a for a in range(1 << j) if a.bit_count() % 2 == (parity ^ (j & 1))]
            assert len(labels) == len(columns) == 1 << (j - 1)
            if j <= 5:
                rows = [[kernel[a ^ b] for b in columns] for a in labels]
                independent = matrix_rank(rows)
                assert independent == rank // 2
                parity_checks.append({'parity': parity, 'rows': len(rows),
                                      'columns': len(columns), 'rank': independent})
            else:
                parity_checks.append({'parity': parity, 'rank': rank // 2,
                                      'method': 'Equal disjoint parity blocks and complete Walsh diagonalization; no elimination claim'})
    return {'j': j, 'kernel_values': [str(a) for a in kernel],
            'complete_eigenvalues': [str(a) for a in eigenvalues],
            'eigenvalue_by_degree': degree_values,
            'nonzero_degrees': [low, high], 'rank': rank,
            'parity_block_controls': parity_checks,
            'raw_rows': 1 << j, 'kernel_dimension': (1 << j) - rank}


def case(k):
    t, size = (k - 1) // 2, 1 << k
    full = [value(k, k - z.bit_count()) for z in range(size)]
    eigenvalues = walsh(full)
    assert eigenvalues == [Q(2) if a.bit_count() <= t else Q(0) for a in range(size)]
    rows = [response(k, j) for j in range(k)]
    raw = sum(comb(k, r['j']) * r['raw_rows'] for r in rows)
    live = sum(comb(k, r['j']) * r['rank'] for r in rows)
    assert raw == 3 ** k - 2 ** k
    top_rank = comb(k - 1, t)
    assert rows[-1]['rank'] == top_rank
    top_charge = Q(3 * k * top_rank, size)
    assert top_charge >= Q(9, 4) > 2
    all_charge = Q(3 * (live - 1), size)
    assert all_charge >= top_charge
    # This applies only when p>=k+1: every highest proper intersection exists.
    # A common copied stream can serve many targets at one actual frame.
    # The explicit separable model charges only its independent scalar rows,
    # and excludes shared/evolving copies or address-encoded row multiplexing.
    next_charge = Q(3 * (k + 2) * comb(k + 1, t + 1), 1 << (k + 2))
    assert next_charge / top_charge == Q(k + 2, k + 1)
    invalid_distinct_row_charge_rejected = any(r['rank'] < r['raw_rows'] for r in rows)
    assert invalid_distinct_row_charge_rejected
    complete_entries = 0
    if k <= 7:
        # Explicit all-source/all-target endpoint entries for every canonical
        # partial support, with ignored source bits retained as spectators.
        for r in rows:
            j = r['j']
            kernel = [Q(a) for a in r['kernel_values']]
            low_mask = (1 << j) - 1
            for alpha in range(1 << j):
                for source in range(size):
                    actual = kernel[(alpha ^ source) & low_mask]
                    intersection = j - ((alpha ^ source) & low_mask).bit_count()
                    assert actual == value(k, intersection)
                    complete_entries += 1
    return {'k': k, 't': t, 'sources_per_cube': size, 'partial_supports': rows,
            'complete_full_kernel': [str(a) for a in full],
            'complete_full_eigenvalues': [str(a) for a in eigenvalues],
            'joint_low_degree_dimension': sum(comb(k, a) for a in range(t + 1)),
            'raw_rows_per_cube': raw, 'independent_rows_per_cube': live,
            'highest_proper_support_rows': top_rank,
            'top_query_rank_per_master_source': str(top_charge),
            'all_separable_query_rank_per_master_source': str(all_charge),
            'top_charge_monotonic_ratio': str(next_charge / top_charge),
            'complete_explicit_scalar_entries': complete_entries,
            'negative_distinct_rows_equal_rank_rejected': invalid_distinct_row_charge_rejected,
            'scope': 'Exact characteristic-zero scalar ranks; conditional separate common-Q copied scalar-row reads, p>=k+1; no general physical/native/exponent theorem'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    frozen = Path(__file__).read_bytes()
    start = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    ks = [3, 5] if args.bounded else [3, 5, 7, 9, 11]
    if args.workers == 1:
        cases = [case(k) for k in ks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(case, ks))
    assert Path(__file__).read_bytes() == frozen
    result = {'status': 'PASS partial-overlap Fourier ranks and separable-copy controls',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'elapsed_seconds': time.monotonic() - clock, 'workers': args.workers,
              'bounded': args.bounded, 'source_sha256': sha256(frozen).hexdigest(),
              'cases': cases,
              'model': 'Separate common-Q copy per independent scalar response row at each distinct fixed orthogonal query hyperplane; no shared/evolving copies, row packing, address-dependent encoding or mixed geodesic preparation',
              'conclusion': 'REFUTED within the separable query model for odd k>=3,p>=k+1: highest-proper queries alone exceed the unspent2v master deficit',
              'no_new_kappa': True}
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'certificate.json').write_text(text)
        print(json.dumps({k: v for k, v in result.items() if k != 'cases'}))
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
