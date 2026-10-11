#!/usr/bin/env python3
"""Run frozen useful questions after independently checked finite receipts."""
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


def complete(summary, kind, device, source_hash, orders=None):
    assert summary['device'] == device and summary['source_sha256'] == source_hash
    if kind == 'joint_field':
        assert summary['method_kind'] == 'exhaustive_joint_finite_field_loci'
        assert summary['unique_joint_classes_completed'] == summary['parameter_pairs']
        assert all(sum(hist.values()) == summary['parameter_pairs']
                   for hist in summary['profile_cut_histograms_by_fixture'])
    elif kind == 'boundary_catalogue':
        assert summary['method_kind'] == 'full_source_family_multiswap_catalogue'
        assert len(summary['completed_receipts']) == orders
    else:
        assert kind == 'finite_queue'
        assert summary['state'] == 'complete bounded GPU questions'
        assert len(summary['completed']) == orders


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', type=Path, required=True)
    args = ap.parse_args()
    cfg = json.loads(args.config.read_text())
    work = Path(cfg['queue_work'])
    assert not work.exists()
    work.mkdir(parents=True)
    predecessor = Path(cfg['predecessor']) / 'summary.json'
    while not predecessor.exists():
        (work / 'status.json').write_text(json.dumps({
            'utc': datetime.now(timezone.utc).isoformat(), 'state': 'waiting for useful predecessor',
            'queue_pid': os.getpid(), 'device': cfg['device'], 'predecessor': str(predecessor)}) + '\n')
        time.sleep(5)
    prior = json.loads(predecessor.read_text())
    complete(prior, cfg['predecessor_kind'], cfg['device'],
             cfg['predecessor_source_sha256'], cfg.get('predecessor_orders'))
    env = dict(os.environ)
    env.update(cfg['environment'])
    completed = []
    for index, job in enumerate(cfg['jobs']):
        assert digest(job['source']) == job['source_sha256']
        assert not Path(job['output']).exists()
        for item in job['immutable_inputs']:
            assert digest(item['path']) == item['sha256']
        env['CUPY_CACHE_DIR'] = str(work / f'cupy-{index}')
        with (work / f'job-{index}.log').open('xb') as stream:
            child = subprocess.Popen(job['command'], stdout=stream, stderr=subprocess.STDOUT, env=env)
            status = {'utc': datetime.now(timezone.utc).isoformat(),
                      'state': 'running distinct mathematical GPU question',
                      'queue_pid': os.getpid(), 'device': cfg['device'], 'actual_child_pid': child.pid,
                      'question': job['question'], 'command': job['command'], 'completed': completed}
            (work / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
            print(json.dumps(status), flush=True)
            assert child.wait() == 0
        result = Path(job['output']) / 'summary.json'
        complete(json.loads(result.read_text()), job['kind'], cfg['device'],
                 job['source_sha256'], job.get('orders'))
        completed.append({'question': job['question'], 'output': job['output'],
                          'summary_sha256': digest(result), 'classification': 'DISCOVERY'})
    final = {'utc': datetime.now(timezone.utc).isoformat(), 'state': 'complete bounded GPU questions',
             'device': cfg['device'], 'completed': completed,
             'source_sha256': digest(__file__), 'config_sha256': digest(args.config),
             'predecessor_summary_sha256': digest(predecessor)}
    (work / 'summary.json').write_text(json.dumps(final, indent=2) + '\n')
    print(json.dumps(final), flush=True)


if __name__ == '__main__':
    main()
