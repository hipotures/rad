#!/usr/bin/env python3
"""Exact bounded controls for the rational vertex-feature uniqueness proof.

For h >= 6, each column M(S,T)=sum_{i in S} z_i is forced to the
retained fitting map by its diagonal and intersection-one zero conditions.
This scope does not include general pair features or general fitting maps.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path

from review_rational_frames import basis


def rank(rows):
    return len(basis(rows))


def column_control(h):
    triples = list(combinations(range(h), 3))
    target = (0, 1, 2)
    constraints = [s for s in triples if len(set(s) & set(target)) == 1]
    values = [Q(1, 3) if i in target else -Q(1, 6) for i in range(h)]
    rows = [[Q(i in s) for i in range(h)] for s in constraints + [target]]
    right = [Q(0)]*len(constraints)+[Q(1)]
    assert all(sum(a*b for a, b in zip(row, values)) == b
               for row, b in zip(rows, right))
    assert rank(rows) == h
    incidence = [[Q(i in s) for i in range(h)] for s in triples]
    assert rank(incidence) == h
    hessian = [[Q(i == j)-Q(1, 9) for j in range(h)] for i in range(h)]
    gram_rank = rank(hessian)
    assert gram_rank == (h-1 if h == 9 else h)
    result = dict(h=h, canonical_target=list(target),
                  constraints=len(rows), unique_column= [str(x) for x in values],
                  constraint_rank=h, incidence_rank=h,
                  retained_hessian_rank=gram_rank)
    if h in (6, 8, 9):
        fitting = [[Q(len(set(s) & set(t))-1, 2) for t in triples]
                   for s in triples]
        assert rank(fitting) == gram_rank
        result['independent_full_fitting_rank'] = gram_rank
    return result


def xor_feature_screen(h):
    """Test a specific translation-invariant binary Fourier row ansatz.

    Its normal coordinates count source triples lying in a binary
    hyperplane. This includes the known h8 seven-color row space.
    Full constraint rank at h16 excludes this row space, not every
    rational pair-feature construction of rank15.
    """
    assert h in (8, 16)
    target = (0, 1, 2)
    triples = list(combinations(range(h), 3))
    rows = []
    for s in triples:
        a, b, c = s
        rows.append([Q((n & (a ^ b)).bit_count() % 2 == 0
                       and (n & (a ^ c)).bit_count() % 2 == 0)
                     for n in range(1, h)])
    edge_rows = [r for s, r in zip(triples, rows)
                 if len(set(s) & set(target)) == 1]
    target_row = rows[triples.index(target)]
    edge_rank = rank(edge_rows)
    augmented_rank = rank(edge_rows+[target_row])
    return dict(h=h, normal_coordinates=h-1, edge_rows=len(edge_rows),
                full_row_rank=rank(rows), edge_constraint_rank=edge_rank,
                edge_plus_target_rank=augmented_rank,
                fitting_column_possible=augmented_rank > edge_rank,
                scope='Fixed XOR/normal pair-feature row space only')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    result = dict(generated_at=datetime.now(timezone.utc).isoformat(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  column_controls=[column_control(h) for h in range(6, 13)],
                  xor_screens=[xor_feature_screen(h) for h in (8, 16)],
                  optimistic_h9_quotient_count_screen={
                      'triple_count':comb(9, 3), 'ambient_dimension':8,
                      'ground_times_ambient':72,
                      'uniform_deficit_per_N':str(1-Q(6*72, comb(9, 3))),
                      'one_outer_axis_deficit_loss_per_N':str(Q(4*72, comb(9, 3))),
                      'one_middle_axis_deficit_loss_per_N':str(Q(2*72, comb(9, 3))),
                      'scope':'Optimistic retained-motif count screen only; no quotient transfer certified'},
                  proof_scope='Rational vertex-feature columns for h>=6; does not exclude pair-feature or unrestricted lower-rank maps')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'vertex_controls':len(result['column_controls']),
                      'xor_screens':result['xor_screens'], 'status':'PASS'}))


if __name__ == '__main__':
    main()
