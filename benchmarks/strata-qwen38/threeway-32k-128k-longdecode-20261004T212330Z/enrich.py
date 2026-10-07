import json,re,statistics,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parent
def final_labels():
 p=R/'matrix-retry-policy.json'
 return set(json.loads(p.read_text())['final_labels'].values()) if p.exists() else set()

def enrich(a):
 label=a.get('candidate') or a.get('model');tagpath=Path(a.get('config',''))
 a['reported_expert_hit_rate']=a.get('expert_tiers',{}).get('hit_rate')
 a['protocol_mmap_file_blobs']=a.get('expert_tiers',{}).get('file_blobs')
 a['protocol_mmap_file_MB']=a.get('expert_tiers',{}).get('file_mb')
 a['logical_expert_file_blobs']=None
 a['logical_expert_file_MB']=None
 a['expert_file_counter_basis']='UNAVAILABLE: protocol mmap/complement counters do not measure full RAM arena; see expert-io-provenance.json'
 a['headline_eligible']=bool(a.get('valid') and 'DIAG' not in label and not label.startswith('UPSTREAM'))
 a['summary_exclusion']=('INVALID_REQUEST' if not a.get('valid') else 'DIAGNOSTIC_INSTRUMENTATION' if 'DIAG' in label else 'SUPERSEDED_PARTIAL_MATRIX' if label=='LS-B-FINAL' and final_labels() else 'PILOT_UNCONFIRMED' if label.startswith('UPSTREAM') else None)
 if a['summary_exclusion']:a['headline_eligible']=False
 exclusions=R/'background-analysis-exclusions.json'
 if exclusions.exists() and str(Path(a['raw_path']).relative_to(R)) in json.loads(exclusions.read_text())['superseded_cell']:
  a['runtime_request_valid']=a.get('valid');a['valid']=False;a['headline_eligible']=False;a['exclusion']='EXCLUDED_BACKGROUND_ANALYSIS_OR_SUPERSEDED_CELL';a['summary_exclusion']=a['exclusion']
 # caller supplies canonical source file
 st=a.get('initial_layout') or {}
 a['initial_primary_slot_capacity']=st.get('primary');a['initial_helper_slot_capacity']=st.get('helper');a['selected_layer_split_K']=st.get('layer_split_K')
 logpath=Path(a['raw_path']).with_name(Path(a['raw_path']).stem+'-engine.log');text=logpath.read_text() if logpath.exists() else ''
 m=re.search(r'strata decode timing: (\d+) windows, avg T ([\d.]+), ([\d.]+) tokens/window, ([\d.]+) ms/window',text)
 if m:a.update(verify_windows=int(m[1]),average_window_T=float(m[2]),committed_tokens_per_window=float(m[3]),mean_verify_window_latency_ms=float(m[4]))
 timing=re.search(r'verify ([\d.]+) \(GPU-reach wait ([\d.]+) \+ per-layer host ([\d.]+) \[plan ([\d.]+) actq ([\d.]+) jobs ([\d.]+) CPU ([\d.]+)\] \+ stage ([\d.]+)\)',text)
 if timing:
  for key,value in zip(['verify_ms_per_window','GPU_reach_wait_ms_per_window','per_layer_host_ms_per_window','plan_ms_per_window','actq_ms_per_window','jobs_ms_per_window','CPU_work_ms_per_window','stage_ms_per_window'],timing.groups()):a[key]=float(value)
 m=re.search(r'per layer-window: CPU experts ([\d.]+) \(([\d.]+) entries\), VRAM hits ([\d.]+), PCIe ([\d.]+)',text)
 if m:
  a.update(cpu_distinct_experts_per_layer_window=float(m[1]),cpu_fallback_entries_per_layer_window=float(m[2]),primary_hits_per_layer_window=float(m[3]),pcie_experts_per_layer_window=float(m[4]))
  a['cpu_fallback_entries_estimate']=float(m[2])*a['verify_windows']*48
 m=re.search(r'decode expert cache hit rate: ([\d.]+)% \((\d+) hits / (\d+) lookups\)',text)
 if m:
  a.update(reported_primary_cache_hits=int(m[2]),reported_primary_cache_lookups=int(m[3]),reported_primary_cache_nonhits=int(m[3])-int(m[2]),cpu_fallback_entries=int(m[3])-int(m[2]),primary_hits_exact=int(m[2]),cpu_fallback_entries_basis='Native decode cache lookups-minus-hits; source and36 diagnostic records verify equality to multi_entries')
 mo=re.search(r'(\d+) more read by the GPU over PCIe or from another GPU \([\d.]+% of all (\d+) routed\)',text)
 if mo:a.update(offloaded_routed_entries=int(mo[1]),total_routed_entries=int(mo[2]))
 counter_matches=re.findall(r'STRATA_BENCH_COUNTERS (\{[^\n]+\})',text)
 if counter_matches:
  bc=json.loads(counter_matches[-1]);a['boundary_counters']=bc
  a.update(cpu_fallback_entries=bc['CPU_fallback_entries'],primary_hits_exact=bc['primary_expert_hits'],primary_pcie_experts_exact=bc['primary_pcie_experts'],cpu_missed_experts_exact=bc['CPU_missed_experts'],cpu_activation_quant_ms=bc['CPU_activation_quant_ms'])
 m=re.search(r'suffix drafts: (\d+) windows, (\d+) of (\d+) drafts accepted',text)
 a.update(suffix_windows=int(m[1]) if m else 0,suffix_accepted=int(m[2]) if m else 0,suffix_proposed=int(m[3]) if m else 0)
 a['suffix_acceptance_pct']=100*int(m[2])/int(m[3]) if m and int(m[3]) else None
 m=re.search(r'CUDA1: (\d+) expert entries, (\d+) active layer launches, ([\d.]+) MiB returned .*?host ([\d.]+) ms staging\+launching, ([\d.]+) ms waiting',text)
 if m:a.update(helper_entries=int(m[1]),helper_layer_launches=int(m[2]),helper_returned_bytes=float(m[3])*1048576,helper_returned_bytes_per_generated_token=float(m[3])*1048576/a['generated_tokens'],helper_returned_bytes_per_layer_launch=float(m[3])*1048576/int(m[2]),helper_staging_ms=float(m[4]),helper_wait_ms=float(m[5]))
 if a.get('helper_entries') is not None and a.get('total_routed_entries'):
  a['helper_hit_pct_of_all_routed']=100*a['helper_entries']/a['total_routed_entries']
  a['cpu_fallback_pct_of_all_routed']=100*a['cpu_fallback_entries']/a['total_routed_entries']
 snapshots=a.get('cache_snapshots') or []
 if snapshots:
  a['cache_overlap']=snapshots[-1]['overlap'];a['cache_overlap_pct_of_helper']=100*a['cache_overlap']/snapshots[-1]['helper_resident'] if snapshots[-1]['helper_resident'] else 0
 tele=R/'telemetry'/(Path(a['raw_path']).stem+'.jsonl');samples=[json.loads(x) for x in tele.read_text().splitlines()] if tele.exists() else []
 # TTFT bounds emitted content (approximately ends prefill); 1Hz sparse short decode caveat.
 t0=a.get('t_first_monotonic_s');t1=a.get('t_end_monotonic_s');samples=[x for x in samples if t0 and t0<=x['monotonic']<=t1]
 a['decode_telemetry_sample_count']=len(samples)
 dmon=R/'telemetry'/(str(label)+'-pcie-dmon.log')
 if dmon.exists() and samples:
  offset=statistics.mean(x['wall_time']-x['monotonic'] for x in samples)
  pci=[]
  for line in dmon.read_text().splitlines():
   q=line.split()
   if len(q)==5 and q[0].isdigit():
    try:stamp=datetime.datetime.strptime(q[0]+q[1],'%Y%m%d%H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp();gpu=int(q[2]);rx=float(q[3]);tx=float(q[4])
    except:continue
    if t0+offset-.5<=stamp<=t1+offset+.5:pci.append((gpu,rx,tx))
  for gpu in [0,1]:
   gs=[q for q in pci if q[0]==gpu]
   a[f'gpu{gpu}_decode_pcie_samples']=len(gs)
   a[f'gpu{gpu}_decode_pcie_rx_MBps']=statistics.mean(q[1] for q in gs) if gs else None
   a[f'gpu{gpu}_decode_pcie_tx_MBps']=statistics.mean(q[2] for q in gs) if gs else None
  a['pcie_note']='Hardware dmon1Hz with0.5s phase tolerance, includes alltraffic; sparse256-output decode samples.'

 if samples:
  a['decode_cpu_system_pct']=statistics.mean(x['system_cpu_pct'] for x in samples)
  a['decode_cpu_system_pct_peak']=max(x['system_cpu_pct'] for x in samples)
  a['decode_cpu_process_pct']=statistics.mean(sum(p['cpu_pct'] for p in x['processes']) for x in samples)
  a['decode_cpu_process_pct_peak']=max(sum(p['cpu_pct'] for p in x['processes']) for x in samples)
  for gpu in [0,1]:
   gs=[g for x in samples for g in x.get('gpus',[]) if g['index']==gpu]
   a[f'gpu{gpu}_decode_util_pct_peak']=max(g['util_pct'] for g in gs) if gs else None
   a[f'gpu{gpu}_decode_power_w_peak']=max(g['power_w'] for g in gs) if gs else None
   for key,out in [('util_pct','util_pct'),('power_w','power_w'),('vram_gib','peak_vram_gib')]:
    a[f'gpu{gpu}_decode_{out}']=(max if key=='vram_gib' else statistics.mean)(g[key] for g in gs) if gs else None
 return a
