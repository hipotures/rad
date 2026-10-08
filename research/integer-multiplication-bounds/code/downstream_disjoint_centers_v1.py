#!/usr/bin/env python3
"""Two disjoint protected central gathers: scalar and native controls.

Addresses remain the original fixed odd-prime H alphabet. Payload is F2.
The new center basis changes logical coefficients and common frames; no
runtime address-coordinate basis adapter or old-table equality is claimed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import time


def mm(A, B):
    return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]


def frames(h):
    assert h >= 4 and h not in (9,10)
    I=[[Q(i==j) for j in range(h)] for i in range(h)]
    H=[[I[i][j]-Q(1,9) for j in range(h)] for i in range(h)]
    covs=[[Q(1-3*(i==0)) for i in range(h)],
          [Q(i==0) for i in range(h)]]
    zs=[[Q(6,9-h)-3*(i==0) for i in range(h)],
        [Q(i==0)+Q(1,9-h) for i in range(h)]]
    norms=[Q(36,9-h),Q(10-h,9-h)]
    ans={'0':[[Q(0)]*h for _ in range(h)],'F':I}
    for k,(z,cov,norm) in enumerate(zip(zs,covs,norms)):
        assert norm != 0 and sum(z[i]*cov[i] for i in range(h))==norm
        P=[[z[i]*cov[j]/norm for j in range(h)] for i in range(h)]
        assert mm(P,P)==P and mm(H,P)==mm([list(c) for c in zip(*P)],H)
        ans['N'+str(k)]=P
        ans['E'+str(k)]=[[I[i][j]-P[i][j] for j in range(h)] for i in range(h)]
    ts=list(combinations(range(h),3))
    for j,t in enumerate(ts):
        u=[Q(i in t) for i in range(h)]
        dual=[Q(i in t,2)-Q(1,6) for i in range(h)]
        P=[[u[i]*dual[k] for k in range(h)] for i in range(h)]
        assert sum(a*b for a,b in zip(u,dual))==1
        ans['L'+str(j)]=P
        ans['K'+str(j)]=[[I[i][k]-P[i][k] for k in range(h)] for i in range(h)]
        protected=int(0 not in t)
        assert sum(covs[protected][i]*u[i] for i in range(h))==0
    return ts,ans,H


def supports(h,ts):
    G=[{j for j,t in enumerate(ts) if 0 in t},
       {j for j,t in enumerate(ts) if 0 not in t}]
    G.extend({j for j,t in enumerate(ts) if i in t} for i in range(2,h))
    R=[{j for j,t in enumerate(ts) if 0 in t},
       {j for j,t in enumerate(ts) if 1 in t}]
    R.extend({j for j,t in enumerate(ts) if (i in t) != (1 in t)} for i in range(2,h))
    assert not G[0]&G[1] and G[0]|G[1]==set(range(len(ts)))
    assert set.union(*G[2:])==set(range(len(ts)))
    assert all(G) and all(R) and set.union(*R)==set(range(len(ts)))
    for j,s in enumerate(ts):
        for k,t in enumerate(ts):
            actual=sum((j in R[i])*(k in G[i]) for i in range(h))%2
            assert actual==len(set(s)&set(t))%2
    return G,R


def scalar(h):
    ts=list(combinations(range(h),3));v=len(ts);G,R=supports(h,ts)
    old=[[int(i in t) for t in ts] for i in range(h)]
    # Rows of T are e0, sum(j>=1)ej, e2,...; the inverse is the same
    # matrix over F2, while over Q the missing e1 row subtracts e2,... .
    T=[[int(i==j) for j in range(h)] for i in range(h)]
    T[1]=[int(j>=1) for j in range(h)]
    inv=[[int(i==j) for j in range(h)] for i in range(h)]
    inv[1]=[int(j==1)-int(j>=2) for j in range(h)]
    assert mm(T,inv)==[[Q(i==j) for j in range(h)] for i in range(h)]
    for i in range(h):
        for j in range(v):
            assert sum(T[i][k]*old[k][j] for k in range(h))%2==int(j in G[i])
            assert sum(old[k][j]*inv[k][i] for k in range(h))%2==int(j in R[i])
    w=2*v+h
    probes=[]
    for inverse in (False,True):
        values=[1<<i for i in range(w)];reference=values.copy()
        X,Y=(v,0) if inverse else (0,v)
        def gather():
            for i in range(h):
                for j in G[i]:values[2*v+i]^=values[X+j]
        def scatter():
            for i in range(h):
                for j in R[i]:values[Y+j]^=values[2*v+i]
        ops=(gather,scatter,gather,scatter) if inverse else (scatter,gather,scatter,gather)
        for op in ops:op()
        for j,s in enumerate(ts):
            for k,t in enumerate(ts):
                if len(set(s)&set(t))%2:reference[Y+j]^=reference[X+k]
        assert values==reference and values[2*v:]==[1<<i for i in range(2*v,w)]
        probes.append(dict(inverse=inverse,complete_dirty_basis=w,scalar_shear_exact=True,
                           centers_exactly_restored=True))
    return dict(h=h,triples=v,orientations=probes,basis_unimodular_over_Q=True,
                scalar_basis_has_no_address_adapter=True)


def native(h,q,D,reflected):
    assert h==4 and q==7
    ts,Ps,H=frames(h);v=len(ts);w=2*v+h;G,R=supports(h,ts)
    if reflected:
        T=[[Q(i==j)-Q(2,h) for j in range(h)] for i in range(h)]
        assert mm(T,T)==Ps['F'] and mm(mm(T,H),T)==H
        Ps={name:mm(mm(T,P),T) for name,P in Ps.items()}
    shifts={}
    for name,P in Ps.items():
        shifts[name]=tuple(sum(a.numerator*pow(a.denominator,-1,q)*d
                               for a,d in zip(row,D))%q for row in P)
    assert any(shifts['N0']) and any(shifts['N1'])
    addresses=list(product(range(q),repeat=h));size=len(addresses)
    places=[q**(h-1-i) for i in range(h)];perms={}
    def phi(values,shift):
        if not any(shift):return values
        if shift not in perms:
            perms[shift]=[sum(((a+d)%q)*p for a,d,p in zip(A,shift,places)) for A in addresses]
            assert sorted(perms[shift])==list(range(size))
        out=[0]*size
        for i,j in enumerate(perms[shift]):out[j]=values[i]
        return out
    def trans(values,old,new):
        return phi(values,tuple((a-b)%q for a,b in zip(shifts[new],shifts[old])))
    initial=[[1<<(role*size+j) for j in range(size)] for role in range(w)]
    sources=['L'+str(j) for j in range(v)]+['0']*(v+h)
    out=[]
    for inverse in (False,True):
        sinks=['F']*v+(['K'+str(j) for j in range(v)] if inverse else ['0']*v)+['F']*h
        def execute(protected,wrong=False):
            values=initial.copy();labels=sources.copy();omitted=False
            X,Y=(v,0) if inverse else (0,v)
            if inverse:
                gs=[(list(range(2,h)),'0'),([1],'N1'),([0],'N0')]
                ops=[('G',list(range(h)),'0'),('R',list(range(h)),'F')]
                ops += [('G',ind,label) for ind,label in gs] if protected else [('G',list(range(h)),'0')]
                ops += [('R',list(range(h)),'F')]
            else:
                gs=[([0],'E0'),([1],'E1'),(list(range(2,h)),'F')]
                ops=[('R',list(range(h)),'0')]
                ops += [('G',ind,label) for ind,label in gs] if protected else [('G',list(range(h)),'F')]
                ops += [('R',list(range(h)),'0'),('G',list(range(h)),'F')]
            for kind,inds,label in ops:
                support=G if kind=='G' else R;bank=X if kind=='G' else Y
                data=sorted(set.union(*(support[i] for i in inds)))
                touched=[bank+j for j in data]+[2*v+i for i in inds]
                for role in touched:
                    if wrong and not omitted and label in ('E1','N1') and role==2*v+1:
                        omitted=True
                    else:values[role]=trans(values[role],labels[role],label)
                    labels[role]=label
                for i in inds:
                    for j in support[i]:
                        target,source=(2*v+i,bank+j) if kind=='G' else (bank+j,2*v+i)
                        values[target]=[a^b for a,b in zip(values[target],values[source])]
            for role,label in enumerate(sinks):values[role]=trans(values[role],labels[role],label)
            assert not wrong or omitted
            return values
        plain=[phi(A,tuple(-d%q for d in shifts[name])) for A,name in zip(initial,sources)]
        X,Y=(v,0) if inverse else (0,v)
        for j,s in enumerate(ts):
            for k,t in enumerate(ts):
                if len(set(s)&set(t))%2:plain[Y+j]=[a^b for a,b in zip(plain[Y+j],plain[X+k])]
        expected=[phi(A,shifts[name]) for A,name in zip(plain,sinks)]
        baseline=execute(False);new=execute(True);wrong=execute(True,True)
        assert baseline==new==expected
        failure=sum(a!=b for A,B in zip(wrong,new) for a,b in zip(A,B));assert failure>0
        out.append(dict(inverse=inverse,complete_native_dirty_basis=w*size,
                        old_full_vs_two_protected_operator_exact=True,
                        boundary_gauge_scalar_operator_exact=True,
                        omitted_second_protected_chart_discriminating_coordinates=failure))
    return dict(h=h,q=q,D=D,ambient_reflection=reflected,H_addresses=size,
                orientations=out,normal_shifts_nonzero=True,
                finite_address_alphabet_unchanged=True,payload_alphabet='F2')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();t=time.monotonic()
    rational=[]
    for h in (4,6,8,12):
        ts,Ps,H=frames(h)
        rational.append(dict(h=h,triples=len(ts),two_exact_nonzero_normal_projectors=True))
    scalar_rows=[scalar(h) for h in (4,6,8,12)]
    native_rows=[native(4,7,D,refl) for D in ((1,0,2,4),(2,1,3,5)) for refl in (False,True)]
    result=dict(status='PASS EXACT TWO DISJOINT PROTECTED CENTERS; FULL ALL-SIZE REVIEW REQUIRED',
                generated_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                rational_projector_controls=rational,scalar_controls=scalar_rows,native_controls=native_rows,
                complete_native_probes=sum(r['complete_native_dirty_basis'] for row in native_rows for r in row['orientations']),
                mechanism='Gprime=T Inc, Rprime=Inc^T T^-1 over F2; two disjoint supports',
                bit_rank_budget=dict(W_unchanged=True,L='3*v^2*(h^2-2)',D='N-2L',s='W*m-D'),
                credited_generic_families_unchanged=True,
                new_fixed_bit_table_and_shared_prime_required=True,
                complex_numeric_guard_unchanged=True,
                scope='Complete changed central segments, two fixed nonzero D fibers, two ambient charts, both physical orientations. Full side graph inherited from accepted input; not replayed. h>=4,h!=9,10; no complex/alternating extension claimed.',
                wall_seconds=time.monotonic()-t)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],result['complete_native_probes'],result['wall_seconds'],flush=True)


if __name__=='__main__':main()
