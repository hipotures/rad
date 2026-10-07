#!/usr/bin/env python3
"""Bounded exact local block schedule search with persistent row checkpoints."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product
import json
from pathlib import Path
import time

from finite_block_search import install_reference, make_block_class


def worker(job):
    reference, n, sizes, base, combine = job
    install_reference(reference)
    cls = make_block_class()
    start = time.monotonic()
    circuit = cls(n, sizes, base, combine)
    checked = circuit.verify()
    return {
        "n": n, "sizes": list(sizes), "base": base, "combine": combine,
        "additions": circuit.additions, "roles": checked["scratch_roles"],
        "circuit_sha256": checked["circuit_sha256"],
        "all_output_supports_exact": True, "all_additions_disjoint": True,
        "elapsed_seconds": time.monotonic()-start,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--n", type=int, default=49)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--max-size", type=int, default=4)
    parser.add_argument("--levels", type=int, default=3)
    args = parser.parse_args()
    assert 1 <= args.workers <= 4
    schedules = list(product(range(2, args.max_size+1), repeat=args.levels))
    jobs = [(args.reference,args.n,s,b,c) for s in schedules for b in range(2,8) for c in range(3)]
    start = time.monotonic()
    rows = []
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.output).open("x") as stream, ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(worker,j) for j in jobs]
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            stream.write(json.dumps(row,sort_keys=True)+"\n")
            stream.flush()
            if len(rows)%50 == 0:
                best = min(rows,key=lambda r:r["additions"])
                print(json.dumps({"completed":len(rows),"jobs":len(jobs),"best":best,"wall_seconds":time.monotonic()-start}),flush=True)
    rows.sort(key=lambda r:(r["additions"],r["sizes"],r["base"],r["combine"]))
    result = {"reference_commit":"bcd4ebde8692383539f8a48734e5fbf3a18a32c2","settings":vars(args),"jobs":len(rows),"wall_seconds":time.monotonic()-start,"summed_case_seconds":sum(r["elapsed_seconds"] for r in rows),"best_30":rows[:30],"scope":"Bounded schedule enumeration, not a lower bound or transferred multiplication claim"}
    Path(args.summary).parent.mkdir(parents=True,exist_ok=True)
    Path(args.summary).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
