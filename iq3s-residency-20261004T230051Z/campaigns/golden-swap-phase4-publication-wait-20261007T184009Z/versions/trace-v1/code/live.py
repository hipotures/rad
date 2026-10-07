"""Serial owned fresh-server replay, strict effective identities, full tape and finite timeouts."""
import argparse,copy,hashlib,os,signal,psutil,subprocess,time,threading
from common import *
import lab
from q4_multigpu import Q4Session
from tape import Tape
import inspect_oracle
clock=load(R/'clock.json');lab.deadline=lambda:__import__('datetime').datetime.fromisoformat(clock['deadline_utc']).timestamp()
def stop_owned(pid,created):
 try:
  p=psutil.Process(pid);assert abs(p.create_time()-created)<.1,'PID reused';children=p.children(recursive=True);p.terminate()
  try:p.wait(8)
  except psutil.TimeoutExpired:
   os.killpg(pid,signal.SIGTERM)
   try:p.wait(5)
   except psutil.TimeoutExpired:os.killpg(pid,signal.SIGKILL);p.wait(5)
  for child in children:
   try:
    if child.is_running() and child.status()!=psutil.STATUS_ZOMBIE:
     child.terminate()
     try:child.wait(3)
     except psutil.TimeoutExpired:child.kill();child.wait(3)
   except psutil.NoSuchProcess:pass
 except psutil.NoSuchProcess:pass
lab.owned_stop=stop_owned
# q4_multigpu imports its own owned_stop only for unrelated manual entrypoint; Session cleanup uses lab.
activity={'task':None,'arm':None,'phase':'idle'}
def alarm(*_):raise TimeoutError('Finite campaign/request timeout')
signal.signal(signal.SIGALRM,alarm)
signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt('Owned live runner interrupted')))
def identities():
 i=load(C/'configs/runtime-identity.json');assert hashlib.sha256((P0/'configs.json').read_bytes()).hexdigest()==i['base_configs_sha256'];assert hashlib.sha256(pathlib.Path(i['exe']).read_bytes()).hexdigest()==i['binary_sha256'];assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=i['source'],text=True).strip()==i['source_sha'];assert not subprocess.check_output(['git','status','--porcelain'],cwd=i['source'],text=True).strip()
 for p,v in load(P0/'provenance/model-identity.json')['files'].items():
  st=pathlib.Path(p).stat();assert (st.st_size,st.st_mtime_ns,st.st_ino)==(v['size'],v['mtime_ns'],v['inode'])
 return i

def fidelity(p,task):
 t=Tape(task['trace_path']);v=t.validate();assert v['state']=='PASS';r=load(p/'raw/run.json');o=np.fromfile(p/'raw/observations.bin',t.obs_dtype);errors=[];log=(p/'raw/run-engine.log').read_text();import re
 mat=re.search(r'Q4_TAPE_END mode=replay windows=(\d+) main_events=(\d+) mtp_events=(\d+) output=(\d+) work_hash=([0-9a-f]+)',log)
 if not mat or tuple(map(int,mat.groups()[:4]))!=(len(t.ws),48*len(t.ws),int(t.ws['draft_count'].sum()),int(t.h['output_count'])) or mat[5]!=v['native_FNV64']:errors.append('native completion/work conservation')
 expected=[]
 for w in t.ws:expected.extend(w['outputs'][:min(int(w['accepted'])+1,int(t.h['output_count'])-len(expected))].tolist())
 actual=load(r['actual_output_ids_path']);
 if actual!=expected:errors.append('actual emitted token IDs')
 if len(o)!=len(t.ws):errors.append('main/MTP window observation count')
 else:
  seen=np.ones((len(o),51),np.int32);seen[:,48:]=np.arange(3)[None,:]<t.ws['draft_count'][:,None]
  if not np.array_equal(o['seen'],seen) or not np.all(o['qsa_seen']==1):errors.append('main/MTP/QSA branch counts')
  if not np.isfinite(o['activation']).all():errors.append('nonfinite activations')
 side=pathlib.Path(task['trace_path']+'.initial-state.bin');observed=p/'raw/observations.bin.initial-state.bin'
 if not observed.exists() or side.read_bytes()!=observed.read_bytes():errors.append('initial numerical/meaningful state mismatch')
 if 'exact_initial_state=1' not in log:errors.append('initial native attestation absent')
 if r['verify_windows']!=len(t.ws) or r['mtp_proposed']!=v['MTP_proposed_to_verifier'] or r['mtp_accepted']!=v['MTP_accepted_to_commit'] or r['all_routed_entries']!=v['main_routed_entries']:errors.append('timing demand counters')
 if r['actual_output_tokens']!=int(t.h['output_count']) or r['actual_input_tokens']!=len(t.prompt) or r['reuse']!=0:errors.append('token/input/reuse')
 if task['task_id']=='text-websocket' and (len(actual)!=1773 or actual[-1] not in [248044,248046]):errors.append('actual EOS boundary')
 ref=np.fromfile(pathlib.Path(task.get('reference_observations',str(P0/'raw'/task['task_id']/'raw/observations.bin'))),t.obs_dtype);mask=o['seen']>0;diff=(o['activation'][mask]-ref['activation'][mask]).astype(np.float64);activation={'bitwise_equal':bool(np.array_equal(o['activation'][mask],ref['activation'][mask])),'relative_L2':float(np.linalg.norm(diff)/max(np.linalg.norm(ref['activation'][mask]),1e-12)),'max_abs_error':float(np.max(np.abs(diff)))}
 bad=np.argwhere(mask & np.any(o['activation']!=ref['activation'],axis=-1));activation['first_divergence']=None
 if len(bad):
  wi,role=map(int,bad[0]);component=int(np.flatnonzero(o['activation'][wi,role]!=ref['activation'][wi,role])[0]);activation['first_divergence']={'window':wi,'role':role,'component':component,'capture':float(ref['activation'][wi,role,component]),'replay':float(o['activation'][wi,role,component])}
 rr={'state':'PASS' if not errors else 'FAIL','errors':errors,'work_sha256':v['work_sha256'],'tape_sha256':v['tape_sha256'],'initial_state_sha256':hashlib.sha256(side.read_bytes()).hexdigest(),'emitted_tokens':len(actual),'state_committed_tokens':v['committed_in_state_prefix'],'windows':len(t.ws),'main_entries':v['main_routed_entries'],'mtp_entries':v['MTP_routed_entries'],'native_head_agreement':float(np.mean((o['native_outputs']==t.ws['outputs'])[np.arange(4)[None,:]<t.ws['T'][:,None]])),'selected_activation':activation,'information':'Incoming oracle/current-window safety privileged; forced token identity is work conservation, not natural-generation correctness'};save(p/'fidelity.json',rr);assert not errors,rr
 return rr
import numpy as np

def point(task,arm,label,step=3,wait_profile=1,frozen_phase2=False):
 no_gpu();i=identities();assert time.monotonic()-clock['start_monotonic']<11700, 'Reporting reserve';
 if frozen_phase2:
  i=load(INPUT_PARENT/'golden-swap-phase2-20261007T093357Z/configs/runtime-identity.json');assert hashlib.file_digest(pathlib.Path(i['exe']).open('rb'),'sha256').hexdigest()==i['binary_sha256']
 tape_path=pathlib.Path(task['trace_path']);expected_tape=task.get('tape_sha256',task.get('trace_hashes',{}).get(str(tape_path)));assert expected_tape,'Missing frozen tape identity';assert hashlib.file_digest(tape_path.open('rb'),'sha256').hexdigest()==expected_tape,'Tape identity mismatch';selection=load(C/'models/selection.json');model=C/'models'/(selection['policy']+'.txt');assert hashlib.sha256(model.read_bytes()).hexdigest()==selection['checkpoint_sha256'];cfg=copy.deepcopy(load(P0/'configs.json')[task['profile']]);cfg.update(exe=i['exe'],cwd=i['source'],source_sha=i['source_sha'],Strata_HEAD=i['source_sha'],binary_sha256=i['binary_sha256'],build_variant='phase4-publication-trace-v1',server_entrypoint=str(C/'code/serve_capture.py'),variant_overrides={'mode':arm,'policy':'Frozen causal victim' if arm in ['ORACLE_IN_LOGISTIC_TC','LOGISTIC_OFF'] else 'Causal history victim with minimum transaction control' if arm in ['CONTROL','TRACE','PLANNER_BASELINE','PLANNER_OPT','ORACLE_IN_HISTORY_TC'] else 'Existing full-future heuristic' if arm=='ORACLE_FULL' else 'Native current residency'},headline_instrumentation='ON: forced fixed-work replay, routing/native/oracle observations; contemporary same-binary comparison')
 p=W/'raw'/label;assert not p.exists(),'Preserve existing attempt; no replacement';cfg['env'].update(STRATA_Q4_TAPE=task['trace_path'],STRATA_Q4_TAPE_MODE='replay',STRATA_Q4_TAPE_REQUEST='2',STRATA_Q4_TAPE_OBSERVATIONS=str(p/'raw/observations.bin'),STRATA_Q4_ORACLE_SUBSTRATE='1',STRATA_Q4_ORACLE_MODE='off' if arm=='REPLAY_CURRENT' else 'full',STRATA_Q4_ORACLE_INCOMING='full',STRATA_Q4_ORACLE_VICTIM='full',STRATA_Q4_ORACLE_LOG=str(p/'raw/oracle'),STRATA_Q4_ORACLE_CHECK='1',STRATA_Q4_CAUSAL_VICTIM='native' if arm in ['CONTROL','TRACE','ORACLE_IN_HISTORY_TC','HISTORY_OFF','PLANNER_BASELINE','PLANNER_OPT'] else selection['policy'] if arm in ['ORACLE_IN_LOGISTIC_TC','LOGISTIC_OFF'] else 'off',STRATA_Q4_VICTIM_MODEL=str(model),STRATA_Q4_VICTIM_THRESHOLD=str(selection['threshold']),STRATA_Q4_TRANSACTION_CONTROL='1' if arm in ['CONTROL','TRACE','ORACLE_IN_HISTORY_TC','ORACLE_IN_LOGISTIC_TC','PLANNER_BASELINE','PLANNER_OPT'] else '0',STRATA_Q4_POST_USE_EVENTS=str(selection.get('post_use_events',0)),STRATA_Q4_PLANNER_OPT='1' if arm in ['CONTROL','TRACE','PLANNER_OPT'] else '0',STRATA_Q4_WAIT_PROFILE=str(wait_profile),STRATA_Q4_CACHE_TIMING='0',STRATA_Q4_DECISION_AUDIT='0',STRATA_Q4_PUBLICATION_TRACE='1' if arm=='TRACE' else '0')
 assert 'STRATA_VERIFY_PROFILE' not in cfg['env'] and 'STRATA_POOL_TRACE' not in cfg['env'];save(C/'configs'/(label+'.json'),cfg);print('EFFECTIVE_SETTINGS',__import__('json').dumps({'arm':arm,'task':task['task_id'],'profile':task['profile'],'actual_input_tokens':task['actual_input_tokens'],'settings':cfg,'binary_sha256':i['binary_sha256'],'checkpoint_sha256':selection['checkpoint_sha256']},sort_keys=True),flush=True);progress(step,task['task_id']+' '+arm+' START',task=task['task_id'],arm=arm,phase='startup',eta='unknown',model=selection['policy'] if arm in ['ORACLE_IN_LOGISTIC_TC','LOGISTIC_OFF'] else None,valid=None);ledger('Live attempt START',task=task['task_id'],arm=arm,label=label,binary=i['binary_sha256'],checkpoint=selection['checkpoint_sha256']);activity.update(task=task['task_id'],arm=arm,phase='startup');start=time.monotonic();s=Q4Session(C,cfg,p,task['profile'],port=18166);result={'task':task['task_id'],'arm':arm,'label':label,'valid':False};hbstop=threading.Event()
 def beat():
  while not hbstop.wait(25):progress(step,'HEARTBEAT '+task['task_id']+' '+arm,task=task['task_id'],arm=arm,phase=activity['phase'],owned_pid=s.proc.pid if s.proc else None,eta='unknown')
 thread=threading.Thread(target=beat,daemon=True);thread.start()
 try:
  signal.setitimer(signal.ITIMER_REAL,180);s.__enter__();s.budgeted=True;resource=load(p/'raw/resource-check.json');assert resource['split_K']==24 and resource['pool_spin_us']=='100';assert cfg['args'][cfg['args'].index('--pcie-frac')+1]=='.28';native=[q for q in psutil.Process(s.proc.pid).children(recursive=True) if pathlib.Path(q.exe()).resolve()==pathlib.Path(cfg['exe']).resolve()];assert len(native)==1;save(p/'raw/native-process.json',{'pid':native[0].pid,'created':native[0].create_time(),'executable':native[0].exe(),'command':native[0].cmdline(),'environment':{k:v for k,v in native[0].environ().items() if k.startswith('STRATA_') or k=='CUDA_VISIBLE_DEVICES'},'cpu_affinity':native[0].cpu_affinity()});activity['phase']='warmup';signal.setitimer(signal.ITIMER_REAL,max(1,180-(time.monotonic()-start)));warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID' and warm['actual_output_tokens']==64;signal.setitimer(signal.ITIMER_REAL,240);activity['phase']='prefill/decode';r=s.request(task['task_id'],'run','replay');signal.setitimer(signal.ITIMER_REAL,0);assert r['state']=='VALID' and r['actual_engine_input_verified'],r
  save(p/'results.json',{'warmup':warm,'runs':[r],'mode':'replay','arm':arm,'task':task['task_id'],'tape':task['trace_path']});proof=fidelity(p,task);audit=inspect_oracle.audit(str(p),task['trace_path']);assert audit['state']=='PASS',audit;result.update(valid=True,run=r,fidelity=proof,ownership=audit,startup_s=load(p/'raw/startup.json')['cold_start_s'],warmup_s=warm['wall_s'])
 except BaseException as e:result.update(error=repr(e));ledger('Live attempt invalid',label=label,error=repr(e));print('LIVE INVALID',label,repr(e),flush=True)
 finally:
  signal.setitimer(signal.ITIMER_REAL,0);activity['phase']='cleanup';before=time.monotonic();s.__exit__();result.update(cleanup_s=time.monotonic()-before,total_operating_s=time.monotonic()-start);hbstop.set();thread.join(3);no_gpu();save(p/'episode.json',result);ledger('Live attempt END',label=label,valid=result['valid'],operating_s=result['total_operating_s'],error=result.get('error'));progress(step,task['task_id']+' '+arm+' END',valid=result['valid'],phase='idle',owned_pid=None,operating_s=result['total_operating_s'])
 assert result['valid'],result.get('error');return result

def main():
 q=argparse.ArgumentParser();q.add_argument('--task',required=True);q.add_argument('--arm',required=True);q.add_argument('--label',required=True);a=q.parse_args();tasks={t['task_id']:t for t in load(P0/'benchmark-manifest.json')['tasks']};ind=C/'inputs/independent-task-manifest.json';tasks.update({load(ind)['task_id']:load(ind)} if ind.exists() else {});point(tasks[a.task],a.arm,a.label,3)
if __name__=='__main__':main()
