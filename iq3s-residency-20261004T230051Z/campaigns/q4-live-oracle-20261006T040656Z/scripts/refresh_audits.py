"""Rebuild analyses from preserved evidence after GPU work; never runs inference."""
from pathlib import Path
import json,time,subprocess
import fidelity,inspect_oracle,progression,system_metrics,event_diagnostics,aggregate
C=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip(),'Refuse heavy audit concurrent with GPU work'
 records=[]
 for p in sorted((C/'raw').iterdir()):
  if not (p/'results.json').exists():continue
  r=json.loads((p/'results.json').read_text())
  if not r.get('tape') or 'v3' not in p.name:continue
  t=Path(r['tape']);start=time.monotonic();print('AUDIT_START',p.name,flush=True)
  a=fidelity.audit(p.name,t);b=inspect_oracle.audit(p.name,t)
  assert a['state']=='PASS' and b['state']=='PASS',(p.name,a['errors'],b['errors'])
  progression.analyze(p.name,t);system_metrics.analyze(p.name,t);event_diagnostics.analyze(p.name,t)
  records.append({'label':p.name,'state':'PASS','wall_s':time.monotonic()-start})
  print('AUDIT_PASS',p.name,round(records[-1]['wall_s'],2),flush=True)
 (C/'analysis/final-audit-index.json').write_text(json.dumps(records,indent=2)+'\n');aggregate.generate()
