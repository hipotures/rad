"""Independently verify completed long requests without touching live inference."""
from pathlib import Path
import json,time,sys
R=Path(__file__).resolve().parent
rows=[]
incomplete=[]
int8='--int8-validation' in sys.argv
for tag,target,count in [('64K-4096-sampled',63400,4096),('128K-4096-sampled',127000,4096),('128K-8192-sampled',127000,8192)]:
    name=('LONG-INT8-v0132-' if int8 else 'LONG-FINAL-v0132-')+tag
    path=R/'raw'/f'{name}.json'
    if not path.exists():continue
    d=json.loads(path.read_text())
    # The first atomic raw save precedes final enrichment. Never audit that intermediate record.
    if not d.get('acceptance_trace_file'):continue
    req=json.loads((R/'raw'/f'{name}-request.json').read_text())
    trace=json.loads(Path(d['acceptance_trace_file']).read_text())
    assert d['status']=='OK' and not d.get('abort') and d['min_mem_available_gib']>=12
    assert d['actual_prompt_tokens']==d['actual_prompt_tokens_tokenizer']==d['usage']['prompt_tokens']
    assert abs(d['actual_prompt_tokens']-target)<=8
    assert d['generated_tokens']==d['usage']['completion_tokens'] and req['max_tokens']==count
    if d['generated_tokens']!=count:
        incomplete.append({'raw':str(path),'requested':count,'actual':d['generated_tokens'],'reason':'Natural short output; not a full-length result','retained':True})
        if int8:continue
        retry=R/'raw/LONG-RETRY8K-v0132-128K-8192-sampled.json'
        if not retry.exists():continue
        path=retry;name=retry.stem;d=json.loads(path.read_text())
        if not d.get('acceptance_trace_file'):continue
        req=json.loads((R/'raw'/f'{name}-request.json').read_text());trace=json.loads(Path(d['acceptance_trace_file']).read_text())
        assert d['status']=='OK' and not d.get('abort') and d['min_mem_available_gib']>=12
        assert d['actual_prompt_tokens']==d['actual_prompt_tokens_tokenizer']==d['usage']['prompt_tokens'] and abs(d['actual_prompt_tokens']-target)<=8
        assert d['generated_tokens']==d['usage']['completion_tokens']==req['max_tokens']==count
    assert d['cache_reused_tokens']==0
    assert req['temperature']==1 and req['top_p']==.95 and req['top_k']==20
    assert d['Strata_HEAD']=='c499bd102e7a4135c0de389dcfe38c399759ccc8'
    assert d['model_revision']=='38bb39ee97821de2c9009abb7e93950eec396e66'
    assert d['build_variant']=='default' and d['Strata_version']=='0.1.32'
    cfg=d['full_config'];args=cfg['args']
    assert cfg['gpu']==[0,1] and cfg['layer_split']=='24' and cfg['env']['STRATA_TRACE']=='1'
    assert args[args.index('--kv')+1]==('int8' if int8 else 'k8v4') and args[args.index('--max-context')+1]=='262144'
    assert 'No tools are available. Answer directly using only the supplied repository excerpts.' in req['messages'][0]['content']
    assert trace['status']=='VERIFIED_AGAINST_REQUEST_END_COUNTERS'
    assert trace['draft_offered']==d['draft_tokens'] and trace['draft_accepted']==d['accepted_tokens']
    assert trace['verify_windows']==d['verify_rounds'] and trace['generated_tokens']==count
    samples=[json.loads(x) for x in Path(d['telemetry_file']).read_text().splitlines()]
    start=samples[0]['wall_time']-(samples[0]['monotonic']-d['t_start_monotonic_s'])
    end=start+d['total_wall_s']
    assert all(x['pss_sample_wall']<start for x in d['pss_before'].values())
    assert all(x['pss_sample_wall']>=end for x in d['pss_after'].values())
    for sample in samples:
        for proc in sample.get('processes',[]):
            if proc.get('pss_sample_wall') is not None:
                assert proc['pss_sample_wall']==d['pss_before'][str(proc['pid'])]['pss_sample_wall']
    rows.append({'raw':str(path),'actual_prompt_tokens':d['actual_prompt_tokens'],'generated_tokens':count,'PP':d['pp_tps'],'TG':d['tg_tps'],'TTFT':d['ttft_s'],'expert_tiers':d['expert_tiers'],'normal_trace':d['acceptance_trace_file']})
out={'status':'VERIFIED_COMPLETED_LONG_REQUESTS_ONLY','observed_at':time.time(),'requests':rows,'incomplete_attempts':incomplete,'completed_count':len(rows),'required_count':3,'scope':'Completed enriched records only. Trace overhead included; combined MTP/suffix acceptance. Logical expert file fetch counters do not prove physical host SSD activity. API/tokenizer counts, sampling, runtime/model/config, RAM safety, trace aggregate and PSS timing independently checked.'}
(R/'evidence'/('long-int8-validation-independent-audit.json' if int8 else 'long-progress-independent-audit.json')).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
