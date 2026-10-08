#!/usr/bin/env python3
"""Run a small explicit compiler plan in one CPU lane, preserving each attempt."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--wait-pid', type=int)
    parser.add_argument('--wait-marker')
    args = parser.parse_args()
    output = Path(args.output)
    assert '/work/joint-frame/layout/' in str(output.resolve())
    output.mkdir(parents=True, exist_ok=False)
    plan_raw = Path(args.plan).read_bytes()
    plan = json.loads(plan_raw)
    receipt = dict(created_utc=utc(), plan_sha256=hashlib.sha256(plan_raw).hexdigest(),
                   source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   wait_pid=args.wait_pid, wait_marker=args.wait_marker,
                   CPU_lanes=1, runs=[], limitation='PID is a live waiting hint only; no process is controlled or killed.')

    def save():
        (output/'status.json').write_text(json.dumps(receipt, indent=2)+'\n')

    save()
    if args.wait_pid:
        assert args.wait_marker
        while True:
            try:
                proc = Path('/proc')/str(args.wait_pid)
                marker = (proc/'cmdline').read_bytes().replace(b'\0', b' ').decode()
                state = (proc/'stat').read_text().split(') ', 1)[1].split()[0]
            except FileNotFoundError:
                break
            if args.wait_marker not in marker or state == 'Z':
                break
            time.sleep(2)
    receipt['started_utc'] = utc()
    env = os.environ.copy()
    for name in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS']:
        env[name] = '1'
    for index, case in enumerate(plan['cases']):
        entry = dict(name=case['name'], command=case['command'], started_utc=utc())
        receipt['runs'].append(entry)
        save()
        with (output/(str(index)+'-'+case['name']+'.log')).open('wb') as log:
            child = subprocess.Popen(case['command'], env=env, stdout=log, stderr=subprocess.STDOUT)
            entry['pid'] = child.pid
            save()
            entry['exit_code'] = child.wait()
        entry['completed_utc'] = utc()
        save()
        if entry['exit_code']:
            break
    receipt['completed_utc'] = utc()
    save()
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == '__main__':
    main()
