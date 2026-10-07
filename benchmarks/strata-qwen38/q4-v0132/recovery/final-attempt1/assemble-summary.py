"""Offline summaries from standalone evidence; never run during timed requests."""
from pathlib import Path
import json, csv, re, statistics, time
import psutil

R = Path(__file__).resolve().parent

def load(p):
    return json.loads(Path(p).read_text())

def arg(cfg, key, default=None):
    a = cfg.get('args', [])
    return a[a.index(key)+1] if key in a else default

def median(values):
    values = [x for x in values if isinstance(x, (int,float))]
    return statistics.median(values) if values else None

def telemetry(record):
    path = record.get('telemetry_file')
    if not path or not Path(path).exists():
        return {}
    samples = [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
    out = {'CPU_process_pct': median([sum(x.get('cpu_pct',0) for x in s.get('processes',[])) for s in samples[1:]]),
           'CPU_system_pct': median([s.get('system_cpu_pct') for s in samples[1:]])}
    for gpu in [0,1]:
        rows = [g for s in samples for g in s.get('gpus',[]) if g['index']==gpu]
        for target,key in [('util','util_pct'),('power','power_w')]:
            out[f'GPU{gpu}_{target}'] = median([g.get(key) for g in rows])
    if samples:
        # Process read_bytes are OS accounting, not an expert-only or physical-SSD counter.
        first = {p['pid']:p for p in samples[0].get('processes',[])}
        last = {p['pid']:p for p in samples[-1].get('processes',[])}
        out['OS_process_read_bytes_request_sample_delta'] = sum(max(0,p['read_bytes']-first[pid]['read_bytes']) for pid,p in last.items() if pid in first)
    return out

def normal_logs(path, record):
    cfg = record.get('full_config',{})
    startup = Path(cfg.get('log','/nonexistent'))
    text = startup.read_text(errors='replace') if startup.is_file() else ''
    request_log = path.with_name(path.stem+'-engine.log')
    request = request_log.read_text(errors='replace') if request_log.exists() else ''
    cache0 = re.search(r'expert cache (\d+) slots, ([\d.]+) GiB',text)
    cache1 = re.search(r'layer split: CUDA1 runs layers .*?expert cache (\d+) slots \(([\d.]+) GiB\)',text)
    hit = re.search(r'decode expert cache hit rate: ([\d.]+)% \((\d+) hits / (\d+) lookups\)',request)
    out = {'GPU0_cache_slots':int(cache0[1]) if cache0 else None,'GPU1_cache_slots':int(cache1[1]) if cache1 else None,
           'GPU0_cache_GiB':float(cache0[2]) if cache0 else None,'GPU1_cache_GiB':float(cache1[2]) if cache1 else None,
           'GPU0_hit_count':None,'GPU1_hit_count':None,'CPU_misses':int(hit[3])-int(hit[2]) if hit else None,
           'combined_GPU_hit_count':int(hit[2]) if hit else None,'combined_expert_lookups':int(hit[3]) if hit else None,
           'combined_hit_percent':float(hit[1]) if hit else None,
           'host_expert_source':'resident_RAM_complement' if '--resident-budget-gib' in cfg.get('args',[]) else 'full_RAM_native_arena' if 'expert arena:' in text else 'source_not_proven_by_startup_log',
           'prefill_expert_file_reads':None,'prefill_PLE_file_reads':None,
           'physical_expert_SSD_bytes_decode':None,
           'normal_stage_timing_lines':[x for x in request.splitlines() if x.startswith(('strata decode timing:','strata serve: stage '))],
           'counter_limits':'Hitratio denominator counts cachekind0 and CPUkind<0 entries, excludes PCIekind1/remotekind2; lookup-minus-hit countsCPU routedentries, not allGPUcachemisses. Per-GPU hits not exposed in normal request stats. Stage lines may be cumulative since startup. Logical file_blobs measures expert source fetches; OS reads include PLE and other files; virtiofs hides physical host SSD attribution.'}
    # Explicit prefill arguments may be reduced at startup; record resolved size separately.
    requested = arg(cfg,'--prefill')
    reductions = re.findall(r'prompt chunk (\d+) -> (\d+) tokens',text)
    auto_k = re.search(r'layer split auto: K=(\d+)',text)
    requested_split = cfg.get('layer_split')
    out['layer_split_requested'] = requested_split
    out['layer_split'] = int(auto_k[1]) if auto_k else int(requested_split) if requested_split and str(requested_split).isdigit() else requested_split
    out['CPU_routed_entries'] = out['CPU_misses']
    out['GPU_cache_CPU_lookups'] = out['combined_expert_lookups']
    out['prefill_chunk_argument'] = requested
    out['prefill_chunk_actual'] = int(reductions[-1][1]) if reductions else int(requested) if requested and str(requested).isdigit() else None
    return out

def row(path, d):
    cfg=d['full_config'];a=cfg['args'];tiers=d.get('expert_tiers',{})
    out={'raw_result':str(path),'candidate':d.get('candidate',d.get('model')),'kind':d.get('kind'),
         'Strata_HEAD':d['Strata_HEAD'],'Strata_version':d['Strata_version'],'build_variant':d['build_variant'],'model_revision':d['model_revision'],
         'topology':d['topology'],'gpu_count':len(cfg['gpu']) if isinstance(cfg.get('gpu'),list) else 1,
         'layer_split':cfg.get('layer_split'),'remote_cache_mode':arg(cfg,'--expert-cache-remote'),
         'remote_cache_slots':arg(cfg,'--expert-cache-device1'), 'resident_mode':'--resident-budget-gib' in a,
         'KV_mode':arg(cfg,'--kv'),'KV_streaming':'--kv-resident' in a,'KV_resident_tokens':arg(cfg,'--kv-resident'),
         'rotated_INT8':cfg.get('effective_experiment_environment',{}).get('STRATA_KV_ROT')=='1',
         'split_own':cfg.get('effective_experiment_environment',{}).get('STRATA_SPLIT_OWN')=='1',
         'spec':arg(cfg,'--spec'),'spec_min_p':arg(cfg,'--spec-min-p'),
         'pool_workers':arg(cfg,'--pool-workers','runtime_default'),'pcie_frac':arg(cfg,'--pcie-frac','runtime_default'),
         'actual_prompt_tokens':d['actual_prompt_tokens'],'output_tokens':d['generated_tokens'],
         'PP_tps':d.get('pp_tps'),'TG_tps':d.get('tg_tps'),'TTFT_s':d.get('ttft_s'),'wall_s':d.get('total_wall_s'),
         'prompt_processing_s':d.get('prompt_processing_wall_s'),'generation_s':d.get('decode_wall_s'),
         'MTP_accept':d.get('acceptance_pct'),'drafted':d.get('draft_tokens'),'accepted':d.get('accepted_tokens'),
         'mean_accepted_length':d.get('mean_accepted_length'),'verify_windows':d.get('verify_rounds'),
         'reused_tokens':d.get('cache_reused_tokens'),'final_KV_occupancy':d.get('final_kv_occupancy_tokens'),
         'expert_file_reads_decode':tiers.get('file_blobs'),'expert_file_MB_decode':tiers.get('file_mb'),
         'RAM_used_GiB':d.get('peak_ram_used_gib'),'RSS_GiB':d.get('peak_rss_gib'),'MemAvailable_min_GiB':d.get('min_mem_available_gib'),
         'VRAM0_GiB':d.get('peak_vram0_gib'),'VRAM1_GiB':d.get('peak_vram1_gib'),
         'status':d.get('status'),'abort':d.get('abort'),'full_config':cfg,'full_engine_command':d['full_engine_command']}
    out.update(normal_logs(path,d));out.update(telemetry(d))
    per_cell={'int8':1056,'k8v4':816,'q4_0':576,'fp16':2048}.get(out['KV_mode'])
    out['KV_KV_payload_bytes_per_cell_per_layer']=per_cell
    out['KV_KV_logical_payload_bytes_estimate']=d['actual_prompt_tokens']*12*per_cell if per_cell else None
    out['KV_payload_estimate_scope']='Source-derived QSA K/V payload only, twelve QSA layers; excludes indexer/GDN/pagepadding/state/checkpoints and allocator overhead. Uses actualpromptpositions; not a measured GPU allocation. Source: architecture-notes.md/evidence/architecture-source-identity.json.'
    out['selection_eligible']=d.get('kind')=='candidate' and not d.get('diagnostic_only') and d.get('status')=='OK'
    return out

if __name__=='__main__':
    for marker in ['phase-final-matrix-terminal.json','phase-long-terminal.json','phase-agent64-terminal.json','phase-agent128-terminal.json','phase-compaction-terminal.json','phase-quality-terminal.json','phase-needle-terminal.json','phase-iq3-terminal.json','phase-diagnostics-terminal.json']:
        assert load(R/'raw'/marker)['status']=='COMPLETE',marker
    for p in psutil.process_iter(['pid','cmdline']):
        try:
            cmd=p.info['cmdline'] or []
            assert not (cmd and cmd[0] in ['/srv/ai/strata-v0.1.32/build-default/strata','/srv/ai/strata/build/strata']),f'Active engine {p.pid}; defer offline analysis'
        except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    records=[]
    roots=[R/'raw',R/'controls/v0131/raw',R/'controls/v0132/raw',R/'controls/v0131-compaction/raw']
    for root in roots:
        for path in sorted(root.glob('*.json')):
            if any(path.name.endswith(x) for x in ['-request.json','-stream.json','-metrics.json','-status.json','-official-config.json']):continue
            d=load(path)
            if isinstance(d,dict) and all(k in d for k in ['pp_tps','actual_prompt_tokens','generated_tokens','full_config','full_engine_command','Strata_HEAD']):
                records.append(row(path,d))
    assert records
    output={'status':'ASSEMBLED_REQUIRES_INDEPENDENT_FINAL_AUDIT','created':time.time(),'records':records,
            'final_context_matrix':load(R/'raw/final-matrix-summary.json')['cells'],
            'controlled_version_PP_comparison':load(R/'comparison-pp-control.json'),
            'limits':'Null means unavailable; no invented physicalSSD, per-GPU expert hits or prefill expert/PLE counters. Memory peaks cover whole request, including PP and TG. Medians and peaks must remain distinct.'}
    (R/'summary.json').write_text(json.dumps(output,indent=2))
    keys=list(dict.fromkeys(k for d in records for k in d))
    with (R/'summary.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,keys);writer.writeheader()
        for d in records:writer.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in d.items()})
    print(f'Assembled {len(records)} standalone requests; final audit remains mandatory.')
