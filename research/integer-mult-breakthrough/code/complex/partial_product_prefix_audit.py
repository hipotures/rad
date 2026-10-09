#!/usr/bin/env python3
"""Literal product-packet prefix, real-product and complete buffer audit.

The frozen partial algebra is used only as an exact endpoint reference.
Every source sum, three-real-product Gaussian leaf, decode and fixed-grid
multiplication temporary is counted. The array word does not supply orbit
layout, arbitrary dirty fields, native tape multiplication or an exponent.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time

import partial_kernel_product_algebra as reference

REFERENCE_SHA = '3e56ceb544baa77441c6371c248ddabe770769940e8c3dc32b6ac683a9393553'


class Audit:
    def __init__(self,axes,real):
        self.axes = axes
        self.real = real
        self.live = 0
        self.peak = 0
        self.observations = 0
        self.source_additions = 0
        self.decode_additions = 0
        self.Gaussian_products = 0
        self.real_products = 0
        self.max_operand_bits = 1
        self.maximum = {}
        self.fixed_grid_temporary_grid = 0

    def allocate(self,count):
        self.live += count
        self.peak = max(self.peak,self.live)

    def release(self,count):
        self.live -= count
        if self.live < 0:
            raise AssertionError('buffer word freed an unallocated coefficient')

    def observe(self,value,grid,stage):
        if grid < 0:
            raise AssertionError('negative fractional grid')
        bits = abs(value).bit_length()+1
        self.maximum[stage] = max(self.maximum.get(stage,1),bits)
        self.observations += 1
        if grid <= self.axes:
            common = bits+self.axes-grid
            self.maximum['complete_common_grid_numerator'] = max(
                self.maximum.get('complete_common_grid_numerator',1),common)
        else:
            self.fixed_grid_temporary_grid = max(self.fixed_grid_temporary_grid,grid)

    def observe_pair(self,pair,grid,stage):
        for value in pair:
            self.observe(value,grid,stage)

    def product(self,a,b):
        self.Gaussian_products += 1
        if self.real:
            if a[1] or b[1]:
                raise AssertionError('real-only leaf acquired an imaginary field')
            self.real_products += 1
            self.max_operand_bits = max(self.max_operand_bits,abs(a[0]).bit_length()+1,abs(b[0]).bit_length()+1)
            value = a[0]*b[0]
            self.observe(value,0,'leaf_real_product')
            self.observe(value << (2*self.axes),2*self.axes,'literal_fixed_grid_product')
            return value,0
        ar,ai = a
        br,bi = b
        sums = (ar+ai,br+bi)
        for value in sums:
            self.observe(value,0,'leaf_Karatsuba_operand_sum')
        for value in (ar,ai,br,bi,*sums):
            self.max_operand_bits = max(self.max_operand_bits,abs(value).bit_length()+1)
        p = ar*br
        q = ai*bi
        r = sums[0]*sums[1]
        self.real_products += 3
        for value in (p,q,r):
            self.observe(value,0,'leaf_real_product')
            # If physical operands are padded to common grid s, their
            # literal integer product has grid2s before exact zero removal.
            self.observe(value << (2*self.axes),2*self.axes,'literal_fixed_grid_product')
        real = p-q
        temp = r-p
        imag = temp-q
        for value in (real,temp,imag):
            self.observe(value,0,'leaf_Gaussian_recombination')
            self.observe(value << (2*self.axes),2*self.axes,'literal_fixed_grid_product_recombination')
        fixed = (real << self.axes,imag << self.axes)
        if any(value % (1 << self.axes) for value in fixed):
            raise AssertionError('declared fixed-grid zero removal is not exact')
        return real,imag


def plus(a,b,audit):
    value = a[0]+b[0],a[1]+b[1]
    audit.source_additions += 2
    audit.observe_pair(value,0,'source_linear_sum')
    return value


def recursive(A,B,audit):
    size = len(A)
    if size==1:
        out = [audit.product(A[0],B[0])]
        audit.allocate(1)
        return out,0
    half = size//2
    a0,a1,b0,b1 = A[:half],A[half:],B[:half],B[half:]
    audit.allocate(2*size)  # Four literal source slice buffers.
    P,g = recursive(a0,b0,audit)
    Q,h = recursive(a1,b1,audit)
    sumsA = [plus(x,y,audit) for x,y in zip(a0,a1)]
    sumsB = [plus(x,y,audit) for x,y in zip(b0,b1)]
    audit.allocate(size)
    S,k = recursive(sumsA,sumsB,audit)
    audit.release(size)
    if g!=h or g!=k:
        raise AssertionError('child fractional grids differ')
    lower,upper = [],[]
    for child,target in ((Q,lower),(P,upper)):
        for s,q in zip(S,child):
            doubled = 2*q[0],2*q[1]
            value = s[0]-doubled[0],s[1]-doubled[1]
            audit.decode_additions += 2
            audit.observe_pair(doubled,g,'decode_double')
            audit.observe_pair(value,g,'decode_before_halving')
            audit.observe_pair(value,g+1,'decode_output')
            target.append(value)
    audit.allocate(size)  # Lower and upper temporary lists.
    out = lower+upper
    audit.allocate(size)  # Literal final concatenation is a second buffer.
    audit.release(size)
    audit.release(len(P)+len(Q)+len(S))
    audit.release(2*size)
    return out,g+1


def probe(task):
    axes,width,real = task
    size = 1 << axes
    seed = 202610090525+axes+width+int(real)
    randoms = Random(seed)
    limit = 1 << (width-1)
    A = [(randoms.randrange(-limit,limit),0 if real else randoms.randrange(-limit,limit)) for _ in range(size)]
    B = [(randoms.randrange(-limit,limit),0 if real else randoms.randrange(-limit,limit)) for _ in range(size)]
    audit = Audit(axes,real)
    audit.allocate(2*size)
    for value in A+B:
        audit.observe_pair(value,0,'input')
    output,grid = recursive(A,B,audit)
    direct,g = reference.q_direct(A,B)
    literal,h = reference.q_literal(A,B)
    if output!=direct or grid!=g or not reference.equal(output,grid,literal,h):
        raise AssertionError('instrumented product word differs from exact tensor/reference')
    if audit.live!=3*size:
        raise AssertionError('complete input/output buffer endpoints are not retained')
    if audit.peak!=10*size-5:
        raise AssertionError('literal slice/concatenate buffer recurrence differs from10D-5')
    if audit.Gaussian_products!=3**axes or audit.real_products!=(1 if real else 3)*3**axes:
        raise AssertionError('actual signed scalar product count differs from named packet word')
    if audit.max_operand_bits>width+axes+2:
        raise AssertionError('leaf operand precision exceeded source-sum bound')
    dynamic_bound=2*width+4*axes+4
    fixed_bound=2*width+5*axes+4
    for stage,bits in audit.maximum.items():
        bound=fixed_bound if stage.startswith('literal_fixed') or stage=='complete_common_grid_numerator' else dynamic_bound
        if bits>bound:
            raise AssertionError('a literal multiplication/decode prefix exceeded its complete guard')
    if audit.fixed_grid_temporary_grid!=2*axes:
        raise AssertionError('fixed-grid multiplication temporary charge omitted')
    # A generic Gaussian packet may not reuse the cheaper real-only product.
    real_rejected=False
    if not real:
        try:
            Audit(axes,True).product((1,1),(1,0))
        except AssertionError:
            real_rejected=True
        if not real_rejected:
            raise AssertionError('real-only product negative failed to reject')
    return dict(packet_axes=axes,coefficient_count=size,input_component_signed_bits=width,
                real_operands=real,seed=seed,endpoint_fields=2*size,
                Gaussian_leaf_products=audit.Gaussian_products,signed_real_products=audit.real_products,
                actual_max_signed_product_operand_bits=audit.max_operand_bits,
                safe_signed_product_operand_bits=width+axes+2,
                complete_prefix_observations=audit.observations,
                actual_prefix_bits=audit.maximum,
                safe_dynamic_numerator_bits=dynamic_bound,safe_fixed_numerator_bits=fixed_bound,
                endpoint_fractional_grid=grid,largest_fixed_multiplication_temporary_grid=2*axes,
                literal_peak_Gaussian_coefficient_buffers=audit.peak,
                complete_input_output_buffer_endpoint=3*size,
                source_component_additions=audit.source_additions,decode_component_additions=audit.decode_additions,
                normalized_product_factor=dict(numerator=3**axes,denominator=2**axes),
                no_orbit_layout_supplied=True,no_arbitrary_dirty_bank_contract=True,
                generic_real_only_negative_rejected=real_rejected if not real else None)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.workers<1:
        parser.error('positive worker count required')
    source=Path(__file__).resolve()
    imported=Path(reference.__file__).resolve()
    pins={str(p):sha256(p.read_bytes()).hexdigest() for p in (source,imported)}
    if pins[str(imported)]!=REFERENCE_SHA:
        raise AssertionError('frozen exact algebra reference changed')
    started=time.monotonic()
    utc=datetime.now(timezone.utc).isoformat()
    tasks=[(1,2,True),(2,3,False)] if args.bounded else [(1,4,True),(2,8,False),(4,16,True),(6,32,False)]
    if args.workers==1:
        cases=[probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases=list(pool.map(probe,tasks))
    if any(sha256(Path(p).read_bytes()).hexdigest()!=value for p,value in pins.items()):
        raise AssertionError('source closure changed during audit')
    result=dict(status='PASS LITERAL PARTIAL PRODUCT PREFIX AND BUFFER AUDIT',started_utc=utc,
                completed_utc=datetime.now(timezone.utc).isoformat(),source_sha256=pins[str(source)],
                exact_reference_sha256=pins[str(imported)],workers=args.workers,bounded=args.bounded,
                cases=cases,seconds=time.monotonic()-started,
                scope='Exact array-word prefix, product operands and buffer charges. Paid orbit layout, fixed-tape multiplication, arbitrary dirty banks, full coupled recurrence and kappa remain open.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(cases),products=[c['signed_real_products'] for c in cases],seconds=result['seconds'])),flush=True)


if __name__=='__main__':
    main()
