#!/usr/bin/env python3
"""Integral nonspectral completion of the exceptional five-subset side kernel.

Two-sided Euclidean reduction retains the right-column operations as explicit
reversible scalar words and the left-row operations as a rank certificate.
An explicit integral ballot-incidence basis controls coefficient growth.
This independently determines rank and gives an actual integer projector onto
the kernel. Its noncommutation with K is the price of avoiding the forbidden
Gaussian-dyadic invariant spectral projector; no native phase cost is inferred.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import time

from odd_weight_spectrum import central_value


TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/side-kernel-completion.json'


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def product(a, b):
    columns = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, column) if x and y)
             for column in columns] for row in a]


def integer_bits(matrix):
    return max(abs(x).bit_length() for row in matrix for x in row)


def apply_column(matrix, op):
    kind, target, source, coefficient = op
    if kind == 'add':
        for row in matrix:
            row[target] += coefficient*row[source]
    elif kind == 'swap':
        for row in matrix:
            row[target], row[source] = row[source], row[target]
    elif kind == 'negate':
        for row in matrix:
            row[target] = -row[target]
    else:
        raise ValueError('Unknown column operation')


def euclidean_columns(matrix, config):
    a = [row[:] for row in matrix]
    v = identity(len(a[0]))
    u = identity(len(a))
    word, row_word, pivots = [], [], []

    def record(op):
        apply_column(a, op)
        apply_column(v, op)
        word.append(op)
        if len(word)+len(row_word) > config['maximum_column_operations']:
            raise ValueError('Column-operation guard exceeded')
        if max(integer_bits(v), integer_bits(u), integer_bits(a)) > config['maximum_integer_bits']:
            raise ValueError('Integer coefficient guard exceeded')

    def record_row(op):
        kind, target, source, coefficient = op
        for matrix in (a, u):
            if kind == 'add':
                matrix[target] = [x+coefficient*y for x, y in zip(matrix[target], matrix[source])]
            elif kind == 'swap':
                matrix[target], matrix[source] = matrix[source], matrix[target]
            elif kind == 'negate':
                matrix[target] = [-x for x in matrix[target]]
        row_word.append(op)
        if len(word)+len(row_word) > config['maximum_column_operations']:
            raise ValueError('Two-sided operation guard exceeded')
        if max(integer_bits(v), integer_bits(u), integer_bits(a)) > config['maximum_integer_bits']:
            raise ValueError('Integer coefficient guard exceeded')

    r = 0
    while r < min(len(a), len(a[0])):
        candidates = [(i, j) for i in range(r, len(a))
                      for j in range(r, len(a[0])) if a[i][j]]
        if not candidates:
            break
        first_row, first_col = min(candidates, key=lambda ij: (abs(a[ij[0]][ij[1]]), ij))
        if first_row != r:
            record_row(['swap', r, first_row, 0])
        if first_col != r:
            record(['swap', r, first_col, 0])
        while True:
            for i in range(r+1, len(a)):
                while a[i][r]:
                    quotient = a[i][r]//a[r][r]
                    if quotient:
                        record_row(['add', i, r, -quotient])
                    if a[i][r]:
                        record_row(['swap', i, r, 0])
            for j in range(r+1, len(a[0])):
                while a[r][j]:
                    quotient = a[r][j]//a[r][r]
                    if quotient:
                        record(['add', j, r, -quotient])
                    if a[r][j]:
                        record(['swap', j, r, 0])
            if not any(a[i][r] for i in range(r+1, len(a))):
                break
        if a[r][r] < 0:
            record(['negate', r, r, 0])
        pivots.append([r, r, a[r][r]])
        r += 1
        if r == len(a[0]):
            break
    if any(a[i][j] for i in range(len(a)) for j in range(r, len(a[0]))):
        raise ValueError('Reduced active columns are not zero')
    for i, j, value in pivots:
        if value <= 0 or any(a[i][k] for k in range(j+1, len(a[0]))):
            raise ValueError('Nonzero triangular rank certificate failed')
    if any(a[i][j] for i in range(len(a)) for j in range(len(a[0])) if i != j):
        raise ValueError('Two-sided diagonal rank certificate failed')
    if product(product(u, matrix), v) != a:
        raise ValueError('Literal U*H*V diagonal certificate failed')
    return product(matrix, v), v, word, pivots, row_word, a, u


def scalar_word(column_word):
    # V = E1 ... Eq. The chronological data word therefore applies Eq first.
    # col[target] += c*col[source] means data[source] += c*data[target].
    result = []
    for kind, target, source, coefficient in reversed(column_word):
        result.append([kind, source if kind == 'add' else target,
                       target if kind == 'add' else source, coefficient])
    return result


def inverse_word(word):
    return [[kind, target, source, -coefficient if kind == 'add' else coefficient]
            for kind, target, source, coefficient in reversed(word)]


def apply_word(values, word):
    values = values[:]
    for kind, target, source, coefficient in word:
        if kind == 'add':
            values[target] += coefficient*values[source]
        elif kind == 'swap':
            values[target], values[source] = values[source], values[target]
        elif kind == 'negate':
            values[target] = -values[target]
        else:
            raise ValueError('Unknown scalar operation')
    return values


def symbolic_guard(word, n):
    rows = identity(n)
    peak, endpoint = 1, 1
    for kind, target, source, coefficient in word:
        if kind == 'add':
            temporary = [coefficient*x for x in rows[source]]
            peak = max(peak, sum(abs(x) for x in temporary))
            rows[target] = [x+y for x, y in zip(rows[target], temporary)]
        elif kind == 'swap':
            rows[target], rows[source] = rows[source], rows[target]
        elif kind == 'negate':
            rows[target] = [-x for x in rows[target]]
        peak = max(peak, sum(abs(x) for x in rows[target]),
                   sum(abs(x) for x in rows[source]))
    endpoint = max(sum(abs(x) for x in row) for row in rows)
    return dict(extra_fraction_bits=0, peak_row_L1_including_scalar_temporary=peak,
                endpoint_row_L1=endpoint, scalar_coefficient_max_bits=max(
                    [abs(op[3]).bit_length() for op in word if op[0] == 'add']+[1]))


def incidence_preconditioner(labels, h, k):
    ell = h-k
    columns = [a for j in range(ell+1) for a in combinations(range(h), j)
               if all(x >= 2*i+1 for i, x in enumerate(a))]
    B = [[int(all(not(s & (1 << x)) for x in a)) for a in columns] for s in labels]
    n = len(labels)
    if len(columns) != n:
        raise ValueError('Ballot-incidence basis count failed')
    rows = [row+unit for row, unit in zip(B, identity(n))]
    undo = []

    def record(op):
        kind, target, source, coefficient = op
        if kind == 'add':
            rows[target] = [x+coefficient*y for x, y in zip(rows[target], rows[source])]
        elif kind == 'swap':
            rows[target], rows[source] = rows[source], rows[target]
        elif kind == 'negate':
            rows[target] = [-x for x in rows[target]]
        undo.append(op)

    for j in range(n):
        candidates = [i for i in range(j, n) if rows[i][j]]
        pivot = min(candidates, key=lambda i: (abs(rows[i][j]), i))
        if pivot != j:
            record(['swap', j, pivot, 0])
        for i in range(j+1, n):
            while rows[i][j]:
                quotient = rows[i][j]//rows[j][j]
                if quotient:
                    record(['add', i, j, -quotient])
                if rows[i][j]:
                    record(['swap', i, j, 0])
        if abs(rows[j][j]) != 1:
            raise ValueError('Incidence preconditioner requires a nonunit pivot')
        if rows[j][j] < 0:
            record(['negate', j, j, 0])
        for i in range(n):
            if i == j or not rows[i][j]:
                continue
            coefficient = -rows[i][j]
            record(['add', i, j, coefficient])
    Bi = [row[n:] for row in rows]
    if [row[:n] for row in rows] != identity(n) or product(B, Bi) != identity(n):
        raise ValueError('Incidence preconditioner exact inverse failed')
    return B, Bi, columns, undo


def case(task):
    order, config = task
    started = time.monotonic()
    h, k = config['ambient_h'], config['odd_weight_k']
    labels = [sum(1 << x for x in s) for s in combinations(range(h), k)]
    if order == 'reverse':
        labels.reverse()
    elif order == 'rotate-17':
        labels = labels[17:]+labels[:17]
    elif order == 'seeded-shuffle':
        random.Random(config['shuffle_seed']).shuffle(labels)
    elif order != 'lexicographic':
        raise ValueError('Unknown source ordering')
    n = len(labels)
    H = [[Q(8)*(int(i == j)-central_value(k, (s&t).bit_count()))
          for j, t in enumerate(labels)] for i, s in enumerate(labels)]
    if any(z.denominator != 1 for row in H for z in row):
        raise ValueError('Scaled side matrix is not integral')
    H = [[int(z) for z in row] for row in H]
    B, Bi, incidence_columns, incidence_undo = incidence_preconditioner(labels, h, k)
    Hpre = product(product(Bi, H), B)
    reduced, V, column_word, pivots, row_word, diagonal, U = euclidean_columns(Hpre, config)
    reduced, V, U = product(B, reduced), product(B, V), product(U, Bi)
    r = len(pivots)
    if r != 36 or product(H, V) != reduced or product(product(U, H), V) != diagonal:
        raise ValueError('Rank or literal right-coordinate certificate failed')
    word = scalar_word(column_word)+inverse_word(incidence_undo)
    undo = inverse_word(word)
    basis_outputs = [apply_word([int(i == j) for i in range(n)], word) for j in range(n)]
    inverse_outputs = [apply_word([int(i == j) for i in range(n)], undo) for j in range(n)]
    replayed = [list(row) for row in zip(*basis_outputs)]
    Vinv = [list(row) for row in zip(*inverse_outputs)]
    if replayed != V or product(V, Vinv) != identity(n) or product(Vinv, V) != identity(n):
        raise ValueError('Full forward and inverse scalar words failed')
    dirty_fields = [[Q(((i+1)*(field+3) % 41)-20, 1 << (field+1))
                     for i in range(n)] for field in range(4)]
    for values in dirty_fields:
        if apply_word(apply_word(values, word), undo) != values:
            raise ValueError('Arbitrary dyadic dirty-bank restoration failed')
    transformed_H = product(Vinv, reduced)
    couplings = [(i, j, transformed_H[i][j]) for i in range(r, n)
                 for j in range(r) if transformed_H[i][j]]
    if not couplings or any(transformed_H[i][j] for i in range(n) for j in range(r, n)):
        raise ValueError('Nonspectral lower coupling or complete kernel columns lost')
    Vkernel = [[V[i][j] if j >= r else 0 for j in range(n)] for i in range(n)]
    P = product(Vkernel, Vinv)
    HP, PH = product(H, P), product(P, H)
    if product(P, P) != P or any(x for row in HP for x in row) or not any(x for row in PH for x in row):
        raise ValueError('Integer kernel projector/coupling discriminator failed')
    if sum(P[i][i] for i in range(n)) != n-r:
        raise ValueError('Integral kernel projector trace failed')
    ci, cj, cv = couplings[0]
    witness = next((i, j, PH[i][j]) for i in range(n) for j in range(n) if PH[i][j])
    return dict(source_order=order, labels=labels, volume=n, rank=r, nullity=n-r,
        pivots=pivots, column_word=column_word, rank_certificate_row_word=row_word,
        incidence_basis_columns=[list(a) for a in incidence_columns],
        incidence_basis_inverse_word=incidence_undo, incidence_basis_sha256=digest(B),
        incidence_basis_inverse_sha256=digest(Bi),
        diagonal_rank_certificate_sha256=digest(diagonal), U_sha256=digest(U),
        exact_UHV_diagonal=True,
        scalar_word_convention='First reverse preconditioned column operations: column target+=c*source becomes data source+=c*target. Then apply the inverse of incidence_basis_inverse_word to return to physical scalar coordinates.',
        scalar_operations=len(word), scalar_operation_counts={kind: sum(op[0] == kind for op in word)
            for kind in ['add', 'swap', 'negate']}, V_max_bits=integer_bits(V),
        inverse_max_bits=integer_bits(Vinv), V_sha256=digest(V), inverse_sha256=digest(Vinv),
        transformed_H_sha256=digest(transformed_H), integer_kernel_projector_sha256=digest(P),
        complete_basis_columns_replayed=n, arbitrary_dyadic_dirty_fields_replayed=len(dirty_fields),
        forward_scalar_guard=symbolic_guard(word, n), inverse_scalar_guard=symbolic_guard(undo, n),
        K_coordinate_shape='[[A,0],[C,I_20]] with C nonzero; H=8*(I-K)',
        nonzero_bottom_coupling_count=len(couplings), K_bottom_coupling_witness=dict(
            row=ci, column=cj, coefficient=str(Q(-cv, 8))),
        integer_projector_trace=20, exact_HP_zero=True, exact_PH_nonzero=True,
        noncommutation_PH_witness=dict(row=witness[0], column=witness[1], integer=witness[2]),
        projector_diagonal=sorted(set(P[i][i] for i in range(n))),
        exact_HV_reconstruction=True, exact_two_sided_inverse=True, seconds=time.monotonic()-started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    paths = [Path(__file__).resolve(), Path(__file__).with_name('odd_weight_spectrum.py'), CONFIG]
    hashes = {str(p.relative_to(TOPIC)): sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        native_threads_per_worker=1, source_and_config_sha256=hashes, shuffle_seed=config['shuffle_seed'],
        scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    try:
        orders = config['source_orders'][:1] if args.small else config['source_orders']
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(case, [(order, config) for order in orders]))
        if any(sha256((TOPIC/p).read_bytes()).hexdigest() != value for p, value in hashes.items()):
            raise ValueError('Effective source/config changed during attempt')
        result = dict(status='EXACT INTEGRAL NONSPECTRAL KERNEL COMPLETION PASS', cases=cases,
            seconds=time.monotonic()-started, scope=config['scope'],
            conclusion='A reversible integer basis avoids the 5/14 projector by retaining nonzero cross-channel coupling; it does not provide independent invariant channels or an exponent gain.')
        if args.output:
            (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(dict(status=result['status'], cases=len(cases), seconds=result['seconds'],
                              scalar_operations=[row['scalar_operations'] for row in cases])))
    except Exception as error:
        if args.output:
            (args.output/'failure.json').write_text(json.dumps(dict(error_type=type(error).__name__,
                error=str(error), seconds=time.monotonic()-started), indent=2)+'\n')
        raise


if __name__ == '__main__':
    main()
