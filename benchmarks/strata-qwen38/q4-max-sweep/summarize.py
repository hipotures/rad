#!/usr/bin/env python3
import json,csv,re,statistics
from pathlib import Path
import phase_telemetry
R=Path(__file__).resolve().parent
FIELDS='topology gpu_count layer_split remote_cache_mode remote_cache_slots resident_mode host_expert_source KV_mode KV_streaming prefill_chunk spec spec_min_p pool_workers pcie_frac actual_prompt_tokens output_tokens PP_tps TG_tps TTFT_s wall_s MTP_accept GPU0_cache_slots GPU1_cache_slots GPU0_hit_count GPU1_hit_count CPU_misses expert_file_reads expert_file_MB RAM_used MemAvailable VRAM0 VRAM1 GPU0_util GPU1_util GPU0_power GPU1_power'.split()
def avg(v):return statistics.mean(v) if v else None
def main():
 rows=[]
 for p in sorted((R/'raw').glob('*.json')):
  d=json.loads(p.read_text())
  if not isinstance(d,dict) or 'actual_prompt_tokens' not in d or 'timings' not in d:continue
  label=d.get('candidate',d.get('model'));cfgpath=R/'configs'/f'{label}.json'
  if not cfgpath.exists():continue
  cfg=json.loads(cfgpath.read_text());a=cfg['args'];val=lambda k,default=None:a[a.index(k)+1] if k in a else default
  startup=R/'raw'/f'{label}-startup.json';e=json.loads(startup.read_text()).get('metrics',{}).get('engine',{}) if startup.exists() else {}
  tp=R/'telemetry'/(p.stem+'.jsonl');ss=[json.loads(line) for line in tp.read_text().splitlines()] if tp.exists() else []
  startup_log=(R/'logs'/f'{label}-engine.log').read_text(errors='replace') if (R/'logs'/f'{label}-engine.log').exists() else ''
  log=(R/'raw'/(p.stem+'-engine.log')).read_text() if (R/'raw'/(p.stem+'-engine.log')).exists() else ''
  hits=re.search(r'\((\d+) hits / (\d+) lookups\)',log)
  cpu=re.search(r'CPU experts ([\d.]+) \(([\d.]+) entries\), VRAM hits ([\d.]+), PCIe ([\d.]+)',log)
  row={'topology':label,'gpu_count':2 if isinstance(cfg.get('gpu'),list) or val('--expert-cache-device1') else 1,'layer_split':cfg.get('layer_split'), 'remote_cache_mode':val('--expert-cache-remote-placement'),'remote_cache_slots':val('--expert-cache-device1'), 'resident_mode':'budget' if val('--resident-budget-gib') else 'arena','host_expert_source':'GGUF+RAM_complement' if val('--resident-budget-gib') else 'full_RAM_native_arena','KV_mode':val('--kv'),'KV_streaming':val('--kv-resident',0),'prefill_chunk':val('--prefill'),'spec':val('--spec'),'spec_min_p':val('--spec-min-p',e.get('spec_min_p')),'pool_workers':val('--pool-workers',e.get('pool_workers')),'pcie_frac':val('--pcie-frac',e.get('pcie_frac')),'actual_prompt_tokens':d['actual_prompt_tokens'],'output_tokens':d['generated_tokens'],'PP_tps':d.get('pp_tps'),'TG_tps':d.get('tg_tps'),'TTFT_s':d.get('ttft_s'),'wall_s':d.get('total_wall_s'),'MTP_accept':d.get('acceptance_pct'),'GPU0_cache_slots':e.get('expert_slots_primary'),'GPU1_cache_slots':e.get('expert_slots',0)-e.get('expert_slots_primary',0) if isinstance(cfg.get('gpu'),list) else val('--expert-cache-device1'),'GPU0_hit_count':None,'GPU1_hit_count':None,'CPU_misses':None,'expert_file_reads':d.get('expert_tiers',{}).get('file_blobs'),'expert_file_MB':d.get('expert_tiers',{}).get('file_mb'),'RAM_used':d.get('peak_ram_used_gib'),'MemAvailable':d.get('min_mem_available_gib'),'VRAM0':d.get('peak_vram0_gib'),'VRAM1':d.get('peak_vram1_gib'),'run':p.stem,'kind':d.get('kind'),'total_GPU_hits':int(hits[1]) if hits else None,'total_lookups':int(hits[2]) if hits else None,'CPU_experts_per_layer_window':float(cpu[1]) if cpu else None,'PCIe_experts_per_layer_window':float(cpu[4]) if cpu else None,'status':d['status']}
  timing=re.search(r'strata decode timing: (\d+) windows, avg T ([\d.]+), ([\d.]+) tokens/window, ([\d.]+) ms/window = verify ([\d.]+) \(GPU-reach wait ([\d.]+) \+ per-layer host ([\d.]+) \[plan ([\d.]+) actq ([\d.]+) jobs ([\d.]+) CPU ([\d.]+)\] \+ stage ([\d.]+)\) \+ commit/emit ([\d.]+) \+ draft ([\d.]+)',log)
  if timing:
   names=['decode_windows','decode_mean_verify_T','decode_tokens_per_window','decode_ms_per_window','verify_ms_per_window','GPU_reach_wait_ms_per_window','host_pool_ms_per_window','host_plan_ms_per_window','host_actq_ms_per_window','host_jobs_ms_per_window','CPU_run_ms_per_window','host_stage_ms_per_window','commit_emit_ms_per_window','draft_ms_per_window']
   row.update({name:float(value) for name,value in zip(names,timing.groups())})
   row['decode_timing_note']='Request-delta diagnostic averages per verify window; CPU run can overlap GPU/host work. Do not add subcomponents as independent wall times. Printed per-layer host label is normalized by windows in upstream generate.cpp5092.'
  actual_K=re.search(r'layer split auto: K=(\d+)',startup_log)
  chunk_changes=list(re.finditer(r'prompt chunk auto: (\d+) tokens|prompt chunk \d+ -> (\d+) tokens|prompt buffers need [^\n]*: (\d+)-token chunks|strata serve: [^\n]*: trying a (\d+)-token chunk',startup_log))
  chosen_chunk=int(next(v for v in chunk_changes[-1].groups() if v is not None)) if chunk_changes else None
  borrowed0=re.search(r'prompt path borrows (\d+) CUDA0 cache slots \(([\d.]+) GiB\)',startup_log)
  borrowed1=re.search(r'CUDA1 prompt path borrows (\d+) of its \d+ slots \(([\d.]+) GiB\)',startup_log)
  changed_after_borrow=any(c.start()>b.end() for c in chunk_changes for b in [borrowed0,borrowed1] if b is not None)
  if changed_after_borrow:borrowed0=borrowed1=None
  row.update(GPU0_prefill_borrowed_slots=int(borrowed0[1]) if borrowed0 else None,GPU1_prefill_borrowed_slots=int(borrowed1[1]) if borrowed1 else None,GPU0_prefill_borrowed_GiB_approx=float(borrowed0[2]) if borrowed0 else None,GPU1_prefill_borrowed_GiB_approx=float(borrowed1[2]) if borrowed1 else None,prefill_borrowed_memory_note='Startup-reported expert-cache slots lent to prompt buffers; GiB values are rounded upstream log values, not total scratch allocations.')
  if changed_after_borrow:row['prefill_borrowed_memory_note']='Unavailable: upstream reduced the chunk after reporting its initial loan and does not log the revised borrowed slot count. Initial loan remains in raw engine log.'
  remote=re.search(r'CUDA1: (\d+) expert entries, (\d+) active layer launches, ([\d.]+) MiB returned.*?host ([\d.]+) ms staging\+launching, ([\d.]+) ms waiting',log)
  row.update(layer_split_actual=int(actual_K[1]) if actual_K else row['layer_split'],prefill_chunk_actual=chosen_chunk if chosen_chunk is not None else row['prefill_chunk'],prefill_chunk_resolution_note='Last upstream startup selection/reduction, or unchanged explicit CLI value when no reduction was logged.',verify_capacity=e.get('spec'),mtp_max=e.get('mtp_max'),cache_reused_tokens=d.get('cache_reused_tokens'),prompt_processing_wall_s=d.get('prompt_processing_wall_s'),decode_wall_s=d.get('decode_wall_s'),drafted=d.get('draft_tokens'),accepted=d.get('accepted_tokens'),verify_rounds=d.get('verify_rounds'),mean_accepted_length=d.get('mean_accepted_length'),CPU_routed_entries_per_layer_window=float(cpu[2]) if cpu else None,CPU_distinct_experts_per_layer_window=float(cpu[1]) if cpu else None,primary_VRAM_hits_per_layer_window=float(cpu[3]) if cpu else None,remote_returned_MiB=float(remote[3]) if remote else None,remote_staging_ms=float(remote[4]) if remote else None,remote_wait_ms=float(remote[5]) if remote else None)
  kv_cell={'int8':1056,'k8v4':816,'q4_0':576,'fp16':2048}.get(row['KV_mode'])
  context_capacity=int(e.get('context',val('--max-context',262144)));kv_res=int(val('--kv-resident',0) or 0)
  split_value=row['layer_split_actual']
  split_k=int(split_value) if str(split_value).isdigit() else None
  stage_qsa=[max(1,split_k//4),max(1,12-split_k//4)] if split_k is not None else [12,0]
  streamed=kv_res>0 and context_capacity>kv_res
  if kv_cell:
   row.update(KV_payload_bytes_capacity=12*context_capacity*kv_cell,KV_payload_bytes_logical_occupied=12*(d['actual_prompt_tokens']+d['generated_tokens'])*kv_cell,KV_payload_gpu0_bytes=stage_qsa[0]*(kv_res if streamed else context_capacity)*kv_cell,KV_payload_gpu1_bytes=stage_qsa[1]*(kv_res if streamed else context_capacity)*kv_cell,KV_payload_host_bytes=12*context_capacity*kv_cell if streamed else 0,KV_bytes_note='Derived K/V codes and scales only; excludes indexer,GDN,scratch,map/alignment. Sources kv_q8.hpp,kv_q4.hpp;12QSA layers,2heads256dims. Logical occupied excludes verify overshoot.')
  row['draft_acceptance_scope']='Normal Strata draft_n/draft_n_accepted include MTP and suffix-lookup offers; not an isolated MTP-only acceptance counter.'
  if hits:
   row['CPU_misses']=int(hits[2])-int(hits[1]);row['CPU_misses_unit']='decode routed entries in CPU branch; not distinct expert jobs'
  row['expert_counter_scope_note']='Decode cache hits/lookups exclude PCIe and helper entries. CPU=lookups-hits in the tested graphed path. Helper log counts entire request incl short-read header; do not combine scopes as exact decode shares.'
  if remote:
   row['GPU0_hit_count']=int(hits[1]) if hits else None;row['GPU1_hit_count']=int(remote[1])
  elif row['gpu_count']==1 and hits:row['GPU0_hit_count']=int(hits[1]);row['GPU1_hit_count']=0
  for i in [0,1]:
   gs=[g for s in ss for g in s.get('gpus',[]) if g['index']==i]
   row[f'GPU{i}_util']=avg([g['util_pct'] for g in gs]);row[f'GPU{i}_power']=avg([g['power_w'] for g in gs])
  row.update(phase_telemetry.summarize(d,ss))
  pss_snapshots={}
  for when in ['before','after']:
   snapshot=d.get('pss_'+when) or {}
   values=[process.get('pss_gib') for process in snapshot.values()]
   pss_snapshots[when]=sum(values) if values and all(value is not None for value in values) else None
  available_pss=[value for value in pss_snapshots.values() if value is not None]
  row.update(peak_RSS_GiB=d.get('peak_rss_gib'),PSS_before_GiB=pss_snapshots['before'],PSS_after_GiB=pss_snapshots['after'],PSS_max_snapshot_GiB=max(available_pss) if available_pss else None,PSS_measurement_note='Sum over server/engine processes in snapshots outside timed requests. Maximum of these snapshots is not an in-request PSS peak. RAM_used is VM MemTotal minus MemAvailable and is separate from RSS/PSS.')
  rows.append(row)
  if ss:
   flat=[]
   for s in ss:
    z={k:s.get(k) for k in ['wall_time','monotonic','mem_available_gib','ram_used_gib','system_cpu_pct']}
    z.update(rss_gib=sum(x['rss_gib'] for x in s['processes']),pss_gib=sum(x['pss_gib'] for x in s['processes']) if all(x.get('pss_gib') is not None for x in s['processes']) else None,process_cpu_pct=sum(x['cpu_pct'] for x in s['processes']),process_read_bytes=sum(x['read_bytes'] for x in s['processes']))
    for g in s.get('gpus',[]):
     for k in ['util_pct','power_w','vram_gib','sm_mhz','memory_mhz']:z[f'gpu{g["index"]}_{k}']=g.get(k)
    hw=s.get('metrics',{}).get('hardware',{});z.update(pcie_rx_mb_s=hw.get('gpu_pcie_rx_mb'),pcie_tx_mb_s=hw.get('gpu_pcie_tx_mb'))
    flat.append(z)
   columns=list(dict.fromkeys(k for x in flat for k in x))
   with tp.with_suffix('.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(flat)
 cols=FIELDS+list(dict.fromkeys(k for row in rows for k in row if k not in FIELDS))
 with (R/'summary.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
 (R/'summary.json').write_text(json.dumps({'status':'IN_PROGRESS','units':'RAM/VRAM in GiB; time in s; rates tokens/s. null = unavailable; GPU shares not inferred from combined hits.','rows':rows},indent=2))
if __name__=='__main__':main()
