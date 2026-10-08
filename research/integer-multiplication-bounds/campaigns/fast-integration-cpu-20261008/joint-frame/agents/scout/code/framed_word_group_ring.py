#!/usr/bin/env python3
"""Exact finite projected-address dirty-wrapper model and matched negatives.

Matrices describe actual address permutations over an odd finite field. A
symbolic row is a binary sum of source-bank payloads evaluated at those maps.
Exact cancellation proves equality for every address and arbitrary payload.
The read-only copied-center adapter is modeled as an explicit conjugated XOR;
its inherited native recursive cost remains a separate hypothesis.
"""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import random
import time


class Geometry:
    def __init__(self,h,q):
        self.h,self.q=h,q;self.d=2*h
        self.zero=tuple(0 for _ in range(h*h));self.identity=tuple(int(i==j) for i in range(h) for j in range(h))
        self.full=self.identity;self.I=tuple(int(i==j) for i in range(2*h) for j in range(2*h))
        inv9=pow(9,-1,q)
        self.G=tuple((int(i==j)-inv9)%q for i in range(h) for j in range(h))
        self.swaps={};self.products={};self.projectors={}
    def multiply(self,A,B,n=None):
        n=n or self.d;key=(A,B,n)
        if key in self.products:return self.products[key]
        result=tuple(sum(A[i*n+k]*B[k*n+j] for k in range(n))%self.q for i in range(n) for j in range(n))
        self.products[key]=result;return result
    def inverse(self,A,n):
        rows=[[A[i*n+j] for j in range(n)]+[int(i==j) for j in range(n)] for i in range(n)]
        for c in range(n):
            pivot=next(i for i in range(c,n) if rows[i][c])
            rows[c],rows[pivot]=rows[pivot],rows[c]
            z=pow(rows[c][c],-1,self.q);rows[c]=[(x*z)%self.q for x in rows[c]]
            for i in range(n):
                if i!=c:
                    z=rows[i][c];rows[i]=[(x-z*y)%self.q for x,y in zip(rows[i],rows[c])]
        return tuple(rows[i][n+j] for i in range(n) for j in range(n))
    def projector(self,core,cover):
        key=(tuple(core),tuple(cover))
        if key in self.projectors:return self.projectors[key]
        h,q=self.h,self.q
        if len(core)==3:
            assert set(core)==set(cover);basis=[[int(i in core) for i in range(h)]]
        else:
            assert len(core) in (1,2);outside=sorted(set(cover)-set(core));s=3-len(core);inv=pow(s,-1,q)
            basis=[[int(i==j)+(inv if i in core else 0) for i in range(h)] for j in outside]
        r=len(basis)
        dual=[[sum(basis[a][i]*self.G[i*h+j] for i in range(h))%q for j in range(h)] for a in range(r)]
        gram=tuple(sum(dual[a][i]*basis[b][i] for i in range(h))%q for a in range(r) for b in range(r))
        inverse=self.inverse(gram,r)
        P=tuple(sum(basis[a][i]*inverse[a*r+b]*dual[b][j] for a in range(r) for b in range(r))%q for i in range(h) for j in range(h))
        assert self.multiply(P,P,h)==P
        GP=self.multiply(self.G,P,h);assert all(GP[i*h+j]==GP[j*h+i] for i in range(h) for j in range(h))
        self.projectors[key]=P;return P
    def complement(self,P):return tuple((a-b)%self.q for a,b in zip(self.identity,P))
    def S(self,P):
        if P not in self.swaps:
            h,q=self.h,self.q;E=self.complement(P)
            A=tuple((P if (i<h)!=(j<h) else E)[(i%h)*h+j%h] for i in range(2*h) for j in range(2*h))
            assert self.multiply(A,A)==self.I;self.swaps[P]=A
        return self.swaps[P]
    def apply(self,row,M):return {(source,self.multiply(A,M)) for source,A in row}
    def matvec(self,M,vector):return tuple(sum(M[i*self.d+j]*vector[j] for j in range(self.d))%self.q for i in range(self.d))


def model(h,q,orientation='forward',negative=None):
    assert h==5
    geo=Geometry(h,q);triples=list(combinations(range(h),3));v=len(triples);allcoords=tuple(range(h))
    x=list(range(v));y=list(range(v,2*v))
    if orientation=='reverse endpoints':x,y=y,x
    primary={T:2*v+i for i,T in enumerate(triples)};nextslot=2*v+v
    clones={};sides={};centers={}
    for T in triples:
        for c in T:clones[T,c]=nextslot;nextslot+=1
        for c in T:sides[T,c]=nextslot;nextslot+=1
    for c in range(h):centers[c]=nextslot;nextslot+=1
    size=nextslot;aux=list(range(2*v,size));rows=[{(i,geo.I)} for i in range(size)]
    frame=[geo.zero]*size;source_P={T:geo.projector(T,T) for T in triples}
    center_P={c:geo.projector((c,),allcoords) for c in range(h)}
    side_P={(T,c):geo.projector((c,),T) for T in triples for c in T}
    for i,T in enumerate(triples):frame[x[i]]=source_P[T]
    moves=[]
    def grow(role,P,label):
        old=frame[role]
        assert geo.multiply(P,old,h)==old and geo.multiply(old,P,h)==old
        if P!=old:
            residue=geo.multiply(geo.S(P),geo.S(old))
            assert geo.multiply(residue,residue)==geo.I
            rows[role]=geo.apply(rows[role],residue);frame[role]=P;moves.append((label,role))
    M=[]
    for T in triples:
        for c in T:M.append((clones[T,c],primary[T],source_P[T]))
        for c in T:M.append((sides[T,c],primary[T],source_P[T]))
    for c in range(h):
        for T in triples:
            if c in T:M.append((centers[c],clones[T,c],center_P[c]))
    Jcenter=[(y[i],centers[c],c) for i,T in enumerate(triples) for c in T]
    Jside=[]
    for T in triples:
        for c in T:
            target=tuple(sorted((c,)+tuple(set(allcoords)-set(T))))
            Jside.append((y[triples.index(target)],sides[T,c],target))
    def unframed_mixer(reverse=False):
        for a,b,P in reversed(M) if reverse else M:rows[a]^=rows[b]
    def scatter_unframed():
        for a,b,c in Jcenter:rows[a]^=rows[b]
        for a,b,T in Jside:rows[a]^=rows[b]
    def injection():
        for i,T in enumerate(triples):rows[primary[T]]^=rows[x[i]]
    unframed_mixer();scatter_unframed();unframed_mixer(True)
    for T in triples:grow(primary[T],source_P[T],'first source frame')
    injection()
    for a,b,P in M:
        grow(a,P,'middle mixer');grow(b,P,'middle mixer');rows[a]^=rows[b]
    for T in triples:
        for c in T:grow(sides[T,c],side_P[T,c],'side output incidence')
    # Explicit conjugated read-only XOR: y(a) ^= center(S_E a). This exact
    # macro is the copied-center interface whose native cost is inherited.
    for a,b,c in Jcenter:
        operand=rows[b] if negative=='omit center adapter' else geo.apply(rows[b],geo.S(center_P[c]))
        rows[a]^=operand
    for i,T in enumerate(triples):grow(y[i],geo.complement(source_P[T]),'target complement')
    for a,b,T in Jside:
        grow(b,geo.complement(source_P[T]),'ordinary output completion');rows[a]^=rows[b]
    if negative!='omit auxiliary cleanup':
        for role in aux:grow(role,geo.full,'auxiliary common full frame')
    unframed_mixer(True)
    for i,T in enumerate(triples):grow(x[i],geo.full,'source final complement')
    injection()
    expected=[{(i,geo.S(geo.full))} if i in aux else None for i in range(size)]
    for i,T in enumerate(triples):
        E=geo.S(geo.complement(source_P[T]));F=geo.S(geo.full)
        expected[x[i]]={(x[i],E)};expected[y[i]]={(y[i],E),(x[i],F)}
    failures=[i for i in range(size) if rows[i]!=expected[i]]
    witness=None
    if failures:
        candidates=[tuple(int(j==i) for j in range(2*h)) for i in range(2*h)]
        rng=random.Random(58261008)
        candidates.extend(tuple(rng.randrange(q) for _ in range(2*h)) for _ in range(128))
        for role in failures:
            difference=rows[role]^expected[role]
            for address in candidates:
                active=set()
                for source,A in difference:
                    term=(source,geo.matvec(A,address))
                    if term in active:active.remove(term)
                    else:active.add(term)
                if active:
                    source,payload_address=sorted(active)[0]
                    witness=dict(physical_output_role=role,output_address=address,
                        single_nonzero_initial_payload_bank=source,initial_payload_address=payload_address)
                    break
            if witness:break
        assert witness,'Symbolic failure without actual address/payload witness'
    if negative:assert failures and witness
    else:assert not failures
    return dict(status='RIGOROUS FINITE ADDRESS COUNTEREXAMPLE' if negative else 'EXACT EVERY-ADDRESS PROJECTED-WORD IDENTITY PASS',
        h=h,q=q,orientation=orientation,negative=negative,roles=size,auxiliary_roles=len(aux),
        scalar_mixer_xors=len(M),projected_frame_moves=len(moves),
        all_addresses=q**(2*h),arbitrary_payload_function_and_dirty_banks=True,
        differing_rows=len(failures),counterexample=witness,
        copied_center_contract='Exact read-only conjugated XOR y(a)^=center(S_E a), cost/stock inherited and not proved by this model.',
        output_law='x_T -> S_(t_T^perp)x_T; y_T -> S_F x_T + S_(t_T^perp)y_T; every auxiliary -> S_F dirty auxiliary.',
        scope='Exact finite address permutation algebra on a new h5 hand producer, with explicit copied-center adapter. No native compiler cost proof, actual h23/h25 execution or all-size tape claim.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args();assert __debug__ and not args.output.exists();args.output.parent.mkdir(parents=True,exist_ok=True)
    start=time.monotonic();cases=[]
    for q in [7,11,13]:
        for orientation in ['forward','reverse endpoints']:
            cases.append(model(5,q,orientation))
            for negative in ['omit center adapter','omit auxiliary cleanup']:cases.append(model(5,q,orientation,negative))
    result=dict(status='EXACT PROJECTED WORD AND MATCHED ADDRESS NEGATIVES PASS',
        recorded_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        cases=cases,seconds=time.monotonic()-start,native_threads=1,
        interpretation='The eight-phase wrapper needs projected growth only in the middle mixer plus completed endpoint/auxiliary moves. The extra mixers are scalar pointwise XORs at common zero/full frames. This supports the proposed framing law conditional on the exact copied-center and residual-compiler interfaces; it does not establish their native costs.')
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(cases),seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
