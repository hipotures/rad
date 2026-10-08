#!/usr/bin/env python3
"""Exact signed mixed-radix tensor convolution, with no axis binary padding.

The Python integer backend validates the finite identity only. Its runtime is
not evidence for the conditional multitape multiplication cost used in a proof.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import reduce
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import random
import time


def strides(shape):
    return [math.prod(shape[i+1:]) for i in range(len(shape))]


def encode(values,shape,padded_shape,width):
    size=math.prod(padded_shape);ps=strides(padded_shape)
    positive=bytearray(size*width);negative=bytearray(size*width)
    for x,value in zip(product(*(range(n) for n in shape)),values):
        if value:
            offset=width*sum(a*b for a,b in zip(x,ps))
            target=positive if value>0 else negative
            target[offset:offset+width]=abs(value).to_bytes(width,'little')
    return int.from_bytes(positive,'little'),int.from_bytes(negative,'little')


def direct(values,shape,kernels):
    values=list(values);shape=list(shape)
    for axis,kernel in enumerate(kernels):
        old=shape[axis];suffix=math.prod(shape[axis+1:]);prefix=math.prod(shape[:axis])
        changed=old+len(kernel)-1;out=[0]*(prefix*changed*suffix)
        for p in range(prefix):
            for x in range(old):
                for k,coefficient in enumerate(kernel):
                    if not coefficient:continue
                    source=(p*old+x)*suffix;target=(p*changed+x+k)*suffix
                    for y in range(suffix):out[target+y]+=coefficient*values[source+y]
        values=out;shape[axis]=changed
    return values,shape


def case(job):
    dimension,side,radius,seed,output=job
    start=time.monotonic();rng=random.Random(seed)
    shape=[side]*dimension;kernel_shape=[2*radius+1]*dimension
    padded=[side+2*radius]*dimension
    values=[rng.randrange(-7,8) for _ in range(side**dimension)]
    kernels=[]
    for axis in range(dimension):
        # Alternating signs exercise the inverse-kernel encoding path.
        kernels.append([(-1 if (j+axis)%2 else 1)*(1+(j+axis)%3) for j in range(2*radius+1)])
    kernel_values=[math.prod(kernels[i][x[i]] for i in range(dimension))
                   for x in product(*(range(n) for n in kernel_shape))]
    bound=7*math.prod(sum(map(abs,k)) for k in kernels)
    width=max(1,(bound.bit_length()+7)//8)
    assert 256**width>bound
    ip,im=encode(values,shape,padded,width)
    kp,km=encode(kernel_values,kernel_shape,padded,width)
    total=math.prod(padded);length=total*width
    products=[(ip*kp).to_bytes(length,'little'),(im*km).to_bytes(length,'little'),
              (ip*km).to_bytes(length,'little'),(im*kp).to_bytes(length,'little')]
    actual=[]
    for offset in range(0,length,width):
        digits=[int.from_bytes(p[offset:offset+width],'little') for p in products]
        actual.append(digits[0]+digits[1]-digits[2]-digits[3])
    expected,out_shape=direct(values,shape,kernels)
    assert out_shape==padded and actual==expected
    # Full tensor product and padding have exact non-power-of-two dimensions.
    coefficients=total
    digest=hashlib.sha256(','.join(map(str,actual)).encode()).hexdigest()
    receipt={'dimension':dimension,'side':side,'radius':radius,'seed':seed,
             'input_records':len(values),'padded_records':total,
             'padded_shape':padded,'checked_signed_coefficients':coefficients,
             'coefficient_absolute_bound':bound,'coefficient_bytes':width,
             'four_integer_products':True,'padding_ratio':f'{total}/{side**dimension}',
             'result_sha256':digest,'elapsed_seconds':time.monotonic()-start,
             'negative_padding_comparison':{'per_axis_next_power_of_two':2**dimension,
                 'explanation':'The implementation uses exactly side+2R and never rounds every axis to2side.'}}
    path=Path(output)/f'd{dimension}-side{side}-r{radius}-seed{seed}.json'
    path.write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=7);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    shapes=[(2,64,2),(3,28,2),(4,12,2),(5,8,1),(6,8,1),(4,20,1),
            (3,40,2),(2,128,3),(5,6,2),(6,6,1),(4,24,1),(3,64,3)]
    jobs=[(*s,20261008+i,str(args.output.resolve())) for i,s in enumerate(shapes)]
    start=time.monotonic();receipts=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed(pool.submit(case,j) for j in jobs):
            r=future.result();receipts.append(r)
            print(json.dumps({k:r[k] for k in ['dimension','side','radius','checked_signed_coefficients','elapsed_seconds']}),flush=True)
    output={'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'status':'Exact signed Kronecker coefficient equality on all declared cases',
            'workers':args.workers,'elapsed_seconds':time.monotonic()-start,
            'checked_signed_coefficients':sum(r['checked_signed_coefficients'] for r in receipts),
            'integer_products':4*len(receipts),'cases':sorted(receipts,key=lambda r:(r['dimension'],r['side'],r['radius'])),
            'scope':'Finite local convolution only; Gaussian kernel generation, dense resampling movement, sparse repair and all-size precision are separate proof obligations.'}
    (args.output/'certificate.json').write_text(json.dumps(output,indent=2)+'\n')


if __name__=='__main__':main()
