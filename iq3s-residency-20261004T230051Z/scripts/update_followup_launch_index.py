"""Append new follow-up entries; never regenerate prior launchers or metadata."""
import argparse, pathlib
from lab import ROOT, load, save
ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['P0','P1','P2'],required=True);a=ap.parse_args()
names={'P0':['pool-p0-default','pool-p0-100','pool-p0-diag-default','pool-p0-diag-sleep100us'],'P1':['p1-pool-default','p1-baseline'],'P2':['persistent-signal-v1','persistent-v1-off','persistent-v1-on','persistent-v1-fixed-off','persistent-v1-fixed-on','persistent-v2-off','persistent-v2-on','persistent-v2-diagnostic']}[a.phase]
idx=load(ROOT/'launch-index.json');existing={x['variant'] for x in idx};text=(ROOT/'launch-index.md').read_text();addition=[]
for name in names:
 d=ROOT/'variants'/name
 if not d.exists():continue
 diag='diag' in name or name=='persistent-signal-v1';state='DIAGNOSTIC_ONLY' if diag else 'CLEAN_RESEARCH_CONTROL' if name!='p1-baseline' else 'P1_FROZEN_BASELINE'
 cfgs=[load(d/(p+'.json')) for p in ['32k','128k']]
 # Aliases missing on new diagnostic configs only. Never rewrite existing scripts.
 py=str(ROOT/'src/control/.venv/bin/python');lab=str(ROOT/'scripts/lab.py')
 for p in ['32k','128k']:
  for mode in ['start','benchmark']:
   script=d/(mode+'-'+p+'.sh')
   if not script.exists():script.write_text(f'#!/usr/bin/env bash\nset -euo pipefail\nexec "{py}" "{lab}" {mode} --variant "{name}" --profile "{p}" "$@"\n');script.chmod(0o755)
 for script,body in [('stop.sh',f'exec "{py}" "{lab}" stop --variant "{name}" "$@"'),('reproduce.sh',f'"{d}/benchmark-32k.sh" "$@"\n"{d}/benchmark-128k.sh" "$@"')]:
  p=d/script
  if not p.exists():p.write_text('#!/usr/bin/env bash\nset -euo pipefail\n'+body+'\n');p.chmod(0o755)
 if a.phase=='P2':
  state='DIAGNOSTIC_ONLY' if diag else 'P2_CORRECTNESS_NEGATIVE_RESEARCH' if name.endswith('-on') else 'P2_OFF_INTEGRATION_GUARD'
  if name in ['persistent-v1-off','persistent-v1-on']:state='SUPERSEDED_SOURCE_VALIDATION_BLOCKER'
 if name in existing:continue
 c=cfgs[0];entry={'variant':name,'state':state,'phase':a.phase,'source_sha':c['source_sha'],'binary_sha256':c['binary_sha256'],'source':c['cwd'],'build':c['exe'],'configs':[str(d/(p+'.json')) for p in ['32k','128k']],'start32':str(d/'start-32k.sh'),'start128':str(d/'start-128k.sh'),'stop':str(d/'stop.sh'),'reproduce':str(d/'reproduce.sh'),'environment':c['env'],'model_revision':c['model_revision'],'actual_start_records':'experiments/E026-pool-generalization/' if a.phase=='P0' else 'experiments/E027-pool-baseline/' if a.phase=='P1' else 'experiments/E029-persistent-runtime/','scope':'Research-only; normal user launchers unchanged'}
 idx.append(entry);addition.append(f'| {name} | {state} | `{c["source_sha"]}` | [configs](variants/{name}/README.md) | `{d}/start-32k.sh` | `{d}/start-128k.sh` | `{d}/stop.sh` |')
if addition:text+='\n## '+a.phase+' follow-up\n\n| Variant | State | Source | Config |32K|128K|Stop|\n|---|---|---|---|---|---|---|\n'+'\n'.join(addition)+'\n'
save(ROOT/'launch-index.json',idx);(ROOT/'launch-index.md').write_text(text)
ledger=load(ROOT/'candidate-ledger.json');experiment={'P0':'E026-pool-generalization','P1':'E027-pool-baseline','P2':'E029-persistent-runtime'}[a.phase];result=ROOT/'experiments'/experiment/'summary.json'
ledger.setdefault('followup_phases',{})[a.phase]={'experiment':experiment,'report':'experiments/'+experiment+'/report.md','state':load(result)['state'] if result.exists() else load(ROOT/'STATUS.json')['last_stage']['state']}
save(ROOT/'candidate-ledger.json',ledger)
print('INDEX_APPENDED',a.phase,len(addition),flush=True)
