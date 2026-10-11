#!/usr/bin/env python3
"""Run a frozen, bounded sequence of distinct mathematical GPU questions."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    args = ap.parse_args()
    assert not args.work.exists()
    args.work.mkdir(parents=True)
    doc = json.loads(args.config.read_text())
    protocol = {'utc': stamp(), 'config': str(args.config),
                'config_sha256': hashlib.sha256(args.config.read_bytes()).hexdigest(),
                'queue': doc}
    (args.work / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    completed = []
    for i, job in enumerate(doc['questions']):
        logpath = args.work / f'question-{i}.log'
        with logpath.open('x') as log:
            process = subprocess.Popen(job['argv'], stdout=log, stderr=subprocess.STDOUT, env=env)
            receipt = {'utc': stamp(), 'pid': process.pid, 'index': i, 'argv': job['argv'],
                       'question': job['question'], 'log': str(logpath)}
            (args.work / f'question-{i}-launch.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print(json.dumps(receipt), flush=True)
            code = process.wait()
        summary = Path(job['summary'])
        if code != 0 or not summary.exists():
            fail = {**receipt, 'exit_code': code, 'status': 'QUEUE HALTED AT FAILED QUESTION'}
            (args.work / 'failure.json').write_text(json.dumps(fail, indent=2) + '\n')
            print(json.dumps(fail), flush=True)
            raise SystemExit(1)
        completed.append({'index': i, 'question': job['question'], 'summary': str(summary),
                          'summary_sha256': hashlib.sha256(summary.read_bytes()).hexdigest(),
                          'exit_code': code})
        (args.work / 'checkpoint.json').write_text(json.dumps(completed, indent=2) + '\n')
    result = {'utc': stamp(), 'status': 'COMPLETE BOUNDED MATHEMATICAL GPU QUEUE',
              'completed': completed}
    (args.work / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
