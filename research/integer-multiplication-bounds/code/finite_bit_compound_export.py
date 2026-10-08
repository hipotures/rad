#!/usr/bin/env python3
"""Complete reconstruction artifact for a saved successive rational clone DAG.

No coefficient or dirty-scratch replay occurs here. Constructor, every
intermediate compiled identity, actual inherited frames, recovered whole
chains and exact capacities are reconstructed. All mappings and final links
are saved explicitly; the independent reviewer performs the changed checks.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

import finite_bit_clone_options as first
from finite_clone_plan_export import digest
from finite_clone_recovered_witness import recovered_plan,compiled_hash
from fast_frame_envelope import labels
import frame_reuse


def frame_rows(frames,order):
    for node in order:
        s=frames[node]
        yield [node,[s.common,list(s.tags),list(s.basis),s.core,s.vertices]]


def sequence_hash(rows):
    value=sha256()
    for row in rows:value.update(json.dumps(row,separators=(',',':')).encode()+b'\n')
    return value.hexdigest()


def export(reference,certificate,output,h=None):
    assert not output.exists();first.witness.install_reference(reference);start=time.monotonic()
    document=json.loads(certificate.read_text())
    row=next(r for r in document['rows'] if h is None or r['h']==h) if 'rows'in document else document
    parent_path=Path(row.get('parent_path',row.get('input_path')))
    assert sha256(parent_path.read_bytes()).hexdigest()==row.get('parent_sha256',row.get('input_sha256'))
    parent_document=json.loads(parent_path.read_text())
    parent=next(r for r in parent_document['rows'] if r['h']==row['h']) if 'rows'in parent_document else parent_document
    original=first.witness.build(parent['h'],parent['base'],parent['positions'])
    assert first.logical_identity(original)==parent['baseline']['circuit_sha256']
    frames,_=labels(original,True)
    plan=frame_reuse.optimize_chains(original,frames,'rank')
    code=frame_reuse.compile_reuse(original,frames,plan)
    assert code['roles']==parent['baseline']['roles']
    assert compiled_hash(code)==parent['baseline']['compiled_sha256']
    canonical_owner={}
    for node in sorted(original.active):canonical_owner.setdefault(frames[node],node)
    original_frame_hash=sequence_hash(frame_rows(frames,sorted(original.active)))
    stages=[];current=original
    initial=dict(stage='initial-multi-option-parent',chosen=parent['chosen'],
        old_roles=code['roles'],old_compiled_sha256=compiled_hash(code),
        old_logical_sha256=first.logical_identity(current),
        new_roles=parent['compiled_roles'],new_compiled_sha256=parent['checked']['compiled_sha256'],
        new_logical_sha256=parent['final']['logical']['circuit_sha256'])
    for definition in [initial,*row['rounds']]:
        assert definition['old_roles']==code['roles']
        assert definition['old_compiled_sha256']==compiled_hash(code)
        assert definition['old_logical_sha256']==first.logical_identity(current)
        jobs=[first.deserialize(j) for j in definition['chosen']]
        if not jobs:
            assert definition['new_roles']==code['roles']
            stages.append(dict(stage=definition.get('stage',definition.get('round')),chosen=[],
                old_roles=code['roles'],new_roles=code['roles'],old_compiled_sha256=compiled_hash(code),
                new_compiled_sha256=compiled_hash(code),old_logical_sha256=first.logical_identity(current),
                new_logical_sha256=first.logical_identity(current),empty_stage=True));continue
        view=first.witness.DelayedCloneView(current,frames,jobs)
        new_frames=first.witness.descendant_frames(current,frames,view,jobs)
        new_plan=recovered_plan(current,plan,view,new_frames,jobs)
        new_code=frame_reuse.compile_reuse(view,new_frames,new_plan)
        assert definition['new_roles']==new_code['roles']
        assert definition['new_compiled_sha256']==compiled_hash(new_code)
        assert definition['new_logical_sha256']==first.logical_identity(view)
        old_ids=sorted(current.active)
        mapping=[view.original_mapping[node] for node in old_ids]
        placement=[[j['node'],view.clones[j['node']],j['clone_frame_owner'],
                    view.original_mapping[j['clone_frame_owner']],canonical_owner[frames[j['clone_frame_owner']]]]
                   for j in jobs]
        order=sorted(view.active,key=lambda node:(new_frames[node].dimension,node))
        stages.append(dict(stage=definition.get('stage',definition.get('round')),
            chosen=definition['chosen'],original_mapping_values=mapping,
            original_mapping_key_order='sorted previous-stage active node IDs',
            original_mapping_pairs_sha256=digest([[n,view.original_mapping[n]] for n in old_ids]),
            clone_placement_and_frame_owners=placement,
            clone_placement_columns=['previous_node','new_clone_node','previous_frame_owner','new_mapped_frame_owner','canonical_original_frame_owner'],
            clone_count=len(jobs),old_node_count=len(old_ids),new_node_count=len(order),
            old_roles=code['roles'],new_roles=new_code['roles'],
            old_compiled_sha256=compiled_hash(code),new_compiled_sha256=compiled_hash(new_code),
            old_logical_sha256=first.logical_identity(current),new_logical_sha256=first.logical_identity(view),
            selected_links_sha256=digest(sorted([a,b] for a,b in new_plan[2].items())),
            selected_link_count=len(new_plan[2]),descriptions_sha256=digest(new_plan[1]),
            description_count=len(new_plan[1]),node_order_sha256=digest(order),
            inherited_frames_sha256=sequence_hash(frame_rows(new_frames,sorted(view.active)))))
        current,frames,plan,code=view,new_frames,new_plan,new_code
    assert code['roles']==row['compiled_roles']
    assert compiled_hash(code)==row['checked']['compiled_sha256']
    assert first.logical_identity(current)==row['final']['logical']['circuit_sha256']
    selected=sorted([a,b] for a,b in plan[2].items())
    order=sorted(current.active,key=lambda node:(frames[node].dimension,node))
    frame_owners=[canonical_owner[frames[node]] for node in sorted(current.active)]
    identity=dict(compound_candidate_id=row['candidate_id'],compound_certificate_sha256=sha256(certificate.read_bytes()).hexdigest(),
        initial_parent_candidate_id=parent['candidate_id'],initial_parent_sha256=sha256(parent_path.read_bytes()).hexdigest(),
        stages_sha256=digest(stages),selected_links_sha256=digest(selected),node_order_sha256=digest(order),
        descriptions_sha256=digest(plan[1]),actual_frame_owners_sha256=digest(frame_owners),
        actual_frame_fields_sha256=sequence_hash(frame_rows(frames,sorted(current.active))),
        compiled_sha256=compiled_hash(code),logical_sha256=first.logical_identity(current),roles=code['roles'],
        residual_rank_histogram_sha256=digest(row.get('residual_rank_histogram')),
        literal_scalar_guard_sha256=digest(row.get('literal_scalar_guard')))
    value=dict(status='Terminal complete successive clone reconstruction PASS',candidate_id=digest(identity),identity=identity,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),h=row['h'],base=parent['base'],positions=parent['positions'],
        compound_certificate_path=str(certificate),initial_parent_path=str(parent_path),
        baseline=parent['baseline'],initial_parent_sha256=identity['initial_parent_sha256'],
        canonical_original_frames_sha256=original_frame_hash,
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            ('finite_bit_clone_options.py','finite_bit_rounds_from_parent.py','finite_clone_descendant_frame.py',
             'finite_clone_recovered_witness.py','finite_clone_batch.py','fast_frame_envelope.py','frame_envelope.py',
             'frame_reuse.py','finite_odd_pair_positions.py','finite_singleton_search.py')},
        stages=stages,exact_selected_links=selected,selected_link_count=len(selected),
        node_order=order,node_count=len(order),description_count=len(plan[1]),
        node_frame_original_owner_values=frame_owners,node_frame_key_order='sorted final active node IDs',
        frame_recovery='Each frame value is literally a canonical original positive envelope; regenerate its complete common/tags/basis/core/vertices at the named original owner. Later clones inherit the actual previous-stage first-consumer frame, never their canonical source envelope.',
        residual_rank_histogram=row.get('residual_rank_histogram'),literal_scalar_guard=row.get('literal_scalar_guard'),
        final=row['final'],elapsed_seconds=time.monotonic()-start,
        reconstruction_policy='Original constructor and compiled identities only; no old coefficient replay or parent selector; each saved clone stage retains actual inherited frames and whole recovered chain/capacity checks. This export does not repeat scientific physical verification.')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps(dict(candidate_id=value['candidate_id'],h=row['h'],roles=code['roles'],
        links=len(selected),stages=[s.get('clone_count',0) for s in stages],bytes=output.stat().st_size,
        seconds=value['elapsed_seconds'])),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reference',required=True)
    p.add_argument('--certificate',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--h',type=int);a=p.parse_args();export(a.reference,a.certificate,a.output,a.h)


if __name__=='__main__':main()
