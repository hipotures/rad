#!/usr/bin/env python3
"""Earlier clone-capacity choices followed by exact actual-frame greedy rounds.

The complete saved allocation is reconstructed once with rounds=0 and used
only as an immutable source of the original graph/frames/links. A new first
batch changes which formal children and controller capacities are used.
Only the final changed compound graph is scientifically verified.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import resource
import time

import finite_bit_rounds_cached as allocation
import finite_complex_clone_nosym as offers
from finite_clone_batch import serialized
from finite_clone_chain_bridge import bridge_compatible
from finite_clone_recovered_witness import recovered_plan,compiled_hash
from frame_envelope import target_check
import frame_reuse


POLICIES=('late-parent','early-parent','scarce-capacity','scarce-parent','wide-owner','narrow-owner','seeded-parent')


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def reorder(jobs,frames,policy,seed):
    assert policy in POLICIES
    counts=Counter(j['node'] for j in jobs)
    loads=Counter(g for j in jobs for g in {j['node'],*j['predecessor_gates']})
    def key(j):
        node=j['node'];frame=frames[node]
        tie=sha256(repr((seed,node,j['predecessor_gates'],j.get('chain_first_user'),j['clone_frame_owner'])).encode()).digest()
        if policy=='late-parent':return (-frame.dimension,-node,tie)
        if policy=='early-parent':return (frame.dimension,node,tie)
        if policy=='scarce-capacity':return (sum(loads[g] for g in {node,*j['predecessor_gates']}),frame.dimension,tie)
        if policy=='scarce-parent':return (counts[node],frame.dimension,tie)
        if policy=='wide-owner':return (-j['clone_frame_dimension'],frame.dimension,tie)
        if policy=='narrow-owner':return (j['clone_frame_dimension'],frame.dimension,tie)
        return (sha256(repr((seed,node)).encode()).digest(),tie)
    return sorted(jobs,key=key)


def case(parent,policy='late-parent',seed=0,limit=4,rounds=4,dirty=False):
    start=time.monotonic()
    pinned=allocation.case(parent,0,4,'wide',0,6.0)
    assert pinned['pinned_parent_physical_evidence_reused'] and pinned['role_saving']==0
    cache=allocation.CACHE
    current=cache['original'];frames=cache['label_result'][0];plan=cache['old_plan'];code=cache['original_compile']
    first=allocation.first;records=[];total=0;prepare=time.monotonic()-start
    for iteration in range(rounds):
        at=time.monotonic();jobs,diagnostic=offers.opportunities(current,frames,plan,limit,'wide',seed+iteration*1000003)
        if iteration==0:
            preferred=[first.deserialize(j) for j in parent['chosen']]
            keys=set();merged=[]
            for j in [*preferred,*jobs]:
                k=digest(serialized(j))
                if k not in keys:keys.add(k);merged.append(j)
            jobs=merged
        chosen,rejected=bridge_compatible(reorder(jobs,frames,policy,seed+iteration*1000003))
        audited,bad=bridge_compatible(chosen);assert not bad and len(audited)==len(chosen)
        record=dict(round=iteration+1,chosen=[serialized(j) for j in chosen],old_roles=code['roles'],
            old_compiled_sha256=compiled_hash(code),old_logical_sha256=first.logical_identity(current),
            offered_count=len(jobs),rejected_count=len(rejected),diagnostic=diagnostic)
        if not chosen:
            record.update(new_roles=code['roles'],seconds=time.monotonic()-at);records.append(record);break
        view=first.witness.DelayedCloneView(current,frames,chosen)
        new_frames=first.witness.descendant_frames(current,frames,view,chosen)
        new_plan=recovered_plan(current,plan,view,new_frames,chosen)
        new_code=frame_reuse.compile_reuse(view,new_frames,new_plan)
        assert code['roles']-new_code['roles']==len(chosen)
        record.update(new_roles=new_code['roles'],new_compiled_sha256=compiled_hash(new_code),
            new_logical_sha256=first.logical_identity(view),seconds=time.monotonic()-at)
        records.append(record);total+=len(chosen);current,frames,plan,code=view,new_frames,new_plan,new_code
    assert cache['original_compile']['roles']-code['roles']==total
    at=time.monotonic();logical=current.verify();checked=frame_reuse.check(current,frames,code)
    targets=target_check(current,frames,True)
    row=dict(h=parent['h'],base=parent['base'],positions=parent['positions'],
        baseline=dict(parent['baseline']),frozen_allocation_parent_candidate_id=parent.get('candidate_id'),
        compiled_roles=code['roles'],role_saving_from_original=total,
        difference_from_saved_parent=parent['compiled_roles']-code['roles'],rounds=records,
        final=dict(logical=logical,checked=checked,roles=code['roles'],links=len(plan[2]),targets=targets),checked=checked,
        allocation_prepare_seconds=prepare,final_changed_verification_seconds=time.monotonic()-at,
        selection_scope='Exact greedy integer capacity/formal-child subset in a genuinely different earlier parent order; no MILP or optimality claim',
        frame_scope='Original positive envelopes; every actual inherited earlier clone frame retained literally in subsequent stages')
    if dirty:row['complete_small_controls']=first.witness.small_controls(current,frames,code)
    if parent['h']>=40:
        from finite_residual_rank_histogram import histogram
        from downstream_parameter_optimum import as_strings,saving_enclosure
        ranks=histogram(parent['h'],current,frames,code);v=len(current.inputs)
        G=3*v*v*(4*(current.additions+code['roles']-v)+20*v)
        E=64*(ranks['W']+ranks['m']+1)**3;depth=2*G*ranks['W']**2+4*ranks['s']+4*ranks['W']+4;assert depth<E
        row.update(residual_rank_histogram=as_strings(ranks),exact_counts=as_strings(ranks),
            literal_scalar_guard=as_strings(dict(G=G,E=E,depth=depth,slack=E-depth)),
            uniform_shrink_saving=as_strings(saving_enclosure(Fraction(ranks['D'],ranks['W']*ranks['m']),ranks['m'])))
    assert compiled_hash(cache['parent_compile'])==parent['checked']['compiled_sha256']
    assert tuple(cache['parent_frames'].items())==cache['frame_snapshot']
    assert tuple(cache['parent_plan'][2].items())==cache['link_snapshot']
    row.update(policy=policy,seed=seed,limit=limit,max_rounds=rounds,elapsed_seconds=time.monotonic()-start,
        process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    frame_reuse.included.cache_clear();first.witness.GroupUnion.support_in.cache_clear()
    return row


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reference',required=True)
    p.add_argument('--parent',type=Path,required=True);p.add_argument('--h',type=int,default=12)
    p.add_argument('--policies',nargs='+',choices=POLICIES,default=['late-parent','early-parent','scarce-capacity'])
    p.add_argument('--seed',type=int,default=0);p.add_argument('--limit',type=int,default=4)
    p.add_argument('--rounds',type=int,default=4);p.add_argument('--dirty',action='store_true');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists();allocation.first.witness.install_reference(a.reference)
    document=json.loads(a.parent.read_text());parent=next(r for r in document['rows']if r['h']==a.h)if 'rows'in document else document
    value=dict(status='Running',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        parent_path=str(a.parent),parent_sha256=sha256(a.parent.read_bytes()).hexdigest(),rows=[],
        started_utc=datetime.now(timezone.utc).isoformat())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    for policy in a.policies:
        row=case(parent,policy,a.seed,a.limit,a.rounds,a.dirty);value['rows'].append(row)
        a.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=row['h'],policy=policy,roles=row['compiled_roles'],
            clone_counts=[len(r['chosen'])for r in row['rounds']],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact earlier-selection compound witnesses PASS',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
