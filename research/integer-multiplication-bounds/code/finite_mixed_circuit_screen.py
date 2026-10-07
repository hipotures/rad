#!/usr/bin/env python3
"""Exact whole-graph screen for aggregated full-pair target contributions.

The two common-point contributions for a target A union {b}, with A a
global pair, equal a single vertex-exclusion map on pair inputs aggregated
over A. This graph is globally interned against the original paired circuit.
Counts are accepted only after complete formal coefficient checks and pruning.
Nondegeneracy screens are separate from any transferred theorem claim.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import resource
import time

from finite_block_search import GroupUnion, install_reference, make_block_class
from finite_mixed_spans import component_criterion


def active_for(args,outputs):
    active=set()
    stack=list(outputs)
    while stack:
        node=stack.pop()
        if not node or node in active:
            continue
        active.add(node)
        if args[node]:
            stack.extend(args[node])
    return active


def single_template(n,kind):
    from exclusion_circuit import ExclusionCircuit
    from paired_exclusion_circuit import PairedExclusionCircuit
    cls=PairedExclusionCircuit if kind=="paired" else ExclusionCircuit
    c=cls(n)
    _,one,_=c.pair(list(range(n)))
    c.outputs={(a,):node for a,node in one.items()}
    c.active=active_for(c.args,c.outputs.values())
    c.additions=sum(c.args[node] is not None for node in c.active)
    for (a,),node in c.outputs.items():
        expected=sum(1<<i for i,pair in enumerate(c.inputs) if a not in pair)
        assert c.support[node]==expected
    return c


def screen(reference,h,kind):
    install_reference(reference)
    block=make_block_class()
    old=GroupUnion(h,lambda n:block(n,(2,),4,0),"paired",109)
    old_checked=old.verify()
    local=single_template(h-2,kind)
    support=[0]*len(old.args)
    lookup={}
    for node in sorted(old.active):
        if old.args[node]:
            a,b=old.args[node]
            assert not support[a]&support[b]
            support[node]=support[a]|support[b]
        else:
            support[node]=1<<(node-1)
        assert support[node] not in lookup
        lookup[support[node]]=node
    args=list(old.args)
    core=list(old.core)
    provenance=[None]*len(args)
    reused_old=reused_new=created=0
    local_criterion={}
    for node in sorted(local.active):
        if local.args[node]:
            edge_mask=local.support[node]
            edges=[]
            while edge_mask:
                bit=edge_mask&-edge_mask
                edge_mask-=bit
                edges.append(local.inputs[bit.bit_length()-1])
            local_criterion[node]=component_criterion(list(range(h-2)),edges)

    def add(a,b,origin):
        nonlocal reused_old,reused_new,created
        assert not support[a]&support[b]
        value=support[a]|support[b]
        if value in lookup:
            node=lookup[value]
            if node<len(old.args):
                reused_old+=1
            else:
                reused_new+=1
            return node
        node=len(args)
        lookup[value]=node
        args.append((a,b))
        support.append(value)
        core.append(core[a]&core[b])
        provenance.append(origin)
        created+=1
        return node

    outputs={}
    full_pair_targets=set()
    for A in [(a,a+1) for a in range(0,h,2)]:
        points=[x for x in range(h) if x not in A]
        mapping={}
        for node in sorted(local.active):
            if local.args[node] is None:
                u,v=(points[x] for x in local.inputs[node-1])
                i=old.variables[tuple(sorted((A[0],u,v)))]
                j=old.variables[tuple(sorted((A[1],u,v)))]
                mapping[node]=add(i,j,(A,"input",node))
            else:
                a,b=(mapping[x] for x in local.args[node])
                mapping[node]=add(a,b,(A,"graph",node))
        for (b,),node in local.outputs.items():
            target=tuple(sorted((*A,points[b])))
            outputs[("mixed",A,target)]=mapping[node]
            full_pair_targets.add(target)
    for (common,target),node in old.outputs.items():
        if target in full_pair_targets:
            A=next((a,a+1) for a in range(0,h,2) if a in target and a+1 in target)
            if common in A:
                continue
        outputs[("old",common,target)]=node
    active=active_for(args,outputs.values())
    old_surviving=sum(node<len(old.args) and args[node] is not None for node in active)
    new_surviving=sum(node>=len(old.args) and args[node] is not None for node in active)
    additions=old_surviving+new_surviving
    combined={t:0 for t in old.inputs}
    for key,node in outputs.items():
        target=key[-1]
        assert not combined[target]&support[node]
        combined[target]|=support[node]
    for target,value in combined.items():
        expected=sum(1<<i for i,t in enumerate(old.inputs) if len(set(t).intersection(target))==1)
        assert value==expected
    bad=[]
    by_core=Counter()
    digest=sha256()
    for node in sorted(active):
        if args[node]:
            a,b=args[node]
            assert a<node and b<node
            assert not support[a]&support[b]
            assert support[node]==support[a]|support[b]
            assert core[node]==core[a]&core[b]
        by_core[core[node].bit_count()]+=1
        if node>=len(old.args) and not core[node]:
            A,stage,local_node=provenance[node]
            assert stage=="graph"
            if not local_criterion[local_node]["nondegenerate"]:
                bad.append({"node":node,"A":A,"local_node":local_node,"criterion":local_criterion[local_node]})
        digest.update(json.dumps((node,args[node],provenance[node]),separators=(",", ":")).encode()+b"\n")
    return {
        "h":h,"template":kind,"original":old_checked,
        "single_exclusion_template":{"n":local.n,"inputs":len(local.inputs),"outputs":len(local.outputs),"additions":local.additions,"all_outputs_exact":True},
        "new_graph":{"additions":additions,"partial_outputs":len(outputs),"roles":additions+len(outputs),"old_additions_retained":old_surviving,"old_additions_removed":old.additions-old_surviving,"new_additions_retained":new_surviving,"new_additions_created":created,"old_nodes_reused_during_construction":reused_old,"new_nodes_reused_during_construction":reused_new,"node_common_point_counts":dict(by_core),"all_additions_disjoint":True,"all_whole_output_coefficients_exact":True,"circuit_sha256":digest.hexdigest()},
        "role_saving":old_checked["roles"]-(additions+len(outputs)),
        "nondegeneracy":{"new_active_degenerate_nodes":len(bad),"first_20":bad[:20],"criterion":"For aggregate over A, source span is a positive line plus incidence span with form I-J/8"},
        "claim_scope":"Exact scalar graph and nondegeneracy screen; no compiled-frame, stage-transfer, or downstream theorem claim",
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",type=int,default=50)
    parser.add_argument("--template",default="paired")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    started=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    result=screen(args.reference,args.h,args.template)
    result.update(started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,reference_commit="bcd4ebde8692383539f8a48734e5fbf3a18a32c2")
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="nondegeneracy"},indent=2,sort_keys=True))
    print("New active degenerate spans:",result["nondegeneracy"]["new_active_degenerate_nodes"])


if __name__=="__main__":
    main()
