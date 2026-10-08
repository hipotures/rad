#!/usr/bin/env python3
"""One fresh-process exact failing-ground memory discriminator."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import gc
import json
from pathlib import Path
import resource
import time

from finite_rank_ground_cohort import evaluate


def proc_memory():
    values={}
    for line in Path('/proc/self/status').read_text().splitlines():
        if line.startswith(('VmPeak:','VmSize:','VmHWM:','VmRSS:')):
            name,value,unit=line.split();assert unit=='kB';values[name.rstrip(':')+'_kib']=int(value)
    return values


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--protocol',type=Path,required=True)
    ap.add_argument('--candidate-id',required=True)
    ap.add_argument('--reference',required=True)
    ap.add_argument('--cap-gib',type=int,default=10)
    ap.add_argument('--deadline',required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    protocol=json.loads(args.protocol.read_text())
    definition=next(row for row in protocol['candidate_definitions'] if row['candidate_id']==args.candidate_id)
    job=dict(definition,reference=args.reference,local_cache=True,phase='fresh-memory-discriminator',
             worker_address_space_gib=args.cap_gib,deadline=args.deadline)
    started=datetime.now(timezone.utc).isoformat();at=time.monotonic();gc.collect()
    row=evaluate(job)
    peak=proc_memory();gc.collect();after=proc_memory()
    result=dict(status='Terminal exact fresh-process memory control PASS',row=row,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_protocol_sha256=sha256(args.protocol.read_bytes()).hexdigest(),
        frozen_evaluator_sha256=sha256(Path(__file__).with_name('finite_rank_ground_cohort.py').read_bytes()).hexdigest(),
        started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-at,
        address_space_limit_gib=args.cap_gib,memory_before_final_gc=peak,memory_after_final_gc=after,
        process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='One formerly failed ID in a fresh process; compiler and every scalar/frame/target/histogram check unchanged')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(h=job['h'],candidate=args.candidate_id,roles=row['compiled_roles'],
        memory=peak,seconds=result['elapsed_seconds'])),flush=True)


if __name__=='__main__':main()
