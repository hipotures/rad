#!/usr/bin/env python3
"""Start one fresh GPU job after an owned finite predecessor completes cleanly.

No PID control. Live command lines are checked solely to detect an exited
predecessor without a complete receipt. The next exact command is versioned.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--current-output', type=Path, required=True)
    parser.add_argument('--next-config', type=Path, required=True)
    parser.add_argument('--log', type=Path, required=True)
    args = parser.parse_args()
    configuration = json.loads(args.next_config.read_text())
    source = Path(configuration['source_path'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == configuration['source_sha256']
    assert not Path(configuration['output']).exists()
    assert configuration['mathematical_change'].startswith('Complementary class partition at different controlled permutation')
    protocol = json.loads((args.current_output / 'protocol.json').read_text())
    assert protocol['device'] == configuration['device']
    assert protocol['source_sha256'] == configuration['source_sha256']
    print(json.dumps({'utc': stamp(), 'state': 'WAITING FOR OWNED COMPLETE RECEIPT',
                      'current_output': str(args.current_output),
                      'next_config_sha256': hashlib.sha256(args.next_config.read_bytes()).hexdigest()}), flush=True)
    missing_since = None
    while not (args.current_output / 'summary.json').exists():
        assert not (args.current_output / 'failure.json').exists(), 'Predecessor failed; next job not launched'
        live = False
        for process in Path('/proc').iterdir():
            if not process.name.isdecimal():
                continue
            try:
                argv = (process / 'cmdline').read_bytes().decode().split('\0')
            except (OSError, UnicodeDecodeError):
                continue
            if '--output' in argv and argv[argv.index('--output') + 1] == str(args.current_output):
                live = True
                break
        if live:
            missing_since = None
        elif missing_since is None:
            missing_since = time.monotonic()
        else:
            assert time.monotonic() - missing_since < 5, 'Predecessor exited without complete receipt'
        time.sleep(1)
    summary = json.loads((args.current_output / 'summary.json').read_text())
    assert summary['status'] == 'COMPLETE JOINT FINITE FIELD LOCI DISCOVERY'
    start, end = protocol['joint_class_partition']
    assert summary['unique_joint_classes_completed'] == end - start
    assert all(sum(axis.values()) == end - start for axis in summary['profile_cut_histograms_by_fixture'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == configuration['source_sha256']
    assert not Path(configuration['output']).exists() and not args.log.exists()
    env = dict(os.environ)
    env.update(configuration['env'])
    print(json.dumps({'utc': stamp(), 'state': 'LAUNCHING FRESH COMPLEMENTARY PERMUTATION RANGE',
                      'predecessor_summary_sha256': hashlib.sha256((args.current_output / 'summary.json').read_bytes()).hexdigest(),
                      'next_output': configuration['output']}), flush=True)
    with args.log.open('x') as log:
        result = subprocess.run(configuration['argv'], env=env, stdout=log, stderr=subprocess.STDOUT)
    print(json.dumps({'utc': stamp(), 'state': 'NEXT JOB EXITED', 'returncode': result.returncode,
                      'output': configuration['output']}), flush=True)
    assert result.returncode == 0


if __name__ == '__main__':
    main()
