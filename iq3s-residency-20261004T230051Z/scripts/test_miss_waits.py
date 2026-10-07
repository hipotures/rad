"""Preserve actual external-event fixture and relevant native test commands."""
import argparse,os,subprocess,time
from lab import ROOT,save
ap=argparse.ArgumentParser();ap.add_argument('--variant',default='diagnostic-v8');ap.add_argument('--experiment',default='E011-miss-waits');ap.add_argument('--attempt',default='v1');args=ap.parse_args()
out=ROOT/'experiments'/args.experiment/args.attempt/'tests'
if out.exists():raise RuntimeError('Existing test attempt')
out.mkdir(parents=True);commands=[];src=ROOT/'src'/args.variant;build=ROOT/'builds'/args.variant
def call(name,cmd,env=None):
    start=time.time();path=out/f'{name}.log'
    with path.open('w') as stream:r=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,env=env,timeout=300)
    commands.append({'name':name,'command':cmd,'environment_overrides':{k:env.get(k) for k in ['STRATA_LAB_MISS_WAITS','STRATA_LAB_TRACE']} if env else None,'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(path)})
    save(out/'commands.json',commands);print(name,r.returncode,path.read_text()[-2500:],flush=True)
    if r.returncode:raise SystemExit(r.returncode)
call('compile-event-fixture',['c++','-std=c++20','-O2','-I'+str(src/'include'),'-I/usr/local/cuda/include',str(ROOT/'scripts/miss_waits_test.cpp'),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(out/'event-fixture')])
off=os.environ.copy()
for key in ['STRATA_LAB_MISS_WAITS','STRATA_LAB_TRACE']:off.pop(key,None)
call('fixture-default-off',[str(out/'event-fixture')],off)
on=off|{'STRATA_LAB_MISS_WAITS':'1','STRATA_LAB_TRACE':str(out/'fixture')}
call('fixture-two-GPUs',[str(out/'event-fixture')],on)
if args.experiment=='E012-compatible-diagnostic':
    call('cross-layer-schema-regression',[str(ROOT/'src/control/.venv/bin/python'),str(ROOT/'scripts/test_crosslayer_trace.py')])
call('targeted-native',[str(ROOT/'src/control/.venv/bin/ctest'),'--test-dir',str(build),'--output-on-failure','--timeout','60','-R','(cache|adapt|async|verify|split|expert_multi|native_expert_parity)','-j','1'])
call('realIQparity',[str(build/'native_expert_parity'),'/srv/ai/models/strata/models/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf','0','1','2','12'])
save(out/'summary.json',{'state':'PASS','scope':'Default-off allocates no events; enabled two-device captured fixture T1/T4 two replays verifies72records; targeted native expert/cache/verify tests and real IQ parity. No frontend or algorithm change from already full-tested frozen diagnostics.'})
