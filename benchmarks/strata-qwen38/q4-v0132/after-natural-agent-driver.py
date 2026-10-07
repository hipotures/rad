"""Serial remainingworkloads after fullsession independent outcome audit."""
from pathlib import Path
import json,psutil,subprocess,time,sys
R=Path(__file__).resolve().parent
state=json.loads((R/'agent128-natural-outcomes-process.json').read_text())
try:
    p=psutil.Process(state['pid']);assert str(R/'agent128-natural-outcomes.py') in p.cmdline();p.wait()
except psutil.NoSuchProcess:pass
assert json.loads((R/'raw/phase-agent128-natural-outcomes-terminal.json').read_text())['status'] in ['COMPLETE','MEASURED_WITH_SHORT_TURNS']
for script,args in [('audit-agent-progress.py',['--natural-outcomes']),('select-final-k8-outcomes.py',[])]:
    subprocess.run([sys.executable,str(R/script),*args],check=True)
jobs=[('compaction',[str(R/'extended.py'),'compaction'],'compaction'),('compaction-old-control',[str(R/'controls/v0131-compaction/control.py')],'compaction-old-control'),('quality',[str(R/'phase-quality.py')],'quality'),('needle',[str(R/'phase-needle.py')],'needle'),('iq3',[str(R/'phase-iq3.py')],'iq3'),('diagnostics',[str(R/'phase-diagnostics.py')],'diagnostics')]
from final_identity import require_phase
for label,args,phase in jobs:
    with (R/'logs'/f'remaining-after-natural-{label}-driver.log').open('x') as stream:
        command=[sys.executable,*args];process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT)
        (R/'next-phase-process.json').write_text(json.dumps({'pid':process.pid,'started':time.time(),'command':command}))
        rc=process.wait();(R/'raw'/f'remaining-after-natural-{label}-process-terminal.json').write_text(json.dumps({'exit_code':rc,'ended':time.time()}));assert rc==0,'Retain results andinspect; noautomaticretry'
        require_phase(phase)
print('Remaining measurements complete. Offlineanalysis/report/fullrequirementaudit stillrequired; no automaticgoalcompletion.',flush=True)
