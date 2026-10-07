#!/usr/bin/env python3
"""Add selected target-orthogonal difference lines to positive support frames.

For a fixed matching, a difference e_a-e_b is available at a node exactly
when a,b lie outside its common core and all descendant physical targets
contain both or neither. Availability persists toward parent gates; adding
all available selected lines to the support envelope therefore preserves
nesting and positivity. The initial input frames remain triple lines.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import sys
import time
from unittest.mock import patch

from finite_block_search import GroupUnion,install_reference,make_block_class
from finite_schedule_search import reordered
from finite_target_frames import TargetSpace,bits,coordinate,included,independent
import frame_reuse


def matching(h,mode,seed,count):
    if mode=="none":return []
    vertices=list(range(h))
    if mode=="shifted":vertices=vertices[1:]+vertices[:1]
    elif mode=="random":random.Random(seed).shuffle(vertices)
    else:assert mode=="aligned"
    pairs=[tuple(sorted(vertices[index:index+2])) for index in range(0,h,2)]
    return pairs if count is None else pairs[:count]


def labels(circuit,selected):
    h=circuit.h
    all_pairs=list(combinations(range(h),2))
    ids={pair:index for index,pair in enumerate(all_pairs)}
    omitted={node:0 for node in circuit.active}
    for (common,target),node in circuit.outputs.items():
        pair=tuple(vertex for vertex in target if vertex!=common)
        omitted[node]|=1<<ids[pair]
    for node in sorted(circuit.active,reverse=True):
        if circuit.args[node]:
            for child in circuit.args[node]:omitted[child]|=omitted[node]
    bad=[sum(1<<index for index,pair in enumerate(all_pairs) if (a in pair) != (b in pair))
         for a,b in selected]
    frames={}
    intern={}
    augmented=extra_dimensions=0
    for node in sorted(circuit.active):
        core=circuit.core[node]
        free=circuit.union[node]&~core
        negative=[]
        for (a,b),forbidden in zip(selected,bad):
            pair=(1<<a)|(1<<b)
            if core&pair or omitted[node]&forbidden:continue
            present=free&pair
            if present:
                free|=pair
            else:
                negative.append((1<<a,1<<b))
        components=tuple(sorted([(1<<vertex,0) for vertex in bits(free)]+negative,
                                key=lambda component:(component[0]&-component[0]).bit_length()))
        frame=TargetSpace(h,core,components)
        frames[node]=intern.setdefault((core,components),frame)
        if core.bit_count()==3:
            assert frame.dimension==1 and not components
        old_dimension=(circuit.union[node].bit_count()-core.bit_count()) if core.bit_count()<3 else 1
        augmented+=frame.dimension>old_dimension
        extra_dimensions+=frame.dimension-old_dimension
        if circuit.args[node]:
            assert all(included(frames[child],frame) for child in circuit.args[node])
    for triple,node in circuit.variables.items():
        assert frames[node].core==sum(1<<vertex for vertex in triple)
        assert frames[node].dimension==1 and frames[node].basis==((1,0,0,0),)
    checked=0
    for (common,target),node in circuit.outputs.items():
        frame=frames[node]
        assert frame.core&(1<<common)
        assert sum(bool(frame.core&(1<<vertex)) for vertex in target)==1
        for column in frame.basis:
            assert sum(coordinate(frame,column,vertex) for vertex in target)==column[0]
            checked+=1
    return frames,{"unique_rational_frames":len(intern),"selected_matching":selected,
                   "augmented_nodes":augmented,"sum_added_dimensions":extra_dimensions,
                   "source_triple_lines_checked":len(circuit.inputs),
                   "physical_target_pairings_checked":checked,"all_original_edges_nested":True,
                   "frame_family":"Support envelope plus selected available zero-sum matching difference lines",
                   "nondegeneracy":"Subspace of positive common-core total-sum envelope"}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",type=int,nargs="+",default=[8,12])
    parser.add_argument("--base",type=int,default=4)
    parser.add_argument("--sizes",default="2")
    parser.add_argument("--combine",type=int,choices=[0,1,2],default=0)
    parser.add_argument("--pair-mode",choices=["none","aligned","shifted","random"],default="aligned")
    parser.add_argument("--count",type=int)
    parser.add_argument("--seed",type=int,default=109)
    parser.add_argument("--schedule",default="rank_id")
    parser.add_argument("--independent",action="store_true")
    parser.add_argument("--dirty",action="store_true")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    install_reference(args.reference)
    block_class=make_block_class()
    sizes=tuple(map(int,args.sizes.split(",")))
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    rows=[]
    for h in args.h:
        case_start=time.monotonic()
        circuit=GroupUnion(h,lambda n:block_class(n,sizes,args.base,args.combine),"paired")
        original=circuit.verify()
        frames,metadata=labels(circuit,matching(h,args.pair_mode,args.seed,args.count))
        rational=independent(circuit,frames,args.seed) if args.independent else {}
        view,spaces,schedule_hash=reordered(circuit,frames,args.schedule,args.seed)
        with patch.object(frame_reuse,"included",included):
            compiled=frame_reuse.compile_reuse(view,spaces,frame_reuse.optimize_chains(view,spaces,"id"))
            checked=frame_reuse.check(view,spaces,compiled)
        row={"h":h,"original":original,"original_roles":original["roles"],"roles":compiled["roles"],
             "chains":compiled["chain_summary"],"checked":checked,"frames":metadata,
             "independent":rational,"schedule_sha256":schedule_hash,
             "elapsed_seconds":time.monotonic()-case_start}
        if args.dirty:
            from dag_network import exact_invocation
            from frame_reuse_certificate import program
            scalar=program(view,compiled)
            row["dirty_input_basis_checks"]=[exact_invocation(h,inverse,scalar) for inverse in (False,True)]
        rows.append(row)
        import numpy,scipy
        result={"started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat(),
                "wall_seconds":time.monotonic()-start,"settings":vars(args),"rows":rows,
                "reference_commit":"bcd4ebde8692383539f8a48734e5fbf3a18a32c2",
                "runtime":{"python":sys.version,"numpy":numpy.__version__,"scipy":scipy.__version__},
                "source_sha256":{name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ("finite_selected_target_frames.py","finite_target_frames.py","finite_schedule_search.py","finite_block_search.py","frame_reuse.py")},
                "scope":"Exact finite positive selected-target-frame/compiler witness; full three-stage transfer not claimed"}
        output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print(json.dumps(row),flush=True)
        included.cache_clear()
        GroupUnion.support_in.cache_clear()
    print(json.dumps({"output":str(output),"cases":len(rows),"wall_seconds":time.monotonic()-start}),flush=True)


if __name__=="__main__":
    main()
