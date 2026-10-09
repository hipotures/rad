#!/usr/bin/env python3
"""Rational complete supplier moments after actual terminal-sink deletion.

RaD; GPT-6.1 Sol assistance. Apache-2.0. Uses the unchanged independently
authored rational kernel. Literal geometry and scalar correctness must be
certified separately; this checker verifies profile accounting and moments.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)


def need(condition,message):
    if not condition:raise ValueError(message)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--export',type=Path,required=True)
    p.add_argument('--body-export',type=Path,required=True)
    p.add_argument('--interval-code',type=Path,required=True)
    p.add_argument('--saving',type=Fraction,action='append',required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();need(not sys.flags.optimize,'assertion-disabled execution rejected');start=time.monotonic()
    protocol=json.loads((a.export/'protocol.json').read_text())
    for filename,pin in protocol['input_pins'].items():
        need(sha256((a.export/filename).read_bytes()).hexdigest()==pin['sha256'],'finite input pin: '+filename)
    paid=json.loads((a.export/'profile.json').read_text());row=json.loads((a.body_export/'profile-before.json').read_text())
    body_protocol=json.loads((a.body_export/'protocol.json').read_text())
    need(body_protocol['input_pins']==protocol['body_input_pins'],'coherent body inputs')
    for filename,pin in body_protocol['input_pins'].items():
        need(sha256((a.body_export/filename).read_bytes()).hexdigest()==pin['sha256'],'body input pin '+filename)
    pairs=json.loads((a.body_export/'physical-pairs.json').read_text())
    children=Counter()
    for part in ('local_histogram','source_data_histogram','target_data_histogram'):
        children.update({int(r):3*n for r,n in paid[part].items() if int(r) and n})
    children.update({3*int(r):n for r,n in paid['physical_gauge_histogram'].items() if int(r) and n})
    children[2]+=2*paid['v']
    need(dict(children)=={int(r):n for r,n in paid['child_histogram'].items() if int(r) and n},'complete histogram')
    mass=sum(r*n for r,n in children.items());m,W=paid['m'],paid['W_per_vertex']
    need(m==3*paid['h'] and W==2*paid['v']+paid['physical_R'],'local dimensions')
    need(paid['physical_R']==row['R']-len(pairs)-paid['sinks'] and len(pairs)==paid['pairs'],'logical/physical stock')
    need(m*W-mass==paid['deficit_per_vertex']==2*paid['v']-3*paid['loss'],'complete rank deficit')
    need(all(0<r<m and n>0 for r,n in children.items()),'proper positive children')
    spec=importlib.util.spec_from_file_location('rad_frozen_intervals',a.interval_code)
    intervals=importlib.util.module_from_spec(spec);spec.loader.exec_module(intervals)
    trials=[]
    for saving in a.saving:
        lower,upper=intervals.moment(m,W,dict(children),saving)
        trials.append(dict(saving=str(saving),lower=str(lower),upper=str(upper),
                           lower_decimal=float(lower),upper_decimal=float(upper),
                           classification='ACCEPTED' if upper<1 else 'REJECTED' if lower>1 else 'UNRESOLVED',
                           accepted_gap_lower=str(1-upper),rejected_excess_lower=str(lower-1)))
    lo,hi=0.,.01
    for _ in range(70):
        middle=(lo+hi)/2
        value=math.fsum(n*r*math.exp(middle*math.log(m/r)) for r,n in children.items())/(m*W)
        if value<1:lo=middle
        else:hi=middle
    grid=math.floor(lo*10**12);low,high=Fraction(grid,10**12),Fraction(grid+1,10**12)
    _,low_upper=intervals.moment(m,W,dict(children),low);high_lower,_=intervals.moment(m,W,dict(children),high)
    need(low_upper<1<high_lower,'root grid unresolved')
    result=dict(status='EXACT_RATIONAL_COMPLETE_FINITE_SUPPLIER',m=m,W=W,mass=mass,deficit=m*W-mass,
                complete_children=dict(children),trials=trials,root_grid_lower=str(low),root_grid_upper=str(high),
                accepted_root_gap_lower=str(1-low_upper),rejected_root_excess_lower=str(high_lower-1),
                input_pins=protocol['input_pins'],body_input_pins=body_protocol['input_pins'],sinks=paid['sinks'],interval_source_sha256=sha256(a.interval_code.read_bytes()).hexdigest(),
                driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),elapsed_seconds=time.monotonic()-start,
                scope='Independently reconstructs the complete finite inventory from all paid parts and rigorously '
                      'encloses moments using rational logarithm/exponential tails and outward rounding. Literal '
                      'signed arbitrary-dirty scalar core, complemented geometry and all-size assembly are separate. '
                      'No binary supplier or final integer multiplication exponent is claimed.')
    with a.output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print('PASS exact complete moment root (%s,%s)'%(low,high))
    for trial in trials:print(trial['saving']+': '+trial['classification'])


if __name__=='__main__':main()
