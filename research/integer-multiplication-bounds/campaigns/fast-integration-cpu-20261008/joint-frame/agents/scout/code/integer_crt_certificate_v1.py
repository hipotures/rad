#!/usr/bin/env python3
"""Certify primes and a generic integer determinant bound for h=23,25.

For p=k*2**32+1, odd k<2**32, a**((p-1)//2)=-1 mod p
proves primality: each prime factor q has 2**32 dividing q-1, so
q>sqrt(p). Twelve such primes exceed every integer minor bound.
"""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from math import factorial,prod
from pathlib import Path
import subprocess
import time


def certificate():
    primes=[];k=(1<<29)+1
    while len(primes)<12:
        p=k*(1<<32)+1
        for a in range(2,34):
            if pow(a,(p-1)//2,p)==p-1:
                assert k%2==1 and k<(1<<32) and p<(1<<64)
                primes.append(dict(p=p,k=k,power_of_two=32,witness=a))
                break
        k+=2
    P=prod(row['p'] for row in primes)
    bounds={}
    for h in [23,25]:
        den=3*(h+1)*(h-1)
        B0=(4*h-2)*(3*h-7)+27*(h+1)
        H=2*den*(den+B0)
        bound=factorial(h)*H**h
        assert P>bound and min(row['p'] for row in primes)>den
        bounds[str(h)]=dict(maximum_projector_denominator=den,
            maximum_projector_integer_numerator=den+B0,
            maximum_residual_integer_numerator=H,
            every_minor_integer_bound=bound,prime_product_gap=P-bound)
    return dict(status='GENERIC EVERY-MINOR INTEGER CRT CERTIFICATE PASS',
        primes=primes,prime_product=P,dimensions=bounds,
        proof='Each prime divisor q of p has 2^32 dividing q-1 by the certified halfway power. Thus q>sqrt(p), proving p prime. A k by k minor of an integer matrix bounded by H has absolute determinant <=k! H^k<=h! H^h. Product of the twelve distinct certified primes strictly exceeds this bound. Pointwise maxima of modular corner ranks equal rational corner ranks.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--binary',type=Path)
    ap.add_argument('--transitions',type=Path)
    ap.add_argument('--profiles',type=Path)
    args=ap.parse_args();assert __debug__ and not args.output.exists()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    result=certificate();result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    result['recorded_utc']=datetime.now(timezone.utc).isoformat()
    if args.binary:
        assert args.transitions and args.profiles and not args.profiles.exists()
        h=int.from_bytes(args.transitions.read_bytes()[:4],'little')
        command=[str(args.binary.resolve()),str(args.transitions.resolve()),str(args.profiles.resolve()),
                 str(result['dimensions'][str(h)]['maximum_residual_integer_numerator'])]
        command.extend(str(row['p']) for row in result['primes'])
        result['command']=command
        result['input_sha256']=sha256(args.transitions.read_bytes()).hexdigest()
        result['binary_sha256']=sha256(args.binary.read_bytes()).hexdigest()
        result['cpp_source_sha256']=sha256(Path(__file__).with_name('integer_crt_profiles.cpp').read_bytes()).hexdigest()
        start=time.monotonic();subprocess.run(command,check=True)
        result['seconds']=time.monotonic()-start
        result['profiles_sha256']=sha256(args.profiles.read_bytes()).hexdigest()
        result['native_threads']=1
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],moduli=len(result['primes']),seconds=result.get('seconds'))),flush=True)


if __name__=='__main__':main()
