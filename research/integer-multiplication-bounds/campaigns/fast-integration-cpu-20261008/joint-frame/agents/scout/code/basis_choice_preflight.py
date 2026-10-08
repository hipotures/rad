#!/usr/bin/env python3
"""Exact early discriminator for a duplicate complementary matrix choice.

This rebuilds the complete original graph and matching, then compares every
regional ordered invertible row matrix before expensive physical reclamation.
An identical row matrix at every region implies an identical deterministic
word for a fixed acquire policy. It does not replace word checks for a change.
"""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time
from future_retirement_basis import candidate_factory
from joint_match_components import load_source


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root',required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=[23,25])
    ap.add_argument('--policies',default='output,output-reverse')
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args();assert __debug__ and not args.output.exists()
    start=time.monotonic();compiler=load_source(args.source_root.resolve())
    c,blocks,uses,value_uses,owner,signal,order,contains=compiler.build(args.h)
    edges,chosen,right,stats=compiler.match(blocks,uses,True)
    results=[]
    for policy in args.policies.split(','):
        candidates=candidate_factory(policy);changes=[];checked=0
        for g in order:
            b=blocks[g]
            if b['source']:continue
            initial=[];echelon=[]
            values=sorted({uses[u][0] for u in b['uses'] if u not in right})
            assert values==b['outvalues']
            for x in values:
                row=b['coeff'][x]
                if compiler.independent(echelon,row):initial.append(row);echelon=compiler.basis(initial)
            for e in sorted(b['selected']):
                row=1<<edges[e][2];assert compiler.independent(echelon,row)
                initial.append(row);echelon=compiler.basis(initial)
            def finish(offered):
                rows=initial.copy();basis=compiler.basis(rows)
                for row in offered:
                    if compiler.independent(basis,row):rows.append(row);basis=compiler.basis(rows)
                assert len(rows)==len(b['inputs'])
                return rows
            baseline=finish([1<<i for i in range(len(b['inputs']))])
            modified=finish(candidates(b,g,blocks,uses,value_uses,order,contains,signal))
            checked+=1
            if baseline!=modified:changes.append(dict(region=g,frame=b['frame'],old_rows=baseline,new_rows=modified))
        results.append(dict(policy=policy,checked_nonsource_regions=checked,changed_regions=len(changes),
            exactly_identical_regional_matrices=not changes,changes=changes))
    output=dict(status='EXACT FULL GRAPH COMPLEMENT CHOICE DISCRIMINATOR COMPLETE',
        recorded_utc=datetime.now(timezone.utc).isoformat(),h=args.h,native_threads=1,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        candidate_helper_sha256=sha256(Path(__file__).with_name('future_retirement_basis.py').read_bytes()).hexdigest(),
        graph_source_sha256=sha256((args.source_root/'references/frame-compiler/pr55/research/skip-suffix/skip_graph.py').read_bytes()).hexdigest(),
        matching_edges=len(edges),matching_cardinality=len(chosen),policies=results,
        limitation='Duplicate conclusion assumes the same original graph, matching and acquire policy. Retired row label indices are unused; physical word depends on ordered rows. Any changed matrix still needs full word/profile review.',
        seconds=time.monotonic()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ['status','h','seconds']}));print(json.dumps([{k:r[k] for k in ['policy','checked_nonsource_regions','changed_regions','exactly_identical_regional_matrices']} for r in results]))


if __name__=='__main__':main()
