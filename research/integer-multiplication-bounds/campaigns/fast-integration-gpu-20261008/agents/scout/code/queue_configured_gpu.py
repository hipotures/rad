#!/usr/bin/env python3
"""Launch a fresh, versioned scientific configuration after an owned receipt.

The queue never signals a PID. Missing or failed predecessor evidence blocks
launch; the finite successor is a distinct mathematical question.
"""
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    source = Path(cfg['source_path'])
    assert digest(source) == cfg['source_sha256']
    output = Path(cfg['output'])
    assert not output.exists()
    previous = Path(cfg['predecessor_output'])
    protocol = json.loads((previous / 'protocol.json').read_text())
    assert protocol['source_sha256'] == cfg['predecessor_source_sha256']
    assert protocol['device'] == cfg['device']
    while not (previous / 'summary.json').exists():
        assert not (previous / 'failure.json').exists()
        time.sleep(1)
    receipt = json.loads((previous / 'summary.json').read_text())
    assert receipt['status'] == 'COMPLETE JOINT FINITE FIELD LOCI DISCOVERY'
    assert receipt['source_sha256'] == cfg['predecessor_source_sha256']
    count = receipt['joint_class_partition'][1] - receipt['joint_class_partition'][0]
    assert receipt['unique_joint_classes_completed'] == count
    assert all(sum(h.values()) == count for h in receipt['profile_cut_histograms_by_fixture'])
    assert digest(source) == cfg['source_sha256']
    environment = os.environ.copy()
    environment.update(cfg['environment'])
    log = Path(cfg['stdout_log'])
    log.parent.mkdir(parents=True, exist_ok=True)
    print(json.dumps({'utc': datetime.now(timezone.utc).isoformat(),
                      'state': 'LAUNCHING DISTINCT FOLLOWUP',
                      'question': cfg['mathematical_question'],
                      'config_sha256': digest(args.config)}), flush=True)
    with log.open('x') as stream:
        process = subprocess.Popen(cfg['command'], env=environment, stdout=stream, stderr=subprocess.STDOUT)
        print(json.dumps({'utc': datetime.now(timezone.utc).isoformat(),
                          'actual_successor_pid': process.pid,
                          'device': cfg['device'], 'output': str(output)}), flush=True)
        status = process.wait()
    assert status == 0, {'returncode': status, 'log': str(log)}
    assert (output / 'summary.json').is_file()
    print(json.dumps({'utc': datetime.now(timezone.utc).isoformat(),
                      'state': 'COMPLETE FOLLOWUP RECEIPT', 'output': str(output)}), flush=True)


if __name__ == '__main__':
    main()
