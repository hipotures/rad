"""Complete the bounded native/full-router diagnostic, with owned timeout cleanup."""
import shlex, subprocess, time
from lab import ROOT,load,owned_stop,save
variant='diagnostic-gpu-router-v2'
out=ROOT/'experiments/E017-gpu-router/v2/commands'
if out.exists():raise RuntimeError('Existing attempt')
out.mkdir(parents=True)
py=str(ROOT/'src/control/.venv/bin/python'); records=[]
def call(name,command,timeout):
 path=out/f'{name}.log'; start=time.time()
 try:
  with path.open('w') as f:r=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 except subprocess.TimeoutExpired:
  owned=ROOT/'variants'/variant/'owned-process.json'
  if owned.exists():p=load(owned);owned_stop(p['pid'],p['create_time'])
  save(out/f'{name}-timeout.json',{'command':command,'timeout_s':timeout});raise
 records.append({'name':name,'command':command,'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(path)})
 save(out/'commands.json',records);print(name,r.returncode,path.read_text()[-1500:],flush=True)
 if r.returncode:raise SystemExit(r.returncode)
call('register',[py,'scripts/register_variant.py',variant,'--source',str(ROOT/'src'/variant),'--binary',str(ROOT/'builds'/variant/'strata'),'--diagnostic','--overrides',str(out.parent/'overrides.json')],60)
call('native-targeted',[str(ROOT/'src/control/.venv/bin/ctest'),'--test-dir',str(ROOT/'builds'/variant),'--output-on-failure','--timeout','60','-R','(cache|adapt|async|verify|split|expert_multi|native_expert_parity)','-j','1'],300)
call('real-IQ',[str(ROOT/'builds'/variant/'native_expert_parity'),'/srv/ai/models/strata/models/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf','0','1','2','12'],300)
for mode in ['profiles','episodes']:
 command=[py,str(ROOT/'scripts/collect_traces.py'),mode,'--variant',variant,'--experiment','E017-gpu-router','--attempt','v2']
 script=ROOT/'variants'/variant/f'diagnose-{mode}.sh'
 script.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+' '.join(shlex.quote(x) for x in command)+' "$@"\n');script.chmod(0o755)
call('profiles',[str(ROOT/'variants'/variant/'diagnose-profiles.sh')],900)
call('episodes',[str(ROOT/'variants'/variant/'diagnose-episodes.sh')],900)
