"""Finite default-OFF falsification for the new output-row binary."""
import subprocess,time
from lab import ROOT,load,save,owned_stop
variant='direct-parts-off-v1';experiment='E025-direct-parts-off-guard'
base=ROOT/'experiments'/experiment/'v1';out=base/'commands'
assert not out.exists()
source=load(ROOT/'experiments/E023-direct-parts/summary.json')
assert any(c['role']=='candidate' and c['statistics']['TG']['median']>=1.05*
    next(r['statistics']['TG']['median'] for r in source['cells'] if r['role']=='reference' and r['profile']==c['profile'])
    for c in source['cells']), 'No5% apparent gain; do not run the optional guard'
assert load(ROOT/'experiments/E023-direct-parts/diagnostic-v2/summary.json')['state']=='PASS'
assert load(ROOT/'experiments/E023-direct-parts/v1/tests/failure-audit.json')['state']=='PASS_WITH_KNOWN_ENVIRONMENT_LIMITS'
out.mkdir();py=str(ROOT/'src/control/.venv/bin/python');records=[]
def call(name,cmd,timeout):
 path=out/f'{name}.log';start=time.time()
 try:
  with path.open('w') as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 except subprocess.TimeoutExpired:
  owned=ROOT/'variants'/variant/'owned-process.json'
  if owned.exists():p=load(owned);owned_stop(p['pid'],p['create_time'])
  save(out/f'{name}-timeout.json',{'command':cmd,'timeout_s':timeout});raise
 records.append({'name':name,'command':cmd,'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(path)})
 save(out/'commands.json',records);print(name,r.returncode,path.read_text()[-1700:],flush=True)
 if r.returncode:raise SystemExit(r.returncode)
call('register',[py,'scripts/register_variant.py',variant,'--source',str(ROOT/'src/direct-parts-v1'),
 '--binary',str(ROOT/'builds/direct-parts-v1/strata'),'--overrides',str(base/'overrides.json')],60)
call('battery',[py,'scripts/correctness_battery.py','--variant',variant,'--experiment',experiment,'--attempt','v1',
 '--reference',str(ROOT/'experiments/E006-frequency/correctness-r2/correctness/control')],600)
call('ground-truth',[py,'scripts/check_battery.py',str(base/'correctness'/variant)],60)
call('confirmation',[str(ROOT/'variants'/variant/'reproduce.sh'),'--experiment',experiment,'--attempt','v1'],1300)
call('analysis',[py,'scripts/compare_confirmation.py','--experiment',experiment,'--reference','E023-direct-parts'],180)
