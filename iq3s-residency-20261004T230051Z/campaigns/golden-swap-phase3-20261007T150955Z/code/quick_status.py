"""Read atomic campaign status; never controls processes or launches work."""
import json,time
from pathlib import Path
c=Path(__file__).resolve().parents[1];clock=json.loads((c/'clock.json').read_text());p=json.loads((c/'progress.json').read_text());elapsed=time.monotonic()-clock['start_monotonic_s'];p.update(elapsed_s_now=elapsed,hard_remaining_s_now=max(0,clock["hard_budget_s"]-elapsed),status_age_s=time.time()-__import__('datetime').datetime.fromisoformat(p['utc']).timestamp());
if p.get('step')==4 and 'block' not in p and (c/'run-order.json').exists():
 order=json.loads((c/'run-order.json').read_text());kind='independent' if p.get('task')=='text-json-rfc8259' else 'main';idx=min(p.get('completed',0),len(order[kind])-1);p['block_from_frozen_order']=order[kind][idx]['block']
print(json.dumps(p,indent=2))
