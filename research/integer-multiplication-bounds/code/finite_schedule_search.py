#!/usr/bin/env python3
"""Search topological schedules for the exact retained-controller compiler.

This imports the coordinating agent's frame_reuse implementation without
modifying it. Each schedule is represented by an explicit node reindexing,
then compiled by the same fixed maximum-flow chain optimizer. Whole scalar
coefficients and both rational frame directions are checked for every case.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
import heapq
import json
from pathlib import Path
import random
import sys
from types import SimpleNamespace
import time

from finite_block_search import GroupUnion,install_reference,make_block_class
from frame_reuse import labels,optimize_chains,compile_reuse,check


MODES=("id","rank_id","rank_reverse_id","rank_fanout_hi","rank_fanout_lo",
       "rank_support_hi","rank_support_lo","rank_span_id","rank_span_fanout_hi",
       "rank_critical_hi","rank_critical_lo","rank_pressure_hi","rank_random")


def reordered(circuit,spaces,mode,seed=0):
    """Topological relabeling, preserving the physical input/output names."""
    p=len(circuit.inputs)
    assert all(i in circuit.active and circuit.args[i] is None for i in range(1,p+1))
    users={node:[] for node in circuit.active}
    fanout=Counter(circuit.outputs.values())
    for node in circuit.active:
        if circuit.args[node]:
            for child in circuit.args[node]:
                users[child].append(node)
                fanout[child]+=1
    critical={}
    for node in sorted(circuit.active,reverse=True):
        critical[node]=max((critical[parent]+1 for parent in users[node]),default=0)
    support_size={}
    if "support" in mode:
        for node in circuit.active:
            if hasattr(circuit,"h"):
                common=(circuit.core[node]&-circuit.core[node]).bit_length()-1
                support_size[node]=circuit.support_in(node,common).bit_count()
            else:
                support_size[node]=circuit.support[node].bit_count()
    rng=random.Random(seed)
    random_key={node:rng.randrange(1<<62) for node in sorted(circuit.active)} if mode=="rank_random" else {}

    def priority(node):
        dimension=spaces[node].dimension
        if mode=="rank_reverse_id":return (dimension,-node)
        if mode=="rank_fanout_hi":return (dimension,-fanout[node],node)
        if mode=="rank_fanout_lo":return (dimension,fanout[node],node)
        if mode=="rank_support_hi":return (dimension,-support_size[node],node)
        if mode=="rank_support_lo":return (dimension,support_size[node],node)
        if mode=="rank_span_id":return (dimension,spaces[node].common,spaces[node].tags,node)
        if mode=="rank_span_fanout_hi":return (dimension,spaces[node].common,spaces[node].tags,-fanout[node],node)
        if mode=="rank_critical_hi":return (dimension,-critical[node],node)
        if mode=="rank_critical_lo":return (dimension,critical[node],node)
        if mode=="rank_pressure_hi":return (dimension,-sum(fanout[child] for child in circuit.args[node]),node)
        if mode=="rank_random":return (dimension,random_key[node],node)
        return (dimension,node)

    if mode=="id":
        order=sorted(circuit.active)
    else:
        assert mode in MODES
        remaining={node:2 for node in circuit.active if circuit.args[node]}
        order=list(range(1,p+1))
        ready=[]
        for source in order:
            for parent in users[source]:
                remaining[parent]-=1
                if not remaining[parent]:heapq.heappush(ready,(priority(parent),parent))
        while ready:
            _,node=heapq.heappop(ready)
            order.append(node)
            for parent in users[node]:
                remaining[parent]-=1
                if not remaining[parent]:heapq.heappush(ready,(priority(parent),parent))
        assert len(order)==len(circuit.active)
    mapping={old:new for new,old in enumerate(order,1)}
    assert all(mapping[i]==i for i in range(1,p+1))
    args=[None]*(p+1)
    for old in order[p:]:
        node=mapping[old]
        assert node==len(args)
        children=tuple(mapping[child] for child in circuit.args[old])
        assert all(child<node for child in children)
        args.append(children)
    outputs={target:mapping[node] for target,node in circuit.outputs.items()}
    variables={key:mapping[node] for key,node in circuit.variables.items()}
    fields=dict(inputs=circuit.inputs,variables=variables,args=args,active=set(range(1,len(args))),outputs=outputs,additions=circuit.additions)
    if hasattr(circuit,"h"):fields["h"]=circuit.h
    else:fields["n"]=circuit.n
    view=SimpleNamespace(**fields)
    frames={mapping[node]:frame for node,frame in spaces.items()}
    for old in order[p:]:
        assert view.args[mapping[old]]==tuple(mapping[child] for child in circuit.args[old])
    assert all(view.outputs[target]==mapping[node] for target,node in circuit.outputs.items())
    return view,frames,sha256(json.dumps(order,separators=(",", ":")).encode()).hexdigest()


def build(h,ordering,base,reference,sizes=(2,),combine=0):
    install_reference(reference)
    cls=make_block_class()
    if ordering=="gap":
        factory=lambda n,common:cls(n,sizes,base,combine,common//2)
    else:
        factory=lambda n:cls(n,sizes,base,combine)
    circuit=GroupUnion(h,factory,ordering,109,ordering=="gap")
    original=circuit.verify()
    spaces,unique=labels(circuit,global_graph=True)
    return circuit,original,spaces,unique


def evaluate(circuit,original,spaces,unique,mode,seed,dirty=False):
    start=time.monotonic()
    view,frames,schedule_hash=reordered(circuit,spaces,mode,seed)
    plan=optimize_chains(view,frames,"id")
    code=compile_reuse(view,frames,plan)
    checked=check(view,frames,code)
    row={"h":circuit.h,"mode":mode,"seed":seed,"original_roles":original["roles"],"roles":code["roles"],"saving":original["roles"]-code["roles"],"unique_spans":unique,"chains":code["chain_summary"],"checked":checked,"schedule_sha256":schedule_hash,"elapsed_seconds":time.monotonic()-start}
    if dirty:
        from dag_network import exact_invocation
        from frame_reuse_certificate import program
        scalar=program(view,code)
        row["dirty_input_basis_checks"]=[exact_invocation(circuit.h,inv,scalar) for inv in (False,True)]
    return row


def worker(job):
    reference,h,ordering,base,sizes,combine,modes,seeds,dirty,checkpoint=job
    started=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    circuit,original,spaces,unique=build(h,ordering,base,reference,sizes,combine)
    rows=[]
    for mode in modes:
        for seed in seeds if mode=="rank_random" else [0]:
            row=evaluate(circuit,original,spaces,unique,mode,seed,dirty)
            row.update(ordering=ordering,base=base,sizes=sizes,combine=combine,started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat())
            rows.append(row)
            partial={"h":h,"ordering":ordering,"base":base,"sizes":sizes,"combine":combine,"rows":rows,"worker_elapsed_seconds":time.monotonic()-start,"started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat()}
            Path(checkpoint).write_text(json.dumps(partial,indent=2,sort_keys=True)+"\n")
            print(json.dumps({"h":h,"mode":mode,"seed":seed,"roles":row["roles"],"links":row["chains"]["selected_links"],"elapsed_seconds":row["elapsed_seconds"]}),flush=True)
    return {"h":h,"ordering":ordering,"base":base,"rows":rows,"worker_elapsed_seconds":time.monotonic()-start,"started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat()}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",type=int,nargs="+",default=[8,12])
    parser.add_argument("--ordering",default="paired")
    parser.add_argument("--base",type=int,default=4)
    parser.add_argument("--sizes",default="2")
    parser.add_argument("--combine",type=int,choices=[0,1,2],default=0)
    parser.add_argument("--modes",default=",".join(MODES))
    parser.add_argument("--seeds",default="1,109,20261007")
    parser.add_argument("--workers",type=int,default=2)
    parser.add_argument("--dirty",action="store_true")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    assert 1<=args.workers<=4
    modes=args.modes.split(",")
    seeds=[int(seed) for seed in args.seeds.split(",")]
    started=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    # Each worker builds each graph once and caches its exact spaces across modes.
    sizes=tuple(int(size) for size in args.sizes.split(","))
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    jobs=[(args.reference,h,args.ordering,args.base,sizes,args.combine,modes,seeds,args.dirty,output.with_name(output.stem+f"-h{h}-checkpoint.json")) for h in args.h]
    rows=[]
    groups=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(worker,job) for job in jobs]):
            group=future.result()
            groups.append(group)
            rows.extend(group["rows"])
            best=min(group["rows"],key=lambda row:row["roles"])
            print(json.dumps({"h":group["h"],"cases":len(group["rows"]),"best":best,"worker_seconds":group["worker_elapsed_seconds"]}),flush=True)
            import numpy,scipy
            result={"started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat(),"wall_seconds":time.monotonic()-start,"settings":vars(args),"reference_commit":"bcd4ebde8692383539f8a48734e5fbf3a18a32c2","code_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),"compiler_sha256":sha256(Path(__file__).with_name("frame_reuse.py").read_bytes()).hexdigest(),"runtime":{"python":sys.version,"numpy":numpy.__version__,"scipy":scipy.__version__},"rows":rows,"scope":"Exact finite schedule/compiler checks; no optimum over arbitrary schedules or independent multiplication theorem asserted"}
            Path(args.output).parent.mkdir(parents=True,exist_ok=True)
            Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"output":args.output,"cases":len(rows),"wall_seconds":time.monotonic()-start},indent=2))


if __name__=="__main__":
    main()
