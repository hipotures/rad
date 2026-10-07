"""Continue only after the existing serial MTP owner exits successfully."""
from pathlib import Path
import psutil,json,subprocess,time,sys
from final_identity import final_label
R=Path(__file__).resolve().parent
state=json.loads((R/'after-calibration-driver-process.json').read_text())
try:
 p=psutil.Process(state['pid']);assert str(R/'after-calibration-driver.py') in p.cmdline();p.wait()
except psutil.NoSuchProcess:pass
assert json.loads((R/'raw/phase-mtp-terminal.json').read_text())['status']=='COMPLETE'
jobs=[('phase-kv.py','phase-kv-terminal.json'),('phase-final-matrix.py','phase-final-matrix-terminal.json')]
resume='--resume-final-only' in sys.argv
if resume:
 assert json.loads((R/'raw/phase-kv-terminal.json').read_text())['status']=='COMPLETE'
 jobs=jobs[1:]
for script,marker in jobs:
 suffix='-attempt2' if resume else ''
 with (R/'logs'/f'{script}-driver{suffix}.log').open('x') as f:
  cmd=['/srv/ai/strata-v0.1.32/.venv/bin/python',str(R/script)]
  p=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
  (R/'next-phase-process.json').write_text(json.dumps({'pid':p.pid,'started':time.time(),'command':cmd}))
  rc=p.wait()
  (R/'raw'/f'{script}-process-terminal.json').write_text(json.dumps({'exit_code':rc,'ended':time.time()}))
  assert rc==0, f'{script} failed; preserve results and inspect before continuing'
  assert json.loads((R/'raw'/marker).read_text())['status']=='COMPLETE'
print('KV and final matrix complete; proceed with final workloads.',flush=True)
