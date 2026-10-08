#!/usr/bin/env python3
"""Fresh one-case-process repair of the bounded multi-ground rank study.

Verified old candidates are excluded. Larger grounds await an independent
memory calibration. Only process lifetime changes: the frozen scientific
evaluator, compiler and all exact checks remain unchanged.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from hashlib import sha256
import gc
import json
from pathlib import Path
import sys

import finite_rank_ground_cohort as old
import finite_singleton_neighborhood as queue
from finite_singleton_successor import predecessor_workers

REPAIR=None
EXTRA=[]
CONFIG={}


def candidates(anchor,prior):
    previous=json.loads((REPAIR/'protocol.json').read_text())
    verified={json.loads(path.read_text())['candidate_id'] for path in (REPAIR/'cases').glob('*.json')
              if '.error.' not in path.name}
    excluded=set(verified)
    for protocol in [prior,*[json.loads((path/'protocol.json').read_text()) for path in EXTRA]]:
        for row in protocol['candidate_definitions']:
            if row.get('sum_rule_early',0) in (0,1) and row.get('sum_rule_late',0) in (0,1):
                excluded.add(queue.identity(row['h'],2 if row['base']==3 else row['base'],row['positions'])[1])
    rows=[];seen=set()
    def append(h,positions,kind):
        value,key=queue.identity(h,2,positions)
        if key in seen or key in excluded:return
        seen.add(key);rows.append(dict(value,candidate_id=key,neighborhood=kind,
            changed=[dict(field='ground_and_position_pattern',h=h,pattern=kind)]))
    for row in previous['candidate_definitions']:
        if row['h']<=52:append(row['h'],row['positions'],'memory-repair-'+row['neighborhood'])
    repaired=len(rows)
    # Distinct endpoint-window patterns test the supported saving on the
    # smaller grounds while larger-ground memory is measured separately.
    for width_delta in (0,-2,2,-4,4,-6,6):
        for start in (0,1,3,5,7):
            for h in range(38,54,2):
                half=h//2;length=half+width_delta
                positions=[0]*h
                for offset in range(length):positions[(start+offset)%h]=half-2
                append(h,positions,'fresh-endpoint-window-'+str(start)+'-'+str(length))
    assert len(rows)==len(seen) and not seen&excluded
    CONFIG.update(repaired_unverified_small_candidates=repaired,verified_original_excluded=len(verified),
        fresh_candidates=len(rows)-repaired,planned_candidates=len(rows),maximum_ground=52,
        old_protocol_sha256=sha256((REPAIR/'protocol.json').read_bytes()).hexdigest(),
        process_policy='One scientific candidate per worker lifetime; immutable local cache reused within its single graph only')
    return rows,sorted(excluded)


def evaluate(job):
    import singleton_sensitivity
    singleton_sensitivity._LOCAL_CACHE.clear();gc.collect()
    row=old.evaluate(job)
    singleton_sensitivity._LOCAL_CACHE.clear();gc.collect()
    row['process_lifetime_policy']='Exactly one candidate; old checks unchanged; cache cleared at boundaries'
    return row


real_write_json=queue.write_json
def write_json(path,value):
    if path.name=='protocol.json' and 'candidate_definitions' in value:
        value=dict(value,rank_ground_repair=CONFIG)
    real_write_json(path,value)


def main():
    global REPAIR,EXTRA
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('--repair-run',type=Path,required=True)
    ap.add_argument('--exclude-run',type=Path,action='append',default=[])
    args,remaining=ap.parse_known_args();REPAIR=args.repair_run;EXTRA=args.exclude_run
    CONFIG.update(source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        frozen_evaluator_sha256=sha256(Path(old.__file__).read_bytes()).hexdigest(),
        campaign_original_deadline='2026-10-08T08:25:21Z',campaign_user_extended_deadline='2026-10-08T10:00:00Z',
        repair_scope='All exact scalar/frame/target and histogram checks retained; failed larger grounds omitted pending targeted memory calibration')
    queue.neighborhood=candidates;queue.evaluate=evaluate;queue.predecessor_workers=predecessor_workers
    queue.write_json=write_json;queue.ProcessPoolExecutor=partial(ProcessPoolExecutor,max_tasks_per_child=1)
    sys.argv=[sys.argv[0],*remaining];queue.main()


if __name__=='__main__':main()
