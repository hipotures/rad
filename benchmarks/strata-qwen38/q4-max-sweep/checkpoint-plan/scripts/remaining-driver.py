#!/usr/bin/env python3
"""Resume only after verified live topology process terminates; no overlapping engines."""
from pathlib import Path
import subprocess,json,time,psutil,sys
R=Path(__file__).resolve().parent;PY='/srv/ai/strata/.venv/bin/python'
state=json.loads((R/'topology-process.json').read_text());pid=state['pid']
try:
 proc=psutil.Process(pid);assert str(R/'topology.py') in proc.cmdline(),f'PID{pid} belongs to another process';proc.wait()
except psutil.NoSuchProcess:pass
assert (R/'raw/topology-selection.json').exists(),'Topology process ended without complete selection; inspect topology-driver.log'
for stage in ['tuning','contexts','extended','quality']:
 completed=R/'raw'/f'phase-{stage}-terminal.json'
 if completed.exists() and json.loads(completed.read_text()).get('exit_code')==0:continue
 with (R/'logs'/f'{stage}-driver.log').open('w') as f:
  cmd=[PY,str(R/(stage+'.py'))];proc=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT)
  (R/'remaining-process.json').write_text(json.dumps({'pid':proc.pid,'stage':stage,'command':cmd,'started':time.time()}))
  rc=proc.wait();completed.write_text(json.dumps({'exit_code':rc,'ended':time.time(),'stage':stage}))
  if rc:raise SystemExit(f'{stage} failed with{rc}; inspect log and authoritative terminal records before resuming')
print('Measurements ended. Completion still requires results/plots/report/requirements audit.',flush=True)
