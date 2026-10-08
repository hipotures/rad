#!/usr/bin/env python3
"""Use an original gate's unused capacity as one clone predecessor.

P_A->clone_A is newly available because the clone follows P at the same
frame. If an unused earlier Q_B can also reach clone_B, moving one whole
P-output chain preserves the original flow and adds two links for one sum.
This search changes no inclusion, coefficient, compiler or rank checker.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

import finite_clone_chain_bridge as driver
import frame_reuse


def unused_opportunities(circuit, frames, plan):
    users, descriptions, successor, predecessor, _ = plan
    retained = {descriptions[first][1] for first in successor}
    recipient = {(parent, position):user for user, (_,parent,position) in enumerate(descriptions)
                 if parent is not None}
    jobs=[];diagnostic=dict(multiple_output_chains=0,own_capacity_unused=0,
                           one_unused_predecessor_available=0)
    for node in sorted(circuit.active):
        if not circuit.args[node]: continue
        chains=[]
        for first in users[node]:
            if first in predecessor: continue
            chain=[];user=first
            while True:
                _,parent,position=descriptions[user]
                chain.append(('gate',parent) if parent is not None else ('output',position))
                if user not in successor:break
                user=successor[user]
            chains.append(chain)
        if len(chains)<2:continue
        diagnostic['multiple_output_chains']+=1
        if node in retained:continue
        diagnostic['own_capacity_unused']+=1
        options=[]
        for position,child in enumerate(circuit.args[node]):
            current=recipient[node,position]
            for first in users[child]:
                if first>=current:break
                _,previous,_=descriptions[first]
                if previous is not None and previous not in retained and frame_reuse.included(frames[previous],frames[node]):
                    options.append((first,previous,position))
        if not options:continue
        diagnostic['one_unused_predecessor_available']+=1
        first,previous,position=options[0]
        other=1-position
        assert recipient[node,other] not in successor
        assert recipient[node,position] in predecessor
        jobs.append(dict(node=node,selected=frozenset(chains[-1]),
                         predecessor_gates=[node,previous],
                         original_predecessor_users=[recipient[node,other],first],
                         original_children=list(circuit.args[node]),
                         same_gate_new_predecessor_input=other,
                         earlier_predecessor_input=position))
    return jobs,diagnostic


def main():
    # Only candidate generation is rebound; every inherited verifier remains.
    parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--output',type=Path,required=True)
    args,_=parser.parse_known_args()
    driver.bridge_opportunities=unused_opportunities
    driver.main()
    value=json.loads(args.output.read_text())
    value.update(candidate_generator_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                 candidate_generation_binding='driver.bridge_opportunities=unused_opportunities; all compiler and exact check functions unchanged')
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
