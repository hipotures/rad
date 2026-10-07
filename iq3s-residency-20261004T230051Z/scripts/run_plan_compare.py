"""Two frozen same-binary warmup-only arithmetic diagnostics, no speed claim."""
import argparse,subprocess
from lab import ROOT,Session,save
ap=argparse.ArgumentParser();ap.add_argument('--attempt',default='compare-v1');ap.add_argument('--reuse-registered',action='store_true');a=ap.parse_args()
variant='diagnostic-plan-compare-v1';out=ROOT/'experiments/E016-device-plan-ids'/a.attempt
py=str(ROOT/'src/control/.venv/bin/python')
if (ROOT/'variants'/variant).exists() and not a.reuse_registered:raise RuntimeError('Variant already registered')
fixture=out/'PLE-fixture'
commands=[['c++','-std=c++20','-O2','-I/usr/local/cuda/include',str(ROOT/'scripts/ple_device_plan_test.cpp'),str(ROOT/'builds'/variant/'libstrata_kernels.a'),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-lcublas','-lcublasLt','-pthread','-o',str(fixture)],[str(fixture)]]
for n,command in enumerate(commands):
 with (out/f'PLE-fixture-command{n}.log').open('w') as f:r=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=60)
 save(out/f'PLE-fixture-command{n}.json',{'command':command,'returncode':r.returncode})
 print('PLE fixture',n,r.returncode,(out/f'PLE-fixture-command{n}.log').read_text()[-1500:],flush=True)
 if r.returncode:raise SystemExit(r.returncode)
if not a.reuse_registered:subprocess.run([py,'scripts/register_variant.py',variant,'--source',str(ROOT/'src'/variant),'--binary',str(ROOT/'builds'/variant/'strata'),'--diagnostic'],check=True)
for mode in ['off','on','on-ple-fence']:
 path=out/mode
 if path.exists():raise RuntimeError('Existing arithmetic attempt')
 extra={'STRATA_LAB_PLAN_COMPARE':'1'}
 if mode!='off':extra.update(STRATA_VERIFY_DEVICE_PLAN='1',STRATA_LAB_PLAN_IDS='1')
 if mode=='on-ple-fence':extra['STRATA_LAB_PLAN_PLE_FENCE']='1'
 with Session(variant,'32k',path,diagnostic_env=extra) as s:
  r=s.request('warmup','warmup','warmup')
  assert r['state']=='VALID'
  save(path/'results.json',{'headline':False,'request':r,'changed_setting':mode})
  subprocess.run([str(ROOT/'variants'/variant/'stop.sh')],check=True)
