#!/usr/bin/env python3
"""Combine safe even-pair D/E sharing with actual binary delayed clones."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time
from unittest.mock import patch
import frame_reuse
import finite_complex_clone_options as options
import finite_complex_even_pair_cse as sharing
from finite_clone_recovered_witness import compiled_hash


def case(h,limit=4,policy='wide',seed=0,time_limit=6.0,dirty=False,exchange=False,sizes=None):
    at=time.monotonic();plain=options.witness.TripleSideCircuit(h)
    original=sharing.EvenPairCSEView(plain,sizes);frames,_=options.witness.binary.labels(original)
    with patch.object(frame_reuse,'included',options.witness.binary.admissible):
        plan=frame_reuse.optimize_chains(original,frames,'rank');code=frame_reuse.compile_reuse(original,frames,plan)
    # Identity preparation only. The complete changed view verifies every
    # original shared node and all newly inserted clones exactly once.
    baseline=dict(logical=dict(circuit_sha256=options.witness.logical_identity(original)),
        compiled_roles=code['roles'],checked=dict(compiled_sha256=compiled_hash(code)))
    preparation=time.monotonic()-at
    with patch.object(options.witness,'TripleSideCircuit',lambda ground:original):
        row=options.case(h,baseline,limit,policy,seed,time_limit,dirty,exchange)
    row.update(cross_DE_sharing=original.diagnostic,original_shared_identity_only_preparation_seconds=preparation,
        elapsed_seconds=time.monotonic()-at,
        scientific_scope='Combined exact even-pair D/E support aliases and binary first-consumer/provider clones; complete changed graph/physical/Gram/phase/target/G/E checks; independent transfer pending')
    return row


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--h',type=int,nargs='+',default=[8,12])
    ap.add_argument('--limit',type=int,default=4);ap.add_argument('--policy',choices=['wide','narrow','seeded'],default='wide')
    ap.add_argument('--seed',type=int,default=0);ap.add_argument('--time-limit',type=float,default=6)
    ap.add_argument('--dirty-ground',type=int,default=8);ap.add_argument('--exchange-h8',action='store_true')
    ap.add_argument('--outside-size',type=int,nargs='+');ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();at=time.monotonic()
    value=dict(status='Running',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),rows=[],
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            ('finite_complex_even_pair_cse.py','finite_complex_clone_options.py','finite_complex_delayed_clones.py')},
        started_utc=datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h in args.h:
        row=case(h,args.limit,args.policy,args.seed,args.time_limit,h==args.dirty_ground,h==8 and args.exchange_h8,
            set(args.outside_size) if args.outside_size else None)
        value['rows'].append(row);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,roles=row['compiled_roles'],shared_before_clone=row['baseline_roles'],
            clones=row['role_saving'],aliases=row['cross_DE_sharing']['chosen_even_pair_aliases'],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact combined D/E sharing and binary clone PASS',
        elapsed_seconds=time.monotonic()-at,completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
