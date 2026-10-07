"""Final read-only preservation/provenance/process audit; run after cleanup."""
from campaign import C,R,V,load,save
from launch import verify
from pathlib import Path
import argparse,hashlib,os,psutil,subprocess,time,datetime
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  while chunk:=f.read(8*1024**2):h.update(chunk)
 return h.hexdigest()
def previous():
 rows=load(C/'git/previous-evidence-manifest.json');bad=[];t=time.time()
 for i,r in enumerate(rows):
  p=Path(r['path'])
  if not p.exists() or p.stat().st_size!=r['bytes'] or sha(p)!=r['sha256']:bad.append(r['path'])
  if i%500==0:print('PREVIOUS_HASH_PROGRESS',i,len(rows),round(time.time()-t,1),flush=True)
 expected={r['path'] for r in rows};excluded={'src','builds','.venv','__pycache__','.git'}
 actual={str(p) for p in V.rglob('*') if p.is_file() and not any(part in excluded for part in p.relative_to(V).parts)}
 extra=sorted(actual-expected);missing=sorted(expected-actual)
 out={'files':len(rows),'bytes':sum(r['bytes'] for r in rows),'mismatches':bad,'added_artifacts':extra,'missing_artifacts':missing,'presence_check_exclusions':sorted(excluded),'PASS':not bad and not extra and not missing,'wall_s':time.time()-t};save(C/'git/prior-v2-final-verification.json',out);assert out['PASS'],out;return out
def model():
 m=load(C/'git/model.json');rows=[];t=time.time()
 entries=[(r['path'],r['bytes'],r['previous_verified_sha256']) for r in m['shards']]+[(p,r['bytes'],r['sha256']) for p,r in m['files'].items()]
 for name,bytes_,expected in entries:
  print('MODEL_HASH_BEGIN',name,bytes_,flush=True);p=Path(name);assert p.stat().st_size==bytes_;got=sha(p);rows.append({'path':name,'bytes':bytes_,'sha256':got,'expected':expected,'PASS':got==expected});print('MODEL_HASH_END',name,got==expected,round(time.time()-t,1),flush=True)
 out={'revision':m['revision'],'quant':m['quant'],'full_file_hashes':rows,'PASS':all(r['PASS'] for r in rows),'wall_s':time.time()-t};save(C/'git/model-final-fullhash-verification.json',out);assert out['PASS'];return out
def final():
 s=load(C/'summary.json');rs=s['live']['records'];assert len(rs)==18 and s['live']['complete']
 for variant in ('control','conditional'):
  for profile in ('32k','128k','256k'):
   cell=[r for r in rs if r['variant']==variant and r['context']==profile];assert len(cell)==3 and all(r['state']=='VALID' and r['actual_output_tokens']==4096 and r['reuse']==0 for r in cell)
 for p in s['live']['trajectory']:assert p['identical_actual_engine_input'] and p['identical_input_ID_hash'] and p['warmup_same_actual_input']
 checked=[]
 for variant in ('control','conditional'):
  for profile in ('32k','128k','256k'):checked.append(verify(load(C/'launchers'/variant/f'{profile}.json')))
 files=sorted((C/'manual').glob('*/*/smoke.json'));assert len(files)==6 and all(load(p)['PASS'] for p in files),len(files)
 assert load(C/'tests/native-tests-summary.json')['expected_fixture_environment_failures_only'];assert len(load(C/'tests/scheduler/result.json')['PASS'])==10
 assert load(C/'phase-c/small-correctness.json')['PASS'] and load(C/'phase-c/cancellation.json')['PASS']
 assert sha(C/'checkpoints/conditional-logistic.json')==load(C/'phase-b/frozen-decision.json')['checkpoint_sha256']
 processes=[]
 for p in psutil.process_iter(['pid','create_time','cmdline','exe']):
  if p.pid==os.getpid():continue
  cmd=p.info['cmdline'] or [];exe=p.info['exe'] or ''
  # Avoid recording this audit's shell parent merely because its command
  # string names the campaign. Match executable/individual argv paths.
  owned=(exe.startswith(str(C/'builds')) or exe.startswith(str(C/'tests')) or any(a.startswith(str(C/'scripts')) and not a.endswith('/audit.py') for a in cmd))
  if owned:processes.append(p.info)
 # Also check recorded native/wrapper PIDs by creation time, including a
 # control engine whose executable lives outside this campaign.
 records=[]
 for record_path in list(C.rglob('native-process.json'))+list(C.rglob('process.json')):
  rec=load(record_path)
  if rec.get('pid')==os.getpid():continue
  try:
   proc=psutil.Process(rec['pid'])
   if abs(proc.create_time()-rec['create_time'])<.1 and proc.status()!=psutil.STATUS_ZOMBIE:records.append({'record':str(record_path),'pid':proc.pid,'command':proc.cmdline()})
  except (psutil.NoSuchProcess,KeyError):pass
 assert not records,records
 gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True).strip();assert not gpu,gpu;assert not processes,processes
 out={'PASS':True,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deadline_remaining_s':load(C/'deadline.json')['deadline_epoch']-time.time(),'headline_measured_requests':18,'paired_input_ID_checks':9,'launcher_smokes':len(files),'launcher_identity_checks':len(checked),'owned_processes':processes,'GPU_compute_apps':gpu,'recorded_processes_still_alive':records,'GPU_idle_snapshot':subprocess.check_output(['nvidia-smi','--query-gpu=index,name,utilization.gpu,memory.used','--format=csv,noheader'],text=True).strip(),'native_failures':'Four unchanged fixture/environment failures reported, not hidden','control_binary':checked[0]['binary_sha256'],'no_push_PR_or_model_writes':'Only local research/source commits; no push/PR/network model download performed; complete model hashes and prior-evidence checks separate.'};save(C/'analysis/final-audit.json',out);print('FINAL_AUDIT_PASS',out,flush=True)
def manifest():
 excluded={'src','builds','.plotvenv','.git','__pycache__'};rows=[]
 for p in sorted(C.rglob('*')):
  if not p.is_file() or any(part in excluded for part in p.relative_to(C).parts) or p.name in {'artifact-manifest.json','audit-manifest-pid.json','audit-manifest.log'}:continue
  rows.append({'path':str(p.relative_to(C)),'bytes':p.stat().st_size,'sha256':sha(p)})
 save(C/'artifact-manifest.json',{'files':rows,'excluded':['Source/buildtrees separately identified by Git/source/binary hashes; plotting venv dependencies recorded','Manifest itself and its own audit-manifest PID/output log (self-reference); no request/trace excluded'],'warning':'Generate after servers/collectors/analysis output finalized; no measurement deletion.'});print('ARTIFACT_MANIFEST',len(rows),sum(x['bytes'] for x in rows),flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('action',choices=['previous','model','final','manifest']);args=a.parse_args();save(C/'logs'/f'audit-{args.action}-pid.json',{'pid':os.getpid(),'create_time':psutil.Process().create_time(),'timeout_s':600,'action':args.action});globals()[args.action]()
