"""Sequential prerequisites for E014 guard then E013 repair, before clean measurement."""
import subprocess,time
from lab import ROOT,save
out=ROOT/'analysis/batteries-E014-E013-v1'
if out.exists():raise RuntimeError('Existing battery command attempt')
out.mkdir(parents=True);commands=[];py=str(ROOT/'src/control/.venv/bin/python');ref=ROOT/'experiments/E006-frequency/correctness-r2/correctness/control'
for experiment,variant in [('E014-policy-off-guard','compatible-policy-off'),('E013-compatible-fast','compatible-fast-v2')]:
    cmd=[py,'scripts/correctness_battery.py','--variant',variant,'--experiment',experiment,'--reference',str(ref)]
    jobs=[('battery',cmd),('known-ground-truth',[py,'scripts/check_battery.py',str(ROOT/'experiments'/experiment/'v1/correctness'/variant)])]
    for name,cmd in jobs:
        start=time.time();path=out/f'{experiment}-{name}.log'
        with path.open('w') as stream:r=subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=400)
        commands.append({'experiment':experiment,'name':name,'command':cmd,'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(path)})
        save(out/'commands.json',commands);print(experiment,name,r.returncode,path.read_text()[-1800:],flush=True)
        if r.returncode:raise SystemExit(r.returncode)
