#!/usr/bin/env python3
"""Launch a pinned successor after an already-running finite queue completes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', type=Path, required=True)
    args = ap.parse_args()
    cfg = json.loads(args.config.read_text())
    source = Path(cfg['source_path'])
    predecessor = Path(cfg['predecessor_queue_summary'])
    assert digest(source) == cfg['source_sha256']
    assert not Path(cfg['output']).exists()
    while not predecessor.exists():
        time.sleep(5)
    queue = json.loads(predecessor.read_text())
    assert queue['state'] == 'complete finite queue'
    assert queue['config_sha256'] == cfg['predecessor_config_sha256']
    assert queue['source_sha256'] == cfg['predecessor_queue_source_sha256']
    assert [x['catalogue_index'] for x in queue['completed']] == cfg['predecessor_completed_indices']
    for row in queue['completed']:
        path = Path(row['output']) / 'summary.json'
        assert digest(path) == row['summary_sha256']
        completed = json.loads(path.read_text())
        count = completed['joint_class_partition'][1] - completed['joint_class_partition'][0]
        assert completed['status'] == 'COMPLETE JOINT FINITE FIELD LOCI DISCOVERY'
        assert completed['device'] == cfg['device']
        assert completed['unique_joint_classes_completed'] == count
        assert all(sum(x.values()) == count for x in completed['profile_cut_histograms_by_fixture'])
    assert digest(source) == cfg['source_sha256']
    assert not Path(cfg['output']).exists()
    env = dict(os.environ)
    env.update(cfg['environment'])
    log = Path(cfg['stdout_log'])
    log.parent.mkdir(parents=True, exist_ok=True)
    receipt = {'utc': datetime.now(timezone.utc).isoformat(), 'state': 'running distinct full-family successor',
               'device': cfg['device'], 'command': cfg['command'], 'question': cfg['mathematical_question'],
               'config_sha256': digest(args.config), 'predecessor_summary_sha256': digest(predecessor)}
    with log.open('x') as stream:
        child = subprocess.Popen(cfg['command'], env=env, stdout=stream, stderr=subprocess.STDOUT)
        receipt['actual_child_pid'] = child.pid
        print(json.dumps(receipt), flush=True)
        Path(cfg['launch_receipt']).write_text(json.dumps(receipt, indent=2) + '\n')
        assert child.wait() == 0
    summary = Path(cfg['output']) / 'summary.json'
    assert summary.exists()
    print(json.dumps({'utc': datetime.now(timezone.utc).isoformat(), 'state': 'complete distinct successor',
                      'summary_sha256': digest(summary), 'output': cfg['output']}), flush=True)


if __name__ == '__main__':
    main()
