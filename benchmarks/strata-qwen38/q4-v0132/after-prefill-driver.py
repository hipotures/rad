"""Validated prefill -> evidence review -> prompt modes -> placement; serial only."""
from pathlib import Path
import psutil,json,subprocess,time
R=Path(__file__).resolve().parent;state=json.loads((R/'after-pp-driver-process.json').read_text())
try:
 p=psutil.Process(state['pid']);assert str(R/'after-pp-driver.py') in p.cmdline();p.wait()
except psutil.NoSuchProcess:pass
assert json.loads((R/'raw/phase-prefill-terminal.json').read_text())['status']=='COMPLETE'
for script in ['review-prefill.py','phase-prompt-modes.py','phase-placement.py']:
 with (R/'logs'/f'{script[:-3]}-driver.log').open('w') as f:
  cmd=['/srv/ai/strata-v0.1.32/.venv/bin/python',str(R/script)]
  p=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
  (R/'next-phase-process.json').write_text(json.dumps({'pid':p.pid,'started':time.time(),'command':cmd,'phase':script}))
  rc=p.wait();(R/'raw'/f'{script[:-3]}-process-terminal.json').write_text(json.dumps({'exit_code':rc,'ended':time.time()}))
  assert rc==0,f'{script} failed; retain results and STOP followup'
print('Prefill review, prompt modes and placement complete; next upstream calibration.',flush=True)
