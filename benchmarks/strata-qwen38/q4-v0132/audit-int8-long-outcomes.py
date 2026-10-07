"""Audit all INT8 long outcomes, explicitly retaining optional8K natural EOS."""
from pathlib import Path
import json,time
R=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text())
rows=[]
for tag,target,cap in [('64K-4096-sampled',63400,4096),('128K-4096-sampled',127000,4096),('128K-8192-sampled',127000,8192)]:
    name='LONG-INT8-v0132-'+tag;p=R/'raw'/f'{name}.json';d=load(p);req=load(R/'raw'/f'{name}-request.json');trace=load(d['acceptance_trace_file'])
    assert d['status']=='OK' and not d['abort'] and d['min_mem_available_gib']>=12
    assert d['actual_prompt_tokens']==d['actual_prompt_tokens_tokenizer']==d['usage']['prompt_tokens'] and abs(d['actual_prompt_tokens']-target)<=8
    count=d['generated_tokens'];assert count==d['usage']['completion_tokens'] and req['max_tokens']==cap
    assert count==cap if cap==4096 else 0<count<=cap
    assert d['cache_reused_tokens']==0 and d['sampling']=={'temperature':1.0,'top_p':.95,'top_k':20}
    assert all(req[k]==v for k,v in d['sampling'].items())
    assert (d['Strata_HEAD'],d['Strata_version'],d['build_variant'],d['model_revision'])==('c499bd102e7a4135c0de389dcfe38c399759ccc8','0.1.32','default','38bb39ee97821de2c9009abb7e93950eec396e66')
    cfg=d['full_config'];args=cfg['args'];assert cfg['gpu']==[0,1] and cfg['layer_split']=='24' and cfg['env']['STRATA_TRACE']=='1'
    assert args[args.index('--kv')+1]=='int8' and args[args.index('--max-context')+1]=='262144'
    assert 'No tools are available. Answer directly using only the supplied repository excerpts.' in req['messages'][0]['content']
    assert trace['status']=='VERIFIED_AGAINST_REQUEST_END_COUNTERS'
    assert (trace['draft_offered'],trace['draft_accepted'],trace['verify_windows'],trace['generated_tokens'])==(d['draft_tokens'],d['accepted_tokens'],d['verify_rounds'],count)
    matching=[x for x in load(R/'raw'/f'{name}-metrics.json')['requests'] if x['prompt_tokens']==d['actual_prompt_tokens'] and x['output_tokens']==count]
    assert len(matching)==1 and matching[0]['finish']==('length' if count==cap else 'stop')
    samples=[json.loads(x) for x in Path(d['telemetry_file']).read_text().splitlines()];assert samples
    start=samples[0]['wall_time']-(samples[0]['monotonic']-d['t_start_monotonic_s']);end=start+d['total_wall_s']
    assert all(x['pss_sample_wall']<start for x in d['pss_before'].values()) and all(x['pss_sample_wall']>=end for x in d['pss_after'].values())
    for sample in samples:
        for proc in sample.get('processes',[]):
            if proc.get('pss_sample_wall') is not None:assert proc['pss_sample_wall']==d['pss_before'][str(proc['pid'])]['pss_sample_wall']
    rows.append({'raw':str(p),'actual_prompt_tokens':d['actual_prompt_tokens'],'actual_output':count,'requested_output':cap,'finish':matching[0]['finish'],'full_requested_length':count==cap,'TG':d['tg_tps'],'expert_tiers':d['expert_tiers'],'trace':d['acceptance_trace_file']})
value={'status':'VERIFIED_MEASURED_OUTCOMES_WITH_OPTIONAL8K_NATURAL_EOS','created':time.time(),'requests':rows,'fully_completed_lengths':sum(x['full_requested_length'] for x in rows),'scope':'All3 outcomes independently verified, both mandatory4K cases full. Optional8K attempted once and stopped naturally at6777; no full8K INT8 claim, no retry/EOS suppression. K8V4 full8K remains separate.'}
(R/'evidence/int8-long-outcomes-independent-audit.json').write_text(json.dumps(value,indent=2)+'\n')
print(value['status'])
