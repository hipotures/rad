"""Inventory external artifacts after timing; preserve recovery gaps and compact evidence."""
import hashlib,os,json,datetime,subprocess,shutil
from common import *
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
if __name__=='__main__':
 no_gpu();raw=[];roots=[W/'raw',W/'logs'];repro=[load(x) for x in (C/'tests').glob('reproduction-*.json')]
 roots.extend(pathlib.Path(x['directory']) for x in repro)
 with Heartbeat('external artifact identity inventory',5):
  for root_id,root in enumerate(roots):
   for p in sorted(root.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts or p.name.startswith('storage-manifest-'):continue
    raw.append({'root':root_id,'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':digest(p)})
 save(C/'results/external-artifact-inventory.json',{'roots':list(map(str,roots)),'files':{str(i):x for i,x in enumerate(raw)},'recovery':'Exact observations are irreplaceable; frozen experiment can be rerun but timing bytes differ. Persistent local disk only; independent backup unknown.'})
 inputs=[]
 for task in load(P0/'benchmark-manifest.json')['tasks']:
  p=pathlib.Path(task['trace_path']);side=pathlib.Path(str(p)+'.initial-state.bin');inputs.append({'id':task['task_id'],'role':task['split'],'prior_exposure':'Previously evaluated fixed regression' if task['split']=='reserved_evaluation' else task['split'],'source_manifest':str(P0/'benchmark-manifest.json'),'tape':str(p),'bytes':p.stat().st_size,'sha256':task['trace_hashes'][str(p)],'initial_state_path':str(side),'initial_state_bytes':side.stat().st_size,'initial_state_sha256':digest(side),'actual_input_tokens':task['actual_input_tokens'],'recovery':'Irreplaceable original natural capture retained locally in Phase0; prompt/source/settings recoverable, exact future natural tape not guaranteed','independent_backup':None})
 independent=load(C/'inputs/independent-task-manifest.json');p=pathlib.Path(independent['trace_path']);inputs.append({'id':independent['task_id'],'role':'independent validation, no retuning','task_manifest':'inputs/independent-task-manifest.json','tape':str(p),'bytes':p.stat().st_size,'sha256':independent['tape_sha256'],'main_output':independent['main_output_tokens'],'observed_tail':independent['observed_tail_tokens'],'recovery':'Irreplaceable exact capture; public source and deterministic prompt/template/tokenization are regenerable, natural continuation may vary','independent_backup':None})
 save(C/'input-manifest.json',{'inputs':inputs,'ordinary_backing_revision':'38bb39ee97821de2c9009abb7e93950eec396e66','backing_identity_manifest':str(P0/'provenance/model-identity.json'),'public_source':{'url':independent['source_url'],'title':'RFC8259 JSON Data Interchange Format','date':'December2017','local_original':independent['source_path'],'bytes':pathlib.Path(independent['source_path']).stat().st_size,'sha256':independent['source_sha256'],'recovery':'Downloadable licensed original; deterministic excerpt retained in fixtures/rfc8259-excerpt.txt'},'prompt_and_tokenization':{'manifest':'inputs/manifest.json','recovery':'Existing Phase0 prompts/IDs remain immutable references. Independent prompt serialization and IDs regenerate with code/prepare_independent.py and pinned tokenizer/model. Execution payloads/IDs excluded by archive role policy; their identities and code are preserved.'}})
 episodes=[]
 for p in sorted(list((C/'raw').iterdir())+[pathlib.Path(x['directory'])/'raw'/('replay-'+x['task']+'-'+x['arm']) for x in repro]):
  if not (p/'episode.json').exists():continue
  target=C/'results/requests'/p.name;target.mkdir(parents=True,exist_ok=True)
  for name in ['episode.json','fidelity.json','results.json']:
   if (p/name).exists():shutil.copyfile(p/name,target/name)
  episodes.append({'label':p.name,'raw_path':str(p),'compact_path':str(target.relative_to(C)),'scope':'Compact request/run/fidelity facts only; full engine logs, telemetry and journals remain external'})
 identity=load(C/'configs/runtime-identity.json');deps=load(C/'configs/dependencies.json');manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'work_root':str(W),'ordinary_backing':'Full immutable expert host RAM, pinned model manifest. No SSD/helper/new capacity experiment.','runtime':dict(identity,recovery='Obtain pinned upstream base and apply patches/cumulative-from-original.diff; explicit build commands in configs/dependencies.json. Local-only derivative SHA is not the sole source backup.'),'dependencies':deps,'raw_inventory':'results/external-artifact-inventory.json','raw_files':len(raw),'raw_bytes':sum(x['bytes'] for x in raw),'compact_requests':episodes,'input_manifest':'input-manifest.json','frozen_checkpoint':{'path':'models/logistic.txt','bytes':(C/'models/logistic.txt').stat().st_size,'sha256':digest(C/'models/logistic.txt'),'recovery':'Small checkpoint/export stored in Git; no retraining required'},'recovery_limit':'No independent persistent backup destination identified for exact large tapes/raw observations. They remain on persistent local disk; local-host/storage loss would prevent exact byte-for-byte raw recovery. Compact outcomes and authored source/patches are retained in Git and published to the canonical GitHub repository; the original results commit is 22be02507a86db78b254630414ee4530fb47beb3. The restriction on push and PR was removed by the operator. No private-data upload.'}
 save(C/'artifact-manifest.json',manifest);print('STORAGE_MANIFEST',len(raw),manifest['raw_bytes'],flush=True)
