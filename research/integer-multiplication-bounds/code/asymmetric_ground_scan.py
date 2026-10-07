#!/usr/bin/env python3
"""Bounded independent full-graph envelope scans for unequal motif factors.

The scan measures the actual checked physical role counts. The subsequent
asymmetric tensor composition remains a separate mathematical obligation.
Each subprocess uses one BLAS thread; process concurrency supplies parallelism.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


DEADLINE = datetime(2026,10,8,8,25,21,tzinfo=timezone.utc)


def run_owned_group(command, environment, output, seconds):
    """Wait for a new process group and terminate all its members on timeout.

    Killing only /usr/bin/time can leave its Python child running. A fresh
    session lets us terminate only the group created for this invocation.
    """
    child = subprocess.Popen(command, env=environment, stdout=output,
                             stderr=subprocess.STDOUT, start_new_session=True)
    try:
        return child.wait(timeout=seconds), 'completed'
    except subprocess.TimeoutExpired:
        try:
            os.killpg(child.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        # The wrapper can exit before a descendant which ignores SIGTERM.
        # Kill remaining members even if waiting for the wrapper succeeded.
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        child.wait(timeout=5)
        return child.returncode, 'bounded timeout; owned process group terminated; partial log retained'


def worker(job):
    h, args = job
    started = datetime.now(timezone.utc)
    cap = min(args.seconds, (DEADLINE-started).total_seconds()-180)
    assert cap > 0
    result = args.run_dir/f'h{h}.json'
    log = args.run_dir/f'h{h}.log'
    command = [sys.executable, '-B', str(Path(__file__).with_name('frame_envelope.py')),
               '--reference', str(args.reference), '--global-h', str(h),
               '--schedule', 'rank', '--output', str(result)]
    environment = os.environ.copy()
    environment.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    start = time.monotonic()
    with log.open('x') as out:
        code, reason = run_owned_group(['/usr/bin/time','-v',*command], environment, out, cap)
        if reason == 'completed' and code != 0:
            reason = 'subprocess failure'
    row = {'h':h,'start_utc':started.isoformat(),'elapsed_seconds':time.monotonic()-start,
           'return_code':code,'terminal_reason':reason,'command':command,
           'log':str(log),'result':str(result),'time_cap_seconds':cap}
    if code == 0:
        data = json.loads(result.read_text())[0]
        row.update(roles=data['roles'],chains=data['chains'],finite_status=data['status'],
                   compiled_sha256=data['check']['compiled_sha256'])
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--h',type=int,nargs='+',required=True)
    parser.add_argument('--workers',type=int,default=8)
    parser.add_argument('--seconds',type=float,default=2400)
    parser.add_argument('--run-dir',type=Path,required=True)
    args = parser.parse_args()
    assert 1 <= args.workers <= 8 and all(h >= 38 and h%2 == 0 for h in args.h)
    args.run_dir.mkdir(parents=True,exist_ok=False)
    protocol = {'campaign_id':'20261007T222521Z','start_utc':datetime.now(timezone.utc).isoformat(),
                'deadline_utc':DEADLINE.isoformat(),'question':'Actual envelope role counts for unequal tensor factors',
                'settings':{k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},
                'source_sha256':{p.name:sha256(p.read_bytes()).hexdigest() for p in
                    [Path(__file__),Path(__file__).with_name('frame_envelope.py'),Path(__file__).with_name('frame_reuse.py')]},
                'upstream_revision':'bcd4ebde8692383539f8a48734e5fbf3a18a32c2',
                'resource_policy':'8 independent single-thread jobs; campaign 14 CPU / 96 GiB ceiling; largest grounds separately'}
    (args.run_dir/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    rows = []
    with (args.run_dir/'cases.jsonl').open('x') as stream, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(worker,(h,args)) for h in args.h]
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            stream.write(json.dumps(row)+'\n');stream.flush()
            print(json.dumps({'h':row['h'],'roles':row.get('roles'),'reason':row['terminal_reason'],
                              'elapsed_seconds':row['elapsed_seconds'],'completed':len(rows)}),flush=True)
    (args.run_dir/'summary.json').write_text(json.dumps({'protocol':protocol,'cases':rows},indent=2)+'\n')


if __name__ == '__main__':
    main()
