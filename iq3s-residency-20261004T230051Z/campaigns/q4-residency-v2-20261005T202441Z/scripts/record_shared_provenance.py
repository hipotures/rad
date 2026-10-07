"""Identity of preserved shared harness/frontend and dependency/build settings."""
from campaign import C,R,save
from pathlib import Path
import hashlib,subprocess,json
paths=[R/'scripts/lab.py',R/'scripts/q4_multigpu.py',R/'scripts/record_ui_metrics.py',C/'scripts/serve_capture.py']
rows=[]
for p in paths:
 if p.exists():rows.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
for name in ['serve/server.py','serve/frontend.py','serve/backends/strata.py','tools/strata_tokenizer.py']:
 p=R/'src/control'/name
 if p.exists():rows.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
save(C/'git/shared-harness.json',rows)
cmd=[str(R/'src/control/.venv/bin/python'),'-m','pip','freeze']
r=subprocess.run(cmd,capture_output=True,text=True,timeout=30);(C/'git/python-lock.txt').write_text(r.stdout);save(C/'git/python-lock-command.json',{'command':cmd,'exit_code':r.returncode,'stderr':r.stderr})
