"""Run bounded regenerations with flushed progress, after all GPU work stops."""
import subprocess,sys
from common import *
no_gpu()
progress(5,'Regenerate exact byte partitions and paired results',task='all retained runs',arm='all frozen arms',version=load(C/'configs/runtime-identity.json')['source_sha'],completed=1,remaining=3,next_action='Analysis, source recovery, storage audit and cleanup',eta='unknown')
for script in ['summarize.py','protection_costs.py','resources.py','final_diagnostics.py','render_report.py']:
 ledger('Regeneration START',script=script)
 with Heartbeat('regeneration '+script,5):r=subprocess.run([sys.executable,str(C/'code'/script)],timeout=1200)
 ledger('Regeneration END',script=script,exit_code=r.returncode);assert r.returncode==0,script
