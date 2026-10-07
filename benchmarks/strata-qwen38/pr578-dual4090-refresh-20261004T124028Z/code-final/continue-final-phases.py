#!/usr/bin/env python3
"""Sequential phase launcher; never starts a successor when its predecessor fails."""
import subprocess,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parent
for phase in ['fresh','steady','matrix']:
 state={'running_phase':phase,'updated_UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'next_phases':['fresh','steady','matrix'][['fresh','steady','matrix'].index(phase)+1:]}
 (R/'continuation-progress.json').write_text(json.dumps(state,indent=2)+'\n')
 with (R/'logs'/('refresh-'+phase+'.log')).open('a') as f:
  code=subprocess.call([sys.executable,str(R/'refresh-driver.py'),phase],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if code:
  state.update(status='FAILED',exit_code=code);(R/'continuation-progress.json').write_text(json.dumps(state,indent=2)+'\n');raise SystemExit(code)
state.update(status='MEASUREMENTS_COMPLETE',running_phase=None,next_phases=['analyze','report','audit']);(R/'continuation-progress.json').write_text(json.dumps(state,indent=2)+'\n')
