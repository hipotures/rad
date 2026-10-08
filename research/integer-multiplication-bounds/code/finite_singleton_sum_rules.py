#!/usr/bin/env python3
"""Actual retained-role search for local four-term sum associations.

The three existing cancellation-free BlockCircuit associations are used
unchanged. Only the choice of rule for early/late singleton positions varies.
The frozen full scalar/frame/compiler/target evaluator remains authoritative.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from unittest.mock import patch

import finite_singleton_neighborhood as queue
from finite_singleton_successor import evaluate_direct, predecessor_workers, DIRECT_HASH
import finite_singleton_search as local
from singleton_sensitivity import _LOCAL_CACHE

CONFIG = {}
real_write_json = queue.write_json
POLICIES = ((1,1),(2,2),(1,0),(0,1),(2,0),(0,2),(1,2),(2,1))


def configured_class(early, late):
    original = local.singleton_class()
    block = original.__mro__[1]

    class AssociatedSingleton(original):
        def __init__(self,n,position,base=4):
            self.position=position
            rule=early if position==0 else late
            block.__init__(self,n,(2,),base,rule,position)

    return AssociatedSingleton


def evaluate(job):
    original_function=local.singleton_class
    selected=configured_class(job['sum_rule_early'],job['sum_rule_late'])
    # Frozen cache keys contain base/position but not this new association.
    # Empty the cache at both boundaries; every new local DAG is verified
    # before immutable VerifiedLocal reuse within the current candidate.
    _LOCAL_CACHE.clear()
    try:
        with patch.object(local,'singleton_class',lambda:selected):
            row=evaluate_direct(job)
    finally:
        _LOCAL_CACHE.clear()
    assert local.singleton_class is original_function
    row.update(sum_rule_early=job['sum_rule_early'],sum_rule_late=job['sum_rule_late'],
        sum_rule_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        local_cache_boundary='New association not part of frozen cache key; cache cleared before/after every case, exact local verification occurs before within-case reuse')
    return row


def identity(h,base,positions,early,late):
    value=dict(h=h,base=base,positions=positions,sum_rule_early=early,sum_rule_late=late,
        reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2')
    return value,sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def candidates(anchor,prior):
    h=anchor['h'];rows=[];seen=set()
    vectors=[anchor['positions']]
    for count in (h//2-3,h//2-2,h//2-1,h//2,h//2+1,h//2+2,h//2+3):
        vectors.append([0]*count+[h//2-2]*(h-count))
    for start in range(1,18):
        vectors.append([0 if (c-start)%h<h//2-1 else h//2-2 for c in range(h)])
    assert len(vectors)==25
    for early,late in POLICIES:
        for base in (2,4):
            for positions in vectors:
                value,key=identity(h,base,positions,early,late)
                if key in seen:continue
                seen.add(key);rows.append(dict(value,candidate_id=key,neighborhood='four-term-sum-association',
                    changed=[dict(field='local_sum_rule',early=early,late=late)]))
    assert len(rows)==400 and len(seen)==len(rows)
    return rows,[anchor['candidate_id']]


def write_json(path,value):
    if path.name=='protocol.json' and 'candidate_definitions' in value:
        value=dict(value,sum_rule_configuration=CONFIG)
    real_write_json(path,value)


def main():
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('--reference',required=True)
    ap.add_argument('--small-control',type=Path)
    ap.add_argument('--control',type=Path)
    args,remaining=ap.parse_known_args();source_hash=sha256(Path(__file__).read_bytes()).hexdigest()
    if args.small_control:
        assert not args.small_control.exists()
        from finite_block_search import install_reference,GroupUnion
        install_reference(args.reference);original=local.singleton_class();canonical=configured_class(0,0)
        for n in (7,11):
            for position in (0,n//2-1):
                a,b=original(n,position,4),canonical(n,position,4)
                for field in ('inputs','args','support','outputs','active','additions'):
                    assert getattr(a,field)==getattr(b,field),('Canonical association regression',field)
        rows=[]
        for h in (8,12):
            positions=[0]*(h//2-1)+[h//2-2]*(h//2+1);positions[-2:]=[0,h//2-1]
            for early,late in POLICIES:
                value,key=identity(h,2,positions,early,late)
                row=evaluate(dict(value,candidate_id=key,reference=args.reference,phase='small-association-control',
                    local_cache=True,worker_address_space_gib=6,deadline='2026-10-08T08:25:21+00:00'))
                if h==8 and (early,late) in ((1,1),(2,2),(2,0)):
                    from fast_frame_envelope import labels
                    from frame_reuse import compile_reuse,optimize_chains
                    from frame_reuse_certificate import program
                    from dag_network import exact_invocation
                    cls=configured_class(early,late);circuit=GroupUnion(h,lambda n,c:cls(n,positions[c],2),'paired',0,True)
                    frames,_=labels(circuit,True);code=compile_reuse(circuit,frames,optimize_chains(circuit,frames,'rank'))
                    row['dirty_basis']=[exact_invocation(h,inverse,program(circuit,code)) for inverse in (False,True)]
                rows.append(row)
        args.small_control.parent.mkdir(parents=True,exist_ok=True)
        real_write_json(args.small_control,dict(status='Terminal PASS',source_sha256=source_hash,rows=rows))
        print(json.dumps(dict(status='Terminal PASS',controls=len(rows),roles=[r['compiled_roles'] for r in rows])))
        return
    assert args.control
    control=json.loads(args.control.read_text())
    assert control['status']=='Terminal PASS' and len(control['rows'])==16 and control['source_sha256']==source_hash
    CONFIG.update(source_sha256=source_hash,control_path=str(args.control),
        control_sha256=sha256(args.control.read_bytes()).hexdigest(),direct_envelope_sha256=DIRECT_HASH,
        policies=POLICIES,cache_invalidation='Frozen key lacks sum association; explicit empty cache boundaries',
        local_source_sha256=sha256(Path(__file__).with_name('finite_block_search.py').read_bytes()).hexdigest(),
        scientific_scope='Change existing exact four-term association only; inherited Singleton pair placement and all frozen evaluator/checkers unchanged')
    queue.neighborhood=candidates;queue.evaluate=evaluate;queue.predecessor_workers=predecessor_workers;queue.write_json=write_json
    sys.argv=[sys.argv[0],'--reference',args.reference,*remaining];queue.main()


if __name__=='__main__':main()
