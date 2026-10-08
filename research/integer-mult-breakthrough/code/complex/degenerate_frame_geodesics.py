#!/usr/bin/env python3
"""Exact subspace-to-Lagrangian embedding and a branching rank certificate.

Includes arbitrary degenerate spans, complementary directions, a complete
three-role local ledger, and transparent scalar dirty-restoration controls.
Literal Clifford edge execution and whole-motif integration are separate.
"""
import argparse
from collections import deque
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
from time import perf_counter

from lagrangian_phase_screen import basis,distance,graph_frames,pairing


def dot(a,b):return (a&b).bit_count()&1


def perpendicular(E,n):
    pivots={row.bit_length()-1:row for row in E};out=[]
    for free in range(n):
        if free in pivots:continue
        x=1<<free
        for j,row in pivots.items():
            if dot(row,x):x |=1<<j
        assert all(not dot(row,x) for row in E);out.append(x)
    return basis(tuple(out))


def lagrangian(E,n):
    E=basis(tuple(E));P=perpendicular(E,n)
    L=basis(P+tuple(x|(x<<n) for x in E))
    assert len(L)==n and all(not pairing(x,y,n) for x in L for y in L)
    return L


def intersection_dimension(E,F):return len(E)+len(F)-len(basis(E+F))


def all_subspaces(n):
    known={()};queue=deque(((),))
    while queue:
        E=queue.popleft()
        for v in range(1,1<<n):
            new=basis(E+(v,))
            if new not in known:known.add(new);queue.append(new)
    return sorted(known)


def random_subspace(rng,n):
    d=rng.randrange(n+1);E=()
    while len(E)<d:E=basis(E+(rng.randrange(1,1<<n),))
    return E


def check_pair(E,F,n):
    L=lagrangian(E,n);M=lagrangian(F,n)
    zero=lagrangian((),n);full=lagrangian(tuple(1<<j for j in range(n)),n)
    expected=len(E)+len(F)-2*intersection_dimension(E,F)
    assert distance(L,M,n)==expected
    assert distance(zero,L,n)==len(E) and distance(L,full,n)==n-len(E)
    if len(basis(E+F))==len(F):assert distance(L,M,n)==len(F)-len(E)
    EP,FP=perpendicular(E,n),perpendicular(F,n)
    assert distance(lagrangian(EP,n),lagrangian(FP,n),n)==expected
    radical=intersection_dimension(E,EP)
    assert intersection_dimension(L,lagrangian(EP,n))==2*radical
    return radical,expected


def line(t,n):
    assert t.bit_count()%2==1
    return lagrangian((t,),n)


def kernel(t,n):return lagrangian(perpendicular((t,),n),n)


def scalar_dirty_control():
    def L(v,inverse=False):
        v=list(v)
        if inverse:v[6]-=v[4];v[4]-=v[5]
        else:v[4]+=v[5];v[6]+=v[4]
        return v
    def J(v,sign):
        v=list(v);v[2]+=sign*v[4];v[3]+=sign*v[6];return v
    def V(v,sign):
        v=list(v);v[4]+=sign*v[0];v[5]+=sign*v[1];return v
    def word(v):
        v=L(v);v=J(v,-1);v=L(v,True);v=V(v,1)
        v=L(v);v=J(v,1);v=L(v,True);return V(v,-1)
    for j in range(7):
        v=[int(k==j) for k in range(7)];out=word(v);expected=list(v)
        expected[2]+=v[0]+v[1];expected[3]+=v[0]+v[1]
        assert out==expected
    arbitrary=[7,-3,11,-5,13,-17,19];out=word(arbitrary)
    assert out[4:]==arbitrary[4:]
    return dict(input_order=['x1','x7','y8','y14','a','b','p'],basis_inputs=7,
                virtual_side_map='Both y8 and y14 increase by x1+x7',
                virtual_dirty_scratch_restored=True,
                word=['L','-J','L^-1','V','L','J','L^-1','V^-1'])


def branching_certificate():
    n=4;U=basis((1,7));M=perpendicular(U,n);LU=lagrangian(U,n)
    assert U==(6,1) and M==(8,6) and LU==(96,17,8,6)
    graphs=graph_frames(n);zero=lagrangian((),n);full=lagrangian((1,2,4,8),n)
    inputs=[line(t,n) for t in (1,7)];outputs=[kernel(t,n) for t in (8,14)]
    rankcodes=[distance(zero,g,n) for g in graphs]
    costs1=[sum(distance(t,g,n) for t in inputs)+distance(g,full,n) for g in graphs]
    costs2=[distance(zero,g,n)+sum(distance(g,t,n) for t in outputs) for g in graphs]
    graph_minimum,a,b=min((4+costs1[a]+rankcodes[a^b]+costs2[b],a,b)
                          for a in range(len(graphs)) for b in range(len(graphs)))
    ranks={
        'a':[distance(zero,inputs[0],n),distance(inputs[0],LU,n),0,distance(LU,outputs[0],n),distance(outputs[0],full,n)],
        'b':[distance(zero,inputs[1],n),distance(inputs[1],LU,n),distance(LU,full,n)],
        'p':[distance(zero,LU,n),distance(LU,outputs[1],n),distance(outputs[1],full,n)]}
    assert all(sum(path)==n for path in ranks.values())
    assert graph_minimum==14 and sum(map(sum,ranks.values()))==12
    # Complementary direction is independently labeled, not a false product identity.
    reverse=lagrangian(M,n)
    reverse_inputs=[line(t,n) for t in (8,14)];reverse_outputs=[kernel(t,n) for t in (1,7)]
    reverse_total=4+sum(distance(t,reverse,n) for t in reverse_inputs)+distance(reverse,full,n)+distance(zero,reverse,n)+sum(distance(reverse,t,n) for t in reverse_outputs)
    assert reverse_total==12
    assert intersection_dimension(LU,reverse)==2
    return dict(ambient_dimension=n,source_directions=[1,7],target_directions=[8,14],
                source_span=U,target_span=M,radical_dimension=1,
                common_lagrangian=LU,reverse_common_lagrangian=reverse,
                forward_auxiliary_paths=ranks,forward_total_rank=12,reverse_total_rank=12,
                auxiliary_endpoint_capacity=12,all_symmetric_graph_minimum=graph_minimum,
                graph_minimizing_codes=[a,b],graph_assignment_count=len(graphs)**2,
                scalar_dirty_control=scalar_dirty_control(),
                literal_candidate='F_U=C_onbit0 * (SCS)_onbit1 * CNOT_1_to_2; reverse swaps bit0 and bit3',
                scope='Complete local auxiliary rank and scalar dirty certificate; literal phase matrices and external data transitions separately reviewed')


def run(n,mode,samples,seed):
    started=perf_counter();rng=random.Random(seed)
    if mode=='exhaustive':
        spaces=all_subspaces(n);pairs=product(spaces,repeat=2)
    else:pairs=((random_subspace(rng,n),random_subspace(rng,n)) for _ in range(samples))
    count=degenerate=0;digest=sha256()
    for E,F in pairs:
        rad,rank=check_pair(E,F,n);count+=1;degenerate +=rad>0
        digest.update(f'{E},{F}:{rad},{rank};'.encode())
    witness=None
    if n==8:
        U=basis((151,87,12));M=basis((211,31));H=perpendicular(M,n);w=204
        assert len(basis(U+(w,)))==len(U) and len(basis(M+(w,)))==len(M)
        assert all(not dot(w,v) for v in M)
        assert len(basis(U+H))==len(H)
        zero=lagrangian((),n);LU=lagrangian(U,n);LH=lagrangian(H,n);full=lagrangian(tuple(1<<j for j in range(n)),n)
        ranks=[distance(zero,LU,n),distance(LU,LH,n),distance(LH,full,n)]
        assert ranks==[3,3,2] and len(basis(LU+((w<<n),)))==n
        witness=dict(source_span=U,downstream_target_span=M,common_kernel_span=H,
                     old_forbidden_vector=w,new_vertical_direction=w<<n,
                     geodesic_ranks=ranks,total_rank=sum(ranks))
    return dict(status='PASS exact degenerate-subspace Lagrangian geometry',n=n,mode=mode,seed=seed,
                pair_cases=count,first_span_degenerate_cases=degenerate,
                result_sha256=digest.hexdigest(),weighted_tree_witness=witness,
                branching_certificate=branching_certificate() if n==4 else None,
                elapsed_seconds=perf_counter()-started,
                scope='Exact finite geometry plus mathematical embedding formula; component scalar dirty certificate; no whole network or exponent')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--n',type=int,required=True);p.add_argument('--mode',choices=('exhaustive','sampled'),default='sampled')
    p.add_argument('--samples',type=int,default=1024);p.add_argument('--seed',type=int,default=20261008);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if not 1<=a.n<=12 or a.samples<=0 or a.mode=='exhaustive' and a.n>4:raise ValueError('Unsupported bounded geometry')
    if a.output.exists():raise FileExistsError('Use a fresh output')
    result=run(a.n,a.mode,a.samples,a.seed);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('branching_certificate','weighted_tree_witness')}),flush=True)


if __name__=='__main__':main()
