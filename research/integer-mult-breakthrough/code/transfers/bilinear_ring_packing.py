#!/usr/bin/env python3
"""Exact bilinear fusion, ordinary-product collisions and paid CRT packing.

Character encoding/decoding is literal dense reference work, never free.
The CRT products have their actual full modulus operand sizes recorded.
No new multiplier oracle, all-size native transfer or exponent is claimed.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import prod
from pathlib import Path
from random import Random
import time

import conditioned_frame_review as g

TOPIC=Path(__file__).resolve().parents[2]
CONFIG=TOPIC/'configs/transfers/bilinear-ring-packing.json'
ALPHA,BETA=(Q(1,2),Q(1,2)),(Q(1,2),Q(-1,2))


def transforms(values,f,inverse=False):
    out=list(values);alpha,beta=(g.conjugate(ALPHA),g.conjugate(BETA)) if inverse else (ALPHA,BETA)
    for bit in range(f):
        mask=1<<bit
        for a in range(1<<f):
            if a&mask:continue
            x,y=out[a],out[a|mask]
            out[a]=g.add(g.multiply(alpha,x),g.multiply(beta,y))
            out[a|mask]=g.add(g.multiply(beta,x),g.multiply(alpha,y))
    return out


def fused_product(u,v,f):
    a,b=transforms(u,f),transforms(v,f)
    return transforms([g.multiply(x,y) for x,y in zip(a,b)],f,True)


def exact_tensor_formula(u,v,f):
    size=1<<f;out=[g.ZERO]*size
    for a,x in enumerate(u):
        if x==g.ZERO:continue
        for b,y in enumerate(v):
            if y==g.ZERO:continue
            value=g.multiply(x,y)
            for c in range(size):
                negative=((a&b).bit_count()+(c&((size-1)^(a^b))).bit_count())%2
                out[c]=g.add(out[c],((-value[0]/size,-value[1]/size) if negative else (value[0]/size,value[1]/size)))
    return out


def ring_product(u,v,f,negative_square=True):
    out=[g.ZERO]*(1<<f)
    for a,x in enumerate(u):
        for b,y in enumerate(v):
            value=g.multiply(x,y)
            if negative_square and (a&b).bit_count()%2:value=(-value[0],-value[1])
            out[a^b]=g.add(out[a^b],value)
    return out


def evaluate(values,f):
    size=1<<f;out=[]
    for character in range(size):
        total=g.ZERO
        for a,value in enumerate(values):
            phase=g.power(g.IMAGINARY,a.bit_count()+2*(a&character).bit_count())
            total=g.add(total,g.multiply(value,phase))
        out.append(total)
    return out


def interpolate(values,f):
    size=1<<f;out=[]
    for a in range(size):
        total=g.ZERO
        for character,value in enumerate(values):
            total=g.add(total,(-value[0],-value[1]) if (a&character).bit_count()%2 else value)
        total=g.multiply(total,g.power(g.IMAGINARY,-a.bit_count()))
        out.append((total[0]/size,total[1]/size))
    return out


def prime(value):
    if value<2:return False
    if value%2==0:return value==2
    divisor=3
    while divisor*divisor<=value:
        if value%divisor==0:return False
        divisor+=2
    return True


def crt_code(values,moduli,modulus):
    total=0
    for value,p in zip(values,moduli):
        if value.denominator!=1:raise ValueError('CRT finite input is not an integer field')
        part=modulus//p
        total+=(value.numerator%p)*part*pow(part,-1,p)
    return total%modulus


def crt_multiply(u,v,f,radius):
    size=1<<f;bound=4*size*size*radius*radius;moduli=[];candidate=bound+1
    while len(moduli)<size:
        if candidate%4==3 and prime(candidate):moduli.append(candidate)
        candidate+=1
    modulus=prod(moduli);a,b=evaluate(u,f),evaluate(v,f)
    ar,ai=[crt_code([z[k] for z in a],moduli,modulus) for k in (0,1)]
    br,bi=[crt_code([z[k] for z in b],moduli,modulus) for k in (0,1)]
    operands=[(ar,br),(ai,bi),(ar+ai,br+bi)]
    first,second,third=[x*y for x,y in operands]
    packed_real=(first-second)%modulus;packed_imag=(third-first-second)%modulus
    recovered=[]
    for p in moduli:
        real,imag=packed_real%p,packed_imag%p
        real=real-p if real>p//2 else real;imag=imag-p if imag>p//2 else imag
        recovered.append((Q(real),Q(imag)))
    products=[g.multiply(x,y) for x,y in zip(a,b)]
    if recovered!=products:raise ValueError('Complete CRT component product exceeds its guard or is wrong')
    result=interpolate(recovered,f);wanted=ring_product(u,v,f)
    if result!=wanted or any(z.denominator!=1 for row in result for z in row):
        raise ValueError('Exact Gaussian character interpolation/recovery failed')
    # One omitted component loses a nonzero bounded integral algebra element.
    missing=size-1
    kernel=[g.power(g.IMAGINARY,-a.bit_count()+2*(a&missing).bit_count()) for a in range(size)]
    response=evaluate(kernel,f)
    if any(value!=((Q(size),Q(0)) if a==missing else g.ZERO) for a,value in enumerate(response)):
        raise ValueError('Omitted-character integral kernel identity failed')
    if any(value!=g.ZERO for a,value in enumerate(response) if a!=missing) or all(value==g.ZERO for value in kernel):
        raise ValueError('Missing-component indistinguishability failed')
    return dict(character_components=size,distinct_prime_moduli=moduli,
                gaussian_extension='F_p[i]/(i^2+1), p=3mod4; two real/imaginary residue fields retained',
                integer_modulus_bits=modulus.bit_length(),integer_modulus_sha256=sha256(str(modulus).encode()).hexdigest(),
                actual_three_integer_product_operand_bits=[[x.bit_length(),y.bit_length()] for x,y in operands],
                dense_character_encoding_terms_per_operand=size*size,
                dense_character_interpolation_terms=size*size,
                centered_components_recovered=2*size,
                evaluated_product_component_peak=str(max(abs(z) for row in products for z in row)),
                component_guard_prime_lower_exclusive=bound,
                original_coefficient_component_peak=radius,
                missing_character=missing,omitted_character_kernel_nonzero_and_invisible=True,
                no_character_encoding_or_decoding_cost_waived=True,
                native_multiplication_cost_supplied=False)


def collision(f):
    size=1<<f
    pairs=[(1,1),(2,0)]
    ordinary=[];xor=[];negative=[]
    for a,b in pairs:
        polynomial=[0]*(2*size-1);polynomial[a+b]=1;ordinary.append(polynomial)
        x=[0]*size;x[a^b]=1;xor.append(x)
        n=[0]*size;n[a^b]=(-1 if (a&b).bit_count()%2 else 1);negative.append(n)
    if ordinary[0]!=ordinary[1] or xor[0]==xor[1] or negative[0]==negative[1]:
        raise ValueError('The complete ordinary-product collision does not discriminate')
    return dict(nonnegative_basis_pairs=pairs,ordinary_univariate_products_identical=True,
                ordinary_output_retains_full_degree=True,xor_targets=xor,negative_square_targets=negative,
                arbitrary_operand_independent_product_decoder_impossible=True,
                radix_three_no_carry_packed_span=3**f,radix_two_coefficients=size,
                radix_three_volume_ratio=str(Q(3**f,size)))


def monomial_embedding_control():
    rows=[]
    for n in (2,3,4,8,12,16):
        exponents=[a for a in range(n) if 2*a%n==0]
        if len(exponents)!=(2 if n%2==0 else 1):raise ValueError('Cyclic exponent two-torsion count failed')
        generated={0}
        for a in exponents:generated|={(x+a)%n for x in list(generated)}
        if len(generated)>2:raise ValueError('Independent order-two monomial exponent rank unexpectedly grew')
        rows.append(dict(extension_dimension=n,involutive_basis_exponents=exponents,
                         generated_scalar_basis_dimension_at_most=len(generated)))
    return rows


def probe(case):
    started=time.monotonic();f,seed=case['f'],case['seed'];size=1<<f;radius=2;randoms=Random(seed)
    u=[(Q(randoms.randrange(-radius,radius+1)),Q(randoms.randrange(-radius,radius+1))) for _ in range(size)]
    v=[(Q(randoms.randrange(-radius,radius+1)),Q(randoms.randrange(-radius,radius+1))) for _ in range(size)]
    literal=fused_product(u,v,f);formula=exact_tensor_formula(u,v,f)
    if literal!=formula:raise ValueError('Exact C-conjugated bilinear tensor or phase failed')
    unit=[g.ONE]*size
    if fused_product(unit,u,f)!=u:raise ValueError('The actual C-basis algebra unit is wrong')
    columns=0;coefficients=0
    if f<=3:
        for a in range(size):
            for b in range(size):
                x=[g.ZERO]*size;y=list(x);x[a]=g.ONE;y[b]=g.ONE
                if fused_product(x,y,f)!=exact_tensor_formula(x,y,f):raise ValueError('Complete C-basis bilinear column failed')
                columns+=1;coefficients+=size
    e0=[g.ZERO]*size;e0[0]=g.ONE
    if fused_product(e0,e0,f)==ring_product(e0,e0,f,False):
        raise ValueError('Ungauged XOR substitution did not reject')
    return dict(f=f,seed=seed,algebra_dimension=size,
                complete_C_bilinear_basis_pairs=columns,complete_C_bilinear_coefficients=coefficients,
                full_gaussian_operand_pair_checked=True,C_algebra_unit_is_all_ones=True,
                ungauged_XOR_product_rejected=True,binary_product_collision=collision(f),
                integral_negative_square_CRT=crt_multiply(u,v,f,radius),
                cyclic_monomial_two_torsion=monomial_embedding_control(),seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--small',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.workers<1 or (args.output and args.output.exists()):raise ValueError('Positive workers and a fresh output are required')
    config=json.loads(CONFIG.read_text());helper=Path(g.__file__).resolve()
    if sha256(helper.read_bytes()).hexdigest()!=config['independent_gaussian_helper_sha256']:raise ValueError('Frozen Gaussian helper changed')
    pins={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in (Path(__file__).resolve(),CONFIG,helper)}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,source_config_sha256=pins,
                  producer_imports=False,scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);(args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    cases=config['cases'][:1] if args.small else config['cases'];started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:rows=list(pool.map(probe,cases))
    if any(sha256((TOPIC/p).read_bytes()).hexdigest()!=value for p,value in pins.items()):raise ValueError('Source changed during immutable attempt')
    summary=dict(status='EXACT BILINEAR RING PACKING AND CAPACITY CONTROLS PASS',cases=rows,
                 seconds=time.monotonic()-started,scope=config['scope'],same_volume_native_supplier=False,new_exponent=False)
    if args.output:(args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('status','seconds','scope')}))


if __name__=='__main__':main()
