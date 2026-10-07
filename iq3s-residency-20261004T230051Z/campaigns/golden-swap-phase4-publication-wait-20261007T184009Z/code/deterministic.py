"""One tape, fixed modeled completion schedule: detail OFF/ON decision/work parity."""
from common import *
import numpy as np,hashlib,os
from inspect_oracle import E
no_gpu();task=next(t for t in load(P0/'benchmark-manifest.json')['tasks'] if t['task_id']=='math-rational')
cmd=['g++','-O3','-std=c++20','-pthread','-I'+str(SOURCE/'include'),'-I/usr/local/cuda/include',str(C/'code/offline.cpp'),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(W/'builds/offline')]
with Heartbeat('deterministic compile',2),(W/'logs/compile-offline.log').open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
rows=[];logical=[]
for detail in [0,1]:
 prefix=W/'raw'/f'deterministic-detail{detail}';env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(STRATA_Q4_TAPE=task['trace_path'],STRATA_Q4_TAPE_MODE='replay',STRATA_Q4_CAUSAL_VICTIM='native',STRATA_Q4_VICTIM_THRESHOLD='0.5',STRATA_Q4_TRANSACTION_CONTROL='1',STRATA_Q4_POST_USE_EVENTS='0',STRATA_Q4_PLANNER_OPT='1',STRATA_Q4_DECISION_AUDIT='1',STRATA_Q4_PUBLICATION_TRACE=str(detail),STRATA_Q4_SIM_LOG=str(prefix))
 with Heartbeat('deterministic detail '+str(detail),2):result=subprocess.run([str(W/'builds/offline'),'transfer','0','0'],env=env,capture_output=True,text=True,timeout=180)
 (W/'logs'/f'deterministic-detail{detail}.log').write_text(result.stdout+result.stderr);assert result.returncode==0
 values=[json.loads(s) for s in result.stdout.splitlines() if s.startswith('{')];a=np.fromfile(str(prefix)+'-admissions.bin',E);a['issue_ns']=0;logical.append(hashlib.sha256(a.tobytes()).hexdigest());rows.append({'detail':detail,'accounting':values[0],'decisions':values[1],'logical_admissions_sha256':logical[-1],'lifecycle_sha256':hashlib.file_digest(pathlib.Path(str(prefix)+'-lifecycle.bin').open('rb'),'sha256').hexdigest()})
ignore={'scorer_feature_ms','scorer_model_ms','scorer_selection_ms','cache_hits'}
assert {k:v for k,v in rows[0]['accounting'].items() if k not in ignore}=={k:v for k,v in rows[1]['accounting'].items() if k not in ignore}
for k in ['candidate_hash','candidate_records']:assert rows[0]['decisions'][k]==rows[1]['decisions'][k]
assert logical[0]==logical[1] and rows[0]['lifecycle_sha256']==rows[1]['lifecycle_sha256']
save(C/'checks/deterministic-parity.json',{'state':'PASS','rows':rows,'scope':'Same current source/detail switch, one development tape and fixed modeled completion schedule. This proves no deterministic decision change; it does not assert equal live asynchronous arrivals or trace neutrality.'})
