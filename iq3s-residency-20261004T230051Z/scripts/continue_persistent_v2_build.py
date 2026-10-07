"""No compilation concurrently with headline screening; build only after completed server cleanup."""
import time,subprocess
from lab import ROOT,load
base=ROOT/'experiments/E029-persistent-runtime/v1-fixed'
while not (base/'screen-driver/command.json').exists() or 'returncode' not in load(base/'screen-driver/command.json'):time.sleep(2)
r=load(base/'screen-driver/command.json');assert r['returncode']==0,r
subprocess.run([str(ROOT/'src/control/.venv/bin/python'),'scripts/build_variant.py','persistent-runtime-v2-fixed','--patch-script','patch_persistent_runtime_v2_fixed.py','--experiment','E029-persistent-runtime','--attempt','v2-fixed'],cwd=ROOT,check=True)
