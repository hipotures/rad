"""Final artifact/provenance/fairness audit. No inference or source modification."""
import argparse,datetime,hashlib,json,pathlib,subprocess
import psutil
from lab import ROOT,load,save
from q4_multigpu import status
a=argparse.ArgumentParser();a.add_argument('--campaign',type=pathlib.Path,required=True);v=a.parse_args();C=v.campaign
s=load(C/'summary.json');assert s['state']=='COMPLETE_27_VALID' and len(s['runs'])==27
env=s['provenance'];assert hashlib.sha256(pathlib.Path(env['binary_realpath']).read_bytes()).hexdigest()==env['binary_sha256']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT/'src/control',text=True).strip()==env['source_sha']
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT/'src/control',text=True).strip()
for p,h in load(C/'git/protected-files.json').items():assert hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==h,('Protected file changed',p)
for shard in s['model']['shards']:
 st=pathlib.Path(shard['path']).stat();assert st.st_size==shard['bytes'] and st.st_mtime_ns==shard['mtime_ns']
for p,info in s['model']['files'].items():assert hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==info['sha256'],('Model/pack/profile/MTP changed',p)
checks=[]
for cell in s['cells']:
 assert cell['n']==3
 for raw in cell['raw_paths']:
  r=load(raw);assert r['state']=='VALID';assert r['actual_output_tokens']==4096 and r['reuse']==0 and r['actual_engine_input_verified']
  assert r['source_sha']==env['source_sha'] and r['binary_sha256']==env['binary_sha256'];cfg=r['full_config'];assert cfg['exe']==env['binary_realpath'] and cfg['Strata_version']=='0.1.39'
  assert cfg['env']=={'CUDA_VISIBLE_DEVICES':'0,1','STRATA_POOL_SPIN_US':'100','STRATA_SPLIT_TIMING':'1','STRATA_DECODE_TIMING':'1'}
  assert r['mtp_proposed']>0 and r['mtp_accepted']>0
  args=r['full_engine_commands'][0];assert ('--remote-expert-opt' in args)==(cell['method']=='optimized-helper');assert ('--layer-split' in args)==(cell['method']=='layer-split')
  assert ('--expert-cache-device1' in args)==(cell['method']!='layer-split')
  ids=load(r['actual_output_ids_path']);assert len(ids)==4096
  p=pathlib.Path(raw).with_name(pathlib.Path(raw).stem+'-request.json');expected=load(C/'inputs/manifest.json')['payloads'][r['profile']+'-'+p.stem.split('-')[0]]
  assert hashlib.sha256(json.dumps(load(expected['token_ids_path']),separators=(',',':')).encode()).hexdigest()==r['actual_engine_input']['sha256']
  checks.append({'raw':raw,'state':'PASS','input_count':r['actual_input_tokens'],'output':4096,'source':r['source_sha'],'binary':r['binary_sha256']})
# Check launchers without starting a tenth benchmark server or repeating a valid point.
for profile in ['32k','128k','256k']:
 cmd=[str(C/'launchers'/f'start-{profile}.sh'),'--host','0.0.0.0','--port','8080','--check'];r=subprocess.run(cmd,capture_output=True,text=True);(C/'logs'/f'launcher-check-{profile}.log').write_text(r.stdout+r.stderr);assert r.returncode==0,(cmd,r.stderr)
gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv'],text=True);gpu_idle=not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
remaining=[]
for p in psutil.process_iter(['pid','exe','cmdline']):
 try:
  if p.info['exe'] and pathlib.Path(p.info['exe']).resolve()==pathlib.Path(env['binary_realpath']).resolve():remaining.append(p.info)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
assert gpu_idle and not remaining,(gpu,remaining)
collector=C/'telemetry/temperature-monitor-finished.json';assert collector.exists(),'Temperature collector still running'
finished=load(collector);cpu=[x['collector_CPU_one_core100'] for x in finished['CPU_samples']];collector_mean=sum(cpu)/len(cpu) if cpu else None
save(C/'analysis/audit.json',{'state':'PASS','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requests':checks,'protected_launchers_unchanged':True,'source_unchanged':True,'model_provenance_unchanged':True,'GPUs_idle':gpu_idle,'GPU_processes':gpu,'remaining_engines':remaining,'temperature_collector_exited':True,'temperature_collector_CPU_mean_one_core100':collector_mean,'missing_metrics':'GPU1temperature absent before added1HzNVML collector; preserved as unavailable, no run repetition','no_push_or_PR':True})
inventory={}
for p in sorted(C.rglob('*')):
 if p.is_file() and p.name not in ['artifact-sha256.json','STATUS.md','STATUS.json'] and '__pycache__' not in p.parts:inventory[str(p.relative_to(C))]=hashlib.sha256(p.read_bytes()).hexdigest()
save(C/'git/artifact-sha256.json',inventory)
status(C,'COMPLETE',running=None,pending=[],completed=['binary/source/model verified','bounded layer check','27valid measured4096requests','9fixed64-output warmups','sameID and helper-capacity fairness','report/CSV/JSON','frozen safe launchers checked','artifact hashes','owned processes stopped and bothGPUsidle'],next_exact_action='user review and real-prompt testing; no automatic residency experiment',audit=str(C/'analysis/audit.json'))
print('AUDIT PASS',len(checks),'requests',len(inventory),'artifact hashes','GPU_IDLE',gpu_idle)
