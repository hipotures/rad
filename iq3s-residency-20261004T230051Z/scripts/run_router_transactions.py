"""One finite replay per frozen task; no repeated deterministic simulations."""
import subprocess
from lab import ROOT,save
out=ROOT/'experiments/E018-router-transactions/v1';py=str(ROOT/'src/control/.venv/bin/python');records=[]
if (out/'commands.json').exists():raise RuntimeError('Existing replayattempt')
for name in ['32k','128k','dev-code','dev-math','cal-prose','hold-code','hold-structured','hold-math']:
 command=[py,'scripts/router_transactions.py',str(ROOT/f'experiments/E017-gpu-router/v2/analysis/{name}.json'),'--output',str(out/f'analysis/{name}.json')]
 log=out/f'{name}.log'
 with log.open('w') as f:r=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 records.append({'command':command,'returncode':r.returncode});save(out/'commands.json',records)
 print(name,r.returncode,log.read_text()[-800:],flush=True)
 if r.returncode:raise SystemExit(r.returncode)
