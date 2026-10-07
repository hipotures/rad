#!/usr/bin/env python3
"""Exact rational frame examples and the rank-one nondegeneracy criterion.

The scalar circuit may be over F_2, but the label form tested here is
the rational matrix I-J/9. No modular evidence is treated as a rational lift.
"""

import argparse
from fractions import Fraction as Q
from itertools import combinations, product
import json
from pathlib import Path


def basis(vectors):
    rows = {}
    for source in vectors:
        v = [Q(x) for x in source]
        for pivot, row in sorted(rows.items()):
            if v[pivot]:
                factor = v[pivot]
                v = [a - factor*b for a, b in zip(v, row)]
        if not any(v):
            continue
        pivot = next(i for i, x in enumerate(v) if x)
        factor = v[pivot]
        rows[pivot] = [x / factor for x in v]
    return [rows[p] for p in sorted(rows)]


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def form(a, b):
    return dot(a, b) - sum(a)*sum(b)/9


def solve(matrix, rhs):
    n = len(rhs)
    rows = [[Q(x) for x in row] + [Q(y)] for row, y in zip(matrix, rhs)]
    for p in range(n):
        j = next(j for j in range(p, n) if rows[j][p])
        rows[p], rows[j] = rows[j], rows[p]
        factor = rows[p][p]
        rows[p] = [x / factor for x in rows[p]]
        for j in range(n):
            if j != p and rows[j][p]:
                factor = rows[j][p]
                rows[j] = [a-factor*b for a, b in zip(rows[j], rows[p])]
    return [row[-1] for row in rows]


def analyze(vectors):
    rows = basis(vectors)
    if not rows:
        return dict(dimension=0, gram_rank=0, radical_dimension=0,
                    euclidean_projection_ones_squared='0', nondegenerate=True)
    euclidean = [[dot(a, b) for b in rows] for a in rows]
    sums = [sum(a) for a in rows]
    coefficients = solve(euclidean, sums)
    projection_squared = dot(sums, coefficients)
    gram = [[form(a, b) for b in rows] for a in rows]
    rank = len(basis(gram))
    assert len(rows) - rank <= 1
    assert (rank == len(rows)) == (projection_squared != 9)
    return dict(dimension=len(rows), gram_rank=rank,
                radical_dimension=len(rows)-rank,
                euclidean_projection_ones_squared=str(projection_squared),
                nondegenerate=rank == len(rows),
                signature=('positive' if projection_squared < 9 else
                           'degenerate' if projection_squared == 9 else 'indefinite'))


def indicator(triple, h):
    return [Q(i in triple) for i in range(h)]


def examples(h=12):
    target = (0, 1, 2)
    sources = [(0, 3, 4), (1, 5, 6), (2, 7, 8)]
    vectors = [indicator(t, h) for t in sources]
    target_vector = indicator(target, h)
    assert all(form(v, target_vector) == 0 for v in vectors)
    radical = [sum(x) for x in zip(*vectors)]
    assert all(form(radical, v) == 0 for v in vectors)
    assert form(radical, radical) == 0
    degenerate = analyze(vectors)
    assert degenerate['radical_dimension'] == 1
    # All target transversals use one point from each disjoint source triple.
    transversals = [tuple(sorted(t)) for t in product(*sources)]
    target_vectors = [indicator(t, h) for t in transversals]
    assert all(form(radical, t) == 0 for t in target_vectors)
    assert all(form(s, t) == 0 for s in vectors for t in target_vectors)
    assert len(basis(target_vectors)) == 7
    assert len(basis(target_vectors + [radical])) == 7
    # A nondegenerate containing span exists for a smaller target family.
    # Its fourth source introduces a point outside the radical's support.
    fourth = (0, 3, 9)
    four = vectors + [indicator(fourth, h)]
    assert form(four[-1], target_vector) == 0
    healed = analyze(four)
    assert healed['nondegenerate'] and healed['signature'] == 'indefinite'
    # Balanced child pairs avoid the degenerate three-source intermediate.
    assert analyze(four[:2])['nondegenerate']
    assert analyze(four[2:])['nondegenerate']
    return dict(h=h, target=target, sources=sources,
                degenerate_span=degenerate,
                radical_support=list(range(9)),
                complete_target_transversal_count=len(transversals),
                complete_target_span_dimension=7,
                no_nondegenerate_nested_repair_for_complete_target_family=True,
                added_source=fourth, balanced_repaired_span=healed,
                scope='Exact examples of label eligibility; no general circuit lower bound.')


def census(h=10):
    triples = list(combinations(range(h), 3))
    count = 0
    degenerate = 0
    positive = 0
    indefinite = 0
    for selected in combinations(triples, 3):
        # Restrict the census to triples with pairwise empty intersection.
        if any(set(a).intersection(b) for a, b in combinations(selected, 2)):
            continue
        result = analyze([indicator(t, h) for t in selected])
        count += 1
        degenerate += not result['nondegenerate']
        positive += result['signature'] == 'positive'
        indefinite += result['signature'] == 'indefinite'
    assert count > 0 and degenerate == count
    return dict(h=h, pairwise_disjoint_three_source_families=count,
                degenerate=degenerate, positive=positive, indefinite=indefinite)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--census-h', type=int, default=10)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = dict(examples=examples(), census=census(args.census_h))
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
