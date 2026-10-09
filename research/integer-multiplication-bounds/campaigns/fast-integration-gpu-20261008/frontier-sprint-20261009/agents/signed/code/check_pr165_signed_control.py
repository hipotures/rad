#!/usr/bin/env python3
"""Independent exact integer audit of the selected PR165 complex core.

Prepared by RaD with GPT-6.1 Sol assistance, Apache-2.0. Reuses the separate
baseline lane's literal-event builder, not PR165's packed formal execution.
No sampled or modular identities establish the signed result. Exported
finite inputs are checked against their immutable source pins; loading the
saved finite graph is not called regeneration of its historical search.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def oriented(audit, graph, events, mutations, cleanup, live, direction):
    need(direction in (-1,1), 'orientation')
    need(len(cleanup) == len(mutations), 'cleanup count')
    need(all(c == audit.inverse(m) for c,m in zip(cleanup,reversed(mutations))),
         'exact inverse cleanup binding')
    adj = {role:{} for role in live}
    source = [{} for _ in range(graph['v'])]
    for event in reversed(events):
        kind = event[0]
        if kind == 'read':
            _,role,sign,response,_ = event
            need(role in adj, 'illegal physical read')
            audit.add(adj[role],response,direction*sign)
        elif kind == 'gate':
            _,dst,src,ca,cb = event
            need(dst in adj and src in adj and dst != src, 'illegal physical gate')
            audit.add(adj[src],adj[dst],cb)
            if ca == -1:
                adj[dst] = audit.scaled(adj[dst],-1)
        elif kind == 'inject':
            _,role,x,sign = event
            need(role in adj and 0 <= x < len(source), 'illegal physical injection')
            audit.add(source[x],adj[role],sign)
        else:
            raise ValueError('unknown event')
    for role,response in adj.items():
        need(not response or not any(audit.expanded(response,graph)),
             'nonzero arbitrary-dirty output response at role '+str(role))
    v = graph['v']
    for s,response in enumerate(source):
        row = audit.expanded(response,graph)
        cube = (s//8)*8
        for t in range(cube,cube+8):
            distance = (graph['inputs'][s]^graph['inputs'][t]).bit_count()
            row[t] += direction*(3 if distance == 6 else -3 if distance == 2 else 0)
        need(all(value == direction*6*(t==s) for t,value in enumerate(row)),
             'signed source output mismatch at source '+str(s))
    need(all(audit.inverse(audit.inverse(event)) == event for event in mutations),
         'literal inverse roundtrip')
    return dict(direction=direction,source_output_coefficients=v*v,
                arbitrary_dirty_output_coefficients=len(live)*v,dirty_slots=len(live),
                exact_signed_source_map=True,all_dirty_responses_zero=True,
                literal_reads_and_mutations=len(events),exact_inverse_cleanup_events=len(cleanup),
                target_spectators='Literal output shear leaves all existing target coefficients unchanged.',
                exact_inverse_roundtrip=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path, required=True)
    parser.add_argument('--exact-core', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(not sys.flags.optimize, 'assertion-disabled execution rejected')
    started = time.monotonic()
    protocol = json.loads((args.export/'protocol.json').read_text())
    for name,item in protocol['input_pins'].items():
        need(sha256((args.export/name).read_bytes()).hexdigest() == item['sha256'],
             'immutable finite input mismatch: '+name)
    data = {name:json.loads((args.export/(name+'.json')).read_text()) for name in
            ('graph','word','profile-before','physical-pairs','profile','frames')}
    g,word,row,pairs = (data[name] for name in ('graph','word','profile-before','physical-pairs'))
    spec = importlib.util.spec_from_file_location('rad_exact_core_pr165',args.exact_core)
    audit = importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    events,mutations,cleanup,live,response = audit.prepare(g,word,pairs,row['R'])
    checks = [oriented(audit,g,events,mutations,cleanup,live,direction) for direction in (1,-1)]
    need(len(live) == data['profile']['physical_R'] == row['R']-len(pairs), 'physical alias stock')
    controls = {}
    for mutation in ('omitted_read','bad_sign','illegal_index','omit_cleanup'):
        try:
            audit.check(g,events,mutations,cleanup,live,mutation=mutation)
        except (ValueError,KeyError) as error:
            controls[mutation] = str(error)
        else:
            raise ValueError('negative control accepted: '+mutation)
    # Exact local scalar expansion used by the inherited finite bridge.
    h,v,R,c,M = (row[key] for key in ('h','v','R','c','total_M_operations'))
    local = 4*(c+v)+10*v+4*h*v+4*h*h+8*h+8+2*h+8*R*v*(M+16)+32*v
    coefficients = {coefficient for root in g['roots'] for coefficient in root['coefficients']}
    need(coefficients <= {'1/2','-1/2','1/3','-1/6'} and 3*row['q'] < 2**15,
         'retained numerator/denominator bound')
    result = dict(status='PASS_EXACT_SIGNED_ARBITRARY_DIRTY_CORE',started_utc=datetime.now(timezone.utc).isoformat(),
                  checks=checks,negative_controls=controls,
                  scalar_counts={key:row[key] for key in ('h','v','c','q','matched','R','total_M_operations','loss')},
                  physical_roles=len(live),pairs=len(pairs),late_pairs=sum(t is not None for a,b,t in pairs),
                  local_expanded_group_upper=local,virtual_scalar_roles=R,
                  binary_dirty_read_bits=M+16,coefficient_denominator_divides=6,fixed_odd_divisor=3,
                  complete_paid_profile=data['profile'],input_pins=protocol['input_pins'],
                  exact_checker_sha256=sha256(args.exact_core.read_bytes()).hexdigest(),
                  driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  elapsed_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Exact integer adjoint of emitted source injections, all physical aliases/deadline reads, '
                        'signed mixers, center/scalar readouts and exact inverse cleanup, under both shear signs. '
                        'No sampling, modular inference or saved verdict consumption. Full complemented geometric '
                        'replay and graph assembly provenance are separate concurrent checks; general all-size '
                        'Clifford/shared-core/stopped/analytic interfaces remain inherited.')
    with args.output.open('x') as stream:
        json.dump(result,stream,indent=2);stream.write('\n')
    print('PASS exact signed source/dirty core in both orientations; physical slots %d, local scalar bill %d, %.3fs' %
          (len(live),local,result['elapsed_seconds']))


if __name__ == '__main__':
    main()
