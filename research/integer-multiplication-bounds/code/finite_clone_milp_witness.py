#!/usr/bin/env python3
"""Full changed finite witness for an exactly feasible optimized clone set."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import finite_clone_capacity_repair2 as evaluator
import finite_clone_compatibility_milp as selector


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True);ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--small-control',type=Path,required=True);ap.add_argument('--time-limit',type=float,default=30)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    control=json.loads(args.small_control.read_text())
    assert control['status']=='Terminal exact feasible compatibility-MILP clone witness PASS'
    assert control['source_sha256']==sha256(Path(selector.__file__).read_bytes()).hexdigest()
    assert next(row for row in control['rows'] if row['h']==12)['compatibility_selection']['improvement_over_capacity_matching']==11
    parent=json.loads(args.candidate.read_text());digest=sha256(args.candidate.read_bytes()).hexdigest()
    definition=dict(parent_candidate_id=parent['candidate_id'],parent_sha256=digest,
        selector_source_sha256=sha256(Path(selector.__file__).read_bytes()).hexdigest(),
        evaluator_source_sha256=sha256(Path(evaluator.__file__).read_bytes()).hexdigest(),
        witness_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        clone_strategy='exact-feasible-compatibility-MILP-delayed-envelopes',
        selector_time_limit_seconds=args.time_limit,reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2')
    candidate_id=sha256(json.dumps(definition,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    at=time.monotonic();selector.TIME_LIMIT=args.time_limit;evaluator.matching=selector
    row=evaluator.evaluate(dict(definition,h=parent['h'],base=parent['base'],positions=parent['positions'],
        parent_path=str(args.candidate),candidate_id=candidate_id,reference=args.reference,
        worker_address_space_gib=8,phase='full-optimized-clone-witness'))
    value=dict(status='Terminal full exact feasible optimized clone witness PASS',definition=definition,
        candidate_id=candidate_id,rows=[row],elapsed_seconds=time.monotonic()-at,
        completed_utc=datetime.now(timezone.utc).isoformat(),small_control_sha256=sha256(args.small_control.read_bytes()).hexdigest(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        scientific_scope='Exactly feasible explicit clone set, inherited first-consumer envelopes, complete changed physical/rank/target checks; numerical optimization claims excluded')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(candidate_id=candidate_id,h=row['h'],roles=row['compiled_roles'],
        strict_gain=row['strict_selection_gain'],clones=len(row['chosen']),selector=row['capacity_selection']['solver'],
        compiled_sha256=row['checked']['compiled_sha256'],seconds=value['elapsed_seconds'])),flush=True)


if __name__=='__main__':main()
