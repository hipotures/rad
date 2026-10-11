#!/usr/bin/env python3
"""Execute distinct pinned GPU questions after a complete source-family queue."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', type=Path, required=True)
    args = ap.parse_args()
    cfg = json.loads(args.config.read_text())
    work = Path(cfg['queue_work'])
    assert not work.exists()
    work.mkdir(parents=True)
    completed = []
    predecessor = Path(cfg['predecessor'])
    while not (predecessor / 'summary.json').exists():
        time.sleep(5)
    prior = json.loads((predecessor / 'summary.json').read_text())
    assert prior['device'] == cfg['device']
    assert prior['source_sha256'] == cfg['predecessor_source_sha256']
    assert prior['method_kind'] == 'full_source_family_single_swap_catalogue'
    assert len(prior['completed_receipts']) == cfg['predecessor_orders']
    env = dict(os.environ)
    env.update(cfg['environment'])
    for index, job in enumerate(cfg['jobs']):
        assert digest(job['source']) == job['source_sha256']
        assert not Path(job['output']).exists()
        for row in job.get('immutable_inputs', []):
            assert digest(row['path']) == row['sha256']
        env['CUPY_CACHE_DIR'] = str(work / f'cupy-{index}')
        with (work / f'job-{index}.log').open('xb') as stream:
            child = subprocess.Popen(job['command'], stdout=stream, stderr=subprocess.STDOUT, env=env)
            state = {'utc': datetime.now(timezone.utc).isoformat(), 'state': 'running distinct GPU question',
                     'queue_pid': os.getpid(), 'device': cfg['device'], 'actual_child_pid': child.pid,
                     'question': job['question'], 'command': job['command'], 'completed': completed}
            (work / 'status.json').write_text(json.dumps(state, indent=2) + '\n')
            print(json.dumps(state), flush=True)
            assert child.wait() == 0
        summary_path = Path(job['output']) / 'summary.json'
        summary = json.loads(summary_path.read_text())
        assert summary['device'] == cfg['device'] and summary['source_sha256'] == job['source_sha256']
        if job['kind'] == 'whole_family':
            assert summary['source_pairs_completed'] == summary['source_family_size'] == 4073300
            assert summary['whole_family_on_device']
        else:
            assert summary['method_kind'] == 'full_source_family_single_swap_catalogue'
            assert len(summary['completed_receipts']) == job['orders']
        completed.append({'question': job['question'], 'output': job['output'],
                          'summary_sha256': digest(summary_path), 'classification': 'DISCOVERY'})
    final = {'utc': datetime.now(timezone.utc).isoformat(), 'state': 'complete bounded GPU questions',
             'device': cfg['device'], 'completed': completed, 'source_sha256': digest(Path(__file__)),
             'config_sha256': digest(args.config)}
    (work / 'summary.json').write_text(json.dumps(final, indent=2) + '\n')
    print(json.dumps(final), flush=True)


if __name__ == '__main__':
    main()
