#!/usr/bin/env python3
"""Delayed clones inherit the first-use frame of a complete output chain.

The clone's source span is contained in that existing positive envelope.
It executes immediately before its first use, so unused controller gates
after the original sum may supply its second input. Original nodes keep
their frames. The unchanged compiler checks the complete changed timeline.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import resource
import time

from finite_block_search import GroupUnion,install_reference
from finite_clone_batch import build,serialized
from finite_clone_chain_bridge import bridge_compatible
from finite_clone_gate_screen import compile_checked
from finite_clone_recovered_witness import compiled_hash,recovered_plan
from fast_frame_envelope import labels
from frame_envelope import target_check
import frame_reuse


def opportunities(circuit,frames,plan):
    users,descriptions,successor,predecessor,_=plan
    retained={descriptions[first][1] for first in successor}
    recipients={(parent,position):user for user,(_,parent,position) in enumerate(descriptions) if parent is not None}
    jobs=[];diagnostic=dict(unused_multiple_chain_parents=0,eligible_delayed_parents=0,
                            chosen_frames_strictly_larger=0,predecessors_after_original_parent=0)
    for node in sorted(circuit.active):
        if not circuit.args[node] or node in retained:continue
        chains=[]
        for first in users[node]:
            if first in predecessor:continue
            chain=[];user=first
            while True:
                _,parent,position=descriptions[user]
                chain.append(('gate',parent) if parent is not None else ('output',position))
                if user not in successor:break
                user=successor[user]
            chains.append((first,chain))
        if len(chains)<2:continue
        diagnostic['unused_multiple_chain_parents']+=1
        found=None
        # Larger first-use frames offer more admissible unused predecessors.
        chains.sort(key=lambda pair:(-(frames[descriptions[pair[0]][1] or node].dimension),pair[0]))
        for _,chain in chains:
            kind,owner=chain[0];owner_node=owner if kind=='gate' else node
            chosen_frame=frames[owner_node]
            assert frame_reuse.included(frames[node],chosen_frame)
            owner_key=(chosen_frame.dimension,owner_node) if kind=='gate' else None
            for position,child in enumerate(circuit.args[node]):
                for first in users[child]:
                    _,previous,_=descriptions[first]
                    if previous is None:continue
                    if previous==node or previous in retained:continue
                    if owner_key is not None and (frames[previous].dimension,previous)>=owner_key:continue
                    if not frame_reuse.included(frames[previous],chosen_frame):continue
                    found=dict(node=node,selected=frozenset(chain),predecessor_gates=[node,previous],
                        original_predecessor_users=[recipients[node,1-position],first],
                        original_children=list(circuit.args[node]),same_gate_new_predecessor_input=1-position,
                        earlier_predecessor_input=position,clone_frame_owner=owner_node,
                        clone_insertion_owner=owner if kind=='gate' else None,
                        original_frame_dimension=frames[node].dimension,clone_frame_dimension=chosen_frame.dimension)
                    break
                if found:break
            if found:break
        if not found:continue
        diagnostic['eligible_delayed_parents']+=1
        diagnostic['chosen_frames_strictly_larger']+=found['clone_frame_dimension']>frames[node].dimension
        diagnostic['predecessors_after_original_parent']+=(frames[found['predecessor_gates'][1]].dimension,
            found['predecessor_gates'][1])>(frames[node].dimension,node)
        jobs.append(found)
    return jobs,diagnostic


class DelayedCloneView(GroupUnion):
    """Build explicit IDs in the verified original physical rank order."""
    def __init__(self,original,old_frames,jobs):
        for name in ('h','inputs','variables','locals','pair_ids','points','merged'):
            setattr(self,name,getattr(original,name))
        selected={job['node']:job['selected'] for job in jobs};before={};terminal=[]
        for job in jobs:
            owner=job['clone_insertion_owner']
            (terminal if owner is None else before.setdefault(owner,[])).append(job)
        self.args=[None];self.core=[0];self.union=[0];self.provenance=[None]
        mapping={};clones={}
        def clone(job):
            old=job['node'];assert old in mapping and old not in clones
            children=tuple(mapping[child] for child in original.args[old])
            new=len(self.args);clones[old]=new
            self.args.append(children);self.core.append(original.core[old]);self.union.append(original.union[old]);self.provenance.append(original.provenance[old])
        order=sorted(original.active,key=lambda node:(old_frames[node].dimension,node))
        for old in order:
            for job in sorted(before.get(old,[]),key=lambda job:job['node']):clone(job)
            args=original.args[old]
            children=(tuple(clones[child] if child in clones and ('gate',old) in selected[child] else mapping[child]
                            for child in args) if args else None)
            new=len(self.args);mapping[old]=new
            self.args.append(children);self.core.append(original.core[old]);self.union.append(original.union[old]);self.provenance.append(original.provenance[old])
        for job in sorted(terminal,key=lambda job:job['node']):clone(job)
        self.outputs={target:clones[node] if node in clones and ('output',target) in selected[node] else mapping[node]
                      for target,node in original.outputs.items()}
        self.active=set();stack=list(self.outputs.values())
        while stack:
            node=stack.pop()
            if node in self.active:continue
            self.active.add(node)
            if self.args[node]:stack.extend(self.args[node])
        self.additions=sum(self.args[node] is not None for node in self.active)
        assert self.additions==original.additions+len(jobs)
        assert set(mapping.values())|set(clones.values())==self.active
        assert all(mapping[node]==node for node in range(1,len(self.inputs)+1))
        self.original_mapping=mapping;self.clones=clones


def descendant_frames(original,old_frames,view,jobs):
    frames={view.original_mapping[node]:old_frames[node] for node in original.active}
    for job in jobs:
        frame=old_frames[job['clone_frame_owner']]
        assert frame_reuse.included(old_frames[job['node']],frame)
        frames[view.clones[job['node']]]=frame
    assert set(frames)==view.active
    for node in view.active:
        if view.args[node]:assert all(frame_reuse.included(frames[child],frames[node]) for child in view.args[node])
        else:assert frames[node].basis==(view.core[node],)
    return frames


def small_controls(circuit,frames,code):
    from review_frame_reuse import dirty_check
    from review_singleton_witness import physical_coefficients
    from review_aligned_graph import check as logical_check
    from frame_reuse_certificate import program
    from dag_network import exact_invocation
    return dict(independent_logical=logical_check(circuit),independent_physical=physical_coefficients(circuit,code),
        complete_dirty_and_independent_rational_timeline=dirty_check(circuit,frames,code),
        complete_center_dirty_bases=[exact_invocation(circuit.h,inverse,program(circuit,code)) for inverse in (False,True)])


def case(h,base,positions,frozen=None,dirty=False):
    at=time.monotonic();original=build(h,base,positions)
    if frozen:
        logical=original.verify();assert logical==frozen['logical']
        old_frames,_=labels(original,True);old_plan=frame_reuse.optimize_chains(original,old_frames,'rank')
        old_code=frame_reuse.compile_reuse(original,old_frames,old_plan)
        assert old_code['roles']==frozen['compiled_roles'] and compiled_hash(old_code)==frozen['checked']['compiled_sha256']
        baseline=dict(logical=logical,roles=old_code['roles'],links=len(old_plan[2]),compiled_sha256=compiled_hash(old_code),frozen_physical_verification_reused=True)
    else:
        checked,old_frames,old_code=compile_checked(original);old_plan=frame_reuse.optimize_chains(original,old_frames,'rank')
        baseline=dict(logical=checked['logical'],roles=old_code['roles'],links=len(old_plan[2]),compiled_sha256=compiled_hash(old_code))
    jobs,diagnostic=opportunities(original,old_frames,old_plan);chosen,rejected=bridge_compatible(jobs)
    view=DelayedCloneView(original,old_frames,chosen);frames=descendant_frames(original,old_frames,view,chosen)
    plan=recovered_plan(original,old_plan,view,frames,chosen);code=frame_reuse.compile_reuse(view,frames,plan)
    logical=view.verify();checked=frame_reuse.check(view,frames,code);targets=target_check(view,frames,True)
    assert baseline['roles']-code['roles']==len(chosen)
    row=dict(h=h,base=base,positions=positions,baseline=baseline,opportunity_diagnostic=diagnostic,
        chosen=[serialized(job) for job in chosen],conflict_rejected=len(rejected),
        final=dict(logical=logical,roles=code['roles'],links=len(plan[2]),checked=checked,targets=targets,chains=plan[4]),
        role_saving=len(chosen),frame_scope='Original envelopes at original nodes; clone envelope inherited from first gate of its selected complete output chain')
    if dirty:row['complete_small_controls']=small_controls(view,frames,code)
    if h>=40:
        from finite_residual_rank_histogram import histogram
        from downstream_parameter_optimum import as_strings,saving_enclosure
        ranks=histogram(h,view,frames,code);row['exact_counts']=as_strings(ranks)
        row['uniform_shrink_saving']=as_strings(saving_enclosure(Fraction(ranks['D'],ranks['W']*ranks['m']),ranks['m']))
        v=len(view.inputs);G=3*v*v*(4*(view.additions+code['roles']-v)+20*v);E=64*(ranks['W']+ranks['m']+1)**3
        depth=2*G*ranks['W']**2+4*ranks['s']+4*ranks['W']+4
        assert E>depth;row['literal_scalar_guard']=as_strings(dict(G=G,E=E,depth=depth,slack=E-depth))
    row.update(elapsed_seconds=time.monotonic()-at,process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    frame_reuse.included.cache_clear();GroupUnion.support_in.cache_clear();return row


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True);ap.add_argument('--h',nargs='+',type=int,default=[8,12,20])
    ap.add_argument('--base',type=int,default=2);ap.add_argument('--candidate',type=Path)
    ap.add_argument('--dirty-ground',type=int);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();install_reference(args.reference)
    at=time.monotonic();value=dict(status='Running',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),rows=[],
        started_utc=datetime.now(timezone.utc).isoformat(),
        scope='Delayed clones with inherited positive first-use frames; unchanged exact timeline checks; independent transfer review pending')
    frozen=json.loads(args.candidate.read_text()) if args.candidate else None
    if frozen:value['candidate_input_sha256']=sha256(args.candidate.read_bytes()).hexdigest()
    configs=[(frozen['h'],frozen['base'],frozen['positions'])] if frozen else [(h,args.base,[0]*(h//2-1)+[h//2-2]*(h//2+1)) for h in args.h]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h,base,positions in configs:
        row=case(h,base,positions,frozen,args.dirty_ground==h);value['rows'].append(row)
        args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,baseline=row['baseline']['roles'],roles=row['final']['roles'],clones=len(row['chosen']),
            diagnostic=row['opportunity_diagnostic'],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact descendant-frame clone witness PASS',completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-at)
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
