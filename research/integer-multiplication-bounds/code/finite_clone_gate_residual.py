#!/usr/bin/env python3
"""Target clone gates with two unused predecessor capacities and intact outputs.

If each input's old recipient is saturated, but a distinct unused preceding
gate can retain that same input into a cloned recipient, splitting an entire
output-controller chain preserves its old links and supplies two new links.
The prediction is checked with the full unchanged compiler, not assumed.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time

from finite_clone_gate_screen import CloneView,compile_checked
from finite_block_search import GroupUnion,install_reference
from finite_singleton_search import singleton_class
from fast_frame_envelope import labels
import frame_reuse


def opportunities(circuit,frames,plan):
    users,descriptions,successor,predecessor,_=plan
    retained={descriptions[first][1] for first in successor}
    target_user={(parent,position):user for user,(_,parent,position) in enumerate(descriptions) if parent is not None}
    results=[];diagnostic=dict(eligible_multiple_output_chains=0,one_input_has_unused_predecessor=0,both_inputs_have_unused_predecessors=0)
    for node in sorted(circuit.active):
        if not circuit.args[node]:continue
        chains=[]
        for first in users[node]:
            if first in predecessor:continue
            chain=[];user=first
            while True:
                _,parent,target=descriptions[user]
                chain.append(('gate',parent) if parent is not None else ('output',target))
                if user not in successor:break
                user=successor[user]
            chains.append(chain)
        if len(chains)<2:continue
        diagnostic['eligible_multiple_output_chains']+=1
        options=[]
        for position,child in enumerate(circuit.args[node]):
            recipient=target_user[node,position];values=[]
            if recipient in predecessor:
                for user in users[child]:
                    _,previous,_=descriptions[user]
                    if user>=recipient:break
                    if previous is not None and previous not in retained and frame_reuse.included(frames[previous],frames[node]):
                        values.append((user,previous))
            options.append(values)
        diagnostic['one_input_has_unused_predecessor']+=int(any(options))
        if not all(options):continue
        diagnostic['both_inputs_have_unused_predecessors']+=1
        pair=next(((a,b) for a in options[0] for b in options[1] if a[1]!=b[1]),None)
        if pair is None:continue
        results.append(dict(node=node,selected=frozenset(chains[-1]),predecessor_gates=[pair[0][1],pair[1][1]],
            original_predecessor_users=[pair[0][0],pair[1][0]]))
    return results,diagnostic


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reference',required=True)
    ap.add_argument('--h',type=int,nargs='+',default=[8,12,20]);ap.add_argument('--maximum',type=int,default=32)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    install_reference(args.reference);rows=[];started=datetime.now(timezone.utc).isoformat();at=time.monotonic()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h in args.h:
        cls=singleton_class();positions=[0]*(h//2-1)+[h//2-2]*(h//2+1)
        original=GroupUnion(h,lambda n,c:cls(n,positions[c],2),'paired',0,True)
        baseline,frames,_=compile_checked(original);plan=frame_reuse.optimize_chains(original,frames,'rank')
        jobs,diagnostic=opportunities(original,frames,plan);tested=[]
        for job in jobs[:args.maximum]:
            view=CloneView(original,job['node'],job['selected']);result,_,_=compile_checked(view)
            delta_links=result['links']-baseline['links']
            tested.append(dict(original_node=job['node'],selected_uses=sorted(job['selected'],key=str),
                unused_predecessor_gates=job['predecessor_gates'],roles=result['roles'],delta_links=delta_links,
                delta_additions=1,predicted_two_extra_links_achieved=delta_links>=2,checked=result['checked']))
        row=dict(h=h,positions=positions,baseline_roles=baseline['roles'],baseline_links=baseline['links'],
            diagnostic=diagnostic,predicted_opportunities=len(jobs),tested=tested,
            best_roles=min([baseline['roles'],*[r['roles'] for r in tested]]))
        rows.append(row);print(json.dumps(row),flush=True)
        value=dict(status='Running',rows=rows,started_utc=started,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    value.update(status='Terminal exact clone-residual discriminator PASS',elapsed_seconds=time.monotonic()-at,
        completed_utc=datetime.now(timezone.utc).isoformat(),scope='Sufficient baseline-residual cloning opportunities only; absence is not a general recomputation exclusion')
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
