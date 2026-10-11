#!/usr/bin/env python3
"""Launch a frozen mathematical GPU successor after an owned word search.

The predecessor is identified by its immutable protocol, physical word and
transition hashes. A completed discovery receipt authorizes scheduling only;
it does not promote modular scores to rational or conditional certificates.
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
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config', type=Path, required=True)
    args = ap.parse_args()
    config = json.loads(args.config.read_text())
    protocol_path = Path(config['predecessor_protocol'])
    assert digest(protocol_path) == config['predecessor_protocol_sha256']
    protocol = json.loads(protocol_path.read_text())
    for key in ('device', 'word_sha256', 'transition_sha256'):
        assert protocol[key] == config['predecessor'][key]
    output = Path(config['output'])
    assert not output.exists()
    summary_path = Path(config['predecessor_summary'])
    while not summary_path.exists():
        # This waiter neither touches the GPU nor controls a live process by
        # an archived PID. Failed searches stay visible for diagnosis.
        time.sleep(1)
    summary = json.loads(summary_path.read_text())
    assert summary['status'] == config['predecessor_status']
    for key in ('device', 'word_sha256', 'transition_sha256'):
        assert summary[key] == config['predecessor'][key]
    for item in config['dependencies']:
        assert digest(item['path']) == item['sha256']
    assert not output.exists()
    environment = dict(os.environ)
    environment.update(config.get('environment', {}))
    launch = {
        'utc': datetime.now(timezone.utc).isoformat(),
        'question': config['question'], 'device': config['device'],
        'config_sha256': digest(args.config),
        'predecessor_summary_sha256': digest(summary_path),
        'argv': config['argv'],
    }
    with Path(config['stdout_log']).open('x') as log:
        child = subprocess.Popen(config['argv'], stdout=log,
                                 stderr=subprocess.STDOUT, env=environment)
        launch['actual_compute_pid'] = child.pid
        Path(config['launch_receipt']).write_text(json.dumps(launch, indent=2) + '\n')
        print(json.dumps(launch), flush=True)
        code = child.wait()
    assert code == 0, f'Mathematical successor failed with exit status {code}'
    assert (output / 'summary.json').exists()


if __name__ == '__main__':
    main()
