#!/usr/bin/env python3
"""Exact slice/support controls for all-rank partial-product decompositions.

All basis input and output slices of q_s have full rankD. A separable
rank-one scalar product word therefore has at leastD^2 nonzero coefficients
on each of its two input-form and output-vector sides. This is a direct/depth2
wire boundary, not a time bound on shared or layered native circuits.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import time


LOCAL_W = ((0,-2,1),(-2,0,1))


def coefficient(z,x,y,mask):
    return -1 if ((x&y).bit_count()+(z&(mask^(x^y))).bit_count())&1 else 1


def row_masks(rows):
    return [sum(1<<j for j,x in enumerate(row) if x==-1) for row in rows]


def gram_identity(rows):
    D = len(rows)
    packed = row_masks(rows)
    return all(D-2*(a^b).bit_count()==(D if i==j else 0)
               for i,a in enumerate(packed) for j,b in enumerate(packed))


def input_support(choices,D):
    return [x for x in range(D) if all(c==2 or (x>>j&1)==c for j,c in enumerate(choices))]


def output_support(choices,D):
    return [z for z in range(D) if all(c==2 or (z>>j&1)==(1-c) for j,c in enumerate(choices))]


def local_identity():
    for z,x,y in product(range(2),repeat=3):
        value = 0
        for k in range(3):
            u = int(k==2 or x==k)
            v = int(k==2 or y==k)
            value += LOCAL_W[z][k]*u*v
        if value!=coefficient(z,x,y,1):
            raise AssertionError('local three-product tensor coefficient identity failed')


def probe(s):
    D = 1 << s
    mask = D-1
    source_checks = 0
    output_checks = 0
    for coordinate in range(D):
        source = [[coefficient(z,coordinate,y,mask) for y in range(D)] for z in range(D)]
        output = [[coefficient(coordinate,x,y,mask) for y in range(D)] for x in range(D)]
        if not gram_identity(source) or not gram_identity(output):
            raise AssertionError('an exact product basis slice lost its Hadamard Gram/rank')
        source_checks += D*D
        output_checks += D*D
        if any(coefficient(z,coordinate,y,mask)!=coefficient(z,y,coordinate,mask)
               for z in range(D) for y in range(D)):
            raise AssertionError('the two input-slice families lost tensor symmetry')
    source = [[coefficient(z,0,y,mask) for y in range(D)] for z in range(D)]
    source[0][0] *= -1
    if gram_identity(source):
        raise AssertionError('one-entry slice corruption negative did not reject')
    incidence_in = [0]*D
    incidence_out = [0]*D
    wire_in = 0
    wire_out = 0
    support_histogram = {}
    for choices in product(range(3),repeat=s):
        incoming = input_support(choices,D)
        outgoing = output_support(choices,D)
        expected = 1 << choices.count(2)
        if len(incoming)!=expected or len(outgoing)!=expected:
            raise AssertionError('tensor product-form supports have an incorrect size')
        wire_in += len(incoming)
        wire_out += len(outgoing)
        support_histogram[str(expected)] = support_histogram.get(str(expected),0)+1
        for x in incoming:
            incidence_in[x] += 1
        for z in outgoing:
            incidence_out[z] += 1
    if wire_in!=D*D or wire_out!=D*D or incidence_in!=[D]*D or incidence_out!=[D]*D:
        raise AssertionError('named three-product word does not attain the coordinate slice wire floors')
    return dict(packet_axes=s,dimension=D,source_slice_Gram_entries=source_checks,
                output_slice_Gram_entries=output_checks,
                both_input_families_bound_by_exact_symmetry=True,
                raw_slice_Gram='D I',raw_structure_grid_bits=s,
                scalar_product_terms=3**s,source_U_wires=wire_in,source_V_wires=wire_in,
                output_W_wires=wire_out,coordinate_product_incidence=D,
                product_support_histogram=support_histogram,
                average_input_output_support=dict(numerator=4**s,denominator=3**s),
                one_entry_corruption_rejected=True,
                scope='Complete finite basis-slice and named tensor form-support controls. Arbitrary separable decomposition lower bound is analytical; shared/layered circuit time and nonhomomorphic or record-algebra products remain outside.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.workers<1:
        parser.error('positive workers required')
    source=sha256(Path(__file__).read_bytes()).hexdigest()
    utc=datetime.now(timezone.utc).isoformat()
    started=time.monotonic()
    local_identity()
    tasks=[1,2] if args.bounded else [1,2,4,6]
    if args.workers==1:
        cases=[probe(s) for s in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases=list(pool.map(probe,tasks))
    if sha256(Path(__file__).read_bytes()).hexdigest()!=source:
        raise AssertionError('source changed during run')
    result=dict(status='PASS EXACT ALL-RANK PRODUCT SLICE/WIRE CONTROLS',source_sha256=source,
                started_utc=utc,completed_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
                bounded=args.bounded,cases=cases,seconds=time.monotonic()-started,
                scope='Product-tensor slice ranks and direct/depth2 form-incidence floor, not a general time bound, native compiler or kappa.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(cases),Gram_entries=sum(c['source_slice_Gram_entries']+c['output_slice_Gram_entries'] for c in cases),seconds=result['seconds'])),flush=True)


if __name__=='__main__':
    main()
