#!/usr/bin/env python3
"""One-slot exact rational-basis experiments on the executed word multiset."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--binary', type=Path, required=True)
    ap.add_argument('--native-source', type=Path)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    native_source = args.native_source or Path(__file__).with_name(args.binary.name+'.cpp')
    assert native_source.exists()
    native_source_sha = digest(native_source)
    driver_sha = digest(Path(__file__))
    configs = json.loads(args.input.read_text())
    start = time.monotonic()
    rows = []
    (args.work/'process.json').write_text(json.dumps(dict(pid=os.getpid(),command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')
    env = dict(os.environ)
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[key] = '1'
    for config in configs:
        work = args.work/config['case_id']
        work.mkdir()
        result = work/'profile.json'
        audit = work/'transitions.json'
        command = [str(args.binary), config['transitions'], config['basis'], str(result), str(audit)]
        with (work/'run.log').open('wb') as log:
            child = subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env)
            (work/'process.json').write_text(json.dumps(dict(pid=child.pid,command=command,started_utc=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')
            print(json.dumps(dict(status='RATIONAL-BASIS ACTUAL WORD PROFILE RUNNING',pid=child.pid,**config)),flush=True)
            assert child.wait() == 0, config
        profile = json.loads(result.read_text())
        rows.append(dict(config=config,profile=profile,profile_path=str(result),profile_sha256=digest(result),
                         transition_audit=str(audit),transition_audit_sha256=digest(audit),input_binary_sha256=digest(Path(config['transitions']))))
        status = dict(utc=datetime.now(timezone.utc).isoformat(),completed=len(rows),total=len(configs),elapsed_seconds=time.monotonic()-start,workers=1)
        (args.work/'status.json').write_text(json.dumps(status,indent=2)+'\n')
        print(json.dumps(status),flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(dict(status='PASS EXACT RATIONAL-BASIS EXECUTED WORD PROFILE COHORT',rows=rows,
        input_sha256=digest(args.input),driver_sha256=driver_sha,native_source=str(native_source),native_source_sha256=native_source_sha,
        binary_sha256=digest(args.binary),completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,
        scope='All actual word transition NE ranks bounded by exact prime-product certificates. Literal nesting, source-only word replay, basis/source data compatibility and complete moment/assembly are separate gates.'),indent=2)+'\n')


if __name__ == '__main__':
    main()
