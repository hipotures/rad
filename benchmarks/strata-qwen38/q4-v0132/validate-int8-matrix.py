"""Separate final INT8 candidate validation; preserve every K8V4 artifact."""
import json,time,statistics
import run as r
R=r.ROOT;label='FINAL-v0132-Q4-INT8-stability'
cfg=json.loads((R/'configs'/f'{label}.json').read_text())
assert cfg['args'][cfg['args'].index('--kv')+1]=='int8'
assert cfg['gpu']==[0,1] and cfg['layer_split']=='24'
assert not list((R/'raw').glob(label+'-ctx*-request.json')),'Preserve/review partial validation before restart'
review=json.loads((R/'evidence/agent-KV-stability-review.json').read_text())
assert review['INT8']['status']=='COMPLETE_11_REQUESTS'
state=json.loads((R/'STATUS.json').read_text());state['running']={'phase':'INT8 final candidate matrix','candidate':label};state['next_exact_action']='Finish separate actual32/64/128/256K n3 INT8 validation; compare stability evidence before production selection.';r.c.save(R/'STATUS.json',state)
rows=[];cells=[]
with r.Session(label,cfg) as session:
    smoke=session.request(8000,64,'smoke','smoke');assert smoke['text'].strip() and smoke['draft_tokens']>0
    for target in [31400,63400,127000,259500]:
        session.request(target,256,f'ctx{target}-warmup','warmup')
        cell=[]
        for repeat in range(1,4):
            row=session.request(target,256,f'ctx{target}-run{repeat}')
            assert abs(row['actual_prompt_tokens']-target)<=8 and row['actual_prompt_tokens']==row['actual_prompt_tokens_tokenizer']
            assert row['generated_tokens']==256 and row['cache_reused_tokens']==0 and not row.get('abort')
            cell.append(row);rows.append(row)
        cells.append({'target':target,'actual_prompt_tokens':statistics.median(x['actual_prompt_tokens'] for x in cell),'PP':statistics.median(x['pp_tps'] for x in cell),'TG':statistics.median(x['tg_tps'] for x in cell),'TTFT':statistics.median(x['ttft_s'] for x in cell),'runs':cell})
r.c.save(R/'raw/int8-final-matrix-summary.json',{'status':'COMPLETE','config':str(R/'configs'/f'{label}.json'),'runs':rows,'cells':cells,'classification':'INT8_CANDIDATE_AFTER_OBSERVED_K8V4_AGENT_SHORT_OUTPUTS_CAUSALITY_UNPROVEN'})
r.c.save(R/'raw/phase-int8-final-matrix-terminal.json',{'status':'COMPLETE','ended':time.time(),'measured_requests':12,'config':str(R/'configs'/f'{label}.json')})
print('Separate INT8 matrix complete; independent validation and final decision remain.',flush=True)
