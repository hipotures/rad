"""Supervise four independent existing-login Codex parents and two bounded evaluator workers."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time

from .bootstrap_broker import Broker
from .bootstrap_launch import CAMPAIGN
from .bootstrap_prepare import TOPIC, verify


def main():
    verify()
    root=TOPIC/'work/phaseD-bootstrap/execution'
    root.mkdir(parents=True,exist_ok=True)
    logs=root/'logs';logs.mkdir(exist_ok=True)
    if (root/'supervisor.json').exists():
        raise RuntimeError('campaign already started; inspect recorded process state, do not duplicate')
    raw=TOPIC/'work/raw'/CAMPAIGN;raw.mkdir(parents=True,exist_ok=True)
    (root/'results').symlink_to(raw,target_is_directory=True)
    for i in range(1,5):Broker(f'phaseD-parent-{i:02d}',root)
    devices=subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True).strip().splitlines()[:2]
    workers=[];parents=[];streams=[]
    base=dict(os.environ,PYTHONPATH=str(TOPIC/'code'),TMPDIR=str(TOPIC/'work/tmp'),
              HF_HOME=str(TOPIC/'work/cache/hf'),XDG_CACHE_HOME=str(TOPIC/'work/cache'),
              VLLM_CACHE_ROOT=str(TOPIC/'work/cache/vllm-bench'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    started=time.time()
    try:
        for device in devices:
            f=(logs/f'worker-{device}.log').open('x');streams.append(f)
            cmd=[str(TOPIC/'work/envs/vllm/bin/python'),'-m','wse.bootstrap_worker','--root',str(root),'--campaign',CAMPAIGN,'--follow']
            workers.append(subprocess.Popen(cmd,env=dict(base,CUDA_VISIBLE_DEVICES=device),stdout=f,stderr=f,start_new_session=True,cwd=TOPIC))
        for i in range(1,5):
            sid=f'phaseD-parent-{i:02d}';f=(logs/f'{sid}-launcher.log').open('x');streams.append(f)
            parents.append(subprocess.Popen([str(TOPIC/'work/envs/wse/bin/python'),'-m','wse.bootstrap_launch',
                 '--session',sid,'--root',str(root)],env=base,stdout=f,stderr=f,start_new_session=True,cwd=TOPIC))
        state={'started':started,'supervisor_pid':os.getpid(),'workers':[p.pid for p in workers],
               'parents':[p.pid for p in parents],'devices':devices,'campaign':CAMPAIGN,'status':'running'}
        (root/'supervisor.json').write_text(json.dumps(state,indent=2))
        print(json.dumps(state),flush=True)
        while any(p.poll() is None for p in parents):
            if any(w.poll() is not None for w in workers):raise RuntimeError('evaluator worker exited before parents finished')
            if time.time()-started>15000:raise RuntimeError('campaign wall limit reached')
            time.sleep(5)
        (root/'queue/STOP').touch()
        returns=[p.wait(timeout=600) for p in workers]
        state.update(status='terminal',parent_returncodes=[p.returncode for p in parents],worker_returncodes=returns,
                     wall_s=time.time()-started)
        (root/'supervisor.json').write_text(json.dumps(state,indent=2))
        print(json.dumps(state),flush=True)
    finally:
        for p in parents+workers:
            try:os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError:pass
        for f in streams:f.close()


if __name__=='__main__':
    main()
