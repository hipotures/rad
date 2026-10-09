#!/usr/bin/env python3
"""Bounded exact cyclic-core checks, including signed guards and dirty zeros."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path

import finite_field_cyclic_reduction as f


def verify():
    receipt=f.probe(3)
    geo=f.geometry(3)
    zero=[f.g.ZERO]*geo['d']
    for normalization in ('late','early'):
        actual,records=f.full_word(zero,zero,zero,geo,normalization)
        if actual!=(zero,zero,zero) or any(r['peak']['maximum_real_or_imaginary_component']!='0' for r in records):
            raise ValueError('All-zero instrumentation regression failed')
    values=[f.Q(-17,8),f.Q(9,4),f.Q(0),f.Q(-5,2),f.Q(3,8),f.Q(-1),f.Q(27,8)]
    components=[(x,f.Q(-i,16)) for i,x in enumerate(values)]
    actual,interface=f.convolution(components,geo)
    if actual!=f.direct_core(components,geo):raise ValueError('Signed Gaussian convolution does not match exact cyclic sums')
    # An intentionally insufficient radix cannot certify these coefficients.
    try:f.packed_component([128]*7,[1]*7,1)
    except ValueError as error:
        if 'overflowed' not in str(error):raise
    else:raise ValueError('Insufficient signed radix guard was not rejected')
    # The positive data word includes independent zero-coordinate source,
    # sink and dirty columns; a corrupted field generator is not a permutation.
    previous=f.PRIMITIVE[3]
    f.PRIMITIVE[3]=0b1001
    try:
        try:f.geometry(3)
        except ValueError as error:
            if 'Primitive polynomial/generator' not in str(error):raise
        else:raise ValueError('Invalid field enumeration was not rejected')
    finally:f.PRIMITIVE[3]=previous
    return dict(status='PASS EXACT FIELD CYCLIC CORE',recorded_utc=datetime.now(timezone.utc).isoformat(),
                complete_word=receipt,signed_component_interface=interface,
                zero_peak_regression=True,insufficient_guard_detected=True,invalid_field_detected=True,
                scope='Complete bounded Gaussian source/sink/dirty word and explicit integer product guards. Native fixed-tape routing, cost, approximation guard and asymptotic exponent remain unproved.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);args=p.parse_args()
    result=verify();files=[Path(__file__),Path(f.__file__),Path(f.g.__file__),Path(f.__file__).with_name('lagrangian_graph_completion.py')]
    result['source_sha256']={p.name:sha256(p.read_bytes()).hexdigest() for p in files}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],column_checks=result['complete_word']['complete_column_direction_checks'],
                         zero_peak_regression=True,insufficient_guard_detected=True,invalid_field_detected=True)))


if __name__=='__main__':main()
