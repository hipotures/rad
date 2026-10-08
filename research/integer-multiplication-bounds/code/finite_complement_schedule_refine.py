#!/usr/bin/env python3
"""Alternate exact recovered frame choices and legal actual-rank schedules.

After binary frame/controller selection, sorting by the chosen frame ranks
preserves every strict retained inclusion and the old ID orientation of
equal frames. It can expose new narrow-to-complement links that a narrow
rank schedule placed in the opposite chronology. All compilers/checks remain
unchanged and each adopted candidate is recovered explicitly.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time
from unittest.mock import patch

from finite_block_search import GroupUnion,install_reference
from finite_singleton_search import singleton_class
from finite_schedule_search import reordered
from finite_adaptive_complements import alternatives,included,target_check,independent
from finite_label_milp import solve
import frame_reuse


def rank_reorder(circuit,choices,frames,original_ids):
    view,labels,digest=reordered(circuit,frames,"rank_id",109)
    order=sorted(circuit.active,key=lambda node:(frames[node].dimension,node))
    mapping={old:new for new,old in enumerate(order,1)}
    assert all(view.args[mapping[node]]==tuple(mapping[child] for child in circuit.args[node])
               for node in circuit.active if circuit.args[node])
    assert all(view.outputs[key]==mapping[node] for key,node in circuit.outputs.items())
    return (view,{mapping[n]:value for n,value in choices.items()},labels,
            {mapping[n]:original_ids[n] for n in circuit.active},digest)


def compiled(circuit,frames):
    with patch.object(frame_reuse,"included",included):
        code=frame_reuse.compile_reuse(circuit,frames,frame_reuse.optimize_chains(circuit,frames,"id"))
        checked=frame_reuse.check(circuit,frames,code)
    return code,checked


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",type=int,nargs="+",default=[12,16,20])
    parser.add_argument("--gap",type=int)
    parser.add_argument("--iterations",type=int,default=8)
    parser.add_argument("--time-limit",type=float,default=60)
    parser.add_argument("--dirty",action="store_true")
    parser.add_argument("--independent",action="store_true")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();install_reference(args.reference)
    assert not args.output.exists(),"Use a fresh output path"
    args.output.parent.mkdir(parents=True,exist_ok=True)
    start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    names=("finite_complement_schedule_refine.py","finite_adaptive_complements.py","finite_label_milp.py",
        "finite_adaptive_cores.py","finite_schedule_search.py","finite_singleton_search.py",
        "finite_block_search.py","frame_envelope.py","frame_reuse.py")
    source={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names}
    rows=[]
    for h in args.h:
        begin=time.monotonic();gap=h//2-1 if args.gap is None else args.gap
        cls=singleton_class();positions=[gap if c//2<=gap else gap+1 for c in range(h)]
        original=GroupUnion(h,lambda n,c:cls(n,positions[c],4),"paired",0,True)
        graph=original.verify();choices,targets,omitted,pairs,metadata=alternatives(original)
        extra=independent(original,choices,targets,omitted,pairs) if args.independent else {}
        narrow={node:frames[0] for node,frames in choices.items()}
        circuit,choices,current,ids,schedule_sha=rank_reorder(original,choices,narrow,{n:n for n in original.active})
        code,checked=compiled(circuit,current);baseline=code["roles"]
        history=[]
        for iteration in range(args.iterations):
            frames,plan,milp=solve(circuit,choices,included,args.time_limit)
            with patch.object(frame_reuse,"included",included):
                mixed=frame_reuse.compile_reuse(circuit,frames,plan)
                frame_reuse.check(circuit,frames,mixed)
            best,proof=compiled(circuit,frames)
            if best["roles"]>code["roles"]:
                assert not milp["solver_reported_optimal"]
                frames=current;best=code;proof=checked
            old_role=best["roles"]
            chosen_original=[ids[node] for node,frame in frames.items() if frame!=choices[node][0]]
            circuit,choices,current,ids,new_schedule=rank_reorder(circuit,choices,frames,ids)
            new_code,new_checked=compiled(circuit,current)
            assert new_code["roles"]<=old_role,"Actual-rank reordering must preserve the previous valid retained links"
            compact={key:value for key,value in milp.items() if key not in ("selected_link_user_pairs","selected_relevant_wide_nodes")}
            compact.update(iteration=iteration,before_rank_roles=old_role,after_rank_roles=new_code["roles"],
                chosen_original_wide_node_ids=chosen_original,schedule_sha256=new_schedule,
                compiled_sha256=new_checked["compiled_sha256"])
            history.append(compact)
            unchanged=new_schedule==schedule_sha
            schedule_sha=new_schedule;code,checked=new_code,new_checked
            print(json.dumps(dict(h=h,iteration=iteration,before_rank=old_role,roles=code["roles"],
                wide=len(chosen_original),unchanged_schedule=unchanged)),flush=True)
            if unchanged:break
        row=dict(h=h,gap=gap,positions=positions,graph=graph,positive_baseline_roles=baseline,
            roles=code["roles"],frame_metadata=metadata,independent=extra,history=history,
            checked=checked,physical_targets=target_check(circuit,current),final_schedule_sha256=schedule_sha,
            final_original_wide_node_ids=[ids[n] for n,frame in current.items() if frame!=choices[n][0]])
        if args.dirty:
            from dag_network import exact_invocation
            from frame_reuse_certificate import program
            row["dirty_basis"]=[exact_invocation(h,inverse,program(circuit,code)) for inverse in (False,True)]
        row["elapsed_seconds"]=time.monotonic()-begin;rows.append(row)
        result=dict(settings={**vars(args),"output":str(args.output)},started_utc=started,
            completed_utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,
            reference_commit="bcd4ebde8692383539f8a48734e5fbf3a18a32c2",source_sha256=source,rows=rows,
            scope="Exact recovered mixed nondegenerate finite labels and monotone actual-role schedule refinement; generic projector transfer and analytic promotion remain separate")
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        included.cache_clear();GroupUnion.support_in.cache_clear()


if __name__=="__main__":main()
