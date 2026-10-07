"""Read atomic campaign status; never controls processes or launches work."""
import json,time
from pathlib import Path
c=Path(__file__).resolve().parents[1];clock=json.loads((c/'clock.json').read_text());p=json.loads((c/'progress.json').read_text());elapsed=time.monotonic()-clock['start_monotonic_s'];p.update(elapsed_s_now=elapsed,hard_remaining_s_now=max(0,clock["hard_budget_s"]-elapsed),status_age_s=time.time()-__import__('datetime').datetime.fromisoformat(p['utc']).timestamp());print(json.dumps(p,indent=2))
