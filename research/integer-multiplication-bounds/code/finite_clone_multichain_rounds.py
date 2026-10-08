#!/usr/bin/env python3
"""Move multiple whole chains to a clone and test bounded further rounds.

The sufficient unused-P/unused-Q two-link proof is unchanged. Moving all
but one output chain keeps both explicit sums active and may leave the clone
with more than one chain. Its fresh unused capacity can then profit in a
later round. The new fixed graph's exact optimizer is used between rounds.
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
from finite_clone_batch import BatchCloneView,build,dirty_controls,serialized
from finite_clone_chain_bridge import bridge_compatible
from finite_clone_gate_screen import compile_checked
from finite_clone_recovered_witness import compiled_hash,mapped_frames,recovered_plan
from finite_clone_unused_capacity import unused_opportunities
from fast_frame_envelope import labels
from frame_envelope import target_check
import frame_reuse


def multichain_jobs(circuit,plan,jobs):
    users,descriptions,successor,predecessor,_=plan
    expanded=[]
    for job in jobs:
        chains=[]
        for first in users[job['node']]:
            if first in predecessor:continue
            selected=[];user=first
            while True:
                _,parent,position=descriptions[user]
                selected.append(('gate',parent) if parent is not None else ('output',position))
                if user not in successor:break
                user=successor[user]
            chains.append(selected)
        assert len(chains)>=2
        expanded.append(dict(job,selected=frozenset(use for chain in chains[1:] for use in chain),
                             original_output_chains=len(chains),moved_output_chains=len(chains)-1))
    return expanded


def case(h,base,positions,max_rounds,frozen=None,compare_frames=False,dirty=False):
    at=time.monotonic();circuit=build(h,base,positions)
    if frozen:
        logical=circuit.verify();assert logical==frozen['logical']
        frames,_=labels(circuit,True);plan=frame_reuse.optimize_chains(circuit,frames,'rank')
        code=frame_reuse.compile_reuse(circuit,frames,plan)
        assert code['roles']==frozen['compiled_roles'] and compiled_hash(code)==frozen['checked']['compiled_sha256']
        baseline=dict(roles=code['roles'],links=len(plan[2]),logical=logical,compiled_sha256=compiled_hash(code),
                      verification_reused_from_immutable_baseline=True)
    else:
        checked,frames,code=compile_checked(circuit);plan=frame_reuse.optimize_chains(circuit,frames,'rank')
        baseline=dict(roles=code['roles'],links=len(plan[2]),logical=checked['logical'],compiled_sha256=compiled_hash(code))
    row=dict(h=h,base=base,positions=positions,baseline=baseline,rounds=[])
    for number in range(max_rounds):
        started=time.monotonic();jobs,diagnostic=unused_opportunities(circuit,frames,plan)
        jobs=multichain_jobs(circuit,plan,jobs);chosen,rejected=bridge_compatible(jobs)
        entry=dict(round=number+1,opportunity_diagnostic=diagnostic,predicted_opportunities=len(jobs),
            conflict_rejected=len(rejected),chosen=[serialized(job) for job in chosen],
            old_roles=code['roles'],old_links=len(plan[2]),old_additions=circuit.additions)
        if not chosen:
            entry.update(status='Terminal no sufficient opportunity',elapsed_seconds=time.monotonic()-started)
            row['rounds'].append(entry);break
        view=BatchCloneView(circuit,chosen);new_frames=mapped_frames(circuit,frames,view,compare_frames)
        feasible=recovered_plan(circuit,plan,view,new_frames,chosen)
        optimized=frame_reuse.optimize_chains(view,new_frames,'rank')
        assert len(optimized[2])>=len(feasible[2])
        new_code=frame_reuse.compile_reuse(view,new_frames,optimized)
        assert new_code['roles']<=code['roles']-len(chosen)
        entry.update(status='Exact induced feasible flow and new optimum constructed',roles=new_code['roles'],
            extra_links=len(optimized[2])-len(plan[2]),extra_additions=len(chosen),
            exact_compiled_sha256=compiled_hash(new_code),elapsed_seconds=time.monotonic()-started)
        row['rounds'].append(entry);circuit,frames,plan,code=view,new_frames,optimized,new_code
    if compare_frames:
        rebuilt,_=labels(circuit,True);assert rebuilt==frames
    logical=circuit.verify();checked=frame_reuse.check(circuit,frames,code);targets=target_check(circuit,frames,True)
    total=sum(len(entry['chosen']) for entry in row['rounds'])
    assert logical['additions']==baseline['logical']['additions']+total
    gain=baseline['roles']-code['roles'];assert gain>=total
    row.update(final=dict(logical=logical,roles=code['roles'],links=len(plan[2]),checked=checked,
        targets=targets,chains=plan[4]),total_clones=total,role_saving=gain,canonical_frame_equality=compare_frames)
    if dirty:row['complete_dirty_controls']=dirty_controls(circuit,frames,code,shared=h<=8 and h%2==0)
    if h>=40:
        from finite_residual_rank_histogram import histogram
        from downstream_parameter_optimum import as_strings,saving_enclosure
        counts=histogram(h,circuit,frames,code);row['exact_counts']=as_strings(counts)
        row['uniform_shrink_saving']=as_strings(saving_enclosure(Fraction(counts['D'],counts['W']*counts['m']),counts['m']))
        v=len(circuit.inputs);G=3*v*v*(4*(circuit.additions+code['roles']-v)+20*v)
        E=64*(counts['W']+counts['m']+1)**3;depth=2*G*counts['W']**2+4*counts['s']+4*counts['W']+4
        assert E>depth;row['literal_scalar_guard']=as_strings(dict(G=G,E=E,depth=depth,slack=E-depth))
    row.update(elapsed_seconds=time.monotonic()-at,process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    frame_reuse.included.cache_clear();GroupUnion.support_in.cache_clear();return row


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True);ap.add_argument('--h',type=int,nargs='+',default=[8,12,20])
    ap.add_argument('--base',type=int,default=2);ap.add_argument('--candidate',type=Path)
    ap.add_argument('--max-rounds',type=int,default=6);ap.add_argument('--compare-frames',action='store_true')
    ap.add_argument('--dirty-ground',type=int);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();assert 1<=args.max_rounds<=20;install_reference(args.reference)
    at=time.monotonic();value=dict(status='Running',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        started_utc=datetime.now(timezone.utc).isoformat(),rows=[],
        scope='Bounded explicit multi-chain clones; old maps/frames are preserved; final changed graph checked in full; no final exponent promotion')
    frozen=json.loads(args.candidate.read_text()) if args.candidate else None
    if frozen:value['candidate_input_sha256']=sha256(args.candidate.read_bytes()).hexdigest()
    configs=[(frozen['h'],frozen['base'],frozen['positions'])] if frozen else [(h,args.base,[0]*(h//2-1)+[h//2-2]*(h//2+1)) for h in args.h]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h,base,positions in configs:
        row=case(h,base,positions,args.max_rounds,frozen,args.compare_frames,args.dirty_ground==h)
        value['rows'].append(row);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,baseline=row['baseline']['roles'],roles=row['final']['roles'],clones=row['total_clones'],
            rounds=[dict(round=entry['round'],clones=len(entry['chosen']),roles=entry.get('roles')) for entry in row['rounds']],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact multi-chain clone witness PASS',completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-at)
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
