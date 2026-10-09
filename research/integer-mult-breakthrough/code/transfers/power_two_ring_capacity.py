#!/usr/bin/env python3
"""Exact field-factor/idempotent controls for power-two product encodings.

The all-size Gaussian Eisenstein and orthogonal-idempotent argument is stated
in the report. Finite CRT polynomials here are paid algebra reference work,
not a native supplier, a linear-transform circulant equivalence, or a new kappa.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
from random import Random
import time

import conditioned_frame_review as g

TOPIC=Path(__file__).resolve().parents[2]
CONFIG=TOPIC/'configs/transfers/power-two-ring-capacity.json'


def trim(a):
    a=list(a)
    while a and a[-1]==g.ZERO:a.pop()
    return a


def add(a,b):
    return trim([g.add(a[j] if j<len(a) else g.ZERO,b[j] if j<len(b) else g.ZERO)
                 for j in range(max(len(a),len(b)))])


def scale(a,c):return trim([g.multiply(x,c) for x in a])


def subtract(a,b):return add(a,scale(b,(-Q(1),Q(0))))


def multiply(a,b):
    out=[g.ZERO]*max(0,len(a)+len(b)-1)
    for j,x in enumerate(a):
        if x==g.ZERO:continue
        for k,y in enumerate(b):
            if y!=g.ZERO:out[j+k]=g.add(out[j+k],g.multiply(x,y))
    return trim(out)


def divide(a,b):
    if not b:raise ValueError('Polynomial divisor zero')
    a=trim(a);q=[g.ZERO]*max(0,len(a)-len(b)+1);inverse=g.power(b[-1],-1)
    while len(a)>=len(b):
        k=len(a)-len(b);c=g.multiply(a[-1],inverse);q[k]=g.add(q[k],c)
        a=subtract(a,[g.ZERO]*k+scale(b,c))
    return trim(q),a


def inverse_mod(a,b):
    old,r=b,a;old_s,s=[],[g.ONE]
    while r:
        q,next_r=divide(old,r)
        old,r=r,next_r;old_s,s=s,subtract(old_s,multiply(q,s))
    if len(old)!=1:raise ValueError('Distinct factor CRT inverse failed')
    return divide(scale(old_s,g.power(old[0],-1)),b)[1]


def modulus(n,negative):
    size=1<<n
    return [(Q(1 if negative else -1),Q(0))]+[g.ZERO]*(size-1)+[g.ONE]


def factors(n,negative):
    degrees=[1<<(n-1)] if negative else [1<<j for j in range(n-1)]
    out=[] if negative else [[(-Q(1),Q(0)),g.ONE],[g.ONE,g.ONE]]
    for degree in degrees:
        for sign in (-1,1):
            out.append([(Q(0),Q(sign))]+[g.ZERO]*(degree-1)+[g.ONE])
    return out


def eisenstein(degree,sign):
    # X->X+1 gives constant 1+sign*i with Gaussian-(1+i) valuation one.
    # For degree a power of two every nonleading interior binomial is even.
    if degree<1 or degree&(degree-1):raise ValueError('Eisenstein degree is not a power of two')
    middle=[comb(degree,j) for j in range(1,degree)]
    if any(x%2 for x in middle):raise ValueError('Gaussian prime divisibility failed')
    constant=(Q(1),Q(sign))
    first=g.multiply(constant,g.power((Q(1),Q(1)),-1))
    second=g.multiply(first,g.power((Q(1),Q(1)),-1))
    if any(x.denominator!=1 for x in first) or all(x.denominator==1 for x in second):
        raise ValueError('Gaussian constant has wrong prime valuation')
    return dict(degree=degree,sign=sign,all_interior_binomials_even=True,
                shifted_constant_gaussian_prime_valuation=1)


def primitive_idempotents(n,negative):
    full=modulus(n,negative);pieces=factors(n,negative);product=[g.ONE]
    for p in pieces:product=multiply(product,p)
    if product!=full:raise ValueError('Complete power-two factorization failed')
    out=[]
    for p in pieces:
        other,remainder=divide(full,p)
        if remainder:raise ValueError('Field factor did not divide full modulus')
        e=divide(multiply(other,inverse_mod(divide(other,p)[1],p)),full)[1]
        if not e:raise ValueError('Primitive idempotent vanished')
        out.append(e)
    for j,e in enumerate(out):
        for k,d in enumerate(out):
            if divide(multiply(e,d),full)[1]!=(e if j==k else []):
                raise ValueError('Full orthogonal idempotent product failed')
    total=[]
    for e in out:total=add(total,e)
    if total!=[g.ONE]:raise ValueError('Complete primitive idempotents do not sum to one')
    if any(x.denominator&(x.denominator-1) for e in out for z in e for x in z):
        raise ValueError('Power-two CRT introduced an odd denominator')
    return full,pieces,out


def rank(columns):
    n=len(columns[0]);a=[[column[j] for column in columns] for j in range(n)];row=0
    for column in range(len(columns)):
        pivot=next((j for j in range(row,n) if a[j][column]!=g.ZERO),None)
        if pivot is None:continue
        a[row],a[pivot]=a[pivot],a[row]
        inv=g.power(a[row][column],-1);a[row]=[g.multiply(x,inv) for x in a[row]]
        for j in range(n):
            if j!=row and a[j][column]!=g.ZERO:
                c=a[j][column];a[j]=[g.add(x,g.multiply((-c[0],-c[1]),y)) for x,y in zip(a[j],a[row])]
        row+=1
    return row


def encoded_product_control():
    full,pieces,idempotents=primitive_idempotents(2,False)
    generators=[]
    for bit in range(2):
        p=[]
        for character,e in enumerate(idempotents):
            p=add(p,scale(e,(Q(0),Q(-1 if character>>bit&1 else 1))))
        if divide(multiply(p,p),full)[1]!=[(-Q(1),Q(0))]:raise ValueError('Encoded generator square is wrong')
        generators.append(p)
    basis=[[g.ONE],generators[0],generators[1],divide(multiply(*generators),full)[1]]
    padded=[p+[g.ZERO]*(4-len(p)) for p in basis]
    if rank(padded)!=4:raise ValueError('Positive nonmonomial four-character encoding lost rank')
    randoms=Random(202610090445);u=[(Q(randoms.randrange(-2,3)),Q(randoms.randrange(-2,3))) for _ in range(4)]
    v=[(Q(randoms.randrange(-2,3)),Q(randoms.randrange(-2,3))) for _ in range(4)]
    def encode(values):
        result=[]
        for x,p in zip(values,basis):result=add(result,scale(p,x))
        return result
    result=[g.ZERO]*4
    for a,x in enumerate(u):
        for b,y in enumerate(v):
            z=g.multiply(x,y)
            if (a&b).bit_count()%2:z=(-z[0],-z[1])
            result[a^b]=g.add(result[a^b],z)
    if divide(multiply(encode(u),encode(v)),full)[1]!=encode(result):
        raise ValueError('Positive complete nonmonomial algebra product failed')
    if not any(sum(x!=g.ZERO for x in p)>1 for p in generators):
        raise ValueError('Nonmonomial positive control was unexpectedly monomial')
    return dict(algebra_characters=4,cyclic_extension_dimension=4,faithful_basis_rank=4,
                encoded_generator_polynomials=[[[str(a),str(b)] for a,b in p] for p in generators],
                arbitrary_gaussian_product_checked=True,not_all_generators_monomial=True,
                encoding_cost_not_waived=True)


def probe(n):
    started=time.monotonic();rows=[]
    for negative in (False,True):
        full,pieces,idem=primitive_idempotents(n,negative);checks=[]
        for p in pieces:
            if p[0][0]==0:checks.append(eisenstein(len(p)-1,int(p[0][1])))
        count=2 if negative else 2*n
        if len(pieces)!=count:raise ValueError('Analytical field-factor count differs')
        rows.append(dict(ring='negacyclic' if negative else 'cyclic',extension_dimension=1<<n,
                         exact_field_factor_count=count,field_factor_degrees=[len(p)-1 for p in pieces],
                         gaussian_eisenstein_checks=checks,complete_orthogonal_idempotent_pair_checks=count*count,
                         all_idempotents_nonzero=True,idempotents_sum_to_one=True,idempotent_coefficients_dyadic=True,
                         max_idempotent_denominator=max(x.denominator for p in idem for z in p for x in z),
                         literal_factorization_and_idempotents_verified=True))
    return dict(n=n,rings=rows,positive_nonmonomial_control=encoded_product_control() if n==2 else None,
                seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--small',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.workers<1 or (args.output and args.output.exists()):raise ValueError('Positive workers and fresh output required')
    config=json.loads(CONFIG.read_text());helper=Path(g.__file__).resolve()
    if sha256(helper.read_bytes()).hexdigest()!=config['independent_gaussian_helper_sha256']:raise ValueError('Frozen Gaussian helper changed')
    pins={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in (Path(__file__).resolve(),CONFIG,helper)}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,source_config_sha256=pins,
                  producer_imports=False,scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);(args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    cases=[2] if args.small else config['n_cases'];started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:rows=list(pool.map(probe,cases))
    if any(sha256((TOPIC/p).read_bytes()).hexdigest()!=value for p,value in pins.items()):raise ValueError('Source changed during attempt')
    result=dict(status='EXACT POWER-TWO FIELD FACTOR AND IDEMPOTENT CONTROLS PASS',cases=rows,
                seconds=time.monotonic()-started,scope=config['scope'],native_encoding_cost_supplied=False,new_exponent=False)
    if args.output:(args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','seconds','scope')}))


if __name__=='__main__':main()
