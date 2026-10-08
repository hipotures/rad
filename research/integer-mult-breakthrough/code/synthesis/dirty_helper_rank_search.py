#!/usr/bin/env python3
"""Global CNOT/frame synthesis with one arbitrary dirty helper.

Searches an abstract rank-cost model, including actual before/after wire
frames and a reversible scalar SWAP with helper identity. Every CNOT uses
one common frame. Full-width calls are allowed; strict capacity is tested.
Even a positive rank word would still require Gaussian-dyadic phase lifts,
literal payload replay, a recursive router and all-size cost transfer.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import heapq
from itertools import combinations
import json
from pathlib import Path
import time

from lagrangian_graph_completion import (basis,distance,graph,pairing,
                                         symmetric_columns)


def frame_domain(n,kind):
    graphs=[graph(symmetric_columns(n,c)) for c in range(1<<(n*(n+1)//2))]
    if kind=='graph':return graphs
    result=set()
    for vectors in combinations(range(1,1<<(2*n)),n):
        if any(pairing(a,b,n) for a,b in combinations(vectors,2)):continue
        candidate=basis(vectors,2*n)
        if len(candidate)==n:result.add(candidate)
    expected=1
    for j in range(1,n+1):expected*=2**j+1
    if len(result)!=expected:raise ValueError('Incomplete bounded full Lagrangian domain')
    return sorted(result)


def search(n,kind,max_seconds,max_states):
    started=time.monotonic();frames=frame_domain(n,kind);count=len(frames);ids={f:j for j,f in enumerate(frames)}
    table=[[distance(a,b,n) for b in frames] for a in frames]
    pcolumns=tuple(1 if j==0 else 0 for j in range(n));icolumns=tuple(1<<j for j in range(n))
    compcolumns=tuple(a^b for a,b in zip(pcolumns,icolumns))
    zero=ids[graph((0,)*n)];ip=ids[graph(pcolumns)];full=ids[graph(icolumns)];comp=ids[graph(compcolumns)]
    startframes=(ip,zero,zero);endframes=(full,comp,full);roles=3;capacity=roles*n;budget=capacity-1
    fbits=(count-1).bit_length();one_mask=(1<<fbits)-1;all_frame_bits=roles*fbits;frame_mask=(1<<all_frame_bits)-1
    encode=lambda f:sum(v<<(j*fbits) for j,v in enumerate(f))
    startmatrix=1|(2<<roles)|(4<<(2*roles));targetmatrix=2|(1<<roles)|(4<<(2*roles))
    start=(startmatrix<<all_frame_bits)|encode(startframes)
    scores={start:0};parents={};heap=[(0,start)];expanded=0;hist=Counter();found=None;status=None
    pairs=[(a,b) for a in range(roles) for b in range(roles) if a!=b]
    options={(a,b):sorted((table[a][c]+table[b][c],c) for c in range(count))
             for a in range(count) for b in range(count)}
    clears={(a,b):frame_mask^((one_mask<<(a*fbits))|(one_mask<<(b*fbits))) for a,b in pairs}
    candidates=0
    while heap:
        cost,state=heapq.heappop(heap)
        if scores.get(state)!=cost:continue
        fcode=state&frame_mask;wireframes=tuple((fcode>>(j*fbits))&one_mask for j in range(roles));matrix=state>>all_frame_bits
        finish=[table[wireframes[j]][endframes[j]] for j in range(roles)]
        if cost+sum(finish)>budget:continue
        if matrix==targetmatrix:
            found=(state,cost,finish);status='FOUND STRICT ABSTRACT RANK WORD';break
        expanded+=1;hist[cost]+=1
        if expanded%1000==0 and time.monotonic()-started>max_seconds:
            status='UNKNOWN TIME LIMIT';break
        for dest,source in pairs:
            source_row=(matrix>>(source*roles))&7
            newmatrix=matrix^(source_row<<(dest*roles))
            for increment,common in options[wireframes[dest],wireframes[source]]:
                newcost=cost+increment
                if newcost>budget:break
                remaining=sum(finish[j] for j in range(roles) if j not in (dest,source))
                remaining+=table[common][endframes[dest]]+table[common][endframes[source]]
                if newcost+remaining>budget:continue
                candidates+=1
                newf=(fcode&clears[dest,source])|(common<<(dest*fbits))|(common<<(source*fbits))
                newstate=(newmatrix<<all_frame_bits)|newf
                if newcost>=scores.get(newstate,capacity):continue
                scores[newstate]=newcost;parents[newstate]=(state,dest,source,common,increment)
                heapq.heappush(heap,(newcost,newstate))
                if len(scores)>=max_states:
                    status='UNKNOWN STATE LIMIT';break
            if status:break
        if status:break
    if status is None:status='EXCLUDED BELOW CAPACITY IN COMPLETE FINITE MODEL'
    witness=None
    if found:
        state,cost,finish=found;steps=[]
        while state!=start:
            previous,dest,source,common,increment=parents[state]
            oldcode=previous&frame_mask;oldframes=tuple((oldcode>>(j*fbits))&one_mask for j in range(roles))
            steps.append(dict(destination=dest,source=source,common_frame=common,
                              old_destination_frame=oldframes[dest],old_source_frame=oldframes[source],rank_charge=increment))
            state=previous
        steps.reverse()
        # Replay every scalar gate/frame choice and rank charge independently
        # of Dijkstra's scalar-state updates and final row test.
        scalar=[1,2,4];current=list(startframes);mass=0
        for step in steps:
            dest,source,common=step['destination'],step['source'],step['common_frame']
            measured=distance(frames[current[dest]],frames[common],n)+distance(frames[current[source]],frames[common],n)
            if measured!=step['rank_charge']:raise ValueError('Found word rank replay failed')
            mass+=measured;current[dest]=common;current[source]=common;scalar[dest]^=scalar[source]
        finish=[distance(frames[current[j]],frames[endframes[j]],n) for j in range(roles)]
        mass+=sum(finish)
        if scalar!=[2,1,4] or mass>=capacity:raise ValueError('Found word fails scalar/helper or strict rank replay')
        witness=dict(steps=steps,final_wire_frames=current,final_completion_ranks=finish,
                     scalar_rows=scalar,rank_mass=mass,capacity=capacity,
                     arbitrary_dirty_helper_restored_in_scalar_map=True,
                     frame_bases=frames)
    digest=sha256()
    for state,cost in sorted(scores.items()):digest.update(f'{state}:{cost};'.encode())
    return dict(status=status,n=n,domain=kind,frame_count=count,roles=roles,capacity=capacity,
                searched_strict_budget=budget,start_frame_bases=[frames[i] for i in startframes],
                end_frame_bases=[frames[i] for i in endframes],
                scalar_target_rows=[2,1,4],expanded_states=expanded,discovered_states=len(scores),
                expanded_by_cost=dict(sorted(hist.items())),examined_admissible_edges=candidates,
                explored_state_sha256=digest.hexdigest(),witness=witness,
                seconds=time.monotonic()-started,
                completeness='No circuit-length cap; all CNOT orientations and every common frame are enumerated. Endpoint-distance pruning is admissible by the triangle inequality on each physical wire. Time/state-limited runs prove no exclusion.',
                scope='Abstract complete finite CNOT/common-Lagrangian-frame rank model only. All-width calls included. A positive word would require exact phase representatives, dirty payload-function replay, paid physical adapters and an all-size recurrence before any exponent claim.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',required=True,type=Path);ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--max-seconds',type=float,default=300);ap.add_argument('--max-states',type=int,default=500000)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(__file__).with_name('lagrangian_graph_completion.py')]
    specs=[(2,'graph'),(2,'full'),(3,'graph'),(3,'full')]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,
                  seed=None,specs=specs,max_seconds_each=args.max_seconds,max_states_each=args.max_states,
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    start=time.monotonic();receipts=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(search,n,kind,args.max_seconds,args.max_states):(n,kind) for n,kind in specs}
        for future in as_completed(jobs):
            result=future.result();receipts.append(result)
            name=f"n{result['n']}-{result['domain']}.json"
            (args.output/name).write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps({k:result[k] for k in ('status','n','domain','expanded_states','discovered_states','seconds')}),flush=True)
    summary=dict(status='COMPLETE SEARCH RECEIPTS',cases=receipts,seconds=time.monotonic()-start,
                 scope='Statuses distinguish complete finite exclusions, abstract positive rank words and inconclusive limits. No integer-multiplication exponent claimed.')
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')


if __name__=='__main__':main()
