#!/usr/bin/env python3
"""Explore equal-cost plateaus of the complete dirty cancellation word.

The strict-only alpha search can stop at a uniform label before distinct
frontiers form. This independent attempt accepts unseen equal-cost words
and adds nonuniform starts. Every outcome is a heuristic finite discovery,
not an exhaustive exclusion. It replays all actual chronological ranks.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import time

import global_word_frame_search as g


def probe(spec):
    h,k,kind,limit,rounds,seed=spec;started=time.monotonic();rng=random.Random(seed)
    dag=g.cancellation_dag(h,k);word,w=g.scalar_word(dag);sys.setrecursionlimit(max(10000,len(word)*3))
    v=len(dag['top']);zero=g.le((),h);full=g.le(tuple(1<<j for j in range(h)),h)
    starts=[g.le((T,),h) for T in dag['top']]+[zero]*(w-v)
    ends=[full]*v+[g.le(g.perpendicular((T,),h),h) for T in dag['top']]+[full]*(w-2*v)
    domain=g.lagrangians(h) if kind=='full' else [g.le(E,h) for E in g.subspaces(h)]
    total=len(domain);required=set(starts+ends)
    if limit and total>limit:
        others=[F for F in domain if F not in required];rng.shuffle(others)
        domain=sorted(required|set(others[:max(0,limit-len(required))]))
    else:domain=sorted(domain)
    ids={F:j for j,F in enumerate(domain)};count=len(domain);cache={}
    def dist(a,b):
        if a==b:return 0
        key=tuple(sorted((a,b)))
        if key not in cache:cache[key]=g.distance(domain[a],domain[b],h)
        return cache[key]
    edges,boundaries,constant=g.incidence_graph(word,w,starts,ends)
    unary=[[sum(dist(j,ids[F]) for F in B) for j in range(count)] for B in boundaries]
    initial=[('zero',[ids[zero]]*len(word)),('full',[ids[full]]*len(word))]
    # Four block labels avoid manufacturing a high-entropy random workload.
    chosen=[ids[zero],ids[full]]+rng.sample(range(count),2)
    initial.append(('four-block',[chosen[min(3,4*j//len(word))] for j in range(len(word))]))
    best=w*h;best_word=initial[0][1];traces=[]
    for name,labels in initial:
        cost=g.energy(labels,edges,unary,dist,constant);history=[cost];states={tuple(labels)};plateaus=0;strict=0
        for sweep in range(rounds):
            alphabets=list(range(count));rng.shuffle(alphabets)
            for alpha in alphabets:
                new=g.alpha_move(labels,alpha,edges,unary,dist);value=g.energy(new,edges,unary,dist,constant)
                if value>cost:raise ValueError('Exact expansion increased cost')
                state=tuple(new)
                if state in states:continue
                states.add(state)
                if value<cost:strict+=1
                else:plateaus+=1
                labels=new;cost=value
                if cost<best:best=cost;best_word=list(labels)
            history.append(cost)
        traces.append(dict(initial=name,cost_trace=history,strict_steps=strict,equal_cost_steps=plateaus,distinct_words=len(states)))
    current=list(starts);hist=Counter();actual=[]
    for node,(a,b,c) in enumerate(word):
        frame=domain[best_word[node]]
        for role in (a,b):
            r=g.distance(current[role],frame,h)
            if r:hist[r]+=1
            current[role]=frame
        actual.append((a,b,str(c),best_word[node]))
    for role,F in enumerate(ends):
        r=g.distance(current[role],F,h)
        if r:hist[r]+=1
    lower=sum(g.distance(a,b,h) for a,b in zip(starts,ends))
    if sum(r*c for r,c in hist.items())!=best or best<lower:raise ValueError('All-role chronological rank replay failed')
    return dict(status='FOUND STRICT WHOLE-WORD ABSTRACT RANK DEFICIT' if best<w*h else 'NO DEFICIT FOUND BY PLATEAU HEURISTIC; NOT AN EXCLUSION',
                h=h,k=k,kind=kind,seed=seed,rounds=rounds,complete_domain_count=total,searched_domain_count=count,
                vertices=v,reused_SSA_auxiliaries=w-2*v,payload_stock=w,scalar_shears=len(word),
                capacity=w*h,endpoint_lower_bound=lower,rank_charge=best,deficit=w*h-best,
                chronological_histogram=dict(sorted(hist.items())),traces=traces,
                scalar_replay=g.scalar_replay(dag,word,w),scalar_negative=g.scalar_replay(dag,word,w,True),
                frames=domain,word=actual,seconds=time.monotonic()-started,
                scope='Complete source/sink/dirty scalar word and chronological rank-cost certificate. Equal-cost and nonuniform many-label optimization remains heuristic; a no-deficit result is not a lower bound. Exact phase lifts, scalar-unit adapters and asymptotic/native costs are open.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--workers',type=int,default=4);ap.add_argument('--rounds',type=int,default=4)
    ap.add_argument('--limit',type=int,default=256);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    paths=[Path(__file__),Path(g.__file__),Path(g.__file__).with_name('lagrangian_graph_completion.py'),
           Path(g.__file__).with_name('trimmed_zeta_dirty_probe.py'),g.SIDE_SOURCE]
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in paths}
    specs=[(4,3,'LE',0,a.rounds,202610085),(4,3,'full',a.limit,a.rounds,202610086),
           (5,3,'LE',0,a.rounds,202610087),(6,5,'LE',a.limit,a.rounds,202610088)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=a.workers,native_threads_each=1,specs=specs,
                  source_sha256={p.name:s for p,s in hashes.items()},optimizer='Exact alpha binary cuts; accept unseen equal costs; three initial words')
    (a.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');controls=g.binary_controls();cases=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        tasks={pool.submit(probe,spec):spec for spec in specs}
        for future in as_completed(tasks):
            result=future.result();cases.append(result)
            print(json.dumps({k:result[k] for k in ('h','k','kind','status','deficit','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=s for p,s in hashes.items()):raise ValueError('Effective source changed during run')
    (a.output/'certificate.json').write_text(json.dumps(dict(controls=controls,cases=cases),indent=2)+'\n')


if __name__=='__main__':main()
