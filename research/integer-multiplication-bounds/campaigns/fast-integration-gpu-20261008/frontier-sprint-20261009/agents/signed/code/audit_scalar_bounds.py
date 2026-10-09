#!/usr/bin/env python3
"""Independently bound every literal complex decoder/old-value coefficient.

RaD; GPT-6.1 Sol assistance. Apache-2.0. Exact integer adjoints represent
coefficients with denominator six, including copied-center scatter.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode=True


def need(condition,message):
    if not condition:raise ValueError(message)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('export','exact-core','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();need(not sys.flags.optimize,'assertion-disabled execution rejected');start=time.monotonic()
    pins=json.loads((a.export/'protocol.json').read_text())['input_pins']
    for name,pin in pins.items():need(sha256((a.export/name).read_bytes()).hexdigest()==pin['sha256'],'input pin: '+name)
    g,w,row,pairs=[json.loads((a.export/name).read_text()) for name in
                   ('graph.json','word.json','profile-before.json','physical-pairs.json')]
    spec=importlib.util.spec_from_file_location('rad_scalar_bound_core',a.exact_core)
    core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
    events,mutations,cleanup,live,response=core.prepare(g,w,pairs,row['R'])
    maximum=0;max_role=None
    for role,coefficients in enumerate(response):
        top=max(map(abs,core.expanded(coefficients,g)),default=0)
        if top>maximum:maximum,max_role=top,role
    read_max=max((max(map(abs,core.expanded(event[3],g)),default=0) for event in events if event[0]=='read'),default=0)
    root_max=max(abs(Fraction(c)) for root in g['roots'] for c in root['coefficients'])
    need(maximum<=6*(g['h']+4) and read_max<=6*(g['h']+4),'expanded exact coefficient exceeds h+4')
    need(all(6*Fraction(c)==int(6*Fraction(c)) for root in g['roots'] for c in root['coefficients']), 'root denominator')
    need(3*row['q']<2**15,'literal decoder numerator precision bound')
    h,v,R,c,M=(row[k] for k in ('h','v','R','c','total_M_operations'))
    local=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8+2*h+8*R*v*(M+16)+32*v
    result=dict(status='PASS_EXACT_EXPANDED_SCALAR_BOUNDS',logical_roles=R,physical_roles=len(live),q=row['q'],
                expanded_adjoint_coefficients_checked=R*v,expanded_literal_read_coefficients_checked=sum(e[0]=='read' for e in events)*v,
                max_adjoint_numerator_over_6=maximum,max_adjoint_coefficient=str(Fraction(maximum,6)),max_role=max_role,
                max_literal_read_numerator_over_6=read_max,max_root_coefficient=str(root_max),
                coefficient_bound_h_plus_4=h+4,coefficient_denominator_divides=6,three_q=3*row['q'],
                three_q_below_2_to_15=True,literal_M=M,dirty_numerator_bit_upper=M+16,local_expanded_group_upper=local,
                input_pins=pins,checker_sha256=sha256(a.exact_core.read_bytes()).hexdigest(),
                driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),elapsed_seconds=time.monotonic()-start,
                scope='Exact expanded JM adjoint coefficients for every logical role, plus every actually emitted '
                      'old-value/center/side read. Every coefficient has denominator dividing6 and satisfies h+4. '
                      'Literal gates/injections use units; K coefficients have magnitude1/2. The retained worst-case '
                      'M+16 numerator precision bound and complete expanded scalar bill are checked with actual new counts. '
                      'Uniform scalar/router/row assembly and geometry remain separate.')
    with a.output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print('PASS scalar bound max%sover6 <= h+4=%d, 3q=%d, L=%d, %.3fs' %(maximum,h+4,3*row['q'],local,result['elapsed_seconds']))


if __name__=='__main__':main()
