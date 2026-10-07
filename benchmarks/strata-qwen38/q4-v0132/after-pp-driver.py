"""Wait authoritative livecontrolhandle, then launchprefill onlyaftervalidatedterminal."""
from pathlib import Path
import psutil,json,subprocess,time
R=Path(__file__).resolve().parent;state=json.loads((R/'pp-control-driver-process.json').read_text())
try:
 p=psutil.Process(state['pid']);assert str(R/'phase-pp-control.py') in p.cmdline();p.wait()
except psutil.NoSuchProcess:pass
assert json.loads((R/'raw/phase-pp-control-terminal.json').read_text())['status']=='COMPLETE','Control ended withoutvalidatedterminal; inspect ratherthanrestart'
assert json.loads((R/'comparison-pp-control.json').read_text())['status']=='COMPLETE_CONTROLLED_VERSION_AB'
with (R/'logs/prefill-driver.log').open('w') as f:
 cmd=['/srv/ai/strata-v0.1.32/.venv/bin/python',str(R/'phase-prefill.py')];p=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
 (R/'prefill-process.json').write_text(json.dumps({'pid':p.pid,'started':time.time(),'command':cmd}))
 rc=p.wait();(R/'raw/prefill-process-terminal.json').write_text(json.dumps({'exit_code':rc,'ended':time.time()}));assert rc==0,'Prefillphase failed, do notstartanotherphase'
print('Prefill ended; nextphase own/no-borrowrequiresconfirmedpolicyreview.',flush=True)
