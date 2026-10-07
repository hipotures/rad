"""Explicit post-campaign reproducer; new artifacts and finite operation, original deadline/evidence untouched."""
from pathlib import Path
import argparse,hashlib,json,subprocess,datetime,time,shutil,os,signal,psutil
import runner
from verify_model import verify as verify_model
from tape import Tape
ORIGIN=Path(__file__).resolve().parents[1];R=ORIGIN.parents[1]
def load(p):return json.loads(Path(p).read_text())
def checked_config(profile):
 verify_model();cfg=runner.config(profile,'oracle-v3');assert hashlib.sha256(Path(cfg['exe']).read_bytes()).hexdigest()==cfg['binary_sha256'];assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['cwd'],text=True,timeout=10).strip()==cfg['source_sha'];assert not subprocess.check_output(['git','status','--porcelain'],cwd=cfg['cwd'],text=True,timeout=10).strip();return cfg
def main():
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['capture','validate','current','full','short']);a.add_argument('--profile',choices=['32k','128k','256k'],default='32k');a.add_argument('--tape');a.add_argument('--horizon',type=int,choices=[64],default=64);a.add_argument('--check',action='store_true');a.add_argument('--timeout-s',type=int,default=1200);a.add_argument('--worker',help=argparse.SUPPRESS);v=a.parse_args()
 if v.worker:
  root=Path(v.worker).resolve();assert root.parent==R/'campaigns' and root.name.startswith('q4-oracle-reproduce-');runner.C=root
  label='manual-'+v.mode+'-'+v.profile;mode='record' if v.mode=='capture' else 'replay';policy={'current':'off','full':'full','short':'short'}.get(v.mode,'off');tape=Path(v.tape).resolve() if v.tape else (root/'tapes'/f'{label}.bin' if mode=='record' else ORIGIN/'tapes'/f'capture-{v.profile}-v3.bin')
  try:
   runner.point(v.profile,mode,label,v.profile+'-run1','oracle-v3',str(tape),policy,'deadline',v.horizon)
   import fidelity,inspect_oracle,progression,system_metrics,cleanup
   for m in [fidelity,inspect_oracle,progression,system_metrics,cleanup]:m.C=root
   f=fidelity.audit(label,tape);assert f['state']=='PASS',f;f=inspect_oracle.audit(label,tape);assert f['state']=='PASS',f;progression.analyze(label,tape);system_metrics.analyze(label,tape);runner.status('COMPLETE',running=None,next_exact_action='Inspect this isolated reproduction; original campaign unchanged');print('REPRODUCTION_COMPLETE',root,flush=True)
  finally:
   import cleanup;cleanup.C=root
   if(root/'raw'/label).exists():cleanup.cleanup_attempt(root/'raw'/label)
  return
 cfg=checked_config(v.profile);tape=Path(v.tape).resolve() if v.tape else ORIGIN/'tapes'/f'capture-{v.profile}-v3.bin'
 print('EXPERIMENTAL_REPLAY_ONLY',json.dumps({'mode':v.mode,'profile':v.profile,'config':cfg,'reference_tape':str(tape),'normal_serving':False,'horizon_unit':'future main routed-layer invocation, full T-by10 batch'},indent=2),flush=True)
 if v.mode!='capture':
  manifest=Tape(tape).validate();assert manifest['state']=='PASS',manifest;print('TAPE_VALIDATED',json.dumps(manifest,indent=2),flush=True)
  if v.mode!='validate':assert Path(str(tape)+'.initial-state.bin').exists(),'Required initial-state sidecar'
 if v.check or v.mode=='validate':return
 assert load(ORIGIN/'STATUS.json')['state']=='COMPLETE','Original research still active: use its declared plans, never reset its deadline'
 assert 300<=v.timeout_s<=1800,'Bounded manual operation300..1800seconds'
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');root=R/'campaigns'/f'q4-oracle-reproduce-{stamp}';root.mkdir()
 for d in ['raw','logs','configs','inputs','git','tapes','analysis','phase-a']:(root/d).mkdir()
 shutil.copyfile(ORIGIN/'inputs/manifest.json',root/'inputs/manifest.json');shutil.copyfile(ORIGIN/'git/oracle-v3-identity.json',root/'git/oracle-v3-identity.json')
 for p in ['32k','128k','256k']:shutil.copyfile(ORIGIN/f'configs/control-{p}.json',root/f'configs/control-{p}.json')
 now=time.time();mono=time.monotonic();deadline={'start_epoch':now,'deadline_epoch':now+v.timeout_s,'experiment_cutoff_monotonic':mono+v.timeout_s,'deadline_utc':datetime.datetime.fromtimestamp(now+v.timeout_s,datetime.timezone.utc).isoformat(),'separate_user_operation':True,'original_campaign_deadline_unchanged':load(ORIGIN/'deadline.json')}
 (root/'deadline.json').write_text(json.dumps(deadline,indent=2)+'\n');(root/'STATUS.json').write_text(json.dumps({'state':'STARTING','origin':str(ORIGIN),'running':v.mode})+'\n');(root/'GOAL.md').write_text('# Explicit isolated manual reproduction\n\nMode '+v.mode+', profile '+v.profile+'. Source/tapes/provenance from '+str(ORIGIN)+'. Original campaign evidence and absolute deadline remain unchanged. No normal serving replacement.\n')
 cmd=[cfg['python'],str(Path(__file__).resolve()),v.mode,'--profile',v.profile,'--worker',str(root),'--horizon',str(v.horizon)]
 if v.tape:cmd+=['--tape',str(tape)]
 with (root/'logs/driver.log').open('x') as f:
  p=subprocess.Popen(cmd,cwd=ORIGIN,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);(root/'driver-process.json').write_text(json.dumps({'pid':p.pid,'create_time':psutil.Process(p.pid).create_time(),'command':cmd,'timeout_s':v.timeout_s})+'\n');start=time.monotonic();last=start
  try:
   while p.poll() is None:
    if time.monotonic()-start>v.timeout_s:raise TimeoutError('Manual reproduction finite timeout')
    if time.monotonic()-last>20:print('REPRODUCTION_PROGRESS',root,round(time.monotonic()-start),flush=True);last=time.monotonic()
    time.sleep(1)
  finally:
   if p.poll() is None:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=30)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=10)
   import cleanup;cleanup.C=root
   for path in (root/'raw').iterdir():cleanup.cleanup_attempt(path)
 print('REPRODUCTION_EXIT',p.returncode,root,flush=True);assert p.returncode==0,'Preserved reproduction failure; inspect logs'
if __name__=='__main__':main()
