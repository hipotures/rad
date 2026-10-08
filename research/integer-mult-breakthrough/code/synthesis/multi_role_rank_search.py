#!/usr/bin/env python3
"""Broader exact CNOT/common-frame rank synthesis, including multiple data pairs.

The finite state includes the whole invertible GF2 scalar matrix and every
physical wire frame. Rank costs include all endpoints. Searches are complete
below capacity only when no time/state limit is reached. Physical Gaussian
lifts, payload replay, precision, routing and transfer remain separate.
"""
import argparse
from collections import Counter,deque
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time

from dirty_helper_rank_search import frame_domain
from lagrangian_graph_completion import distance,graph


def search(n,kind,mode,max_seconds,max_states):
    started=time.monotonic();frames=frame_domain(n,kind);count=len(frames);ids={f:j for j,f in enumerate(frames)}
    distances=[[distance(a,b,n) for b in frames] for a in frames]
    zero=ids[graph((0,)*n)];full=ids[graph(tuple(1<<j for j in range(n)))]
    if mode=='two-orthogonal-data-pairs':
        if n!=2:raise ValueError('Declared two-data geometry has width two')
        p0=ids[graph((1,0))];p1=ids[graph((0,2))]
        starts=(p0,zero,p1,zero);ends=(full,p1,full,p0);target=(2,1,8,4)
    elif mode=='rank-two-one-helper':
        if n!=3:raise ValueError('Declared rank-two geometry has width three')
        p=ids[graph((1,2,0))];complement=ids[graph((0,0,4))]
        starts=(p,zero,zero);ends=(full,complement,full);target=(2,1,4)
    else:raise ValueError('Unknown geometry')
    roles=len(starts);capacity=roles*n;budget=capacity-1;fbits=(count-1).bit_length();single=(1<<fbits)-1
    total_frame_bits=roles*fbits;frame_mask=(1<<total_frame_bits)-1;row_mask=(1<<roles)-1
    initial_matrix=sum((1<<j)<<(j*roles) for j in range(roles));target_matrix=sum(row<<(j*roles) for j,row in enumerate(target))
    initial=(initial_matrix<<total_frame_bits)|sum(f<<(j*fbits) for j,f in enumerate(starts))
    scores={initial:0};parents={};buckets=[deque() for _ in range(budget+1)];buckets[0].append(initial)
    pairs=[(a,b) for a in range(roles) for b in range(a+1,roles)]
    clear={(a,b):frame_mask^((single<<(a*fbits))|(single<<(b*fbits))) for a,b in pairs}
    finish_table=[[distances[f][ends[j]] for f in range(count)] for j in range(roles)]
    cache={};expanded=0;admissible_edges=0;hist=Counter();found=None;status=None
    for cost,bucket in enumerate(buckets):
        while bucket:
            state=bucket.popleft()
            if scores.get(state)!=cost:continue
            fcode=state&frame_mask;current=tuple((fcode>>(j*fbits))&single for j in range(roles));matrix=state>>total_frame_bits
            finish=[finish_table[j][current[j]] for j in range(roles)];finish_sum=sum(finish)
            if cost+finish_sum>budget:continue
            if matrix==target_matrix:found=(state,cost,finish);status='FOUND STRICT ABSTRACT RANK WORD';break
            expanded+=1;hist[cost]+=1
            if expanded%1000==0 and time.monotonic()-started>max_seconds:status='UNKNOWN TIME LIMIT';break
            for a,b in pairs:
                key=(current[a],current[b])
                if key not in cache:cache[key]=sorted((distances[key[0]][c]+distances[key[1]][c],c) for c in range(count))
                outside=finish_sum-finish[a]-finish[b]
                for increment,common in cache[key]:
                    newcost=cost+increment
                    if newcost>budget:break
                    if newcost+outside+finish_table[a][common]+finish_table[b][common]>budget:continue
                    newf=(fcode&clear[a,b])|(common<<(a*fbits))|(common<<(b*fbits))
                    for dest,source in ((a,b),(b,a)):
                        newmatrix=matrix^(((matrix>>(source*roles))&row_mask)<<(dest*roles))
                        newstate=(newmatrix<<total_frame_bits)|newf;admissible_edges+=1
                        if newcost>=scores.get(newstate,capacity):continue
                        scores[newstate]=newcost;parents[newstate]=(state,dest,source,common,increment)
                        buckets[newcost].append(newstate)
                        if len(scores)>=max_states:status='UNKNOWN STATE LIMIT';break
                    if status:break
                if status:break
            if status:break
        if status:break
    if status is None:status='EXCLUDED BELOW CAPACITY IN COMPLETE FINITE MODEL'
    witness=None
    if found:
        state,cost,finish=found;steps=[]
        while state!=initial:
            previous,dest,source,common,increment=parents[state]
            steps.append(dict(destination=dest,source=source,common_frame=common,rank_charge=increment));state=previous
        steps.reverse();scalar=[1<<j for j in range(roles)];current=list(starts);mass=0
        for step in steps:
            dest,source,common=step['destination'],step['source'],step['common_frame']
            measured=distance(frames[current[dest]],frames[common],n)+distance(frames[current[source]],frames[common],n)
            if measured!=step['rank_charge']:raise ValueError('Rank witness fails independent event replay')
            mass+=measured;current[dest]=common;current[source]=common;scalar[dest]^=scalar[source]
        finish=[distance(frames[current[j]],frames[ends[j]],n) for j in range(roles)];mass+=sum(finish)
        if tuple(scalar)!=target or mass>=capacity:raise ValueError('Witness scalar/restoration or rank mass is invalid')
        witness=dict(steps=steps,frame_bases=frames,final_frame_ids=current,final_completion_ranks=finish,
                     rank_mass=mass,capacity=capacity,scalar_rows=scalar)
    digest=sha256()
    for state,cost in sorted(scores.items()):digest.update(f'{state}:{cost};'.encode())
    return dict(status=status,n=n,domain=kind,mode=mode,frame_count=count,roles=roles,capacity=capacity,
                strict_budget=budget,start_frame_bases=[frames[j] for j in starts],end_frame_bases=[frames[j] for j in ends],
                scalar_target_rows=target,expanded_states=expanded,discovered_states=len(scores),expanded_by_cost=dict(sorted(hist.items())),
                admissible_edges=admissible_edges,explored_state_sha256=digest.hexdigest(),witness=witness,
                seconds=time.monotonic()-started,
                completeness='All scalar CNOT directions, common frames, and arbitrarily long finite words within the rank budget; per-wire endpoint-distance pruning follows the triangle inequality. Resource-limited statuses do not prove exclusions.',
                scope='Abstract exact common-Lagrangian rank model. Even a strict positive word needs phase representatives, complete physical payload replay, nonrecursive movement/scalar costs and asymptotic transfer.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--workers',type=int,default=4);ap.add_argument('--max-seconds',type=float,default=300)
    ap.add_argument('--max-states',type=int,default=1000000);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(__file__).with_name('dirty_helper_rank_search.py'),Path(__file__).with_name('lagrangian_graph_completion.py')]
    specs=[(2,'graph','two-orthogonal-data-pairs'),(2,'full','two-orthogonal-data-pairs'),
           (3,'graph','rank-two-one-helper'),(3,'full','rank-two-one-helper')]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,seed=None,
                  specs=specs,max_seconds_each=args.max_seconds,max_states_each=args.max_states,
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');receipts=[];start=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(search,*spec,args.max_seconds,args.max_states):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();receipts.append(result)
            name=f"n{result['n']}-{result['domain']}-{result['mode']}.json"
            (args.output/name).write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps({k:result[k] for k in ('status','n','domain','mode','expanded_states','discovered_states','seconds')}),flush=True)
    (args.output/'summary.json').write_text(json.dumps(dict(status='COMPLETE SEARCH RECEIPTS',cases=receipts,seconds=time.monotonic()-start),indent=2)+'\n')


if __name__=='__main__':main()
