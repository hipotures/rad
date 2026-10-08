#!/usr/bin/env python3
"""Frame-safe temporary computation and restoration on a frozen compiler.

For B=A+C with one later use P=B+D, an unused future A copy may be
deleted if B is computed temporarily on another A role, P consumes D,
and C restores A afterward. Both restored-A and C frames remain enlarged
to frame(P). This file first screens exact physical timelines; a screen
is not a witness or an integer-multiplication theorem.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
import time


def screen(circuit, spaces, code, plan):
    from frame_reuse import included
    users, descriptions, successor, predecessor, _ = plan
    gates = code['gates']
    location = {node:i for i,(node,_,_) in enumerate(gates)}
    uses = [[] for _ in range(code['roles'])]
    for i,(node,ins,outs) in enumerate(gates):
        for role in set(ins+outs):
            uses[role].append((i,spaces[node]))
    for target,role in code['outputs'].items():
        uses[role].append((len(gates),spaces[circuit.outputs[target]]))
    use_for_gate = {(parent,position):user for user,(_,parent,position) in enumerate(descriptions)
                    if parent is not None}
    reasons = Counter(); rows = []
    for b,ins,outs in gates:
        if circuit.args[b] is None:
            continue
        reasons['addition_nodes'] += 1
        if len(users[b]) != 1 or descriptions[users[b][0]][1] is None:
            continue
        reasons['one_nonterminal_user'] += 1
        p = descriptions[users[b][0]][1]
        bi,pi = location[b],location[p]
        pins,pouts = gates[pi][1:]
        incoming_p = [use_for_gate[p,pos] for pos in (0,1)]
        if any(user in successor for user in incoming_p):
            continue
        reasons['parent_retains_no_input'] += 1
        incoming_b = [use_for_gate[b,pos] for pos in (0,1)]
        terminal = [pos for pos,user in enumerate(incoming_b) if user not in successor]
        consumed_position = terminal[0]
        a,c = circuit.args[b][consumed_position],circuit.args[b][1-consumed_position]
        a_role,c_role = ins
        assert len(outs) == 1 and outs[0] == a_role
        assert a_role in pins
        d_role = pins[1] if pins[0] == a_role else pins[0]
        ai = location[a]
        a_outs = gates[ai][2]
        future = []
        for role in a_outs[1:]:
            if role == a_role:
                continue
            later = [(i,frame) for i,frame in uses[role] if i > ai]
            if later and later[0][0] > pi and included(spaces[p],later[0][1]):
                future.append((later[0][0],role))
        if not future:
            continue
        reasons['future_A_copy_contains_parent_frame'] += 1
        later_c = [(i,frame) for i,frame in uses[c_role] if i > bi]
        if later_c and later_c[0][0] <= pi:
            continue
        if later_c and not included(spaces[p],later_c[0][1]):
            continue
        reasons['C_survives_to_restore_and_future_frame_contains_parent'] += 1
        assert included(spaces[b],spaces[p]) and included(spaces[a],spaces[p]) and included(spaces[c],spaces[p])
        future_role = min(future)[1]
        rows.append(dict(a=a,b=b,c=c,p=p,a_gate=ai,b_gate=bi,p_gate=pi,
            a_role=a_role,c_role=c_role,d_role=d_role,deleted_future_a_copy=future_role,
            old_parent_pivot=pins[0],parent_frame_rank=spaces[p].dimension,
            a_frame_rank=spaces[a].dimension,c_frame_rank=spaces[c].dimension,
            first_future_a_gate=min(future)[0],first_future_c_gate=later_c[0][0] if later_c else None))
    selected=[]; busy_roles=set(); busy_gates=set()
    for row in rows:
        roles={row[key] for key in ('a_role','c_role','d_role','deleted_future_a_copy')}
        affected_gates={row['b_gate'],row['p_gate']}
        if roles & busy_roles or affected_gates & busy_gates:
            continue
        selected.append(row);busy_roles.update(roles);busy_gates.update(affected_gates)
    return dict(screen_counts=dict(reasons),candidates=rows,disjoint_selected=selected,
        potential_role_reduction=len(selected),scope='Timeline/frame screen only; no changed executable compiled or validated')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--reference',required=True)
    ap.add_argument('--h',type=int,nargs='+',default=[6,8,12])
    ap.add_argument('--base',type=int,default=2)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    assert not args.output.exists()
    from finite_block_search import install_reference,GroupUnion
    install_reference(args.reference)
    from finite_singleton_search import singleton_class
    from fast_frame_envelope import labels
    from frame_envelope import target_check
    from frame_reuse import optimize_chains,compile_reuse,check
    start=time.monotonic();rows=[];cls=singleton_class()
    for h in args.h:
        positions=([0]*6+[23]*26+[0]*18) if h == 50 else [0]*(h//2-1)+[h//2-2]*(h//2+1)
        circuit=GroupUnion(h,lambda n,c:cls(n,positions[c],args.base),'paired',0,True)
        original=circuit.verify();spaces,metadata=labels(circuit,True)
        plan=optimize_chains(circuit,spaces,'rank');code=compile_reuse(circuit,spaces,plan)
        checked=check(circuit,spaces,code);targets=target_check(circuit,spaces,True)
        row=dict(h=h,base=args.base,positions=positions,original=original,roles=code['roles'],
            original_compiled=checked,frames=metadata,targets=targets,episode_screen=screen(circuit,spaces,code,plan))
        rows.append(row)
        print(json.dumps(dict(h=h,roles=code['roles'],potential_reduction=row['episode_screen']['potential_role_reduction'],
            counts=row['episode_screen']['screen_counts'])),flush=True)
    result=dict(status='Terminal screen',started_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=time.monotonic()-start,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            ('frame_reuse.py','frame_envelope.py','fast_frame_envelope.py','finite_singleton_search.py','finite_block_search.py')})
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
