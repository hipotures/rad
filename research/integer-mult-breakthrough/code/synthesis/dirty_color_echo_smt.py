#!/usr/bin/env python3
"""Exact finite-label search for a dirty rank-one center echo and side map.

Orthogonal axis labels form one color class. The center J is copied through
one arbitrary-dirty helper using an echo; I-J is direct off-diagonal shears.
No source/sink pair has a literal matched copy. Every scalar column, dirty
restoration and selected frame edge is independently replayed. All-Lagrangian
labels lift the L_E restriction, but literal Gaussian/native costs stay open.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import importlib.metadata
import json
from pathlib import Path
import sys
import time

import z3
import global_word_frame_search as f


def scalar_word(m,chronology):
    helper=2*m
    side=[(m+i,j,Q(-1)) for i in range(m) for j in range(m) if i!=j]
    minus=[(m+i,helper,Q(-1)) for i in range(m)]
    gather=[(helper,i,Q(1)) for i in range(m)]
    plus=[(m+i,helper,Q(1)) for i in range(m)]
    ungather=[(helper,i,Q(-1)) for i in reversed(range(m))]
    if chronology=='center-first':return minus+gather+plus+ungather+side
    if chronology=='side-first':return side+minus+gather+plus+ungather
    if chronology=='side-inside':return minus+gather+side+plus+ungather
    raise ValueError('Unknown exact center/side chronology')


def replay(word,m,corrupt=False):
    w=2*m+1;rows=[{j:Q(1)} for j in range(w)]
    for step,(a,b,c) in enumerate(word):
        if corrupt and step==0:c=-c
        for j,q in list(rows[b].items()):
            z=rows[a].get(j,Q())+c*q
            if z:rows[a][j]=z
            else:rows[a].pop(j,None)
    expected=[{j:Q(1)} for j in range(w)]
    for j in range(m):expected[m+j][j]=Q(1)
    bad=[j for j in range(w) if rows[j]!=expected[j]]
    if bool(bad)!=corrupt:raise ValueError('Exact dirty center echo scalar word failed')
    witness=None
    if bad:
        a=bad[0];j=next(j for j in sorted(set(expected[a])|set(rows[a])) if expected[a].get(j,Q())!=rows[a].get(j,Q()))
        witness=dict(output_role=a,initial_column=j,expected=str(expected[a].get(j,Q())),observed=str(rows[a].get(j,Q())))
    return dict(status='CORRUPTION DETECTED' if corrupt else 'EXACT ALL SCALAR COLUMNS PASS',
                initial_columns=w,arbitrary_dirty_helpers=1,helper_data_columns_restored=True,witness=witness)


def probe(spec):
    n,m,kind,chronology,seconds,seed=spec;started=time.monotonic();word=scalar_word(m,chronology);w=2*m+1
    if m>n:raise ValueError('Axis color labels require at most n data roles')
    positive=replay(word,m);negative=replay(word,m,True)
    zero=f.le((),n);full=f.le(tuple(1<<j for j in range(n)),n)
    starts=[f.le((1<<j,),n) for j in range(m)]+[zero]*(m+1)
    ends=[full]*m+[f.le(f.perpendicular((1<<j,),n),n) for j in range(m)]+[full]
    domain=f.lagrangians(n) if kind=='all-Lagrangian' else [f.le(E,n) for E in f.subspaces(n)]
    domain=sorted(domain);frames=len(domain);table=[[f.distance(a,b,n) for b in domain] for a in domain]
    ids={L:j for j,L in enumerate(domain)};edges,boundaries,constant=f.incidence_graph(word,w,starts,ends)
    unary=[[sum(table[j][ids[F]] for F in boundary) for j in range(frames)] for boundary in boundaries]
    solver=z3.Solver();solver.set(timeout=seconds*1000,random_seed=seed,max_memory=512)
    labels=[z3.Int('frame_'+str(j)) for j in range(len(word))]
    for label in labels:solver.add(label>=0,label<frames)
    # One immutable complete finite distance array is shared by all edges.
    # Unlisted pairs have maximal rank; every smaller distance is a literal
    # exact table entry. No learned relaxation substitutes for this model.
    distances=z3.K(z3.IntSort(),z3.IntVal(n))
    for a in range(frames):
        for b in range(frames):
            if table[a][b]!=n:distances=z3.Store(distances,a*frames+b,table[a][b])
    charges=[weight*z3.Select(distances,labels[a]*frames+labels[b]) for a,b,weight in edges]
    for node,costs in enumerate(unary):
        if any(costs):charges.append(z3.Sum([z3.If(labels[node]==j,cost,0) for j,cost in enumerate(costs) if cost]))
    capacity=w*n;budget=capacity-1;solver.add(z3.Sum(charges)+constant<=budget)
    answer=solver.check();assignment=None;receipt=None;hist=None
    if answer==z3.sat:
        model=solver.model();assignment=[model.eval(label).as_long() for label in labels]
        energy=f.energy(assignment,edges,unary,lambda a,b:table[a][b],constant)
        current=list(starts);hist=Counter()
        for gate,(a,b,c) in enumerate(word):
            common=domain[assignment[gate]]
            for role in (a,b):
                r=f.distance(current[role],common,n)
                if r:hist[r]+=1
                current[role]=common
        for role,F in enumerate(ends):
            r=f.distance(current[role],F,n)
            if r:hist[r]+=1
        if sum(r*count for r,count in hist.items())!=energy or energy>budget:
            raise ValueError('Exact complete frame candidate does not replay solver cost')
        receipt=dict(rank_charge=energy,capacity=capacity,deficit=capacity-energy,
                     chronological_histogram=dict(sorted(hist.items())),
                     optimistic_homogeneous_moment_at_kappa_1e_4=sum(r*count*2**(1e-4*(n-r)) for r,count in hist.items())/capacity)
    return dict(status='EXACT FINITE FRAME DEFICIT FOUND' if answer==z3.sat else
                'UNSAT IN COMPLETE DECLARED FINITE FRAME MODEL' if answer==z3.unsat else 'UNKNOWN RESOURCE LIMIT',
                active_bits=n,color_size=m,frame_kind=kind,chronology=chronology,source_seed=seed,
                frame_count=frames,payload_stock=w,arbitrary_dirty_helpers=1,scalar_shears=len(word),
                capacity=capacity,strict_deficit_budget=budget,complete_endpoint_floor=sum(f.distance(a,b,n) for a,b in zip(starts,ends)),
                solver_result=str(answer),solver_unknown_reason=solver.reason_unknown() if answer==z3.unknown else None,
                timeout_seconds=seconds,memory_limit_MiB=512,statistics=str(solver.statistics()),
                exact_scalar_replay=positive,scalar_corruption=negative,candidate=receipt,
                selected_frames=domain if assignment else None,word=[dict(destination=a,source=b,coefficient=str(c),common_frame=assignment[j]) for j,(a,b,c) in enumerate(word)] if assignment else None,
                seconds=time.monotonic()-started,
                scope='Complete exact scalar center/side word with arbitrary-dirty helper and fixed original source/sink/helper endpoints. Full declared finite frame domain and all transitions are charged. SAT gets exact geometric replay; UNSAT is this word/domain only; UNKNOWN is inconclusive. Literal Gaussian lifts, residual frame gauges, native tape/precision costs and a full exponent result are unproved.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4);parser.add_argument('--timeout',type=int,default=60);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    specs=[(3,3,'L_E','center-first',args.timeout,20261009011),
           (3,3,'all-Lagrangian','center-first',args.timeout,20261009012),
           (3,3,'all-Lagrangian','side-first',args.timeout,20261009013),
           (3,3,'all-Lagrangian','side-inside',args.timeout,20261009014)]
    paths=[Path(__file__),Path(f.__file__),Path(f.__file__).with_name('lagrangian_graph_completion.py'),
           Path(f.__file__).with_name('trimmed_zeta_dirty_probe.py'),f.SIDE_SOURCE]
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,specs=specs,
                  source_sha256={p.name:v for p,v in hashes.items()},z3_solver_distribution_version=importlib.metadata.version('z3-solver'),
                  z3_engine_version=z3.get_version_string(),query='Strict all-endpoint rank deficit for one dirty center echo and orthogonal off-diagonal side shears')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');cases=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();cases.append(result)
            print(json.dumps({key:result[key] for key in ('status','active_bits','frame_kind','chronology','solver_result','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=v for p,v in hashes.items()):raise ValueError('Effective source changed during experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=cases),indent=2)+'\n')


if __name__=='__main__':main()
