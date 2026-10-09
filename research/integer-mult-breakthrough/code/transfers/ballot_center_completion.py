#!/usr/bin/env python3
"""Integral ballot-feature center/null completion; finite scalar discriminator.

Base unimodularity uses Bier's incidence theorem and subset-closed complement
Mobius inversion. A new-point block recursion constructs all larger minors.
No Gaussian frames, native tape program or exponent is certified here.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time


TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/ballot-center-completion.json'


def labels(h, weight):
    return tuple(sum(1 << j for j in subset) for subset in combinations(range(h), weight))


def standard(h, r):
    return tuple(sum(1 << j for j in subset) for weight in range(r+1)
        for subset in combinations(range(h), weight)
        if all(j >= 2*i+1 for i, j in enumerate(subset)))


@lru_cache(None)
def layout(h, k, r):
    if not 0 <= r <= k or h < k+r:
        raise ValueError('Require0<=r<=k and h>=k+r')
    if r == 0:
        return (0,), ((1 << k)-1,)
    if h == k+r:
        all_bits = (1 << h)-1
        return standard(h, r), tuple(all_bits ^ subset for subset in labels(h, r))
    old_features, old_pivots = layout(h-1, k, r)
    new_features, new_pivots = layout(h-1, k-1, r-1)
    high = 1 << (h-1)
    return old_features+tuple(a | high for a in new_features), old_pivots+tuple(s | high for s in new_pivots)


def inverse_word(word):
    return tuple((event[0], event[1], event[2], -event[3]) if event[0] == 'add' else event
                 for event in reversed(word))


def update(rows, event):
    kind, target, source, coefficient = event
    if kind == 'swap':
        rows[target], rows[source] = rows[source], rows[target]
    elif kind == 'negate':
        rows[target] = [-x for x in rows[target]]
    elif kind == 'add':
        rows[target] = [a+coefficient*b for a, b in zip(rows[target], rows[source])]
    else:
        raise ValueError('Nonintegral or unknown elementary gate')


def unimodular_reduce(matrix):
    """Integer Euclidean row operations, recording every swap/negation/shear."""
    rows = [list(row) for row in matrix]; n = len(rows); word = []
    determinant = 1
    def emit(event):
        nonlocal determinant
        update(rows, event); word.append(event)
        if event[0] in ['swap', 'negate']:
            determinant *= -1
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        if pivot != j:
            emit(('swap', j, pivot, 0))
        for i in range(j+1, n):
            while rows[i][j]:
                quotient = rows[j][j]//rows[i][j]
                if quotient:
                    emit(('add', j, i, -quotient))
                emit(('swap', j, i, 0))
        if abs(rows[j][j]) != 1:
            raise ValueError('The base incidence minor is not unimodular')
        if rows[j][j] == -1:
            emit(('negate', j, j, -1))
        for i in range(n):
            if i != j and rows[i][j]:
                emit(('add', i, j, -rows[i][j]))
    if rows != [[int(i == j) for j in range(n)] for i in range(n)]:
        raise ValueError('Base reduction did not reach identity')
    return tuple(word), determinant


@lru_cache(None)
def minor_word(h, k, r):
    features, pivots = layout(h, k, r)
    if r == 0:
        return ()
    if h == k+r:
        matrix = [[int(a & s == a) for s in pivots] for a in features]
        reduction, _ = unimodular_reduce(matrix)
        return inverse_word(reduction)
    old_features, old_pivots = layout(h-1, k, r)
    new_features, new_pivots = layout(h-1, k-1, r-1)
    q_old = len(old_features); high = 1 << (h-1)
    word = list(minor_word(h-1, k, r))
    # The new pivot data are still original here. This timing is essential.
    word += [('add', i, q_old+j, 1) for i, a in enumerate(old_features)
             for j, s in enumerate(new_pivots) if a & (s | high) == a]
    word += [(kind, a+q_old, b+q_old, c) for kind, a, b, c in minor_word(h-1, k-1, r-1)]
    return tuple(word)


def complete_word(h, k, r):
    features, pivots = layout(h, k, r)
    pivot_set = set(pivots)
    nonpivots = tuple(s for s in labels(h, k) if s not in pivot_set)
    source_order = pivots+nonpivots
    word = list(minor_word(h, k, r)); q = len(features)
    word += [('add', i, q+j, 1) for i, a in enumerate(features) for j, s in enumerate(nonpivots) if a & s == a]
    return features, source_order, tuple(word)


def replay_matrix(word, size):
    rows = [[int(i == j) for j in range(size)] for i in range(size)]
    peak, temporary, max_coefficient = 1, 1, 1
    for event in word:
        kind, a, b, c = event
        if kind == 'add':
            temporary = max(temporary, abs(c)*sum(abs(x) for x in rows[b]))
            max_coefficient = max(max_coefficient, abs(c))
        update(rows, event)
        peak = max(peak, sum(abs(x) for x in rows[a]))
    return rows, dict(integer_grid_bits=0, row_l1_prefix=max(peak, temporary),
        coefficient_times_source_l1=temporary, endpoint_row_l1=max(sum(abs(x) for x in row) for row in rows),
        maximum_gate_coefficient=max_coefficient)


def central(k, intersection):
    r = (k-1)//2
    value = Q(1)
    for j in range(r):
        value *= Q(intersection-(2*j+1), 2*(j+1))
    return value


def matrix_product(a, b):
    columns = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, col)) for col in columns] for row in a]


def experiment(case):
    h, k = case; r = (k-1)//2; q, v = comb(h, r), comb(h, k)
    features, sources, word = complete_word(h, k, r)
    if len(features) != q or len(sources) != v or set(features) != set(standard(h, r)):
        raise ValueError('Recursive layout is incomplete')
    if any(b not in set(features) for a in features for j in range(a.bit_count()+1)
           for indices in combinations([i for i in range(h) if a >> i & 1], j)
           for b in [sum(1 << i for i in indices)]):
        raise ValueError('Ballot family is not subset closed')
    actual, forward_guard = replay_matrix(word, v)
    expected = [[int(a & s == a) for s in sources] for a in features]
    expected += [[int(j == i) for j in range(v)] for i in range(q, v)]
    if actual != expected:
        raise ValueError('Complete in-place basis word differs from all incidence columns')
    actual_inverse, inverse_guard = replay_matrix(inverse_word(word), v)
    for event in inverse_word(word):
        update(actual, event)
    if actual != [[int(i == j) for j in range(v)] for i in range(v)]:
        raise ValueError('All source/null columns failed exact inverse replay')
    M = [row[:q] for row in expected[:q]]
    Mi = [row[:q] for row in actual_inverse[:q]]
    if matrix_product(M, Mi) != [[int(i == j) for j in range(q)] for i in range(q)] or \
            matrix_product(Mi, M) != [[int(i == j) for j in range(q)] for i in range(q)]:
        raise ValueError('Two-sided integral pivot inverse failed')
    values = [central(k, t) for t in range(k+1)]
    if any(x.denominator & (x.denominator-1) for x in values):
        raise ValueError('An integer-overlap central value has a non-dyadic denominator')
    denominator = max(x.denominator for x in values)
    central_numerators = [int(x*denominator) for x in values]
    feature_columns = [[i for i, a in enumerate(features) if a & s == a] for s in sources]
    decoder_peak = 0; digest = sha256(); entries = 0
    for target in sources:
        pivot_row = [central_numerators[(target & s).bit_count()] for s in sources[:q]]
        decoder = [sum(pivot_row[j]*Mi[j][i] for j in range(q)) for i in range(q)]
        decoder_peak = max(decoder_peak, *(abs(x) for x in decoder))
        digest.update(json.dumps(decoder, separators=(',', ':')).encode())
        for source, column in zip(sources, feature_columns):
            if sum(decoder[i] for i in column) != central_numerators[(target & source).bit_count()]:
                raise ValueError('Ballot decoder failed a central source/target entry')
            entries += 1
    # Dirty control: all initial null data persist; dropping their identity
    # coordinates makes a singular matrix whenever a null bank is present.
    if v > q and any(actual_inverse[j][j] != 1 for j in range(q, v)):
        raise ValueError('Null identity coordinates were not preserved')
    nnz = sum(len(column) for column in feature_columns)
    count_formula = sum((comb(h, j)-(comb(h, j-1) if j else 0))*comb(h-j, k-j) for j in range(r+1))
    if nnz != count_formula or nnz > v*sum(comb(k, j) for j in range(r+1)):
        raise ValueError('Complete incidence gather count failed')
    return dict(h=h, k=k, r=r, center_rank=q, data_banks=v,
        features_and_source_layout_sha256=sha256(json.dumps([features,sources]).encode()).hexdigest(),
        full_basis_columns_and_inverses_checked=v, full_central_entries_checked=entries,
        pivot_inverse_integer=True, pivot_inverse_maximum=max(abs(x) for row in Mi for x in row),
        complete_word_gates=len(word), additions=sum(e[0]=='add' for e in word),
        exchanges=sum(e[0]=='swap' for e in word), negations=sum(e[0]=='negate' for e in word),
        feature_gather_nonzeros=nnz, feature_gather_bound_per_source=sum(comb(k, j) for j in range(r+1)),
        center_decoder_common_denominator=denominator, decoder_maximum_numerator=decoder_peak,
        decoder_sha256=digest.hexdigest(), forward_prefix=forward_guard, inverse_prefix=inverse_guard,
        grid_scope='Every literal gate is an integer shear, sign or exchange on one common actual frame',
        native_frame_routing_precision_transfer=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(); config = json.loads(CONFIG.read_text())
    cases = [tuple(c) for c in config['small_cases' if args.small else 'cases']]
    paths = [Path(__file__).resolve(), CONFIG]
    hashes = {str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        source_config_sha256=hashes, cases=cases, primary_input=config['primary_input'], seed=None,
        scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(experiment, cases))
    if any(sha256((TOPIC/p).read_bytes()).hexdigest() != digest for p, digest in hashes.items()):
        raise ValueError('Sources changed during attempt')
    result = dict(status='INTEGRAL BALLOT CENTER COMPLETION PASS', cases=rows,
        seconds=time.monotonic()-started, scope=config['scope'],
        all_size_claim='Analytic unimodular block induction; finite checks support but do not formalize it',
        uniform_all_h_prefix_bound_proved=False, native_circuit_or_exponent_claim=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','seconds','scope']}))


if __name__ == '__main__':
    main()
