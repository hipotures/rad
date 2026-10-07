"""Run preserved upstream tests and real-model expert parity for one frozen variant."""
import argparse, json, pathlib, subprocess, time
from lab import ROOT, save, deadline
ap=argparse.ArgumentParser()
ap.add_argument('variant');ap.add_argument('--experiment',required=True);ap.add_argument('--attempt',default='v1');ap.add_argument('--scope',choices=['all','python'],default='all')
a=ap.parse_args();cfg=json.loads((ROOT/'variants'/a.variant/'32k.json').read_text())
src=pathlib.Path(cfg['cwd']);build=pathlib.Path(cfg['exe']).parent
out=ROOT/'experiments'/a.experiment/a.attempt/('tests' if a.scope=='all' else 'tests-python-repair')
if out.exists():raise RuntimeError('Test attempt exists; refuse overwrite')
out.mkdir(parents=True);commands=[]
def call(name,cmd,timeout=900,cwd=None):
    path=out/f'{name}.log';start=time.time()
    with path.open('w') as stream:
        r=subprocess.run(cmd,cwd=cwd,stdout=stream,stderr=subprocess.STDOUT,timeout=min(timeout,max(1,int(deadline()-time.time()-2700))))
    rec={'name':name,'command':cmd,'cwd':str(cwd) if cwd else None,'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(path)}
    commands.append(rec);save(out/'commands.json',commands)
    print(name,r.returncode,path.read_text()[-2200:],flush=True)
    return r.returncode
ctest=call('native-tests',[str(ROOT/'src/control/.venv/bin/ctest'),'--test-dir',str(build),'--output-on-failure','--timeout','60','-j','1']) if a.scope=='all' else None
python=call('python-tests',[cfg['python'],'-m','unittest','discover','-s','serve','-p','test_*.py'],cwd=src)
parity=call('iq3s-real-expert-parity',[str(build/'native_expert_parity'),'/srv/ai/models/strata/models/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf','0','1','2','12'],timeout=300) if a.scope=='all' else None
save(out/'summary.json',{'variant':a.variant,'ctest_returncode':ctest,'python_returncode':python,'real_native_parity_returncode':parity,
    'interpretation':'Review every CTest failure against documented missing fixtures and mlock restriction; no real correctness failure is waived.'})
if python or parity:raise SystemExit('Correctness prerequisite failed')
