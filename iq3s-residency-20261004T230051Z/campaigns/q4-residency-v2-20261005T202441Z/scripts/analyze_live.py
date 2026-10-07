"""Analyze retained live requests without inference, extra attempts, or fabricated counters."""
from campaign import C,load,save,status
from pathlib import Path
import csv,json,re,statistics,datetime

def stats(values):
    values=[x for x in values if isinstance(x,(int,float))]
    return dict(min=min(values),median=statistics.median(values),max=max(values),mean=statistics.mean(values)) if values else None

def phase_system(r):
    rows=[json.loads(line) for line in Path(r['telemetry']['path']).read_text().splitlines()]
    start=r['started_epoch'];first=start+r['TTFT_s'];end=start+r['wall_s'];out={}
    for name,lo,hi in [('prefill',start,first),('decode',first,end)]:
        selected=[row for row in rows if lo<=row['wall_time']<hi]
        cpu=[row for row in selected if row is not rows[0]]
        out[name]={'samples':len(selected),'CPU_VM_pct':stats([x['system_cpu_pct'] for x in cpu]),
            'CPU_process_one_core100':stats([sum(p['cpu_pct'] for p in x['processes']) for x in cpu]),
            'RAM_used_GiB':stats([x['ram_used_gib'] for x in selected]),
            'RAM_available_GiB':stats([x['mem_available_gib'] for x in selected]),
            'RSS_sum_GiB':stats([sum(p['rss_gib'] for p in x['processes']) for x in selected]),'GPUs':{}}
        for device in [0,1]:
            gpu=[g for row in selected for g in row.get('gpus',[]) if int(g['index'])==device]
            out[name]['GPUs'][str(device)]={key:stats([g[key] for g in gpu]) for key in ['util_pct','power_w','vram_mib','sm_mhz']}
    return out,rows

def progression(r,rows):
    samples=[]
    for row in rows:
        live=(row.get('metrics') or {}).get('live') or {}
        count=live.get('generated')
        if live.get('state')=='generating' and isinstance(count,int) and 0<count<r['actual_output_tokens']:
            samples.append({'time':row['wall_time']-r['started_epoch'],'tokens':count,
                'ui_2s_TG':live.get('tok_s'),'ui_cumulative_TG':live.get('tok_s_mean')})
    # These are sampled actual-ID counters, NOT one token per SSE message.
    # TTFT is an approximation to decode start, final wall includes cleanup.
    points=[(0,r['TTFT_s'])]+[(x['tokens'],x['time']) for x in samples]+[(r['actual_output_tokens'],r['wall_s'])]
    monotone=all(b[0]>=a[0] and b[1]>a[1] for a,b in zip(points,points[1:]))
    bounds=[0,512,1024,2048,4096]
    def cross(n):
        if n==0:return r['TTFT_s']
        if n==r['actual_output_tokens']:return r['wall_s']
        for (a,t),(b,u) in zip(points,points[1:]):
            if a<=n<=b and b>a:return t+(n-a)*(u-t)/(b-a)
        return None
    intervals=[]
    if monotone:
        for a,b in zip(bounds,bounds[1:]):
            t,u=cross(a),cross(b)
            intervals.append({'start':a,'end':b,'TG_estimate':(b-a)/(u-t) if t is not None and u is not None and u>t else None,
                'cumulative_TG_estimate':b/(u-r['TTFT_s']) if u is not None and u>r['TTFT_s'] else None})
    return {'method':'Linear interpolation of1Hz actual generated-ID counters; approximate TTFT origin and request-wall endpoint. Final interval includes cleanup. Not exact per-token/native-window timing.',
        'target_sampling_resolution_s':1,'max_observed_sample_gap_s':max((b['time']-a['time'] for a,b in zip(samples,samples[1:])),default=None),
        'monotone':monotone,'samples':samples,'intervals':intervals,
        'hit_rate_progression':None,'MTP_progression':None,'limitation':'Frozen speed counters for hits/MTP are request aggregates, not per-interval. Sampled aggregate PCIe cannot identify expert events or critical-path waits.'}

def counters(text):
    out={}
    for label in ['Q4_HISTORY','Q4_EARLY']:
        lines=[line for line in text.splitlines() if line.startswith(label+' ')]
        out[label]=({k:float(v) if '.' in v else int(v) for k,v in re.findall(r'(\w+)=([\d.]+)',lines[-1])} if lines else None)
    timing=next((line for line in text.splitlines() if line.startswith('strata decode timing:')),'')
    out['decode_timing_line']=timing
    patterns={'CPU_completion_ms':r' CPU ([\d.]+)\]', 'GPU_reach_wait_ms':r'GPU-reach wait ([\d.]+)',
        'window_ms':r'([\d.]+) ms/window','activation_quantization_ms':r'actq ([\d.]+)',
        'CPU_experts_per_layer_window':r'CPU experts ([\d.]+)','CPU_entries_per_layer_window':r'CPU experts [\d.]+ \(([\d.]+) entries\)'}
    out['native_timing']={key:float(m[1]) if (m:=re.search(pattern,timing)) else None for key,pattern in patterns.items()}
    out['CPU_positive_wait_ms']=None;out['all_local_wait_floor_ms']=None
    out['useful_promotions']=None;out['victim_damage_exclusive']=None
    out['note']='Exact useful/victim counters are diagnostic-only; unavailable clean headline counters remain null. Aggregate CPU completion wait is not an exclusive causal timer.'
    return out

def pcie_samples(base,r):
    path=base/'telemetry/pcie-dmon.log';samples=[]
    for line in path.read_text().splitlines():
        parts=line.split()
        if len(parts)!=5 or parts[0].startswith('#'):continue
        try:
            t=datetime.datetime.strptime(parts[0]+' '+parts[1],'%Y%m%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp()
            samples.append({'epoch':t,'device':int(parts[2]),'RX_MB_s':float(parts[3]),'TX_MB_s':float(parts[4])})
        except ValueError:continue
    start=r['started_epoch'];first=start+r['TTFT_s'];end=start+r['wall_s']
    out={'limitation':'Aggregate1Hz PCIe samples; not logical expert bytes, exact burst attribution, or evidence of saturation. Times have1s granularity.'}
    for phase,lo,hi in [('prefill',start,first),('decode',first,end)]:
        out[phase]={str(device):{key:stats([x[key] for x in samples if x['device']==device and lo<=x['epoch']<hi]) for key in ['RX_MB_s','TX_MB_s']} for device in [0,1]}
    return out

KEYS=['PP','TG','TTFT_s','wall_s','pp_s','decode_s','actual_input_tokens','actual_output_tokens','mtp_proposed','mtp_accepted','mtp_acceptance_pct','verify_windows','mtp_accepted_per_window','local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries','all_routed_entries','local_vram_share_all_pct']

def one(base):
    r=load(base/'raw/run.json');system,rows=phase_system(r)
    assert r.get('actual_engine_input_verified') and r.get('reuse')==0,'Actual IDs/reuse protocol mismatch: '+str(base)
    if r['state']=='VALID':
        assert r['actual_engine_output_ID_count']==r['actual_output_tokens']==len(load(r['actual_output_ids_path'])),'Output IDs/count mismatch: '+str(base)
    warm=load(base/'raw/warmup.json')
    assert warm['state']=='VALID' and warm['actual_input_tokens']==4096 and warm['actual_output_tokens']==64 and warm['actual_engine_input_verified']
    warm_text=(base/'raw/warmup-engine.log').read_text()
    run_text=(base/'raw/run-engine.log').read_text()
    graph_capture={'warmup_capture_counts':{str(n):len(re.findall(r'captured the '+str(n)+r'-token window',warm_text)) for n in [1,2,3,4]},
        'measured_capture_counts':{str(n):len(re.findall(r'captured the '+str(n)+r'-token window',run_text)) for n in [1,2,3,4]},
        'source':'Native verifier capture messages retained per request. Two devices can produce the same shape message; message text does not include device identity.',
        'capture_errors':re.findall(r'captured[^\n]*(?:upload|sync) (?!no error)[^\n]*',warm_text+'\n'+run_text),
        'cache_state_scope':'Exact startup capacities and warmup routing/adaptation counters retained. Full resident-ID sets require buffered diagnostic traces and are unavailable on clean speed binary.'}
    result={'variant':base.parts[-3],'profile':base.parts[-2],'replicate':int(base.name.removeprefix('rep')),
        'raw':str(base/'raw/run.json'),'path':str(base),'state':r['state'],'invalid_reasons':r.get('invalid_reasons'),
        'performance':{k:r.get(k) for k in KEYS},'finish_reason':r.get('finish_reason'),
        'application_status':r.get('application_status'),'input_sha256':r.get('actual_engine_input',{}).get('sha256'),
        'output_sha256':r.get('actual_output_ids_sha256'),'output_ids_path':r.get('actual_output_ids_path'),
        'source_sha':r['source_sha'],'binary_sha256':r['binary_sha256'],'system':system,
        'resource':load(base/'raw/resource-check.json'),'counters':counters((base/'raw/run-engine.log').read_text()),
        'progression':progression(r,rows),'PCIe':pcie_samples(base,r),'logical_file_blobs_decode':None,'logical_file_bytes_decode':None,
        'started_epoch':r['started_epoch'],'warmup':warm,'graph_capture':graph_capture}
    met=load(base/'raw/run-metrics.json')
    matches=[x for x in met.get('requests',[]) if x.get('prompt_tokens')==r['actual_input_tokens'] and x.get('output_tokens')==r['actual_output_tokens']]
    if matches:
        result['logical_file_blobs_decode']=matches[-1].get('file_blobs')
        result['logical_file_bytes_decode']=matches[-1].get('file_bytes')
        result['logical_file_MB_reported_decode']=matches[-1].get('file_mb')
        result['logical_file_counter_scope']='Native source deltas sampled after prefill; reported file MB = byte delta / 1e6 rounded to one decimal. CS-T RAM-blob counter does not count every direct full-arena CPU/mapped access.'
    return result

def compare(a,b):
    aa=load(a['output_ids_path']);bb=load(b['output_ids_path'])
    first=next((i for i,(x,y) in enumerate(zip(aa,bb)) if x!=y),None)
    if first is None and len(aa)!=len(bb):first=min(len(aa),len(bb))
    return {'same_input_ids':a['input_sha256']==b['input_sha256'],'same_output_ids':aa==bb,
        'first_diverging_token':first,'prefix_tokens_before_divergence':first if first is not None else len(aa),
        'positionwise_token_agreement_pct':100*sum(x==y for x,y in zip(aa,bb))/max(len(aa),len(bb)),
        'counter_equal':{k:a['performance'][k]==b['performance'][k] for k in ['mtp_proposed','mtp_accepted','verify_windows','local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries','all_routed_entries']},
        'free_generation_limitation':'ON changes placement/execution order; output/MTP divergence prevents interpreting TG delta as pure fixed-trajectory memory speedup.'}

def analyze(require_complete=True):
    runs=[one(p.parent) for p in sorted((C/'raw').glob('*/*/rep*/results.json'))]
    prim=[r for r in runs if r['variant'] in ['control','history-v2','early-v1']]
    if require_complete:assert len(prim)==27 and all(sum(r['variant']==v and r['profile']==p for r in prim)==3 for v in ['control','history-v2','early-v1'] for p in ['32k','128k','256k'])
    assert all(sum(r['variant']==v and r['profile']==p for r in runs)<=3 for v in {r['variant'] for r in runs} for p in ['32k','128k','256k'])
    cells=[]
    for variant in ['control','history-v2','early-v1']:
        for profile in ['32k','128k','256k']:
            attempted=[r for r in prim if r['variant']==variant and r['profile']==profile]
            valid=[r for r in attempted if r['state']=='VALID' and r['performance']['actual_output_tokens']==4096]
            aggregate={k:stats([r['performance'][k] for r in valid]) for k in KEYS}
            for key in ['CPU_VM_pct','CPU_process_one_core100','RAM_used_GiB','RSS_sum_GiB']:
                aggregate[key]=stats([r['system']['decode'][key]['mean'] if r['system']['decode'][key] else None for r in valid])
            for device in ['0','1']:
                for phase in ['prefill','decode']:
                    for key in ['util_pct','power_w','vram_mib']:
                        aggregate[f'GPU{device}_{phase}_{key}']=stats([r['system'][phase]['GPUs'][device][key]['mean'] if r['system'][phase]['GPUs'][device][key] else None for r in valid])
            for label in ['Q4_HISTORY','Q4_EARLY']:
                fields=set().union(*(set((r['counters'][label] or {}).keys()) for r in valid))
                for field in fields:aggregate[f'{label}_{field}']=stats([(r['counters'][label] or {}).get(field) for r in valid])
            for key in ['CPU_completion_ms','GPU_reach_wait_ms','window_ms','activation_quantization_ms','CPU_experts_per_layer_window','CPU_entries_per_layer_window']:
                aggregate[key]=stats([r['counters']['native_timing'].get(key) for r in valid])
            cells.append({'variant':variant,'profile':profile,'context':{'32k':32768,'128k':131072,'256k':262144}[profile],
                'valid':len(valid),'attempts':len(attempted),'stats':aggregate,'raw_paths':[r['raw'] for r in attempted],
                'resources':[r['resource'] for r in attempted],'publication_note':'early-v1 reserves one native3.072MB physical slot/device during decode; active residency is minus2, original physical capacity remains fixed.' if variant=='early-v1' else None})
    paired=[]
    for b in prim:
        if b['variant']=='control' or b['state']!='VALID':continue
        a=next((a for a in prim if a['variant']=='control' and a['profile']==b['profile'] and a['replicate']==b['replicate'] and a['state']=='VALID'),None)
        if not a:continue
        pair={'variant':b['variant'],'profile':b['profile'],'replicate':b['replicate'],**compare(a,b),
            'ratios':{k:b['performance'][k]/a['performance'][k] for k in ['PP','TG','TTFT_s','wall_s']},
            'chronology_limitation':'256K controlrep1 was already measured inA and reused without fourth repetition' if b['profile']=='256k' and b['replicate']==1 else None}
        assert pair['same_input_ids'];paired.append(pair)
    guards=[]
    for b in runs:
        if not b['variant'].endswith('-off'):continue
        a=next((r for r in prim if r['variant']=='control' and r['profile']==b['profile'] and r['replicate']==b['replicate']),None)
        if a:guards.append({'variant':b['variant'],**compare(a,b),'TG_ratio':b['performance']['TG']/a['performance']['TG'],
            'wall_ratio':b['performance']['wall_s']/a['performance']['wall_s'],'capacity_identical':b['resource']['primary_slots']==a['resource']['primary_slots'] and b['resource']['helper_or_stage1_slots']==a['resource']['helper_or_stage1_slots'],
            'limitation':'One long guard plus4 short cases; a single timing comparison does not establish sub1% equivalence.'})
    ratios=[]
    for variant in ['history-v2','early-v1']:
        for profile in ['32k','128k','256k']:
            rr=[x for x in paired if x['variant']==variant and x['profile']==profile]
            ratios.append({'variant':variant,'profile':profile,'n':len(rr),'ratios':{k:stats([r['ratios'][k] for r in rr]) for k in ['PP','TG','TTFT_s','wall_s']},
                'same_output_pairs':sum(r['same_output_ids'] for r in rr)})
    summary={'state':'COMPLETE_PRIMARY' if len(prim)==27 else 'PARTIAL','cells':cells,'runs':runs,'paired':paired,'paired_ratios':ratios,'off_guards':guards,
        'protocol':load(C/'phase-c/primary-plan.json'),'practical_materiality_pct':3,'recommendation':None,
        'limitations':['Three attempts are not a significance test. Invalid attempts retained; no fourth request.',
            'Output/MTP trajectory can differ after residency changes; headline TG is application-level free generation.',
            'Physical cache capacities and all-demand counts recorded; early spare and CUDA resources charged.',
            'Sampled1Hz progression/PCIe are approximate; logical expert counters distinct from aggregate transfer.',
            'Exact useful/late/victim outcomes available in diagnostics, not inferred as zero in clean speed.',
            'Reserve setup affects TTFT and request-end cleanup affects wall; enginePP/decode timers do not cover both.']}
    recent256=[]
    for variant in ['history-v2','early-v1']:
        selected=[item for item in paired if item['variant']==variant and item['profile']=='256k' and item['replicate'] in [2,3]]
        recent256.append({'variant':variant,'replicates':[2,3],'n':len(selected),
            'ratios':{key:stats([item['ratios'][key] for item in selected]) for key in ['PP','TG','TTFT_s','wall_s']},
            'note':'Supplementary chronology sensitivity only. Earlier compatible controlrep1 remains valid and included in all three-attempt headline cells.'})
    summary['recent256_paired_sensitivity']=recent256
    save(C/'phase-c/summary.json',summary);save(C/'analysis/live-paired.json',paired);save(C/'analysis/live-run-details.json',runs)
    flat=[]
    for cell in cells:
        row={k:cell[k] for k in ['variant','profile','context','valid','attempts']}
        for key,value in cell['stats'].items():
            for statistic in ['min','median','max']:row[f'{key}_{statistic}']=value[statistic] if value else None
        flat.append(row)
    fields=sorted(set().union(*(set(row) for row in flat)))
    with (C/'phase-c/summary.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(flat)
    print(json.dumps([{'variant':x['variant'],'profile':x['profile'],'valid':x['valid'],'TG':x['stats']['TG'],'wall':x['stats']['wall_s']} for x in cells],indent=2))
    if require_complete:
        status('C_PRIMARY_ANALYZED',phase='C',running=None,
               completed=['Frozen Q4 provenance', 'Phase A ground truth/costs/reconciled replay',
                          'Phase B causal families and frozen learned checkpoints',
                          'Short correctness/OFF/adverse-copy gates', '27 primary attempts and two long OFF guards'],
               pending=['Held-out application confirmation', 'Matched prediction/history diagnostics and cancellation',
                        'Nine actual launcher smoke paths', 'Decision/reports/identity audit/local commit/cleanup'],
               next_exact_action='Run only the predeclared serial post-matrix stages; no parameter tuning')
    return summary

if __name__=='__main__':analyze()
