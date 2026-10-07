"""Read development evidence; no selection on main policy outcomes."""
import re
from common import *
labels=['dev-smoke-opt-profile1-attempt2','dev-guard-profile0-a','dev-guard-profile1-a','dev-guard-profile1-b','dev-guard-profile0-b','dev-frozen-phase2-history'];rows=[]
for label in labels:
 e=load(C/'raw'/label/'episode.json');assert e['valid'];rows.append(e)
pairs=[]
for off,on in [(rows[1],rows[2]),(rows[4],rows[3])]:
 pairs.append({'off':off['label'],'on':on['label'],'decode_change_pct':100*(on['run']['decode_s']/off['run']['decode_s']-1),'wall_change_pct':100*(on['run']['wall_s']/off['run']['wall_s']-1)})
gate=not all(x['decode_change_pct']>3 for x in pairs)
# The instrumented smoke must reach every routed plan dependency on both devices.
wait=(C/'raw'/labels[0]/'raw/run-engine.log').read_text();w=re.findall(r'Q4_WAIT_END device=(\d+) plan_ns=(\d+) plan_count=(\d+) mapped_ns=(\d+) mapped_count=(\d+) cpu_ns=(\d+) cpu_count=(\d+)',wait);assert len(w)==2
assert all(int(x[2])==24*rows[0]['run']['verify_windows'] for x in w),w
result={'state':'PASS' if gate else 'PROFILE_GATE_REQUIRED','instrumentation_pairs':pairs,'headline_profile_enabled':gate,'frozen_binary_check':'Both frozen Phase2 and new OFF pass exact tape/work/initial-state, physical publication/ownership validation; exact deterministic inherited parity proven separately on 16 task/scorer points. Live scheduling readiness is asynchronous.','frozen_phase2_decode_s':rows[5]['run']['decode_s'],'new_unprofiled_OFF_decode_s':[rows[i]['run']['decode_s'] for i in [1,4]],'wait_coverage':w,'rows':[{'label':x['label'],'valid':x['valid'],'decode_s':x['run']['decode_s'],'wall_s':x['run']['wall_s'],'operating_s':x['total_operating_s']} for x in rows]}
save(C/'tests/development-guard.json',result);print(json.dumps(result,indent=2));assert gate,'Reduce/gate instrumentation before headline'
