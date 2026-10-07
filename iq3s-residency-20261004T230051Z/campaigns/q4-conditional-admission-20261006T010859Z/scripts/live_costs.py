"""Aggregate reported timing only: no causal decomposition from overlapping timers."""
from campaign import C,load,save
from pathlib import Path
import re,statistics
rows=[]
pat=re.compile(r'strata decode timing: (\d+) windows, avg T ([\d.]+), ([\d.]+) tokens/window, ([\d.]+) ms/window = verify ([\d.]+) \(GPU-reach wait ([\d.]+) \+ per-layer host ([\d.]+) \[plan ([\d.]+) actq ([\d.]+) jobs ([\d.]+) CPU ([\d.]+)\] \+ stage ([\d.]+)\) \+ commit/emit ([\d.]+) \+ draft ([\d.]+)')
names=['windows','avg_T','tokens_per_window','window_ms','verify_ms','GPU_reach_wait_ms','host_ms','plan_ms','activation_quant_ms','jobs_ms','CPU_completion_ms','stage_ms','commit_emit_ms','draft_ms']
for r in load(C/'analysis/live-records.json'):
 p=Path(r['raw_result']).parent/'raw/run-engine.log';m=pat.search(p.read_text());assert m,p
 d={k:float(v) for k,v in zip(names,m.groups())};d.update(context=r['context'],variant=r['variant'],replicate=r['replicate'],TG=r['TG'],wall_s=r['wall_s'],decode_s=r['decode_s'],CPU_entries=r['cpu_fallback_entries'],approx_CPU_unique_jobs=r.get('approx_CPU_unique_jobs'),all_routed_entries=r['all_routed_entries'],MTP_acceptance_pct=r['mtp_acceptance_pct']);d['feature_plus_gate_ms']=(r.get('feature_ms') or 0)+(r.get('score_selection_ms') or 0) if r['variant']=='conditional' else None;d['old_early_history_ms']=r.get('algorithm_tracker_ms');d['scorer_plus_all_history_pct_of_decode']=100*(d['feature_plus_gate_ms']+(d['old_early_history_ms'] or 0))/1000/r['decode_s'] if d['feature_plus_gate_ms'] is not None else None
 d['copy_timers_reported']=r['admission'].get('Q4_EARLY');rows.append(d)
summary=[]
for ctx in ['32k','128k','256k']:
 for v in ['control','conditional']:
  rs=[d for d in rows if d['context']==ctx and d['variant']==v];summary.append({'context':ctx,'variant':v,'runs':len(rs),**{k:statistics.median(d[k] for d in rs if d[k] is not None) if any(d[k] is not None for d in rs) else None for k in names+['TG','wall_s','CPU_entries','approx_CPU_unique_jobs','feature_plus_gate_ms','old_early_history_ms','scorer_plus_all_history_pct_of_decode']}})
save(C/'analysis/reported-timing-costs.json',{'runs':rows,'medians':summary,'interpretation':['Timers are rounded reported per-verifier-window averages; CPU completion includes waits and overlaps GPU/host work, not exclusive expert arithmetic.','Model input IDs are paired, outputs/MTP/routing diverge; changed expert distribution can change CPU cost even with more CPU entries.','Both binaries have identical actual ggml CPU compile flags and linked libraries; see git/CPU-build-flags-audit.json.','Feature/gate plus old early history percentage omits additional GPU H4 prediction, publication and copy waits; it is not the total algorithm overhead.']})
print('COST_ANALYSIS',len(rows),flush=True)
