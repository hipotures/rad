"""Offline artifacts only after all engines and measured requests have finished."""
from pathlib import Path
import psutil,json,subprocess,time,importlib.util
R=Path(__file__).resolve().parent;state=json.loads((R/'after-natural-agent-driver-process.json').read_text())
try:
 p=psutil.Process(state['pid']);assert str(R/'after-natural-agent-driver.py') in p.cmdline();p.wait()
except psutil.NoSuchProcess:pass
assert json.loads((R/'raw/phase-diagnostics-terminal.json').read_text())['status']=='COMPLETE'
for p in psutil.process_iter(['cmdline']):
 try:
  cmd=p.info['cmdline'] or [];assert not(cmd and Path(cmd[0]).name=='strata'),'An engine is still active; defer offline work'
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
python='/srv/ai/strata-v0.1.32/.venv/bin/python'
s=json.loads((R/'STATUS.json').read_text());s['running']={'phase':'offline artifacts'};s['next_exact_action']='Assemble summaries/comparisons/plots/report, then independent renderedplots/20answers/bottleneck/completion audit.';(R/'STATUS.json').write_text(json.dumps(s,indent=2))
if subprocess.run([python,'-c','import matplotlib'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
 with (R/'logs/after-natural-matplotlib-install.log').open('x') as f:
  cmd=[python,'-m','pip','install','--only-binary=:all:','matplotlib'];rc=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT).returncode
  (R/'raw/after-natural-matplotlib-install-terminal.json').write_text(json.dumps({'command':cmd,'exit_code':rc,'scope':'Newvenv plottingdependency only, after alltimedrequests/engines stop','ended':time.time()}));assert rc==0,'Plot dependency install failed; inspect, preserve measurements'
for script in ['assemble-summary.py','compare-upgrade.py','plots.py','write-report.py','completion-audit.py']:
 with (R/'logs'/f'after-natural-{script}-offline.log').open('x') as f:
  cmd=[python,str(R/script)];rc=subprocess.run(cmd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT).returncode
  (R/'raw'/f'after-natural-{script}-offline-terminal.json').write_text(json.dumps({'command':cmd,'exit_code':rc,'ended':time.time()}));assert rc==0,f'{script} failed; preserve outputs and inspect'
s=json.loads((R/'STATUS.json').read_text());s['running']=None;s['completed'].append('Offline artifacts assembled; completion unproven until independent manual audit');s['next_exact_action']='Inspect renderedfigures, validate numeric/reportclaims and explicit usersections0–26, interpretbottleneck/OpenCodecosts, preserve source/model/oldfiles; repair missing artifacts andrerunaudit. Do notmarkgoalcompleteyet.';(R/'STATUS.json').write_text(json.dumps(s,indent=2))
spec=importlib.util.spec_from_file_location('status_render',R/'status-render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.render()
print('Artifacts assembled; mandatory independent final review pending.',flush=True)
