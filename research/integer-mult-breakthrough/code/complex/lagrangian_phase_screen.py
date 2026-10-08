#!/usr/bin/env python3
"""Bounded common-frame rank screen: graph frames versus all Lagrangians.

This is an abstract finite rank-cost model. It omits endpoint lifts,
scalar schedule, complete dirty restoration and physical routing costs.
"""
import argparse
from collections import deque
from hashlib import sha256
from itertools import combinations
import json
from math import prod
from pathlib import Path
import random
from time import perf_counter


def dot(a,b):return (a&b).bit_count()&1


def basis(rows):
    pivots={}
    for row in rows:
        for j in sorted(pivots,reverse=True):
            if row>>j&1:row ^=pivots[j]
        if row:
            j=row.bit_length()-1
            for k,old in tuple(pivots.items()):
                if old>>j&1:pivots[k]=old^row
            pivots[j]=row
    return tuple(pivots[j] for j in sorted(pivots,reverse=True))


def pairing(a,b,n):
    mask=(1<<n)-1
    return dot(a&mask,b>>n)^dot(a>>n,b&mask)


def distance(A,B,n):return len(basis(A+B))-n


def h(v,j,n):
    a=(v>>j)&1;b=(v>>(j+n))&1
    return v^(((1<<j)|(1<<(j+n))) if a!=b else 0)


def s(v,j,n):return v^((1<<(j+n)) if v>>j&1 else 0)


def cnot(v,control,target,n):
    return v^((1<<target) if v>>control&1 else 0)^((1<<(control+n)) if v>>(target+n)&1 else 0)


def all_lagrangians(n):
    initial=tuple(1<<j for j in range(n-1,-1,-1));known={initial};queue=deque((initial,))
    while queue:
        lag=queue.popleft()
        updates=[basis(tuple(fun(v,j,n) for v in lag)) for fun in (h,s) for j in range(n)]
        updates +=[basis(tuple(cnot(v,a,b,n) for v in lag)) for a in range(n) for b in range(n) if a!=b]
        for new in updates:
            if new not in known:known.add(new);queue.append(new)
    result=sorted(known)
    assert len(result)==prod(2**j+1 for j in range(1,n+1))
    assert all(len(lag)==n and all(not pairing(a,b,n) for a in lag for b in lag) for lag in result)
    return result


def graph_frames(n):
    result=[]
    for code in range(1<<(n*(n+1)//2)):
        rows=[0]*n;bit=0
        for j in range(n):
            for k in range(j,n):
                if code>>bit&1:rows[j] |=1<<k;rows[k] |=1<<j
                bit+=1
        result.append(basis(tuple((1<<j)|(rows[j]<<n) for j in range(n))))
    return result


def screen(n,arity,mode,samples,seed):
    started=perf_counter();lags=all_lagrangians(n);graphs=graph_frames(n);indices={lag:j for j,lag in enumerate(lags)}
    graph_indices=tuple(indices[lag] for lag in graphs)
    table=[bytes(distance(g,L,n) for L in lags) for g in graphs]
    cases=combinations(range(len(graphs)),arity) if mode=='exhaustive' else (tuple(sorted(random.Random(seed+i).sample(range(len(graphs)),arity))) for i in range(samples))
    gap_count=0;maximum_gap=0;witnesses=[];count=0;digest=sha256();sum_graph=sum_full=0
    for terminals in cases:
        cost=[sum(table[t][c] for t in terminals) for c in range(len(lags))]
        full=min(cost);restricted=min(cost[j] for j in graph_indices);gap=restricted-full
        assert gap>=0
        if gap:
            gap_count+=1;maximum_gap=max(maximum_gap,gap)
            if len(witnesses)<8:
                candidate=cost.index(full);restricted_candidate=next(j for j in graph_indices if cost[j]==restricted)
                witnesses.append(dict(terminal_graph_codes=terminals,terminal_bases=[graphs[t] for t in terminals],
                                      full_candidate_basis=lags[candidate],graph_candidate_basis=lags[restricted_candidate],
                                      full_cost=full,graph_cost=restricted,distances=[table[t][candidate] for t in terminals]))
        sum_graph +=restricted;sum_full +=full;count+=1
        digest.update(f'{terminals}:{restricted},{full};'.encode())
    return dict(status='PASS exact finite Lagrangian median screen',n=n,arity=arity,mode=mode,seed=seed,
                lagrangian_count=len(lags),symmetric_graph_count=len(graphs),terminal_cases=count,
                strict_gap_cases=gap_count,maximum_gap=maximum_gap,sum_graph_cost=sum_graph,sum_full_cost=sum_full,
                witnesses=witnesses,result_sha256=digest.hexdigest(),elapsed_seconds=perf_counter()-started,
                scope='Abstract common-gate Fourier-rank metric only; no physical scalar network or exponent')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--n',type=int,required=True);p.add_argument('--arity',type=int,default=3)
    p.add_argument('--mode',choices=('exhaustive','sampled'),default='sampled');p.add_argument('--samples',type=int,default=512)
    p.add_argument('--seed',type=int,default=20261008);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if not 1<=a.n<=4 or not 2<=a.arity<=5 or a.samples<=0:raise ValueError('Unsupported bounded configuration')
    if a.mode=='exhaustive' and (a.n>3 or a.arity>3):raise ValueError('Use bounded sampled exploration')
    if a.output.exists():raise FileExistsError('Use a fresh output')
    result=screen(a.n,a.arity,a.mode,a.samples,a.seed);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='witnesses'}),flush=True)


if __name__=='__main__':main()
