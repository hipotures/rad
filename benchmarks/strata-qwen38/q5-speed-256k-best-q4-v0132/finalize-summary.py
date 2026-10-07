from pathlib import Path
import json,statistics,csv
r=Path(__file__).parent
s=json.loads((r/'summary.json').read_text())
assert s['status']=='COMPLETE' and len(s['measured'])==3
rows=s['measured']
assert all(a['status']=='OK' and a['actual_prompt_tokens']==259500 and a['generated_tokens']==256 and a['cache_reused_tokens']==0 and a['abort'] is None for a in rows)
for k in ['prompt_processing_wall_s','decode_wall_s','peak_rss_gib','mean_accepted_length','acceptance_pct','final_kv_occupancy_tokens']:
 s['median'][k]=statistics.median(a[k] for a in rows)
s['peak_across_measured']['peak_rss_gib']=max(a['peak_rss_gib'] for a in rows)
s['prefill']={'configured_chunk_tokens':32768,'actual_chunk_tokens':16384,'evidence':'logs/Q5-BEST-Q4-K24-259500-engine.log and references Q4 engine log; runtime reduced chunk to fit both expert caches'}
s['all_zero_prompt_reuse']=True
s['all_no_abort']=True
s['comparison_classification']='NOT_CONTROLLED_A_B'
s['expert_file_stats']=[{'run':i+1,'expert_tiers':a['expert_tiers']} for i,a in enumerate(rows)]
s['expert_io_note']='Normal expert counters report file_mb=0. Full routed arena in RAM. Native PLE mmap is separate; these counters do not prove absence of all physical host storage I/O on virtiofs.'
(r/'summary.json').write_text(json.dumps(s,indent=2)+'\n')
fields=['model','run','actual_prompt_tokens','generated_tokens','pp_tps','tg_tps','ttft_s','prompt_processing_wall_s','decode_wall_s','peak_ram_used_gib','peak_rss_gib','peak_vram0_gib','peak_vram1_gib','acceptance_pct','mean_accepted_length']
with (r/'summary.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
 for i,a in enumerate(rows):w.writerow(dict(a,model='UD-Q5_K_XL',run=i+1))
 w.writerow(dict(s['median'],model='UD-Q5_K_XL',run='median'))
 w.writerow(dict(s['Q4_reference_median'],model='UD-Q4_K_XL historical',run='median',actual_prompt_tokens=259500,generated_tokens=256))
m=s['median']
with (r/'report.md').open('a') as f:
 f.write('\nConfigured prefill chunk:32768; actual chunk:16384 for both historical Q4 and Q5.\n')
 f.write(f'\nQ5 median prompt processing wall:{m["prompt_processing_wall_s"]:.3f}s; decode wall:{m["decode_wall_s"]:.3f}s; MTP acceptance:{m["acceptance_pct"]:.2f}%; mean accepted length:{m["mean_accepted_length"]:.3f}.\n')
 f.write(f'\nPeak process RSS:{s["peak_across_measured"]["peak_rss_gib"]:.3f}GiB includes file-backed mappings; peak system RAM usage is reported separately.\n')
 f.write('\nComparison classification:NOT_CONTROLLED_A_B (historical Q4, Q5 support patches and native PLE mmap). Routed-expert file counters:0 MB for all measured requests; no claim about all host physical storage I/O.\n')
print(json.dumps({'median':s['median'],'peak':s['peak_across_measured'],'delta':s['delta_vs_Q4_median_pct'],'GPU_compute_apps_after':s['GPU_compute_apps_after'],'model_stat_unchanged':s['model_stat_unchanged'],'clean_checkout_tracked_unchanged':s['clean_checkout_tracked_unchanged']},indent=2))
