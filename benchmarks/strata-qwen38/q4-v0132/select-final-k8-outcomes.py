"""Select tested speedwinner while explicitly preserving negative agentic length outcomes."""
from pathlib import Path
import json,time,psutil
R=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text())
assert not (R/'production-selection.json').exists()
for p in psutil.process_iter(['cmdline']):
    c=p.info['cmdline'] or []
    assert not(c and c[0] in ['/srv/ai/strata-v0.1.32/build-default/strata','/srv/ai/strata/build/strata'])
a=load(R/'evidence/agent-natural-outcomes-independent-audit.json')
assert {x['target'] for x in a['sessions']}=={63400,127000} and all(x['completed_turns']==11 and x['full_history_verified'] for x in a['sessions'])
matrix=load(R/'evidence/final-matrix-progress-independent-audit.json');assert len(matrix['cells'])==4 and all(x['n']==3 for x in matrix['cells'])
assert load(R/'evidence/long-progress-independent-audit.json')['completed_count']==3
term=R/'raw/phase-agent128-natural-outcomes-terminal.json';assert load(term)['status'] in ['COMPLETE','MEASURED_WITH_SHORT_TURNS']
selected={'status':'SELECTED_FROM_VERIFIED_EVIDENCE','created':time.time(),'matrix_label':'FINAL-v0132-Q4-attempt2','config':str(R/'configs/FINAL-v0132-Q4.json'),'long_summary':str(R/'raw/long-decode-done.json'),'agent_labels':{'63400':'AGENT-63400-v0132','127000':'AGENT-127000-v0132-natural-eos-session'},'phase_terminals':{'agent128':str(term)},'accepted_phase_statuses':{'agent128':['COMPLETE','MEASURED_WITH_SHORT_TURNS']},'classification':'TESTED_K8V4_SPEED_FINALIST_WITH_NEGATIVE_LENGTH_OUTCOMES','rationale':'K8V4 won confirmed speedselection and completed finalmatrix/long lengths. Full11-request128K lifecycle now measured, recording any below256 naturalEOS as negative outputlength outcomes without masking, suppression, or process restart. INT8 fullmatrix/long and agentdiagnostics preserved separately: agent64 short235; no proof of increased stability or quality. This selection is not a claim of universal correctness or suitability; literal qualityparity and downstreamworkloads remain required.','controlled_AB':False,'agentic_output_minimum_met':not a['incomplete_attempts'],'negative_output_outcomes':a['incomplete_attempts'],'INT8_not_promoted':str(R/'evidence/int8-agent64-short-review.json'),'retained_original_manifests':['final-matrix-attempt.json','agent-attempts.json'],'evidence':[str(R/'evidence'/x) for x in ['final-matrix-progress-independent-audit.json','long-progress-independent-audit.json','agent-natural-outcomes-independent-audit.json','int8-agent64-short-review.json']]}
(R/'production-selection.json').write_text(json.dumps(selected,indent=2)+'\n')
s=load(R/'STATUS.json');s['running']=None;s['current_winners']['final']={'config':selected['config'],'kv':'k8v4','selection':str(R/'production-selection.json'),'classification':selected['classification']};s['completed'].append('Full11-turn agent128 lifecycle measured with naturalEOS negatives disclosed; INT8notpromoted');s['pending']=[x for x in s['pending'] if not x.startswith('agentic11turn')];s['next_exact_action']='Compaction128/250K from fullactualhistories, exactoldruntime control, qualityparity, needle andIQ3, then diagnostics/plots/report/independentaudit.';(R/'STATUS.json').write_text(json.dumps(s,indent=2)+'\n')
print('K8V4 speedfinalist retained; allnegativeoutcomes explicit, previous artifacts untouched.')
