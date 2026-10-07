"""Wait finalheadlineclean completion, then build one diagnostic version andrun one perprofile."""
import time,subprocess
from lab import ROOT,load,save,Session
base=ROOT/'experiments/E029-persistent-runtime';py=str(ROOT/'src/control/.venv/bin/python');final=base/'v2-fixed/run_persistent_v2_final-driver/command.json'
while not final.exists() or 'returncode' not in load(final):time.sleep(3)
assert load(final)['returncode']==0,load(final)
subprocess.run([py,'scripts/build_variant.py','persistent-runtime-v2-diagnostic-fixed','--patch-script','patch_persistent_diagnostic.py','--experiment','E029-persistent-runtime','--attempt','v2-diagnostic-fixed'],cwd=ROOT,check=True)
file=base/'v2-diagnostic/overrides.json';save(file,{'env':{'STRATA_POOL_SPIN_US':'100','STRATA_LAB_PERSISTENT':'1'},'diagnostic_only':True,'algorithm':'Exact frozenv2policy, adds hostsubmission/joinphase clocks and causaltimecolumns.'})
subprocess.run([py,'scripts/register_variant.py','persistent-v2-diagnostic','--source',str(ROOT/'src/persistent-runtime-v2-diagnostic-fixed'),'--binary',str(ROOT/'builds/persistent-runtime-v2-diagnostic-fixed/strata'),'--overrides',str(file)],cwd=ROOT,check=True)
for profile in ['32k','128k']:
 cfgfile=ROOT/'variants/persistent-v2-diagnostic'/f'{profile}.json';cfg=load(cfgfile);cfg.pop('diagnostic_env',None);cfg['diagnostic_env']={'STRATA_LAB_PERSISTENT_LOG':'{attempt}/raw/admissions'};cfg['server_entrypoint']=str(ROOT/'scripts/serve_capture.py');save(cfgfile,cfg)
 path=base/f'v2-diagnostic/{profile}';assert not path.exists()
 with Session('persistent-v2-diagnostic',profile,path) as s:
  assert s.request('warmup','warmup','warmup')['state']=='VALID';r=s.request(profile+'-run1','run','diagnostic');save(path/'results.json',{'run':r,'headline':False})
 assert r['state']=='VALID' and r['actual_output_tokens']==4096
 print('DIAGNOSTIC_COMPLETED',profile,flush=True)
save(base/'v2-diagnostic/ready.json',{'state':'COMPLETE_SCOPED_COPY_DIAGNOSTICS','headline':False})
