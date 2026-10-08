#!/usr/bin/env python3
"""Exact addition duplication versus controller-role savings.

A new node is deliberately not re-interned by formal support. It has the
same local provenance, source frame and scalar value as its original. A
strict improvement needs extra retained links greater than extra additions.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time

from finite_block_search import GroupUnion,install_reference
from finite_singleton_search import singleton_class
from fast_frame_envelope import labels
from frame_envelope import target_check
import frame_reuse


class CloneView(GroupUnion):
    def __init__(self,original,node,selected):
        for name in ('h','inputs','variables','locals','pair_ids','points','merged'):
            setattr(self,name,getattr(original,name))
        self.args=[None];self.core=[0];self.union=[0];self.provenance=[None]
        mapping={};clone=None
        for old in range(1,len(original.args)):
            args=original.args[old]
            if args:
                children=tuple(clone if child==node and ('gate',old) in selected else mapping[child] for child in args)
            else:children=None
            new=len(self.args);mapping[old]=new
            self.args.append(children);self.core.append(original.core[old]);self.union.append(original.union[old]);self.provenance.append(original.provenance[old])
            if old==node:
                assert args and clone is None
                clone=len(self.args);self.args.append(children);self.core.append(original.core[old]);self.union.append(original.union[old]);self.provenance.append(original.provenance[old])
        assert clone is not None
        self.outputs={target:clone if value==node and ('output',target) in selected else mapping[value]
                      for target,value in original.outputs.items()}
        self.active=set();stack=list(self.outputs.values())
        while stack:
            value=stack.pop()
            if value in self.active:continue
            self.active.add(value)
            if self.args[value]:stack.extend(self.args[value])
        self.additions=sum(self.args[value] is not None for value in self.active)
        assert mapping[node] in self.active and clone in self.active
        assert self.additions==original.additions+1
        self.cloned_original=node;self.cloned_new=clone;self.original_mapping=mapping


def compile_checked(circuit):
    logical=circuit.verify();frames,metadata=labels(circuit,True)
    plan=frame_reuse.optimize_chains(circuit,frames,'rank');code=frame_reuse.compile_reuse(circuit,frames,plan)
    checked=frame_reuse.check(circuit,frames,code);targets=target_check(circuit,frames,True)
    row=dict(logical=logical,roles=code['roles'],links=len(plan[2]),checked=checked,targets=targets,
        chains=code['chain_summary'],frames=metadata)
    frame_reuse.included.cache_clear();GroupUnion.support_in.cache_clear()
    return row,frames,code


def candidates(circuit,frames,maximum):
    users=defaultdict(list)
    for parent in sorted(circuit.active):
        for child in circuit.args[parent] or ():users[child].append(('gate',parent))
    for target,node in sorted(circuit.outputs.items()):users[node].append(('output',target))
    def label(use):return frames[use[1]] if use[0]=='gate' else frames[circuit.outputs[use[1]]]
    nodes=[node for node in circuit.active if circuit.args[node] and len(users[node])>=2
           and all(len(users[child])>=2 for child in circuit.args[node])]
    nodes.sort(key=lambda node:(-len(users[node]),-circuit.core[node].bit_count(),node))
    rows=[];seen=set()
    for node in nodes:
        outgoing=users[node];ordered=sorted(outgoing,key=lambda use:(label(use).dimension,str(use)))
        subsets=[ordered[:len(ordered)//2],ordered[::2],ordered[:1]]
        for use in ordered:
            incomparable=[other for other in ordered if not frame_reuse.included(label(use),label(other))
                          and not frame_reuse.included(label(other),label(use))]
            if incomparable:subsets.append([use]);subsets.append(incomparable)
        for subset in subsets:
            chosen=frozenset(subset)
            if not chosen or len(chosen)==len(outgoing):continue
            key=(node,tuple(sorted(chosen,key=str)))
            if key in seen:continue
            seen.add(key);rows.append((node,chosen))
            if len(rows)>=maximum:return rows,len(nodes)
    return rows,len(nodes)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reference',required=True)
    ap.add_argument('--h',type=int,nargs='+',default=[8,12]);ap.add_argument('--maximum',type=int,default=160)
    ap.add_argument('--dirty-best',action='store_true');ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();install_reference(args.reference)
    result=dict(status='Running',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        started_utc=datetime.now(timezone.utc).isoformat(),rows=[],
        scope='Exact duplicated DAG nodes with fixed positive envelopes; strict physical role reductions require delta_links>delta_additions')
    args.output.parent.mkdir(parents=True,exist_ok=True);allstart=time.monotonic()
    for h in args.h:
        start=time.monotonic();cls=singleton_class();positions=[0]*(h//2-1)+[h//2-2]*(h//2+1)
        original=GroupUnion(h,lambda n,c:cls(n,positions[c],2),'paired',0,True)
        baseline,frames,_=compile_checked(original);jobs,eligible=candidates(original,frames,args.maximum)
        rows=[];best=baseline;best_view=None;best_code=None
        for index,(node,selected) in enumerate(jobs):
            view=CloneView(original,node,selected);checked,_,code=compile_checked(view)
            delta_c=view.additions-original.additions;delta_links=checked['links']-baseline['links']
            assert checked['roles']-baseline['roles']==delta_c-delta_links
            row=dict(original_node=node,selected_uses=sorted(selected,key=str),roles=checked['roles'],
                delta_additions=delta_c,delta_retained_links=delta_links,
                compiled_sha256=checked['checked']['compiled_sha256'])
            rows.append(row)
            if checked['roles']<best['roles']:best=checked;best_view=view;best_code=code
        dirty=None
        if best_view is not None and args.dirty_best:
            from frame_reuse_certificate import program
            from dag_network import exact_invocation
            from review_singleton_witness import physical_coefficients
            from review_aligned_graph import check as independent_logical
            dirty=dict(complete_invocation=[exact_invocation(h,inverse,program(best_view,best_code)) for inverse in (False,True)],
                independent_physical=physical_coefficients(best_view,best_code),independent_logical=independent_logical(best_view))
        result['rows'].append(dict(h=h,positions=positions,baseline=baseline,best=best,
            eligible_duplicate_nodes=eligible,tested_splits=len(rows),candidates=rows,dirty_best=dirty,
            elapsed_seconds=time.monotonic()-start))
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,baseline=baseline['roles'],best=best['roles'],tested=len(rows),seconds=time.monotonic()-start)),flush=True)
    result.update(status='Terminal exact gate-duplication screen PASS',elapsed_seconds=time.monotonic()-allstart,
        completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
