#!/usr/bin/env python3
"""Exact identity-endpoint counterexample to omitting intervening children.

Every matrix is a weighted permutation, so its largest absolute entry is
its exact Euclidean operator norm. No spectral approximation is used.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path


IDENTITY = ((Q(1), Q(0)), (Q(0), Q(1)))
SWAP = ((Q(0), Q(1)), (Q(1), Q(0)))


def multiply(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def norm(a):
    if any(sum(x != 0 for x in row) != 1 for row in a):
        raise AssertionError('The exact norm formula requires a weighted permutation')
    if any(sum(a[i][j] != 0 for i in range(2)) != 1 for j in range(2)):
        raise AssertionError('The exact norm formula requires distinct nonzero columns')
    return max(abs(x) for row in a for x in row)


def probe(e):
    if e < 2:
        raise ValueError('A width-one child must be at most half parent width')
    D = ((Q(2**e), Q(0)), (Q(0), Q(1, 2**e)))
    inverse_D = ((Q(1, 2**e), Q(0)), (Q(0), Q(2**e)))
    word = [('local', D), ('child', SWAP), ('local', inverse_D),
            ('local', D), ('child', SWAP), ('local', inverse_D)]
    actual = collapsed = IDENTITY
    actual_prefix = collapsed_prefix = Q(1)
    local_factor_product = Q(1)
    for kind, gate in word:
        actual = multiply(gate, actual)
        actual_prefix = max(actual_prefix, norm(actual))
        if kind == 'local':
            collapsed = multiply(gate, collapsed)
            collapsed_prefix = max(collapsed_prefix, norm(collapsed))
            local_factor_product *= norm(gate)
    if actual != IDENTITY or collapsed != IDENTITY:
        raise AssertionError('Both complete endpoints must be exact identities')
    if (actual_prefix, collapsed_prefix, local_factor_product) != (2**(2*e), 2**e, 2**(4*e)):
        raise AssertionError('The exact prefix/factor distinction was lost')
    broken = IDENTITY
    for index, (_, gate) in enumerate(word):
        if index != 4:
            broken = multiply(gate, broken)
    if broken == IDENTITY:
        raise AssertionError('Deleting the second unitary child must change the endpoint')
    return dict(parent_width=e, child_width=1, unitary_child_calls=2,
                complete_endpoint='identity', actual_prefix_norm=str(actual_prefix),
                collapsed_local_prefix_norm=str(collapsed_prefix),
                product_of_local_factor_norms=str(local_factor_product),
                undercount_ratio=str(actual_prefix/collapsed_prefix),
                all_two_basis_columns_exact=True,
                arbitrary_complex_fields_follow_from_real_linear_identity=True,
                omitted_child_rejected=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                    widths=[2, 8] if args.bounded else [2, 4, 16, 64],
                    scope='Exact two-coordinate block repeated on spectators; no native algorithm')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, protocol['widths']))
    result = dict(status='PASS EXACT INTERLEAVED LOCAL NORM COUNTEREXAMPLE',
                  cases=rows, formal_verification=False, new_exponent=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], cases=len(rows))))


if __name__ == '__main__':
    main()
