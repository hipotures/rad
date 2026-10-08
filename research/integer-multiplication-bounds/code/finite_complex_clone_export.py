#!/usr/bin/env python3
"""Export exact complex-clone reconstruction identities without physical replay."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch
import finite_complex_delayed_clones as witness
from finite_clone_recovered_witness import compiled_hash, recovered_plan
import frame_reuse


def digest(value):return sha256(json.dumps(value,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def frozen(value):return tuple(frozen(item) for item in value) if isinstance(value,list) else value
def restored(job):
    job=dict(job);job['selected']=frozenset((kind,frozen(owner)) for kind,owner in job['selected']);return job


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    row=json.loads(args.candidate.read_text());assert row['witness_source_sha256']==sha256(Path(witness.__file__).read_bytes()).hexdigest()
    original=witness.TripleSideCircuit(row['h']);assert witness.logical_identity(original)==row['original_logical_sha256']
    old_frames,_=witness.binary.labels(original);jobs=[restored(job) for job in row['chosen']]
    with patch.object(frame_reuse,'included',witness.binary.admissible):
        old_plan=frame_reuse.optimize_chains(original,old_frames,'rank');old_code=frame_reuse.compile_reuse(original,old_frames,old_plan)
        assert compiled_hash(old_code)==row['original_compiled_sha256'] and old_code['roles']==row['baseline_roles']
        view=witness.ComplexCloneView(original,old_frames,jobs)
        frames={view.original_mapping[node]:old_frames[node] for node in original.active}
        for job in jobs:frames[view.clones[job['node']]]=old_frames[job['clone_frame_owner']]
        plan=recovered_plan(original,old_plan,view,frames,jobs);code=frame_reuse.compile_reuse(view,frames,plan)
    assert code['roles']==row['compiled_roles'] and compiled_hash(code)==row['checked']['compiled_sha256']
    order=sorted(view.active,key=lambda node:(frames[node].dimension,node));uses=plan[1];links=sorted(plan[2].items())
    provenance=[dict(original_node=job['node'],original_mapping=view.original_mapping[job['node']],
        clone_node=view.clones[job['node']],frame_owner_original=job['clone_frame_owner'],
        frame_owner_mapping=view.original_mapping[job['clone_frame_owner']],
        assigned_frame_tag=frames[view.clones[job['node']]].tag,
        insertion_owner_original=job['clone_insertion_owner']) for job in jobs]
    dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
        ('finite_complex_delayed_clones.py','finite_complex_controller_reuse.py','downstream_complex_circuit.py',
         'finite_clone_recovered_witness.py','frame_reuse.py')}
    identity=dict(h=row['h'],parent_compiled_sha256=row['original_compiled_sha256'],
        exact_chosen_jobs_sha256=digest(row['chosen']),compiled_sha256=compiled_hash(code),roles=code['roles'],
        node_order_sha256=digest(order),use_descriptions_sha256=digest(uses),selected_links_sha256=digest(links),
        frame_provenance_sha256=digest(provenance),original_mapping_sha256=digest(sorted(view.original_mapping.items())),
        clone_mapping_sha256=digest(sorted(view.clones.items())),source_dependencies=dependencies)
    value=dict(status='Terminal exact reconstruction export PASS; no scalar/frame replay performed',
        candidate_id=row['candidate_id'],candidate_input_sha256=sha256(args.candidate.read_bytes()).hexdigest(),
        candidate_identity_sha256=digest(identity),identity=identity,selected_links=links,
        use_descriptions=uses,node_order=order,frame_provenance=provenance,
        original_mapping=sorted(view.original_mapping.items()),clone_mapping=sorted(view.clones.items()),
        chosen=row['chosen'],shared_complex_counts=row['shared_complex_counts'],guard=row['guard'],
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps(dict(candidate_id=row['candidate_id'],roles=code['roles'],links=len(links),
        clones=len(jobs),candidate_identity_sha256=value['candidate_identity_sha256'],output_sha256=sha256(args.output.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
