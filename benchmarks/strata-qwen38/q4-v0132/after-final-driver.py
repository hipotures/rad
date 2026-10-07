"""Single serial owner for final workloads, old comparison, quality and IQ3 controls."""
from pathlib import Path
import psutil,json,subprocess,time,sys
R=Path(__file__).resolve().parent;state=json.loads((R/'after-mtp-driver-process.json').read_text())
try:
 p=psutil.Process(state['pid']);assert str(R/'after-mtp-driver.py') in p.cmdline();p.wait()
except psutil.NoSuchProcess:pass
assert json.loads((R/'raw/phase-final-matrix-terminal.json').read_text())['status']=='COMPLETE'
jobs=[
 ('long',[str(R/'extended.py'),'long'],'phase-long-terminal.json'),
 ('agent64',[str(R/'extended.py'),'agent64'],'phase-agent64-terminal.json'),
 ('agent128',[str(R/'extended.py'),'agent128'],'phase-agent128-terminal.json'),
 ('compaction',[str(R/'extended.py'),'compaction'],'phase-compaction-terminal.json'),
 ('compaction-v0131-control',[str(R/'controls/v0131-compaction/control.py')],'phase-compaction-old-control-terminal.json'),
 ('quality',[str(R/'phase-quality.py')],'phase-quality-terminal.json'),
 ('needle',[str(R/'phase-needle.py')],'phase-needle-terminal.json'),
 ('IQ3',[str(R/'phase-iq3.py')],'phase-iq3-terminal.json'),
]
if '--resume-agent128' in sys.argv:
 jobs=jobs[2:]
for label,args,marker in jobs:
 if label=='agent128' and '--resume-agent128' in sys.argv:label='agent128-retry'
 if label=='long' and (R/'long-recovery-plan.json').exists():
  label='long-retry';args=[str(R/'retry-long-8k.py')]
 logpath=R/'logs'/f'{label}-serial-driver.log'
 if logpath.exists() and '--resume-agent128' in sys.argv:
  logpath=R/'logs'/f'{label}-after-agent128-retry-serial-driver.log'
 with logpath.open('x') as f:
  cmd=['/srv/ai/strata-v0.1.32/.venv/bin/python',*args]
  p=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
  (R/'next-phase-process.json').write_text(json.dumps({'pid':p.pid,'started':time.time(),'command':cmd}))
  rc=p.wait();(R/'raw'/f'{label}-process-terminal.json').write_text(json.dumps({'exit_code':rc,'ended':time.time()}))
  assert rc==0,f'{label} failed; stop dependent chain and inspect preserved results'
  assert json.loads((R/'raw'/marker).read_text())['status']=='COMPLETE'
print('Measurements complete; independent diagnostics/audit/report remain.',flush=True)
