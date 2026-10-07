#!/usr/bin/env python3
"""Compare block graph alternatives by their actual compiled role count.

Each independent case verifies its complete monotone global map, constructs
the exact rational source-span frames, compiles a rank-prioritized legal
schedule, and checks scalar coefficients and both frame directions. This is
a bounded family screen, not an optimum over arbitrary circuits.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys
import time

from finite_schedule_search import build,evaluate
from finite_block_search import GroupUnion
from frame_reuse import included


def case(job):
    reference,h,ordering,sizes,base,combine=job
    started=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    circuit,original,spaces,unique=build(h,ordering,base,reference,sizes,combine)
    row=evaluate(circuit,original,spaces,unique,"rank_id",0)
    row.update(ordering=ordering,sizes=sizes,base=base,combine=combine,
               started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),
               total_seconds=time.monotonic()-start,
               global_graph_sha256=original["circuit_sha256"])
    included.cache_clear()
    GroupUnion.support_in.cache_clear()
    return row


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",type=int,nargs="+",default=[8,12,16,20])
    parser.add_argument("--orderings",default="paired")
    parser.add_argument("--size-patterns",default="2;2,3;2,4;3,2;4,2;3;4")
    parser.add_argument("--bases",default="2,4,6")
    parser.add_argument("--combines",default="0,1,2")
    parser.add_argument("--workers",type=int,default=2)
    parser.add_argument("--rows",required=True)
    parser.add_argument("--summary",required=True)
    args=parser.parse_args()
    assert 1<=args.workers<=4
    sizes=[tuple(map(int,pattern.split(","))) for pattern in args.size_patterns.split(";")]
    jobs=[(args.reference,h,ordering,pattern,base,combine)
          for h,ordering,pattern,base,combine in product(args.h,args.orderings.split(","),sizes,map(int,args.bases.split(",")),map(int,args.combines.split(",")))]
    start=time.monotonic()
    started=datetime.now(timezone.utc).isoformat()
    output=Path(args.rows)
    summary=Path(args.summary)
    output.parent.mkdir(parents=True,exist_ok=True)
    summary.parent.mkdir(parents=True,exist_ok=True)
    rows=[]
    assert not output.exists(), "Use a fresh run path; rows must not overwrite evidence"
    with output.open("x") as handle,ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(case,job) for job in jobs]):
            row=future.result()
            rows.append(row)
            handle.write(json.dumps(row,sort_keys=True)+"\n")
            handle.flush()
            best=min((r for r in rows if r["h"]==row["h"]),key=lambda r:r["roles"])
            print(json.dumps({"case":len(rows),"h":row["h"],"R":row["roles"],"precompile_R":row["original_roles"],"sizes":row["sizes"],"base":row["base"],"combine":row["combine"],"best_R":best["roles"]}),flush=True)
    import numpy,scipy
    result={"started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat(),
            "wall_seconds":time.monotonic()-start,"cases":len(rows),"settings":vars(args),
            "reference_commit":"bcd4ebde8692383539f8a48734e5fbf3a18a32c2",
            "runtime":{"python":sys.version,"numpy":numpy.__version__,"scipy":scipy.__version__},
            "source_sha256":{name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ("finite_reuse_graph_scan.py","finite_schedule_search.py","finite_block_search.py","frame_reuse.py")},
            "best_per_h":{str(h):min((r for r in rows if r["h"]==h),key=lambda r:r["roles"]) for h in args.h},
            "rows_path":str(output),"rows_sha256":sha256(output.read_bytes()).hexdigest(),
            "scope":"Complete exact finite map/frame checks for this bounded family; no dirty-stage transfer or optimum over arbitrary graphs claimed"}
    summary.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"summary":str(summary),"cases":len(rows),"wall_seconds":result["wall_seconds"]}),flush=True)


if __name__=="__main__":
    main()
