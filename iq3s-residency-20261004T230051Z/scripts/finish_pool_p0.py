"""Wait for the finite clean driver, then run the predeclared P0 diagnostic stage serially."""
import pathlib, subprocess, time
from lab import ROOT, load, save, deadline
base=ROOT/'experiments/E026-pool-generalization';py=str(ROOT/'src/control/.venv/bin/python')
while time.time()<deadline()-2700:
    record=load(base/'v1/driver/command.json')
    if 'returncode' in record:break
    time.sleep(5)
else:raise RuntimeError('No new diagnostic stage in consolidation window')
if record['returncode']!=0:raise RuntimeError('Clean driver failure preserved; diagnose before starting selected waits')
subprocess.run([py,'scripts/analyze_pool_independent.py'],cwd=ROOT,check=True)
assert load(base/'summary.json')['state']=='COMPLETE_MEASUREMENTS'
cmd=[py,'scripts/run_logged.py','--path',str(base/'diagnostic-v1/driver'),'--timeout','1800','--',py,'scripts/run_pool_p0_diagnostics.py']
subprocess.run(cmd,cwd=ROOT,check=True)
save(base/'p0-ready-for-decision.json',{'state':'ALL_CLEAN_AND_DIAGNOSTIC_MEASUREMENTS_COMPLETE','epoch':time.time(),'next':'Review paired wall/TG/output/routing and waits; write P0 conclusion before P1.'})
print('P0_READY_FOR_DECISION',flush=True)
