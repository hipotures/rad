#!/usr/bin/env python3
"""Bounded exact controls for the complete-word scalar and frame engine.

No many-label discovery sweep is run. This checks complete dirty scalar
columns, graph-versus-chronological rank cost, exact binary expansion and
matched corruptions. It does not certify Gaussian lifts or a new exponent.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import random

import global_word_frame_search as g


def chronological(word,labels,frames,starts,ends):
    current=list(starts);hist=Counter();h=len(starts[0])
    for j,(a,b,_) in enumerate(word):
        F=frames[labels[j]]
        for role in (a,b):
            r=g.distance(current[role],F,h)
            if r:hist[r]+=1
            current[role]=F
    for role,F in enumerate(ends):
        r=g.distance(current[role],F,h)
        if r:hist[r]+=1
    return sum(r*c for r,c in hist.items())


def verify():
    h=4;k=3;dag=g.cancellation_dag(h,k);word,w=g.scalar_word(dag);v=len(dag['top'])
    scalar=g.scalar_replay(dag,word,w);negative=g.scalar_replay(dag,word,w,True)
    frames=[g.le(E,h) for E in g.subspaces(h)];ids={F:j for j,F in enumerate(frames)}
    zero=g.le((),h);full=g.le(tuple(1<<j for j in range(h)),h)
    starts=[g.le((T,),h) for T in dag['top']]+[zero]*(w-v)
    ends=[full]*v+[g.le(g.perpendicular((T,),h),h) for T in dag['top']]+[full]*(w-2*v)
    table=[[g.distance(a,b,h) for b in frames] for a in frames];dist=lambda a,b:table[a][b]
    edges,boundaries,constant=g.incidence_graph(word,w,starts,ends)
    unary=[[sum(dist(j,ids[F]) for F in B) for j in range(len(frames))] for B in boundaries]
    rng=random.Random(20261008);controls=0
    for labels in [[ids[zero]]*len(word),[ids[full]]*len(word)]+[
            [rng.randrange(len(frames)) for _ in word] for _ in range(8)]:
        graph=g.energy(labels,edges,unary,dist,constant);literal=chronological(word,labels,frames,starts,ends)
        if graph!=literal:raise ValueError('All chronological wire transitions disagree with incidence graph')
        if literal<sum(g.distance(a,b,h) for a,b in zip(starts,ends)):
            raise ValueError('Complete endpoint bound was omitted')
        controls+=1
    baseline=[ids[zero]]*len(word)
    if g.energy(baseline,edges,unary,dist,constant)!=w*h:
        raise ValueError('Whole-word stock baseline is incorrect')
    # An omitted dirty completion falsely manufactures a rank deficit.
    wrong_ends=list(ends);wrong_ends[-1]=zero
    e,b,c=g.incidence_graph(word,w,starts,wrong_ends)
    u=[[sum(dist(j,ids[F]) for F in B) for j in range(len(frames))] for B in b]
    omitted_dirty=g.energy(baseline,e,u,dist,c)
    if omitted_dirty!=w*h-h or omitted_dirty==chronological(word,baseline,frames,starts,ends):
        raise ValueError('Dirty-endpoint corruption was not detected')
    labels=[rng.randrange(len(frames)) for _ in word]
    broken=[e for e in edges if dist(labels[e[0]],labels[e[1]])]
    if not broken:raise ValueError('Missing-edge control has no active charged edge')
    altered=list(edges);altered.remove(broken[0])
    if g.energy(labels,altered,unary,dist,constant)==chronological(word,labels,frames,starts,ends):
        raise ValueError('Missing chronological transition was not detected')
    # A radical-containing support is admissible; do not reintroduce a graph-chart restriction.
    radical=(3,);L=g.le(radical,h)
    if len(L)!=h or any(g.pairing(a,b,h) for a in L for b in L):
        raise ValueError('Degenerate L_E was incorrectly rejected')
    binary=g.binary_controls()
    return dict(status='PASS EXACT BOUNDED WORD CONTROLS',recorded_utc=datetime.now(timezone.utc).isoformat(),
                h=h,k=k,complete_scalar_columns=w,source_columns=v,sink_columns=v,dirty_columns=w-2*v,
                scalar_replay=scalar,scalar_corruption=negative,chronological_graph_checks=controls,
                binary_expansion_controls=binary,complete_payload_stock=w,capacity=w*h,
                false_dirty_omission_rank=omitted_dirty,matched_negative_controls=['omitted source subtraction','omitted dirty endpoint','omitted positive chronological transition'],
                scope='Complete rational scalar map and arbitrary-dirty/source restoration, exact rank accounting for all common-frame incidences/endpoints, finite binary mincut controls. No many-label optimum, Gaussian operator lift, native tape or exponent is certified.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args()
    files=[Path(__file__),Path(g.__file__),Path(g.__file__).with_name('lagrangian_graph_completion.py'),
           Path(g.__file__).with_name('trimmed_zeta_dirty_probe.py'),g.SIDE_SOURCE]
    result=verify();result['source_sha256']={F.name:sha256(F.read_bytes()).hexdigest() for F in files}
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','complete_scalar_columns','chronological_graph_checks','scope')}))


if __name__=='__main__':main()
