import psutil,time,subprocess,json
from pathlib import Path
R=Path(__file__).resolve().parent
pid=53273
try:
 p=psutil.Process(pid)
 assert 'phase1' in p.cmdline()
 p.wait()
except psutil.NoSuchProcess:pass
for name in ['T2-auto','T1-arena','T0-control']:
 assert (R/'raw'/f'{name}-done.json').exists(),f'Missing terminal result {name}'
with (R/'logs/topology-driver.log').open('w') as f:
 p=subprocess.Popen(['/srv/ai/strata/.venv/bin/python',str(R/'topology.py')],stdout=f,stderr=subprocess.STDOUT)
 (R/'topology-process.json').write_text(json.dumps({'pid':p.pid,'command':p.args,'started':time.time()}))
 rc=p.wait()
 (R/'topology-process-terminal.json').write_text(json.dumps({'exit_code':rc,'ended':time.time()}))
