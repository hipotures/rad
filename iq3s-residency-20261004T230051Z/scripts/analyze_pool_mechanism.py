"""Existing summary/log counters only; no new instrumentation or additional requests."""
import argparse,re,statistics
from lab import ROOT,load,save
ap=argparse.ArgumentParser();ap.add_argument('experiment');a=ap.parse_args();base=ROOT/'experiments'/a.experiment;s=load(base/'summary.json')
pattern=re.compile(r'strata serve: stage (\d): (\d+) windows; per window: wait for the GPU ([\d.]+) ms, pool \+ plan ([\d.]+) ms, host staging ([\d.]+) ms, commit ([\d.]+) ms')
rows=[]
for c in s['cells']:
 for raw in c['raw_paths']:
  p=__import__('pathlib').Path(raw);r=load(p);log=(p.parent/'run-engine.log').read_text()
  stages=[dict(zip(['stage','windows','GPU_reach_wait_ms','pool_plan_ms','host_staging_ms','commit_ms'],[int(m[1]),int(m[2]),*map(float,m.groups()[2:])])) for m in pattern.finditer(log)]
  rows.append({'raw':raw,'family':c['family'],'profile':c['profile'],'role':c['role'],'TG':r['TG'],'wall_s':r['wall_s'],'stages':stages,'limits':'Overlapping pipeline averages; do not sum across stages or call GPU-reach wait pureGPUcompute.'})
save(base/'mechanism-log-rows.json',{'state':'COMPLETE_LOG_ANALYSIS','rows':rows,'interpretation':'Pool100 changes idle spin/wakeup timing, not expert identities or math. Higher CPU-positive waits can coexist with shorter GPU-reach/staging/overall latency. Exact cause within OS scheduling/host contention is an inference, not separately proven.'})
text='# Existing pipeline timing evidence\n\nRounded runtime stage averages, excluding warmup. Overlap prevents summing stage costs into synthetic request latency. GPU-reach includes coordination; it is not a pure GPU kernel timer.\n\n| Family |Profile|Policy|Stage|GPU-reach ms|Pool+plan ms|Host staging ms|\n|---|---|---|---:|---:|---:|---:|\n'
for c in s['cells']:
 for stage in [0,1]:
  st=[g for r in rows if all(r[k]==c[k] for k in ['family','profile','role']) for g in r['stages'] if g['stage']==stage]
  if st:text+=f'|{c["family"]}|{c["profile"]}|{c["role"]}|{stage}|'+ '|'.join(f'{statistics.median(g[k] for g in st):.3f}' for k in ['GPU_reach_wait_ms','pool_plan_ms','host_staging_ms'])+'|\n'
(base/'mechanism.md').write_text(text)
print('EXISTING_LOG_ROWS',len(rows),flush=True)
