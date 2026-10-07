"""Select practical INT8 finalist only after independent matrix/session/outcome proof."""
from pathlib import Path
import json,psutil,time
R=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text())
for proc in psutil.process_iter(['cmdline']):
    command=proc.info['cmdline'] or []
    assert not (command and command[0] in ['/srv/ai/strata-v0.1.32/build-default/strata','/srv/ai/strata/build/strata']),'Engine still active'
assert not (R/'production-selection.json').exists(),'Selection already exists; do not overwrite'
matrix=load(R/'evidence/int8-final-matrix-progress-independent-audit.json');assert matrix['measured_requests_verified']==12
agents=load(R/'evidence/agent-int8-validation-independent-audit.json')
assert {x['target'] for x in agents['sessions']}=={63400,127000}
assert all(x['completed_turns']==11 and x['full_history_verified'] for x in agents['sessions']),'Both complete11-turn INT8 sessions required'
assert load(R/'raw/phase-int8-agent64-terminal.json')['status']=='COMPLETE'
assert load(R/'raw/phase-agent128-int8-control-terminal.json')['status']=='COMPLETE'
long=load(R/'evidence/int8-long-outcomes-independent-audit.json')
assert len(long['requests'])==3 and long['fully_completed_lengths']==2
assert long['requests'][2]['actual_output']==6777 and long['requests'][2]['finish']=='stop'
for target,label in [(63400,'AGENT-63400-v0132-int8-validation'),(127000,'AGENT-127000-v0132-int8-control')]:
    d=load(R/'raw'/f'{label}-done.json');assert len(d['runs'])==11 and len(load(d['history']))==23
    assert all(x['generated_tokens']==1024 if i==0 else 256<=x['generated_tokens']<=1024 for i,x in enumerate(d['runs']))
    assert all(x['full_config']['args'][x['full_config']['args'].index('--kv')+1]=='int8' for x in d['runs'])
config=R/'configs/FINAL-v0132-Q4-INT8-stability.json';cfg=load(config)
assert cfg['args'][cfg['args'].index('--kv')+1]=='int8' and cfg['layer_split']=='24'
terminal=R/'raw/phase-int8-long-outcome-terminal.json'
assert not terminal.exists()
terminal.write_text(json.dumps({'status':'MEASURED_WITH_NATURAL_EOS','created':time.time(),'result':str(R/'raw/int8-long-decode-done.json'),'evidence':str(R/'evidence/int8-long-outcomes-independent-audit.json'),'required4K_cases_complete':2,'optional8K_actual':6777,'optional8K_requested':8192,'note':'Full8K INT8 outcome not achieved; allactual results retained, not relabelled as complete8192.'},indent=2)+'\n')
selection={'status':'SELECTED_FROM_VERIFIED_EVIDENCE','created':time.time(),'matrix_label':'FINAL-v0132-Q4-INT8-stability','config':str(config),'long_summary':str(R/'raw/int8-long-decode-done.json'),'agent_labels':{'63400':'AGENT-63400-v0132-int8-validation','127000':'AGENT-127000-v0132-int8-control'},'phase_terminals':{'final-matrix':str(R/'raw/phase-int8-final-matrix-terminal.json'),'long':str(terminal),'agent64':str(R/'raw/phase-int8-agent64-terminal.json'),'agent128':str(R/'raw/phase-agent128-int8-control-terminal.json')},'accepted_phase_statuses':{'long':['MEASURED_WITH_NATURAL_EOS']},'classification':'PRACTICAL_INT8_FINALIST_WITH_EXPLICIT_LIMITATIONS','rationale':'Full12-cell INT8 matrix and both11-turn agent sessions observed. K8V4 speed finalist retained; two128K sessions stopped below256 outputminimum. Single successful INT8 diagnostic128K plus64K validation supports this practical candidate, not KVcausality or universalstability. No qualitywinner inferred. BothINT8 required4K long cases complete; optional8K naturalEOS6777 retainednegative. K8V4 full8K remains separate.','controlled_AB':False,'quality_review':'Saved literal qualityresponses required downstream; no automatedqualityjudgment.','retained_K8V4':{'config':str(R/'configs/FINAL-v0132-Q4.json'),'matrix_label':'FINAL-v0132-Q4-attempt2','long_summary':str(R/'raw/long-decode-done.json'),'failed_agent_attempts':['AGENT-127000-v0132','AGENT-127000-v0132-attempt2']},'evidence':[str(R/'evidence'/x) for x in ['int8-final-matrix-progress-independent-audit.json','agent-int8-validation-independent-audit.json','int8-long-outcomes-independent-audit.json','agent-KV-stability-review.json']]}
(R/'production-selection.json').write_text(json.dumps(selection,indent=2)+'\n')
s=load(R/'STATUS.json');s['running']=None;s['current_winners']['final']={'config':str(config),'kv':'int8','classification':selection['classification'],'selection':str(R/'production-selection.json')};s['completed'].append('Practical INT8finalist selected from verifiedmatrix/bothagent sessions; optional8K naturalEOS reportedseparately');s['pending']=[x for x in s['pending'] if not x.startswith('agentic11turn')];s['next_exact_action']='Run compaction128/250K on selected actualhistories/config, then exactoldruntime control, quality, needle andIQ3; preserve allpriorK8V4results.';(R/'STATUS.json').write_text(json.dumps(s,indent=2)+'\n')
print('Selected separate INT8 finalist; old configs/manifests/raw untouched.')
