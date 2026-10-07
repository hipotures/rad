"""Foreground unchanged Q4 control. Experimental oracle is never selected here."""
from pathlib import Path
import argparse,hashlib,json,subprocess,time,signal,psutil
from q4_multigpu import Q4Session
from lab import owned_stop
import lab
from verify_model import verify as verify_model
C=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text())
def verify(profile):
 verify_model()
 cfg=load(C/'configs'/f'control-{profile}.json');assert cfg['source_sha']=='6f32ec070f23ced9f50e704d854d775da52591ab';assert cfg['binary_sha256']=='eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d'
 assert hashlib.sha256(Path(cfg['exe']).read_bytes()).hexdigest()==cfg['binary_sha256'];assert cfg['model_revision']=='38bb39ee97821de2c9009abb7e93950eec396e66';assert cfg['layer_split']=='24'
 for k in ['--pack','--native','--ple-gguf','--mtp','--expert-profile']:
  assert Path(cfg['args'][cfg['args'].index(k)+1]).exists(),k
 assert not any('ORACLE' in k or 'TAPE' in k for k in cfg['env']);assert cfg['env']['STRATA_POOL_SPIN_US']=='100'
 print('VERIFIED_UNCHANGED_CONTROL',json.dumps(cfg,indent=2),flush=True);return cfg
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['start','stop']);a.add_argument('--profile',choices=['32k','128k','256k'],default='32k');a.add_argument('--host',default='0.0.0.0');a.add_argument('--port',type=int,default=8080);a.add_argument('--timeout-s',type=int,default=43200);a.add_argument('--check',action='store_true');v=a.parse_args()
 owned=C/'launchers/control/owned-process.json'
 if v.mode=='stop':
  if owned.exists():
   r=load(owned);assert str(C/'manual') in r['attempt'];owned_stop(r['pid'],r['create_time'])
 else:
  cfg=verify(v.profile)
  if v.check:raise SystemExit(0)
  # A manually launched future serving session has its own finite lifetime, never resets the completed research deadline.
  manual_deadline=time.time()+v.timeout_s;lab.deadline=lambda:manual_deadline
  path=C/'manual'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt('Owned stop')))
  with Q4Session(C,cfg,path,v.profile,v.port,v.host,console=True) as s:
   owned.write_text((C/'owned-process.json').read_text());print('NORMAL_CONTROL_READY',s.url,'bind',v.host,flush=True)
   try:s.proc.wait(timeout=v.timeout_s)
   except subprocess.TimeoutExpired:print('NORMAL_CONTROL_FINITE_TIMEOUT',v.timeout_s,flush=True)
