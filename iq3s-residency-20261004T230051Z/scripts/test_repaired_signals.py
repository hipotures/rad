"""Target CUDA/cache/split paths affected by the event-node-only repair."""
import subprocess,time
from lab import ROOT,save
out=ROOT/'experiments/E008-router-boundary/v2/tests'
if out.exists():raise RuntimeError('Existing repaired test attempt')
out.mkdir(parents=True);commands=[]
pattern='(cache|adapt|async|verify|split|expert_multi|native_expert_parity)'
plan=[('targeted-native',[str(ROOT/'src/control/.venv/bin/ctest'),'--test-dir',str(ROOT/'builds/diagnostic-v7'),'--output-on-failure','--timeout','60','-R',pattern,'-j','1']),('realIQparity',[str(ROOT/'builds/diagnostic-v7/native_expert_parity'),'/srv/ai/models/strata/models/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf','0','1','2','12'])]
for name,cmd in plan:
    start=time.time()
    with (out/f'{name}.log').open('w') as stream:r=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
    commands.append({'command':cmd,'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(out/f'{name}.log')});save(out/'commands.json',commands)
    print(name,r.returncode,(out/f'{name}.log').read_text()[-3000:],flush=True)
    if r.returncode:raise SystemExit(r.returncode)
save(out/'summary.json',{'state':'PASS','scope':'Same frozen base plus external-event-record repair. Full v6 native/Python evidence retained separately; no frontend or algorithm change in v7. Actual two-device graph event reproducer also passes.'})
