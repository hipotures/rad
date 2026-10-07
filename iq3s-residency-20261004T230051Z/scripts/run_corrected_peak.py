"""Repair peak-envelope replay after a demonstrated numerical queue bug."""
import hashlib, subprocess
from lab import ROOT,save
py=str(ROOT/'src/control/.venv/bin/python');out=ROOT/'experiments/E004-replay/v6-corrected-peak'
if out.exists():raise RuntimeError('Existing corrected peak attempt')
plan=[]
for profile,attempt in [('32k','v5'),('128k','v5-portfix')]:
    prefix=ROOT/'experiments/E003-diagnostics'/attempt/profile/'traces/runtime-request2'
    cmd=[py,str(ROOT/'scripts/replay.py'),str(prefix),'--output',str(out/f'{profile}-rate12p6'),'--rate','12.6','--policies','current','frequency','future-nextuse']
    plan.append({'profile':profile,'command':cmd})
save(out/'protocol.json',{'question':'Corrected exact completion publication eliminates cancellation at slow rates and one-entry floating discrepancies. Produce authoritative corrected peak results rather than overwrite legacy tables.','source_sha256':hashlib.sha256((ROOT/'scripts/replay.py').read_bytes()).hexdigest(),'repetitions':1,'plan':plan,'scope':'Deterministic repair, not an extra unchanged live benchmark repetition.'})
for item in plan:
    wrapped=[py,str(ROOT/'scripts/run_logged.py'),'--path',str(out/item['profile']/'logs/replay'),'--timeout','120','--',*item['command']]
    rc=subprocess.run(wrapped,cwd=ROOT,timeout=140).returncode
    if rc:raise SystemExit(rc)
