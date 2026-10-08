#!/usr/bin/env python3
"""Independent exact controls for general symmetric quadratic phase edges.

This proves finite operator identities, not a complete recursive machine.
Quadratic values use Z/4, coefficient numerators use Gaussian integers.
The direct reference uses an integer Walsh transform; the candidate uses
orthogonal block reduction and ordinary Gaussian-dyadic C tensor entries.
"""
import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
from time import perf_counter


def dot(a,b):return (a&b).bit_count()&1


def embed(coefficients,basis):
    value=0
    for j,v in enumerate(basis):
        if coefficients>>j&1:value ^=v
    return value


def multiply(z,w):return z[0]*w[0]-z[1]*w[1],z[0]*w[1]+z[1]*w[0]


def unit(z,k):return (z,(-z[1],z[0]),(-z[0],-z[1]),(z[1],-z[0]))[k%4]


def add(z,w):return z[0]+w[0],z[1]+w[1]


def tensor_c_numerator(a,b,r):
    z=(1,0)
    for j in range(r):z=multiply(z,(1,-1) if (a^b)>>j&1 else (1,1))
    return z


class Quadratic:
    def __init__(self,rows,linear):
        self.rows=tuple(rows);self.linear=tuple(linear);self.n=len(rows)
        if len(linear)!=self.n:raise ValueError('Wrong quadratic lift dimension')
        if any(row<0 or row>=1<<self.n for row in rows):raise ValueError('Bad binary matrix row')
        if any(a not in range(4) for a in linear):raise ValueError('Bad Z4 linear coefficient')
        if any((linear[j]&1)!=((rows[j]>>j)&1) for j in range(self.n)):
            raise ValueError('Quadratic lift parity differs from its polar diagonal')
        if any(((rows[j]>>k)&1)!=((rows[k]>>j)&1) for j in range(self.n) for k in range(self.n)):
            raise ValueError('Polar matrix is not symmetric')

    def matrix(self,x):return sum(dot(row,x)<<j for j,row in enumerate(self.rows))

    def bilinear(self,x,y):return dot(x,self.matrix(y))

    def value(self,x):
        result=sum(c for j,c in enumerate(self.linear) if x>>j&1)
        result +=2*sum(((self.rows[j]>>k)&1) for j in range(self.n) for k in range(j+1,self.n) if x>>j&1 and x>>k&1)
        return result%4

    def block_basis(self):
        remaining=[1<<j for j in range(self.n)];chosen=[];blocks=[]
        while remaining:
            diagonal=next((j for j,v in enumerate(remaining) if self.bilinear(v,v)),None)
            if diagonal is not None:
                u=remaining.pop(diagonal);chosen.append(u);blocks.append(1)
                remaining=[v^(u if self.bilinear(u,v) else 0) for v in remaining]
                continue
            pair=next(((j,k) for j,u in enumerate(remaining) for k,v in enumerate(remaining) if j<k and self.bilinear(u,v)),None)
            if pair is None:break
            j,k=pair;u,v=remaining[j],remaining[k];chosen.extend((u,v));blocks.append(2)
            remaining=[w^(u if self.bilinear(v,w) else 0)^(v if self.bilinear(u,w) else 0)
                       for a,w in enumerate(remaining) if a not in (j,k)]
        rank=len(chosen);basis=tuple(chosen+remaining)
        assert len({embed(a,basis) for a in range(1<<self.n)})==1<<self.n
        assert all(not self.matrix(v) for v in remaining)
        return basis,tuple(blocks),rank

    def normal_form(self):
        basis,blocks,r=self.block_basis();lift=tuple(self.value(v) for v in basis)
        b_rows=tuple(sum(self.bilinear(u,v)<<j for j,v in enumerate(basis[:r])) for u in basis[:r])
        assert all(sum(dot(row,b_rows[j])<<j for j in range(r))==1<<k for k,row in enumerate(b_rows))
        G=(1,0);offset=0
        for size in blocks:
            if size==1:G=multiply(G,add((1,0),unit((1,0),lift[offset])))
            else:
                block=(0,0)
                for x,y in product(range(2),repeat=2):block=add(block,unit((1,0),lift[offset]*x+lift[offset+1]*y+2*x*y))
                assert block in ((2,0),(-2,0));G=multiply(G,block)
            offset+=size
        denominator=tensor_c_numerator(0,0,r)
        quotient=multiply(G,(denominator[0],-denominator[1]))
        scale=1<<r
        assert all(x%scale==0 for x in quotient)
        constant=tuple(x//scale for x in quotient)
        assert constant in ((1,0),(0,1),(-1,0),(0,-1))
        radical_translation=sum((lift[r+j]//2)<<j for j in range(self.n-r))
        assert all(x%2==0 for x in lift[r:])
        return dict(basis=basis,blocks=blocks,rank=r,lift=lift,b_rows=b_rows,
                    gauss_sum=G,constant=constant,radical_translation=radical_translation)


def walsh_reference(q):
    values=[unit((1,0),q.value(x)) for x in range(1<<q.n)]
    step=1
    while step<len(values):
        for start in range(0,len(values),2*step):
            for j in range(start,start+step):
                a,b=values[j],values[j+step]
                values[j]=add(a,b);values[j+step]=(a[0]-b[0],a[1]-b[1])
        step *=2
    return values


def candidate_numerator(q,nf,a,b,omit_radical=False,omit_constant=False):
    r=nf['rank'];basis=nf['basis'];rows=nf['b_rows'];mask=(1<<r)-1
    aa=sum(dot(a,v)<<j for j,v in enumerate(basis));bb=sum(dot(b,v)<<j for j,v in enumerate(basis))
    required=0 if omit_radical else nf['radical_translation']
    if (aa^bb)>>r!=required:return (0,0)
    aa &=mask;bb &=mask
    ia=sum(dot(row,aa)<<j for j,row in enumerate(rows));ib=sum(dot(row,bb)<<j for j,row in enumerate(rows))
    chirp=q.value(embed(ia,basis[:r]))+q.value(embed(ib,basis[:r]))
    result=unit(tensor_c_numerator(aa,ib,r),aa.bit_count()+ib.bit_count()-chirp)
    return result if omit_constant else multiply(nf['constant'],result)


def verify_case(q,all_entries=True):
    nf=q.normal_form();reference=walsh_reference(q);r=nf['rank']
    assert all(q.value(x^y)==(q.value(x)+q.value(y)+2*q.bilinear(x,y))%4
               for x in range(1<<q.n) for y in range(1<<q.n))
    direct_G=(0,0)
    for a in range(1<<r):direct_G=add(direct_G,unit((1,0),q.value(embed(a,nf['basis'][:r]))))
    assert direct_G==nf['gauss_sum']
    count=0;digest=sha256()
    for a in range(1<<q.n):
        for b in range(1<<q.n) if all_entries else (0,):
            z=candidate_numerator(q,nf,a,b);expected=reference[a^b]
            assert expected==tuple(v*(1<<(q.n-r)) for v in z),(q.rows,q.linear,a,b,nf,z,expected)
            digest.update(f'{a},{b}:{z[0]},{z[1]};'.encode());count+=1
    return dict(n=q.n,rows=q.rows,linear=q.linear,rank=r,blocks=nf['blocks'],
                gauss_sum=nf['gauss_sum'],gaussian_unit=nf['constant'],
                radical_translation=nf['radical_translation'],exact_entries=count,
                coefficient_digest=digest.hexdigest())


def symmetric_rows(n,code):
    rows=[0]*n;position=0
    for j in range(n):
        for k in range(j,n):
            if code>>position&1:rows[j] |=1<<k;rows[k] |=1<<j
            position+=1
    return rows


def run(n,mode,seed,samples):
    started=perf_counter();rng=random.Random(seed);rows=[]
    total=1<<(n*(n+1)//2)
    configurations=((code,even) for code in range(total) for even in range(1<<n)) if mode=='exhaustive' else ((rng.randrange(total),rng.randrange(1<<n)) for _ in range(samples))
    by_rank={};entries=0;digest=sha256();examples=[]
    for code,even in configurations:
        matrix=symmetric_rows(n,code);linear=[((matrix[j]>>j)&1)+2*((even>>j)&1) for j in range(n)]
        q=Quadratic(matrix,linear);result=verify_case(q);r=result['rank'];by_rank[r]=by_rank.get(r,0)+1;entries+=result['exact_entries']
        digest.update(json.dumps(result,sort_keys=True).encode())
        if len(examples)<8:examples.append(result)
    # Pure radical phases require an address translation despite rank zero.
    radical=Quadratic([0]*n,[2]+[0]*(n-1));nf=radical.normal_form()
    assert walsh_reference(radical)[1]==(1<<n,0)
    assert candidate_numerator(radical,nf,1,0)==(1,0)
    assert candidate_numerator(radical,nf,1,0,omit_radical=True)==(0,0)
    # Hyperbolic Gauss sign is indispensable.
    sign=Quadratic([2,1],[2,2]);nf=sign.normal_form();ref=walsh_reference(sign)[0]
    assert ref==(-2,0) and candidate_numerator(sign,nf,0,0,omit_constant=True)!=(ref[0]//1,ref[1]//1)
    return dict(status='PASS exact general symmetric quadratic operator identities',n=n,mode=mode,seed=seed,
                configuration_count=sum(by_rank.values()),by_rank=by_rank,exact_entries=entries,
                deterministic_result_sha256=digest.hexdigest(),examples=examples,
                negative_controls=['Missing radical translation rejects a rank-zero phase','Missing Gaussian unit rejects a hyperbolic lift'],
                elapsed_seconds=perf_counter()-started,
                scope='Finite Gaussian-dyadic algebra only; paid selected-bit adapters, coefficient guards, a finite scalar network and full recurrence remain separate')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--n',type=int,required=True)
    p.add_argument('--mode',choices=('exhaustive','sampled'),default='sampled');p.add_argument('--samples',type=int,default=256)
    p.add_argument('--seed',type=int,default=20261008);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if not 1<=a.n<=10 or a.samples<=0:raise ValueError('Unsupported bounded configuration')
    if a.mode=='exhaustive' and a.n>4:raise ValueError('Avoid uncontrolled exhaustive growth')
    if a.output.exists():raise FileExistsError('Use a fresh output')
    result=run(a.n,a.mode,a.seed,a.samples);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='examples'}),flush=True)


if __name__=='__main__':main()
