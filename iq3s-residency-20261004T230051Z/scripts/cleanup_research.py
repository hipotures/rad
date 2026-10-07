"""Stop only recorded owned inference groups and preserve the final idle evidence."""
from datetime import datetime, timezone
import json
import os
import socket
import subprocess
import psutil
from lab import ROOT, load, save, owned_stop

stopped, stale, owned = [], [], {}
for record in (ROOT / 'variants').glob('*/owned-process.json'):
    x = load(record); owned[x['pid']] = x
    try:
        p = psutil.Process(x['pid'])
        if abs(p.create_time() - x['create_time']) > .1:
            stale.append({'record': str(record), 'reason': 'PID reused; not touched'})
            continue
        command = p.cmdline()
        if '-m' not in command or 'serve.server' not in command:
            stale.append({'record': str(record), 'reason': 'Not the recorded server; not touched'})
            continue
        owned_stop(x['pid'], x['create_time'])
        stopped.append({'record': str(record), 'pid': x['pid']})
    except psutil.NoSuchProcess:
        pass
active = []
for p in psutil.process_iter(['pid', 'cmdline', 'name']):
    command = p.info['cmdline'] or []
    if not any(str(ROOT) in s for s in command):
        continue
    if ('serve.server' in command or p.info['name'] == 'strata' or
            any(s.endswith(('train_predictors.py', 'build_variant.py')) for s in command)):
        active.append(p.info)
commands = {}
for name, command in {
    'GPU_compute': ['nvidia-smi', '--query-compute-apps=pid,process_name,used_gpu_memory', '--format=csv,noheader'],
    'GPU_state': ['nvidia-smi', '--query-gpu=index,name,utilization.gpu,memory.used,power.draw', '--format=csv'],
    'RAM': ['cat', '/proc/meminfo']}.items():
    r = subprocess.run(command, capture_output=True, text=True, timeout=15)
    commands[name] = {'command': command, 'returncode': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}
with socket.socket() as s:
    s.settimeout(1)
    port_open = s.connect_ex(('127.0.0.1', 18132)) == 0
save(ROOT / 'analysis/cleanup.json', {'utc': datetime.now(timezone.utc).isoformat(),
     'stopped_owned': stopped, 'stale_PID_records_not_touched': stale,
     'owned_active_inference_or_training': active, 'private_port18132_open': port_open,
     'commands': commands, 'unrelated_processes': 'Never killed.'})
assert not active and not port_open
assert commands['GPU_compute']['returncode'] == 0
assert not commands['GPU_compute']['stdout'].strip(), 'An unrelated GPU process exists; report it without stopping it'
print('Owned cleanup complete; no compute processes on either GPU; private port closed.')
