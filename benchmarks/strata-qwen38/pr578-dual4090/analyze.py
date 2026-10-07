import json,re,statistics,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parent

def enrich(a):
 label=a.get('candidate') or a.get('model');tagpath=Path(a.get('config',''))
 a['reported_expert_hit_rate']=a.get('expert_tiers',{}).get('hit_rate')
 a['logical_expert_file_blobs']=a.get('expert_tiers',{}).get('file_blobs')
 a['logical_expert_file_MB']=a.get('expert_tiers',{}).get('file_mb')
 a['headline_eligible']=bool(a.get('valid') and 'DIAG' not in label and label!='H-OPT-LOOKUP-ON')
 a['summary_exclusion']=('INVALID_REQUEST' if not a.get('valid') else 'DIAGNOSTIC_INSTRUMENTATION' if 'DIAG' in label else 'INITIAL_CACHE_CAPACITY_MISMATCH' if label=='H-OPT-LOOKUP-ON' else None)
 # caller supplies canonical source file
 st=a.get('initial_layout') or {}
 a['initial_primary_slot_capacity']=st.get('primary');a['initial_helper_slot_capacity']=st.get('helper');a['selected_layer_split_K']=st.get('layer_split_K')
 logpath=Path(a['raw_path']).with_name(Path(a['raw_path']).stem+'-engine.log');text=logpath.read_text() if logpath.exists() else ''
 m=re.search(r'strata decode timing: (\d+) windows, avg T ([\d.]+), ([\d.]+) tokens/window, ([\d.]+) ms/window',text)
 if m:a.update(verify_windows=int(m[1]),average_window_T=float(m[2]),committed_tokens_per_window=float(m[3]),mean_verify_window_latency_ms=float(m[4]))
 m=re.search(r'per layer-window: CPU experts ([\d.]+) \(([\d.]+) entries\), VRAM hits ([\d.]+), PCIe ([\d.]+)',text)
 if m:
  a.update(cpu_distinct_experts_per_layer_window=float(m[1]),cpu_fallback_entries_per_layer_window=float(m[2]),primary_hits_per_layer_window=float(m[3]),pcie_experts_per_layer_window=float(m[4]))
  a['cpu_fallback_entries_estimate']=float(m[2])*a['verify_windows']*48
 m=re.search(r'decode expert cache hit rate: ([\d.]+)% \((\d+) hits / (\d+) lookups\)',text)
 if m:a.update(reported_primary_cache_hits=int(m[2]),reported_primary_cache_lookups=int(m[3]),reported_primary_cache_nonhits=int(m[3])-int(m[2]))
 m=re.search(r'suffix drafts: (\d+) windows, (\d+) of (\d+) drafts accepted',text)
 a.update(suffix_windows=int(m[1]) if m else 0,suffix_accepted=int(m[2]) if m else 0,suffix_proposed=int(m[3]) if m else 0)
 a['suffix_acceptance_pct']=100*int(m[2])/int(m[3]) if m and int(m[3]) else None
 m=re.search(r'CUDA1: (\d+) expert entries, (\d+) active layer launches, ([\d.]+) MiB returned .*?host ([\d.]+) ms staging\+launching, ([\d.]+) ms waiting',text)
 if m:a.update(helper_entries=int(m[1]),helper_layer_launches=int(m[2]),helper_returned_bytes=float(m[3])*1048576,helper_returned_bytes_per_generated_token=float(m[3])*1048576/a['generated_tokens'],helper_returned_bytes_per_layer_launch=float(m[3])*1048576/int(m[2]),helper_staging_ms=float(m[4]),helper_wait_ms=float(m[5]))
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
  a['decode_cpu_process_pct']=statistics.mean(sum(p['cpu_pct'] for p in x['processes']) for x in samples)
  for gpu in [0,1]:
   gs=[g for x in samples for g in x.get('gpus',[]) if g['index']==gpu]
   for key,out in [('util_pct','util_pct'),('power_w','power_w'),('vram_gib','peak_vram_gib')]:
    a[f'gpu{gpu}_decode_{out}']=(max if key=='vram_gib' else statistics.mean)(g[key] for g in gs) if gs else None
 return a

def summarize():
 rows=[]
 for p in R.glob('raw/*-done.json'):
  group=json.loads(p.read_text())
  for orig in group.get('runs',[]):
   name=orig.get('candidate')+'-'+orig.get('context_label','32K')+'-run'+str(orig.get('repeat') or '')
   # Link by config candidate/context/output to actual canonical file.
   for f in sorted(R.glob('raw/'+group['label']+'-*-run[123].json')):
    a=json.loads(f.read_text());a['raw_path']=str(f)
    if not any(x['raw_path']==str(f) for x in rows):rows.append(enrich(a))
 cells=[]
 for label,ctx in sorted(set((a['candidate'],a['actual_prompt_tokens']) for a in rows)):
  rs=[a for a in rows if a['candidate']==label and a['actual_prompt_tokens']==ctx and a.get('valid')]
  if not rs:continue
  cell={'config':label,'actual_prompt':ctx,'valid_runs':len(rs),'three_run_headline_complete':len(rs)==3 and 'DIAG' not in label and label!='H-OPT-LOOKUP-ON','statistic_basis':f'median_of_{len(rs)}_valid_runs','raw_paths':[a['raw_path'] for a in rs]}
  for k in ['pp_tps','tg_tps','ttft_s','acceptance_pct','mean_accepted_length','verify_windows','committed_tokens_per_window','mean_verify_window_latency_ms','suffix_accepted','helper_entries','helper_returned_bytes','helper_returned_bytes_per_generated_token','helper_returned_bytes_per_layer_launch','helper_wait_ms','primary_hits_per_layer_window','pcie_experts_per_layer_window','cpu_fallback_entries_estimate','cache_overlap','decode_cpu_system_pct','decode_cpu_process_pct','gpu0_decode_util_pct','gpu1_decode_util_pct','gpu0_decode_power_w','gpu1_decode_power_w','gpu0_decode_pcie_rx_MBps','gpu0_decode_pcie_tx_MBps','gpu1_decode_pcie_rx_MBps','gpu1_decode_pcie_tx_MBps','peak_rss_gib','peak_ram_used_gib','peak_vram0_gib','peak_vram1_gib','draft_tokens','accepted_tokens','reported_expert_hit_rate','reported_primary_cache_hits','reported_primary_cache_lookups','reported_primary_cache_nonhits','logical_expert_file_blobs','logical_expert_file_MB','initial_primary_slot_capacity','initial_helper_slot_capacity','selected_layer_split_K']:
   vals=[a[k] for a in rs if a.get(k) is not None]
   cell[k]=statistics.median(vals) if vals else None
   if k in ['pp_tps','tg_tps']:cell[k+'_min']=min(vals);cell[k+'_max']=max(vals)
  cells.append(cell)
 (R/'summary.json').write_text(json.dumps({'cells':cells,'runs':rows},indent=2))
 import csv
 if cells:
  with (R/'summary.csv').open('w') as f:
   cw=csv.DictWriter(f,fieldnames=list(cells[0]));cw.writeheader();cw.writerows(cells)
 return cells
if __name__=='__main__':
 for x in summarize():print(x['config'],x['actual_prompt'],x['valid_runs'],x['pp_tps'],x['tg_tps'])
