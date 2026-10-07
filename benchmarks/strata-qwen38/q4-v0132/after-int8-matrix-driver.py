"""Serial validation only; do not promote config or start reporting automatically."""
from pathlib import Path
import json,psutil,time,subprocess,sys
R=Path(__file__).resolve().parent;state=json.loads((R/'int8-final-matrix-process.json').read_text())
try:
    process=psutil.Process(state['pid']);assert str(R/'validate-int8-matrix.py') in process.cmdline();process.wait()
except psutil.NoSuchProcess:pass
assert json.loads((R/'raw/phase-int8-final-matrix-terminal.json').read_text())['status']=='COMPLETE'
subprocess.run([sys.executable,str(R/'audit-int8-matrix-progress.py')],check=True)
assert json.loads((R/'evidence/int8-final-matrix-progress-independent-audit.json').read_text())['measured_requests_verified']==12
for action in ['long','agent64']:
    command=[sys.executable,str(R/'validate-int8-workloads.py'),action]
    with (R/'logs'/f'int8-validation-{action}-driver.log').open('x') as stream:
        process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT)
        (R/'int8-validation-current-process.json').write_text(json.dumps({'pid':process.pid,'started':time.time(),'command':command}))
        rc=process.wait();(R/'raw'/f'int8-validation-{action}-process-terminal.json').write_text(json.dumps({'exit_code':rc,'ended':time.time()}));assert rc==0,'Preserve failed validation and inspect; no automatic retry'
print('INT8 candidate validation completed. Review before changing final aliases or production selection.',flush=True)
