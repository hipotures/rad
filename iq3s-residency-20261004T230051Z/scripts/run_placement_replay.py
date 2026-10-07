"""Run the predeclared two-profile compatible-slot experiment serially."""
import hashlib,subprocess
from lab import ROOT,save
py=str(ROOT/'src/control/.venv/bin/python');out=ROOT/'experiments/E009-placement/v1'
plan=[]
for profile,attempt in [('32k','v5'),('128k','v5-portfix')]:
    prefix=ROOT/'experiments/E003-diagnostics'/attempt/profile/'traces/runtime-request2'
    cmd=[py,str(ROOT/'scripts/placement_replay.py'),str(prefix),'--output',str(out/profile/'replay.json')]
    plan.append({'profile':profile,'command':cmd})
if (out/'plan.json').exists():raise RuntimeError('Existing placement plan')
save(out/'plan.json',{'plan':plan,'source_hashes':{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in ['placement_replay.py','replay.py']},'repetitions':1,'same_frozen_per_device_memory':True})
for p in plan:
    rc=subprocess.run([py,str(ROOT/'scripts/run_logged.py'),'--path',str(out/p['profile']/'logs/replay'),'--timeout','120','--',*p['command']],cwd=ROOT,timeout=140).returncode
    if rc:raise SystemExit(rc)
