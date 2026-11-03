"""Operator-only final fixed-candidate evaluation; parents never receive this queue or outputs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from . import patch, registry
from .tensors import bf16_bits_to_f32, f32_to_bf16_bits

from . import pd2_eval as E
from .bootstrap_broker import GOLD, Ledger, TIERS
from .bootstrap_prepare import TOPIC, verify
from .bootstrap_patch_archive import export

CONTROLS=['p50c','rand-dir-0','rand-dir-1','rand-dir-2','rand-dir-3','rand-sparse-0']


def sealed(root):
    ledger=Ledger(root)
    with ledger.connect() as db:
        rows=db.execute('SELECT id,sealed FROM sessions ORDER BY id').fetchall()
    if len(rows)!=4 or any(pid is None for _,pid in rows):raise RuntimeError('all four sessions must seal before final evaluation')
    return rows


def evaluate_worker(root,campaign):
    registry_path=root/'final-registry.json'
    registry=json.loads(registry_path.read_text())
    E.editors=lambda:{e['editor_id']:e for e in registry['editors']}
    E.worker(argparse.Namespace(queue=str(root/'final-queue'),campaign=campaign,swap_mode='direct',
             engine_profile='profile3',engine_json='{}',follow=True,allow_heldout=True))


def matched_control(pid, seed):
    names=sorted({t['name'] for member in patch.lineage(pid) for t in patch.load_patch(member)['tensors']})
    gold=registry.load(GOLD,names);cand=patch.materialize(GOLD,pid,names)
    rng=np.random.default_rng(seed);proposed={};details=[]
    for name in names:
        dt,b=gold[name];c=cand[name][1]
        if dt!='BF16':raise RuntimeError('expected BF16 candidate')
        base=bf16_bits_to_f32(b).reshape(-1);target=bf16_bits_to_f32(c).reshape(-1)
        idx=np.flatnonzero(b.reshape(-1)!=c.reshape(-1))
        if not len(idx):continue
        delta=target[idx].astype(np.float64)-base[idx].astype(np.float64)
        live=np.flatnonzero(base!=0)
        exclusive=np.setdiff1d(live,idx,assume_unique=True)
        pool=exclusive if len(exclusive)>=len(idx) else live
        if len(pool)<len(idx):raise RuntimeError('not enough live weights for matched null')
        positions=rng.choice(pool,len(idx),replace=False)
        w=base.copy();w[positions]+=rng.permutation(delta).astype(np.float32)
        proposed[name]=f32_to_bf16_bits(w.reshape(b.shape))
        details.append({'tensor':name,'candidate_entries':len(idx),'control_entries':int(np.sum(proposed[name]!=b)),
                        'candidate_delta_l2':float(np.linalg.norm(delta)),
                        'control_delta_l2':float(np.linalg.norm(bf16_bits_to_f32(proposed[name]).astype(np.float64)-bf16_bits_to_f32(b).astype(np.float64))),
                        'exclude_candidate_positions':pool is exclusive})
    rec=patch.create(GOLD,proposed,{'allowed_tensors':names,'max_abs_value':1e4,'max_changed_entries':10**7,
                        'forbid_uniform_scale':True},{'method':'parent-matched random live-position delta permutation',
                        'source_candidate':pid,'seed':seed,'author':'operator final controls'})
    return rec['patch_id'],details


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--worker',action='store_true');ap.add_argument('--root',required=True)
    ap.add_argument('--campaign',default='20261103T-phaseD-bootstrap-final');a=ap.parse_args();root=Path(a.root)
    if a.worker:return evaluate_worker(root,a.campaign)
    verify();candidates=sealed(root)
    superstate=json.loads((root/'supervisor.json').read_text())
    if superstate['status']!='terminal':raise RuntimeError('parents and development workers must be terminal first')
    if (root/'final-plan.json').exists():raise RuntimeError('final evaluation already planned; inspect live state before resuming')
    original={e['editor_id']:e for e in json.loads((TOPIC/'configs/phaseD_v2/editors.json').read_text())['editors']}
    editors=[original['E0']]+[original[e] for e in CONTROLS]
    matched={}
    for sid,pid in candidates:
        if pid!='FAILURE':
            editors.append({'editor_id':sid,'patch_id':pid,'gold_id':GOLD,'author_session':sid})
            control,details=matched_control(pid,2026110300+int(sid[-2:]))
            label='matched-'+sid
            editors.append({'editor_id':label,'patch_id':control,'gold_id':GOLD,'kind':'matched random editor control'})
            matched[sid]={'editor_id':label,'patch_id':control,'details':details}

    plan={'campaign':a.campaign,'sealed':dict(candidates),'editors':editors,'splits':['select','test','transfer'],
          'rule':'fixed candidates, no replacement or parent feedback; primary Holm family includes four parents',
          'timestamp':time.time(),'matched_controls':matched}
    (root/'final-plan.json').write_text(json.dumps(plan,indent=2))
    (root/'final-registry.json').write_text(json.dumps({'editors':editors},indent=2))
    destination=TOPIC/'work/raw'/a.campaign/'patch-exports'
    for e in editors:
        pid=e.get('patch_id')
        if pid:
            from .patch import lineage
            for member in lineage(pid):export(member,destination)
    devices=superstate['devices'];logs=root/'logs';handles=[];streams=[]
    queue=root/'final-queue/pending';queue.mkdir(parents=True,exist_ok=True)
    started=time.time()
    try:
        for device in devices:
            f=(logs/f'final-worker-{device}.log').open('x');streams.append(f)
            env=dict(os.environ,PYTHONPATH=str(TOPIC/'code'),CUDA_VISIBLE_DEVICES=device,TMPDIR=str(TOPIC/'work/tmp'),
                     HF_HOME=str(TOPIC/'work/cache/hf'),XDG_CACHE_HOME=str(TOPIC/'work/cache'),
                     VLLM_CACHE_ROOT=str(TOPIC/'work/cache/vllm-bench'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
            handles.append(subprocess.Popen([str(TOPIC/'work/envs/vllm/bin/python'),'-m','wse.bootstrap_final','--worker',
                 '--root',str(root),'--campaign',a.campaign],stdout=f,stderr=f,env=env,start_new_session=True,cwd=TOPIC))
        (root/'final-processes.json').write_text(json.dumps({'pids':[p.pid for p in handles],'started':started}))
        for stage, split in enumerate(plan['splits']):
            for i,e in enumerate(editors):
                jid=e['editor_id']+'__'+split
                job={'job_id':jid,'editor_id':e['editor_id'],'split':split,'tiers':TIERS,'ids':None,'submitted_at':time.time()}
                target=queue/f'{stage:02d}-{i:02d}-{jid}.json'
                temporary=queue/('.'+target.name)
                temporary.write_text(json.dumps(job));os.replace(temporary,target)
            deadline=time.time()+1800
            while True:
                if any(p.poll() is not None for p in handles):raise RuntimeError('worker exited before split completed')
                if list((root/'final-queue/failed').glob('*.json')):raise RuntimeError('final evaluation job failed')
                completed=len(list((root/'final-queue/done').glob('*.json')))
                if completed >= len(editors)*(stage+1):break
                if time.time()>deadline:raise RuntimeError('split evaluation deadline exceeded')
                time.sleep(5)
            (root/f'final-{split}-complete.json').write_text(json.dumps({'completed':time.time(),'jobs':len(editors)}))
            print(json.dumps({'split':split,'jobs_completed':len(editors)}),flush=True)
        (root/'final-queue/STOP').touch()
        rc=[p.wait(timeout=2400) for p in handles]
        if any(rc):raise RuntimeError(f'final worker failures: {rc}')
        complete={'returncodes':rc,'wall_s':time.time()-started,'jobs':len(editors)*3}
        (root/'final-complete.json').write_text(json.dumps(complete,indent=2));print(json.dumps(complete))
    finally:
        import signal
        for child in handles:
            try:os.killpg(child.pid,signal.SIGTERM)
            except ProcessLookupError:pass
        for f in streams:f.close()


if __name__=='__main__':main()
