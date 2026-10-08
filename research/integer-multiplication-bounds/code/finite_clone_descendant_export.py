#!/usr/bin/env python3
"""Freeze exact delayed-clone links, placement/frame IDs and distinct identity.

Reconstructs and compares the immutable baseline and changed compiled hashes.
No second coefficient or dirty-scratch replay is performed. Large JSON is
written externally and published only as a complete gzip copy.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

from finite_clone_batch import build
from finite_clone_plan_export import tuples,digest
from finite_clone_recovered_witness import compiled_hash,recovered_plan
from finite_clone_descendant_frame import DelayedCloneView,descendant_frames
from finite_block_search import install_reference
from fast_frame_envelope import labels
import frame_reuse


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True);ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();install_reference(args.reference);at=time.monotonic()
    certificate=json.loads(args.certificate.read_text());row=certificate['rows'][0];baseline=json.loads(args.baseline.read_text())
    assert sha256(args.baseline.read_bytes()).hexdigest()==certificate['candidate_input_sha256']
    assert sha256(Path(__file__).with_name('finite_clone_descendant_frame.py').read_bytes()).hexdigest()==certificate['source_sha256']
    original=build(row['h'],row['base'],row['positions']);old_frames,_=labels(original,True)
    old_plan=frame_reuse.optimize_chains(original,old_frames,'rank');old_code=frame_reuse.compile_reuse(original,old_frames,old_plan)
    assert compiled_hash(old_code)==baseline['checked']['compiled_sha256']
    jobs=[dict(job,selected=frozenset(tuples(use) for use in job['selected'])) for job in row['chosen']]
    view=DelayedCloneView(original,old_frames,jobs);frames=descendant_frames(original,old_frames,view,jobs)
    plan=recovered_plan(original,old_plan,view,frames,jobs);code=frame_reuse.compile_reuse(view,frames,plan)
    assert compiled_hash(code)==row['final']['checked']['compiled_sha256'] and code['roles']==row['final']['roles']
    selected=sorted([first,second] for first,second in plan[2].items())
    order=sorted(view.active,key=lambda node:(frames[node].dimension,node))
    locations=[[job['node'],view.clones[job['node']],view.original_mapping[job['clone_frame_owner']]] for job in jobs]
    identity=dict(parent_candidate_id=baseline['candidate_id'],parent_input_sha256=certificate['candidate_input_sha256'],
        clone_edits_sha256=digest(row['chosen']),selected_links_sha256=digest(selected),
        clone_placement_and_frame_owner_sha256=digest(locations),producer_source_sha256=certificate['source_sha256'],
        changed_logical_sha256=row['final']['logical']['circuit_sha256'],compiled_sha256=compiled_hash(code),roles=code['roles'])
    value=dict(status='Terminal exact delayed clone artifact PASS',candidate_id=digest(identity),identity=identity,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        dependency_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in (
            'finite_clone_descendant_frame.py','finite_clone_recovered_witness.py','finite_clone_batch.py',
            'finite_clone_chain_bridge.py','finite_block_search.py','finite_odd_pair_positions.py',
            'finite_singleton_search.py','fast_frame_envelope.py','frame_envelope.py','frame_reuse.py')},
        baseline_sha256=sha256(args.baseline.read_bytes()).hexdigest(),certificate_sha256=sha256(args.certificate.read_bytes()).hexdigest(),
        exact_selected_links=selected,selected_link_count=len(selected),description_count=len(plan[1]),
        descriptions_sha256=digest(plan[1]),node_order_sha256=digest(order),node_count=len(order),
        original_node_mapping_sha256=digest(sorted(view.original_mapping.items())),
        clone_placement_and_frame_owner_ids=locations,clone_count=len(jobs),schedule=plan[4],
        elapsed_seconds=time.monotonic()-at,
        recovery='Reindex original active nodes in canonical old rank/node order; insert each explicit clone immediately before its selected first-use gate (terminal clones at end). Copy original envelopes at original IDs and first-use owner envelope at the clone. Regenerate ordered uses and substitute exact_selected_links. Audit all source/order/capacity/frame constraints and compile/check changed witness independently.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps(dict(candidate_id=value['candidate_id'],roles=code['roles'],links=len(selected),clones=len(jobs),bytes=args.output.stat().st_size,seconds=value['elapsed_seconds'])),flush=True)


if __name__=='__main__':main()
