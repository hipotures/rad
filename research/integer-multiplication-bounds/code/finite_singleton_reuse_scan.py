#!/usr/bin/env python3
"""Actual role screen across all globally aligned singleton gaps.

Every case checks the complete finite map, positive support envelopes,
physical target orthogonality, scalar compilation and both frame directions.
The local diagnostic and full global objective are explicitly distinguished.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

from finite_singleton_search import singleton_class
from finite_block_search import GroupUnion,install_reference
from frame_envelope import labels,target_check
from frame_reuse import optimize_chains,compile_reuse,check,included


def case(job):
    reference,h,base,kind,parameter=job
    install_reference(reference)
    cls=singleton_class()
    started=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    if kind=="local":
        positions=[parameter]
        circuit=cls(h-1,parameter,base)
        global_graph=False
    else:
        gap=parameter
        positions=[gap if common//2<=gap else gap+1 for common in range(h)]
        assert all(0<=position<h//2 for position in positions)
        circuit=GroupUnion(h,lambda n,common:cls(n,positions[common],base),"paired",0,True)
        global_graph=True
    original=circuit.verify()
    frames,metadata=labels(circuit,global_graph)
    code=compile_reuse(circuit,frames,optimize_chains(circuit,frames,"rank"))
    checked=check(circuit,frames,code)
    targets=target_check(circuit,frames,global_graph)
    row={"kind":kind,"h":h,"base":base,"parameter":parameter,"positions":positions,
         "original":original,"original_roles":circuit.additions+len(circuit.outputs),
         "compiled_roles":code["roles"],"chains":code["chain_summary"],"checked":checked,
         "frames":metadata,"targets":targets,"elapsed_seconds":time.monotonic()-start,
         "started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat()}
    included.cache_clear()
    GroupUnion.support_in.cache_clear()
    return row


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",type=int,default=50)
    parser.add_argument("--base",type=int,default=4)
    parser.add_argument("--kind",choices=["local","global"],default="global")
    parser.add_argument("--parameters",default="all")
    parser.add_argument("--workers",type=int,default=4)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    assert args.h>=6 and args.h%2==0 and 1<=args.workers<=4
    choices=args.h//2
    parameters=(list(range(choices)) if args.kind=="local" else list(range(-1,choices))) if args.parameters=="all" else list(map(int,args.parameters.split(",")))
    jobs=[(args.reference,args.h,args.base,args.kind,parameter) for parameter in parameters]
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    assert not output.exists(),"Use a fresh output path"
    started=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    rows=[]
    source={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ("finite_singleton_reuse_scan.py","finite_singleton_search.py","finite_block_search.py","frame_envelope.py","frame_reuse.py")}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(case,job) for job in jobs]):
            row=future.result()
            rows.append(row)
            best=min(rows,key=lambda value:value["compiled_roles"])
            import numpy,scipy
            result={"started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat(),
                    "wall_seconds":time.monotonic()-start,"settings":vars(args),"completed_cases":len(rows),
                    "planned_cases":len(jobs),"rows":rows,"best":best,
                    "runtime":{"python":sys.version,"numpy":numpy.__version__,"scipy":scipy.__version__},
                    "reference_commit":"bcd4ebde8692383539f8a48734e5fbf3a18a32c2","source_sha256":source,
                    "scope":"Actual compiled roles for this bounded singleton family; exact finite map/frame/target checks; dirty-stage transfer not claimed"}
            output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
            print(json.dumps({"kind":row["kind"],"parameter":row["parameter"],"R":row["compiled_roles"],
                              "before_R":row["original_roles"],"retained":row["chains"]["selected_links"],
                              "best_R":best["compiled_roles"],"case":len(rows)}),flush=True)
    print(json.dumps({"output":str(output),"cases":len(rows),"wall_seconds":time.monotonic()-start}),flush=True)


if __name__=="__main__":main()
