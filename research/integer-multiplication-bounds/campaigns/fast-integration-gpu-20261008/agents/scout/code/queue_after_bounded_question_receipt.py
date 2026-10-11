#!/usr/bin/env python3
"""Launch one pinned GPU successor after an owned bounded queue completes."""
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
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config', type=Path, required=True)
    args = ap.parse_args()
    config = json.loads(args.config.read_text())
    source = Path(config['source_path'])
    assert digest(source) == config['source_sha256']
    queue = Path(config['predecessor_queue'])
    protocol = json.loads((queue / 'protocol.json').read_text())
    assert protocol['config_sha256'] == config['predecessor_config_sha256']
    assert protocol['queue']['device'] == config['device']
    assert not Path(config['output']).exists()
    while not (queue / 'summary.json').exists():
        assert not (queue / 'failure.json').exists(), 'Owned predecessor failed'
        time.sleep(1)
    receipt = json.loads((queue / 'summary.json').read_text())
    assert receipt['status'] == 'COMPLETE BOUNDED MATHEMATICAL GPU QUEUE'
    assert len(receipt['completed']) == len(protocol['queue']['questions'])
    for row in receipt['completed']:
        assert row['exit_code'] == 0
        assert digest(Path(row['summary'])) == row['summary_sha256']
    assert digest(source) == config['source_sha256']
    assert not Path(config['output']).exists()
    for dependency in config.get('dependencies', []):
        assert digest(Path(dependency['path'])) == dependency['sha256']
    environment = dict(os.environ)
    environment.update(config.get('environment', {}))
    launch = {'utc': datetime.now(timezone.utc).isoformat(),
              'device': config['device'], 'question': config['question'],
              'config_sha256': digest(args.config),
              'predecessor_summary_sha256': digest(queue / 'summary.json'),
              'argv': config['argv']}
    with Path(config['stdout_log']).open('x') as log:
        process = subprocess.Popen(config['argv'], stdout=log,
                                   stderr=subprocess.STDOUT, env=environment)
        launch['actual_compute_pid'] = process.pid
        Path(config['launch_receipt']).write_text(json.dumps(launch, indent=2)+'\n')
        print(json.dumps(launch), flush=True)
        assert process.wait() == 0
    assert (Path(config['output']) / 'summary.json').exists()


if __name__ == '__main__':
    main()
