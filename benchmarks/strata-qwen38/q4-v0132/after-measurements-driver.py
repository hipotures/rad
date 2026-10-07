from pathlib import Path
import psutil,json,subprocess,time
R=Path(__file__).resolve().parent;state=json.loads((R/'after-final-driver-process.json').read_text())
try:
 p=psutil.Process(state['pid']);assert str(R/'after-final-driver.py') in p.cmdline();p.wait()
except psutil.NoSuchProcess:pass
for marker in ['phase-long-terminal.json','phase-agent64-terminal.json','phase-agent128-terminal.json','phase-compaction-terminal.json','phase-quality-terminal.json','phase-needle-terminal.json','phase-iq3-terminal.json']:
 assert json.loads((R/'raw'/marker).read_text())['status']=='COMPLETE'
with (R/'logs/phase-diagnostics-driver.log').open('x') as f:
 cmd=['/srv/ai/strata-v0.1.32/.venv/bin/python',str(R/'phase-diagnostics.py')];p=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
 (R/'next-phase-process.json').write_text(json.dumps({'pid':p.pid,'started':time.time(),'command':cmd}))
 rc=p.wait();(R/'raw/diagnostics-process-terminal.json').write_text(json.dumps({'exit_code':rc,'ended':time.time()}));assert rc==0
assert json.loads((R/'raw/phase-diagnostics-terminal.json').read_text())['status']=='COMPLETE'
print('All measurements/diagnostics ready; final offline analysis and audit required.',flush=True)
