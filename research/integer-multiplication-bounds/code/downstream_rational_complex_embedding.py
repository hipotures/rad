#!/usr/bin/env python3
"""Exact scoped obstruction to an intersection-invariant complex-to-bit lift.

The D/E source classes require rational Gram zeros at intersections0 and2.
Every such invariant Gram is gamma*I+delta*A_intersection1. Its incidence
spectrum forces at least C(h,2) dimensions for h>=11. Even an optimistic
endpoint rank budget fails with the retained h central channels.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

from downstream_gaussian import check_sources, require


def rank_mod(rows,p=1000003):
    rows = [[x % p for x in r] for r in rows]
    done = 0
    for col in range(len(rows[0])):
        at = next((i for i in range(done,len(rows)) if rows[i][col]),None)
        if at is None:
            continue
        rows[done],rows[at] = rows[at],rows[done]
        inv = pow(rows[done][col],-1,p)
        rows[done] = [(x*inv)%p for x in rows[done]]
        pivot = rows[done]
        for i in range(done+1,len(rows)):
            c = rows[i][col]
            if c:
                rows[i] = [(x-c*y)%p for x,y in zip(rows[i],pivot)]
        done += 1
    return done


def spectrum(h):
    v,f = comb(h,3),comb(h,2)
    values = [3*comb(h-3,2),(h-4)*(h-9)//2,11-2*h,3]
    multiplicities = [1,h-1,f-h,v-f]
    require(sum(multiplicities) == v, 'Incidence multiplicities do not sum to v')
    if h >= 11:
        require(len(set(values)) == 4 and multiplicities[-1] == max(multiplicities),
                'Declared distinct eigenvalue/minimum rank range failed')
    return values,multiplicities


def tiny(h):
    triples = [frozenset(t) for t in combinations(range(h),3)]
    pairs = [frozenset(t) for t in combinations(range(h),2)]
    B = [[int(p <= t) for p in pairs] for t in triples]
    A = [[int(i in p) for p in pairs] for i in range(h)]
    C = [[int(i in t) for i in range(h)] for t in triples]
    require(all(2*C[j][i] == sum(B[j][k]*A[i][k] for k in range(len(pairs)))
                for i in range(h) for j in range(len(triples))), 'C=B*A^T/2 incidence identity failed')
    Q4 = [[8*int(j==k)-len(pairs[j]&pairs[k]) for k in range(len(pairs))]
          for j in range(len(pairs))]
    qrank,brank = rank_mod(Q4),rank_mod(B)
    require(brank == len(pairs), 'Pair incidence lacks full rational column rank')
    expected = len(pairs)-(1 if h == 5 else h-1 if h == 10 else 0)
    require(qrank == expected, 'Quadratic Gram rank differs at a degeneracy control')
    values,mults = spectrum(h)
    if h >= 11:
        require(qrank == len(pairs) == len(triples)-max(mults),
                'Rational ambient minimum rank differs')
    # Direct Johnson-class multiplication, independent of eigenspaces.
    # Each trace power is a full sum over intermediates for representative
    # pairs S,T at every attainable intersection, not a floating eigenvalue.
    S = triples[0]
    attainable = range(max(0,6-h),4)
    representatives = {r:next(t for t in triples if len(S&t)==r) for r in attainable}
    function = {r:int(r==1) for r in range(4)}
    traces = []
    for power in range(1,7):
        actual = len(triples)*function[3]
        expected_trace = sum(m*t**power for m,t in zip(mults,values))
        require(actual == expected_trace, 'Independent adjacency trace power differs')
        traces.append(actual)
        function = {r:sum(function[len(S&U)] for U in triples if len(U&T)==1)
                    for r,T in representatives.items()}
    return dict(h=h,triples=len(triples),pairs=len(pairs),pair_incidence_rank_mod_prime=brank,
                quadratic_Gram_rank_mod_prime=qrank,prime=1000003,
                exact_six_adjacency_trace_powers=traces,integer_eigenvalues=values,multiplicities=mults)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    started = time.monotonic()
    small = [tiny(h) for h in (5,10,11,12)]
    full = []
    for h in range(11,65):
        values,multiplicities = spectrum(h)
        v,f = comb(h,3),comb(h,2)
        optimistic_D = v*v*(2*v-6*f*h)
        require(optimistic_D == -v*v*h*(h-1)*(8*h+2)//3 < 0,
                'Optimistic central-rank budget unexpectedly positive')
        full.append(dict(h=h,v=v,min_ambient_dimension=f,eigenvalues=values,
                         multiplicities=multiplicities,optimistic_D=optimistic_D))
    result = dict(status='PASS scoped negative: invariant rational D/E lift with retained h centers has negative rank deficit',
                  campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                  campaign_deadline='2026-10-08T08:25:21Z',generated_at=datetime.now(timezone.utc).isoformat(),
                  provenance=check_sources(args.upstream),
                  source_sha256={Path(__file__).name:hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
                  exact_small_controls=small,full_count_and_spectrum_controls=full,
                  elapsed_seconds=time.monotonic()-started,
                  scope='Intersection-invariant rational Gram zeros at0/2, fixed D/E identity and retained h reduced central channels; not a general impossibility for noninvariant labels, different correction circuits or routing algorithms')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS invariant rational lift obstruction',len(full),'grounds and',len(small),'independent rank/trace controls',flush=True)


if __name__ == '__main__':
    main()
