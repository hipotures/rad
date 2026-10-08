#!/usr/bin/env python3
"""One process-local immutable parent allocation for repeated clone probes.

Only the constructor/frames/feasible-plan/compile identities of one complete
parent are cached. The frozen evaluator still checks those identities on
every call and completely verifies every strict changed final graph. Every
later-round constructor, recovered link plan and compiler call is unchanged.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time
from unittest.mock import patch

import finite_bit_rounds_from_parent as frozen
from finite_clone_recovered_witness import compiled_hash

first=frozen.first
CACHE=None


def parent_key(parent):
    fields={name:parent[name] for name in ('h','base','positions','baseline','chosen','checked','final')}
    return sha256(json.dumps(fields,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def case(parent,*args,**kwargs):
    global CACHE
    key=parent_key(parent);hit=bool(CACHE and CACHE['key']==key)
    cache=CACHE if hit else dict(key=key)
    expected=parent['checked']['compiled_sha256']
    real_build=first.witness.build;real_labels=frozen.labels
    real_optimize=frozen.frame_reuse.optimize_chains
    real_view=first.witness.DelayedCloneView;real_frames=first.witness.descendant_frames
    real_plan=frozen.recovered_plan;real_compile=frozen.frame_reuse.compile_reuse
    hooks={name:0 for name in ('build','labels','original_flow','original_compile','parent_view','parent_frames','parent_plan','parent_compile')}
    def build(h,base,positions):
        assert (h,base,positions)==(parent['h'],parent['base'],parent['positions'])
        hooks['build']+=1
        if not hit:cache['original']=real_build(h,base,positions)
        return cache['original']
    def labels(circuit,global_graph):
        assert circuit is cache['original'] and global_graph
        hooks['labels']+=1
        if not hit:cache['label_result']=real_labels(circuit,global_graph)
        return cache['label_result']
    def optimize(circuit,frames,schedule):
        assert circuit is cache['original'] and schedule=='rank'
        hooks['original_flow']+=1
        if not hit:cache['old_plan']=real_optimize(circuit,frames,schedule)
        return cache['old_plan']
    def view(circuit,frames,jobs):
        if circuit is cache['original']:
            hooks['parent_view']+=1
            literal=json.loads(json.dumps([first.serialized(job) for job in jobs],sort_keys=True))
            assert literal==parent['chosen']
            if not hit:cache['parent_view']=real_view(circuit,frames,jobs)
            return cache['parent_view']
        return real_view(circuit,frames,jobs)
    def frames(circuit,old_frames,changed,jobs):
        if circuit is cache['original']:
            assert changed is cache['parent_view'];hooks['parent_frames']+=1
            if not hit:cache['parent_frames']=real_frames(circuit,old_frames,changed,jobs)
            return cache['parent_frames']
        return real_frames(circuit,old_frames,changed,jobs)
    def plan(circuit,old_plan,changed,new_frames,jobs):
        if circuit is cache['original']:
            assert changed is cache['parent_view'];hooks['parent_plan']+=1
            if not hit:cache['parent_plan']=real_plan(circuit,old_plan,changed,new_frames,jobs)
            return cache['parent_plan']
        return real_plan(circuit,old_plan,changed,new_frames,jobs)
    def compile(circuit,spaces,links):
        name='original_compile' if circuit is cache['original'] else ('parent_compile' if circuit is cache.get('parent_view') else None)
        if name:
            hooks[name]+=1
            if not hit:cache[name]=real_compile(circuit,spaces,links)
            return cache[name]
        return real_compile(circuit,spaces,links)
    before=time.monotonic()
    with patch.object(first.witness,'build',build),patch.object(frozen,'labels',labels), \
         patch.object(frozen.frame_reuse,'optimize_chains',optimize), \
         patch.object(first.witness,'DelayedCloneView',view),patch.object(first.witness,'descendant_frames',frames), \
         patch.object(frozen,'recovered_plan',plan),patch.object(frozen.frame_reuse,'compile_reuse',compile):
        row=frozen.case(parent,*args,**kwargs)
    assert all(value==1 for value in hooks.values())
    assert compiled_hash(cache['parent_compile'])==expected
    assert first.logical_identity(cache['parent_view'])==parent['final']['logical']['circuit_sha256']
    snapshot=tuple(cache['parent_frames'].items())
    if hit:
        assert snapshot==cache['frame_snapshot']
        assert tuple(cache['parent_plan'][2].items())==cache['link_snapshot']
    else:
        cache['frame_snapshot']=snapshot;cache['link_snapshot']=tuple(cache['parent_plan'][2].items())
        assert all(space.__dataclass_params__.frozen for space in cache['parent_frames'].values())
    CACHE=cache
    row.update(parent_allocation_cache=dict(hit=hit,key=key,process_entries=1,
        complete_parent_identities_checked_on_every_call=True,
        cached_frame_and_link_objects_unchanged=True,cached_constructor_calls=hooks),
        cached_wrapper_elapsed_seconds=time.monotonic()-before)
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',required=True);parser.add_argument('--parent',type=Path,required=True)
    parser.add_argument('--h',type=int,default=12);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists();first.witness.install_reference(args.reference)
    document=json.loads(args.parent.read_text());parent=next(row for row in document['rows'] if row['h']==args.h)
    before=time.monotonic();cold=case(parent,2,4,'wide',0,6,False);warm=case(parent,2,4,'wide',0,6,False)
    assert not cold['parent_allocation_cache']['hit'] and warm['parent_allocation_cache']['hit']
    for key in ('compiled_roles','role_saving','rounds','final','checked'):
        if key=='rounds':
            def strip(rows):return [{k:v for k,v in row.items() if k not in ('seconds','selection')} for row in rows]
            assert strip(cold[key])==strip(warm[key])
        else:assert cold[key]==warm[key]
    value=dict(status='Terminal exact cold/warm parent-allocation identity PASS',
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        frozen_evaluator_source_sha256=sha256(Path(frozen.__file__).read_bytes()).hexdigest(),
        parent_input_sha256=sha256(args.parent.read_bytes()).hexdigest(),
        rows=[cold,warm],elapsed_seconds=time.monotonic()-before,
        scope='Exact same changed compile/maps/frames/targets; parent logical and compiled identities remain mandatory; only allocation reuse differs; h12 dirty evidence is in075500')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(h=args.h,roles=warm['compiled_roles'],
        cold_parent_seconds=cold['pinned_parent_identity_reconstruction_seconds'],
        warm_parent_seconds=warm['pinned_parent_identity_reconstruction_seconds'],
        cold_total_seconds=cold['cached_wrapper_elapsed_seconds'],warm_total_seconds=warm['cached_wrapper_elapsed_seconds'])),flush=True)


if __name__=='__main__':main()
