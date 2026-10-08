#!/usr/bin/env python3
"""Exact even-ground screen for the proved shared D/E complex circuit.

The finite binary-frame construction and all its verifiers are imported
unchanged. This screen does not assert compatibility with a new analytic
assembly merely from improved finite counts.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import time

for _name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[_name]='1'


def worker(job):
    from downstream_complex_certificate import case
    from downstream_parameter_optimum import as_strings
    cap=job['address_space_gib']*1024**3
    resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    before=resource.getrusage(resource.RUSAGE_SELF);start=time.monotonic()
    row=case(job['h'],[])
    after=resource.getrusage(resource.RUSAGE_SELF)
    row.update(pid=os.getpid(),worker_wall_seconds=time.monotonic()-start,
               worker_cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
               lifetime_peak_rss_kib=after.ru_maxrss,
               scientific_scope='Exact unchanged finite map, binary frame residuals, terminal complements, full sharing matching and guard counts. Compact analytic transfer is separate.')
    return as_strings(row)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',type=Path,required=True)
    ap.add_argument('--h',type=int,nargs='+',default=[22,24,26,28,30,32,34,36,38,40,42,44,46,48,52])
    ap.add_argument('--workers',type=int,default=7)
    ap.add_argument('--worker-address-space-gib',type=int,default=6)
    ap.add_argument('--run-dir',type=Path,required=True)
    args=ap.parse_args()
    assert 1<=args.workers<=16 and len(args.h)==len(set(args.h))
    assert all(h>=8 and h%2==0 for h in args.h)
    assert not args.run_dir.exists(),'Use a fresh output directory'
    args.run_dir.mkdir(parents=True);(args.run_dir/'cases').mkdir()
    from downstream_gaussian import check_sources
    from singleton_sensitivity import write_json
    names=('finite_complex_ground_scan.py','downstream_complex_certificate.py',
           'downstream_complex_circuit.py','downstream_gaussian.py','downstream_parameter_optimum.py')
    protocol=dict(campaign_id='20261007T222521Z',campaign_deadline_utc='2026-10-08T08:25:21Z',
        started_utc=datetime.now(timezone.utc).isoformat(),settings={k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},
        source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
        input=check_sources(args.reference),scientific_scope='Verified finite even-ground complex primitives; new compact-control interface not inferred.',
        expected_cases=len(args.h),resource_policy='Single-thread CPU processes, bounded address space; aggregate campaign concurrency coordinated separately.')
    write_json(args.run_dir/'protocol.json',protocol)
    start=time.monotonic();rows=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pending={pool.submit(worker,dict(h=h,address_space_gib=args.worker_address_space_gib)):h for h in args.h}
        for future in as_completed(pending):
            row=future.result();write_json(args.run_dir/'cases'/('h'+str(row['h'])+'.json'),row);rows.append(row)
            saving=row['saving_enclosure']['saving_lower'] if row['saving_enclosure'] else None
            write_json(args.run_dir/'checkpoint.json',dict(status='Running',completed_cases=len(rows),expected_cases=len(args.h),
                completed_grounds=[r['h'] for r in rows],elapsed_seconds=time.monotonic()-start))
            print(json.dumps(dict(h=row['h'],roles=row['shared_complex_counts']['R'],
                 seconds=row['elapsed_seconds'],saving_lower=saving,completed=len(rows))),flush=True)
    from fractions import Fraction
    best=max(rows,key=lambda row:Fraction(row['saving_enclosure']['saving_lower']) if row['saving_enclosure'] else Fraction(-1))
    summary=dict(status='Terminal PASS',completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,
                 completed_cases=len(rows),best_ground=best['h'],best=best,rows=sorted(rows,key=lambda row:row['h']),protocol=protocol,
                 ranking_scope='Certified finite complex saving lower bound; final composed kappa requires the separately reviewed compact assembly.')
    assert len(rows)==len(args.h)
    write_json(args.run_dir/'summary.json',summary)
    print(json.dumps(dict(terminal=True,cases=len(rows),best_ground=best['h'],seconds=summary['elapsed_seconds'])),flush=True)


if __name__=='__main__':
    main()
