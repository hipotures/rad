"""Literal quality request/output integrity only; never score answer quality."""
from pathlib import Path
import json,hashlib,difflib,time
R=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text())
source=load(R/'quality/source-manifest.json');keys=[x['key'] for x in source['items']];results=[]
for done in sorted((R/'raw').glob('QUALITY-*-done.json')):
    summary=load(done);variant=summary['variant']
    if summary['status']!='COMPLETE':
        results.append({'variant':variant,'status':summary['status'],'evidence':str(done),'note':'Preservedfailedvariant; not completequalityparity'});continue
    assert len(summary['rows'])==3 and {x['key'] for x in summary['rows']}==set(keys)
    rows=[]
    for item in summary['rows']:
        key=item['key'];folder=R/'quality'/variant;name=f'QUALITY-{variant}-{key}'
        payload=load(R/'raw'/f'{name}-request.json');saved=load(R/'quality/requests'/f'{key}.json');row=load(R/'raw'/f'{name}.json')
        archived=load(folder/f'{key}.json')
        assert all(archived[k]==row[k] for k in archived), 'Qualityarchive differs from canonical enrichedrawresult'
        assert payload==saved and payload['temperature']==0
        original=next(x for x in source['items'] if x['key']==key)
        assert saved==load(original['request_source'])
        assert row['status']=='OK' and not row.get('abort') and row['min_mem_available_gib']>=12
        assert row['actual_prompt_tokens']==row['actual_prompt_tokens_tokenizer']==row['usage']['prompt_tokens']
        assert 0<row['generated_tokens']<=saved['max_tokens'] and row['generated_tokens']==row['usage']['completion_tokens']
        assert (row['Strata_HEAD'],row['Strata_version'],row['build_variant'],row['model_revision'])==('c499bd102e7a4135c0de389dcfe38c399759ccc8','0.1.32','default','38bb39ee97821de2c9009abb7e93950eec396e66')
        text=(folder/f'{key}.txt').read_text();assert text==row['text'] and hashlib.sha256(text.encode()).hexdigest()==item['output_sha256']
        assert hashlib.sha256((R/'raw'/f'{name}-request.json').read_bytes()).hexdigest()==item['request_sha256']
        ref=item['reference'];old=(R/'quality'/ref/f'{key}.txt').read_text()
        expected=''.join(difflib.unified_diff(old.splitlines(keepends=True),text.splitlines(keepends=True),fromfile=f'{ref}/{key}.txt',tofile=f'{variant}/{key}.txt'))
        assert (folder/f'{key}.diff').read_text()==expected and item['text_identical']==(old==text)
        full=load(folder/f'{key}-full-response.json');stream=load(full['raw_stream'])
        assert full['content']==text and full['reasoning']==row.get('reasoning','') and full['tool_call_events']==row.get('tool_call_events',[])
        assert stream['usage']==row['usage']
        assert (folder/f'{key}-reasoning.txt').read_text()==row.get('reasoning','')
        cfg=row['full_config'];mode=cfg['effective_experiment_environment']
        if variant=='v0132-layer-own':assert mode['STRATA_SPLIT_OWN']=='1'
        elif variant=='v0132-layer-rotated-int8':assert mode['STRATA_KV_ROT']=='1'
        else:assert mode['STRATA_SPLIT_OWN'] is None and mode['STRATA_KV_ROT'] is None
        samples=[json.loads(x) for x in Path(row['telemetry_file']).read_text().splitlines()];assert samples
        start=samples[0]['wall_time']-(samples[0]['monotonic']-row['t_start_monotonic_s']);end=start+row['total_wall_s']
        assert all(x['pss_sample_wall']<start for x in row['pss_before'].values()) and all(x['pss_sample_wall']>=end for x in row['pss_after'].values())
        for sample in samples:
            for proc in sample.get('processes',[]):
                if proc.get('pss_sample_wall') is not None:assert proc['pss_sample_wall']==row['pss_before'][str(proc['pid'])]['pss_sample_wall']
        rows.append({'key':key,'response':str(folder/f'{key}.txt'),'actual_output_tokens':row['generated_tokens'],'output_cap':saved['max_tokens'],'output_SHA256':item['output_sha256'],'reference':ref,'text_identical':item['text_identical'],'full_response':str(folder/f'{key}-full-response.json'),'scope':'Literalparity only, no judgment/score/ranking.'})
    results.append({'variant':variant,'status':'VERIFIED_COMPLETE_LITERAL_PARITY','rows':rows,'evidence':str(done)})
result={'status':'VERIFIED_COMPLETED_QUALITY_VARIANTS_ONLY','created':time.time(),'variants':results,'verified_variants':sum(x['status']=='VERIFIED_COMPLETE_LITERAL_PARITY' for x in results),'verified_responses':sum(len(x.get('rows',[])) for x in results),'scope':'Exactoriginalsavedrequests/system/sampling/caps; actualAPI/tokenizer/outputcount, fulltext/reasoning/toolcalls/streams, SHA256 and reconstructedliteraltextdiff, runtime/config/optin/RAM/PSSclocks. No LLMjudge or automaticqualityranking. Pending/livevariants not success.'}
(R/'evidence/quality-progress-independent-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
