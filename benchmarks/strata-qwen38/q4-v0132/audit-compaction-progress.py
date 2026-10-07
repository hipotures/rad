"""Positive compaction evidence: actual payloads, history provenance, clocks and runtime."""
from pathlib import Path
import json,time
from agent_identity import agent_label
from final_identity import final_config_path
R=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text())
rows=[]
for target in [127000,250000]:
    name=f'COMPACTION-FINAL-v0132-{target}';path=R/'raw'/f'{name}.json'
    if not path.exists():continue
    d=load(path)
    if not d.get('history_sources'):continue # enrichment occurs after request clocks and PSS snapshots
    req=load(R/'raw'/f'{name}-request.json')
    assert d['status']=='OK' and not d.get('abort') and d['min_mem_available_gib']>=12
    assert d['actual_prompt_tokens']==d['actual_prompt_tokens_tokenizer']==d['usage']['prompt_tokens'] and abs(d['actual_prompt_tokens']-target)<=8
    assert 0<d['generated_tokens']<=4096 and d['generated_tokens']==d['usage']['completion_tokens']
    assert req['max_tokens']==4096 and req['temperature']==0 and d['cache_reused_tokens']==0
    assert (d['Strata_HEAD'],d['Strata_version'],d['build_variant'],d['model_revision'])==('c499bd102e7a4135c0de389dcfe38c399759ccc8','0.1.32','default','38bb39ee97821de2c9009abb7e93950eec396e66')
    cfg=d['full_config'];selected=load(final_config_path())
    assert cfg['args']==selected['args'] and cfg['gpu']==[0,1] and cfg['layer_split']==selected['layer_split']
    assert all(Path(source).exists() for source in d['history_sources'])
    for start in [63400,127000]:
        history=R/'raw'/f'{agent_label(start)}-history.json'
        assert str(history) in d['history_sources'] and len(load(history))==23
    assembly=load(R/'raw/compaction-source-assembly.json')
    assert assembly['sources']==d['history_sources']
    content=req['messages'][-1]['content']
    assert 'RECENT RECORDED TOOL OUTPUTS, DECISIONS AND REVIEWS (complete records)' in content
    # Every actual assistant answer and shorttool/historyrecord is included unmodified.
    assistant_count=0;complete_records=0;actual_records=[]
    for source_name in assembly['sources']:
        source=Path(source_name)
        if source.suffix=='.txt':messages=[{'role':'assistant','content':source.read_text()}]
        else:
            value=load(source);messages=value if isinstance(value,list) else value['messages']
        actual_records.extend((source_name,msg['role'],msg['content']) for msg in messages)
    assert len(actual_records)==len(assembly['records'])
    for item,(source_name,role,text) in zip(assembly['records'],actual_records):
        assert item['source']==source_name and item['role']==role
        if item['repository_reservoir']:
            assert role!='assistant' and item['content_tokens']>8192
            continue
        assert text in content,source_name+' missing exactcomplete record'
        complete_records+=1;assistant_count+=role=='assistant'
    assert assistant_count>=22
    samples=[json.loads(x) for x in Path(d['telemetry_file']).read_text().splitlines()];assert samples
    start=samples[0]['wall_time']-(samples[0]['monotonic']-d['t_start_monotonic_s']);end=start+d['total_wall_s']
    assert all(x['pss_sample_wall']<start for x in d['pss_before'].values()) and all(x['pss_sample_wall']>=end for x in d['pss_after'].values())
    for sample in samples:
        for proc in sample.get('processes',[]):
            if proc.get('pss_sample_wall') is not None:assert proc['pss_sample_wall']==d['pss_before'][str(proc['pid'])]['pss_sample_wall']
    entry={'raw':str(path),'actual_prompt_tokens':d['actual_prompt_tokens'],'generated_tokens':d['generated_tokens'],'PP':d['pp_tps'],'TG':d['tg_tps'],'TTFT':d['ttft_s'],'wall':d['total_wall_s'],'complete_history_records_checked':complete_records,'actual_assistant_records_checked':assistant_count}
    oldpath=R/'controls/v0131-compaction/raw'/f'COMPACTION-v0131-control-{target}.json'
    if oldpath.exists():
        old=load(oldpath)
        if old.get('comparison_request_source'):
            oldreq=load(oldpath.with_name(oldpath.stem+'-request.json'))
            assert oldreq==req and old['Strata_HEAD']=='9259cad4cfa3543cd3b8decab5962672b968c649' and old['Strata_version']=='0.1.31'
            assert old['actual_prompt_tokens']==d['actual_prompt_tokens'] and 0<old['generated_tokens']<=4096
            assert old['status']=='OK' and not old.get('abort') and old['min_mem_available_gib']>=12
            entry['old_exact_payload_control']=str(oldpath)
    rows.append(entry)
result={'status':'VERIFIED_COMPLETED_COMPACTION_REQUESTS_ONLY','created':time.time(),'rows':rows,'verified_requests':len(rows),'required_requests':2,'scope':'Saved actual transcripts and unchanged complete assistant/toolrecords; only older large repo reservoir sized. Actual API/tokenizer/usage equality, greedy/cap/reuse/identity/config, safety/PSSoutside clocks. Oldcontrol exactpayload consistency checked when present; configs differ and remainNOT_CONTROLLED_A_B. No summaryqualityjudgment.'}
(R/'evidence/compaction-progress-independent-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
