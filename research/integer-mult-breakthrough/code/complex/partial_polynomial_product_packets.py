#!/usr/bin/env python3
"""Exact partial Gaussian product on complete negacyclic polynomial records.

Every leaf uses one real or three Gaussian signed-radix integer products,
with complete balanced decoding before negacyclic folding. Product operand
sizes refer to whole polynomial records, not coefficient precision. This is
an arithmetic reference; it does not implement orbit layout or tape access.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time

SIGNS = (((1,1),(1,-1)),((-1,1),(1,1)))


def gaussian_add(a,b):
    return a[0]+b[0],a[1]+b[1]


def gaussian_multiply(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def polynomial_add(A,B):
    return [gaussian_add(a,b) for a,b in zip(A,B)]


def polynomial_scale(A,c):
    return [(c*a,c*b) for a,b in A]


def direct_polynomial_product(A,B):
    r = len(A)
    out = [(0,0)]*r
    for j,a in enumerate(A):
        for k,b in enumerate(B):
            value = gaussian_multiply(a,b)
            if j+k>=r:
                value = -value[0],-value[1]
            out[(j+k)%r] = gaussian_add(out[(j+k)%r],value)
    return out


def encode_signed(A,base):
    out = 0
    for a in reversed(A):
        out = out*base+a
    return out


def decode_balanced(value,base,length):
    out = []
    for j in range(length):
        digit = value%base
        if 2*digit>=base:
            digit -= base
        out.append(digit)
        value = (value-digit)//base
    if value:
        raise AssertionError('complete balanced polynomial product retained nonzero tail')
    return out


def integer_polynomial_product(A,B,audit):
    r = len(A)
    limit = max([abs(x) for x in A+B]+[1])
    bound = r*limit*limit
    bits = (2*bound).bit_length()
    base = 1 << bits
    if base<=2*bound:
        raise AssertionError('balanced carry guard is not strict')
    a = encode_signed(A,base)
    b = encode_signed(B,base)
    c = a*b
    audit['integer_products'] += 1
    audit['maximum_radix_bits'] = max(audit['maximum_radix_bits'],bits)
    audit['maximum_product_operand_signed_bits'] = max(audit['maximum_product_operand_signed_bits'],abs(a).bit_length()+1,abs(b).bit_length()+1)
    audit['maximum_integer_product_signed_bits'] = max(audit['maximum_integer_product_signed_bits'],abs(c).bit_length()+1)
    decoded = decode_balanced(c,base,2*r-1)
    direct = [0]*(2*r-1)
    for j,x in enumerate(A):
        for k,y in enumerate(B):
            direct[j+k] += x*y
    if direct!=decoded or any(2*abs(x)>=base for x in direct):
        raise AssertionError('signed integer product did not recover every polynomial coefficient')
    audit['complete_decoded_real_coefficients'] += len(decoded)
    return [decoded[j]-(decoded[j+r] if j+r<len(decoded) else 0) for j in range(r)]


def encoded_gaussian_product(A,B,audit,real):
    ar = [x for x,y in A]
    ai = [y for x,y in A]
    br = [x for x,y in B]
    bi = [y for x,y in B]
    audit['polynomial_leaf_products'] += 1
    if real:
        if any(ai+bi):
            raise AssertionError('real-only polynomial contract acquired imaginary data')
        re = integer_polynomial_product(ar,br,audit)
        result = [(x,0) for x in re]
    else:
        P = integer_polynomial_product(ar,br,audit)
        Q = integer_polynomial_product(ai,bi,audit)
        S = integer_polynomial_product([x+y for x,y in zip(ar,ai)],
                                      [x+y for x,y in zip(br,bi)],audit)
        result = [(p-q,s-p-q) for p,q,s in zip(P,Q,S)]
    if result!=direct_polynomial_product(A,B):
        raise AssertionError('complete Gaussian polynomial record product differs from direct negacyclic reference')
    return result


def packet(A,B,audit,real):
    if len(A)==1:
        return [encoded_gaussian_product(A[0],B[0],audit,real)],0
    half = len(A)//2
    a0,a1,b0,b1 = A[:half],A[half:],B[:half],B[half:]
    P,g = packet(a0,b0,audit,real)
    Q,h = packet(a1,b1,audit,real)
    S,k = packet([polynomial_add(x,y) for x,y in zip(a0,a1)],
                 [polynomial_add(x,y) for x,y in zip(b0,b1)],audit,real)
    if g!=h or g!=k:
        raise AssertionError('child product grids differ')
    return ([polynomial_add(s,polynomial_scale(q,-2)) for s,q in zip(S,Q)]+
            [polynomial_add(s,polynomial_scale(p,-2)) for s,p in zip(S,P)]),g+1


def tensor_direct(A,B):
    size = len(A)
    axes = size.bit_length()-1
    r = len(A[0])
    pairs = [[direct_polynomial_product(a,b) for b in B] for a in A]
    output = []
    for z in range(size):
        out = [(0,0)]*r
        for x in range(size):
            for y in range(size):
                sign = 1
                for j in range(axes):
                    sign *= SIGNS[z>>j&1][x>>j&1][y>>j&1]
                out = polynomial_add(out,polynomial_scale(pairs[x][y],sign))
        output.append(out)
    return output,axes


def transform(A,inverse=False):
    size = len(A)
    axes = size.bit_length()-1
    alpha,beta = ((1,-1),(1,1)) if inverse else ((1,1),(1,-1))
    values = [list(p) for p in A]
    for j in range(axes):
        for x in range(size):
            if x>>j&1:
                continue
            y = x^(1<<j)
            a,b = values[x],values[y]
            values[x] = [gaussian_add(gaussian_multiply(alpha,u),gaussian_multiply(beta,v)) for u,v in zip(a,b)]
            values[y] = [gaussian_add(gaussian_multiply(beta,u),gaussian_multiply(alpha,v)) for u,v in zip(a,b)]
    return values,axes


def literal(A,B):
    a,g = transform(A)
    b,h = transform(B)
    out,k = transform([direct_polynomial_product(x,y) for x,y in zip(a,b)],inverse=True)
    return out,g+h+k


def equal(A,g,B,h):
    grid = max(g,h)
    return [[(x << (grid-g),y << (grid-g)) for x,y in p] for p in A]==[
            [(x << (grid-h),y << (grid-h)) for x,y in p] for p in B]


def weak_carry_negative():
    # Deliberately omit the convolution growth guard: base16 cannot center
    # the middle coefficient27 of (3+3X+3X²)².
    values = [3,3,3]
    encoded = encode_signed(values,16)
    expected = [9,18,27,18,9]
    rejected = False
    try:
        decoded = decode_balanced(encoded*encoded,16,5)
        rejected = decoded!=expected
    except AssertionError:
        rejected = True
    if not rejected:
        raise AssertionError('insufficient carry guard negative was not rejected')
    return dict(base=16,correct_middle_coefficient=27,insufficient_guard_rejected=True)


def probe(task):
    axes,r,p,real = task
    size = 1 << axes
    seed = 202610090531+axes+r+p+int(real)
    randoms = Random(seed)
    limit = 1 << (p-1)
    def operand():
        return [[(randoms.randrange(-limit,limit),0 if real else randoms.randrange(-limit,limit)) for j in range(r)] for x in range(size)]
    A,B = operand(),operand()
    audit = dict(integer_products=0,maximum_radix_bits=0,maximum_product_operand_signed_bits=1,
                 maximum_integer_product_signed_bits=1,complete_decoded_real_coefficients=0,polynomial_leaf_products=0)
    output,g = packet(A,B,audit,real)
    direct,h = tensor_direct(A,B)
    actual,k = literal(A,B)
    if not equal(output,g,direct,h) or not equal(output,g,actual,k):
        raise AssertionError('fused complete polynomial packet disagrees with literal transform product')
    if audit['polynomial_leaf_products']!=3**axes or audit['integer_products']!=(1 if real else 3)*3**axes:
        raise AssertionError('complete integer product count differs from named packet')
    radix_bound = 2*(p+axes)+r.bit_length()+4
    operand_bound = r*radix_bound+2
    if audit['maximum_radix_bits']>radix_bound or audit['maximum_product_operand_signed_bits']>operand_bound:
        raise AssertionError('actual full integer operands exceed precision/packing bound')
    bad = weak_carry_negative()
    return dict(packet_axes=axes,orbit_records=size,polynomial_coefficients=r,component_signed_bits=p,
                real_operands=real,seed=seed,endpoint_fractional_bits=g,
                literal_transform_fractional_bits=k,complete_Gaussian_endpoint_fields=2*size*r,
                actual=audit,safe_radix_bits=radix_bound,safe_full_product_operand_bits=operand_bound,
                normalized_leaf_product_factor=dict(numerator=3**axes,denominator=2**axes),
                record_payload_bits_reference=2*r*p,
                complete_input_output_sha256=sha256(json.dumps([A,B,output]).encode()).hexdigest(),
                negative=bad,native_orbit_layout_supplied=False,improved_multiplier_oracle_used=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.workers<1:
        parser.error('positive workers required')
    source = sha256(Path(__file__).read_bytes()).hexdigest()
    started = time.monotonic()
    utc = datetime.now(timezone.utc).isoformat()
    tasks = [(1,3,3,False),(2,3,4,True)] if args.bounded else [(1,3,3,False),(2,5,8,True),(3,7,16,False),(4,3,4,False)]
    if args.workers==1:
        cases = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe,tasks))
    if sha256(Path(__file__).read_bytes()).hexdigest()!=source:
        raise AssertionError('source changed during run')
    result = dict(status='PASS EXACT PARTIAL POLYNOMIAL PRODUCT PACKETS',source_sha256=source,
                  started_utc=utc,completed_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
                  bounded=args.bounded,cases=cases,seconds=time.monotonic()-started,
                  scope='Complete signed-radix product and carry controls on Gaussian negacyclic polynomial records; not a paid native layout/dirty word, improved recursive multiplier or kappa.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(cases),integer_products=[c['actual']['integer_products'] for c in cases],seconds=result['seconds'])),flush=True)


if __name__=='__main__':
    main()
