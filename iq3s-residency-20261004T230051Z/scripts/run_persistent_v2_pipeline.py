"""Sequential tests -> correctness -> byte audit -> final pairedmatrix, no overlappingrequests."""
from lab import ROOT,load
import subprocess,time
base=ROOT/'experiments/E029-persistent-runtime/v2-fixed';py=str(ROOT/'src/control/.venv/bin/python')
while 'returncode' not in load(base/'native-tests/command.json'):time.sleep(2)
assert load(base/'native-tests/command.json')['returncode']==0
for script in ['run_persistent_v2_correctness.py','run_persistent_v2_audit.py','run_persistent_v2_final.py']:
 subprocess.run([py,'scripts/run_logged.py','--path',str(base/(script.removesuffix('.py')+'-driver')),'--timeout','2600','--',py,'scripts/'+script],cwd=ROOT,check=True)
print('P2_FINAL_CONFIRMATION_COMPLETE',flush=True)
