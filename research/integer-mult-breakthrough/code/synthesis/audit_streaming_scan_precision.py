#!/usr/bin/env python3
"""Literal fixed-grid integer audit for the finite streaming boundary models.

The explicit dense repair has quadratic coordinate work and is a negative
cost control. Its correctness/precision does not certify a fast native repair.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time

import streaming_scan_boundary_preflight as s
p=s.p


def pipeline(original,events,required,f,grid):
    D=1<<f;N=6*D;fields=len(original[0]);peak=0;bit_peak=0;observations=0
    def observe(value):
        nonlocal peak,bit_peak,observations
        if not isinstance(value,int):raise ValueError('A physical integer register became fractional')
        peak=max(peak,abs(value));bit_peak=max(bit_peak,abs(value).bit_length());observations+=1
        return value
    def exact_divide(value,bits):
        observe(value);denominator=1<<bits
        if value%denominator:raise ValueError('The declared common grid lacks an exact division bit')
        return observe(value//denominator)
    M=[]
    for record in original:
        values=[]
        for z in record:
            row=[]
            for value in z:
                scaled=value*(1<<grid)
                if scaled.denominator!=1:raise ValueError('Original field is outside the common format')
                row.append(observe(scaled.numerator))
            values.append(tuple(row))
        M.append(values)
    for event in events:
        kind=event['kind']
        if kind=='add':
            source=event['source'];target=event['target'];c=event['coefficient']
            for a in range(D):
                M[target*D+a]=[tuple(observe(x+c*y) for x,y in zip(u,v)) for u,v in zip(M[target*D+a],M[source*D+a])]
        elif kind=='scan':
            addresses=range(D-1,0,-1) if event['difference'] else range(1,D)
            start=event['bank']*D;c=-1 if event['difference'] else 1
            for a in addresses:M[start+a]=[tuple(observe(x+c*y) for x,y in zip(u,v)) for u,v in zip(M[start+a],M[start+a-1])]
        elif kind=='cyclic_route':s.route_matrix(M,event,f,left=True)
        elif kind=='amplitude':
            for a in range(D):
                index=event['bank']*D+a;half=p.qvalue(a,f)^event['flip']
                M[index]=[tuple(exact_divide(x,1) if half else observe(2*x) for x in z) for z in M[index]]
        else:raise ValueError('Unknown literal physical event')
    pre_peak=bit_peak
    # Complete current-record C kernels, with every signed numerator prefix
    # observed before the exact physical divide, on all three Gaussian fields.
    core_numerators=0
    for bank in range(2,6):
        for bit in range(f):
            direction=1<<bit
            for a in range(D):
                if a&direction:continue
                i=bank*D+a;j=i+direction;left=[];right=[]
                for u,v in zip(M[i],M[j]):
                    expressions=((u[0],v[0],-u[1],v[1]),(u[1],v[1],u[0],-v[0]),
                                 (u[0],v[0],u[1],-v[1]),(u[1],v[1],-u[0],v[0]))
                    outputs=[]
                    for expression in expressions:
                        total=0
                        for operand in expression:total=observe(total+operand)
                        outputs.append(exact_divide(total,1));core_numerators+=1
                    left.append(tuple(outputs[:2]));right.append(tuple(outputs[2:]))
                M[i]=left;M[j]=right
    core_peak=bit_peak;post_input=[list(row) for row in M]
    coefficient_grid=p.ledger(required)['grid_bits'];coefficient_denominator=1<<coefficient_grid
    out=[];products=0;nonzero_coefficients=0
    for row in required:
        accum=[[0,0] for _ in range(fields)]
        for coefficient,record in zip(row,post_input):
            if coefficient==p.ZERO:continue
            real=coefficient[0]*coefficient_denominator;imag=coefficient[1]*coefficient_denominator
            if real.denominator!=1 or imag.denominator!=1:raise ValueError('The dense repair coefficient is not on its declared dyadic grid')
            real=real.numerator;imag=imag.numerator;nonzero_coefficients+=1
            for k,(a,b) in enumerate(record):
                aa=observe(real*a);bb=observe(imag*b);ba=observe(imag*a);ab=observe(real*b);products+=4
                re=exact_divide(observe(aa-bb),coefficient_grid)
                im=exact_divide(observe(ba+ab),coefficient_grid)
                accum[k][0]=observe(accum[k][0]+re);accum[k][1]=observe(accum[k][1]+im)
        out.append([tuple(z) for z in accum])
    return out,dict(common_grid_bits=grid,pre_register_bit_peak=pre_peak,core_register_bit_peak=core_peak,
                    all_register_bit_peak=bit_peak,signed_register_width_sufficient=bit_peak+1,
                    physical_magnitude_bit_allowance=max(0,bit_peak-grid),integer_register_observations=observations,
                    core_complex_numerators=core_numerators,dense_post_coefficient_grid_bits=coefficient_grid,
                    dense_post_nonzero_coefficients=nonzero_coefficients,integer_coefficient_products=products,
                    gaussian_fields_per_record=fields,all_divisions_exact=True,
                    cost_scope='Four integer coefficient products per nonzero matrix coefficient per Gaussian field. This is an explicitly dense negative implementation; generation, tape movement and bit multiplication remain paid.')


def probe(case):
    f,layout=case;started=time.monotonic();D=1<<f;N=6*D;events=s.word(f,layout)
    pre=p.identity(N);pre_guard=s.apply_word(pre,events,f,monitor=True)
    inverse=p.identity(N);s.apply_word(inverse,events,f,inverse=True)
    required=[list(row) for row in inverse]
    p.c_side(required,f,range(2,6),left=False,inverse=True);p.c_side(required,f,range(6),left=True)
    coefficient_grid=p.ledger(required)['grid_bits'];global_grid=2+pre_guard['grid_bits']+f+coefficient_grid
    rng=Random(921117+f+layout)
    original=[[(Q(rng.randrange(-10,11),4),Q(rng.randrange(-10,11),4)) for _ in range(3)] for _ in range(N)]
    actual,bill=pipeline(original,events,required,f,global_grid)
    expected=[list(row) for row in original];p.c_side(expected,f,range(6),left=True)
    for a,b in zip(actual,expected):
        for x,y in zip(a,b):
            if tuple(Q(v,1<<global_grid) for v in x)!=y:raise ValueError('Literal physical integer pipeline differs from the full target')
    rejected=False
    try:pipeline(original,events,required,f,2)
    except ValueError:rejected=True
    if not rejected:raise ValueError('Undercharged common input grid did not reject a physical half')
    return dict(status='PASS LITERAL STREAMING GRID AND DENSE COST CONTROL',selected_columns=f,layout=layout,
                physical_banks=6,operator_dimension=N,original_component_grid_bits=2,
                all_physical_records=N,all_gaussian_components=6*N,literal_integer_bill=bill,
                target_components_compared=6*N,complete_target_grid_bits=2+f,
                global_grid_kept_fixed=True,trailing_zeros_from_exact_endpoint=True,
                record_metadata=dict(bank_bits=3,address_bits=f,grid_descriptor_bits=8,
                    magnitude_descriptor='The explicit observed register width plus incoming allowance; no sampled overflow or normalization'),
                dense_post_operator_sha256=p.matrix_digest(required),seed=921117+f+layout,
                negative_controls={'undercharge_common_grid':'PHYSICAL EXACT DIVISION REJECTED'},
                asymptotic_scope='The maximum post row support is 4*2^f in the retained f2/f4 cases; some rows have fewer entries. A direct dense realization pays its actual nonzero coefficient products and provides no sublinear native boundary. No all-f density extrapolation or universal scan exclusion is claimed.',
                seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(s.__file__),Path(p.__file__)];hashes={source.name:sha256(source.read_bytes()).hexdigest() for source in sources}
    cases=[(2,0),(2,1),(4,0),(4,1)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,cases=cases,
                  source_sha256=hashes,stdlib_only=True,seed_rule='921117+selected_columns+layout',
                  hypothesis='Native prefix/difference prewords require complete fixed-grid and buffer guards; an exact dense repair remains a negative time control, not a supplier.',
                  resource_preflight={'maximum_operator_dimension':96,'expected_aggregate_memory_bytes_upper':128*1024*1024})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,case):case for case in cases}
        for future in as_completed(jobs):
            result=future.result();results.append(result)
            print(json.dumps({key:result[key] for key in ('status','selected_columns','layout','seconds')}|{'common_grid':result['literal_integer_bill']['common_grid_bits'],'integer_products':result['literal_integer_bill']['integer_coefficient_products']}),flush=True)
    if any(sha256(source.read_bytes()).hexdigest()!=hashes[source.name] for source in sources):raise ValueError('An effective source changed during physical precision audit')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__':main()
