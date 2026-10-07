"""Verify completed enriched agent turns; leave live requests untouched."""
from pathlib import Path
import json,time,statistics
R=Path(__file__).resolve().parent
sessions=[]
for target in [63400,127000]:
    label=f'AGENT-{target}-v0132';rows=[];previous=None
    for turn in range(11):
        name=f'{label}-turn{turn}';path=R/'raw'/f'{name}.json'
        if not path.exists():break
        row=json.loads(path.read_text())
        if row.get('turn')!=turn:break
        request=json.loads((R/'raw'/f'{name}-request.json').read_text());messages=request['messages']
        assert row['status']=='OK' and not row.get('abort') and row['min_mem_available_gib']>=12
        assert row['actual_prompt_tokens']==row['actual_prompt_tokens_tokenizer']==row['usage']['prompt_tokens']
        assert row['generated_tokens']==row['usage']['completion_tokens']
        assert request['max_tokens']==1024 and request['temperature']==1 and request['top_p']==.95 and request['top_k']==20
        assert row['Strata_HEAD']=='c499bd102e7a4135c0de389dcfe38c399759ccc8' and row['Strata_version']=='0.1.32'
        assert row['model_revision']=='38bb39ee97821de2c9009abb7e93950eec396e66' and row['build_variant']=='default'
        cfg=row['full_config'];assert cfg['gpu']==[0,1] and cfg['layer_split']=='24'
        assert cfg['args'][cfg['args'].index('--kv')+1]=='k8v4'
        assert 'No tools are available. Answer directly using only the supplied repository excerpts.' in messages[0]['content']
        assert len(messages)==2+2*turn
        if turn==0:
            assert abs(row['actual_prompt_tokens']-target)<=8 and row['generated_tokens']==1024 and row['cache_reused_tokens']==0
        else:
            assert previous and messages[:-2]==previous['messages']
            assert messages[-2]=={'role':'assistant','content':previous['text']}
            assert messages[-1]['role']=='user' and row['tool_source_file'] in messages[-1]['content']
            assert 500<=row['new_tool_tokens']<=2000 and 256<=row['generated_tokens']<=1024
            assert row['cache_reused_tokens']>0 and row['existing_prefix_reused']==row['cache_reused_tokens']
            assert row['new_prompt_tokens_processed']==row['timings']['prompt_n']
        samples=[json.loads(x) for x in Path(row['telemetry_file']).read_text().splitlines()]
        start=samples[0]['wall_time']-(samples[0]['monotonic']-row['t_start_monotonic_s']);end=start+row['total_wall_s']
        assert all(x['pss_sample_wall']<start for x in row['pss_before'].values())
        assert all(x['pss_sample_wall']>=end for x in row['pss_after'].values())
        for sample in samples:
            for proc in sample.get('processes',[]):
                if proc.get('pss_sample_wall') is not None:assert proc['pss_sample_wall']==row['pss_before'][str(proc['pid'])]['pss_sample_wall']
        rows.append({'turn':turn,'raw':str(path),'actual_prompt_tokens':row['actual_prompt_tokens'],'generated_tokens':row['generated_tokens'],'reused':row['cache_reused_tokens'],'newly_processed':row['timings']['prompt_n'],'TTFT':row['ttft_s'],'TG':row['tg_tps']})
        previous={'messages':messages,'text':row['text']}
    history_verified=False
    if len(rows)==11:
        history=json.loads((R/'raw'/f'{label}-history.json').read_text())
        assert history==previous['messages']+[{'role':'assistant','content':previous['text']}]
        history_verified=True
    if rows:sessions.append({'target':target,'completed_turns':len(rows),'required_turns':11,'full_history_verified':history_verified,'turns':rows})
out={'status':'VERIFIED_COMPLETED_AGENT_TURNS_ONLY','observed_at':time.time(),'sessions':sessions,'scope':'Completed enriched records only. API/tokenizer count equality, sampling/identity/config, literal previous conversation prefix plus actual answer, ordinary reuse, recorded tool-token range, full final history when present, RAM safety and PSS outside request verified. Independent re-tokenization of tool texts remains part of offline final audit.'}
(R/'evidence/agent-progress-independent-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
