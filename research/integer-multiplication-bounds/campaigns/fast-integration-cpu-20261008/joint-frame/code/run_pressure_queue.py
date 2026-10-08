#!/usr/bin/env python3
"""Distinct paid clearing policies under the new causal regional scheduler."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', required=True, type=Path)
    parser.add_argument('--h', required=True, type=int, choices=(23,25))
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert not args.output.exists()
    args.output.mkdir(parents=True)
    script = Path(__file__).with_name('region_schedule_family.py').resolve()
    config = script.parents[1]/'configs/reclamation-fixed-dag.json'
    jobs = [('dense-first',0),('sparse-first',0),('seeded',31),('seeded',113),('seeded',233)]
    (args.output/'protocol.json').write_text(json.dumps(dict(
        recorded_utc=datetime.now(timezone.utc).isoformat(), jobs=jobs, h=args.h,
        schedule='rank-pressure', threads=1,
        source_commit='bc2f7ed4c20dc18898305ab17165c0c995cbb804',
        driver_source=script.read_text(), helper_source=script.with_name('causal_region_order.py').read_text(),
        driver_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
        config=json.loads(config.read_text())),indent=2)+'\n')
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    seen = set()
    repeated = 0
    for index, (policy, seed) in enumerate(jobs):
        out = args.output/('job%02d'%index)
        command = [sys.executable,'-B',str(script),'--source-root',str(args.source_root),
                   '--dimension',str(args.h),'--schedule','rank-pressure',
                   '--retired-policy',policy,'--order-seed',str(seed),
                   '--config',str(config),'--output',str(out)]
        print(json.dumps(dict(event='launch',command=command)),flush=True)
        subprocess.run(command,env=env,check=True)
        result=json.loads((out/'case00/result.json').read_text())
        digest=result['word_sha256']; duplicate=digest in seen
        repeated=repeated+1 if duplicate else 0
        seen.add(digest)
        (out/'physical-word-dedup.json').write_text(json.dumps(dict(
            word_sha256=digest,exact_duplicate_word=duplicate))+'\n')
        print(json.dumps(dict(event='completed',h=args.h,policy=policy,seed=seed,
                              R=result['fixed_profile']['R'],duplicate=duplicate)),flush=True)
        if repeated >= 2:
            print(json.dumps(dict(event='stop_redundant_queue',reason='Two consecutive identical physical words.')),flush=True)
            break
    (args.output/'complete.json').write_text(json.dumps(dict(status='COMPLETE',distinct_words=len(seen)))+'\n')


if __name__=='__main__':
    main()
