"""Read-only progress; never generates requests."""
import json,pathlib
from pool_spin import C
from lab import load
from analyze_pool import phases
s=load(C/'STATUS.json');print('STATUS',s['state'],'VALID',s.get('valid_measured_requests',0),'/24','CURRENT',s.get('current'))
if s.get('current'):
 x=s['current'];base=C/'raw'/x['policy']/x['profile']/f"rep{x['replicate']}";p=base/'telemetry/measured.jsonl'
 if p.exists():
  lines=p.read_text().splitlines()
  if lines:
   try:
    row=json.loads(lines[-1]);print('LIVE',(row.get('metrics') or {}).get('live'),'RAMavailableGiB',round(row['mem_available_gib'],1))
   except json.JSONDecodeError:pass
for p in sorted((C/'raw').glob('*/*/rep*/results.json'),key=lambda p:p.stat().st_mtime)[-4:]:
 r=load(p)[0];sys=phases(r);cpu=sys['decode']['CPU_VM_pct'];print(r['spin_policy'],r['profile'],'rep',r['replicate'],'TG',r['TG'],'PP',r['PP'],'wall',round(r['wall_s'],2),'CPUmean',round(cpu['mean'],1) if cpu else None,'output',r['actual_output_tokens'])
