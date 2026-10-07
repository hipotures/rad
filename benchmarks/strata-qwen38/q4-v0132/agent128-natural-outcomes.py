"""Complete one uninterrupted11-request session; negative output-length outcomes retained."""
import extended as e
import run as r
import json,time
label='AGENT-127000-v0132-natural-eos-session'
result=e.agentic(127000,label_override=label,source_override='FINAL-v0132-Q4',observe_natural_short=True)
assert len(result['runs'])==11 and len(json.loads(r.Path(result['history']).read_text()))==23
status='COMPLETE' if result['output_minimum_met'] else 'MEASURED_WITH_SHORT_TURNS'
r.c.save(r.ROOT/'raw/phase-agent128-natural-outcomes-terminal.json',{'status':status,'ended':time.time(),'result':str(r.ROOT/'raw'/f'{label}-done.json'),'short_turns':result['natural_short_turns'],'note':'One unchanged liveengine; ordinaryreuse; all10 followups attempted. Below256 naturalEOS is a reportednegative outcome, not full-output success.'})
print(status,flush=True)
