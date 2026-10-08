#!/usr/bin/env python3
"""Nonmonotone common-frame search on a complete dirty cancellation word.

Every actual scalar shear is a gate variable. Consecutive incidences on
each physical wire and both of its fixed endpoints contribute rank cost.
Alpha expansion is heuristic in the many-label problem; its binary moves
are solved exactly and independently checked on bounded controls.
"""
import argparse
from collections import Counter,deque
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import sys
import time

from lagrangian_graph_completion import basis,distance,intersection,pairing
from trimmed_zeta_dirty_probe import SIDE_SOURCE,side,mixer_edges


def perpendicular(E,n):
    equations=basis(E,n);free=[]
    pivots=[(a&-a).bit_length()-1 for a in equations]
    for j in range(n):
        if j in pivots:continue
        v=1<<j
        for row,pivot in zip(equations,pivots):
            if row>>j&1:v ^=1<<pivot
        free.append(v)
    answer=basis(free,n)
    if len(answer)+len(equations)!=n or any((a&b).bit_count()%2 for a in answer for b in equations):
        raise ValueError('Binary perpendicular failed')
    return answer


def le(E,n):
    return basis(perpendicular(E,n)+tuple(v|(v<<n) for v in basis(E,n)),2*n)


def subspaces(n):
    known={()};queue=deque([()])
    while queue:
        old=queue.popleft()
        for v in range(1,1<<n):
            new=basis(old+(v,),n)
            if new not in known:known.add(new);queue.append(new)
    return sorted(known)


def lagrangians(n):
    start=basis(tuple(1<<j for j in range(n)),2*n);known={start};queue=deque([start])
    while queue:
        old=queue.popleft();updates=[]
        for j in range(n):
            updates.append(basis(tuple(v^(((1<<j)|(1<<(n+j))) if ((v>>j)^(v>>(n+j)))&1 else 0) for v in old),2*n))
            updates.append(basis(tuple(v^((1<<(n+j)) if v>>j&1 else 0) for v in old),2*n))
        for a in range(n):
            for b in range(n):
                if a!=b:updates.append(basis(tuple(v^((1<<b) if v>>a&1 else 0)^((1<<(n+a)) if v>>(n+b)&1 else 0) for v in old),2*n))
        for new in updates:
            if new not in known:known.add(new);queue.append(new)
    expected=1
    for j in range(1,n+1):expected*=2**j+1
    if len(known)!=expected or any(len(L)!=n or any(pairing(a,b,n) for a in L for b in L) for L in known):
        raise ValueError('Full finite Lagrangian enumeration failed')
    return sorted(known)


def cancellation_dag(h,k):
    """Share the entire side DAG; central outputs are x_T-side_T."""
    original=side.build_dag(h,k);dag=dict(original);dag['nodes']=list(original['nodes']);central=[]
    for j,out in enumerate(original['outputs']):
        dag['nodes'].append(('scale',out,-1,1));negative=len(dag['nodes'])-1
        dag['nodes'].append(('add',j,negative));central.append(len(dag['nodes'])-1)
    dag['central_outputs']=central
    return dag


def scalar_word(dag):
    v=len(dag['top']);r=len(dag['nodes']);w=2*v+r
    edges=[(2*v+a,2*v+b,c) for a,b,c in mixer_edges(dag)]
    scatter=[(v+j,2*v+out,Q(1)) for j in range(v)
             for out in (dag['outputs'][j],dag['central_outputs'][j])]
    inverse=[(a,b,-c) for a,b,c in reversed(edges)]
    inject=[(2*v+j,j,Q(1)) for j in range(v)]
    word=edges+[(a,b,-c) for a,b,c in scatter]+inverse+inject+edges+scatter+inverse+[(a,b,-c) for a,b,c in inject]
    return word,w


def scalar_replay(dag,word,w,negative=False):
    v=len(dag['top']);rows=[{j:Q(1)} for j in range(w)]
    for a,b,c in word[:-1] if negative else word:
        for j,z in list(rows[b].items()):
            value=rows[a].get(j,Q())+c*z
            if value:rows[a][j]=value
            else:rows[a].pop(j,None)
    expected=[{j:Q(1)} for j in range(w)]
    for j in range(v):expected[v+j][j]=Q(1)
    bad=[j for j in range(w) if rows[j]!=expected[j]]
    if bool(bad)!=negative:raise ValueError('Full scalar cancellation/dirty replay mismatch')
    witness=None
    if bad:
        a=bad[0];j=next(j for j in sorted(set(rows[a])|set(expected[a])) if rows[a].get(j,Q())!=expected[a].get(j,Q()))
        witness=dict(output_role=a,initial_column=j,expected=str(expected[a].get(j,Q())),actual=str(rows[a].get(j,Q())))
    return dict(status='CORRUPTION DETECTED' if negative else 'EXACT FULL SCALAR PASS',
                restored_dirty_columns=w-2*v,source_columns=v,sink_columns=v,witness=witness)


def incidence_graph(word,w,starts,ends):
    edge_counts=Counter();boundaries=[[] for _ in word];previous=[None]*w;unused=0
    for g,(a,b,_) in enumerate(word):
        for role in (a,b):
            if previous[role] is None:boundaries[g].append(starts[role])
            else:edge_counts[tuple(sorted((previous[role],g)))]+=1
            previous[role]=g
    for role,node in enumerate(previous):
        if node is None:unused+=distance(starts[role],ends[role],len(starts[role]))
        else:boundaries[node].append(ends[role])
    return tuple((a,b,c) for (a,b),c in sorted(edge_counts.items())),boundaries,unused


class Flow:
    def __init__(self,n):self.adj=[[] for _ in range(n)]
    def edge(self,a,b,c,reverse=0):
        self.adj[a].append([b,len(self.adj[b]),c]);self.adj[b].append([a,len(self.adj[a])-1,reverse])
    def minimum(self,s,t):
        result=0;n=len(self.adj)
        while True:
            levels=[-1]*n;levels[s]=0;queue=deque([s])
            while queue:
                a=queue.popleft()
                for b,_,cap in self.adj[a]:
                    if cap and levels[b]<0:levels[b]=levels[a]+1;queue.append(b)
            if levels[t]<0:break
            next_edge=[0]*n
            def send(a,amount):
                if a==t:return amount
                while next_edge[a]<len(self.adj[a]):
                    e=self.adj[a][next_edge[a]];b,rev,cap=e
                    if cap and levels[b]==levels[a]+1:
                        z=send(b,min(amount,cap))
                        if z:e[2]-=z;self.adj[b][rev][2]+=z;return z
                    next_edge[a]+=1
                return 0
            while True:
                z=send(s,10**20)
                if not z:break
                result+=z
        reached={s};queue=deque([s])
        while queue:
            a=queue.popleft()
            for b,_,cap in self.adj[a]:
                if cap and b not in reached:reached.add(b);queue.append(b)
        return result,reached


def alpha_move(labels,alpha,edges,unary,dist):
    count=len(labels);linear=[2*(unary[g][alpha]-unary[g][labels[g]]) for g in range(count)]
    net=Flow(count+2);s=count;t=count+1
    for a,b,weight in edges:
        e00=weight*dist(labels[a],labels[b]);e01=weight*dist(labels[a],alpha);e10=weight*dist(alpha,labels[b])
        cross=e01+e10-e00
        if cross<0:raise ValueError('Metric expansion is not submodular')
        linear[a]+=e10-e01-e00;linear[b]+=e01-e10-e00
        if cross:net.edge(a,b,cross,cross)
    for g,c in enumerate(linear):
        if c>0:net.edge(s,g,c)
        elif c<0:net.edge(g,t,-c)
    _,reachable=net.minimum(s,t)
    return [old if g in reachable else alpha for g,old in enumerate(labels)]


def energy(labels,edges,unary,dist,constant=0):
    return constant+sum(unary[g][label] for g,label in enumerate(labels))+sum(c*dist(labels[a],labels[b]) for a,b,c in edges)


def binary_controls():
    rng=random.Random(20261008);frames=lagrangians(2);table=[[distance(a,b,2) for b in frames] for a in frames]
    dist=lambda a,b:table[a][b]
    for case in range(32):
        labels=[rng.randrange(len(frames)) for _ in range(5)];alpha=rng.randrange(len(frames))
        edges=[(a,b,rng.randrange(1,4)) for a in range(5) for b in range(a+1,5) if rng.randrange(2)]
        unary=[[rng.randrange(7) for _ in frames] for _ in labels]
        new=alpha_move(labels,alpha,edges,unary,dist)
        optimum=min(energy([alpha if bits[j] else labels[j] for j in range(5)],edges,unary,dist) for bits in product((0,1),repeat=5))
        if energy(new,edges,unary,dist)!=optimum:raise ValueError('Exact alpha cut disagrees with independent binary exhaustive control')
    return dict(binary_expansion_controls=32,independent_choices_each=32,status='PASS')


def probe(spec):
    h,k,kind,limit,rounds,seed=spec;start=time.monotonic();rng=random.Random(seed)
    dag=cancellation_dag(h,k);word,w=scalar_word(dag);sys.setrecursionlimit(max(10000,len(word)*3))
    replay=scalar_replay(dag,word,w);negative=scalar_replay(dag,word,w,True);v=len(dag['top'])
    zero=le((),h);full=le(tuple(1<<j for j in range(h)),h)
    starts=[le((T,),h) for T in dag['top']]+[zero]*(w-v)
    ends=[full]*v+[le(perpendicular((T,),h),h) for T in dag['top']]+[full]*(w-2*v)
    if kind=='full':domain=lagrangians(h)
    else:domain=[le(E,h) for E in subspaces(h)]
    complete_domain_count=len(domain)
    required=set(starts+ends);remaining=[a for a in domain if a not in required]
    if limit and len(domain)>limit:
        rng.shuffle(remaining);domain=sorted(required|set(remaining[:max(0,limit-len(required))]))
    else:domain=sorted(domain)
    ids={L:j for j,L in enumerate(domain)};frames=len(domain);cache={}
    def dist(a,b):
        if a==b:return 0
        key=(a,b) if a<b else (b,a)
        if key not in cache:cache[key]=distance(domain[a],domain[b],h)
        return cache[key]
    edges,boundaries,constant=incidence_graph(word,w,starts,ends)
    unary=[[sum(dist(j,ids[F]) for F in b) for j in range(frames)] for b in boundaries]
    capacity=w*h;endpoint=sum(distance(a,b,h) for a,b in zip(starts,ends));best=capacity;best_labels=None;trajectories=[]
    for initial_name,initial in [('zero',[ids[zero]]*len(word)),('full',[ids[full]]*len(word))]:
        labels=initial;cost=energy(labels,edges,unary,dist,constant)
        if cost!=capacity:raise ValueError('Actual whole-word fixed-frame baseline should equal complete stock capacity')
        trace=[cost];completed=0
        for sweep in range(rounds):
            previous=cost;alphas=list(range(frames));rng.shuffle(alphas)
            for alpha in alphas:
                new=alpha_move(labels,alpha,edges,unary,dist);value=energy(new,edges,unary,dist,constant)
                if value>cost:raise ValueError('Exact expansion increased cost')
                if value<cost:labels=new;cost=value
            completed+=1;trace.append(cost)
            if cost==previous:break
        if cost<best or best_labels is None:best=cost;best_labels=labels
        trajectories.append(dict(initial=initial_name,cost_trace=trace,completed_rounds=completed,alpha_local_optimum=trace[-1]==trace[-2]))
    # Direct per-wire chronological replay, independent of graph construction.
    current=list(starts);hist=Counter();chronology=[]
    for g,(a,b,c) in enumerate(word):
        common=domain[best_labels[g]]
        for role in (a,b):
            rank=distance(current[role],common,h)
            if rank:hist[rank]+=1
            current[role]=common
        chronology.append(dict(destination=a,source=b,coefficient=str(c),common_frame=best_labels[g]))
    for j,F in enumerate(ends):
        rank=distance(current[j],F,h)
        if rank:hist[rank]+=1
    if sum(a*b for a,b in hist.items())!=best or best<endpoint:
        raise ValueError('Chronological all-role rank replay or endpoint lower bound failed')
    return dict(status='FOUND STRICT WHOLE-WORD ABSTRACT RANK DEFICIT' if best<capacity else 'NO DEFICIT FOUND BY HEURISTIC; NOT AN EXCLUSION',
                h=h,k=k,kind=kind,seed=seed,complete_domain_count=complete_domain_count,searched_domain_count=frames,
                scalar_shears=len(word),payload_stock=w,reused_SSA_auxiliaries=w-2*v,vertices=v,
                complete_endpoint_lower_bound=endpoint,capacity=capacity,rank_charge=best,deficit=capacity-best,
                chronological_histogram=dict(sorted(hist.items())),trajectories=trajectories,
                scalar_replay=replay,scalar_corruption_control=negative,
                selected_domain_sha256=sha256(json.dumps(domain).encode()).hexdigest(),seconds=time.monotonic()-start,
                selected_common_frames=domain,word=chronology,
                scope='Exact scalar map y+=x with every source/dirty column restored; exact nonmonotone rank accounting for the supplied complete common-frame word and endpoints. Many-label optimization is heuristic. Gaussian phase lifts, gauge adapters, selected-word/tape costs, precision and asymptotic transfer are not certified.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--workers',type=int,default=4);ap.add_argument('--rounds',type=int,default=2)
    ap.add_argument('--full-limit',type=int,default=128);ap.add_argument('--large-limit',type=int,default=128)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(__file__).with_name('lagrangian_graph_completion.py'),Path(__file__).with_name('trimmed_zeta_dirty_probe.py'),SIDE_SOURCE]
    hashes={str(p):sha256(p.read_bytes()).hexdigest() for p in sources}
    specs=[(4,3,'LE',0,args.rounds,202610081),(4,3,'full',args.full_limit,args.rounds,202610082),
           (5,3,'LE',args.large_limit,args.rounds,202610083),(6,5,'LE',args.large_limit,args.rounds,202610084)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,specs=specs,
                  source_sha256={p.name:hashes[str(p)] for p in sources},optimizer='exact binary alpha moves; bounded many-label sweeps')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');controls=binary_controls();cases=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(probe,spec):spec for spec in specs}
        for future in as_completed(futures):
            result=future.result();cases.append(result)
            print(json.dumps({k:result[k] for k in ('h','k','kind','status','deficit','capacity','scalar_shears','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=hashes[str(p)] for p in sources):raise ValueError('Effective source changed during run')
    result=dict(controls=controls,cases=cases)
    (args.output/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
