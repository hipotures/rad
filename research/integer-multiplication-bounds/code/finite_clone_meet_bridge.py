#!/usr/bin/env python3
"""Delayed retained-input clones use the positive meet of two future frames.

Replace P_A->G_A by P_A->clone_A->G_A and add unused Q_B->clone_B.
The clone's frame E(C_F union C_G,V_F intersection V_G) lies between
P and both future uses. Net two links cost one explicit additional sum.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import resource
import time

from finite_block_search import GroupUnion,install_reference
from finite_clone_batch import build,serialized
from finite_clone_chain_bridge import bridge_compatible
from finite_clone_descendant_frame import DelayedCloneView,small_controls
from finite_clone_gate_screen import compile_checked
from finite_clone_recovered_witness import descriptions
from fast_frame_envelope import envelope
from frame_envelope import target_check
import frame_reuse


def opportunities(circuit,frames,plan):
    users,uses,successor,predecessor,_=plan
    retained={uses[first][1]:first for first in successor};jobs=[];cache={}
    diagnostic=dict(retained_multiple_chain_parents=0,eligible_positive_meet_bridges=0,
                    strict_frame_enlargements=0,predecessors_after_P=0)
    for node in sorted(retained):
        if node is None:continue
        first_a=retained[node];second_a=successor[first_a]
        a=uses[first_a][2];b=1-a;child_a,following_a,_=uses[second_a]
        G=frames[following_a if following_a is not None else child_a]
        assert frame_reuse.included(frames[node],G)
        chains=[]
        for first in users[node]:
            if first in predecessor:continue
            chain=[];user=first
            while True:
                _,parent,position=uses[user]
                chain.append(('gate',parent) if parent is not None else ('output',position))
                if user not in successor:break
                user=successor[user]
            chains.append(chain)
        if len(chains)<2:continue
        diagnostic['retained_multiple_chain_parents']+=1
        chains.sort(key=lambda chain:-(frames[chain[0][1] if chain[0][0]=='gate' else node].dimension))
        found=None
        for chain in chains:
            kind,first_f=chain[0];F=frames[first_f if kind=='gate' else node]
            assert frame_reuse.included(frames[node],F)
            key=(F.core|G.core,F.vertices&G.vertices)
            if key not in cache:cache[key]=envelope(*key,circuit.h)
            meet=cache[key]
            assert frame_reuse.included(frames[node],meet) and frame_reuse.included(meet,F) and frame_reuse.included(meet,G)
            owners=[x for x in (first_f if kind=='gate' else None,following_a) if x is not None]
            insertion=min(owners,key=lambda x:(frames[x].dimension,x)) if owners else None
            insertion_key=(frames[insertion].dimension,insertion) if insertion is not None else None
            for first_b in users[circuit.args[node][b]]:
                _,previous,_=uses[first_b]
                if previous is None or previous==node or previous in retained:continue
                if insertion_key is not None and (frames[previous].dimension,previous)>=insertion_key:continue
                if not frame_reuse.included(frames[previous],meet):continue
                found=dict(node=node,selected=frozenset(chain),predecessor_gates=[previous],
                    original_children=list(circuit.args[node]),bridge_input_position=a,other_input_position=b,
                    bridge_original_edge=[first_a,second_a],earlier_other_input_user=first_b,
                    first_output_chain_gate=first_f if kind=='gate' else None,
                    retained_input_next_gate=following_a,clone_insertion_owner=insertion,
                    clone_frame_core=key[0],clone_frame_support=key[1],
                    original_frame_dimension=frames[node].dimension,clone_frame_dimension=meet.dimension)
                break
            if found:break
        if found:
            diagnostic['eligible_positive_meet_bridges']+=1
            diagnostic['strict_frame_enlargements']+=found['clone_frame_dimension']>frames[node].dimension
            diagnostic['predecessors_after_P']+=(frames[found['predecessor_gates'][0]].dimension,
                found['predecessor_gates'][0])>(frames[node].dimension,node)
            jobs.append(found)
    return jobs,diagnostic


def frames_for(original,old_frames,view,jobs):
    frames={view.original_mapping[node]:old_frames[node] for node in original.active};cache={}
    for job in jobs:
        key=job['clone_frame_core'],job['clone_frame_support']
        if key not in cache:cache[key]=envelope(*key,original.h)
        frames[view.clones[job['node']]]=cache[key]
    for node in view.active:
        if view.args[node]:assert all(frame_reuse.included(frames[x],frames[node]) for x in view.args[node])
        else:assert frames[node].basis==(view.core[node],)
    order=sorted(view.active,key=lambda node:(frames[node].dimension,node));position={node:i for i,node in enumerate(order)}
    for job in jobs:
        clone=view.clones[job['node']]
        assert position[view.original_mapping[job['node']]]<position[clone]
        assert position[view.original_mapping[job['predecessor_gates'][0]]]<position[clone]
        for owner in (job['first_output_chain_gate'],job['retained_input_next_gate']):
            if owner is not None:assert position[clone]<position[view.original_mapping[owner]]
    return frames


def bridge_plan(original,old_plan,view,frames,jobs):
    _,old_uses,old_successor,_,_=old_plan;users,uses,index=descriptions(view,frames)
    use_map={user:index[view.original_mapping[parent] if parent is not None else None,position]
             for user,(_,parent,position) in enumerate(old_uses)}
    removed={tuple(job['bridge_original_edge']) for job in jobs};successor={};predecessor={}
    def link(first,second):
        assert first not in successor and second not in predecessor
        node,previous,_=uses[first];node2,following,_=uses[second]
        assert node==node2 and first<second and previous is not None
        assert frame_reuse.included(frames[previous],frames[following if following is not None else node])
        successor[first]=second;predecessor[second]=first
    for first,second in old_successor.items():
        if (first,second) not in removed:link(use_map[first],use_map[second])
    for job in jobs:
        clone=view.clones[job['node']];a=job['bridge_input_position'];b=job['other_input_position']
        first,second=job['bridge_original_edge']
        link(use_map[first],index[clone,a]);link(index[clone,a],use_map[second])
        link(use_map[job['earlier_other_input_user']],index[clone,b])
    retained=set()
    for first in successor:
        parent=uses[first][1];assert parent not in retained;retained.add(parent)
    assert len(uses)==len(old_uses)+2*len(jobs) and len(successor)==len(old_successor)+2*len(jobs)
    return users,uses,successor,predecessor,dict(schedule='rank',selected_links=len(successor),flow_value=len(successor),
        recovered_extra_links=2*len(jobs),scope='Explicit feasible retained-input meet-frame bridge; optimality not asserted',
        exact_source_order_capacity_frame_audit=True)


def case(h,base,positions,dirty):
    at=time.monotonic();original=build(h,base,positions);baseline,old_frames,_=compile_checked(original)
    old_plan=frame_reuse.optimize_chains(original,old_frames,'rank');jobs,diagnostic=opportunities(original,old_frames,old_plan)
    chosen,rejected=bridge_compatible(jobs);view=DelayedCloneView(original,old_frames,chosen)
    frames=frames_for(original,old_frames,view,chosen);plan=bridge_plan(original,old_plan,view,frames,chosen)
    code=frame_reuse.compile_reuse(view,frames,plan);logical=view.verify();checked=frame_reuse.check(view,frames,code)
    targets=target_check(view,frames,True);assert baseline['roles']-code['roles']==len(chosen)
    row=dict(h=h,base=base,positions=positions,baseline=baseline,opportunity_diagnostic=diagnostic,
        chosen=[serialized(job) for job in chosen],conflict_rejected=len(rejected),role_saving=len(chosen),
        final=dict(roles=code['roles'],links=len(plan[2]),logical=logical,checked=checked,targets=targets,chains=plan[4]))
    if dirty:row['complete_small_controls']=small_controls(view,frames,code)
    row.update(elapsed_seconds=time.monotonic()-at,process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    frame_reuse.included.cache_clear();GroupUnion.support_in.cache_clear();return row


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True);ap.add_argument('--h',type=int,nargs='+',default=[8,12,20])
    ap.add_argument('--base',type=int,default=2);ap.add_argument('--dirty-ground',type=int)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists();install_reference(args.reference)
    at=time.monotonic();value=dict(status='Running',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),rows=[],
        started_utc=datetime.now(timezone.utc).isoformat(),scope='Retained-input positive meet-frame bridge; explicit source/order/capacity/target checks; all-size independent transfer pending')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h in args.h:
        positions=[0]*(h//2-1)+[h//2-2]*(h//2+1);row=case(h,args.base,positions,args.dirty_ground==h)
        value['rows'].append(row);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,baseline=row['baseline']['roles'],roles=row['final']['roles'],clones=len(row['chosen']),diagnostic=row['opportunity_diagnostic'],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact positive meet-frame bridge PASS',completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-at)
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
