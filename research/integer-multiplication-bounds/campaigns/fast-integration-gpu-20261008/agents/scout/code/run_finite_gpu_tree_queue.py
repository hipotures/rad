#!/usr/bin/env python3
"""Run a finite, source-bound sequence of distinct joint endpoint questions."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def stamp():
    return datetime.now(timezone.utc).isoformat()


def endpoint(record):
    a = record['permutations'] if 'permutations' in record else record['actual_permutation']
    labels = [a[i%25][i//25] for i in range(47)]
    labels += [a[(528+i)%25][(528+i)//25] for i in range(47)]
    return hashlib.sha256(json.dumps(labels,separators=(',',':')).encode()).hexdigest()


def tree(labels):
    parents = list(range(48))
    def root(x):
        while parents[x] != x:
            parents[x] = parents[parents[x]];x = parents[x]
        return x
    for i,r in enumerate(labels):
        a,b = root(r),root(23+i%25)
        if a == b:return False
        parents[a] = b
    return len({root(x) for x in range(48)}) == 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--device',type=int,required=True)
    args = ap.parse_args()
    assert args.device in (0,1)
    config = json.loads(args.config.read_text())
    work = Path(config['queue_work'])/f'device{args.device}'
    assert not work.exists();work.mkdir(parents=True)
    configs = [x for x in config['jobs'] if x['device'] == args.device]
    assert len(configs) == 6
    env = dict(os.environ)
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    predecessor = Path(config['predecessors'][str(args.device)])
    while not (predecessor/'summary.json').exists():
        (work/'status.json').write_text(json.dumps({'utc':stamp(),'state':'waiting for finite predecessor','predecessor':str(predecessor),'pid':os.getpid()})+'\n')
        time.sleep(5)
    prior = json.loads((predecessor/'summary.json').read_text())
    assert prior['unique_joint_classes_completed'] == prior['parameter_pairs']
    used = set()
    for path in Path(config['derived_root']).glob('gpu-basis-*/protocol.json'):
        p = json.loads(path.read_text())
        if (p.get('method_kind') == 'exhaustive_joint_finite_field_loci'
                and p.get('device') == args.device and 'actual_permutation' in p):
            used.add(endpoint(p))
    completed = []
    for job in configs:
        permutation_path = Path(job['permutation'])
        data = json.loads(permutation_path.read_text())
        assert hashlib.sha256(permutation_path.read_bytes()).hexdigest() == job['permutation_sha256']
        key = endpoint(data)
        assert key == job['endpoint_sha256'] and key not in used
        a = data['permutations']
        assert tree([a[i%25][i//25] for i in range(47)])
        # Column right labels start at 528 rather than zero; translate before
        # using the same bipartite-tree test.
        labels = [a[(528+i)%25][(528+i)//25] for i in range(47)]
        # Direct column tree, with its actual right-coordinate labels.
        parents = list(range(48))
        def root(x):
            while parents[x] != x:parents[x] = parents[parents[x]];x=parents[x]
            return x
        for i,r in enumerate(labels):
            x,y=root(r),root(23+(528+i)%25)
            assert x != y;parents[x]=y
        assert len({root(x) for x in range(48)}) == 1
        output = Path(job['output']);assert not output.exists()
        command = [sys.executable,config['worker_source'],'--device',str(args.device),'--seed',str(job['seed']),
                   '--batch','32768','--pr54-snapshot',config['snapshot'],'--permutation',str(permutation_path),'--output',str(output)]
        env['CUPY_CACHE_DIR'] = str(work/f'cupy-{job["catalogue_index"]:04d}')
        with (work/f'order-{job["catalogue_index"]:04d}.log').open('xb') as log:
            child = subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env)
            state = {'utc':stamp(),'state':'running','queue_pid':os.getpid(),'actual_child_pid':child.pid,'command':command,'completed_orders':completed}
            (work/'status.json').write_text(json.dumps(state,indent=2)+'\n')
            print(json.dumps(state),flush=True)
            code = child.wait()
        assert code == 0, (job,code)
        result = json.loads((output/'summary.json').read_text())
        assert result['unique_joint_classes_completed'] == result['parameter_pairs']
        completed.append({'catalogue_index':job['catalogue_index'],'output':str(output),
                          'summary_sha256':hashlib.sha256((output/'summary.json').read_bytes()).hexdigest()})
        used.add(key)
    (work/'summary.json').write_text(json.dumps({'utc':stamp(),'state':'complete finite queue','completed':completed,'config_sha256':hashlib.sha256(args.config.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')


if __name__ == '__main__':
    main()
