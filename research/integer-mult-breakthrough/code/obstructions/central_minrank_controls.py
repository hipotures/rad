#!/usr/bin/env python3
"""Exact paired-minor and field-scope controls for odd-subset centers.

No minimum-rank completion optimum, paid basis change or exponent is claimed.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time


def kernel(t, k):
    out = Fraction(1)
    for j in range((k-1)//2):
        out *= Fraction(t-(2*j+1), k-(2*j+1))
    return out


def paired_labels(h, k):
    pairs = [(1 << (2*j+1)) | (1 << (2*j+2))
             for j in range((h-1)//2)]
    return [1 | sum(pairs[j] for j in subset)
            for subset in combinations(range(len(pairs)), (k-1)//2)]


def validate_central_entry(t, u, value):
    if t == u and value != 1:
        raise ValueError('Central diagonal is not normalized')
    if t != u and (t & u).bit_count() & 1 and value:
        raise ValueError('Forbidden odd-intersection coefficient is nonzero')


def rational_mod(x, p):
    x = Fraction(x)
    if x.denominator % p == 0:
        raise ValueError('Reduction is undefined at this denominator')
    return x.numerator * pow(x.denominator, -1, p) % p


def modular_rank(matrix, p):
    a = [[rational_mod(x, p) for x in row] for row in matrix]
    rank = 0
    pivots = []
    for col in range(len(a[0])):
        pivot = next((j for j in range(rank, len(a)) if a[j][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        scale = pow(a[rank][col], -1, p)
        a[rank] = [x * scale % p for x in a[rank]]
        for j in range(rank+1, len(a)):
            factor = a[j][col]
            if factor:
                a[j] = [(x-factor*y) % p for x, y in zip(a[j], a[rank])]
        pivots.append(col)
        rank += 1
        if rank == len(a):
            break
    return rank, pivots


def run(h, k, full):
    d = (k-1)//2
    labels = paired_labels(h, k)
    count = 0
    digest = sha256()
    for i, t in enumerate(labels):
        if t.bit_count() != k:
            raise ValueError('Pair-family weight failed')
        for j, u in enumerate(labels):
            overlap = (t & u).bit_count()
            value = kernel(overlap, k)
            validate_central_entry(t, u, value)
            if value != int(i == j) or not overlap & 1:
                raise ValueError('Paired principal identity minor failed')
            digest.update(f'{t},{u}:{value};'.encode())
            count += 1
    if len(labels) != comb((h-1)//2, d):
        raise ValueError('Incomplete paired-family minor')
    # An off-diagonal violation invalidates the minor, not merely its rank.
    corruption_rejected = False
    if len(labels) > 1:
        try:
            validate_central_entry(labels[0], labels[1], Fraction(1))
        except ValueError:
            corruption_rejected = True
    if not corruption_rejected:
        raise ValueError('Forbidden coefficient corruption was not detected')
    undefined = False
    try:
        rational_mod(kernel(0, k), 2)
    except ValueError:
        undefined = True
    if not undefined:
        raise ValueError('Gaussian-dyadic denominator wrongly reduced modulo two')
    common_denominator = 1
    for t in range(k+1):
        denominator = kernel(t, k).denominator
        if denominator & (denominator-1):
            raise ValueError('Kernel is not dyadic on integer intersections')
        common_denominator = max(common_denominator, denominator)
    if (common_denominator * kernel(k, k)).numerator % 2:
        raise ValueError('Scaled modulo-two diagonal unexpectedly a unit')
    v = comb(h, k)
    result = dict(h=h, k=k, vertices=v, degree=d,
                  paired_identity_minor_rank=len(labels), minor_entries=count,
                  minor_sha256=digest.hexdigest(), paired_labels=labels,
                  central_feature_rank_upper=comb(h, d),
                  hypothetical_two_integral_rank_lower=(v+h-1)//h,
                  forced_off_diagonal_corruption_rejected=corruption_rejected,
                  undefined_modulo_two_reduction_rejected=True,
                  scaled_diagonal_modulo_two=0,
                  common_kernel_denominator=common_denominator)
    if full:
        top = [sum(1 << j for j in c) for c in combinations(range(h), k)]
        matrix = [[kernel((t & u).bit_count(), k) for u in top] for t in top]
        rank, pivots = modular_rank(matrix, 101)
        upper = comb(h, d)
        if rank != upper:
            raise ValueError('Declared small rational rank bracket is not tight')
        result['complete_polynomial_rank'] = dict(vertices=len(top), prime=101,
                                                 modular_lower=rank,
                                                 analytic_feature_upper=upper,
                                                 pivot_columns=pivots)
        # B^T B fits the odd-intersection complement over F2.
        odd = [[(t & u).bit_count() & 1 for u in top] for t in top]
        r2, _ = modular_rank(odd, 2)
        if r2 > h or any(odd[j][j] != 1 for j in range(len(top))):
            raise ValueError('Complementary characteristic-two fitting contract failed')
        result['complement_rank_modulo_two'] = r2
    return result


def job(args):
    return run(*args)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError('Invalid worker count')
    cases = [(7, 3, True), (8, 5, True)] if args.bounded else [
        (8, 5, True), (10, 5, True), (20, 5, False), (24, 7, False)]
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh output')
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        outcomes = list(pool.map(job, cases))
    result = dict(status='PASS EXACT CENTRAL RANK AND FIELD SCOPE CONTROLS',
                  recorded_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  workers=args.workers, cases=outcomes,
                  seconds=time.perf_counter()-started,
                  scope='Paired principal identity minors give a scoped central completion rank lower bound; small polynomial ranks bracketed by odd-prime minors and feature upper bounds. Modulo-two controls reject unpaid dyadic reduction. No minrank optimum, dirty basis compiler or exponent.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as f:
            f.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'workers', 'seconds', 'scope')}))


if __name__ == '__main__':
    main()
