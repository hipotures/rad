#!/usr/bin/env python3
"""Independent exhaustive matching and exact old/new selection controls."""
from __future__ import annotations
import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path
import time

import finite_clone_capacity_matching as old
import finite_clone_capacity_fast as fast
from finite_clone_batch import serialized
from finite_clone_recovered_witness import compiled_hash
from fast_frame_envelope import labels
import frame_reuse


def canonical(jobs):
    return json.loads(json.dumps([serialized(job) for job in jobs],sort_keys=True))


def brute(edges):
    best=0
    for mask in range(1<<len(edges)):
        used=set();count=0
        for i,edge in enumerate(edges):
            if not (mask>>i)&1:continue
            if used.intersection(edge):break
            used.update(edge);count+=1
        else:best=max(best,count)
    return best


def exhaustive():
    count=0;comparisons=0
    for n in range(1,6):
        options=[[None,*[q for q in range(n) if q!=p]] for p in range(n)]
        for targets in itertools.product(*options):
            jobs=[dict(node=p,predecessor_gates=[p,q]) for p,q in enumerate(targets) if q is not None]
            edges=sorted({tuple(sorted((p,q))) for p,q in enumerate(targets) if q is not None})
            maximum=brute(edges)
            for seed in (0,-1,1,2):
                first,choices,diag=old.capacity_matching(jobs,seed)
                second,choices_new,diag_new=fast.capacity_matching(jobs,seed)
                assert first==second and choices==choices_new and diag==diag_new
                assert len(first)==maximum
                comparisons+=1
            count+=1
    return dict(functional_capacity_graphs=count,seeds_per_graph=4,exact_matching_comparisons=comparisons,
        maximum_ground_vertices=5,maximum_cardinality_checked_by_exhaustive_edge_subsets=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True);ap.add_argument('--control',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();old.witness.install_reference(args.reference)
    at=time.monotonic();value=dict(exhaustive=exhaustive(),rows=[],
        old_source_sha256=sha256(Path(old.__file__).read_bytes()).hexdigest(),
        fast_source_sha256=sha256(Path(fast.__file__).read_bytes()).hexdigest(),
        old_small_control_sha256=sha256(args.control.read_bytes()).hexdigest())
    saved=json.loads(args.control.read_text());assert saved['source_sha256']==value['old_source_sha256']
    for row in saved['rows']:
        original=old.witness.build(row['h'],row['base'],row['positions'])
        assert original.verify()==row['baseline']['logical']
        frames,_=labels(original,True);plan=frame_reuse.optimize_chains(original,frames,'rank')
        code=frame_reuse.compile_reuse(original,frames,plan)
        assert compiled_hash(code)==row['baseline']['compiled_sha256']
        jobs,diag=old.witness.opportunities(original,frames,plan)
        before=time.monotonic();first,_=old.select(jobs);old_seconds=time.monotonic()-before
        before=time.monotonic();second,_=fast.select(jobs);fast_seconds=time.monotonic()-before
        assert canonical(first)==canonical(second)==row['chosen']
        digest=sha256(json.dumps(canonical(first),sort_keys=True,separators=(',',':')).encode()).hexdigest()
        value['rows'].append(dict(h=row['h'],eligible=len(jobs),selected=len(first),
            canonical_complete_edit_list_sha256=digest,old_seconds=old_seconds,fast_seconds=fast_seconds,
            baseline_compiled_sha256=compiled_hash(code),unchanged_complete_dirty_witness_reused=True))
        frame_reuse.included.cache_clear();old.witness.GroupUnion.support_in.cache_clear()
    value.update(status='Terminal exact matching and complete selection identity PASS',elapsed_seconds=time.monotonic()-at)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print(json.dumps(value,sort_keys=True),flush=True)


if __name__=='__main__':main()
