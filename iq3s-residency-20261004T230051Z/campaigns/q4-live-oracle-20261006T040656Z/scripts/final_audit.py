"""Finite identity-aware cleanup and final evidence audit; no old campaign writes."""
from pathlib import Path
import json,hashlib,time,datetime,subprocess,psutil,py_compile
from cleanup import stop_record
from verify_model import verify
C=Path(__file__).resolve().parents[1];R=C.parents[1]
def read(p):return json.loads(Path(p).read_text())
def command(cmd,cwd=None):return subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=20)
def main():
 deadline=read(C/'deadline.json');assert time.monotonic()<deadline['deadline_monotonic']
 summary=read(C/'summary.json');assert summary['state']=='COMPLETE' and len(summary['rows'])==18 and all(x['valid'] for x in summary['rows'])
 assert all(x['attempts']==3 and x['valid']==3 for x in summary['cells'])
 for x in summary['rows']:
  assert read(C/'phase-a'/f"{x['label']}-fidelity.json")['state']=='PASS'
  assert read(C/'analysis'/f"{x['label']}-oracle.json")['state']=='PASS'
 assert read(C/'tests/launcher-checks/summary.json')['state']=='PASS'
 cleanup=[]
 for p in sorted((C/'raw').iterdir()):
  if not p.is_dir():continue
  for name,group in [('process.json',True),('raw/native-process.json',False),('collector-process.json',False)]:
   cleanup.append(stop_record(p/name,group))
 # Drivers/compilers were individually finite and have exited. Never stop PID-only matches.
 live=[]
 for proc in psutil.process_iter(['pid','cmdline','exe','status']):
  try:
   args=proc.info['cmdline'] or []
   own=str(C) in ' '.join(args) or (proc.info['exe'] or '').startswith(str(C/'builds'))
   if own and proc.pid!=__import__('os').getpid() and proc.info['status']!=psutil.STATUS_ZOMBIE:
    # This finite audit command's shells/timeout ancestors are not inference work.
    if (proc.info['exe'] or '').endswith('/strata') or any(x.endswith('serve_capture.py') or x.endswith('bounded_batch.py') or x.endswith('runner.py') for x in args):
     live.append({'pid':proc.pid,'executable':proc.info['exe'],'command':args})
  except (psutil.NoSuchProcess,psutil.AccessDenied):pass
 gpu=command(['nvidia-smi','--query-compute-apps=pid,process_name,used_gpu_memory','--format=csv,noheader'])
 assert gpu.returncode==0 and not gpu.stdout.strip(),'GPU compute occupied: '+gpu.stdout
 assert not live,live
 identities=[]
 for p in [R/'builds/control/strata',C/'builds/oracle-v3/strata']:
  digest=hashlib.sha256(p.read_bytes()).hexdigest();expect='eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d' if p==R/'builds/control/strata' else '30a31432b5aff51bcd4340900c13cad0c8487a832bfdb22d05f9157b88d5bdb3'
  assert digest==expect;identities.append({'path':str(p),'sha256':digest})
 for source,head in [(R/'src/control','6f32ec070f23ced9f50e704d854d775da52591ab'),(C/'src/oracle-v3','117bc89b3bacbf263379c336557e6c8aa07aff5e')]:
  sha=command(['git','rev-parse','HEAD'],source);status=command(['git','status','--porcelain'],source);assert sha.stdout.strip()==head and not status.stdout.strip()
 for p in (C/'scripts').glob('*.py'):py_compile.compile(str(p),doraise=True)
 model=verify();assert model['state']=='PASS'
 hw=command(['nvidia-smi','--query-gpu=index,name,utilization.gpu,memory.used,power.draw,temperature.gpu','--format=csv'])
 out={'state':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_monotonic_s':time.monotonic()-deadline['start_monotonic'],'deadline_utc':deadline['deadline_utc'],'primary_valid_requests':18,'max_attempts_per_unchanged_primary_point':3,'binary_identities':identities,'source_identity_and_clean_status':True,'model_size_mtime_smallhash_provenance':model['state'],'weights_modified':False,'owned_cleanup':cleanup,'remaining_owned_inference_training_profiling':live,'GPU_compute_apps':gpu.stdout,'GPU_status':hw.stdout,'previous_campaign_policy':'No writes to previous campaign paths; new isolated campaign plus laboratory index/status additions only','no_push_PR':True,'limitations':['No guard tail or secondary-device exact KV DMA counters','Manual wrapper --check plus actual core backend execution; no extra fourth main inference attempt','Four existing native-suite fixture/mlock failures retained','H64 post-request frontend EPIPE retained']}
 (C/'analysis/final-audit.json').write_text(json.dumps(out,indent=2)+'\n')
 print('FINAL_AUDIT_PASS',out['primary_valid_requests'],'GPUs free','elapsed',round(out['elapsed_monotonic_s']),flush=True)
if __name__=='__main__':main()
