#!/usr/bin/env python3
"""Run distinct seeded native matching families in one persistent CPU slot.

The queue never overlaps profilers. Exact occurrence fingerprints from every
completed family are reused before another full five-prime matrix evaluation.
Each attempt has a fresh directory and an immutable protocol. Matching weights
depend on the fixed source matrices, so the same checked reference profiles
can be retained while exploring fresh tie orders and noise realizations.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('profiler','first-dag','second-dag','first-profile','second-profile'):
        ap.add_argument('--'+name,required=True,type=Path)
    ap.add_argument('--saving',required=True)
    ap.add_argument('--previous',action='append',default=[],type=Path)
    ap.add_argument('--seed-start',default=64,type=int)
    ap.add_argument('--families',default=64,type=int)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    worker=Path(__file__).with_name('weighted_native_worker.py')
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),
                  queue_sha256=digest(Path(__file__)),worker_sha256=digest(worker),
                  profiler_sha256=digest(args.profiler),families=args.families,
                  seed_start=args.seed_start,seed_stride=64,threads=1,
                  previous_progress=[str(p) for p in args.previous],
                  reference_saving=args.saving,
                  inputs={k:dict(path=str(getattr(args,k)),sha256=digest(getattr(args,k)))
                          for k in ('first_dag','second_dag','first_profile','second_profile')},
                  scope='Finite ORIGINAL fixed-both witness search; native machine hypotheses remain conditional')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    previous=args.previous[:]
    completed=[]
    for batch in range(args.families):
        run=args.output/('family-%03d'%batch)
        cmd=[sys.executable,str(worker),'--profiler',str(args.profiler.resolve()),
             '--first-dag',str(args.first_dag),'--second-dag',str(args.second_dag),
             '--first-profile',str(args.first_profile),'--second-profile',str(args.second_profile),
             '--saving',args.saving,'--seed-offset',str(args.seed_start+64*batch),
             '--output',str(run)]
        for old in previous:
            cmd.extend(['--previous',str(old)])
        subprocess.run(cmd,check=True)
        previous.append(run/'progress.json')
        summary=json.loads((run/'summary.json').read_text())
        completed.append(dict(batch=batch,run=str(run),summary=summary))
        (args.output/'progress.json').write_text(json.dumps(dict(completed_families=len(completed),families=completed),indent=2)+'\n')
    (args.output/'summary.json').write_text(json.dumps(dict(status='completed_serial_queue',families=completed),indent=2)+'\n')


if __name__=='__main__':
    main()
