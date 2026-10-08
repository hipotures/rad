#!/usr/bin/env python3
"""One persistent mathematical worker; recover only unfinished configurations."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--completed-queue', type=Path, action='append', default=[])
    args = parser.parse_args()
    assert not args.output.exists()
    args.output.mkdir(parents=True)
    script = Path(__file__).with_name('region_schedule_family.py').resolve()
    helper = script.with_name('causal_region_order.py')
    config = script.parents[1]/'configs/causal-selective-hybrids.json'
    policies = ['rank-pressure']
    jobs = [(policy, h) for policy in policies for h in (23, 25)]
    protocol = dict(recorded_utc=datetime.now(timezone.utc).isoformat(), jobs=jobs,
                    source_commit='bc2f7ed4c20dc18898305ab17165c0c995cbb804',
                    threads=1, completed_queues=[str(p) for p in args.completed_queue],
                    sources={str(p): dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                                         text=p.read_text()) for p in (script, helper, config)})
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    seen = {23: set(), 25: set()}
    for old in args.completed_queue:
        for result in old.glob('job*/case00/result.json'):
            data = json.loads(result.read_text())
            seen[data['fixed_profile']['h']].add(data['word_sha256'])
    completed = []
    for index, (policy, h) in enumerate(jobs):
        name = 'job%02d-%s-h%d' % (index, policy, h)
        if any((old/name/'case00/result.json').exists() for old in args.completed_queue):
            continue
        out = args.output/name
        command = [sys.executable, '-B', str(script), '--source-root', str(args.source_root),
                   '--dimension', str(h), '--schedule', policy, '--retired-policy', 'high-rank',
                   '--config', str(config), '--output', str(out)]
        print(json.dumps(dict(event='launch', command=command)), flush=True)
        subprocess.run(command, check=True, env=env)
        data = json.loads((out/'case00/result.json').read_text())
        digest = data['word_sha256']
        receipt = dict(job=index, word_sha256=digest, exact_duplicate_word=digest in seen[h])
        seen[h].add(digest)
        (out/'physical-word-dedup.json').write_text(json.dumps(receipt)+'\n')
        completed.append(receipt)
        print(json.dumps(dict(event='completed', R=data['fixed_profile']['R'], **receipt)), flush=True)
    (args.output/'complete.json').write_text(json.dumps(dict(status='COMPLETE', jobs=completed), indent=2)+'\n')


if __name__ == '__main__':
    main()
