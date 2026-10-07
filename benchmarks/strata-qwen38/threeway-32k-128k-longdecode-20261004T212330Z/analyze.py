import json,csv,statistics,datetime,hashlib,re
from pathlib import Path
import enrich
R=Path(__file__).resolve().parent

def progression(a):
 p=Path(a['telemetry_file']);samples=[json.loads(x) for x in p.read_text().splitlines()];t0=a['t_first_monotonic_s'];t1=a['t_end_monotonic_s'];points=[(0,t0)]
 for x in samples:
  live=(x.get('metrics') or {}).get('live') or {};n=live.get('generated')
  if n is not None and t0<=x['monotonic']<=t1 and n>points[-1][0]:points.append((n,x['monotonic']))
 points.append((a['generated_tokens'],t1))
 boundaries={}
 for n in sorted(set([0,512,1024,2048]+[n for n in [4096,8192] if n<a['generated_tokens']]+[a['generated_tokens']])):
  if n==0:boundaries[n]={'estimate':t0,'lower':t0,'upper':t0};continue
  if n==a['generated_tokens']:boundaries[n]={'estimate':t1,'lower':t1,'upper':t1};continue
  for (n0,tb),(n1,te) in zip(points,points[1:]):
   if n0<=n<=n1:
    boundaries[n]={'estimate':tb+(te-tb)*(n-n0)/(n1-n0),'lower':tb,'upper':te};break
 intervals=[]
 edges=sorted(set([0,512,1024,2048]+[n for n in [4096,8192] if n<a['generated_tokens']]+[a['generated_tokens']]))
 for start,end in zip(edges,edges[1:]):
  b,e=boundaries.get(start),boundaries.get(end)
  if b is None or e is None:continue
  d=e['estimate']-b['estimate'];slow=e['upper']-b['lower'];fast=e['lower']-b['upper']
  intervals.append({'output_start':start,'output_end':end,'tg_estimate':(end-start)/d if d>0 else None,'tg_lower_bound':(end-start)/slow if slow>0 else None,'tg_upper_bound':(end-start)/fast if fast>0 else None,'cumulative_tg_estimate':end/(e['estimate']-t0),'boundary_uncertainty_s':max(b['upper']-b['lower'],e['upper']-e['lower'])})
 return {'basis':'1Hz API live.generated integer counts; linear interpolation with timestamp brackets. Client/SSE wall interval, not exact engine per-token times. First-token anchor zero has ~1-token offset. No interval cache/MTP counters exposed.','points':points,'boundaries':boundaries,'intervals':intervals}

def analyze():
 rows=[];cells=[]
 for f in sorted((R/'raw').glob('*-done.json')):
  done=json.loads(f.read_text())
  if done.get('status')!='COMPLETE':continue
  for p in done['runs']:
   a=json.loads(Path(p).read_text());a['raw_path']=p;a['initial_layout']={'primary':done['layout']['primary_slots'],'helper':done['layout']['helper_slots'],'layer_split_K':done['layout']['K']}
   a['variant']=done['variant'];a['context_label']=done['context'];a=enrich.enrich(a);a['decode_progression']=progression(a)
   a['mapped_RAM_PCIE_entries']=a.get('offloaded_routed_entries') if a['variant']!='HELPER' else a['offloaded_routed_entries']-a['helper_entries'] if a.get('offloaded_routed_entries') is not None and a.get('helper_entries') is not None else None
   a['cache_admissions']=None;a['cache_evictions']=None;a['cache_hit_progression']=None;a['MTP_progression']=None
   rows.append(a)
 for variant,ctx in sorted(set((x['variant'],x['context_label']) for x in rows)):
  rs=[a for a in rows if a['variant']==variant and a['context_label']==ctx];assert len(rs)==3
  cell={'config':variant,'context':ctx,'valid_runs':3,'actual_prompt_tokens':statistics.median(a['actual_prompt_tokens'] for a in rs),'raw_paths':[a['raw_path'] for a in rs]}
  keys=['pp_tps','tg_tps','ttft_s','total_wall_s','acceptance_pct','mean_accepted_length','verify_windows','mean_verify_window_latency_ms','draft_tokens','accepted_tokens','reported_expert_hit_rate','cpu_fallback_entries','primary_hits_exact','mapped_RAM_PCIE_entries','helper_entries','decode_cpu_system_pct','decode_cpu_system_pct_peak','decode_cpu_process_pct','gpu0_decode_util_pct','gpu1_decode_util_pct','gpu0_decode_power_w','gpu1_decode_power_w','gpu0_decode_pcie_rx_MBps','gpu1_decode_pcie_rx_MBps','GPU_reach_wait_ms_per_window','CPU_work_ms_per_window','primary_hits_per_layer_window','pcie_experts_per_layer_window','helper_wait_ms','peak_rss_gib','peak_ram_used_gib','peak_vram0_gib','peak_vram1_gib','initial_primary_slot_capacity','initial_helper_slot_capacity','selected_layer_split_K']
  for k in keys:
   vals=[x[k] for x in rs if x.get(k) is not None];cell[k]=statistics.median(vals) if vals else None
   if k in ['pp_tps','tg_tps']:cell[k+'_min']=min(vals);cell[k+'_max']=max(vals)
  for idx,label in enumerate(['0_512','512_1024','1024_2048','2048_final']):
   for k in ['tg_estimate','tg_lower_bound','tg_upper_bound','boundary_uncertainty_s']:
    vals=[a['decode_progression']['intervals'][idx][k] for a in rs if len(a['decode_progression']['intervals'])>idx and a['decode_progression']['intervals'][idx].get(k) is not None];cell[f'interval_{label}_{k}']=statistics.median(vals) if vals else None
  cells.append(cell)
 out={'cells':cells,'runs':rows};(R/'summary.json').write_text(json.dumps(out,indent=2))
 with (R/'summary.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(cells[0]));writer.writeheader();writer.writerows(cells)
 (R/'analysis/progression.json').write_text(json.dumps({a['raw_path']:a['decode_progression'] for a in rows},indent=2))
 print([(c['config'],c['context'],c['pp_tps'],c['tg_tps'],c['tg_tps_min'],c['tg_tps_max'],[c.get('interval_'+k+'_tg_estimate') for k in ['0_512','512_1024','1024_2048','2048_final']]) for c in cells])
 return out
if __name__=='__main__':analyze()
