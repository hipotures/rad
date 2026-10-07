from pathlib import Path
import json,statistics,csv,subprocess,time
R=Path(__file__).parent;t=json.loads((R/'terminal.json').read_text());rows=[json.loads((R/'raw'/f'IQ3S-v0138-{a["repeat_tag"]}.json').read_text()) for a in t['valid']];med=statistics.median
assert t['status']=='COMPLETE' and len(rows)==12
cells=[]
for target in [31400,63400,127000,259500]:
 a=[x for x in rows if x['target_prompt_tokens']==target];assert len(a)==3
 c={'target_prompt_tokens':target,'actual_prompt_tokens':[x['actual_prompt_tokens'] for x in a],'actual_prompt_median':med(x['actual_prompt_tokens'] for x in a),'n':3,'split_K':a[0]['selected_layer_split_K'],'GPU0_slots':a[0]['GPU0_slots'],'GPU1_slots':a[0]['GPU1_slots'],'raw_paths':[str(R/'raw'/f'IQ3S-v0138-{x["repeat_tag"]}.json') for x in a]}
 for k in ['pp_tps','tg_tps','ttft_s','total_wall_s','prompt_processing_wall_s','decode_wall_s','acceptance_pct','mean_accepted_length','draft_tokens','accepted_tokens','peak_ram_used_gib','peak_rss_gib','peak_vram0_gib','peak_vram1_gib']:
  vals=[x[k] for x in a if isinstance(x.get(k),(int,float))];c[k]={'min':min(vals),'median':med(vals),'max':max(vals)} if vals else None
 hits=[x['expert_tiers']['hit_rate'] for x in a if isinstance(x.get('expert_tiers',{}).get('hit_rate'),(int,float))];c['hit_rate_median']=med(hits) if hits else None
 c['expert_file_mb_decode']=[x['expert_tiers'].get('file_mb') for x in a]
 for phase in ['decode','prefill']:
  d={};c[phase+'_telemetry']=d;agg=[x['telemetry_aggregates'][phase] for x in a]
  for key in ['system_cpu_pct_mean','system_cpu_pct_peak','process_cpu_pct_mean','process_cpu_pct_peak']:
   vals=[x[key] for x in agg if x[key] is not None];d[key+'_median']=med(vals) if vals else None
  d['samples_per_run']=[x['samples'] for x in agg]
  for i in [0,1]:
   for key in ['util_pct_mean','power_w_mean']:
    vals=[x['GPU'][str(i)][key] for x in agg if x['GPU'][str(i)][key] is not None];d[f'GPU{i}_{key}_median']=med(vals) if vals else None
 cells.append(c)
old=[];base=R.parent
for target in [63400,259500]:
 ps=[base/'q4-v0132/raw'/f'IQ3-upgrade-control-{target}-run{i}.json' for i in [1,2,3]];a=[json.loads(p.read_text()) for p in ps]
 assert all(x['Strata_version']=='0.1.32' and x['status']=='OK' and x['actual_prompt_tokens']==target and x['generated_tokens']==256 and x['cache_reused_tokens']==0 for x in a)
 new=next(c for c in cells if c['target_prompt_tokens']==target)
 old.append({'version':'0.1.32','target':target,'n':3,'raw_paths':list(map(str,ps)),'PP_median':med(x['pp_tps'] for x in a),'TG_median':med(x['tg_tps'] for x in a),'TTFT_median':med(x['ttft_s'] for x in a),'classification':'NOT_CONTROLLED_A_B','note':'New unique prompt payloads, same old production config except runtime and offline system policy; historical data, no alternating A/B.'})
 for key,k in [('PP','pp_tps'),('TG','tg_tps')]:old[-1][key+'_delta_pct']=100*(new[k]['median']/old[-1][key+'_median']-1)
for target,name in [(31400,'32K'),(127000,'128K')]:
 ps=[base/'results/raw'/f'IQ3_S-{name}-{i}.json' for i in [1,2,3]];a=[json.loads(p.read_text()) for p in ps]
 old.append({'version':'0.1.31','target':target,'n':3,'raw_paths':list(map(str,ps)),'PP_median':med(x['pp_tps'] for x in a),'TG_median':med(x['tg_tps'] for x in a),'classification':'NOT_CONTROLLED_A_B','note':'Original campaign HEAD9259cad4 / v0.1.31. No v0.1.32 measured32K/128K IQ3_S raw records found. Earlier campaign; different runtime/payloads, retained only as explicitly versioned descriptive baseline.'})
comparison5090=[]
for target,reference in [(31400,170.4),(259500,152.5)]:
 c=next(c for c in cells if c['target_prompt_tokens']==target);tg=c['tg_tps']['median'];comparison5090.append({'actual_prompt_target':target,'RTX5090_TG_user_supplied':reference,'our_2x4090_TG_median':tg,'difference_pct':100*(tg/reference-1),'classification':'NOT_CONTROLLED_A_B','note':'External reference values supplied by user; different machine/potentiallyconfig, not independently verified published raw data.'})
m=json.loads((R/'model-provenance.json').read_text());unchanged=all(Path(x['path']).stat().st_size==x['size'] and Path(x['path']).stat().st_mtime_ns==x['mtime_ns'] for x in m['files']+m['pack_files']);assert unchanged
s={'status':'COMPLETE','completed_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'Strata_HEAD':'99f3dbd0b21d1401b3769e0c0d963913607f380b','version':'0.1.38','config':str(R/'configs/IQ3S-v0138.json'),'environment':str(R/'environment.json'),'model_provenance':str(R/'model-provenance.json'),'model_stat_unchanged':unchanged,'layout':t['layout'],'cells':cells,'old_comparison':old,'RTX5090_comparison':comparison5090,'warmups_excluded':len(t['warmups']),'invalid_runs':t['excluded'],'GPU_apps_after':t['GPU_apps_after'],'git_status_after':t['git_status_after'],'measured_raw':rows}
(R/'summary.json').write_text(json.dumps(s,indent=2)+'\n')
with (R/'summary.csv').open('w',newline='') as f:
 fields=['actual_prompt','PP_min','PP_median','PP_max','TG_min','TG_median','TG_max','TTFT_median','MTP_accept_pct','hit_rate','split_K','GPU0_slots','GPU1_slots'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for c in cells:w.writerow({'actual_prompt':c['actual_prompt_median'],**{f'{name}_{stat}':c[key][stat] for name,key in [('PP','pp_tps'),('TG','tg_tps')] for stat in ['min','median','max']},'TTFT_median':c['ttft_s']['median'],'MTP_accept_pct':c['acceptance_pct']['median'],'hit_rate':c['hit_rate_median'],'split_K':c['split_K'],'GPU0_slots':c['GPU0_slots'],'GPU1_slots':c['GPU1_slots']})
lines=['# IQ3_S — Strata v0.1.38 — 2× RTX4090','', 'Status:COMPLETE.12valid measured requests;4warmups excluded. Each actualprompt verified by upstream tokenizer and API; greedy256 output, finish_reason=length, reuse=0, unique prefix nonce, sequential. Noenginepatches/modelchanges/download/commit/push. Maxcontext262144 for every run.','', 'ExactHEAD99f3dbd0b21d1401b3769e0c0d963913607f380b; tagv0.1.38; CUDARelease sm89defaultbuild. Fullprovenance:environment.json, model-provenance.json, configs/IQ3S-v0138.json. SHA256 both localshards verifiedagainst pinnedHFmanifest. Existingpack reused.','', 'Preserved oldproductionconfig:INT8KV,kv-resident32768,spec4,min-p0.5,prefillauto,expertcacheauto,auto layersplit,oldprofileandMTP. KVstreaming retained deliberately; not a newlytuned fullyresidentKV candidate. PSS only before/afterrequest;1HzRSS/CPU/GPU/RAManddmonPCIe. CPUprocess100%=one logicalCPU, system100%=all16vCPUs.','', '| Actual prompt | PP median | TG median | TTFT median s | MTP accept % | hit rate % | split K |','|---:|---:|---:|---:|---:|---:|---:|']
for c in cells:lines.append(f'| {c["actual_prompt_median"]} | {c["pp_tps"]["median"]:.1f} | {c["tg_tps"]["median"]:.1f} | {c["ttft_s"]["median"]:.3f} | {c["acceptance_pct"]["median"]:.2f} | {100*c["hit_rate_median"]:.2f} | {c["split_K"]} |')
lines+=['','## Spread of3 measured runs','','| Actualprompt | PPmin | PPmedian | PPmax | TGmin | TGmedian | TGmax |','|---:|---:|---:|---:|---:|---:|---:|']
for c in cells:lines.append('| '+str(c['actual_prompt_median'])+' | '+' | '.join(f'{c[k][v]:.1f}' for k in ['pp_tps','tg_tps'] for v in ['min','median','max'])+' |')
lines+=['','## Expert cache','','```json',json.dumps(t['layout'],indent=2),'```','','Capacities fromstartup; promptbuffers temporarily borrow expertslots. Expert fileMB fromnormaldecodecounters for eachrun:']
for c in cells:lines.append(f'- {c["target_prompt_tokens"]}: {c["expert_file_mb_decode"]}')
lines+=['','## Decode CPU/GPU telemetry','','256-token decode lasts only a fewseconds.1Hz samples are sparse and do not establish sustainedbottleneck or whether unsampled shortCPUpeaks hit100%. CPUusage below is systemnormalized; processCPU may exceed100%. PCIe RX/TX rawlog intelemetry/IQ3S-v0138-pcie-dmon.log. No inventedcounters ifunsupported.','','| Actualprompt | Samples/run | CPU mean % | CPU peak % | Process CPU mean % | GPU0 mean % | GPU1 mean % | GPU0 W | GPU1 W |','|---:|---|---:|---:|---:|---:|---:|---:|---:|']
for c in cells:
 d=c['decode_telemetry'];keys=['system_cpu_pct_mean_median','system_cpu_pct_peak_median','process_cpu_pct_mean_median','GPU0_util_pct_mean_median','GPU1_util_pct_mean_median','GPU0_power_w_mean_median','GPU1_power_w_mean_median'];fmt=lambda x:'N/A' if x is None else f'{x:.1f}'
 lines.append('| '+str(c['target_prompt_tokens'])+' | '+str(d['samples_per_run'])+' | '+' | '.join(fmt(d[k]) for k in keys)+' |')
lines+=['','## Previous local runs — NOT_CONTROLLED_A_B','','v0.1.32 raw IQ3_S available only64K/256K.32K/128K numbers that were attributed to0.1.32 in conversation actually come fromoriginal0.1.31. Those two archivalcells are not v0.1.32 results.','','| Previous version | Actualprompt | PreviousPP | PreviousTG | PP delta% | TG delta% |','|---|---:|---:|---:|---:|---:|']
for x in sorted(old,key=lambda x:x['target']):lines.append(f'| {x["version"]} | {x["target"]} | {x["PP_median"]:.1f} | {x["TG_median"]:.1f} | '+(f'{x["PP_delta_pct"]:+.2f}' if 'PP_delta_pct' in x else 'N/A (v0.1.31 baseline)')+' | '+(f'{x["TG_delta_pct"]:+.2f}' if 'TG_delta_pct' in x else 'N/A (v0.1.31 baseline)')+' |')
lines+=['','## RTX5090 reference — NOT_CONTROLLED_A_B','','User-supplied publishedTGreference, differentmachine/potentiallyconfig. No purehardwareA/B inference.','','| Actualprompt | 1×5090 TG reference | 2×4090 TG median | Difference % |','|---:|---:|---:|---:|']
for x in comparison5090:lines.append(f'| {x["actual_prompt_target"]} | {x["RTX5090_TG_user_supplied"]:.1f} | {x["our_2x4090_TG_median"]:.1f} | {x["difference_pct"]:+.2f} |')
lines+=['','## Invalid/negative runs','','```json',json.dumps(t['excluded'],indent=2),'```','','Raw JSON contains fullenginecommand/config/runtimehead/buildrevision/tokenusage/finishreason andtelemetrypaths. Completeprompts/responses/SSEchunks/engineperrequestlogs/status/metrics preserved inraw/. Historicalresults untouched. Runtime stopped; bothGPUsfree.']
(R/'report.md').write_text('\n'.join(lines)+'\n')
status=json.loads((R/'STATUS.json').read_text());status['next_exact_action']='Read completed report.md, summary.csv, summary.json. No benchmark requests remain.';(R/'STATUS.json').write_text(json.dumps(status,indent=2)+'\n');(R/'STATUS.md').write_text('# COMPLETE\n\n'+json.dumps(status,indent=2)+'\n')
print(json.dumps({'cells':cells,'old':old,'reference5090':comparison5090},indent=2))
