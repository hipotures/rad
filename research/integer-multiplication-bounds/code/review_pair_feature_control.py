#!/usr/bin/env python3
"""Exact degree-two h8 rank-seven fitting control and graph orientation."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb, ceil
from pathlib import Path

from review_rational_frames import basis


def rank(a):
    return len(basis(a))


def fano_clique(h):
    assert h >= 7
    lines = {tuple(sorted((a-1, b-1, (a^b)-1))) for a in range(1, 8)
             for b in range(a+1, 8) if a^b}
    assert len(lines) == 7
    assert all(len(set(a)&set(b)) == 1 for a, b in combinations(lines, 2))
    return sorted(lines)


def control():
    triples = list(combinations(range(8), 3))
    pairs = list(combinations(range(8), 2))
    incidence = [[Q(set(pair) <= set(t)) for pair in pairs] for t in triples]
    coefficients = []
    for a, b in pairs:
        row = []
        for n in range(1, 8):
            la, lb = (n&a).bit_count() % 2, (n&b).bit_count() % 2
            value = Q(1, 3)-Q(la+lb, 2)+la*lb
            assert value == (Q(1, 3) if la == lb else -Q(1, 6))
            row.append(value)
        coefficients.append(row)
    columns = [[sum(a*b for a, b in zip(row, col))
                for col in zip(*coefficients)] for row in incidence]
    colors = []
    for t, row in zip(triples, columns):
        assert sum(row) == 1 and all(value in (0, 1) for value in row)
        color = row.index(Q(1))+1
        a, b, c = t
        assert (color&(a^b)).bit_count() % 2 == 0
        assert (color&(a^c)).bit_count() % 2 == 0
        colors.append(color)
    gram = [[sum(a*b for a, b in zip(row, other)) for other in columns]
            for row in columns]
    edges = 0
    for i, a in enumerate(triples):
        assert gram[i][i] == 1
        for j, b in enumerate(triples[:i]):
            if len(set(a)&set(b)) == 1:
                assert gram[i][j] == 0
                edges += 1
    assert rank(columns) == rank(coefficients) == rank(gram) == 7
    assert all(colors.count(color) == 8 for color in range(1, 8))
    clique = fano_clique(8)
    assert len({colors[triples.index(t)] for t in clique}) == 7
    return dict(h=8, vertices=56, pair_features=28, fitting_graph='Complement of intersection-one graph',
                feature_coefficient_values=['1/3', '-1/6'], rational_rank=7,
                color_class_sizes=[8]*7, diagonal_entries=1,
                intersection_one_zero_edges_checked=edges,
                exact_lower_bound_clique=7,
                ordinary_and_fractional_Haemers_over_Q_equal_7=True,
                coefficients=[[str(x) for x in row] for row in coefficients],
                coefficient_rows_pairs=[list(x) for x in pairs],
                coefficient_columns_normals=list(range(1, 8)))


def bounds(h):
    clique = max(7, (h-1)//2)
    # These are constructed cliques, not a claim that they are maximum.
    if clique > 7:
        family = [(0, 2*j+1, 2*j+2) for j in range((h-1)//2)]
        assert all(max(t) < h for t in family)
        assert all(len(set(a)&set(b)) == 1 for a, b in combinations(family, 2))
    ambient = h-1 if h == 9 else h
    if h == 8:
        ambient = 7
    return dict(h=h, field_Q_complement_Haemers_lower=clique,
                field_Q_complement_Haemers_explicit_upper=ambient,
                positive_rank_one_lower=ceil(Q((h-1)*(3*h-14), 2*(2*h-11))),
                characteristic_two_complement_block_rank_per_block_lower=str(Q(comb(h, 3), h)),
                characteristic_two_J_graph_value=h if h % 4 == 0 else None)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result = dict(code_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  rank_seven_degree_two_control=control(),
                  constructed_clique_and_vertex_upper_bounds=[bounds(h) for h in (7, 8, 9, 24, 48, 50, 52)],
                  literature_orientation='Bukh--Cox J_h^2 is the intersection-one graph itself; its Haemers matrices vanish on NONedges. Campaign zero-on-intersection-one matrices fit its complement.',
                  scope='Exact h8 degree-two control and elementary bounds; Lemma12 gives no real/rational exact minrank for the campaign complement at h24')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'rank_seven_degree_two_control'}, indent=2))
    print('PASS exact h8 rank7 pair-feature control, 840 edge zeros and 7-clique lower bound')


if __name__ == '__main__':
    main()
