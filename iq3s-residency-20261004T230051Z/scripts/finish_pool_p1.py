"""No experiment starts automatically beyond the P1 gate."""
import subprocess,time
from lab import ROOT,load,save
base=ROOT/'experiments/E027-pool-baseline';record=base/'v1/driver/command.json'
while True:
 d=load(record)
 if 'returncode' in d:
  assert d['returncode']==0,d
  break
 time.sleep(5)
subprocess.run([str(ROOT/'src/control/.venv/bin/python'),'scripts/analyze_pool_p1.py'],cwd=ROOT,check=True)
save(base/'ready-for-decision.json',{'state':'COMPLETE_STANDARD_MEASUREMENTS','next':'Review paired standard results, finalize P1 report/baseline, then begin P2.'})
print('P1_READY_FOR_DECISION',flush=True)
