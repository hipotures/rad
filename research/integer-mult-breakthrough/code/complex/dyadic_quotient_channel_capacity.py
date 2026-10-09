#!/usr/bin/env python3
"""Finite controls for a Gaussian-dyadic univariate channel-volume boundary.

Reduction R=Z[i,1/2] -> F5 takes i to3. A monic degree-N quotient is
free over R; nonzero idempotents cannot vanish under this reduction. An
embedded R^D therefore needs at leastD distinct irreducible factors of the
reduced modulus. This source checks finite factor counts, field CRTs and
reduced Gaussian product idempotents, not a native product implementation.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import itertools
import json
from pathlib import Path
import time

Q = 5
SIGNS = (((1,1),(1,-1)),((-1,1),(1,1)))


def trim(a):
    a = list(a)
    while a and not a[-1]:
        a.pop()
    return tuple(a)


def add(a,b):
    return trim([((a[j] if j < len(a) else 0)+(b[j] if j < len(b) else 0))%Q
                 for j in range(max(len(a),len(b)))])


def scale(a,c):
    return trim([x*c%Q for x in a])


def subtract(a,b):
    return add(a,scale(b,-1))


def multiply(a,b):
    if not a or not b:
        return ()
    out = [0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j] = (out[i+j]+x*y)%Q
    return trim(out)


def divide(a,b):
    if not b:
        raise ZeroDivisionError('zero polynomial')
    out = [0]*max(0,len(a)-len(b)+1)
    a = list(a)
    inverse = pow(b[-1],-1,Q)
    while len(a) >= len(b):
        k = len(a)-len(b)
        c = a[-1]*inverse%Q
        out[k] = c
        for j,x in enumerate(b):
            a[k+j] = (a[k+j]-c*x)%Q
        a = list(trim(a))
    return trim(out),trim(a)


def mod(a,p):
    return divide(a,p)[1]


def gcd(a,b):
    while b:
        a,b = b,mod(a,b)
    return scale(a,pow(a[-1],-1,Q)) if a else ()


def inverse_mod(a,p):
    old_r,r = p,a
    old_t,t = (), (1,)
    while r:
        quotient,remainder = divide(old_r,r)
        old_r,r = r,remainder
        old_t,t = t,subtract(old_t,multiply(quotient,t))
    if len(old_r)!=1:
        raise ValueError('nonunit polynomial residue')
    return mod(scale(old_t,pow(old_r[0],-1,Q)),p)


def power_mod(a,n,p):
    result = (1,)
    while n:
        if n&1:
            result = mod(multiply(result,a),p)
        a = mod(multiply(a,a),p)
        n >>= 1
    return result


def mobius(n):
    parity = 0
    prime = 2
    while prime*prime <= n:
        if n%prime == 0:
            n //= prime
            parity ^= 1
            if n%prime == 0:
                return 0
            while n%prime == 0:
                n //= prime
        prime += 1
    if n > 1:
        parity ^= 1
    return -1 if parity else 1


def count_formula(degree):
    total = sum(mobius(degree//j)*Q**j for j in range(1,degree+1) if degree%j == 0)
    if total%degree:
        raise AssertionError('irreducible count formula is not integral')
    return total//degree


def prime_divisors(n):
    return [p for p in range(2,n+1) if n%p == 0 and all(p%d for d in range(2,p))]


def irreducible(p):
    degree = len(p)-1
    x = (0,1)
    if subtract(power_mod(x,Q**degree,p),mod(x,p)):
        return False
    for prime in prime_divisors(degree):
        if len(gcd(p,subtract(power_mod(x,Q**(degree//prime),p),x)))!=1:
            return False
    return True


def factor_probe(degree):
    samples = []
    count = 0
    for low in itertools.product(range(Q),repeat=degree):
        p = low+(1,)
        if irreducible(p):
            count += 1
            if len(samples) < 16:
                samples.append(p)
    if count!=count_formula(degree):
        raise AssertionError('literal irreducible enumeration disagrees with Mobius count')
    return dict(degree=degree,enumerated_monic_polynomials=Q**degree,
                irreducibles=count,samples=samples)


def minimum_degree(channels):
    degree = 1
    remaining = channels
    result = 0
    allocation = []
    while remaining:
        amount = min(remaining,count_formula(degree))
        allocation.append(dict(factor_degree=degree,factors=amount))
        result += degree*amount
        remaining -= amount
        degree += 1
    return result,allocation


def crt_probe(f):
    D = 1 << f
    expected,allocation = minimum_degree(D)
    factors = []
    degree = 1
    while len(factors) < D:
        for low in itertools.product(range(Q),repeat=degree):
            p = low+(1,)
            if irreducible(p):
                factors.append(p)
                if len(factors)==D:
                    break
        degree += 1
    P = (1,)
    for factor in factors:
        P = multiply(P,factor)
    if len(P)-1!=expected:
        raise AssertionError('constructed field CRT modulus is not smallest-degree allocation')
    idempotents = []
    for factor in factors:
        quotient,remainder = divide(P,factor)
        if remainder:
            raise AssertionError('CRT factor did not divide product modulus')
        idempotents.append(mod(multiply(quotient,inverse_mod(mod(quotient,factor),factor)),P))
    for i,e in enumerate(idempotents):
        if not e or mod(multiply(e,e),P)!=e:
            raise AssertionError('CRT component idempotent is missing or not idempotent')
        for j in range(i):
            if mod(multiply(e,idempotents[j]),P):
                raise AssertionError('distinct CRT idempotents are not orthogonal')
    if mod(sum_polynomials(idempotents),P)!=(1,):
        raise AssertionError('CRT idempotents do not sum to unit')
    repeated = multiply(factors[0],factors[0])
    if len(gcd(repeated,factors[0]))!=len(factors[0]):
        raise AssertionError('repeated-factor local negative is inconsistent')
    repeated_idempotents = [a for a in itertools.product(range(Q),repeat=2)
                            if mod(multiply(a,a),repeated)==trim(a)]
    if repeated_idempotents!=[(0,0),(1,0)]:
        raise AssertionError('a doubled linear factor created a forbidden extra idempotent')
    return dict(binary_axes=f,channels=D,modulus_degree=expected,
                allocation=allocation,idempotent_pairs=D*(D+1)//2,
                complete_modulus_coefficients=list(P),
                coefficient_grid='F5 only; no lift to R is asserted',
                repeated_factor_adds_no_distinct_factor=True)


def sum_polynomials(values):
    result = ()
    for value in values:
        result = add(result,value)
    return result


def transform(values,inverse=False):
    alpha,beta = (4,2) if inverse else (2,4)
    out = list(values)
    for j in range(len(out).bit_length()-1):
        for x in range(len(out)):
            if x>>j&1:
                continue
            y = x^(1<<j)
            a,b = out[x],out[y]
            out[x],out[y] = (alpha*a+beta*b)%Q,(beta*a+alpha*b)%Q
    return out


def product_direct(A,B):
    f = len(A).bit_length()-1
    output = []
    for z in range(len(A)):
        value = 0
        for x,a in enumerate(A):
            for y,b in enumerate(B):
                sign = 1
                for j in range(f):
                    sign *= SIGNS[z>>j&1][x>>j&1][y>>j&1]
                value += sign*a*b
        output.append(value*pow(3,f,Q)%Q)
    return output


def gaussian_reduction_probe(f):
    D = 1 << f
    idempotents = []
    for j in range(D):
        unit = [0]*D
        unit[j] = 1
        e = transform(unit,inverse=True)
        if not any(e) or transform(e)!=unit:
            raise AssertionError('reduced Gaussian character idempotent vanished or lost inverse')
        idempotents.append(e)
    count = 0
    for i,e in enumerate(idempotents):
        for j,a in enumerate(idempotents):
            reference = e if i==j else [0]*D
            if product_direct(e,a)!=reference:
                raise AssertionError('direct reduced Gaussian product lost orthogonal idempotents')
            count += D
    if [sum(e[x] for e in idempotents)%Q for x in range(D)]!=[1]*D:
        raise AssertionError('reduced Gaussian idempotents do not sum to allones unit')
    # The denominator map 2^-p ->3^p must be independent of zero extension.
    for re in range(-4,5):
        for im in range(-4,5):
            for grid in range(5):
                value = (re+3*im)*pow(3,grid,Q)%Q
                extended = (2*re+6*im)*pow(3,grid+1,Q)%Q
                if value!=extended:
                    raise AssertionError('Gaussian-dyadic residue is grid-dependent')
    return dict(binary_axes=f,channels=D,complete_product_coefficients=count,
                Gaussian_prime='2+i',residue_field=5,i_residue=3,half_residue=3,
                nonzero_reduced_idempotents=D,
                dyadic_zero_extension_cases=9*9*5)


def run_task(task):
    kind,value = task
    return kind,{'factors':factor_probe,'CRT':crt_probe,'Gaussian':gaussian_reduction_probe}[kind](value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive worker count required')
    source = sha256(Path(__file__).read_bytes()).hexdigest()
    utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [('factors',j) for j in ((1,2,3) if args.bounded else range(1,7))]
    tasks += [('CRT',f) for f in ((1,2) if args.bounded else (1,2,3,4))]
    tasks += [('Gaussian',f) for f in ((1,2) if args.bounded else (1,2,3,4))]
    if args.workers==1:
        results = [run_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(run_task,tasks))
    if sha256(Path(__file__).read_bytes()).hexdigest()!=source:
        raise AssertionError('source changed during run')
    capacity = []
    for f in (1,2,3,4,5,6,8,12,16,32,64):
        N,allocation = minimum_degree(1<<f)
        capacity.append(dict(binary_axes=f,channels=1<<f,minimum_reduced_degree=N,
                             degree_ratio=dict(numerator=N,denominator=1<<f),allocation=allocation))
    result = dict(status='PASS EXACT DYADIC QUOTIENT CHANNEL CONTROLS',
                  started_utc=utc,completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=source,workers=args.workers,bounded=args.bounded,
                  results=[dict(kind=kind,case=case) for kind,case in results],capacity=capacity,
                  seconds=time.monotonic()-started,
                  scope='Finite F5 factor/CRT/Gaussian reduction controls. The all-size monic free quotient idempotent argument is analytical; no native multiplier, odd-denominator encoding, sparse format or kappa is certified.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(results),seconds=result['seconds'])),flush=True)


if __name__=='__main__':
    main()
