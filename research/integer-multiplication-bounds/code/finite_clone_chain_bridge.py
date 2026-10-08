#!/usr/bin/env python3
"""Duplicate a gate by bridging its retained input chain.

For an original controller edge P_A->later_A, an immediate same-frame clone
permits P_A->clone_A->later_A. One unused earlier capacity for the other
input B then adds earlier_B->clone_B. Two extra links cost one addition.
One entire output chain of P moves to the clone, preserving all old links.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import resource
import time

from finite_block_search import GroupUnion, install_reference
from finite_clone_batch import BatchCloneView, build, dirty_controls, serialized
from finite_clone_gate_screen import compile_checked
import frame_reuse


def bridge_opportunities(circuit, frames, plan):
    users, descriptions, successor, predecessor, _ = plan
    retained = {descriptions[first][1]:first for first in successor}
    recipients = {(parent, position):user for user, (_,parent,position) in enumerate(descriptions)
                  if parent is not None}
    jobs = []; diagnostic = dict(multiple_output_chains=0, own_capacity_retained=0,
                                available_other_input_predecessor=0)
    for node in sorted(circuit.active):
        if not circuit.args[node]: continue
        chains = []
        for first in users[node]:
            if first in predecessor: continue
            chain = []; user = first
            while True:
                _, parent, position = descriptions[user]
                chain.append(('gate',parent) if parent is not None else ('output',position))
                if user not in successor: break
                user = successor[user]
            chains.append(chain)
        if len(chains) < 2: continue
        diagnostic['multiple_output_chains'] += 1
        if node not in retained: continue
        diagnostic['own_capacity_retained'] += 1
        bridge_first = retained[node]
        assert descriptions[bridge_first][1] == node
        bridge_position = descriptions[bridge_first][2]
        other_position = 1-bridge_position
        recipient = recipients[node, other_position]
        child = circuit.args[node][other_position]
        options = []
        for first in users[child]:
            if first >= recipient: break
            _, previous, _ = descriptions[first]
            if previous is not None and previous not in retained and frame_reuse.included(frames[previous],frames[node]):
                options.append((first, previous))
        if not options: continue
        assert recipient in predecessor, 'An unused eligible predecessor and unused old recipient contradict maximum flow'
        diagnostic['available_other_input_predecessor'] += 1
        first, previous = options[0]
        jobs.append(dict(node=node, selected=frozenset(chains[-1]),
                         predecessor_gates=[previous], original_predecessor_users=[first],
                         bridge_input_position=bridge_position,
                         bridge_original_edge=[bridge_first,successor[bridge_first]],
                         original_children=list(circuit.args[node])))
    return jobs, diagnostic


def bridge_compatible(jobs):
    """Disjoint capacities, and never clone another job's formal input."""
    used = set(); parent_nodes = set(); child_nodes = set(); chosen = []; rejected = []
    for job in jobs:
        capacities = {job['node'],*job['predecessor_gates']}
        if capacities & used or job['node'] in child_nodes or parent_nodes & set(job['original_children']):
            rejected.append(job); continue
        used.update(capacities); parent_nodes.add(job['node']); child_nodes.update(job['original_children']); chosen.append(job)
    return chosen, rejected


def case(h, base, positions, single_tests=0, dirty=False):
    at=time.monotonic(); original=build(h,base,positions)
    baseline,frames,_=compile_checked(original)
    plan=frame_reuse.optimize_chains(original,frames,'rank')
    jobs,diagnostic=bridge_opportunities(original,frames,plan)
    chosen,rejected=bridge_compatible(jobs)
    row=dict(h=h,base=base,positions=positions,baseline=baseline,diagnostic=diagnostic,
             predicted_opportunities=len(jobs),chosen=[serialized(job) for job in chosen],
             conflict_rejected=len(rejected),single_tests=[])
    for job in jobs[:single_tests]:
        view=BatchCloneView(original,[job]);checked,_,_=compile_checked(view)
        gain=baseline['roles']-checked['roles']
        row['single_tests'].append(dict(job=serialized(job),roles=checked['roles'],role_saving=gain,
                                        delta_links=checked['links']-baseline['links'],checked=checked['checked']))
        assert gain >= 1, 'The sufficient explicit bridge failed its predicted actual-role gain'
    if chosen:
        view=BatchCloneView(original,chosen);checked,new_frames,code=compile_checked(view)
        delta_c=view.additions-original.additions;delta_links=checked['links']-baseline['links']
        gain=baseline['roles']-checked['roles']
        assert gain==delta_links-delta_c and delta_c==len(chosen)
        assert gain>=len(chosen), 'The supposedly compatible bridge batch failed'
        row.update(duplicated=checked,delta_additions=delta_c,delta_links=delta_links,role_saving=gain)
        if dirty:row['complete_dirty_controls']=dirty_controls(view,new_frames,code,shared=False)
        if h>=40:
            from finite_residual_rank_histogram import histogram
            from downstream_parameter_optimum import as_strings,saving_enclosure
            from fractions import Fraction
            counts=histogram(h,view,new_frames,code)
            row['exact_counts']=as_strings(counts)
            if counts['D']>0:row['uniform_shrink_saving']=as_strings(saving_enclosure(Fraction(counts['D'],counts['W']*counts['m']),counts['m']))
    row.update(elapsed_seconds=time.monotonic()-at,process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    frame_reuse.included.cache_clear();GroupUnion.support_in.cache_clear()
    return row


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True);ap.add_argument('--h',type=int,nargs='+',default=[8,12,20])
    ap.add_argument('--base',type=int,default=2);ap.add_argument('--candidate',type=Path)
    ap.add_argument('--single-tests',type=int,default=8);ap.add_argument('--dirty-ground',type=int)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();install_reference(args.reference)
    at=time.monotonic();value=dict(status='Running',started_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),rows=[],
        scope='Actual explicit clone/controller bridge; all scalar/rational/physical/target verifiers unchanged; original role endpoints and central paths retained')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.candidate:
        old=json.loads(args.candidate.read_text());configs=[(old['h'],old['base'],old['positions'])]
        value['candidate_input_sha256']=sha256(args.candidate.read_bytes()).hexdigest()
    else:configs=[(h,args.base,[0]*(h//2-1)+[h//2-2]*(h//2+1)) for h in args.h]
    for h,base,positions in configs:
        row=case(h,base,positions,args.single_tests,args.dirty_ground==h);value['rows'].append(row)
        args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,baseline=row['baseline']['roles'],roles=row.get('duplicated',{}).get('roles'),
                              clones=len(row['chosen']),gain=row.get('role_saving'),seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact chain-bridge cloning PASS',completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-at)
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
