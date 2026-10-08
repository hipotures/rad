#!/usr/bin/env python3
"""Literal three-helper component through a degenerate Clifford frame.

All phase anchors, retired-role edges and source/target transitions are
explicit. Each actual phase edge is reconstructed with one C tensor of
its mixing rank, unit chirps and retained affine routing. This finite
component is not a whole multiplication motif or a fixed-tape compiler.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from time import perf_counter

from degenerate_frame_geodesics import lagrangian,perpendicular
from lagrangian_phase_screen import basis,distance
from lagrangian_gate_witness import (ZERO,ONE,UNITS,add,neg,mul,div,compose,
    inverse,identity,embed,sum_complex,quadratic_exponents)
from quadratic_rank_interface import tensor_c_numerator


N=4
SIZE=1<<N


def c_line(t):
    assert t.bit_count()%2
    a=(Q(1,2),Q(1,2));b=(Q(1,2),Q(-1,2))
    return [[a if x==y else b if x==y^t else ZERO for y in range(SIZE)] for x in range(SIZE)]


def full_c():
    return [[tuple(Q(z,1<<N) for z in tensor_c_numerator(x,y,N))
             for y in range(SIZE)] for x in range(SIZE)]


def hadamard_dyadic(bit):
    mask=1<<bit;v=(Q(1,2),Q(1,2))
    return [[(neg(v) if x&mask and y&mask else v) if x&~mask==y&~mask else ZERO
             for y in range(SIZE)] for x in range(SIZE)]


def permutation(function):
    values=[function(x) for x in range(SIZE)]
    assert sorted(values)==list(range(SIZE))
    return [[ONE if x==values[y] else ZERO for y in range(SIZE)] for x in range(SIZE)]


def common_frame(reverse=False):
    routing=permutation(lambda x:x^(4 if x&2 else 0))
    F=compose(c_line(1),compose(hadamard_dyadic(1),routing))
    if reverse:
        swap=permutation(lambda x:(x&6)|((x&1)<<3)|((x&8)>>3))
        F=compose(swap,compose(F,swap))
    return F


def pauli_z_images(F):
    result=[]
    for bit in range(N):
        Z=[[UNITS[2] if x==y and x>>bit&1 else ONE if x==y else ZERO
            for y in range(SIZE)] for x in range(SIZE)]
        image=compose(inverse(F),compose(Z,F))
        active=[x for x in range(SIZE) if image[x][0]!=ZERO]
        assert len(active)==1
        xmask=active[0];phase=UNITS.index(image[xmask][0]);zmask=0
        for j in range(N):
            if image[xmask^(1<<j)][1<<j]!=UNITS[phase]:zmask |=1<<j
        assert all(image[x][y]==(UNITS[(phase+2*((zmask&y).bit_count()%2))%4]
                                if x==y^xmask else ZERO)
                   for x,y in product(range(SIZE),repeat=2))
        result.append(dict(label=zmask|(xmask<<N),phase=phase))
    return result


def complete_basis(columns):
    columns=list(columns)
    for j in range(N):
        if len(basis(tuple(columns)+(1<<j,)))>len(columns):columns.append(1<<j)
    assert len(columns)==N
    return columns


def compile_edge(A):
    """Recover a literal rank normal form from the exact coefficient matrix."""
    support=[a for a in range(SIZE) if A[a][0]!=ZERO];a0=min(support)
    r=(len(support)-1).bit_length();assert len(support)==1<<r
    Rout=basis(tuple(a^a0 for a in support))
    rowsupport=[b for b in range(SIZE) if A[a0][b]!=ZERO]
    Rin=basis(tuple(b^rowsupport[0] for b in rowsupport))
    assert len(Rout)==len(Rin)==r
    inputs=complete_basis(Rin);outputs=list(Rout)
    for j in range(r,N):
        column_support=[a for a in range(SIZE) if A[a][inputs[j]]!=ZERO]
        outputs.append(min(column_support)^a0)
    assert len(basis(tuple(outputs)))==N
    # The active bilinear coupling is invertible; absorb its inverse into
    # input routing rather than charging a second Hadamard/C child.
    coupling=[]
    for j in range(r):
        row=0
        for k in range(r):
            ratio=div(mul(A[a0^outputs[j]][inputs[k]],A[a0][0]),
                      mul(A[a0^outputs[j]][0],A[a0][inputs[k]]))
            assert ratio in (UNITS[0],UNITS[2])
            row |= (UNITS.index(ratio)//2)<<k
        coupling.append(row)
    inverse_columns=[]
    for j in range(r):
        solutions=[x for x in range(1<<r)
                   if sum(((row&x).bit_count()%2)<<k for k,row in enumerate(coupling))==1<<j]
        assert len(solutions)==1
        inverse_columns.append(solutions[0])
    inputs=[embed(x,inputs[:r]) for x in inverse_columns]+inputs[r:]
    amap=[a0^embed(a,outputs) for a in range(SIZE)];bmap=[embed(b,inputs) for b in range(SIZE)]
    assert all((A[amap[a]][bmap[b]]!=ZERO)==(a>>r==b>>r)
               for a,b in product(range(SIZE),repeat=2))
    table=[[tuple(Q(z,1<<r) for z in tensor_c_numerator(a,b,r))
            for b in range(1<<r)] for a in range(1<<r)]
    row=[0]*SIZE;col=[0]*SIZE
    for block in range(1<<(N-r)):
        offset=block<<r
        ratios=[[div(A[amap[offset+a]][bmap[offset+b]],table[a][b])
                 for b in range(1<<r)] for a in range(1<<r)]
        assert all(z in UNITS for line in ratios for z in line)
        for b in range(1<<r):col[offset+b]=UNITS.index(ratios[0][b])
        for a in range(1<<r):row[offset+a]=UNITS.index(div(ratios[a][0],ratios[0][0]))
        assert all(ratios[a][b]==UNITS[(row[offset+a]+col[offset+b])%4]
                   for a,b in product(range(1<<r),repeat=2))
    for gauges in product(range(4),repeat=(1<<(N-r))-1):
        shifts=(0,)+gauges
        rr=[(row[a]+shifts[a>>r])%4 for a in range(SIZE)]
        cc=[(col[b]-shifts[b>>r])%4 for b in range(SIZE)]
        qout,qin=quadratic_exponents(rr),quadratic_exponents(cc)
        if qout is None or qin is None:continue
        nf=dict(rank=r,output_affine_offset=a0,output_columns=outputs,input_columns=inputs,
                output_phase_exponents=rr,input_phase_exponents=cc,
                output_quadratic=qout,input_quadratic=qin)
        assert reconstruct_edge(nf)==A
        return nf
    raise AssertionError('No global quadratic gauge found')


def reconstruct_edge(nf):
    r=nf['rank'];mask=(1<<r)-1;A=[[ZERO]*SIZE for _ in range(SIZE)]
    for a,b in product(range(SIZE),repeat=2):
        if a>>r!=b>>r:continue
        olda=nf['output_affine_offset']^embed(a,nf['output_columns']);oldb=embed(b,nf['input_columns'])
        c=tuple(Q(v,1<<r) for v in tensor_c_numerator(a&mask,b&mask,r))
        A[olda][oldb]=mul(UNITS[(nf['output_phase_exponents'][a]+nf['input_phase_exponents'][b])%4],c)
    return A


def schedule(reverse=False,injection_sign=1):
    t=(8,14) if reverse else (1,7);s=(1,7) if reverse else (8,14)
    full=full_c();common=common_frame(reverse);I=identity(SIZE)
    lines=[c_line(v) for v in t]
    kernels=[compose(full,inverse(c_line(v))) for v in s]
    frame=dict(x0=lines[0],x1=lines[1],y0=I,y1=I,a=I,b=I,p=I)
    initial=dict(frame);events=[]
    labels=dict(zero=lagrangian((),N),full=lagrangian((1,2,4,8),N),
                common=lagrangian(basis(t),N))
    for j,v in enumerate(t):labels['line'+str(j)]=lagrangian((v,),N)
    for j,v in enumerate(s):labels['kernel'+str(j)]=lagrangian(perpendicular((v,),N),N)
    current=dict(x0='line0',x1='line1',y0='zero',y1='zero',a='zero',b='zero',p='zero')
    edges=[]
    def move(role,name,F):
        old=current[role];E=compose(F,inverse(frame[role]));nf=compile_edge(E)
        assert nf['rank']==distance(labels[old],labels[name],N)
        edges.append(dict(role=role,before=old,after=name,normal_form=nf,
                          auxiliary=role in ('a','b','p')))
        events.append(('move',role,len(edges)-1));frame[role]=F;current[role]=name
    def shear(dest,source,sign):
        assert frame[dest]==frame[source]
        events.append(('shear',dest,source,sign))
    # Early dirty echo, in the common zero frame.
    shear('a','b',1);shear('p','a',1)
    shear('y0','a',-injection_sign);shear('y1','p',-injection_sign)
    shear('p','a',-1);shear('a','b',-1)
    move('a','line0',lines[0]);move('b','line1',lines[1])
    shear('a','x0',1);shear('b','x1',1)
    move('a','common',common);move('b','common',common);shear('a','b',1)
    move('b','full',full)  # Second incoming role is explicitly retired.
    move('p','common',common);shear('p','a',1)
    move('a','kernel0',kernels[0]);move('y0','kernel0',kernels[0]);shear('y0','a',injection_sign)
    move('p','kernel1',kernels[1]);move('y1','kernel1',kernels[1]);shear('y1','p',injection_sign)
    move('a','full',full);move('p','full',full)
    shear('p','a',-1);shear('a','b',-1)
    move('x0','full',full);move('x1','full',full)
    shear('a','x0',-1);shear('b','x1',-1)
    assert sum(e['normal_form']['rank'] for e in edges if e['auxiliary'])==12
    assert sum(e['normal_form']['rank'] for e in edges if not e['auxiliary'])==12
    images=pauli_z_images(common)
    assert basis(tuple(i['label'] for i in images))==labels['common']
    return dict(events=events,edges=edges,initial_frames=initial,final_frames=frame,
                pauli_z_images=images,source_directions=t,target_directions=s,
                injection_sign=injection_sign,common_lagrangian=labels['common'])


def apply_column(A,data,positions):
    output=[ZERO]*len(data);selected=sum(1<<j for j in positions)
    for outside in range(len(data)):
        if outside&selected:continue
        addresses=[outside+sum(((a>>j)&1)<<positions[j] for j in range(N)) for a in range(SIZE)]
        for a,address in enumerate(addresses):
            output[address]=sum_complex(mul(A[a][b],data[other]) for b,other in enumerate(addresses) if A[a][b]!=ZERO)
    return output


def apply_columns(A,data,f,width,offset):
    for column in range(f):data=apply_column(A,data,[bank*f*width+column*width+offset for bank in range(N)])
    return data


def execute(spec,data,f,width,offset,undo=False):
    data={key:list(values) for key,values in data.items()}
    for event in reversed(spec['events']) if undo else spec['events']:
        if event[0]=='move':
            _,role,index=event;A=reconstruct_edge(spec['edges'][index]['normal_form'])
            if undo:A=inverse(A)
            data[role]=apply_columns(A,data[role],f,width,offset)
        else:
            _,dest,source,sign=event
            if undo:sign=-sign
            data[dest]=[add(a,b if sign==1 else neg(b)) for a,b in zip(data[dest],data[source])]
    return data


def run(f,width,offset,reverse):
    started=perf_counter();spec=schedule(reverse,-1 if reverse else 1)
    volume=1<<(N*f*width);fields=4;checks=0;digest=sha256()
    for field in range(fields):
        initial={role:[(Q((address*7+j*11+field*3)%31-15),Q((address*13+j*5+field*17)%29-14))
                       for address in range(volume)] for j,role in enumerate(spec['initial_frames'])}
        virtual={role:apply_columns(inverse(spec['initial_frames'][role]),values,f,width,offset)
                 for role,values in initial.items()}
        for role in ('y0','y1'):
            virtual[role]=[add(y,mul((Q(spec['injection_sign']),Q(0)),add(a,b)))
                           for y,a,b in zip(virtual[role],virtual['x0'],virtual['x1'])]
        expected={role:apply_columns(spec['final_frames'][role],values,f,width,offset)
                  for role,values in virtual.items()}
        observed=execute(spec,initial,f,width,offset)
        assert observed==expected
        assert execute(spec,observed,f,width,offset,True)==initial
        checks +=2*len(initial)*volume
        digest.update(str(observed).encode())
    # Removing retirement changes the actual common-frame scalar cleanup.
    bad=dict(spec);bad['events']=[event for event in spec['events']
                                 if not (event[0]=='move' and spec['edges'][event[2]]['role']=='b'
                                         and spec['edges'][event[2]]['after']=='full')]
    assert execute(bad,initial,f,width,offset)!=expected
    # Complementary degenerate frames are not a claimed product factorization.
    assert compose(common_frame(False),common_frame(True))!=full_c()
    return dict(status='PASS literal degenerate-frame branching component',
                orientation='complementary negative shear' if reverse else 'forward positive shear',
                source_directions=spec['source_directions'],target_directions=spec['target_directions'],
                common_lagrangian=spec['common_lagrangian'],actual_pauli_z_images=spec['pauli_z_images'],
                auxiliary_rank=12,external_data_rank=12,auxiliary_endpoint_capacity=12,
                edges=spec['edges'],events=spec['events'],columns=f,chunk_width=width,offset=offset,
                independent_fields=fields,complete_records=volume,exact_forward_and_undo_values=checks,
                result_sha256=digest.hexdigest(),negative_controls=['Omitting retired b full-frame edge changes dirty cleanup',
                'Complementary common-frame product differs from full C anchor'],
                elapsed_seconds=perf_counter()-started,
                scope='Exact finite complete physical payloads, one child per actual edge, all dirty phase anchors restored; no fixed-tape cost, whole motif, child characteristic or exponent')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--columns',type=int,default=1)
    p.add_argument('--chunk-width',type=int,default=1);p.add_argument('--offset',type=int,default=0)
    p.add_argument('--reverse',action='store_true');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if not 1<=a.columns<=2 or not 1<=a.chunk_width<=2 or not 0<=a.offset<a.chunk_width or N*a.columns*a.chunk_width>8:raise ValueError('Unsupported bounded layout')
    if a.output.exists():raise FileExistsError('Use a fresh output')
    result=run(a.columns,a.chunk_width,a.offset,a.reverse)
    result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('edges','events')}),flush=True)


if __name__=='__main__':main()
