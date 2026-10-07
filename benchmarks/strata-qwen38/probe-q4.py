#!/usr/bin/env python3
"""Attempt required Q4 server configuration after IQ3_S exits; no fallback."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import psutil

BASE=Path(__file__).resolve().parent
REPO=Path('/srv/ai/strata')
DATA=Path('/srv/ai/models/strata')
OUT=BASE/'results/raw'
try:
    with urllib.request.urlopen('http://127.0.0.1:18080/health',timeout=1) as response:
        raise SystemExit('Benchmark server still running; stop it before Q4 failed-start measurement')
except (OSError, TimeoutError):
    pass
available=psutil.virtual_memory().available/1024**3
budget=80 if available>=110 else min(80,max(0,available-24))
assert available>=24 and budget>0,'Not enough available RAM'
verified=json.loads((OUT/'q4-sha256.json').read_text())
assert len(verified)==4 and all(x['sha256']==x['actual_sha256'] and x['bytes']==x['actual_bytes'] for x in verified)
pack=DATA/'packs/ud-q4_k_xl'
assert not (pack/'experts.bin').exists()
config={'exe':str(REPO/'engine/strata'),
    'args':['--pack',str(pack),'--native',str(DATA/'models/UD-Q4_K_XL'/verified[0]['file']),
        '--resident-budget-gib',str(budget),'--expert-profile',str(REPO/'data/expert-profile.bin'),
        '--expert-cache','auto','--prefill','auto','--spec','4','--spec-min-p','0.5',
        '--mtp',str(DATA/'mtp/rt'),'--max-context','262144','--kv','int8','--kv-resident','32768'],
    'cwd':str(REPO),'tokenizer':str(pack/'tokenizer'),'model_name':'qwen3.8-flash-next-ud-q4_k_xl',
    'log':str(OUT/'UD-Q4_K_XL-engine.log'),'gpu':[0,1],'layer_split':'auto',
    'host':'127.0.0.1','port':18081,'lib_dirs':['/usr/local/cuda/bin','/usr/local/cuda/lib64']}
path=BASE/'UD-Q4_K_XL-runtime.json'
path.write_text(json.dumps(config,indent=2))
command=[str(REPO/'.venv/bin/python'),'-m','serve.server','--engine','strata','--config',str(path),
         '--host','127.0.0.1','--port','18081']
started=time.perf_counter()
result=subprocess.run(command,cwd=REPO,capture_output=True,text=True,timeout=1200)
elapsed=time.perf_counter()-started
(OUT/'UD-Q4_K_XL-server.log').write_text(result.stdout+result.stderr)
engine_log=(OUT/'UD-Q4_K_XL-engine.log').read_text()
assert result.returncode!=0 and '--resident-cpu-experts does not support layer splits or remote expert caches' in engine_log
status=json.loads((OUT/'Q4-status.json').read_text())
status.update({'actual_pack_server_attempt':True,'returncode':result.returncode,
    'failed_start_wall_s':elapsed,'cold_start_s':None,'mem_available_before_start_gib':available,
    'resident_budget_gib':budget,'config':str(path),'command':command,
    'expert_residency_verified':False,'health_ready':False,'runtime_error':engine_log.strip()})
(OUT/'Q4-status.json').write_text(json.dumps(status,indent=2))
print(json.dumps(status,indent=2),flush=True)
