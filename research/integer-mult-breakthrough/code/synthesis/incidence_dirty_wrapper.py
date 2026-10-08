#!/usr/bin/env python3
"""Exact incidence-basis dirty wrapper and an optimistic chronology bound.

This is a new, explicit finite controller with paid address permutations.
Its same-width self calls are allowed and counted. The favorable ledger
fails even before its real gather/scatter costs are included; this is a
negative for this source/target chronology, not for wider synthesis.
"""
import argparse
from collections import Counter
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
from shared_twist_factorization import FieldMaps


def lower_bound(h):
    """Grant every gather and shared scatter transition zero cost."""
    v = comb(h, 3)
    w = 4*v+h
    optimistic = {1: 3*v+h, h-1: 3*v+h, h: v}
    actual = {1: 7*v+5*h, h-2: 6*v, h-1: 3*v+h, h: v}
    mass = sum(r*n for r,n in optimistic.items())
    if mass != w*h or sum(r*n for r,n in actual.items()) != w*h+4*(v+h)+6*v*(h-2):
        raise ValueError('Rank ledger does not match literal/favorable chronology')
    tests=[]
    for a in (Q(1,9999),Q(1,999)):
        # ln(h/r) >= 2(h-r)/(h+r), exp(a ln(h/r)) >= 1+a ln(h/r).
        excess = a*sum((Q(n*r)*2*(h-r)/(h+r) for r,n in optimistic.items()),Q())/(w*h)
        if excess <= 0:
            raise ValueError('Favorable positive-saving moment was not rejected')
        tests.append(dict(saving=str(a),moment_strict_lower_bound=str(1+excess),
                          strict_excess_lower_bound=str(excess)))
    return dict(h=h,v=v,payload_roles=w,optimistic_histogram=optimistic,
                literal_histogram=actual,optimistic_total_rank=mass,capacity=w*h,
                same_width_calls=v,same_width_stock_ratio=str(Q(v,w)),
                same_width_calls_are_depth_admissible=Q(v,w)<1,
                positive_saving_tests=tests,
                scope='Fixed explicit incidence-wrapper chronology with standard complementary source/sink boundary frames. Every real center gather/scatter transition is optimistically deleted. Full-width self calls are permitted, not forbidden; zero rank deficit still rules out every positive saving in this local moment.')


def field_rank(flat,n,p):
    rows=[list(flat[i*n:(i+1)*n]) for i in range(n)]
    r=0
    for col in range(n):
        pivot=next((i for i in range(r,n) if rows[i][col]),None)
        if pivot is None:continue
        rows[r],rows[pivot]=rows[pivot],rows[r]
        scale=pow(rows[r][col],-1,p)
        rows[r]=[(a*scale)%p for a in rows[r]]
        for i in range(r+1,n):
            scale=rows[i][col]
            rows[i]=[(a-scale*b)%p for a,b in zip(rows[i],rows[r])]
        r+=1
    return r


def finite_word(h,p,negative=None,transposed=False):
    geo=FieldMaps(h,p)
    ts=list(combinations(range(h),3));v=len(ts);w=4*v+h
    x=list(range(v));y=list(range(v,2*v));u=list(range(2*v,3*v))
    s=list(range(3*v,4*v));t=list(range(4*v,w));aux=u+s+t
    zero=[[Q() for _ in range(h)] for _ in range(h)];full=identity(h)
    pt=[projector(h,sum(1<<c for c in T),sum(1<<c for c in T)) for T in ts]
    ft=[subtract(full,a) for a in pt]
    hc=[projector(h,1<<c,(1<<h)-1) for c in range(h)]
    frame=[zero for _ in range(w)]
    for j in range(v):frame[x[j]]=pt[j]
    initial=[{(i,geo.I)} for i in range(w)];rows=[set(r) for r in initial]
    events=[];ranks=Counter();rank_cache={};frame_failures=[]
    def freeze(a):return tuple(tuple(row) for row in a)
    def cnot(dest,source):
        if frame[dest]!=frame[source]:
            frame_failures.append((dest,source))
            if negative is None:raise ValueError('CNOT lacks an actual common frame')
        rows[dest]^=rows[source]
        events.append(('cnot',dest,source,None))
    def move(role,new,rank):
        old=frame[role]
        key=(freeze(old),freeze(new))
        if key not in rank_cache:
            before=geo.partial_swap(old);after=geo.partial_swap(new)
            a=geo.mul(before,after)
            if geo.mul(a,a)!=geo.I:
                raise ValueError('Claimed partial swap is not an involution')
            difference=tuple((z-int(i==j))%p for i in range(geo.n)
                             for j,z in enumerate(a[i*geo.n:(i+1)*geo.n]))
            measured=field_rank(difference,geo.n,p)
            rank_cache[key]=(a,measured)
        a,measured=rank_cache[key]
        if measured!=rank:raise ValueError('Address-map rank differs from charged rank')
        rows[role]=geo.apply(rows[role],a);frame[role]=new;ranks[rank]+=1
        events.append(('permute',role,None,a))
    def scalar_mixer(reverse=False):
        edges=[(t[c],u[j]) for j,T in enumerate(ts) for c in T]
        edges +=[(s[j],t[c]) for j,T in enumerate(ts) for c in T]
        edges +=list(zip(s,u))
        for dest,source in reversed(edges) if reverse else edges:cnot(dest,source)
    def scalar_scatter():
        for j,T in enumerate(ts):
            cnot(y[j],s[j])
            for c in T:cnot(y[j],t[c])
    def shared_scatter(targets):
        # Hc -> full and Ft -> full, scalar CNOTs, then restore both frames.
        for c in range(h):move(t[c],full,1)
        for j in range(v):move(targets[j],full,1)
        for j,T in enumerate(ts):
            for c in T:cnot(targets[j],t[c])
        for j in range(v):move(targets[j],ft[j],1)
        for c in range(h):move(t[c],hc[c],1)

    # Zero-frame dirty echo. Its scalar source/output map is exactly I:
    # M: t=Bu, s=B^T t+u. J: y=s+B^T t.
    scalar_mixer();scalar_scatter();scalar_mixer(True)
    for j in range(v):move(u[j],pt[j],1)
    for j in range(v):move(s[j],ft[j],h-1)
    for c in range(h):move(t[c],hc[c],h-1)
    for j in range(v):cnot(u[j],x[j])
    for j,T in enumerate(ts):
        for c in T:
            move(u[j],hc[c],h-2);cnot(t[c],u[j]);move(u[j],pt[j],h-2)
    shared_scatter(s)
    # The I term requires complementary Pt -> Ft, a width-h partial swap.
    # Keep it applied and absorb its inverse into the final auxiliary cleanup.
    for j in range(v):
        if negative!='erase self transport':move(u[j],ft[j],h)
        cnot(s[j],u[j])
    for j in range(v):move(y[j],ft[j],h-1);cnot(y[j],s[j])
    shared_scatter(y)
    for j in range(v):
        if negative=='use obsolete primary cleanup':
            # Actual wrong literal map S(Ft), retained as a matched corruption.
            a=geo.partial_swap(ft[j]);rows[u[j]]=geo.apply(rows[u[j]],a)
            events.append(('permute',u[j],None,a));frame[u[j]]=full
        else:move(u[j],full,1 if negative!='erase self transport' else h-1)
    for j in range(v):move(s[j],full,1)
    for c in range(h):move(t[c],full,1)
    scalar_mixer(True)
    for j in range(v):move(x[j],full,h-1);cnot(u[j],x[j])
    if negative is None:
        if dict(ranks)!=lower_bound(h)['literal_histogram']:
            raise ValueError('Literal event histogram differs from derived ledger')
        if any(frame[a]!=full for a in x+aux) or any(frame[y[j]]!=ft[j] for j in range(v)):
            raise ValueError('Source/sink/auxiliary boundary frame mismatch')
    if transposed:
        rows=[set(r) for r in initial]
        for kind,dest,source,a in reversed(events):
            if kind=='permute':rows[dest]=geo.apply(rows[dest],a)
            else:rows[source]^=rows[dest]
    expected=[{(i,geo.partial_swap(full))} if i in aux else None for i in range(w)]
    for j in range(v):
        f=geo.partial_swap(ft[j]);g=geo.partial_swap(full)
        if transposed:
            expected[x[j]]={(x[j],f),(y[j],g)};expected[y[j]]={(y[j],f)}
        else:
            expected[x[j]]={(x[j],f)};expected[y[j]]={(y[j],f),(x[j],g)}
    failures=[i for i in range(w) if rows[i]!=expected[i]]
    witness=None
    if failures:
        for role in failures:
            for column in range(geo.n):
                address=tuple(int(i==column) for i in range(geo.n));active=set()
                for source,a in rows[role]^expected[role]:
                    term=(source,tuple(a[i*geo.n+column] for i in range(geo.n)))
                    if term in active:active.remove(term)
                    else:active.add(term)
                if active:
                    source,payload=sorted(active)[0]
                    def bit(row):
                        return sum(source==bank and tuple(a[i*geo.n+column] for i in range(geo.n))==payload
                                   for bank,a in row)%2
                    witness=dict(physical_output_bank=role,output_address=address,
                                 single_nonzero_initial_bank=source,initial_payload_address=payload,
                                 expected_bit=bit(expected[role]),corrupted_bit=bit(rows[role]))
                    break
            if witness:break
        if witness is None:raise ValueError('No literal one-payload negative witness found')
    if negative is None and failures:raise ValueError('Full dirty wrapper failed exact payload replay')
    if negative is not None and not failures:raise ValueError('Matched corruption was not rejected')
    return dict(h=h,prime=p,payload_roles=w,auxiliary_banks=len(aux),all_addresses=p**(2*h),
                orientation='literal reverse and transpose' if transposed else 'forward',
                source_columns=v,sink_columns=v,arbitrary_dirty_columns=len(aux),
                negative=negative,differing_payload_rows=failures,counterexample=witness,
                common_frame_cnot_failures=frame_failures,
                permutation_histogram=dict(sorted(ranks.items())),ordinary_cnots=sum(e[0]=='cnot' for e in events),
                every_address_and_arbitrary_payload_functions_exact=negative is None,
                scope='Exact literal common-frame CNOT/partial-address-swap word over this finite odd field. The explicit fixed chronology has a noncontracting favorable rank ledger; no all-size tape transfer or larger kappa is claimed.')


def probe(spec):
    h,p=spec
    return dict(h=h,prime=p,cases=[finite_word(h,p,negative,transposed)
                for transposed in (False,True)
                for negative in (None,'erase self transport','use obsolete primary cleanup')])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',required=True,type=Path);ap.add_argument('--workers',type=int,default=4)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(__file__).with_name('shared_twist_factorization.py'),Path(__file__).with_name('global_incidence.py')]
    specs=[(5,7),(5,11),(6,11),(7,13)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
                  native_threads_each=1,seed=None,specs=specs,
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    start=time.monotonic();receipts=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();receipts.append(result)
            print(json.dumps(dict(h=result['h'],prime=result['prime'],status='EXACT INCIDENCE WRAPPER AND OPTIMISTIC NEGATIVE PASS',seconds=time.monotonic()-start)),flush=True)
    certificate=dict(status='EXACT INCIDENCE WRAPPER AND OPTIMISTIC NEGATIVE PASS',
                     cases=sorted(receipts,key=lambda d:(d['h'],d['prime'])),
                     favorable_ledgers=[lower_bound(h) for h in (5,6,7,23,25)],
                     seconds=time.monotonic()-start,
                     claim='Same-width self calls have normalized stock below one, but the full favorable moment is noncontracting. This refutes this exact chronology, not different chronology, geometry, source/sink stock or circuit families.')
    (args.output/'certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')


if __name__=='__main__':main()
