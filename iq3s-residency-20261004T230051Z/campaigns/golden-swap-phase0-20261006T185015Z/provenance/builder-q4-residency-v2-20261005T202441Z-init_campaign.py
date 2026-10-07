"""Preserve starting evidence and create Q4-only frozen inputs/configs."""
from pathlib import Path
import copy, hashlib, json, shutil, subprocess, sys, datetime
C=Path(__file__).resolve().parents[1]
R=C.parents[1]
P=R/'campaigns/q4-pool-spin-20261005T184831Z'
M=R/'campaigns/q4-multigpu-20261005T164628Z'
BASE='6f32ec070f23ced9f50e704d854d775da52591ab'
SHA='eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d'
def load(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2)+'\n')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(R/'builds/control/strata')==SHA
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R/'src/control',text=True).strip()==BASE
assert not subprocess.check_output(['git','status','--porcelain'],cwd=R/'src/control',text=True).strip()
evidence=[]
files=[P/'report.md',P/'summary.json',P/'summary.csv',P/'protocol.json',P/'git/model.json',P/'git/environment.json',M/'report.md',M/'summary.json',M/'protocol.json']
for eid in ['E004-replay','E005-expert-jev','E015-lowrank-router','E017-gpu-router','E018-router-transactions','E020-wide-gate-lookahead','E028-persistent-replay','E029-persistent-runtime']:
 files.append(R/'experiments'/eid/'report.md')
files.extend([R/'experiments.jsonl',R/'sources.json',R/'campaigns/pool-persistent-20261005T094800Z/previous-root/report.md'])
files.extend((R/'references/hardware').glob('*'))
for p in files:
 if not p.is_file():continue
 target=C/'git/starting-evidence'/p.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 evidence.append({'source':str(p),'copy':str(target.relative_to(C)),'sha256':digest(p)})
save(C/'git/starting-evidence.json',evidence)
for name in ['lab.py','q4_multigpu.py','serve_capture.py','record_ui_metrics.py']:
 shutil.copy2(P/'scripts'/name,C/'scripts'/name)
# All copied code remains unmodified except the new campaign wrappers.
shutil.copy2(P/'git/model.json',C/'git/model.json')
model=load(C/'git/model.json')
for s in model['shards']:
 st=Path(s['path']).stat();assert st.st_size==s['bytes'] and st.st_mtime_ns==s['mtime_ns']
for p,v in model['files'].items():assert digest(p)==v['sha256']
manifest=load(P/'inputs/manifest.json')
other=load(M/'inputs/manifest.json')
manifest['profiles']['256k']=other['profiles']['256k']
for name,info in other['payloads'].items():
 if name.startswith('256k'):manifest['payloads'][name]=info
for name,info in manifest['payloads'].items():
 dest=C/'inputs'/Path(info['path']).name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(info['path'],dest);info['path']=str(dest)
 dest=C/'inputs/token-ids'/Path(info['token_ids_path']).name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(info['token_ids_path'],dest);info['token_ids_path']=str(dest)
save(C/'inputs/manifest.json',manifest)
for profile,limit in [('32k',32768),('128k',131072),('256k',262144)]:
 cfg=load(P/'launchers/128k.json');cfg.update(max_total_context=limit,port=18136,host='127.0.0.1',model_manifest=str(C/'git/model.json'),server_entrypoint=str(C/'scripts/serve_capture.py'),build_variant='q4-v2-original-control')
 cfg['args'][cfg['args'].index('--max-context')+1]=str(limit)
 cfg['log']=str(C/'logs/unlaunched-engine.log')
 save(C/'configs'/f'control-{profile}.json',cfg)
 ident=load(R/'experiments/E003-diagnostics/v5/build/identity.json')
 dc=copy.deepcopy(cfg);dc.update(exe=str(Path(ident['build'])/'strata'),cwd=ident['source'],source_sha=ident['source_sha'],Strata_HEAD=ident['source_sha'],binary_sha256=ident['binary_sha256'],build_variant='q4-v2-buffered-diagnostic',headline_instrumentation='ON: diagnostic only')
 dc['env']['STRATA_LAB_TRACE']='REPLACED_PER_ATTEMPT'
 save(C/'configs'/f'diagnostic-{profile}.json',dc)
save(C/'protocol.json',{'baseline':'CURRENT Q4 K24/.28 100us workers15 spec4/.5 INT8 prefill auto suffix/cache0','fresh_start':'Fresh server for every final measured request; identical4096-input/64-output warmup','primary_output':4096,'max_attempts_per_unchanged_point':3,'contexts':[32768,131072,262144],'materiality_percent':3,'controls':'Reuse latest pool controls at32/128 where compatible; collect only missing256 profile and candidate paired controls if chronology/protocol requires','phases':['E030 Q4 ground truth and replay','E031 Q4 causal and Expert-Jev policy competition','E032 Q4 live candidates/correctness/confirmation'],'no_extra_gpu_memory':True,'auxiliary_live_predictors_CPU_only':True})
record={'id':'E030-q4-ground-truth','state':'RUNNING','campaign':str(C.relative_to(R)),'question':'Q4-specific trace accounting, byte/capacity budgets, cost/readiness and achievable headroom','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
for p in [C/'ledger.jsonl',R/'experiments.jsonl']:
 with p.open('a') as f:f.write(json.dumps(record)+'\n')
save(C/'git/frozen-identity.json',{'binary':str(R/'builds/control/strata'),'sha256':SHA,'source':BASE,'model':model['revision'],'model_manifest':str(C/'git/model.json'),'front_end_sha256':digest(C/'scripts/serve_capture.py')})
print('INITIALIZED',C,flush=True)
