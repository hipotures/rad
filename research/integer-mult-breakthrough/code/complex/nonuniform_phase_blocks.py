#!/usr/bin/env python3
"""Exact direct-sum C-block screen beyond the uniform-child interface.

Volume-weighted ranks are a finite entropy/array proxy only. Tensor-column
packing, routing, actual recursive volumes and guards are not supplied.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
from time import perf_counter

from nonlinear_common_frame_screen import (N,SIZE,add,mul,unit,normalize,
    compose,inverse,graph_operator,clifford_representatives,phase_of_scaled,
    nonlinear_permutation)
from lagrangian_phase_screen import basis,distance,graph_frames


def classify(A,retain=False):
    rows,den=A;supports=[tuple(j for j,z in enumerate(row) if z!=(0,0)) for row in rows]
    if any(not support for support in supports):return None,'zero-row'
    groups={support:tuple(i for i,s in enumerate(supports) if s==support) for support in set(supports)}
    if any(set(a)&set(b) for a,b in product(groups,repeat=2) if a!=b):return None,'overlapping-supports'
    blocks=[];rank_volume=0
    for columns,row_ids in sorted(groups.items()):
        D=len(columns)
        if len(row_ids)!=D or D&(D-1):return None,'non-dyadic-block-size'
        r=D.bit_length()-1;c0=(1,0)
        for _ in range(r):c0=mul(c0,(1,1))
        a0,b0=row_ids[0],columns[0];patterns={}
        for a in row_ids:
            pattern=0
            for j,b in enumerate(columns):
                num=mul(rows[a][b],rows[a0][b0]);ref=mul(rows[a][b0],rows[a0][b])
                if num==(-ref[0],-ref[1]):pattern |=1<<j
                elif num!=ref:return None,'non-real-dephased-block'
            if pattern in patterns:return None,'duplicate-dephased-row'
            patterns[pattern]=a
        B=basis(tuple(patterns))
        if len(B)!=r or len(patterns)!=1<<r:return None,'non-Walsh-row-group'
        labels={}
        for x in range(1<<r):
            pattern=0
            for j,v in enumerate(B):
                if x>>j&1:pattern ^=v
            if pattern not in patterns:return None,'non-Walsh-row-group'
            labels[pattern]=x
        ins=[None]*D;outs=[None]*D;qin=[0]*D;qout=[0]*D
        for pattern,a in patterns.items():
            label=labels[pattern];outs[label]=a
            phase=phase_of_scaled(rows[a][b0],c0,den,r)
            if phase is None:return None,'non-C-magnitude'
            qout[label]=(phase+label.bit_count())%4
        for j,b in enumerate(columns):
            label=sum(((pattern>>j)&1)<<k for k,pattern in enumerate(B));ins[label]=b
            phase=phase_of_scaled(rows[a0][b],rows[a0][b0],den,den)
            if phase is None:return None,'nonunit-phase'
            qin[label]=(phase+label.bit_count())%4
        if sorted(ins)!=sorted(columns) or sorted(outs)!=sorted(row_ids):return None,'bad-Walsh-coordinates'
        blocks.append(dict(rank=r,volume_records=D,input_addresses=ins,output_addresses=outs,
                           input_unit_exponents=qin,output_unit_exponents=qout))
        rank_volume+=D*r
    nf=dict(blocks=blocks,average_rank=str(Q(rank_volume,SIZE)))
    assert reconstruct(nf)==A
    return (nf if retain else Q(rank_volume,SIZE)),'exact-direct-sum'


def reconstruct(nf):
    maxrank=max(b['rank'] for b in nf['blocks']);rows=[[(0,0)]*SIZE for _ in range(SIZE)]
    for block in nf['blocks']:
        r=block['rank'];D=1<<r
        for a,b in product(range(D),repeat=2):
            z=(1,0)
            for j in range(r):z=mul(z,(1,-1) if (a^b)>>j&1 else (1,1))
            z=unit(z,block['output_unit_exponents'][a]+block['input_unit_exponents'][b])
            rows[block['output_addresses'][a]][block['input_addresses'][b]]=tuple(v*(1<<(maxrank-r)) for v in z)
    return normalize(rows,maxrank)


def run(kind,samples,seed):
    started=perf_counter();reps=clifford_representatives();graphs=graph_frames(N)
    endpoints=[graph_operator(c) for c in range(64)];P,targets=nonlinear_permutation(kind)
    baseline=[[Q(distance(L,G,N)) for G in graphs] for L,_,_ in reps]
    costs=[];reasons=Counter();profiles=Counter();frames=[]
    for L,F,word in reps:
        F=compose(F,P);frames.append((L,F,word));row=[]
        for endpoint in endpoints:
            edge=compose(F,inverse(endpoint));cost,reason=classify(edge)
            row.append(cost);reasons[reason]+=1
            if cost is not None:
                nf,_=classify(edge,True)
                profile=tuple(sorted((b['rank'],b['volume_records']) for b in nf['blocks']))
                profiles[profile]+=1
        costs.append(row)
    undominated=[];dominated=0
    for j,row in enumerate(costs):
        valid=[c for c,x in enumerate(row) if x is not None]
        if any(all(base[c]<=row[c] for c in valid) for base in baseline):dominated+=1
        else:undominated.append(j)
    rng=random.Random(seed);cases=[(3,23,35,56)]+[tuple(sorted(rng.sample(range(64),4))) for _ in range(samples)]
    # A small discriminator samples only admitted edges of each undominated
    # candidate; uniformly sampling all64 endpoints can miss rare interfaces.
    for j in undominated:
        valid=[c for c,x in enumerate(costs[j]) if x is not None]
        if len(valid)>=4:
            cases.extend(tuple(sorted(rng.sample(valid,4))) for _ in range(16))
    scaled_baseline=[[int(x*SIZE) for x in row] for row in baseline]
    scaled_costs=[[None if x is None else int(x*SIZE) for x in row] for row in costs]
    witnesses=[];gains=0;maximum=Q();digest=sha256()
    for terminals in cases:
        old=Q(min(sum(base[c] for c in terminals) for base in scaled_baseline),SIZE)
        options=[(sum(row[c] for c in terminals),j) for j,row in enumerate(scaled_costs) if all(row[c] is not None for c in terminals)]
        if not options:continue
        new,j=min(options);new=Q(new,SIZE);gain=old-new;digest.update(f'{terminals}:{old},{new};'.encode())
        if gain>0:
            gains+=1;maximum=max(maximum,gain)
            if len(witnesses)<8:
                L,F,word=frames[j]
                witnesses.append(dict(terminal_graph_codes=terminals,baseline_rank=str(old),
                    average_rank_proxy=str(new),gain=str(gain),parent_clifford_lagrangian=L,
                    parent_clifford_word=word,right_toffoli_targets=targets,
                    edges=[classify(compose(F,inverse(endpoints[c])),True)[0] for c in terminals]))
    return dict(status='EXACT NONUNIFORM C-BLOCK ARRAY SCREEN',family=kind,
                right_toffoli_targets=targets,complete_edge_cases=135*64,
                edge_classification=dict(reasons),block_profiles=[dict(profile=p,count=n) for p,n in sorted(profiles.items())],
                dominated_candidates=dominated,undominated_candidates=undominated,
                sampled_four_incidence_cases=len(cases),proxy_gain_cases=gains,maximum_proxy_gain=str(maximum),
                witnesses=witnesses,seed=seed,result_sha256=digest.hexdigest(),elapsed_seconds=perf_counter()-started,
                scope='Exact finite direct-sum coefficients with volume-weighted rank proxy only. Nonuniform tensor-column routing, recursive child volumes, literal gates/dirty continuation, guards and exponent remain unproved.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--family',choices=('toffoli0','toffoli1','toffoli2','cycle'),required=True)
    p.add_argument('--samples',type=int,default=1024);p.add_argument('--seed',type=int,default=20261008)
    p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if a.samples<=0 or a.output.exists():raise ValueError('Positive samples and a fresh output required')
    result=run(a.family,a.samples,a.seed);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('witnesses','block_profiles')}),flush=True)


if __name__=='__main__':main()
