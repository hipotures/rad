#!/usr/bin/env python3
"""Optimize the paired singleton position independently in every point group.

All complete global pairs stay intact. Only the location of the common
point's unmatched mate changes. Global star sharing is a pairwise discrete
objective: every pair-star can occur in only its two common-point groups.
The exact before-pruning interner count is therefore local additions minus
the sum of pairwise intersection counts. Promoted candidates need complete
global compilation/frame checks, provided by --full.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import random
import sys
import time

from finite_block_search import GroupUnion,install_reference,make_block_class
from finite_ground_scan import local_geometry,translations


def singleton_class():
    base_class=make_block_class()

    class SingletonCircuit(base_class):
        def __init__(self,n,position,base=4):
            self.position=position
            super().__init__(n,(2,),base,0,position)

        def pair(self,points):
            mate=points[-1]
            others=points[:-1]
            position=2*self.position
            order=others[:position]+[mate]+others[position:]
            edges={tuple(sorted((a,b))):self.variables[tuple(sorted((a,b)))]
                   for a,b in combinations(order,2)}
            return self.block(order,edges,{point:0 for point in order},0)

    return SingletonCircuit


def table(h,base):
    import numpy as np
    cls=make_block_class()
    choices=h//2
    local=[]
    counts=[]
    digests=[]
    for position in range(choices):
        circuit=cls(h-1,(2,),base,0,position)
        checked=circuit.verify()
        stars,nonstar=local_geometry(circuit)
        local.append(stars)
        counts.append(circuit.additions)
        digests.append(checked["circuit_sha256"])
    mapped=[]
    for common in range(h):
        by_choice=[]
        others=[point for point in range(h) if point//2!=common//2]
        for position in range(choices):
            points=others[:2*position]+[common^1]+others[2*position:]
            translate=translations(points)
            groups={point:set() for point in points}
            cache={}
            for fixed,mask in local[position]:
                if mask not in cache:cache[mask]=translate(mask)
                groups[points[fixed]].add(cache[mask])
            by_choice.append(groups)
        mapped.append(by_choice)
    scores=np.zeros((h,h,choices,choices),dtype=np.uint16)
    for a,b in combinations(range(h),2):
        for p in range(choices):
            left=mapped[a][p][b]
            for q in range(choices):
                value=len(left&mapped[b][q][a])
                assert value<65536
                scores[a,b,p,q]=scores[b,a,q,p]=value
    return scores,counts,digests


def objective(positions,scores,counts):
    h=len(positions)
    merged=sum(int(scores[a,b,positions[a],positions[b]]) for a,b in combinations(range(h),2))
    additions=sum(counts[position] for position in positions)-merged
    return additions+h*comb(h-1,2)


def descent(positions,scores,counts,rng):
    import numpy as np
    positions=list(positions)
    h=len(positions)
    old=objective(positions,scores,counts)
    sweeps=0
    while True:
        changed=False
        order=list(range(h))
        rng.shuffle(order)
        for common in order:
            costs=np.asarray(counts,dtype=np.int64).copy()
            for other in range(h):
                if common!=other:costs-=scores[common,other,:,positions[other]]
            minimum=int(costs.min())
            current=positions[common]
            if int(costs[current])==minimum:continue
            selected=int(np.flatnonzero(costs==minimum)[0])
            old+=int(costs[selected])-int(costs[current])
            positions[common]=selected
            changed=True
        sweeps+=1
        assert old==objective(positions,scores,counts)
        if not changed:return positions,old,sweeps


def full(h,positions,base):
    from frame_envelope import labels,target_check
    from frame_reuse import optimize_chains,compile_reuse,check
    cls=singleton_class()
    circuit=GroupUnion(h,lambda n,common:cls(n,positions[common],base),"paired",0,True)
    original=circuit.verify()
    frames,metadata=labels(circuit,True)
    plan=optimize_chains(circuit,frames,"rank")
    code=compile_reuse(circuit,frames,plan)
    checked=check(circuit,frames,code)
    targets=target_check(circuit,frames,True)
    return {"global":original,"compiled_roles":code["roles"],"chains":code["chain_summary"],
            "checked":checked,"frames":metadata,"targets":targets}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",type=int,default=50)
    parser.add_argument("--base",type=int,default=4)
    parser.add_argument("--seed",type=int,default=109)
    parser.add_argument("--starts",type=int,default=128)
    parser.add_argument("--tables",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--full",action="store_true")
    args=parser.parse_args()
    assert args.h>=6 and args.h%2==0
    install_reference(args.reference)
    started=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    scores,counts,digests=table(args.h,args.base)
    import numpy as np
    table_path=Path(args.tables)
    table_path.parent.mkdir(parents=True,exist_ok=True)
    assert not table_path.exists(),"Use a fresh table artifact path"
    np.savez_compressed(table_path,scores=scores,local_additions=np.asarray(counts,dtype=np.int64))
    choices=args.h//2
    initial=[[choices-1]*args.h,[0]*args.h,[common//2 for common in range(args.h)],[choices//2]*args.h]
    rng=random.Random(args.seed)
    initial.extend([[rng.randrange(choices) for _ in range(args.h)] for _ in range(max(0,args.starts-4))])
    rows=[]
    best=None
    for index,positions in enumerate(initial):
        final,cost,sweeps=descent(positions,scores,counts,rng)
        row={"start":index,"initial_before_pruning_R":objective(positions,scores,counts),
             "final_before_pruning_R":cost,"sweeps":sweeps,"positions":final}
        rows.append(row)
        if best is None or cost<best["final_before_pruning_R"]:
            best=row
            print(json.dumps({"phase":"best","start":index,"R":cost,"positions":final}),flush=True)
    result={"started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat(),
            "wall_seconds":time.monotonic()-start,"settings":vars(args),
            "reference_commit":"bcd4ebde8692383539f8a48734e5fbf3a18a32c2",
            "local_additions_by_position":counts,"local_circuit_sha256_by_position":digests,
            "baseline_before_pruning_R":objective([choices-1]*args.h,scores,counts),
            "best":best,"rows":rows,"table_artifact":{"path":str(table_path),"bytes":table_path.stat().st_size,
            "sha256":sha256(table_path.read_bytes()).hexdigest(),"recovery":"Deterministically regenerated by this source and recorded settings"},
            "source_sha256":{name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ("finite_singleton_search.py","finite_ground_scan.py","finite_block_search.py","frame_reuse.py","frame_envelope.py")},
            "scope":"Exact local maps and pairwise before-pruning sharing objective; full compiled checks only when --full is used"}
    if args.full:result["full_candidate"]=full(args.h,best["positions"],args.base)
    result["completed_utc"]=datetime.now(timezone.utc).isoformat()
    result["wall_seconds"]=time.monotonic()-start
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"output":str(output),"best_R":best["final_before_pruning_R"],"wall_seconds":result["wall_seconds"]}),flush=True)


if __name__=="__main__":main()
