#!/usr/bin/env python3
"""Independent closing witness with a changed first capacity allocation.

The frozen earlier review supplies coefficient, physical, envelope and
saved-link checks. This fresh adapter rebuilds the ORIGINAL graph directly
and applies the supplied rounds; the old allocation parent's clone jobs
are not replayed or selected. All actual frames stay literal between rounds.
"""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
from unittest.mock import patch

import review_compound_bit_witness as base_review


def early_history(row,parent):
    h=row['h'];assert (h,row['base'],row['positions'])==(parent['h'],parent['base'],parent['positions'])
    circuit=(base_review.odd_build if h%2 else base_review.even_build)(h,row['base'],row['positions'])
    frames,_=base_review.labels(circuit,True)
    identity=base_review.logical_identity(circuit)
    assert identity==parent['baseline']['circuit_sha256']==row['baseline']['circuit_sha256']
    assert parent['baseline']==row['baseline']
    states=[dict(circuit=circuit,frames=frames,edits=[],expected_roles=parent['baseline']['roles'],
        expected_compiled=parent['baseline']['compiled_sha256'],expected_logical=identity,label='original-direct')]
    total=0
    for item in row['rounds']:
        old=states[-1]
        assert item['old_roles']==old['expected_roles']
        assert item['old_compiled_sha256']==old['expected_compiled']
        assert item['old_logical_sha256']==old['expected_logical']
        if not item['chosen']:
            assert item['new_roles']==old['expected_roles'];continue
        view,new,metadata=base_review.reconstruct_round(old['circuit'],old['frames'],item['chosen'])
        identity=base_review.logical_identity(view)
        assert identity==item['new_logical_sha256']
        assert item['old_roles']-item['new_roles']==len(item['chosen'])
        total+=len(item['chosen'])
        states.append(dict(circuit=view,frames=new,edits=item['chosen'],expected_roles=item['new_roles'],
            expected_compiled=item['new_compiled_sha256'],expected_logical=identity,
            label='direct-first-allocation-round-'+str(item['round']),metadata=metadata))
    assert total==row['role_saving_from_original']
    assert states[-1]['expected_roles']==row['compiled_roles']
    assert states[-1]['expected_compiled']==row['checked']['compiled_sha256']
    assert states[-1]['expected_logical']==row['final']['logical']['circuit_sha256']
    return states


def selected_row(path,h,policy=None):
    value=json.loads(path.read_text())
    rows=value['rows'] if 'rows' in value else [value]
    candidates=[row for row in rows if row['h']==h and (policy is None or row.get('policy')==policy)]
    assert candidates
    return value,min(candidates,key=lambda row:row['compiled_roles'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('reference','certificate','parent','plan','small-certificate','small-parent','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--h',type=int,required=True)
    parser.add_argument('--policy')
    parser.add_argument('--small-policy')
    args=parser.parse_args();assert not args.output.exists()
    revision=subprocess.check_output(['git','-C',str(args.reference),'rev-parse','HEAD'],text=True).strip()
    assert revision=='bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    base_review.install_reference(str(args.reference));start=time.monotonic()
    document,row=selected_row(args.certificate,args.h,args.policy)
    parent_document,parent=selected_row(args.parent,args.h)
    small_document,small_row=selected_row(args.small_certificate,12,args.small_policy)
    _,small_parent=selected_row(args.small_parent,12)
    assert 'role_saving_from_original' in row and 'role_saving_from_original' in small_row
    parent_sha=row.get('parent_sha256',row.get('input_sha256',document.get('parent_sha256')))
    small_sha=small_row.get('parent_sha256',small_row.get('input_sha256',small_document.get('parent_sha256')))
    if parent_sha is not None:assert parent_sha==base_review.file_digest(args.parent)
    if small_sha is not None:assert small_sha==base_review.file_digest(args.small_parent)
    exported=json.loads(args.plan.read_text());identity=exported['identity']
    assert identity['first_batch_from_original']
    assert identity['compound_certificate_sha256']==base_review.file_digest(args.certificate)
    assert identity['initial_parent_sha256']==base_review.file_digest(args.parent)
    assert identity['roles']==row['compiled_roles'] and identity['compiled_sha256']==row['checked']['compiled_sha256']
    assert identity['logical_sha256']==row['final']['logical']['circuit_sha256']
    assert identity['residual_rank_histogram_sha256']==base_review.digest(row['residual_rank_histogram'])
    assert identity['literal_scalar_guard_sha256']==base_review.digest(row['literal_scalar_guard'])
    assert exported['candidate_id']==base_review.digest(identity)
    assert identity['compound_candidate_id']==row['candidate_id']
    assert exported['h']==args.h and exported['base']==row['base'] and exported['positions']==row['positions']
    # Use only the independently rebuilt DAG/plan checks in the frozen own
    # module. No source from the producer allocator/cloner is imported.
    with patch.object(base_review,'history',early_history):
        small=base_review.verify(small_row,small_parent,small=True)
        full=base_review.verify(row,parent,exported=exported)
    if args.h%2==0:
        _,matching=base_review.even_matching(args.h);full['matching']=matching
    result=dict(status='PASS INDEPENDENT CLOSING DIRECT-FIRST-ALLOCATION COMPOUND',
        completed_utc=datetime.now(timezone.utc).isoformat(),python=sys.version,
        reference_commit=revision,h=args.h,policy=row.get('policy'),candidate_id=row['candidate_id'],
        reconstruction_export_candidate_id=exported['candidate_id'],
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256={str(path):base_review.file_digest(path) for path in
            (args.certificate,args.parent,args.plan,args.small_certificate,args.small_parent)},
        frozen_review_source_sha256=base_review.file_digest(Path(base_review.__file__)),
        full=full,small_control=small,old_allocation_parent_jobs_replayed=False,
        producer_allocator_cloner_selector_imported=False,
        all_size_scope='The accepted actual-frame/capacity induction applies to a genuinely changed first allocation and every subsequent actual-DAG round; generic kernels unchanged; protected centers separate',
        wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],args.h,full['roles'],flush=True)


if __name__=='__main__':main()
