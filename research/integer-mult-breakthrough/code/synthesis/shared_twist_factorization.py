#!/usr/bin/env python3
"""Exact shared factorization of globally summed side address twists.

The finite primitive is a bank of arbitrarily dirty payload functions on odd-
field addresses. This proves its literal permutation/CNOT word, not a native
controller ledger or integer-multiplication exponent.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

from global_incidence import identity, projector, subtract


def algebra(h):
    all_cover=(1<<h)-1
    sums=[]
    for c in range(h):
        ell=[Q(3*(h+1)*(i==c)-4) for i in range(h)]
        q=[Q(3*h-7+(h-9)*(i==c)) for i in range(h)]
        product=sum((x*y for x,y in zip(ell,q)),Q())
        if product!=-12*(h+1):
            raise ValueError('Wrong point-total complement denominator')
        k=[[q[i]*ell[j]/product for j in range(h)] for i in range(h)]
        if subtract(identity(h),projector(h,1<<c,all_cover))!=k:
            raise ValueError('Complement formula does not match high frame')
        sums.append((q,ell,k))
    count=0
    for t in combinations(range(h),3):
        w=[Q(3+(i in t)) for i in range(h)]
        z=[Q(3*(h+1)*(i in t)-10) for i in range(h)]
        if sum((a*b for a,b in zip(w,z)),Q())!=6*(h+1):
            raise ValueError('Source-line projector denominator failed')
        for c in t:
            q,ell,k=sums[c]
            if sum((a*b for a,b in zip(ell,w)),Q())!=0:
                raise ValueError('Point complement is not orthogonal to source line')
            if sum((a*b for a,b in zip(z,q)),Q())!=0:
                raise ValueError('Source line is not orthogonal to point complement')
            count+=1
    v=comb(h,3)
    return dict(h=h,triples=v,incident_twists=count,
                Kc_rank=1,Pt_rank=1,KcPt_and_PtKc_zero=True,
                factor='S(Hc)S(I-Pt)=S(Pt)S(Kc), Kc=I-Hc',
                shared_word=dict(rank1_permutation_calls=2*(h+v),ordinary_cnots=3*v,
                                 center_banks=h,target_banks=v),
                per_edge_unshared_word=dict(rank2_permutation_calls=6*v,ordinary_cnots=3*v,
                                           rank_mass=12*v),
                literal_factorized_rank_mass=2*(h+v),
                scope='Every incident rational projector identity and factor is exact; no controller endpoint absorption or all-size routing cost is assumed.')


class FieldMaps:
    def __init__(self,h,p):
        self.h,self.p,self.n=h,p,2*h
        self.I=tuple(int(i==j) for i in range(self.n) for j in range(self.n))
        self.products={}
    def mul(self,a,b):
        key=(a,b)
        if key not in self.products:
            n,p=self.n,self.p
            self.products[key]=tuple(sum(a[i*n+k]*b[k*n+j] for k in range(n))%p
                                     for i in range(n) for j in range(n))
        return self.products[key]
    def partial_swap(self,projector):
        h,p,n=self.h,self.p,self.n
        a=[[int(x.numerator%p)*pow(x.denominator%p,-1,p)%p for x in row]
           for row in projector]
        e=[[((i==j)-a[i][j])%p for j in range(h)] for i in range(h)]
        result=tuple((a if (i<h)!=(j<h) else e)[i%h][j%h]
                     for i in range(n) for j in range(n))
        if self.mul(result,result)!=self.I:
            raise ValueError('Address partial swap is not an involution')
        return result
    def apply(self,row,m):
        return {(source,self.mul(a,m)) for source,a in row}


def field_replay(h,p):
    geo=FieldMaps(h,p)
    ts=list(combinations(range(h),3));v=len(ts)
    ks=[geo.partial_swap(subtract(identity(h),projector(h,1<<c,(1<<h)-1))) for c in range(h)]
    ps=[geo.partial_swap(projector(h,sum(1<<c for c in t),sum(1<<c for c in t))) for t in ts]
    hs=[geo.partial_swap(projector(h,1<<c,(1<<h)-1)) for c in range(h)]
    fs=[geo.partial_swap(subtract(identity(h),projector(h,sum(1<<c for c in t),sum(1<<c for c in t)))) for t in ts]
    for j,t in enumerate(ts):
        for c in t:
            if geo.mul(hs[c],fs[j])!=geo.mul(ps[j],ks[c]):
                raise ValueError('Shared and unshared actual address maps differ')
    initial=[{(i,geo.I)} for i in range(h+v)]
    def run(omit=None):
        rows=[set(row) for row in initial]
        for c in range(h):rows[c]=geo.apply(rows[c],ks[c])
        for j in range(v):rows[h+j]=geo.apply(rows[h+j],ps[j])
        for j,t in enumerate(ts):
            for c in t:rows[h+j]^=rows[c]
        if omit!='target inverse':
            for j in range(v):rows[h+j]=geo.apply(rows[h+j],ps[j])
        if omit!='center inverse':
            for c in range(h):rows[c]=geo.apply(rows[c],ks[c])
        return rows
    expected=[set(row) for row in initial]
    for j,t in enumerate(ts):
        for c in t:expected[h+j].add((c,geo.mul(hs[c],fs[j])))
    actual=run()
    if actual!=expected:
        raise ValueError('Every-address dirty scatter replay failed')
    negatives=[]
    for omit in ['target inverse','center inverse']:
        rows=run(omit)
        changed=[i for i in range(h+v) if rows[i]!=expected[i]]
        if not changed:
            raise ValueError('Missing inverse was not detected')
        own_role=h if omit=='target inverse' else 0
        own_map=next(a for source,a in rows[own_role] if source==own_role)
        column=next(j for j in range(geo.n)
                    if tuple(own_map[i*geo.n+j] for i in range(geo.n))
                    !=tuple(int(i==j) for i in range(geo.n)))
        address=tuple(int(i==column) for i in range(geo.n))
        payload_address=tuple(own_map[i*geo.n+column] for i in range(geo.n))
        if payload_address==address:
            raise ValueError('Negative lacks a literal address/payload witness')
        negatives.append(dict(omitted=omit,changed_payload_rows=changed,
                              independent_symbolic_functions_reject_corruption=True,
                              exact_single_payload_counterexample=dict(
                                  physical_output_bank=own_role,output_address=address,
                                  single_nonzero_initial_bank=own_role,
                                  initial_payload_address=payload_address,
                                  expected_bit=0,corrupted_word_bit=1)))
    return dict(h=h,prime=p,all_addresses=p**(2*h),symbolic_payload_banks=h+v,
                arbitrary_payload_functions_and_dirty_banks=True,
                all_center_functions_restored=True,actual_odd_field_address_maps_exact=True,
                negative_controls=negatives,
                scope='Exact address-permutation group-algebra identity for one shared twisted-scatter batch. No source injection, finite-tape movement or recursive controller integration is included.')


def probe(spec):
    h,p=spec
    result=algebra(h)
    if p:result['finite_field_every_address_replay']=field_replay(h,p)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(__file__).with_name('global_incidence.py')]
    specs=[(6,11),(7,13),(23,None),(25,None)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),worker_processes=args.workers,
                  native_threads_each=1,specs=specs,seed=None,
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    start=time.monotonic();receipts=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();receipts.append(result)
            print(json.dumps(dict(h=result['h'],status='EXACT SHARED TWIST PRIMITIVE PASS',seconds=time.monotonic()-start)),flush=True)
    output=dict(status='EXACT SHARED TWIST PRIMITIVE PASS',cases=sorted(receipts,key=lambda x:x['h']),
                seconds=time.monotonic()-start,
                interpretation='Target-dependent and center-dependent rank-one factors can each be shared. Whether target factors telescope against already required data endpoints must be checked in a complete new physical word and cost ledger; standalone factors cannot be declared free.')
    (args.output/'certificate.json').write_text(json.dumps(output,indent=2)+'\n')


if __name__=='__main__':
    main()
