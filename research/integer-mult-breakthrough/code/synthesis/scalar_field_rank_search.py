#!/usr/bin/env python3
"""Common-frame reversible synthesis over F3 and Gaussian F9 residues.

All elementary row additions and nonzero row scalings are included. F9 is
F3[i], i^2=-1, the Gaussian-dyadic residue field modulo three. A complete
negative excludes that finite superset of scalar lifts; a modular positive
requires an exact characteristic-zero reconstruction before promotion.
"""
import argparse
from array import array
from collections import Counter,deque
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time

from dirty_helper_rank_search import frame_domain
from lagrangian_graph_completion import distance,graph


class Field:
    def __init__(self,q):
        if q not in (3,9):raise ValueError('Only declared residue fields are supported')
        self.q=q
        self.add=[[self.addition(a,b) for b in range(q)] for a in range(q)]
        self.mul=[[self.multiplication(a,b) for b in range(q)] for a in range(q)]
    def addition(self,a,b):
        if self.q==3:return (a+b)%3
        return (a%3+b%3)%3+3*((a//3+b//3)%3)
    def multiplication(self,a,b):
        if self.q==3:return a*b%3
        return ((a%3)*(b%3)-(a//3)*(b//3))%3+3*(((a%3)*(b//3)+(a//3)*(b%3))%3)
    def row_tables(self,k):
        q=self.q;size=q**k;digits=[tuple((r//(q**j))%q for j in range(k)) for r in range(size)]
        powers=[q**j for j in range(k)]
        addition=[array('H',(sum(self.add[a][b]*powers[j] for j,(a,b) in enumerate(zip(left,right)))
                               for right in digits)) for left in digits]
        scaling=[array('H',(sum(self.mul[c][a]*powers[j] for j,a in enumerate(row)) for row in digits)) for c in range(q)]
        return size,addition,scaling


def search(n,kind,q,max_seconds,max_states):
    started=time.monotonic();field=Field(q);frames=frame_domain(n,kind);count=len(frames);ids={f:j for j,f in enumerate(frames)}
    distances=[[distance(a,b,n) for b in frames] for a in frames]
    zero=ids[graph((0,)*n)];full=ids[graph(tuple(1<<j for j in range(n)))]
    rank=1 if n==2 else 2
    p=ids[graph(tuple((1<<j) if j<rank else 0 for j in range(n)))]
    complement=ids[graph(tuple((1<<j) if j>=rank else 0 for j in range(n)))]
    starts=(p,zero,zero);ends=(full,complement,full);roles=3;capacity=roles*n;budget=capacity-1
    rowsize,addition,scaling=field.row_tables(roles);rowpowers=[rowsize**j for j in range(roles)]
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
            finish=[finish_table[j][current[j]] for j in range(roles)];finish_sum=sum(finish)
            if cost+finish_sum>budget:continue
            if matrix==target_matrix:found=(state,cost,finish);status='FOUND STRICT MODULAR RANK WORD';break
            expanded+=1;hist[cost]+=1
            if expanded%1000==0 and time.monotonic()-started>max_seconds:status='UNKNOWN TIME LIMIT';break
            # Scalar unit multiplication preserves the physical wire frame.
            for role in range(roles):
                for coefficient in range(2,q):
                    newrow=scaling[coefficient][rows[role]]
                    newstate=((matrix+(newrow-rows[role])*rowpowers[role])<<total_frame_bits)|fcode
                    admissible_edges+=1
                    if cost>=scores.get(newstate,capacity):continue
                    scores[newstate]=cost;parents[newstate]=(state,'scale',role,None,None,coefficient,0)
                    buckets[cost].append(newstate)
                    if len(scores)>=max_states:status='UNKNOWN STATE LIMIT';break
                if status:break
            if status:break
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
                            newrow=addition[rows[dest]][scaling[coefficient][rows[source]]]
                            newmatrix=matrix+(newrow-rows[dest])*rowpowers[dest]
                            newstate=(newmatrix<<total_frame_bits)|newf;admissible_edges+=1
                            if newcost>=scores.get(newstate,capacity):continue
                            scores[newstate]=newcost;parents[newstate]=(state,'add',dest,source,common,coefficient,increment)
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
            previous,op,dest,source,common,coefficient,increment=parents[state]
            steps.append(dict(op=op,destination=dest,source=source,common_frame=common,coefficient=coefficient,rank_charge=increment));state=previous
        steps.reverse();scalar=[[int(i==j) for j in range(roles)] for i in range(roles)];current=list(starts);mass=0
        for step in steps:
            dest,source,c=step['destination'],step['source'],step['coefficient']
            if step['op']=='scale':scalar[dest]=[field.mul[c][a] for a in scalar[dest]]
            else:
                common=step['common_frame'];measured=distance(frames[current[dest]],frames[common],n)+distance(frames[current[source]],frames[common],n)
                if measured!=step['rank_charge']:raise ValueError('Modular witness rank replay failed')
                mass+=measured;current[dest]=current[source]=common
                scalar[dest]=[field.add[a][field.mul[c][b]] for a,b in zip(scalar[dest],scalar[source])]
        finish=[distance(frames[current[j]],frames[ends[j]],n) for j in range(roles)];mass+=sum(finish)
        if scalar!=[[0,1,0],[1,0,0],[0,0,1]] or mass>=capacity:raise ValueError('Modular witness scalar or strict rank replay failed')
        witness=dict(steps=steps,frame_bases=frames,final_frame_ids=current,final_completion_ranks=finish,
                     rank_mass=mass,capacity=capacity,scalar_rows=scalar,
                     characteristic_zero_reconstruction='NOT YET ESTABLISHED; residue coefficients and final matrix must be lifted exactly before physical claims')
    digest=sha256()
    for state,cost in sorted(scores.items()):digest.update(f'{state}:{cost};'.encode())
    return dict(status=status,n=n,domain=kind,scalar_field_size=q,projector_rank=rank,frame_count=count,
                roles=roles,capacity=capacity,strict_budget=budget,start_frame_bases=[frames[j] for j in starts],end_frame_bases=[frames[j] for j in ends],
                expanded_states=expanded,discovered_states=len(scores),expanded_by_cost=dict(sorted(hist.items())),admissible_edges=admissible_edges,
                explored_state_sha256=digest.hexdigest(),witness=witness,seconds=time.monotonic()-started,
                completeness='All finite words of common-frame row additions with any nonzero coefficient and single-wire nonzero scalar multipliers. No circuit-length cap; triangle-inequality endpoint pruning. Resource-limited runs prove no exclusion.',
                scope='Complete finite scalar-field and Lagrangian-rank model only. F9 is reduction of Gaussian dyadics modulo3; a complete exclusion applies to Gaussian-dyadic invertible scalar lifts within these geometry/roles. Any modular positive requires exact characteristic-zero phase/payload and cost reconstruction.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--workers',type=int,default=4);ap.add_argument('--max-seconds',type=float,default=300)
    ap.add_argument('--max-states',type=int,default=500000);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(__file__).with_name('dirty_helper_rank_search.py'),Path(__file__).with_name('lagrangian_graph_completion.py')]
    specs=[(2,'graph',9),(2,'full',9),(3,'graph',3),(3,'full',3)]
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
            print(json.dumps({k:result[k] for k in ('status','n','domain','scalar_field_size','expanded_states','discovered_states','seconds')}),flush=True)
    (args.output/'summary.json').write_text(json.dumps(dict(status='COMPLETE SEARCH RECEIPTS',cases=receipts,seconds=time.monotonic()-start),indent=2)+'\n')


if __name__=='__main__':main()
