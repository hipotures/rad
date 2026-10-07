"""Two full4K baseline signal traces under the newly frozen100us policy."""
import hashlib,subprocess
from lab import ROOT,Session,load,save
base=ROOT/'experiments/E028-persistent-replay';name='persistent-signal-v1';py=str(ROOT/'src/control/.venv/bin/python')
assert (base/'signal-v1/build/identity.json').exists()
subprocess.run([py,'scripts/register_variant.py',name,'--source',str(ROOT/'src'/name),'--binary',str(ROOT/'builds'/name/'strata'),'--overrides',str(base/'signal-overrides.json'),'--diagnostic'],cwd=ROOT,check=True)
for profile in ['32k','128k']:
 cfg=load(ROOT/'variants'/name/(profile+'.json'));cfg['server_entrypoint']=str(ROOT/'scripts/serve_capture.py');save(ROOT/'variants'/name/(profile+'.json'),cfg)
 path=base/'signal-v1'/profile;assert not path.exists()
 with Session(name,profile,path) as s:
  assert s.request('warmup','warmup','warmup')['state']=='VALID'
  run=s.request(profile+'-run1','run1','diagnostic');save(path/'results.json',{'run':run,'headline':False})
 assert run['actual_output_tokens']==4096 and run['reuse']==0 and run['actual_input_tokens']==load(ROOT/'workloads/manifest.json')['payloads'][profile+'-run1']['actual_input_tokens']
 reference=ROOT/'experiments/E024-pool-wait/diagnostic-v1'/profile/'traces/runtime-request2'
 subprocess.run([py,'scripts/check_trace_parity.py',str(path/'traces/runtime-request2'),str(reference),'--output',str(path/'strict-parity.json')],cwd=ROOT,check=True)
 print('FULL_SIGNAL_AND_BASELINE_PARITY_PASS',profile,flush=True)
save(base/'signal-v1/ready.json',{'state':'PASS_FULL_SIGNALS','profiles':['32k','128k'],'headline':False,'sameP1mathematics':True})
