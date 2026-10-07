"""Finite same-binary OFF guard; no extra ON repetitions or new build."""
import subprocess,time
from lab import ROOT,load,save,owned_stop
variant='host-plan-off-v1';experiment='E022-host-plan-off-guard';out=ROOT/'experiments'/experiment/'v1/commands'
assert load(ROOT/'experiments/E019-skip-local-host-plan/diagnostic-v1/summary.json')['state']=='PASS'
assert load(ROOT/'experiments/E019-skip-local-host-plan/v1/tests/failure-audit.json')['state']=='PASS_WITH_KNOWN_ENVIRONMENT_LIMITS'
if out.exists():raise RuntimeError('Existing guard; retain it')
out.mkdir(parents=True)
py=str(ROOT/'src/control/.venv/bin/python');records=[]
def call(name,cmd,timeout):
 path=out/f'{name}.log';start=time.time()
 try:
  with path.open('w') as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 except subprocess.TimeoutExpired:
  owned=ROOT/'variants'/variant/'owned-process.json'
  if owned.exists():p=load(owned);owned_stop(p['pid'],p['create_time'])
  save(out/f'{name}-timeout.json',{'command':cmd,'timeout_s':timeout});raise
 records.append({'name':name,'command':cmd,'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(path)})
 save(out/'commands.json',records);print(name,r.returncode,path.read_text()[-1800:],flush=True)
 if r.returncode:raise SystemExit(r.returncode)
call('register',[py,'scripts/register_variant.py',variant,'--source',str(ROOT/'src/skip-local-host-plan-v1'),
 '--binary',str(ROOT/'builds/skip-local-host-plan-v1/strata'),'--overrides',str(out.parent/'overrides.json')],60)
call('battery',[py,'scripts/correctness_battery.py','--variant',variant,'--experiment',experiment,'--attempt','v1',
 '--reference',str(ROOT/'experiments/E006-frequency/correctness-r2/correctness/control')],600)
call('ground-truth',[py,'scripts/check_battery.py',str(out.parent/'correctness'/variant)],60)
# No build/training/heavy analysis is started in this clean phase.
call('confirmation',[str(ROOT/'variants'/variant/'reproduce.sh'),'--experiment',experiment,'--attempt','v1'],1400)
call('analysis',[py,'scripts/compare_confirmation.py','--experiment',experiment,'--reference','E019-skip-local-host-plan'],180)
