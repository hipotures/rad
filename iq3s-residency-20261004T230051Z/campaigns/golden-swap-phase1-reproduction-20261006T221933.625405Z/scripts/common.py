import pathlib,json,time,datetime,os,threading,subprocess
C=pathlib.Path(__file__).resolve().parents[1]
P0=C.parents[1]/'campaigns/golden-swap-phase0-20261006T185015Z'
DEC=C.parents[1]/'campaigns/q4-oracle-decomposition-20261006T100032Z'
def load(p):return json.loads(pathlib.Path(p).read_text())
def save(p,x):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp.'+str(os.getpid())+'.'+str(threading.get_ident())+'.'+str(time.monotonic_ns()));tmp.write_text(json.dumps(x,indent=2)+'\n');os.replace(tmp,p)
def progress(step,message,**kw):
 clock=load(C/'clock.json');elapsed=time.monotonic()-clock['start_monotonic'];s=load(C/'progress.json')
 if s.get('step')!=step:
  for key in ['task','arm','model','horizon','fit_s','rows','completed_task','sampled_selected_return_le4','uniform_return_le4','nonlocal_entries','copy_GB','evaluation_wall_s','owned_cpu_pid','owned_pid','phase','valid']:s.pop(key,None)
 s.update(step=step,message=message,next_action=kw.pop('next_action',{1:'validate causal dataset',2:'compare frozen candidates and select on calibration',3:'validate same-runtime replay and safety',4:'complete next frozen adjacent three-mode block',5:'regenerate reports, audit and cleanup'}[step]),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=elapsed,budget_seconds=(datetime.datetime.fromisoformat(clock['deadline_utc'])-datetime.datetime.fromisoformat(clock['start_utc'])).total_seconds(),remaining_seconds=max(0,(datetime.datetime.fromisoformat(clock['deadline_utc'])-datetime.datetime.fromisoformat(clock['start_utc'])).total_seconds()-elapsed),**kw);save(C/'progress.json',s)
 with (C/'progress.jsonl').open('a') as f:f.write(json.dumps(s)+'\n')
 (C/'STATUS.md').write_text('# Golden Swap Phase 1\n\n'+message+'\n\n```json\n'+json.dumps(s,indent=2)+'\n```\n')
 print(f'[PHASE 1 | STEP {step}/5] {message} | elapsed {elapsed/60:.1f}min | remaining {s['remaining_seconds']/60:.1f}min',flush=True)
def ledger(message,**kw):
 x={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'message':message,**kw}
 with (C/'attempt-ledger.jsonl').open('a') as f:f.write(json.dumps(x)+'\n')
 with (C/'DECISIONS.md').open('a') as f:f.write('\n- '+x['utc']+': '+message+' '+json.dumps(kw)+'\n')
class Heartbeat:
 def __init__(self,label,step):self.label=label;self.step=step;self.stop=threading.Event()
 def __enter__(self):
  def worker():
   while not self.stop.wait(25):progress(self.step,'HEARTBEAT '+self.label,status='RUNNING',eta='unknown')
  self.thread=threading.Thread(target=worker,daemon=True);self.thread.start();return self
 def __exit__(self,*_):self.stop.set();self.thread.join(2)
def no_gpu():assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,timeout=8).strip(),'CPU work cannot overlap GPU measurements'
if __name__=='__main__':print(json.dumps(load(C/'progress.json'),indent=2))
