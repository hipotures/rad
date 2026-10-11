#!/usr/bin/env python3
"""Insert a finite exact-basis DATA question after a live GPU job finishes.

The queue host is paused, while its current useful GPU child finishes
unchanged. A source-bound full-family question then runs, and the original
queue resumes. PIDs are checked against fresh /proc command and start time.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def stamp():
    return datetime.now(timezone.utc).isoformat()


def identity(pid):
    proc = Path('/proc')/str(pid)
    command = proc.joinpath('cmdline').read_bytes().split(b'\0')
    fields = proc.joinpath('stat').read_text().rsplit(')', 1)[1].split()
    return {'pid':pid,'start_ticks':fields[19],
            'command':[x.decode() for x in command if x]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config',type=Path,required=True)
    args = ap.parse_args()
    config = json.loads(args.config.read_text())
    work = Path(config['work'])
    assert not work.exists();work.mkdir(parents=True)
    queue = config['queue_pid']
    queue_identity = identity(queue)
    assert queue_identity['command'] == config['queue_command']
    state = json.loads(Path(config['queue_status']).read_text())
    assert state['queue_pid'] == queue and state['state'] == 'running'
    child = state['actual_child_pid'];child_identity = identity(child)
    assert child_identity['command'] == state['command']
    predecessor = Path(state['command'][state['command'].index('--output')+1])
    receipt = {'utc':stamp(),'state':'waiting for active finite child to finish',
               'queue_identity':queue_identity,'child_identity':child_identity,
               'predecessor':str(predecessor),'config_sha256':hashlib.sha256(args.config.read_bytes()).hexdigest(),
               'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (work/'status.json').write_text(json.dumps(receipt,indent=2)+'\n')
    assert identity(queue) == queue_identity
    os.kill(queue,signal.SIGSTOP)
    try:
        while not (predecessor/'summary.json').exists():
            assert identity(queue) == queue_identity
            try:
                assert identity(child) == child_identity
            except FileNotFoundError:
                raise RuntimeError('Active child exited before completing its finite result.')
            time.sleep(2)
        # Completion files are written before the process has fully released
        # its CUDA context. Wait for exit or zombie state, without killing it.
        while Path('/proc',str(child),'stat').exists():
            fields = Path('/proc',str(child),'stat').read_text().rsplit(')',1)[1].split()
            if fields[0]=='Z':break
            time.sleep(1)
        prior = json.loads((predecessor/'summary.json').read_text())
        assert prior['unique_joint_classes_completed'] == prior['parameter_pairs']
        receipt['predecessor_summary_sha256'] = hashlib.sha256((predecessor/'summary.json').read_bytes()).hexdigest()
        env = dict(os.environ)
        for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
        env['PYTHONDONTWRITEBYTECODE']='1';env['CUPY_CACHE_DIR']=str(work/'cupy')
        completed=[]
        for job in config['jobs']:
            output=Path(job['output']);assert not output.exists()
            for dependency in job['dependencies']:
                assert hashlib.sha256(Path(dependency['path']).read_bytes()).hexdigest()==dependency['sha256']
            with (work/f'{job["name"]}.log').open('xb') as log:
                task=subprocess.Popen(job['command'],stdout=log,stderr=subprocess.STDOUT,env=env)
                receipt.update({'utc':stamp(),'state':'running priority full-family question',
                                'actual_child_pid':task.pid,'command':job['command'],'completed':completed})
                (work/'status.json').write_text(json.dumps(receipt,indent=2)+'\n')
                print(json.dumps({'state':receipt['state'],'actual_child_pid':task.pid,'output':str(output)}),flush=True)
                code=task.wait()
            assert code==0,(job['name'],code)
            summary=output/'summary.json';result=json.loads(summary.read_text())
            assert result['source_pairs_completed']==4073300
            completed.append({'name':job['name'],'summary':str(summary),
                              'sha256':hashlib.sha256(summary.read_bytes()).hexdigest()})
        receipt.update({'utc':stamp(),'state':'priority question complete; original queue resumed','completed':completed})
        (work/'summary.json').write_text(json.dumps(receipt,indent=2)+'\n')
        (work/'status.json').write_text(json.dumps(receipt,indent=2)+'\n')
    finally:
        assert identity(queue)==queue_identity
        os.kill(queue,signal.SIGCONT)


if __name__=='__main__':
    main()
