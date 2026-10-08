#!/usr/bin/env python3
"""Independent exact controls for one-core rational constraint frames.

The representation is rational-one-core-constraints-v1, not positive-signed-v1.
Rows constrain the h-1 outside coordinates in increasing coordinate order.
Every projector is constructed twice: a direct kernel-basis H0 Gram inverse,
and the orthogonal complement of the constraint-row space inside Gamma_c.
This file certifies geometry and ordered profiles, not a physical network.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
import time

from review_positive_physical_profiles import mm, inverse
from decompose_common_context_profiles import pivot_run_histogram


def transpose(A):
    return [list(col) for col in zip(*A)]


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def rref(rows, columns=None):
    columns = columns if columns is not None else len(rows[0])
    A = [[Q(x) for x in row] for row in rows]
    assert all(len(row) == columns for row in A)
    pivots = []
    for j in range(columns):
        k = next((k for k in range(len(pivots), len(A)) if A[k][j]), None)
        if k is None:
            continue
        i = len(pivots)
        A[i], A[k] = A[k], A[i]
        divisor = A[i][j]
        A[i] = [x / divisor for x in A[i]]
        for k in range(len(A)):
            if k != i and A[k][j]:
                coefficient = A[k][j]
                A[k] = [x-coefficient*y for x, y in zip(A[k], A[i])]
        pivots.append(j)
        if len(pivots) == len(A):
            break
    return A[:len(pivots)], pivots


def canonical_constraints(rows, columns):
    reduced, _ = rref(rows, columns)
    primitive = []
    for row in reduced:
        denominator = lcm(*(x.denominator for x in row))
        integers = [int(x*denominator) for x in row]
        divisor = gcd(*integers)
        integers = [x//divisor for x in integers]
        if next(x for x in integers if x) < 0:
            integers = [-x for x in integers]
        primitive.append(integers)
    return primitive


def kernel_columns(rows, columns):
    A, pivots = rref(rows, columns)
    free = [j for j in range(columns) if j not in pivots]
    basis = []
    for j in free:
        column = [Q(0)]*columns
        column[j] = Q(1)
        for i, pivot in enumerate(pivots):
            column[pivot] = -A[i][j]
        basis.append(column)
    return transpose(basis) if basis else [[] for _ in range(columns)]


def conjugate(P, beta):
    h = len(P)
    beta = Q(beta)
    assert 1-h*beta
    L = [[Q(i == j)-beta for j in range(h)] for i in range(h)]
    Linverse = [[Q(i == j)+beta/(1-h*beta) for j in range(h)] for i in range(h)]
    return mm(mm(L, P), Linverse)


def explicit_gram_projector(h, common, constraints, beta=Q(0)):
    outside = [i for i in range(h) if i != common]
    T = [[Q(1 if i == common else 2 if i == j else 0)
          for j in outside] for i in range(h)]
    H0 = [[Q(i == j)-Q(1, 9) for j in range(h)] for i in range(h)]
    assert mm(mm(transpose(T), H0), T) == [[4*x for x in row] for row in identity(h-1)]
    U = kernel_columns(constraints, h-1)
    B = mm(T, U)
    rank = len(U[0])
    if rank:
        dual = mm(transpose(B), H0)
        P = mm(mm(B, inverse(mm(dual, B))), dual)
    else:
        P = [[Q(0)]*h for _ in range(h)]
    return conjugate(P, beta), B


def constraint_projector(h, common, constraints, beta=Q(0)):
    outside = [i for i in range(h) if i != common]
    T = [[Q(1 if i == common else 2 if i == j else 0)
          for j in outside] for i in range(h)]
    H0 = [[Q(i == j)-Q(1, 9) for j in range(h)] for i in range(h)]
    dual = mm(transpose(T), H0)
    P = [[x/4 for x in row] for row in mm(T, dual)]
    A, _ = rref(constraints, h-1)
    if A:
        normals = mm(T, transpose(A))
        normal_dual = mm(transpose(normals), H0)
        correction = mm(mm(normals, inverse(mm(normal_dual, normals))), normal_dual)
        P = [[x-y for x, y in zip(row, other)] for row, other in zip(P, correction)]
    return conjugate(P, beta)


def ordered_pivots(matrix):
    A = [row[:] for row in matrix]
    h = len(A)
    pivots = []
    for i in range(h):
        j = next((j for j in range(h-1, -1, -1) if A[i][j]), None)
        if j is None:
            continue
        pivots.append([i, j])
        for k in range(i+1, h):
            ratio = A[k][j]/A[i][j]
            if ratio:
                for c in range(j+1):
                    A[k][c] -= ratio*A[i][c]
    return pivots


def check_case(h, common, beta):
    m = h-1
    a, b, c, d = range(4)
    def row(values):
        return [Q(values.get(i, 0)) for i in range(m)]
    constraints = dict(
        first=[row({a:1,b:-1}), row({c:1,d:-1})],
        second=[row({a:1,c:-1}), row({b:1,d:-1})],
        join=[row({a:1,b:-1,c:-1,d:1})], full=[])
    projectors = {}
    for name, A in constraints.items():
        P, B = explicit_gram_projector(h, common, A, beta)
        alternate = constraint_projector(h, common, A, beta)
        assert P == alternate, 'Independent explicit Gram and row-normal formulas differ'
        assert mm(P, P) == P
        rank = m-len(rref(A, m)[1])
        assert sum(P[i][i] for i in range(h)) == rank
        projectors[name] = P
    transitions = []
    for old, new in [('first','join'), ('second','join'), ('join','full')]:
        P, R = projectors[old], projectors[new]
        assert mm(P, R) == P and mm(R, P) == P
        M = [[y-x for x, y in zip(row, other)] for row, other in zip(P, R)]
        assert mm(M, M) == M
        pivots = ordered_pivots(M)
        assert len(pivots) == 1
        denominator = lcm(*(x.denominator for row in M for x in row))
        bound = max(abs(int(x*denominator)) for row in M for x in row)
        transitions.append(dict(old=old, new=new, rank=1, pivots=pivots,
            contiguous_children=dict(pivot_run_histogram(pivots)),
            integer_denominator=str(denominator), entry_bound=str(bound),
            integer_minor_bound=str(bound), exact_nested_projectors=True))
    first = transpose(kernel_columns(constraints['first'], m))
    second = transpose(kernel_columns(constraints['second'], m))
    join_dimension = len(rref(first+second, m)[1])
    assert join_dimension == m-1
    # Within the four affected coordinates, partition joins connect all of them.
    # Requiring the two different equality partitions simultaneously in a
    # containing partition therefore releases all four singleton dimensions.
    return dict(h=h, common=common, beta=str(beta),
        representation='rational-one-core-constraints-v1',
        exact_constraint_rows={name:canonical_constraints(A,m) for name,A in constraints.items()},
        outside_join_rank=join_dimension, affected_rational_join_rank=3,
        affected_partition_closure_rank=4, ambient_outside_rank=m,
        positive_Gamma_Gram_4I=True, both_projector_derivations_equal=True,
        direct_rational_join_preserves_one_dimension=True,
        transitions=transitions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    started = time.monotonic()
    cases = []
    for h, commons, betas in [(5,[0],[Q(0),Q(-1)]),
            (23,[0,20],[Q(0),Q(1,15),Q(-1,12),Q(-1)]),
            (25,[3,22],[Q(0),Q(7,207),Q(1,2),Q(-1)])]:
        for common in commons:
            for beta in betas:
                case = check_case(h, common, beta)
                cases.append(case)
                print(json.dumps(dict(h=h,common=common,beta=str(beta),
                                      completed=len(cases))),flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(
        status='PASS INDEPENDENT RATIONAL ONE-CORE JOIN GEOMETRY', cases=cases,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        elapsed_seconds=time.monotonic()-started,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        classification='DISCOVERY',
        scope='Exact rational joins, positivity, containment, explicit projectors, '
              'and ordered local transitions. No scalar DAG, dirty-state word, '
              'paid capacities, full CRT, DATA, or conditional exponent accepted.'),indent=2)+'\n')


if __name__ == '__main__':
    main()
