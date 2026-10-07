"""Sequential bounded analysis of completed diagnostic files; no live benchmark."""
import subprocess,time
from lab import ROOT,save
out=ROOT/'experiments/E012-compatible-diagnostic/v1/analysis-commands'
if out.exists():raise RuntimeError('Existing analysis command attempt')
out.mkdir(parents=True);commands=[];py=str(ROOT/'src/control/.venv/bin/python')
for profile in ['32k','128k']:
    jobs=[('waits',[py,'scripts/analyze_miss_waits.py',profile,'--experiment','E012-compatible-diagnostic','--reference-experiment','E011-miss-waits','--reference-attempt','v1']),
          ('original-promotion',[py,'scripts/analyze_live_promotions.py',profile,'--experiment','E011-miss-waits']),
          ('compatible-promotion',[py,'scripts/analyze_live_promotions.py',profile])]
    for name,cmd in jobs:
        start=time.time();path=out/f'{profile}-{name}.log'
        with path.open('w') as stream:r=subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=120)
        commands.append({'name':profile+'-'+name,'command':cmd,'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(path)})
        save(out/'commands.json',commands);print(profile,name,r.returncode,path.read_text()[-2000:],flush=True)
        if r.returncode:raise SystemExit(r.returncode)
