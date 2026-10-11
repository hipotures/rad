#!/usr/bin/env python3
"""Resume an interrupted finite queue without repeating or replacing evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from run_finite_gpu_tree_queue import endpoint, tree


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def process_identity(pid):
    try:
        stat = Path(f'/proc/{pid}/stat').read_text().split(') ', 1)[1].split()
        command = Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
        return stat[19], [x.decode() for x in command if x]
    except FileNotFoundError:
        return None


def check_trees(data):
    a = data['permutations']
    assert len(a) == 25 and all(sorted(column) == list(range(23)) for column in a)
    assert tree([a[i % 25][i // 25] for i in range(47)])
    parents = list(range(48))
    def root(x):
        while parents[x] != x:
            parents[x] = parents[parents[x]]
            x = parents[x]
        return x
    for i in range(47):
        k = 528 + i
        x, y = root(a[k % 25][k // 25]), root(23 + k % 25)
        assert x != y
        parents[x] = y
    assert len({root(x) for x in range(48)}) == 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', type=Path, required=True)
    ap.add_argument('--device', type=int, required=True)
    ap.add_argument('--adopt-launch', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    args = ap.parse_args()
    assert args.device in (0, 1)
    config = json.loads(args.config.read_text())
    launch = json.loads(args.adopt_launch.read_text())
    assert launch['config_sha256'] == digest(args.config)
    adopted = next(x for x in launch['children'] if x['device'] == args.device)
    work = args.work / f'device{args.device}'
    work.mkdir(exist_ok=False, parents=True)
    env = dict(os.environ)
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[key] = '1'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    completed = []
    seen = set()

    def state(value):
        value = dict(value, utc=datetime.now(timezone.utc).isoformat(), queue_pid=os.getpid())
        (work / 'status.json').write_text(json.dumps(value, indent=2) + '\n')
        print(json.dumps(value), flush=True)

    for job in (x for x in config['jobs'] if x['device'] == args.device):
        permutation = Path(job['permutation'])
        assert digest(permutation) == job['permutation_sha256']
        data = json.loads(permutation.read_text())
        check_trees(data)
        key = endpoint(data)
        assert key == job['endpoint_sha256'] and key not in seen
        seen.add(key)
        output = Path(job['output'])
        summary = output / 'summary.json'
        command = [sys.executable, config['worker_source'], '--device', str(args.device),
                   '--seed', str(job['seed']), '--batch', '32768', '--pr54-snapshot',
                   config['snapshot'], '--permutation', str(permutation), '--output', str(output)]
        if not summary.exists():
            if job['catalogue_index'] == adopted['order']:
                assert command == adopted['command']
                pid = adopted['pid']
                identity = process_identity(pid)
                assert identity is not None and identity[1] == command, (pid, identity)
                state({'state': 'adopted live mathematical child', 'child_pid': pid,
                       'command': command, 'completed_orders': completed})
                while not summary.exists():
                    current = process_identity(pid)
                    assert current is not None and current[0] == identity[0], 'Adopted child ended without a summary'
                    time.sleep(5)
            else:
                assert not output.exists(), 'Refusing to overwrite incomplete evidence'
                env['CUPY_CACHE_DIR'] = str(work / f'cupy-{job["catalogue_index"]:04d}')
                with (work / f'order-{job["catalogue_index"]:04d}.log').open('xb') as log:
                    child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
                    state({'state': 'running distinct mathematical job', 'child_pid': child.pid,
                           'command': command, 'completed_orders': completed})
                    assert child.wait() == 0
        result = json.loads(summary.read_text())
        assert result['unique_joint_classes_completed'] == result['parameter_pairs']
        completed.append({'catalogue_index': job['catalogue_index'], 'output': str(output),
                          'summary_sha256': digest(summary), 'parameter_pairs': result['parameter_pairs']})
    receipt = {'state': 'complete finite queue', 'completed': completed,
               'config_sha256': digest(args.config), 'launch_sha256': digest(args.adopt_launch),
               'source_sha256': digest(Path(__file__)),
               'scope': 'Finite-field discovery; not a rational or full-network certificate'}
    state(receipt)
    (work / 'summary.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
