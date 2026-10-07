from agent_identity import agent_label
from final_identity import final_label
"""Offline figures from actual requests; run after assemble-summary.py and engines stop."""
from pathlib import Path
import json,csv,statistics,math,re,hashlib,time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parent;P=R/'plots'
def load(p):return json.loads(Path(p).read_text())
def med(v):return statistics.median([x for x in v if isinstance(x,(int,float))])
def finish(fig,name):
    fig.tight_layout();fig.savefig(P/(name+'.png'),dpi=160);fig.savefig(P/(name+'.svg'));plt.close(fig)
def axis():return plt.subplots(figsize=(8.5,5))
def samples(row):
    record=load(row['raw_result']);return [json.loads(x) for x in Path(record['telemetry_file']).read_text().splitlines() if x.strip()]

def main():
    summary=load(R/'summary.json');rows=summary['records'];P.mkdir(exist_ok=True)
    final=[x for x in rows if x['candidate']==final_label() and x['kind']=='candidate'];assert len(final)==12
    plt.rcParams.update({'axes.grid':True,'grid.alpha':.25,'font.size':10})
    for name,key,title,unit in [('01-context-TG','TG_tps','Decode vs actual prompt context','tokens/s'),('02-context-PP','PP_tps','Prefill vs actual prompt context','tokens/s'),('03-context-TTFT','TTFT_s','TTFT vs actual prompt context','s'),('04-context-RAM','RAM_used_GiB','Peak RAM use vs actual prompt context','GiB (MemTotal minus MemAvailable)')]:
        f,a=axis()
        for label,rr in [('Q4 FINAL v0.1.32',final),('IQ3_S v0.1.32 controls',[x for x in rows if x['candidate']=='IQ3-upgrade-control' and x['kind']=='candidate'])]:
            if not rr:continue
            targets=sorted(set(round(x['actual_prompt_tokens']/100)*100 for x in rr));groups=[[x[key] for x in rr if abs(x['actual_prompt_tokens']-t)<9] for t in targets];middle=[med(v) for v in groups]
            a.errorbar([t/1000 for t in targets],middle,yerr=[[m-min(g) for m,g in zip(middle,groups)],[max(g)-m for m,g in zip(middle,groups)]],fmt='o-',capsize=3,label=label+' median/range')
        a.set(xlabel='Actual prompt tokens (thousands)',ylabel=unit,title=title);a.legend();finish(f,name)
    f,a=axis();comparison=load(R/'comparison-pp-control.json')['rows']
    for version in ['v0131','v0132']:
        points=comparison;a.plot([statistics.median(x['actual_tokens_'+version])/1000 for x in points],[x['pp_tps'][version] for x in points],'o-',label=version)
    a.set(xlabel='Actual prompt tokens (thousands)',ylabel='PP tokens/s',title='Controlled whole-version A/B; identical paired payloads');a.legend();finish(f,'05-controlled-version-PP')
    f,a=axis();rr=[x for x in rows if re.fullmatch(r'SPLIT-K\d+-screen-v0132',x['candidate'] or '')];rr.sort(key=lambda x:int(x['layer_split']));a.plot([int(x['layer_split']) for x in rr],[x['TG_tps'] for x in rr],'o-',label='One screening request')
    confirmations=[x for x in rows if re.fullmatch(r'SPLIT-K\d+-confirm-v0132',x['candidate'] or '') and x['kind']=='candidate']
    for k in sorted(set(x['layer_split'] for x in confirmations)):
        v=[x['TG_tps'] for x in confirmations if x['layer_split']==k];a.errorbar(int(k),med(v),yerr=[[med(v)-min(v)],[max(v)-med(v)]],fmt='s',color='tab:orange')
    a.set(xlabel='First GPU1 layer K',ylabel='TG tokens/s',title='Layer split screening and TOP2 confirmations');finish(f,'06-layer-split')
    f,a=axis();selection=load(R/'raw/prefill-selection.json')
    # Standalone request names remain the data source; aggregate keys vary by phase.
    rr=[x for x in rows if re.fullmatch(r'PREFILL-.*-screen',x['candidate'] or '') and x['kind']=='candidate']
    a.bar([str(x['prefill_chunk_argument']) for x in rr],[x['PP_tps'] for x in rr]);a.set(xlabel='Requested prefill policy (resolved size in allocation evidence)',ylabel='PP tokens/s',title='Actual127K prefill screening');finish(f,'07-prefill')
    for group in ['workers','pcie','minp']:
        f,a=axis();rr=[x for x in rows if re.fullmatch(r'CAL-'+group+r'-.*-screen',x['candidate'] or '') and x['kind']=='candidate'];rr.sort(key=lambda x:float(x['candidate'].split('-')[2]));a.plot([float(x['candidate'].split('-')[2]) for x in rr],[x['TG_tps'] for x in rr],'o-');a.set(xlabel=group,ylabel='TG tokens/s',title='Sequential actual64K '+group+' screening (other settings recorded)');finish(f,'08-calibration-'+group)
    for name,key,title in [('09-MTP-TG','TG_tps','MTP spec length; actual64K / 1024 output'),('10-MTP-acceptance','MTP_accept','Normal draft acceptance; MTP plus suffix lookup')]:
        f,a=axis();rr=[x for x in rows if re.fullmatch(r'MTP-spec\d+-screen-v0132',x['candidate'] or '') and x['kind']=='candidate']
        for spec in sorted(set(int(x['spec']) for x in rr)):
            v=[x[key] for x in rr if int(x['spec'])==spec];a.errorbar(spec,med(v),yerr=[[med(v)-min(v)],[max(v)-med(v)]],fmt='o',capsize=3)
        a.set(xlabel='Spec length (OFF unsupported for this native runtime)',ylabel='tokens/s' if key=='TG_tps' else '%',title=title);finish(f,name)
    f,a=axis()
    for target in [127000,259500]:
        rr=[x for x in rows if (x['candidate'] or '').startswith('KV-') and (x['candidate'] or '').endswith('-screen') and x['kind']=='candidate' and abs(x['actual_prompt_tokens']-target)<9]
        labels=sorted(set(x['candidate'].split(f'-{target}')[0].replace('KV-','') for x in rr));values=[med([x['TG_tps'] for x in rr if x['candidate'].startswith('KV-'+label+'-'+str(target))]) for label in labels];a.plot(labels,values,'o-',label=str(target)+' actual')
    a.set(ylabel='TG tokens/s',title='Legal KV candidates; rotated INT8 separately labelled');a.legend();finish(f,'11-KV')
    representative=next(x for x in final if abs(x['actual_prompt_tokens']-127000)<9)
    ss=samples(representative);f,axes=plt.subplots(3,1,figsize=(9,8),sharex=True);base=ss[0]['monotonic'];ts=[s['monotonic']-base for s in ss]
    for gpu in [0,1]:
        gs=[next((g for g in s.get('gpus',[]) if g['index']==gpu),{}) for s in ss];axes[0].plot(ts,[g.get('util_pct',math.nan) for g in gs],label=f'GPU{gpu}');axes[1].plot(ts,[g.get('power_w',math.nan) for g in gs],label=f'GPU{gpu}')
    axes[2].plot(ts,[sum(p['cpu_pct'] for p in s.get('processes',[])) for s in ss],label='Process CPU (100% per CPU thread)');axes[0].set(ylabel='GPU utilization %',title='Representative actual128K request: '+Path(representative['raw_result']).stem);axes[1].set(ylabel='GPU power W');axes[2].set(ylabel='CPU %',xlabel='Request sampled wall time (s)')
    for a in axes:a.legend()
    finish(f,'12-representative-128K-resources')
    selected_long=json.loads((R/'raw/long-decode-done.json').read_text())['runs']
    selected_stems={Path(x['acceptance_trace_file']).name.removesuffix('-acceptance-trace.json') for x in selected_long}
    longs=[x for x in rows if Path(x['raw_result']).stem in selected_stems and x['Strata_version']=='0.1.32'];assert len(longs)==3
    f,a=axis()
    for row in longs:
        points=[s.get('metrics',{}).get('live',{}) for s in samples(row)];points=[p for p in points if p.get('generated') and isinstance(p.get('tok_s'),(int,float))]
        if points:
            line=a.plot([p['generated'] for p in points],[p['tok_s'] for p in points],label=Path(row['raw_result']).stem+' rolling')[0]
            means=[p for p in points if isinstance(p.get('tok_s_mean'),(int,float))];a.plot([p['generated'] for p in means],[p['tok_s_mean'] for p in means],'--',color=line.get_color(),label=Path(row['raw_result']).stem+' cumulative')
    a.set(xlabel='Live generated tokens (1Hz)',ylabel='TG tokens/s',title='Long decode rolling and cumulative TG');a.legend(fontsize=6);finish(f,'13-long-TG')
    f,a=axis()
    for row in longs:
        rec=load(row['raw_result']);trace=load(rec['acceptance_trace_file']);assert trace['status']=='VERIFIED_AGAINST_REQUEST_END_COUNTERS';points=[x for x in trace['rows'] if x['cumulative_acceptance_pct'] is not None];a.plot([p['generated_token_index'] for p in points],[p['cumulative_acceptance_pct'] for p in points],label=Path(row['raw_result']).stem)
    a.set(xlabel='Generated tokens (verify-window trace)',ylabel='Cumulative accepted drafts %',title='Normal MTP plus suffix lookup acceptance');a.legend(fontsize=6);finish(f,'14-long-acceptance')
    f,a=axis()
    for row in longs:a.scatter(row['output_tokens'],row['combined_hit_percent'],label=Path(row['raw_result']).stem)
    a.set(xlabel='Generated tokens',ylabel='Normal cache hit % (GPU cache + CPU denominator)',title='Request-end hit ratio; excludes PCIe/remote entries' );a.legend(fontsize=6);finish(f,'15-long-expert-hits')
    for name,key,title,unit in [('16-agent-TTFT','TTFT_s','Agentic TTFT by turn','s'),('17-agent-incremental-PP','PP_tps','Agentic incremental prefill by turn','new tokens/s'),('18-agent-wall','wall_s','Agentic request wall time by turn','s')]:
        f,a=axis()
        for target in [63400,127000]:
            rr=[x for x in rows if x['candidate']==agent_label(target) and x['kind']=='agentic'];assert len(rr)==11;rr.sort(key=lambda x:int(re.search(r'turn(\d+)$',Path(x['raw_result']).stem)[1]));a.plot(range(11),[x[key] for x in rr],'o-',label=f'start{target}')
        a.set(xlabel='Turn (0 initial, 1–10 with ordinary prefix reuse)',ylabel=unit,title=title);a.legend();finish(f,name)
    f,a=axis();rr=[x for x in rows if x['kind']=='compaction'];a.bar([x['Strata_version']+' / '+str(x['actual_prompt_tokens']) for x in rr],[x['wall_s'] for x in rr]);a.set(ylabel='Total wall s',title='Real recorded history compaction; different configs NOT_CONTROLLED_A_B');finish(f,'19-compaction')
    manifest={'created':time.time(),'summary_SHA256':hashlib.sha256((R/'summary.json').read_bytes()).hexdigest(),'files':{p.name:{'bytes':p.stat().st_size,'SHA256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in P.iterdir() if p.suffix in ['.png','.svg']},'limitations':'Error bars are observed ranges, not confidence intervals. Instrumented long-run timings include trace overhead. Resources do not measure routed expert share. Request-end hit rate is not a time-resolved curve. Null unavailable values are never plotted as zero.'}
    (P/'source-manifest.json').write_text(json.dumps(manifest,indent=2));print('Figures saved; visual inspection and final audit still required.')

if __name__=='__main__':main()
