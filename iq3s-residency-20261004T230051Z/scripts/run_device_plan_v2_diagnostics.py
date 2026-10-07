"""Require strict repaired snapshots before bounded full-profile routing diagnostics."""
import shlex,subprocess,time
from lab import ROOT,load,save,owned_stop
experiment='E016-device-plan-ids';variant='diagnostic-device-plan-ids-v2';out=ROOT/'experiments'/experiment/'diagnostic-v2/commands';py=str(ROOT/'src/control/.venv/bin/python')
assert load(ROOT/f'experiments/{experiment}/compare-r2/summary.json')['state']=='PASS_REPAIR'
if out.exists():raise RuntimeError('Existing diagnosticattempt')
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
 print(name,r.returncode,path.read_text()[-2000:],flush=True)
 if r.returncode:raise SystemExit(r.returncode)
call('register',[py,'scripts/register_variant.py',variant,'--source',str(ROOT/'src'/variant),'--binary',str(ROOT/'builds'/variant/'strata'),'--diagnostic','--overrides',str(ROOT/f'experiments/{experiment}/v2/overrides.json')],60)
call('targeted-native',[str(ROOT/'src/control/.venv/bin/ctest'),'--test-dir',str(ROOT/'builds'/variant),'--output-on-failure','--timeout','60','-R','(cache|adapt|async|verify|split|expert_multi|native_expert_parity)','-j','1'],300)
command=[py,str(ROOT/'scripts/collect_traces.py'),'profiles','--variant',variant,'--experiment',experiment,'--attempt','diagnostic-v2']
launcher=ROOT/'variants'/variant/'diagnose-profiles.sh';launcher.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+' '.join(shlex.quote(c) for c in command)+' "$@"\n');launcher.chmod(0o755)
call('profiles',[str(launcher)],900)
call('analysis',[py,'scripts/analyze_device_plan_v2.py'],120)
