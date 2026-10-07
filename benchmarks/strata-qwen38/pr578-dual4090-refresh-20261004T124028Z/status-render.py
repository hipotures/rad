"""Render complete persistent status, without querying engine or telemetry."""
import json
from pathlib import Path

def render(root=None):
 root=Path(root or Path(__file__).resolve().parent);s=json.loads((root/'STATUS.json').read_text());lines=['# Strata PR578 — '+s.get('status','IN_PROGRESS'),'','## Running','','```json',json.dumps(s.get('running'),indent=2),'```','','## Completed','']
 lines += ['- '+x for x in s.get('completed',[])]
 lines += ['','## Pending','']+['- '+x for x in s.get('pending',[])]
 lines += ['','## Current winners','','```json',json.dumps(s.get('current_winners'),indent=2),'```','','## Excluded runs','','```json',json.dumps(s.get('excluded_runs',[]),indent=2),'```','','## Next exact action','',s.get('next_exact_action',''),'', 'Full authorized scope: PLAN.md. Both builds use frozen upstream main and local PR snapshot.']
 (root/'STATUS.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':render()
