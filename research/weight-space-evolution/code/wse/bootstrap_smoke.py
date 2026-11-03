"""Two-GPU broker-to-evaluator control run. Synthetic edits are explicitly not parent candidates."""
import json
import os
from pathlib import Path
import subprocess
import time

from .bootstrap_broker import Broker, GOLD, TIERS
from .bootstrap_prepare import TOPIC, verify


def main():
    verify()
    root=TOPIC/'work/phaseD-bootstrap/broker-smoke'
    root.mkdir(parents=True,exist_ok=True)
    if (root/'ledger.sqlite').exists():
        raise RuntimeError('smoke already exists; inspect existing state, do not overwrite')
    campaign='20261103T-phaseD-bootstrap-broker-smoke'
    raw=TOPIC/'work/raw'/campaign;raw.mkdir(parents=True,exist_ok=True)
    (root/'results').symlink_to(raw,target_is_directory=True)
    started=time.time();jobs=[]
    for i in range(1,5):
        b=Broker(f'phaseD-parent-{i:02d}',root)
        n='model.language_model.layers.15.mlp.down_proj.weight'
        code=f'reset()\nn={n!r}\nw=gold(n).copy()\nw.reshape(-1)[{i}]+=0.01\nsave(n,w)\nprint(saved())'
        res=b.call({'action':'run','code':code,'names':[n]})
        if res['returncode']!=0:
            raise RuntimeError(res)
        c=b.call({'action':'submit','rationale':'Operator-authored one-entry smoke control; not a parent proposal'})
        job=b.call({'action':'evaluate','patch_id':c['patch_id']})
        jobs.append({'session_id':b.sid,**c,**job})
    # E0 under identical conditions, queued before controls.
    d=root/'queue/pending'
    (d/'000-E0__dev.json').write_text(json.dumps({'job_id':'E0__dev','editor_id':'E0','split':'dev',
                                              'tiers':TIERS,'ids':None,'submitted_at':time.time()}))
    devices=subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True).strip().splitlines()
    if len(devices)<2:
        raise RuntimeError('two-GPU validation requires two visible devices')
    children=[];streams=[]
    try:
        for device in devices[:2]:
            stream=(root/f'worker-{device}.log').open('x');streams.append(stream)
            env=dict(os.environ,PYTHONPATH=str(TOPIC/'code'),CUDA_VISIBLE_DEVICES=device,
                     TMPDIR=str(TOPIC/'work/tmp'),HF_HOME=str(TOPIC/'work/cache/hf'),
                     XDG_CACHE_HOME=str(TOPIC/'work/cache'),VLLM_CACHE_ROOT=str(TOPIC/'work/cache/vllm-bench'),
                     OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
            children.append(subprocess.Popen([str(TOPIC/'work/envs/vllm/bin/python'),'-m','wse.bootstrap_worker',
                 '--root',str(root),'--campaign',campaign],env=env,cwd=TOPIC,stdout=stream,stderr=stream,start_new_session=True))
        returns=[p.wait(timeout=900) for p in children]
        if any(returns):
            raise RuntimeError(f'worker failure: {returns}')
    finally:
        import signal
        for child in children:
            try: os.killpg(child.pid,signal.SIGTERM)
            except ProcessLookupError: pass
        for stream in streams:stream.close()
    summaries=[]
    for p in sorted(raw.glob('*.summary.json')):
        rec=json.loads(p.read_text())
        if rec.get('error'):raise RuntimeError('evaluation failed')
        summaries.append({'job_id':rec['job_id'],'instances':rec['instances'],'summary':rec['summary'],
                          'gen':rec['gen'],'score_s':rec['score_s'],'transition':rec['transition']})
    audits=[json.loads(p.read_text())['final_audit'] for p in raw.glob('worker-*.json')]
    result={'kind':'operator-authored transport smoke; no parent inference', 'jobs':jobs,'summaries':summaries,
            'worker_returncodes':returns,'final_audits':audits,'devices':devices[:2],'wall_s':time.time()-started}
    if len(summaries)!=5 or len(audits)!=2 or not all(a['ok'] for a in audits):
        raise RuntimeError('incomplete smoke or failed Gold audit')
    out=TOPIC/'runs'/campaign/'results';out.mkdir(parents=True,exist_ok=True)
    (out/'smoke.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'completed_jobs':len(summaries),'audits_pass':True,'wall_s':result['wall_s']}))


if __name__=='__main__':
    main()
