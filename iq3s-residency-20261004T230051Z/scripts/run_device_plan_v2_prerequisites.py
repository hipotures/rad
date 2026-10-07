"""Finite repaired-candidate prerequisites with explicit owned cleanup and real checker."""
import subprocess,time
from lab import ROOT,load,save,owned_stop
variant='device-plan-ids-v2';experiment='E016-device-plan-ids';attempt='v2'
out=ROOT/'experiments'/experiment/attempt/'prerequisite-commands';py=str(ROOT/'src/control/.venv/bin/python')
if out.exists():raise RuntimeError('Existing prerequisites')
out.mkdir();records=[]
def call(name,cmd,timeout):
 start=time.time();path=out/f'{name}.log'
 try:
  with path.open('w') as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 except subprocess.TimeoutExpired:
  owned=ROOT/'variants'/variant/'owned-process.json'
  if owned.exists():p=load(owned);owned_stop(p['pid'],p['create_time'])
  raise
 records.append({'name':name,'command':cmd,'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(path)});save(out/'commands.json',records)
 print(name,r.returncode,path.read_text()[-1800:],flush=True)
 if r.returncode:raise SystemExit(r.returncode)
call('register',[py,'scripts/register_variant.py',variant,'--source',str(ROOT/'src'/variant),'--binary',str(ROOT/'builds'/variant/'strata'),'--overrides',str(out.parent/'overrides.json')],60)
call('native-Python-realIQ',[py,'scripts/test_variant.py',variant,'--experiment',experiment,'--attempt',attempt],900)
call('native-failure-audit',[py,'scripts/check_test_failures.py',experiment,'--attempt',attempt],60)
call('battery',[py,'scripts/correctness_battery.py','--variant',variant,'--experiment',experiment,'--attempt',attempt,'--reference',str(ROOT/'experiments/E006-frequency/correctness-r2/correctness/control')],600)
call('ground-truth',[py,'scripts/check_battery.py',str(out.parent/'correctness'/variant)],60)
