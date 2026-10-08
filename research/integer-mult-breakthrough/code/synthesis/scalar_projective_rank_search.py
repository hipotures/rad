#!/usr/bin/env python3
"""Exact projective-row quotient of free-unit common-frame synthesis.

Independent nonzero row scalings have zero rank charge. Normalize each
scalar row's first nonzero entry to one. An update R_d += c R_s still
enumerates every nonzero relative coefficient, followed by a free unit
normalization. This quotient preserves finite common-frame rank words.
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
from scalar_field_rank_search import Field


def search(n,kind,q,max_seconds,max_states):
    started=time.monotonic();field=Field(q);frames=frame_domain(n,kind);count=len(frames);ids={f:j for j,f in enumerate(frames)}
    distances=[[distance(a,b,n) for b in frames] for a in frames]
    zero=ids[graph((0,)*n)];full=ids[graph(tuple(1<<j for j in range(n)))]
    rank=1 if n==2 else 2
    p=ids[graph(tuple((1<<j) if j<rank else 0 for j in range(n)))]
    complement=ids[graph(tuple((1<<j) if j>=rank else 0 for j in range(n)))]
    starts=(p,zero,zero);ends=(full,complement,full);roles=3;capacity=roles*n;budget=capacity-1
    rowsize,addition,scaling=field.row_tables(roles);rowpowers=[rowsize**j for j in range(roles)]
    inverses={c:next(b for b in range(1,q) if field.mul[c][b]==1) for c in range(1,q)}
    normalize=[0]*rowsize;normal_unit=[0]*rowsize
    for row in range(1,rowsize):
        pivot=next((row//(q**j))%q for j in range(roles) if (row//(q**j))%q)
        normal_unit[row]=inverses[pivot];normalize[row]=scaling[inverses[pivot]][row]
    initial_rows=[q**j for j in range(roles)];target_rows=[q,1,q*q]
    initial_matrix=sum(r*c for r,c in zip(initial_rows,rowpowers));target_matrix=sum(r*c for r,c in zip(target_rows,rowpowers))
    fbits=(count-1).bit_length();single=(1<<fbits)-1;total_frame_bits=roles*fbits;frame_mask=(1<<total_frame_bits)-1
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
            rows=tuple((matrix//power)%rowsize for power in rowpowers)
            if any(normalize[r]!=r for r in rows):raise ValueError('Unnormalized projective scalar state')
            finish=[finish_table[j][current[j]] for j in range(roles)];finish_sum=sum(finish)
            if cost+finish_sum>budget:continue
            if matrix==target_matrix:found=(state,cost,finish);status='FOUND STRICT MODULAR RANK WORD';break
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
                        for coefficient in range(1,q):
                            rawrow=addition[rows[dest]][scaling[coefficient][rows[source]]]
                            if not rawrow:raise ValueError('Invertible scalar state developed a zero row')
                            newrow=normalize[rawrow];unit=normal_unit[rawrow]
                            newmatrix=matrix+(newrow-rows[dest])*rowpowers[dest]
                            newstate=(newmatrix<<total_frame_bits)|newf;admissible_edges+=1
                            if newcost>=scores.get(newstate,capacity):continue
                            scores[newstate]=newcost;parents[newstate]=(state,dest,source,common,coefficient,unit,increment)
                            buckets[newcost].append(newstate)
                            if len(scores)>=max_states:status='UNKNOWN STATE LIMIT';break
                        if status:break
                    if status:break
                if status:break
            if status:break
        if status:break
    if status is None:status='EXCLUDED BELOW CAPACITY IN COMPLETE FINITE MODEL'
    witness=None
    if found:
        state,cost,finish=found;steps=[]
        while state!=initial:
            previous,dest,source,common,coefficient,unit,increment=parents[state]
            steps.append(dict(destination=dest,source=source,common_frame=common,
                              coefficient=coefficient,normalizing_scalar=unit,rank_charge=increment));state=previous
        steps.reverse();scalar=[[int(i==j) for j in range(roles)] for i in range(roles)];current=list(starts);mass=0
        for step in steps:
            dest,source,c,unit=step['destination'],step['source'],step['coefficient'],step['normalizing_scalar']
            common=step['common_frame'];measured=distance(frames[current[dest]],frames[common],n)+distance(frames[current[source]],frames[common],n)
            if measured!=step['rank_charge']:raise ValueError('Projective witness rank replay failed')
            mass+=measured;current[dest]=current[source]=common
            scalar[dest]=[field.mul[unit][field.add[a][field.mul[c][b]]] for a,b in zip(scalar[dest],scalar[source])]
        finish=[distance(frames[current[j]],frames[ends[j]],n) for j in range(roles)];mass+=sum(finish)
        if scalar!=[[0,1,0],[1,0,0],[0,0,1]] or mass>=capacity:raise ValueError('Projective word fails modular scalar/rank replay')
        witness=dict(steps=steps,frame_bases=frames,final_frame_ids=current,final_completion_ranks=finish,
                     rank_mass=mass,capacity=capacity,scalar_rows=scalar,characteristic_zero_reconstruction='NOT ESTABLISHED')
    digest=sha256()
    for state,cost in sorted(scores.items()):digest.update(f'{state}:{cost};'.encode())
    return dict(status=status,n=n,domain=kind,scalar_field_size=q,projector_rank=rank,frame_count=count,
                roles=roles,capacity=capacity,strict_budget=budget,start_frame_bases=[frames[j] for j in starts],end_frame_bases=[frames[j] for j in ends],
                expanded_states=expanded,discovered_projective_states=len(scores),expanded_by_cost=dict(sorted(hist.items())),admissible_edges=admissible_edges,
                projective_state_sha256=digest.hexdigest(),witness=witness,seconds=time.monotonic()-started,
                quotient='Each nonzero scalar row normalized at first nonzero coefficient; all relative row-addition coefficients remain available, so free independent row units do not change reachability or rank minima.',
                completeness='All finite common-frame additions and nonzero single-wire scalar units; no circuit-length cap, exact per-wire endpoint-distance pruning. Resource-limited statuses prove no exclusion.',
                scope='Abstract complete finite scalar-field/Lagrangian-rank model. Complete F9 exclusion rules out invertible Gaussian-dyadic scalar lifts within the specified roles/frames; modular positives require exact lifting and full physical/cost evidence.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--workers',type=int,default=4);ap.add_argument('--max-seconds',type=float,default=300)
    ap.add_argument('--max-states',type=int,default=500000);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(__file__).with_name('scalar_field_rank_search.py'),Path(__file__).with_name('dirty_helper_rank_search.py'),Path(__file__).with_name('lagrangian_graph_completion.py')]
    specs=[(2,'graph',9),(2,'full',9),(3,'graph',9),(3,'full',9)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,seed=None,
                  specs=specs,max_seconds_each=args.max_seconds,max_states_each=args.max_states,
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');receipts=[];start=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(search,*spec,args.max_seconds,args.max_states):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();receipts.append(result)
            name=f"n{result['n']}-{result['domain']}-F{result['scalar_field_size']}.json"
            (args.output/name).write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps({k:result[k] for k in ('status','n','domain','scalar_field_size','expanded_states','discovered_projective_states','seconds')}),flush=True)
    (args.output/'summary.json').write_text(json.dumps(dict(status='COMPLETE SEARCH RECEIPTS',cases=receipts,seconds=time.monotonic()-start),indent=2)+'\n')


if __name__=='__main__':main()
