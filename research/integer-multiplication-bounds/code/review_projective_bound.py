#!/usr/bin/env python3
"""Exact positive-ambient projective bound for intersection-one triples.

Small spectra are checked by an integer annihilating polynomial and trace
moments. The h=8 seven-color control is independently enumerated.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb, ceil
from pathlib import Path
import time


def eigenvalues(h):
    return (3*comb(h-3, 2), Q((h-9)*(h-4), 2), -(2*h-11), 3)


def small_spectrum(h):
    triples = list(combinations(range(h), 3))
    v = len(triples)
    neighbors = [[j for j, b in enumerate(triples) if len(set(a)&set(b)) == 1]
                 for a in triples]
    degree = 3*comb(h-3, 2)
    assert all(len(row) == degree for row in neighbors)
    values = eigenvalues(h)
    assert len(set(values)) == 4
    multiplicities = [1]+[comb(h, j)-comb(h, j-1) for j in range(1, 4)]
    ident = [[int(i == j) for j in range(v)] for i in range(v)]
    current = ident
    moments = []
    for power in range(4):
        actual_trace = sum(current[i][i] for i in range(v))
        expected_trace = sum(mult*value**power for mult, value in zip(multiplicities, values))
        assert actual_trace == expected_trace
        moments.append(actual_trace)
        current = [[sum(current[k][j] for k in neighbors[i]) for j in range(v)]
                   for i in range(v)]
    product = ident
    for value in values:
        product = [[sum(product[k][j] for k in neighbors[i])-value*product[i][j]
                    for j in range(v)] for i in range(v)]
    assert all(x == 0 for row in product for x in row)
    # Four distinct roots and the first four moments determine their exact
    # multiplicities. No floating eigensolver is used.
    return dict(h=h, vertices=v, degree=degree,
                eigenvalues=[str(x) for x in values],
                multiplicities=multiplicities, trace_moments=moments,
                integer_annihilating_polynomial_entries_checked=v*v)


def control():
    triples = list(combinations(range(8), 3))
    colors = []
    for a, b, c in triples:
        normals = [n for n in range(1, 8)
                   if (n&(a^b)).bit_count() % 2 == 0
                   and (n&(a^c)).bit_count() % 2 == 0]
        assert len(normals) == 1
        colors.append(normals[0])
    edges = 0
    for i, a in enumerate(triples):
        for j, b in enumerate(triples[:i]):
            if len(set(a)&set(b)) == 1:
                assert colors[i] != colors[j]
                edges += 1
    assert len(set(colors)) == 7
    # Place each vertex's rank-two plane on the two standard coordinate
    # axes of its color. Distinct-color planes are Euclidean orthogonal.
    return dict(h=8, colors=7, vertices=len(triples), edges_checked=edges,
                ambient_dimension=14, plane_rank=2,
                exact_control_attains_positive_ambient_lower_bound=True)


def bound(h, rank=2):
    degree, a, b, c = eigenvalues(h)
    smallest = min(a, b, c)
    assert smallest < 0
    ratio = 1-Q(degree)/smallest
    if h >= 7:
        assert smallest == -(2*h-11)
        assert ratio == Q((h-1)*(3*h-14), 2*(2*h-11))
    return dict(h=h, plane_rank=rank, degree=degree,
                least_eigenvalue=str(smallest),
                ambient_dimension_per_plane_rank_lower_bound=str(ratio),
                minimum_integer_ambient_dimension=ceil(rank*ratio))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    started = time.monotonic()
    result = dict(code_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  small_exact_spectra=[small_spectrum(h) for h in (6, 8)],
                  exact_h8_control=control(),
                  positive_ambient_bounds=[bound(h) for h in (6, 8, 24, 48, 50, 52)],
                  wall_seconds=time.monotonic()-started,
                  hypotheses='Real Euclidean or complex Hermitian positive-definite ambient form, rank-r orthogonal projectors, graph edges orthogonal; no faithful-nonedge condition',
                  scope='Does not apply to an indefinite ambient form, even when every individual plane is positive')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
