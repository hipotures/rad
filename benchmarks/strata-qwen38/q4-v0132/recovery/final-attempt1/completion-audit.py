"""Requirement-oriented offline audit; missing evidence is incomplete, never success."""
from pathlib import Path
import json,hashlib,subprocess,time,statistics

R=Path(__file__).resolve().parent
HEAD='c499bd102e7a4135c0de389dcfe38c399759ccc8'
checks=[]
def check(name,fn):
    try:
        evidence=fn();checks.append({'requirement':name,'status':'VERIFIED','evidence':evidence})
    except Exception as exc:checks.append({'requirement':name,'status':'INCOMPLETE_OR_CONTRADICTED','error':repr(exc)})
def load(p):return json.loads(Path(p).read_text())
def require(condition,note):
    assert condition,note
def terminal(name):
    p=R/'raw'/f'phase-{name}-terminal.json';require(load(p)['status']=='COMPLETE',str(p));return str(p)
def fixed(names,target,output):
    result=[];payloads=[]
    for name in names:
        p=R/'raw'/f'{name}.json';d=load(p);req=load(p.with_name(p.stem+'-request.json'))
        require(d['status']=='OK' and not d.get('abort'),str(p)+' status')
        require(d['actual_prompt_tokens']==d['actual_prompt_tokens_tokenizer'] and abs(d['actual_prompt_tokens']-target)<=8,str(p)+' actual occupancy')
        require(d['generated_tokens']==output and req['max_tokens']==output,str(p)+' actual generation')
        require(d['cache_reused_tokens']==0 and req['temperature']==0,str(p)+' greedy/no reuse')
        require(d['Strata_HEAD']==HEAD and d['Strata_version']=='0.1.32',str(p)+' runtime identity')
        expected_revision='ed59f92082b1e93c0e96d60a8b11aab089b52f09' if name.startswith('IQ3-upgrade-control-') else '38bb39ee97821de2c9009abb7e93950eec396e66'
        require(d['model_revision']==expected_revision and d['build_variant']=='default',str(p)+' model revision/build identity')
        require(d['usage']['prompt_tokens']==d['actual_prompt_tokens'] and d['usage']['completion_tokens']==output,str(p)+' API usage consistency')
        for key in ['build_variant','model_revision','topology','full_config','full_engine_command']:
            require(key in d,str(p)+' missing '+key)
        require(d['min_mem_available_gib']>=10,str(p)+' RAM safety')
        require(d.get('pss_note','').startswith(('smaps snapshots outside','Outside timed')),str(p)+' PSS timing')
        require(Path(d['telemetry_file']).is_file(),str(p)+' telemetry')
        seen={}
        for line in Path(d['telemetry_file']).read_text().splitlines():
            sample=json.loads(line)
            for proc in sample.get('processes',[]):
                if proc.get('pss_sample_wall') is not None:seen.setdefault(proc['pid'],set()).add(proc['pss_sample_wall'])
        require(all(len(stamps)<=1 for stamps in seen.values()),str(p)+' PSS refreshed during timed telemetry')
        samples=[json.loads(line) for line in Path(d['telemetry_file']).read_text().splitlines()]
        require(bool(samples),str(p)+' empty telemetry')
        wall_start=samples[0]['wall_time']-(samples[0]['monotonic']-d['t_start_monotonic_s'])
        wall_end=wall_start+d['total_wall_s']
        require(all(x['pss_sample_wall']<wall_start for x in d['pss_before'].values()),str(p)+' PSS before inside timer')
        require(all(x['pss_sample_wall']>=wall_end for x in d['pss_after'].values()),str(p)+' PSS after inside timer')
        require(all(stamps=={d['pss_before'][str(pid)]['pss_sample_wall']} for pid,stamps in seen.items()),str(p)+' PSS telemetry differs from before snapshot')
        payloads.append(hashlib.sha256(json.dumps(req,sort_keys=True).encode()).hexdigest());result.append(str(p))
    require(len(set(payloads))==len(payloads),'Duplicate performance payloads')
    return result
def preserved():
    old=R.parent/'q4-max-sweep';manifest=load(old/'V0131-PRESERVATION-MANIFEST.json')
    for item in manifest['files']:
        p=old/item['path'];s=p.stat();require(s.st_size==item['bytes'] and s.st_mtime_ns==item['mtime_ns'],'Old result modified: '+str(p))
    for item in load(R/'raw/model-provenance.json')['files']:
        p=Path(item['path']);s=p.stat();require((s.st_size,s.st_mtime_ns,s.st_ino)==(item['bytes'],item['mtime_ns'],item['inode']),'GGUF changed '+str(p))
    require(not Path('/srv/ai/models/strata/packs/ud-q4_k_xl-v0132/experts.bin').exists(),'Unexpected Q4 experts.bin')
    return {'old_files_unchanged':len(manifest['files']),'GGUF_stat_identity_unchanged':4,'checkpoint':str(old/'V0131-CHECKPOINT.json')}
def source():
    out={}
    for path,expected in [('/srv/ai/strata','9259cad4cfa3543cd3b8decab5962672b968c649'),('/srv/ai/strata-v0.1.32',HEAD)]:
        actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=path,text=True).strip();require(actual==expected,path+' HEAD')
        tracked=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=path,text=True);require(not tracked.strip(),path+' tracked source modified');out[path]={'HEAD':actual,'tracked_diff':tracked}
    require(subprocess.check_output(['git','rev-parse','v0.1.32^{commit}'],cwd='/srv/ai/strata-v0.1.32',text=True).strip()==HEAD,'Tag mismatch')
    return out
def quality():
    d=load(R/'raw/quality-parity-summary.json');require(d['status']=='COMPLETE','Quality incomplete');evidence=[]
    for variant in d['variants']:
        if variant['status']!='COMPLETE':
            require(variant['variant'] not in ['v0132-resident-default','v0132-layer-default','v0132-final'],'Required quality failed');continue
        require(len(variant['rows'])==3,'Three quality outputs missing')
        for entry in variant['rows']:
            key=entry['key'];folder=R/'quality'/variant['variant'];text=(folder/f'{key}.txt').read_bytes()
            require(hashlib.sha256(text).hexdigest()==entry['output_sha256'],'Quality hash mismatch')
            payload=load(R/'raw'/f"QUALITY-{variant['variant']}-{key}-request.json")
            require(payload==load(R/'quality/requests'/f'{key}.json'),'Quality request changed')
            require((folder/f'{key}.diff').exists(),'Quality text diff missing');evidence.append(str(folder/f'{key}.txt'))
    return evidence
def long():
    d=load(R/'raw/long-decode-done.json');require(len(d['runs'])==3,'Three long requests missing')
    for row,(target,count) in zip(d['runs'],[(63400,4096),(127000,4096),(127000,8192)]):
        require(abs(row['actual_prompt_tokens']-target)<=8 and row['generated_tokens']==count,'Long actual occupancy/count')
        require(row['sampling']=={'temperature':1.0,'top_p':.95,'top_k':20},'Long sampling changed')
        trace=load(row['acceptance_trace_file']);require(trace['status']=='VERIFIED_AGAINST_REQUEST_END_COUNTERS','Acceptance curve not verified')
        require(trace['draft_offered']==row['draft_tokens'] and trace['draft_accepted']==row['accepted_tokens'],'Acceptance totals')
    return terminal('long')
def agent(target):
    d=load(R/'raw'/f'AGENT-{target}-v0132-done.json');require(len(d['runs'])==11,'Agentic eleven requests missing');require(len(load(d['history']))==23,'Full agentic history missing')
    for i,row in enumerate(d['runs']):
        require(row['turn']==i,'Agentic turn order');require(row['generated_tokens']==1024 if i==0 else 256<=row['generated_tokens']<=1024,'Agentic output range')
        if i:require(row['cache_reused_tokens']>0 and 500<=row['new_tool_tokens']<=2000,'Agentic reuse/tool-token range')
        require(row['status']=='OK' and not row.get('abort'),'Agentic failed')
    return terminal('agent64' if target==63400 else 'agent128')
def artifacts():
    required=['environment.json','release-delta.md','STATUS.json','STATUS.md','summary.csv','summary.json','report.md','comparison-upgrade.csv','comparison-upgrade.json','comparison-upgrade.md','configs/production-Q4.json','configs/production-IQ3_S.json','plots/source-manifest.json']
    for name in required:require((R/name).is_file() and (R/name).stat().st_size>0,'Missing artifact '+name)
    report=(R/'report.md').read_text();require(all(re.search(r'^'+str(i)+r'\.',report,re.M) for i in range(1,21)),'Twenty final answers not present')
    plots=load(R/'plots/source-manifest.json');require(len([x for x in plots['files'] if x.endswith('.png')])>=19,'Final plot coverage')
    require((R/'evidence/plots-visual-review.json').exists(),'Rendered plots not inspected')
    return required

if __name__=='__main__':
    import re
    check('0–4 frozen old campaign / local model preservation',preserved)
    check('3 exact immutable runtime sources and tag',source)
    for phase in ['baseline','topology','pp-control','prefill','prompt-modes','placement','calibration','mtp','kv','final-matrix','long','agent64','agent128','compaction','quality','needle','iq3','diagnostics']:
        check('Phase terminal '+phase,lambda p=phase:terminal(p))
    check('7 single resident baseline n3',lambda:fixed([f'BASELINE-resident-v0132-run{i}' for i in range(1,4)],63400,256))
    for target in [31400,63400,127000,259500]:check('16 final context '+str(target)+' n3',lambda t=target:fixed([f'FINAL-v0132-Q4-ctx{t}-run{i}' for i in range(1,4)],t,256))
    check('17 actual long lengths / sampling / trace totals',long)
    for target in [63400,127000]:check('18 uninterrupted agentic '+str(target),lambda t=target:agent(t))
    check('20 exact greedy quality requests / full output hashes / diffs',quality)
    for target in [63400,259500]:check('22 IQ3 only required context '+str(target),lambda t=target:fixed([f'IQ3-upgrade-control-{t}-run{i}' for i in range(1,4)],t,256))
    check('21/26 final comparisons / artifacts / report / plots',artifacts)
    incomplete=[x for x in checks if x['status']!='VERIFIED'];result={'status':'INCOMPLETE' if incomplete else 'ALL_AUTOMATED_CHECKS_VERIFIED_REQUIRES_FINAL_HUMAN_REVIEW','created':time.time(),'checks':checks,'incomplete_count':len(incomplete),'scope':'Positive evidence required. Terminal markers alone are insufficient; fixed occupancy/output/reuse/config, histories, hashes, original preservation and final artifacts are separately checked. Final independent manual review must cover release-specific gates, screening/confirmation selection, unsupported evidence and report claims before marking goal achieved.'}
    (R/'completion-audit.json').write_text(json.dumps(result,indent=2));(R/'completion-audit.md').write_text('# Completion audit\n\n'+result['status']+'\n\n'+'\n'.join('- '+x['requirement']+': '+x['status']+(' — '+x.get('error','') if x['status']!='VERIFIED' else '') for x in checks)+'\n')
    print(result['status'],len(incomplete),'incomplete checks')
