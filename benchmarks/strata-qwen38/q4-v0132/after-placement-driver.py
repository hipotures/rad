"""Start upstream calibration only after validated serial placement terminal."""
from pathlib import Path
import psutil,json,subprocess,time
R=Path(__file__).resolve().parent;state=json.loads((R/'after-prefill-driver-process.json').read_text())
try:
 p=psutil.Process(state['pid']);assert str(R/'after-prefill-driver.py') in p.cmdline();p.wait()
except psutil.NoSuchProcess:pass
assert json.loads((R/'raw/phase-placement-terminal.json').read_text())['status']=='COMPLETE'
with (R/'logs/phase-calibration-driver.log').open('w') as f:
 cmd=['/srv/ai/strata-v0.1.32/.venv/bin/python',str(R/'phase-calibration.py')];p=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
 (R/'calibration-driver-process.json').write_text(json.dumps({'pid':p.pid,'started':time.time(),'command':cmd}))
 rc=p.wait();(R/'raw/calibration-process-terminal.json').write_text(json.dumps({'exit_code':rc,'ended':time.time()}));assert rc==0,'Calibration phase failed: STOP and inspect preserved evidence'
print('Calibration complete; MTP phase pending.',flush=True)
