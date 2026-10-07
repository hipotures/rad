"""Evaluate frozen independent episodes without choosing on held-out tasks."""
import subprocess
from lab import ROOT,save
py=str(ROOT/'src/control/.venv/bin/python')
out=ROOT/'experiments/E017-gpu-router/v2/analysis'
records=[]
for n,name in enumerate(['dev-code','dev-math','cal-prose','hold-code','hold-structured','hold-math'],2):
 command=[py,'scripts/analyze_gpu_router.py',str(ROOT/f'experiments/E017-gpu-router/v2/episodes/traces/runtime-request{n}'),'--output',str(out/f'{name}.json'),'--episode',name,'--reference',str(ROOT/f'experiments/E015-lowrank-router/v1/episodes/traces/runtime-request{n}')]
 with (out/f'{name}.log').open('w') as f:r=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 records.append({'command':command,'returncode':r.returncode});save(out/'episode-analysis-commands.json',records)
 print(name,r.returncode,(out/f'{name}.log').read_text()[-1200:],flush=True)
 if r.returncode:raise SystemExit(r.returncode)
