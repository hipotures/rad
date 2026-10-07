from pathlib import Path
import subprocess,json,time,sys,traceback
R=Path(__file__).resolve().parent;py='/srv/ai/strata-pr578-control/.venv/bin/python'
# Resume-safe sequential phases. Each phase has its own raw done markers.
for phase in ['fair64','diagnostics','secondary','fresh','steady','matrix']:
 s=json.loads((R/'STATUS.json').read_text());s.update(running=phase,next_exact_action='Execute later.py '+phase);(R/'STATUS.json').write_text(json.dumps(s,indent=2))
 print('START PHASE',phase,time.strftime('%H:%M:%S',time.gmtime()),flush=True)
 with (R/'logs'/f'{phase}-driver.log').open('a') as f:p=subprocess.run([py,str(R/'later.py'),phase],stdout=f,stderr=subprocess.STDOUT)
 subprocess.run([py,str(R/'report.py')],check=True)
 if p.returncode:raise RuntimeError('Phase failed: '+phase+'; inspect saved exception/raw; no further benchmark started')
 print('COMPLETE PHASE',phase,time.strftime('%H:%M:%S',time.gmtime()),flush=True)
print('ALL PHASES COMPLETE; final audit pending',flush=True)
