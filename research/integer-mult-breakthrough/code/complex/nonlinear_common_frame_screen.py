#!/usr/bin/env python3
"""Bounded right-Toffoli common-frame screen with exact dyadic edge tests.

An admissible edge has one C^tensor(r) block child, arbitrary retained
finite address permutations and fourth-root row/column gauges. Those
nonlinear adapters are an optimistic exact-array interface, not a proved
fixed-tape router. Every input and output incidence is charged.
"""
import argparse
from collections import Counter,deque
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
from time import perf_counter

from lagrangian_phase_screen import (all_lagrangians,basis,cnot,distance,
    graph_frames,h,s)
from quadratic_rank_interface import symmetric_rows,Quadratic,walsh_reference


N=3;SIZE=1<<N


def add(a,b):return a[0]+b[0],a[1]+b[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def unit(a,k):return (a,(-a[1],a[0]),(-a[0],-a[1]),(a[1],-a[0]))[k%4]
def conj(a):return a[0],-a[1]


def normalize(rows,denominator):
    while denominator and all(not(x%2 or y%2) for row in rows for x,y in row):
        rows=[[(x//2,y//2) for x,y in row] for row in rows];denominator-=1
    return tuple(tuple(row) for row in rows),denominator


def compose(A,B):
    aa,ad=A;bb,bd=B;rows=[[(0,0)]*SIZE for _ in range(SIZE)]
    for i in range(SIZE):
        for k,a in enumerate(aa[i]):
            if a==(0,0):continue
            for j,b in enumerate(bb[k]):
                if b!=(0,0):rows[i][j]=add(rows[i][j],mul(a,b))
    return normalize(rows,ad+bd)


def inverse(A):
    a,d=A;return tuple(tuple(conj(a[j][i]) for j in range(SIZE)) for i in range(SIZE)),d


def permutation(values):
    assert sorted(values)==list(range(SIZE))
    return tuple(tuple((int(x==values[y]),0) for y in range(SIZE)) for x in range(SIZE)),0


I=permutation(list(range(SIZE)))


def graph_operator(code):
    rows=symmetric_rows(N,code);q=Quadratic(rows,[(row>>j)&1 for j,row in enumerate(rows)])
    nums=walsh_reference(q)
    return normalize([[nums[a^b] for b in range(SIZE)] for a in range(SIZE)],N)


def c_bit(bit):
    return normalize([[(1,1) if a==b else (1,-1) if a==b^(1<<bit) else (0,0)
                       for b in range(SIZE)] for a in range(SIZE)],1)


def h_bit(bit):
    return normalize([[((-1,-1) if a>>bit&1 and b>>bit&1 else (1,1))
                        if a&~(1<<bit)==b&~(1<<bit) else (0,0)
                        for b in range(SIZE)] for a in range(SIZE)],1)


def clifford_representatives():
    initial=basis((1,2,4));known={initial:(I,[])};queue=deque((initial,))
    generators=[]
    for j in range(N):
        generators.append((lambda v,j=j:h(v,j,N),h_bit(j),['Htilde',j]))
        generators.append((lambda v,j=j:s(v,j,N),c_bit(j),['C',j]))
    for a in range(N):
        for b in range(N):
            if a==b:continue
            # The screen's symplectic convention is the transpose CNOT.
            P=permutation([x^((1<<a) if x>>b&1 else 0) for x in range(SIZE)])
            generators.append((lambda v,a=a,b=b:cnot(v,a,b,N),P,['CNOT',b,a]))
    while queue:
        L=queue.popleft();F,word=known[L]
        for action,G,description in generators:
            new=basis(tuple(action(v) for v in L))
            if new not in known:known[new]=(compose(F,G),word+[description]);queue.append(new)
    assert set(known)==set(all_lagrangians(N)) and len(known)==135
    assert all(compose(F,inverse(F))==I for F,_ in known.values())
    return [(L,*known[L]) for L in sorted(known)]


def phase_of_scaled(value,reference,value_den,reference_den):
    for k in range(4):
        expected=unit(reference,k)
        if (value[0]*(1<<reference_den),value[1]*(1<<reference_den))==(expected[0]*(1<<value_den),expected[1]*(1<<value_den)):
            return k
    return None


def single_child(A,retain=False):
    """Recognize flat Walsh-equivalent blocks without affine restrictions."""
    rows,den=A;supports=[tuple(j for j,z in enumerate(row) if z!=(0,0)) for row in rows]
    degrees={len(support) for support in supports}
    if len(degrees)!=1:return None
    D=next(iter(degrees))
    if D==0 or D&(D-1):return None
    r=D.bit_length()-1;c0=(1,0)
    for _ in range(r):c0=mul(c0,(1,1))
    groups={support:tuple(i for i,support_i in enumerate(supports) if support_i==support) for support in set(supports)}
    if any(len(group)!=D for group in groups.values()):return None
    if any(set(a)&set(b) for a,b in product(groups,repeat=2) if a!=b):return None
    input_map=[None]*SIZE;output_map=[None]*SIZE;qin=[0]*SIZE;qout=[0]*SIZE
    for block,(columns,row_ids) in enumerate(sorted(groups.items())):
        a0,b0=row_ids[0],columns[0];patterns={}
        for a in row_ids:
            pattern=0
            for j,b in enumerate(columns):
                num=mul(rows[a][b],rows[a0][b0]);ref=mul(rows[a][b0],rows[a0][b])
                if num==(-ref[0],-ref[1]):pattern |=1<<j
                elif num!=ref:return None
            if pattern in patterns:return None
            patterns[pattern]=a
        row_basis=basis(tuple(patterns))
        if len(row_basis)!=r or len(patterns)!=1<<r:return None
        combinations={}
        for x in range(1<<r):
            pattern=0
            for j,row in enumerate(row_basis):
                if x>>j&1:pattern ^=row
            if pattern not in patterns:return None
            combinations[pattern]=x
        column_labels=[]
        for j,b in enumerate(columns):
            label=sum(((pattern>>j)&1)<<k for k,pattern in enumerate(row_basis))
            column_labels.append(label)
        if len(set(column_labels))!=D:return None
        for pattern,a in patterns.items():
            label=combinations[pattern];index=(block<<r)|label;output_map[index]=a
            phase=phase_of_scaled(rows[a][b0],c0,den,r)
            if phase is None:return None
            qout[index]=(phase+label.bit_count())%4
        for b,label in zip(columns,column_labels):
            index=(block<<r)|label;input_map[index]=b
            phase=phase_of_scaled(rows[a0][b],rows[a0][b0],den,den)
            if phase is None:return None
            qin[index]=(phase+label.bit_count())%4
    nf=dict(rank=r,input_permutation=input_map,output_permutation=output_map,
            input_unit_exponents=qin,output_unit_exponents=qout)
    assert reconstruct(nf)==A
    return nf if retain else r


def reconstruct(nf):
    r=nf['rank'];rows=[[(0,0)]*SIZE for _ in range(SIZE)];mask=(1<<r)-1
    for a,b in product(range(SIZE),repeat=2):
        if a>>r!=b>>r:continue
        z=(1,0)
        for j in range(r):z=mul(z,(1,-1) if (a^b)>>j&1 else (1,1))
        z=unit(z,nf['output_unit_exponents'][a]+nf['input_unit_exponents'][b])
        rows[nf['output_permutation'][a]][nf['input_permutation'][b]]=z
    return normalize(rows,r)


def nonlinear_permutation(kind):
    def gate(x,target):
        controls=[j for j in range(N) if j!=target]
        return x^((1<<target) if all(x>>j&1 for j in controls) else 0)
    targets=[int(kind[-1])] if kind.startswith('toffoli') else [0,1,2]
    values=[]
    for x in range(SIZE):
        for target in targets:x=gate(x,target)
        values.append(x)
    assert values!=list(range(SIZE))
    return permutation(values),targets


def run(kind,samples,seed):
    started=perf_counter();representatives=clifford_representatives();graphs=graph_frames(N)
    graph_ops=[graph_operator(c) for c in range(64)];P,targets=nonlinear_permutation(kind)
    baseline_rows=[[distance(L,graph,N) for graph in graphs] for L,_,_ in representatives]
    costs=[];admissibility=Counter();full_candidates=[]
    for L,F,word in representatives:
        nonlinear=compose(F,P);row=[]
        for code,endpoint in enumerate(graph_ops):
            edge=compose(nonlinear,inverse(endpoint));rank=single_child(edge)
            row.append(rank);admissibility['valid' if rank is not None else 'not_single_child']+=1
        costs.append(row);full_candidates.append((L,nonlinear,word))
    # Affine/Clifford control: every exact edge rank equals its metric rank.
    for L,F,_ in representatives:
        for code,endpoint in enumerate(graph_ops):
            assert single_child(compose(F,inverse(endpoint)))==distance(L,graphs[code],N)
    # A componentwise dominator excludes a gain for ANY terminal multiset
    # whose edges lie in this admitted one-child interface, not just samples.
    dominance=[];undominated=[]
    for index,row in enumerate(costs):
        valid=[code for code,rank in enumerate(row) if rank is not None]
        candidate=next((j for j,baseline in enumerate(baseline_rows)
                        if all(baseline[code]<=row[code] for code in valid)),None)
        if candidate is None:undominated.append(index)
        else:dominance.append(dict(nonlinear_candidate=index,valid_graph_codes=valid,
            nonlinear_ranks=[row[code] for code in valid],
            dominating_clifford_candidate=candidate,
            dominating_lagrangian=representatives[candidate][0],
            dominating_ranks=[baseline_rows[candidate][code] for code in valid]))
    rng=random.Random(seed);cases=[(3,23,35,56)]+[tuple(sorted(rng.sample(range(64),4))) for _ in range(samples)]
    strict=[];admissible_cases=0;maximum_gain=0;digest=sha256()
    for terminals in cases:
        baseline=min(sum(row[c] for c in terminals) for row in baseline_rows)
        options=[(sum(row[c] for c in terminals),j) for j,row in enumerate(costs) if all(row[c] is not None for c in terminals)]
        if not options:
            digest.update(f'{terminals}:{baseline},none;'.encode());continue
        admissible_cases+=1;cost,candidate=min(options);gain=baseline-cost
        digest.update(f'{terminals}:{baseline},{cost};'.encode());maximum_gain=max(maximum_gain,gain)
        if gain>0 and len(strict)<8:
            L,F,word=full_candidates[candidate]
            strict.append(dict(terminal_graph_codes=terminals,clifford_baseline=baseline,
                nonlinear_cost=cost,rank_gain=gain,parent_clifford_lagrangian=L,
                parent_clifford_word=word,right_toffoli_targets=targets,
                edges=[single_child(compose(F,inverse(graph_ops[c])),True) for c in terminals]))
    return dict(status='EXACT BOUNDED NONLINEAR COMMON-FRAME SCREEN',family=kind,
                right_toffoli_targets=targets,clifford_representatives=135,graph_endpoints=64,
                edge_admissibility=dict(admissibility),clifford_control_edges=8640,
                dominated_nonlinear_candidates=len(dominance),undominated_nonlinear_candidates=undominated,
                componentwise_dominance_certificates=dominance,
                four_incidence_cases=len(cases),admissible_nonlinear_cases=admissible_cases,
                maximum_rank_gain=maximum_gain,promising_witnesses=strict,seed=seed,
                result_sha256=digest.hexdigest(),elapsed_seconds=perf_counter()-started,
                scope='Finite exact-array one-child interface with arbitrary retained nonlinear routers/unit gauges; no recursive router theorem, whole circuit, dirty chronology or exponent. Failure of this interface does not exclude multi-child edges or other nonlinear families.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--family',choices=('toffoli0','toffoli1','toffoli2','cycle'),required=True)
    p.add_argument('--samples',type=int,default=1024);p.add_argument('--seed',type=int,default=20261008)
    p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if a.samples<=0 or a.output.exists():raise ValueError('Positive samples and a fresh output required')
    result=run(a.family,a.samples,a.seed);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('promising_witnesses','componentwise_dominance_certificates')}),flush=True)


if __name__=='__main__':main()
