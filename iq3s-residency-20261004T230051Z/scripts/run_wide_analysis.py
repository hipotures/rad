"""Analyze development/calibration first and freeze horizon before held-out evaluation."""
import argparse
import subprocess
from lab import ROOT, load, save
ap=argparse.ArgumentParser()
ap.add_argument('stage',choices=['development','holdout','benchmarks'])
a=ap.parse_args()
base=ROOT/'experiments/E020-wide-gate-lookahead/v1'
out=base/'analysis'
out.mkdir(exist_ok=True)
py=str(ROOT/'src/control/.venv/bin/python')
names=['dev-code','dev-math','cal-prose','hold-code','hold-structured','hold-math']
if a.stage=='development':
    jobs=[(name,base/f'episodes/traces/runtime-request{n}',ROOT/f'experiments/E015-lowrank-router/v1/episodes/traces/runtime-request{n}') for n,name in enumerate(names,2) if n<=4]
elif a.stage=='holdout':
    assert (base/'selection.json').exists(), 'Freeze the development decision first'
    jobs=[(name,base/f'episodes/traces/runtime-request{n}',ROOT/f'experiments/E015-lowrank-router/v1/episodes/traces/runtime-request{n}') for n,name in enumerate(names,2) if n>=5]
else:
    assert (base/'selection.json').exists()
    jobs=[(p,base/f'{p}/traces/runtime-request2',ROOT/f'experiments/E015-lowrank-router/v1/{p}/traces/runtime-request2') for p in ['32k','128k']]
records=[]
for name,prefix,reference in jobs:
    target=out/f'{name}.json'
    if target.exists():raise RuntimeError('Existing analysis; retain it')
    cmd=[py,'scripts/analyze_wide_gate.py',str(prefix),'--output',str(target),'--episode',name,'--reference',str(reference)]
    with (out/f'{name}.log').open('w') as f:
        r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=180)
    records.append({'command':cmd,'returncode':r.returncode})
    save(out/f'{a.stage}-commands.json',records)
    print(name,r.returncode,(out/f'{name}.log').read_text()[-2500:],flush=True)
    if r.returncode:raise SystemExit(r.returncode)
    assert load(target)['state']=='PASS', 'Resolve correctness before interpreting signals'
