#!/usr/bin/env python3
"""Literal dyadic two-role shear using a non-graph common phase frame.

Both incoming and both outgoing transitions are charged. The exact small
normal forms below retain affine adapters, unit chirps and one rank-r C
tensor, independently of their conceptual full-Clifford frame labels.
"""
import argparse
from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations,product
import json
from pathlib import Path
from time import perf_counter

from quadratic_rank_interface import Quadratic,tensor_c_numerator,walsh_reference
from lagrangian_phase_screen import all_lagrangians,basis,distance,graph_frames


ZERO=(F(0),F(0));ONE=(F(1),F(0));UNITS=(ONE,(F(0),F(1)),(F(-1),F(0)),(F(0),F(-1)))


def add(a,b):return a[0]+b[0],a[1]+b[1]
def neg(a):return -a[0],-a[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def conj(a):return a[0],-a[1]
def div(a,b):
    norm=b[0]*b[0]+b[1]*b[1];z=mul(a,conj(b));return z[0]/norm,z[1]/norm


def compose(A,B):return [[sum_complex(mul(A[i][k],B[k][j]) for k in range(len(A))) for j in range(len(A))] for i in range(len(A))]
def sum_complex(values):
    z=ZERO
    for value in values:z=add(z,value)
    return z
def inverse(A):return [[conj(A[j][i]) for j in range(len(A))] for i in range(len(A))]
def identity(n):return [[ONE if i==j else ZERO for j in range(n)] for i in range(n)]


def matrix_rows(code,n=3):
    rows=[0]*n;p=0
    for j in range(n):
        for k in range(j,n):
            if code>>p&1:rows[j] |=1<<k;rows[k] |=1<<j
            p+=1
    return rows


def graph_operator(code):
    rows=matrix_rows(code);q=Quadratic(rows,[(row>>j)&1 for j,row in enumerate(rows)])
    num=walsh_reference(q)
    return [[(F(num[a^b][0],8),F(num[a^b][1],8)) for b in range(8)] for a in range(8)]


def hadamard_dyadic(bit):
    value=(F(1,2),F(1,2));result=[[ZERO]*8 for _ in range(8)]
    for a,b in product(range(8),repeat=2):
        if (a&~(1<<bit))==(b&~(1<<bit)):
            result[a][b]=neg(value) if (a>>bit&1) and (b>>bit&1) else value
    return result


def embed(x,columns):
    value=0
    for j,v in enumerate(columns):
        if x>>j&1:value ^=v
    return value


def quadratic_exponents(values):
    n=(len(values)-1).bit_length();constant=values[0];linear=[(values[1<<j]-constant)%4 for j in range(n)]
    cross={}
    for j in range(n):
        for k in range(j+1,n):
            coefficient=(values[(1<<j)|(1<<k)]-constant-linear[j]-linear[k])%4
            if coefficient not in (0,2):return None
            cross[j,k]=coefficient
    expected=[(constant+sum(linear[j] for j in range(n) if x>>j&1)+sum(v for (j,k),v in cross.items() if x>>j&1 and x>>k&1))%4 for x in range(1<<n)]
    return dict(constant=constant,linear=linear,cross=[(j,k,v) for (j,k),v in cross.items() if v]) if expected==values else None


def compile_edge(A):
    support0=[a for a in range(8) if A[a][0]!=ZERO];a0=min(support0)
    r=(len(support0)-1).bit_length();assert len(support0)==1<<r
    Rout=basis(tuple(a^a0 for a in support0));columns0=[b for b in range(8) if A[a0][b]!=ZERO]
    Rin=basis(tuple(b^columns0[0] for b in columns0));assert len(Rout)==len(Rin)==r
    bases=[columns for columns in permutations(range(1,8),3) if len(basis(columns))==3]
    outs=[M for M in bases if basis(M[:r])==Rout];ins=[M for M in bases if basis(M[:r])==Rin]
    ctable=[[tuple(F(v,1<<r) for v in tensor_c_numerator(a,b,r)) for b in range(1<<r)] for a in range(1<<r)]
    for M,N in product(outs,ins):
        amap=[a0^embed(a,M) for a in range(8)];bmap=[embed(b,N) for b in range(8)]
        if any((A[amap[a]][bmap[b]]!=ZERO)!=((a>>r)==(b>>r)) for a,b in product(range(8),repeat=2)):continue
        row=[0]*8;col=[0]*8;valid=True
        for block in range(1<<(3-r)):
            offset=block<<r
            ratios=[[div(A[amap[offset+a]][bmap[offset+b]],ctable[a][b]) for b in range(1<<r)] for a in range(1<<r)]
            if any(v not in UNITS for vals in ratios for v in vals):valid=False;break
            for b in range(1<<r):col[offset+b]=UNITS.index(ratios[0][b])
            for a in range(1<<r):row[offset+a]=UNITS.index(div(ratios[a][0],ratios[0][0]))
            if any(ratios[a][b]!=UNITS[(row[offset+a]+col[offset+b])%4] for a,b in product(range(1<<r),repeat=2)):valid=False;break
        if not valid:continue
        for gauges in product(range(4),repeat=(1<<(3-r))-1):
            shifts=(0,)+gauges;rr=[(row[a]+shifts[a>>r])%4 for a in range(8)];cc=[(col[b]-shifts[b>>r])%4 for b in range(8)]
            qout,qin=quadratic_exponents(rr),quadratic_exponents(cc)
            if qout is None or qin is None:continue
            assert all(A[amap[a]][bmap[b]]==(mul(UNITS[(rr[a]+cc[b])%4],ctable[a&((1<<r)-1)][b&((1<<r)-1)]) if a>>r==b>>r else ZERO) for a,b in product(range(8),repeat=2))
            return dict(rank=r,output_affine_offset=a0,output_columns=M,input_columns=N,
                        output_phase_exponents=rr,input_phase_exponents=cc,output_quadratic=qout,input_quadratic=qin)
    raise AssertionError('No exact paid rank interface found')


def reconstruct_edge(nf):
    r=nf['rank'];A=[[ZERO]*8 for _ in range(8)]
    for a,b in product(range(8),repeat=2):
        if a>>r!=b>>r:continue
        olda=nf['output_affine_offset']^embed(a,nf['output_columns']);oldb=embed(b,nf['input_columns'])
        c=tuple(F(v,1<<r) for v in tensor_c_numerator(a&((1<<r)-1),b&((1<<r)-1),r))
        A[olda][oldb]=mul(UNITS[(nf['output_phase_exponents'][a]+nf['input_phase_exponents'][b])%4],c)
    return A


def apply_column(A,data,positions):
    output=[ZERO]*len(data);selected=sum(1<<j for j in positions)
    for outside in range(len(data)):
        if outside&selected:continue
        for a in range(8):
            address=outside+sum(((a>>j)&1)<<positions[j] for j in range(3))
            output[address]=sum_complex(mul(A[a][b],data[outside+sum(((b>>j)&1)<<positions[j] for j in range(3))]) for b in range(8))
    return output


def apply_columns(A,data,f,chunk_width,offset):
    result=data
    for column in range(f):result=apply_column(A,result,[bank*f*chunk_width+column*chunk_width+offset for bank in range(3)])
    return result


def run(f,chunk_width,offset):
    started=perf_counter();codes=[3,23,35,56];graphs=graph_frames(3);L=(32,19,10)
    assert basis(L)==L
    costs=[sum(distance(g,graphs[c],3) for c in codes) for g in graphs]
    distances=[distance(L,graphs[c],3) for c in codes]
    assert distances==[1,1,1,2] and min(costs)==6
    assert min(sum(distance(g,graphs[c],3) for c in codes) for g in all_lagrangians(3))==5
    frames=[graph_operator(c) for c in codes];common=compose(graph_operator(3),hadamard_dyadic(2))
    assert compose(common,inverse(common))==identity(8)
    edges=[compose(common,inverse(frames[0])),compose(common,inverse(frames[1])),
           compose(frames[2],inverse(common)),compose(frames[3],inverse(common))]
    compiled=[compile_edge(edge) for edge in edges]
    assert [x['rank'] for x in compiled]==distances
    assert all(reconstruct_edge(nf)==edge for nf,edge in zip(compiled,edges))
    width=3*f*chunk_width;volume=1<<width;fields=4;checks=0;digest=sha256()
    for field in range(fields):
        x=[(F((a*7+field*11)%31-15),F((a*13+field*3)%23-11)) for a in range(volume)]
        y=[(F((a*17+field*5)%29-14),F((a*3+field*7)%19-9)) for a in range(volume)]
        ux=apply_columns(inverse(frames[0]),x,f,chunk_width,offset);uy=apply_columns(inverse(frames[1]),y,f,chunk_width,offset)
        expectedx=apply_columns(frames[2],ux,f,chunk_width,offset)
        expectedy=apply_columns(frames[3],[add(a,b) for a,b in zip(uy,ux)],f,chunk_width,offset)
        ax=apply_columns(reconstruct_edge(compiled[0]),x,f,chunk_width,offset);ay=apply_columns(reconstruct_edge(compiled[1]),y,f,chunk_width,offset)
        ay=[add(a,b) for a,b in zip(ay,ax)]
        ax=apply_columns(reconstruct_edge(compiled[2]),ax,f,chunk_width,offset);ay=apply_columns(reconstruct_edge(compiled[3]),ay,f,chunk_width,offset)
        assert (ax,ay)==(expectedx,expectedy)
        # Reverse the exact two-role gate and all frame transitions.
        backx=apply_columns(inverse(edges[2]),ax,f,chunk_width,offset);backy=apply_columns(inverse(edges[3]),ay,f,chunk_width,offset)
        backy=[add(a,neg(b)) for a,b in zip(backy,backx)]
        backx=apply_columns(inverse(edges[0]),backx,f,chunk_width,offset);backy=apply_columns(inverse(edges[1]),backy,f,chunk_width,offset)
        assert (backx,backy)==(x,y);checks +=4*volume
        digest.update(str((ax,ay)).encode())
    # Wrong outgoing common-frame assignment changes the operator.
    assert compose(frames[2],inverse(frames[0]))!=compose(edges[3],edges[0])
    return dict(status='PASS exact four-incidence dyadic gate component',input_frame_codes=codes[:2],output_frame_codes=codes[2:],
                common_lagrangian_basis=L,graph_frame_minimum_cost=6,full_lagrangian_minimum_cost=5,
                paid_transition_ranks=distances,compiled_edges=compiled,columns=f,chunk_width=chunk_width,offset=offset,
                complete_records=volume,independent_fields=fields,exact_forward_reverse_values=checks,
                output_sha256=digest.hexdigest(),elapsed_seconds=perf_counter()-started,
                scope='One virtual in-place shear with all4 phase incidences and exact reverse; adapters retained as finite affine maps; no whole motif, fixed-tape implementation or exponent')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--columns',type=int,default=1);p.add_argument('--chunk-width',type=int,default=1)
    p.add_argument('--offset',type=int,default=0);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if not 1<=a.columns<=2 or not 1<=a.chunk_width<=2 or not 0<=a.offset<a.chunk_width or 3*a.columns*a.chunk_width>9:raise ValueError('Unsupported bounded layout')
    if a.output.exists():raise FileExistsError('Use a fresh output')
    result=run(a.columns,a.chunk_width,a.offset);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='compiled_edges'}),flush=True)


if __name__=='__main__':main()
