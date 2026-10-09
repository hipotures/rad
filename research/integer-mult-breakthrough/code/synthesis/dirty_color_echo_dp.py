#!/usr/bin/env python3
"""Deterministic exact small-domain center/side optimization via elimination.

Inputs, domain distances, chronological replay and controls are pure Python.
The retained stdlib C++ kernel minimizes finite factors; its compact argument
is independently replayed and bounded controls match complete enumeration.
Build binaries and factor/graph execution payloads remain in ignored work.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import subprocess
import time

import global_word_frame_search as f

CPP=Path(__file__).with_name('frame_variable_elimination.cpp')


def scalar_word(m,chronology):
    helper=2*m;side=[(m+i,j,Q(-1)) for i in range(m) for j in range(m) if i!=j]
    minus=[(m+i,helper,Q(-1)) for i in range(m)];gather=[(helper,i,Q(1)) for i in range(m)]
    plus=[(m+i,helper,Q(1)) for i in range(m)];ungather=[(helper,i,Q(-1)) for i in reversed(range(m))]
    return minus+gather+plus+ungather+side if chronology=='center-first' else side+minus+gather+plus+ungather if chronology=='side-first' else minus+gather+side+plus+ungather


def scalar_replay(word,m):
    w=2*m+1;rows=[{j:Q(1)} for j in range(w)]
    for a,b,c in word:
        for j,q in list(rows[b].items()):
            z=rows[a].get(j,Q())+c*q
            if z:rows[a][j]=z
            else:rows[a].pop(j,None)
    expected=[{j:Q(1)} for j in range(w)]
    for j in range(m):expected[m+j][j]=Q(1)
    if rows!=expected:raise ValueError('Complete independent dirty center echo scalar replay failed')
    return dict(initial_columns=w,source_columns=m,arbitrary_sink_columns=m,arbitrary_dirty_helpers=1,helper_fully_restored=True)


def minfill(vertices,edges):
    graph={i:set() for i in range(vertices)}
    for a,b,c in edges:graph[a].add(b);graph[b].add(a)
    order=[]
    while graph:
        a=min(graph,key=lambda i:(sum(k not in graph[j] for j in graph[i] for k in graph[i] if j<k),len(graph[i]),i))
        neighbors=graph.pop(a);order.append(a)
        for j in neighbors:graph[j].remove(a);graph[j].update(neighbors-{j})
    return order


def solve(binary,work,edges,unary,table,constant=0,order=None):
    vertices=len(unary);domain=len(table);order=minfill(vertices,edges) if order is None else order
    fields=[vertices,domain,constant,2**24]
    fields+=[x for row in table for x in row];fields+=[x for row in unary for x in row]
    fields.append(len(edges));fields+=[x for edge in edges for x in edge];fields+=order
    path=work/'graph.txt';path.parent.mkdir(parents=True,exist_ok=False);path.write_text(' '.join(map(str,fields))+'\n')
    result=subprocess.run([str(binary.resolve()),str(path.resolve())],text=True,capture_output=True,check=True)
    receipt=json.loads(result.stdout);assignment=receipt['assignment']
    if receipt['optimum']!=f.energy(assignment,edges,unary,lambda a,b:table[a][b],constant):
        raise ValueError('C++ min-sum witness fails independent Python graph replay')
    receipt['graph_input_sha256']=sha256(path.read_bytes()).hexdigest();receipt['elimination_order']=order
    return receipt


def controls(binary,work):
    rng=random.Random(20261009);frames=f.lagrangians(2)[:4];table=[[f.distance(a,b,2) for b in frames] for a in frames];receipts=[]
    for case in range(16):
        vertices=3;unary=[[rng.randrange(6) for _ in frames] for _ in range(vertices)]
        edges=[(a,b,rng.randrange(1,4)) for a in range(vertices) for b in range(a+1,vertices) if rng.randrange(2)]
        constant=rng.randrange(4);answer=solve(binary,work/f'control-{case}',edges,unary,table,constant)
        expected=min(f.energy(list(labels),edges,unary,lambda a,b:table[a][b],constant) for labels in product(range(len(frames)),repeat=vertices))
        if answer['optimum']!=expected:raise ValueError('Finite min-sum controls disagree with complete independent enumeration')
        receipts.append(dict(case=case,optimum=expected,graph_input_sha256=answer['graph_input_sha256']))
    return dict(status='PASS INDEPENDENT EXHAUSTIVE MIN-SUM CONTROLS',seed=20261009,cases=receipts,assignments_each=64)


def probe(spec):
    n,m,kind,chronology,binary,work=spec;started=time.monotonic();word=scalar_word(m,chronology);w=2*m+1;scalar=scalar_replay(word,m)
    # Omitted inverse gather corrupts dirty/source columns and must fail.
    try:scalar_replay(word[:-1],m)
    except ValueError:corruption_detected=True
    else:raise ValueError('Omitted exact scalar gate was not detected')
    zero=f.le((),n);full=f.le(tuple(1<<j for j in range(n)),n)
    starts=[f.le((1<<j,),n) for j in range(m)]+[zero]*(m+1);ends=[full]*m+[f.le(f.perpendicular((1<<j,),n),n) for j in range(m)]+[full]
    domain=sorted(f.lagrangians(n) if kind=='all-Lagrangian' else [f.le(E,n) for E in f.subspaces(n)])
    table=[[f.distance(a,b,n) for b in domain] for a in domain];ids={L:j for j,L in enumerate(domain)}
    edges,boundaries,constant=f.incidence_graph(word,w,starts,ends);unary=[[sum(table[j][ids[F]] for F in boundary) for j in range(len(domain))] for boundary in boundaries]
    exact=solve(binary,work,edges,unary,table,constant);current=list(starts);hist=Counter()
    for gate,(a,b,c) in enumerate(word):
        F=domain[exact['assignment'][gate]]
        for role in (a,b):
            r=f.distance(current[role],F,n)
            if r:hist[r]+=1
            current[role]=F
    for role,F in enumerate(ends):
        r=f.distance(current[role],F,n)
        if r:hist[r]+=1
    if sum(r*c for r,c in hist.items())!=exact['optimum']:raise ValueError('Independent all-port path replay differs from exact min-sum optimum')
    capacity=w*n
    return dict(status='EXACT FINITE MINIMUM HAS RANK DEFICIT' if exact['optimum']<capacity else 'EXACT FINITE MINIMUM HAS NO RANK DEFICIT',
                active_bits=n,color_size=m,frame_kind=kind,chronology=chronology,frame_count=len(domain),scalar_shears=len(word),
                payload_stock=w,capacity=capacity,minimum_rank_charge=exact['optimum'],deficit=capacity-exact['optimum'],
                scalar_replay=scalar,omitted_gate_control=corruption_detected,exact_min_sum=exact,
                chronological_histogram=dict(sorted(hist.items())),complete_frames=domain,
                word=[dict(destination=a,source=b,coefficient=str(c),frame=exact['assignment'][j]) for j,(a,b,c) in enumerate(word)],
                seconds=time.monotonic()-started,
                scope='Deterministic exact finite-label minimum for this full scalar dirty center echo and side chronology; complete independent rank replay and bounded solver controls. All-Lagrangian or L_E domain as stated, not a universal circuit obstruction. Literal Gaussian operators, gauges, tape costs, precision and exponent remain unproved.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4);parser.add_argument('--cxx',default='c++');args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False);build=args.output.parent/'builds';build.mkdir(exist_ok=False);binary=build/'frame-variable-elimination'
    command=[args.cxx,'-O3','-std=c++17',str(CPP.resolve()),'-o',str(binary.resolve())];subprocess.run(command,check=True,capture_output=True,text=True)
    compiler=subprocess.run([args.cxx,'--version'],check=True,text=True,capture_output=True).stdout.splitlines()[0]
    paths=[Path(__file__),CPP,Path(f.__file__),Path(f.__file__).with_name('lagrangian_graph_completion.py'),Path(f.__file__).with_name('trimmed_zeta_dirty_probe.py'),f.SIDE_SOURCE]
    hashes={path:sha256(path.read_bytes()).hexdigest() for path in paths};work=args.output.parent/'derived'
    specs=[(2,2,'all-Lagrangian','center-first',binary,work/'case-0'),(3,3,'L_E','center-first',binary,work/'case-1'),
           (3,3,'L_E','side-first',binary,work/'case-2'),(3,3,'L_E','side-inside',binary,work/'case-3')]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,
                  specs=[list(spec[:4]) for spec in specs],source_sha256={path.name:digest for path,digest in hashes.items()},
                  compiler=compiler,compile_arguments=[args.cxx,'-O3','-std=c++17','code/synthesis/frame_variable_elimination.cpp','-o','<ignored-build>/frame-variable-elimination'],
                  factor_storage='uint16 costs/choices; 2^24 entries maximum per factor; checked arithmetic',
                  method='Exact variable elimination with deterministic min-fill order and reverse argmin witness')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');control=controls(binary,work/'controls');cases=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();cases.append(result)
            print(json.dumps({key:result[key] for key in ('status','active_bits','frame_kind','chronology','minimum_rank_charge','capacity','seconds')}),flush=True)
    if any(sha256(path.read_bytes()).hexdigest()!=digest for path,digest in hashes.items()):raise ValueError('Effective source changed during experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(controls=control,cases=cases),indent=2)+'\n')


if __name__=='__main__':main()
