#!/usr/bin/env python3
"""Run a finite list of distinct ordered-DAG families on one compute slot."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root', required=True, type=Path)
    ap.add_argument('--profiler', required=True, type=Path)
    ap.add_argument('--first', required=True, type=Path)
    ap.add_argument('--second', required=True, type=Path)
    ap.add_argument('--config', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    families = json.loads(args.config.read_text())
    assert families and len({json.dumps(x, sort_keys=True) for x in families}) == len(families)
    args.output.mkdir(parents=True, exist_ok=False)
    script = Path(__file__).with_name('dag_order_family.py')
    protocol = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    worker_pid=os.getpid(), families=families,
                    launcher_source=Path(__file__).read_text(),
                    family_source=script.read_text(),
                    profiler_sha256=hashlib.sha256(args.profiler.read_bytes()).hexdigest(),
                    partners=[dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                              for p in (args.first, args.second)],
                    scope='One sequential child process; full finite support/frame/moment checks, independent integration remains separate.')
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    for index, family in enumerate(families):
        h = family['dimension']
        assert h in (23,25)
        partner = args.second if h == 23 else args.first
        command = [sys.executable, '-B', str(script), '--source-root', str(args.source_root),
                   '--profiler', str(args.profiler), '--partner', str(partner),
                   '--output', str(args.output/('step%02d-h%d'%(index,h)))]
        for key in ('dimension', 'pattern', 'association', 'threshold', 'scope'):
            command += ['--'+key, str(family[key])]
        with (args.output/('step%02d.log'%index)).open('w') as log:
            child = subprocess.Popen(command, stdout=log, stderr=log)
            print(json.dumps(dict(event='math_family_started', parent_pid=os.getpid(),
                                  child_pid=child.pid, command=command)), flush=True)
            status = child.wait()
        receipt = dict(index=index, command=command, exit_code=status)
        (args.output/('step%02d-exit.json'%index)).write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(dict(event='math_family_completed', **receipt)), flush=True)
        if status:
            raise SystemExit(status)


if __name__ == '__main__':
    main()
