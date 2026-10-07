"""Correct selected-sample accounting only; no inference, no residency audit changes."""
from pathlib import Path
import json,time,subprocess
import fidelity
C=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,timeout=15).strip()
 for p in sorted((C/'raw').iterdir()):
  if not (p/'results.json').exists() or 'v3' not in p.name:continue
  r=json.loads((p/'results.json').read_text())
  if not r.get('tape'):continue
  a=fidelity.audit(p.name,Path(r['tape']));assert a['state']=='PASS',a
  print('NUMERICAL_SAMPLE_AUDIT',p.name,a['selected_activation_check']['sampled_values'],flush=True)
