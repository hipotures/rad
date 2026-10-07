"""Small predeclared CPU schedule study; no simulated TG and finite owned commands."""
from pathlib import Path
import os,subprocess,time,json,signal
C=Path(__file__).resolve().parents[1]
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def run(label,args):
 pth=C/'phase-b'/label;assert not pth.with_suffix('.json').exists();env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(STRATA_Q4_TAPE=str(C/'tapes/capture-32k-v1.bin'),STRATA_Q4_TAPE_MODE='replay')
 cmd=[str(C/'analysis/offline'),*args];start=time.monotonic();out=pth.with_suffix('.stdout');err=pth.with_suffix('.stderr')
 with out.open('x') as f,err.open('x') as e:
  p=subprocess.Popen(cmd,stdout=f,stderr=e,env=env,start_new_session=True);save(pth.with_suffix('.pid.json'),{'pid':p.pid,'command':cmd,'timeout_s':240,'environment':{k:v for k,v in env.items() if k.startswith('STRATA_')}});last=start
  try:
   while p.poll() is None:
    assert time.monotonic()-start<240,'finite simulation timeout'
    if time.monotonic()-last>15:print('OFFLINE_PROGRESS',label,round(time.monotonic()-start),flush=True);last=time.monotonic()
    time.sleep(.25)
  finally:
   if p.poll() is None:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10)
 result={'exit_code':p.returncode,'wall_s':time.monotonic()-start,'command':cmd,'stdout':str(out),'stderr':str(err)}
 if p.returncode==0:result['metrics']=json.loads(out.read_text())
 save(pth.with_suffix('.json'),result);print('OFFLINE_COMPLETE',label,result,flush=True);assert p.returncode==0,err.read_text()
for label,args in [('current-capacity-accounting',['current']),('capacity-only-optimistic',['capacity']),('full-deadline-modeled',['transfer','0','0']),('full-reuse-modeled',['transfer','0','1']),*[(f'horizon-{h}-modeled',['transfer',str(h),'0']) for h in [1,4,16,64]]]:run(label,args)
