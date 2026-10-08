#!/usr/bin/env python3
"""Native odd-prime address-fiber replay of the protected central segment.

Every scalar data/center basis on two complete H-address fibers is packed
into integer bits. D is unchanged by address shears. No old side circuit is
replayed; old/new central segment boundaries are identical.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys
import time


def eye(n):
    return [[Q(int(i==j)) for j in range(n)] for i in range(n)]


def multiply(A,B):
    return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]


def subtract(A,B):
    return [[a-b for a,b in zip(row,col)] for row,col in zip(A,B)]


def scale(A,c):
    return [[c*x for x in row] for row in A]


def matrix_field(A,q):
    return [[x.numerator*pow(x.denominator,-1,q)%q for x in row] for row in A]


def projector_frames(h):
    I=eye(h);zero=scale(I,0)
    H=[[Q(int(i==j))-Q(1,9) for j in range(h)] for i in range(h)]
    n=[Q(1-3*int(i==0)) for i in range(h)]
    z=[Q(6,9-h)-3*int(i==0) for i in range(h)]
    norm=Q(36,9-h)
    normal=[[z[i]*n[j]/norm for j in range(h)] for i in range(h)]
    frames={'0':zero,'F':I,'normal':normal,'star':subtract(I,normal)}
    triples=list(combinations(range(h),3))
    for index,t in enumerate(triples):
        u=[Q(int(i in t)) for i in range(h)]
        dual=[Q(int(i in t),2)-Q(1,6) for i in range(h)]
        P=[[u[i]*dual[j] for j in range(h)] for i in range(h)]
        assert multiply(P,P)==P
        frames['line'+str(index)]=P
        frames['kernel'+str(index)]=subtract(I,P)
    assert multiply(normal,normal)==normal
    assert multiply(H,normal)==multiply([list(x) for x in zip(*normal)],H)
    return triples,frames,H


def native_case(h,q,D,reflected):
    triples,frames,H=projector_frames(h);v=len(triples);w=2*v+h
    assert h==4 and q==7 and len(D)==h
    if reflected:
        T=[[Q(int(i==j))-Q(2,h) for j in range(h)] for i in range(h)]
        assert multiply(T,T)==eye(h)
        assert multiply(multiply(T,H),T)==H
        frames={name:multiply(multiply(T,A),T) for name,A in frames.items()}
    field={name:matrix_field(A,q) for name,A in frames.items()}
    shifts={name:tuple(sum(a*b for a,b in zip(row,D))%q for row in A) for name,A in field.items()}
    assert shifts['normal']!=(0,)*h
    addresses=list(product(range(q),repeat=h));length=len(addresses)
    place=[q**(h-1-i) for i in range(h)]
    cache={}
    def permutation(shift):
        if shift not in cache:
            cache[shift]=[sum(((a+s)%q)*p for a,s,p in zip(H0,shift,place)) for H0 in addresses]
            assert sorted(cache[shift])==list(range(length))
        return cache[shift]
    def apply_phi(values,shift):
        if not any(shift):
            return values
        answer=[0]*length
        for i,j in enumerate(permutation(shift)):
            answer[j]=values[i]
        return answer
    def transition(values,old,new):
        return apply_phi(values,tuple((a-b)%q for a,b in zip(shifts[new],shifts[old])))
    def xor_into(values,target,source):
        values[target]=[x^y for x,y in zip(values[target],values[source])]
    stars=[[j for j,t in enumerate(triples) if i in t] for i in range(h)]
    source_names=['line'+str(j) for j in range(v)]+['0']*(v+h)
    source_basis=[[1<<(role*length+j) for j in range(length)] for role in range(w)]
    results=[]
    for inverse in (False,True):
        sinks=(['F']*v+['kernel'+str(j) for j in range(v)]+['F']*h
               if inverse else ['F']*v+['0']*v+['F']*h)
        def operations(protected):
            if not inverse:
                middle=([('gather',[0],'star',0),('gather',list(range(1,h)),'F',0)]
                        if protected else [('gather',list(range(h)),'F',0)])
                return [('scatter',list(range(h)),'0',v)]+middle+[
                    ('scatter',list(range(h)),'0',v),('gather',list(range(h)),'F',0)]
            middle=([('gather',list(range(1,h)),'0',v),('gather',[0],'normal',v)]
                    if protected else [('gather',list(range(h)),'0',v)])
            return [('gather',list(range(h)),'0',v),('scatter',list(range(h)),'F',0)]+middle+[
                ('scatter',list(range(h)),'F',0)]
        def execute(protected,wrong=False):
            values=source_basis.copy();current=source_names.copy()
            omitted=False
            for kind,indices,frame,bank in operations(protected):
                data=sorted(set(j for i in indices for j in stars[i]))
                touched=[bank+j for j in data]+[2*v+i for i in indices]
                for role in touched:
                    if wrong and protected and not omitted and frame in ('star','normal') and role==2*v:
                        omitted=True
                    else:
                        values[role]=transition(values[role],current[role],frame)
                    current[role]=frame
                if kind=='gather':
                    for i in indices:
                        for j in stars[i]:
                            xor_into(values,2*v+i,bank+j)
                else:
                    for j,t in enumerate(triples):
                        for i in t:
                            xor_into(values,bank+j,2*v+i)
            for role,target in enumerate(sinks):
                values[role]=transition(values[role],current[role],target)
            assert not wrong or omitted
            return values
        old=execute(False);new=execute(True);wrong=execute(True,True)
        # Independent boundary gauge: strip starting frames, execute the
        # scalar central RG shear directly, then apply ending frames.
        plain=[]
        for values,name in zip(source_basis,source_names):
            plain.append(apply_phi(values,tuple(-a%q for a in shifts[name])))
        sources=plain[v:2*v] if inverse else plain[:v]
        for j,s in enumerate(triples):
            role=j if inverse else v+j
            for k,t in enumerate(triples):
                if len(set(s).intersection(t))%2:
                    plain[role]=[a^b for a,b in zip(plain[role],sources[k])]
        expected=[apply_phi(values,shifts[name]) for values,name in zip(plain,sinks)]
        assert old==new==expected
        failures=sum(a!=b for A,B in zip(wrong,new) for a,b in zip(A,B))
        assert failures>0
        digest=sha256()
        for values in new:
            for a in values:
                digest.update(a.to_bytes((w*length+7)//8,'little'))
        results.append(dict(inverse_physical_order=inverse,complete_basis_probes=w*length,
            complete_output_coordinates=w*length,all_centers_arbitrarily_dirty=True,
            old_vs_new_native_segment_exact=True,boundary_gauge_rg_identity_exact=True,
            omitted_protected_center_entry_discriminating_coordinates=failures,
            output_sha256=digest.hexdigest()))
    return dict(h=h,q=q,D_fiber=D,all_H_addresses=length,logical_data_and_center_roles=w,
                reflected_metric_basis=reflected,metric_nonzero_mod_q=True,
                native_common_frame_projectors_exact=True,orientations=results,
                cached_address_shift_permutations=len(cache))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();start=time.monotonic()
    cases=[native_case(4,7,D,reflected) for D in ((1,0,2,4),(2,1,3,5)) for reflected in (False,True)]
    result=dict(status='PASS',timestamp=datetime.now(timezone.utc).isoformat(),python=sys.version,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),cases=cases,
        complete_native_basis_probes=sum(x['complete_basis_probes'] for c in cases for x in c['orientations']),
        selected_D_fibers=2,all_D_addresses_exhausted=False,
        actual_changed_central_segments_only=True,old_side_baseline_replayed=False,
        wall_seconds=time.monotonic()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],complete_basis_probes=result['complete_native_basis_probes'],
                         seconds=result['wall_seconds'])))


if __name__=='__main__':
    main()
