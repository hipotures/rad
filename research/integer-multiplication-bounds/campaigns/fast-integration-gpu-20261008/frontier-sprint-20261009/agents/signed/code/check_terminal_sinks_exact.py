#!/usr/bin/env python3
"""Exact integer adjoint of every emitted terminal-sink stage event.

RaD; GPT-6.1 Sol assistance; Apache-2.0. Native modular field encodings are
decoded only against the literal unit/half coefficients prescribed by the
construction. Identity is established by integer coefficient propagation,
not field arithmetic or random vectors. Symbolic centers are expanded exactly.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
P = (1 << 61)-1
HALF = (P+1)//2
DEN = 12


def need(condition,message):
    if not condition:
        raise ValueError(message)


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def half(value):
    need(value in (HALF,P-HALF),'unrecognized literal half coefficient')
    return 1 if value == HALF else -1


def add_div(core,dst,src,numerator=1,denominator=1):
    for key,value in src.items():
        need((value*numerator)%denominator == 0,'nonintegral common-denominator coefficient')
        term=value*numerator//denominator
        new=dst.get(key,0)+term
        if new:
            dst[key]=new
        else:
            dst.pop(key,None)


def check(graph,word,pairs,row,registers,events,core,direction,mutation=None):
    v=graph['v']
    removed=set(registers['removed'])
    slots=registers['body_live']
    slot={int(role):index for role,index in registers['body_slot'].items()}
    count=2*v+len(slots)
    target_bank='Y' if direction == 1 else 'X'
    target_offset=v if target_bank == 'Y' else 0
    adj=[{} for _ in range(count)]
    for target in range(v):
        adj[target_offset+target]={target:DEN}
    _,_,_,_,response=core.prepare(graph,word,pairs,row['R'])
    root_response={}
    for root,role in zip(graph['roots'],word['rootroles']):
        if root['kind'] == 'center':
            root_response[role]={-1-root['coordinate']:1}
        else:
            root_response[role]={target:3 if coefficient == '1/2' else -3
                                 for target,coefficient in zip(root['targets'],root['coefficients'])}
    event_list=list(events)
    if mutation == 'omit_post':
        index=next(i for i,e in enumerate(event_list) if e[0] == 'ysh' and e[3] == 1)
        event_list.pop(index)
    elif mutation == 'bad_pivot_sign':
        index=next(i for i,e in enumerate(event_list) if e[0] == 'yw')
        bad=list(event_list[index]);bad[3]=(P-bad[3])%P;event_list[index]=bad
    elif mutation == 'bad_k_coefficient':
        index=next(i for i,e in enumerate(event_list) if e[0] == 'ktr')
        bad=json.loads(json.dumps(event_list[index]));bad[2][0][0]=(P-bad[2][0][0])%P;event_list[index]=bad
    elif mutation is not None:
        raise ValueError('unknown negative control')
    max_primitive=Fraction(0)
    for event in reversed(event_list):
        kind=event[0]
        if kind in ('op','inj','ysh','kd'):
            _,dst,src,coefficient,*rest=event
            need(dst != src and dst not in removed and src not in removed,'invalid literal registers')
            need(coefficient in (-1,1),'nonunit literal shear')
            add_div(core,adj[src],adj[dst],coefficient)
            max_primitive=max(max_primitive,Fraction(abs(coefficient)))
        elif kind == 'yw':
            _,dst,src,coefficient,*rest=event
            need(dst != src and dst not in removed and src not in removed,'invalid pivot write registers')
            add_div(core,adj[src],adj[dst],half(coefficient),2)
            max_primitive=max(max_primitive,Fraction(1,2))
        elif kind in ('read','centre'):
            if kind == 'read':
                _,register,role,sign,mode,frame,bank,targets=event
                coefficients=response[role] if mode == 'resp' else root_response[role]
            else:
                _,register,role,sign,frame,zero,bank=event
                coefficients=root_response[role]
            need(register not in removed and sign in (-1,1),'invalid read register/sign')
            offset=v if bank == 'Y' else 0
            centers={key:value for key,value in coefficients.items() if key<0 and value}
            if centers:
                identity=all(adj[offset+t] == {t:DEN} for t in range(v))
                if identity:
                    for key,value in centers.items():
                        new=adj[register].get(key,0)+2*sign*value
                        if new:adj[register][key]=new
                        else:adj[register].pop(key,None)
                else:
                    # This branch supports a center read during a target coupling;
                    # it is expanded instead of assuming center closure.
                    expanded=core.expanded(centers,graph)
                    for target,value in enumerate(expanded):
                        if value:add_div(core,adj[register],adj[offset+target],sign*value,6)
            for target,value in coefficients.items():
                if target>=0 and value:
                    add_div(core,adj[register],adj[offset+target],sign*value,6)
            if coefficients:
                expanded=core.expanded(coefficients,graph)
                max_primitive=max(max_primitive,Fraction(max(map(abs,expanded)),6))
        elif kind == 'ktr':
            _,ports,matrix,*rest=event
            need(len(ports) == len(set(ports)) == 4,'four distinct K ports')
            before=[adj[port] for port in ports]
            after=[{} for _ in ports]
            for input_index in range(4):
                for output_index in range(4):
                    add_div(core,after[input_index],before[output_index],half(matrix[output_index][input_index]),2)
            for port,value in zip(ports,after):
                adj[port]=value
        else:
            raise ValueError('unknown literal event '+kind)
    for target in range(v):
        x=core.expanded(adj[target],graph)
        y=core.expanded(adj[v+target],graph)
        expected_x=DEN if direction == 1 else DEN
        expected_y=DEN if direction == 1 else -DEN
        if direction == 1:
            need(all(value == (DEN if output == target else 0) for output,value in enumerate(x)),
                 'forward source coefficient mismatch '+str(target))
            need(all(value == (DEN if output == target else 0) for output,value in enumerate(y)),
                 'forward target spectator mismatch '+str(target))
        else:
            need(all(value == (DEN if output == target else 0) for output,value in enumerate(x)),
                 'reflected target spectator mismatch '+str(target))
            need(all(value == (-DEN if output == target else 0) for output,value in enumerate(y)),
                 'reflected source coefficient mismatch '+str(target))
    checked=0
    for index,role in enumerate(slots):
        register=2*v+index
        if register in removed:
            need(not adj[register],'deleted sink still read')
            continue
        need(not adj[register] or not any(core.expanded(adj[register],graph)),
             'nonzero arbitrary dirty coefficient '+str(role))
        checked+=v
    need(max_primitive <= graph['h']+4,'primitive coefficient bound')
    return dict(direction=direction,source_coefficients=v*v,target_spectator_coefficients=v*v,
                arbitrary_dirty_coefficients=checked,physical_slots=len(slots)-len(removed),
                all_coefficients_exact=True,integer_common_denominator=DEN,
                max_literal_primitive_coefficient=str(max_primitive),events=len(event_list))


def cleanup_and_k(events,removed):
    """All retained scratch mutations are literal inverses; K restores its ports."""
    mutations=[event for event in events if event[0] in ('op','inj')]
    need(len(mutations)%2 == 0,'paired scratch mutation count')
    middle=len(mutations)//2
    for event,inverse in zip(mutations[:middle],reversed(mutations[middle:])):
        need(event[0] == inverse[0] and event[1:3] == inverse[1:3] and event[3] == -inverse[3],
             'literal scratch inverse mismatch')
        need(event[1] not in removed and event[2] not in removed,'deleted sink cleanup retained')
    transforms=[event for event in events if event[0] == 'ktr']
    need(len(transforms)%2 == 0,'paired K transforms')
    for forward,inverse in zip(transforms[::2],transforms[1::2]):
        need(forward[1] == inverse[1],'K port inverse binding')
        a=[[half(value) for value in row] for row in forward[2]]
        b=[[half(value) for value in row] for row in inverse[2]]
        need(all(sum(b[i][k]*a[k][j] for k in range(4)) == 4*(i==j)
                 for i in range(4) for j in range(4)),'exact K inverse product')
    return dict(retained_scratch_mutations=middle,literal_inverse_cleanup=True,K_inverse_blocks=len(transforms)//2)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('body-export','sink-export','exact-core','output'):
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    need(not sys.flags.optimize,'assertion-disabled execution rejected')
    start=time.monotonic()
    body_protocol=json.loads((a.body_export/'protocol.json').read_text())
    sink_protocol=json.loads((a.sink_export/'protocol.json').read_text())
    need(body_protocol['input_pins'] == sink_protocol['body_input_pins'],'coherent body pins')
    for directory,protocol in ((a.body_export,body_protocol),(a.sink_export,sink_protocol)):
        for filename,pin in protocol['input_pins'].items():
            need(sha256((directory/filename).read_bytes()).hexdigest() == pin['sha256'],'input pin '+filename)
    graph,word,pairs,row=[json.loads((a.body_export/name).read_text()) for name in
                        ('graph.json','word.json','physical-pairs.json','profile-before.json')]
    registers=json.loads((a.sink_export/'register-map.json').read_text())
    forward=json.loads((a.sink_export/'forward-events.json').read_text())
    reflected=json.loads((a.sink_export/'reflected-events.json').read_text())
    core=load(a.exact_core,'rad_terminal_exact_core')
    exact=[check(graph,word,pairs,row,registers,events,core,direction)
           for direction,events in ((1,forward),(-1,reflected))]
    cleanup=cleanup_and_k(forward,set(registers['removed']))
    controls={}
    for mutation in ('omit_post','bad_pivot_sign','bad_k_coefficient'):
        try:
            check(graph,word,pairs,row,registers,forward,core,1,mutation)
        except ValueError as error:
            controls[mutation]=str(error)
        else:
            raise ValueError('negative control accepted '+mutation)
    kinds=Counter(event[0] for event in forward)
    source_allowance=4*(row['c']+row['v'])
    primitive_upper=kinds['op']+kinds['inj']+kinds['ysh']+2*kinds['yw']
    need(primitive_upper <= source_allowance,'additional sink primitives exceed paid source bill')
    sinks=json.loads((a.sink_export/'sink-map.json').read_text())
    need(len(set(target for z in sinks for target in z['T'])) == sum(len(z['T']) for z in sinks),
         'disjoint target stars for bounded target precision')
    pivot_writes=sum(len(z['writes']) for z in sinks)
    effective_q=row['q']-len(sinks)+pivot_writes
    need(3*effective_q < 2**15,'new half-read count exceeds retained numerator precision')
    M=row['total_M_operations'];h=row['h'];v=row['v'];R=row['R'];c=row['c']
    local=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8+2*h+8*R*v*(M+16)+32*v
    result=dict(status='PASS_EXACT_LITERAL_TERMINAL_SINK_CORE',source_head=body_protocol['source_head'],
                exact_orientations=exact,cleanup=cleanup,negative_controls=controls,sinks=len(sinks),
                full_event_inventory=dict(kinds),source_primitive_allowance=source_allowance,
                actual_primitive_upper_with_two_per_half_write=primitive_upper,
                source_primitive_margin=source_allowance-primitive_upper,pivot_writes=pivot_writes,
                effective_half_read_count=effective_q,three_effective_half_reads=3*effective_q,
                dirty_numerator_bits=M+16,coefficient_denominator_divides=6,
                local_expanded_group_upper=local,body_input_pins=body_protocol['input_pins'],
                sink_input_pins=sink_protocol['input_pins'],checker_sha256=sha256(a.exact_core.read_bytes()).hexdigest(),
                driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                elapsed_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Exact integer coefficient propagation of every actual forward/reflected event, including '
                      'target spectator shears, half pivot writes, original K and retained inverse cleanup. '
                      'Unit scratch/injection/target primitives plus2perhalfwrite fit the original4(c+v) bill. '
                      'Disjoint pre/post target stars copy a single partial sink sum without amplification; '
                      'the effective number of half reads remains below the retained3q<2^15 ceiling, soM+16 '
                      'digits and the scalar bill are preserved. Geometry/profile and all-size assembly are separate.')
    with a.output.open('x') as stream:
        json.dump(result,stream,indent=2);stream.write('\n')
    print('PASS exact literal sinks both orientations; %d sinks, L%d, %.3fs' %
          (len(sinks),local,time.monotonic()-start),flush=True)


if __name__ == '__main__':
    main()
