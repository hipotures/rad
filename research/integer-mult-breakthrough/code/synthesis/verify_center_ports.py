#!/usr/bin/env python3
"""Bounded complete center-port scalar and exact binary frame controls."""
import argparse
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path

import center_basis_port_search as p


def verify():
    controls=p.f.binary_controls();cases=[];h=7
    for layout,seed in [('batched',20261008101),('interleaved',20261008102)]:
        operations,labels,permutation,component=p.full_word(h,layout,seed);v=len(labels);w=2*v
        middle=next(j for j,e in enumerate(operations) if e[0]=='add' and e[1]>=v and e[2]<v)
        positive=p.replay(operations,w);negative=p.replay(operations,w,middle)
        word=[(e[1],e[2],e[3]) for e in operations if e[0]=='add'];zero=p.f.le((),h);full=p.f.le(tuple(1<<j for j in range(h)),h)
        starts=[p.f.le((T,),h) for T in labels]+[zero]*v;ends=[full]*v+[p.f.le(p.f.perpendicular((T,),h),h) for T in labels]
        domain=[zero,full];dist=lambda a,b:0 if a==b else h
        edges,boundaries,constant=p.f.incidence_graph(word,w,starts,ends)
        unary=[[sum(p.f.distance(F,L,h) for F in boundary) for L in domain] for boundary in boundaries]
        initial=[0]*len(word);assignment=p.f.alpha_move(initial,1,edges,unary,dist)
        exact_binary=p.f.energy(assignment,edges,unary,dist,constant)
        if exact_binary!=w*h:raise ValueError('Bounded complete zero/full binary frame optimum changed')
        # Independent chronological replay checks all incident ports and returns.
        current=list(starts);hist=Counter()
        for gate,(a,b,c) in enumerate(word):
            F=domain[assignment[gate]]
            for role in (a,b):
                r=p.f.distance(current[role],F,h)
                if r:hist[r]+=1
                current[role]=F
        for role,F in enumerate(ends):
            r=p.f.distance(current[role],F,h)
            if r:hist[r]+=1
        if sum(r*n for r,n in hist.items())!=exact_binary:raise ValueError('Binary all-port chronology does not match cut cost')
        for T in labels:
            if p.f.distance(p.f.le((T,),h),p.f.le(p.f.perpendicular((T,),h),h),h)!=h:
                raise ValueError('Paired-port crossed endpoint anchor failed')
        cases.append(dict(layout=layout,seed=seed,component=component,scalar_replay=positive,scalar_corruption=negative,
                          exact_zero_full_frame_optimum=exact_binary,capacity=w*h,chronological_histogram=dict(sorted(hist.items())),
                          all_middle_ports_orthogonal=True,scalar_gate_counts=dict(Counter(e[0] for e in operations))))
    return dict(status='PASS EXACT BOUNDED CENTER PORT WORDS',recorded_utc=datetime.now(timezone.utc).isoformat(),
                binary_controls=controls,cases=cases,
                scope='Complete bounded arbitrary source/sink scalar words, paid basis/permutation inverses, orthogonal port anchors and exact zero/full binary frame optimization. Larger frame search is heuristic; native Gaussian phase lifts, residual gauges, precision and multiplier recurrence remain unproved.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=verify();paths=[Path(__file__),Path(p.__file__),Path(p.f.__file__),Path(p.f.__file__).with_name('lagrangian_graph_completion.py'),
                        Path(p.f.__file__).with_name('trimmed_zeta_dirty_probe.py'),p.f.SIDE_SOURCE]+[
                        p.COMPLEX/name for name in ('center_basis_scalar_word.py','structured_center_basis.py','center_null_basis.py')]
    result['source_sha256']={path.name:sha256(path.read_bytes()).hexdigest() for path in paths}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(result['cases']),complete_scalar_columns=sum(x['scalar_replay']['initial_columns'] for x in result['cases']))))


if __name__=='__main__':main()
