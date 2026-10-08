#!/usr/bin/env python3
"""Scoped negative for one fixed endpoint carried into every middle gate.

This tests the literal union rule and fixed original data terminals. It
does not exclude role-specific matched carry charts or changed endpoints.
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
import time

from downstream_gaussian import require
from downstream_parameter_optimum import as_strings


def mm(a, b):
    return [[sum((x*y for x, y in zip(row, col)), Q(0)) for col in zip(*b)] for row in a]


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def kron(a, b):
    return [[x*y for x in ar for y in br] for ar in a for br in b]


def rank(a):
    rows = [list(row) for row in a];i = 0
    for j in range(len(rows[0])):
        p = next((k for k in range(i, len(rows)) if rows[k][j]), None)
        if p is None:continue
        rows[i], rows[p] = rows[p], rows[i];pivot = rows[i][j]
        rows[i] = [x/pivot for x in rows[i]]
        for k in range(i+1, len(rows)):
            if rows[k][j]:
                c = rows[k][j];rows[k] = [x-c*y for x, y in zip(rows[k], rows[i])]
        i += 1
        if i == len(rows):break
    return i


def small(h):
    I = eye(h);C = (0, 1, 2);A = tuple(range(h-3, h))
    def p(T):
        # Triple norm is2 in I-J/9; the metric dual is(t/2-1/6).
        return [[Q(i in T)*(Q(j in T, 2)-Q(1, 6)) for j in range(h)] for i in range(h)]
    pa, pc = p(A), p(C);full = eye(h*h);carried = kron(I, pc)
    good = bad = entries = 0
    for T in combinations(range(h), 3):
        lost = kron(pa, p(T));K = [[x-y for x, y in zip(a, b)] for a, b in zip(full, lost)]
        overlap = len(set(C).intersection(T));orthogonal = overlap == 1
        contained = mm(K, carried) == carried
        joined_rank = rank([a+b for a, b in zip(K, carried)])
        require(contained == orthogonal and rank(K) == h*h-1 and
                joined_rank == (h*h-1 if orthogonal else h*h),
                'Literal carried-endpoint target containment/span differs')
        if orthogonal:good += 1
        else:
            bad += 1
            require(rank(lost) == 1 and mm(lost, lost) == lost,
                    'Forced terminal loss is not a nondegenerate rank-one projector')
        entries += h**4
    require(good == 3*comb(h-3, 2) and good+bad == comb(h, 3),
            'Small exact triple orthogonality count differs')
    return dict(h=h, local_dimension=h*h, exact_targets=good+bad, good=good, bad=bad,
                exact_matrix_entries=entries, all_span_and_projector_ranks_exact=True,
                qualification='Local chart only; no complete small-ground fast bit primitive asserted')


def count(h):
    v = comb(h, 3);N = v**3;good = 3*comb(h-3, 2);bad = v-good
    forced = v*v*bad;excess = 2*forced-N
    require(excess > 0, 'Chosen large ground lacks the strict negative rank budget')
    return dict(h=h, v=v, N=N, targets_orthogonal_to_carried_line=good,
                targets_not_orthogonal=bad, forced_decreasing_rank=forced,
                strict_excess_over_entire_available_deficit=excess,
                lower_bound='s>=W_new*m-N+2*forced_decreasing_rank>W_new*m',
                even_if_all_original_central_decreases_removed=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args();require(not args.output.exists(), 'Use a fresh output path')
    start = time.monotonic();source = Path(__file__)
    rows = [small(h) for h in (4, 6)]
    budgets = [count(h) for h in (39, 49, 51, 52, 53, 56)]
    result = dict(status='PASS SCOPED NEGATIVE: FIXED COMMON ENDPOINT UNION FAILS RANK DEFICIT',
                  campaign_start='2026-10-07T22:25:21Z', campaign_original_deadline='2026-10-08T08:25:21Z',
                  campaign_deadline='2026-10-08T10:00:00Z', generated_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256={source.name: sha256(source.read_bytes()).hexdigest()},
                  small_exact_rows=rows, exact_large_ground_budgets=budgets,
                  elapsed_seconds=time.monotonic()-start,
                  analytic_interface=dict(carried='E=F tensor line(t_C) tensor Q',
                      middle_base='D0=line(t_A)^perp tensor F tensor Q',
                      prescribed_Y_target='K_T=D0+line(t_A) tensor line(t_T)^perp tensor Q',
                      span_rule='When pairing(t_C,t_T)!=0, K_T+E=F tensor F tensor Q',
                      forced_loss='The carried target gate includes u_A tensor t_T tensor Q; its prescribed final Y route excludes it',
                      rank_budget='All unchanged projector differences have rank>=absolute dimension change; each forced descending rank contributes twice to rank-minus-signed-dimension. The fixed negative source corrections contributeN.'),
                  scope='Rejects unioning one same first-stage endpoint into EVERY middle gate, retaining original data/source/sink labels and scalar permutation. Role-specific matched carries, changed gate charts and alternative terminal contracts are separate hypotheses.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True)+'\n')
    for row in rows:print('LOCAL CARRY CONTROL', row, flush=True)
    for row in budgets:print('STRICT LARGE-GROUND NEGATIVE', row['h'], row['strict_excess_over_entire_available_deficit'], flush=True)


if __name__ == '__main__':
    main()
