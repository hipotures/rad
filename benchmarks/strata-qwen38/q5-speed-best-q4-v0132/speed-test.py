import run as r,workloads as w,json,hashlib,statistics,subprocess,time,traceback
from pathlib import Path
R=r.ROOT;plan=json.loads((R/'plan.json').read_text());env=json.loads((R/'environment.json').read_text());result={'status':'RUNNING','plan':plan,'measured':[],'warmup':None,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
def status(phase,state='RUNNING'):
 r.c.save(R/'STATUS.json',{'status':state,'running':phase,'completed':['Q4 raw/parameters saved']+(['warmup excluded'] if result['warmup'] else [])+[f'measured run {i+1}' for i in range(len(result['measured']))],'pending':[f'measured run {i+1}' for i in range(len(result['measured']),3)]+(['median/comparison report'] if state!='COMPLETE' else []),'next_exact_action':phase or 'Read completed report.md and summary.json'})
 import importlib.util
 spec=importlib.util.spec_from_file_location('sr',R/'status-render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.render()
def check(a):
 assert a['status']=='OK',a.get('error')
 assert a['actual_prompt_tokens']==31400 and a['actual_prompt_tokens_tokenizer']==31400,a
 assert a['generated_tokens']==256,a.get('finish_reasons')
 assert a['cache_reused_tokens']==0 and a['abort'] is None and a['min_mem_available_gib']>=12
 assert a['draft_tokens']>0,'MTP inactive'
try:
 assert hashlib.sha256(Path('/srv/ai/strata-v0.1.32-q5/build-ple-q8/strata').read_bytes()).hexdigest()==env['engine_SHA256']
 assert r.c.psutil.virtual_memory().available/r.c.GIB>115
 # Exact tokenizer and template equality with the historical Q4 reference.
 for f in ['vocab.json','merges.txt','token_type.json','chat_template.jinja']:
  assert hashlib.sha256((Path('/srv/ai/models/strata/packs/ud-q5_k_xl-v0132/tokenizer')/f).read_bytes()).digest()==hashlib.sha256((Path('/srv/ai/models/strata/packs/ud-q4_k_xl-v0132/tokenizer')/f).read_bytes()).digest()
 label='Q5-BEST-Q4-K24-31400';cfg=r.config(label,'split',split=24,context=262144)
 status('load Q5, 2GPU K24')
 with r.Session(label,cfg) as s:
  payloads=[json.loads((R/'references/warmup-payload.json').read_text())]+[json.loads((R/'references'/f'PP-CONTROL-31400-run{i}-request.json').read_text()) for i in [1,2,3]]
  assert len({json.dumps(p['messages'],sort_keys=True) for p in payloads})==4
  for n,payload in enumerate(payloads):
   payload['model']=cfg['model_name'];assert s.run.count(payload['messages'])==31400
   tag='warmup' if n==0 else f'run{n}';status(f'{tag}: actual 31400 + 256')
   print('START',tag,time.strftime('%H:%M:%S',time.gmtime()),flush=True)
   rec=w.request(s,payload['messages'],256,tag,kind='warmup' if n==0 else 'measured',exact_payload=payload);check(rec)
   if n==0:result['warmup']=rec
   else:result['measured'].append(rec)
   r.c.save(R/'summary.json',result)
   print('FINISH',tag,'PP',rec['pp_tps'],'TG',rec['tg_tps'],'TTFT',rec['ttft_s'],flush=True)
 result['status']='COMPLETE'
except BaseException as e:
 result.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());print('STOP',repr(e),flush=True)
finally:
 result['GPU_compute_apps_after']=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True)
 result['clean_checkout_tracked_unchanged']=not subprocess.check_output(['git','diff','--name-only'],cwd='/srv/ai/strata-v0.1.32',text=True).strip()
 result['model_stat_unchanged']=all((lambda st,x:st.st_size==x['size'] and st.st_mtime_ns==x['mtime_ns'] and st.st_ino==x['inode'])(Path(x['path']).stat(),x) for x in env['model_stat_before'])
 if len(result['measured'])==3:
  keys=['pp_tps','tg_tps','ttft_s','total_wall_s','pp_ms','decode_ms','actual_prompt_tokens','generated_tokens','peak_ram_used_gib','peak_vram0_gib','peak_vram1_gib','min_mem_available_gib','draft_tokens','accepted_tokens']
  result['median']={k:statistics.median(a[k] for a in result['measured'] if isinstance(a.get(k),(int,float))) for k in keys if any(isinstance(a.get(k),(int,float)) for a in result['measured'])}
  result['Q4_reference_median']={k:statistics.median(a[k] for a in plan['references']) for k in ['pp_tps','tg_tps','ttft_s']}
  result['Q4_reference_fastest']=max(plan['references'],key=lambda x:x['tg_tps'])
  result['delta_vs_Q4_median_pct']={k:100*(result['median'][k]/result['Q4_reference_median'][k]-1) for k in ['pp_tps','tg_tps','ttft_s']}
  result['peak_across_measured']={k:max(a[k] for a in result['measured']) for k in ['peak_ram_used_gib','peak_vram0_gib','peak_vram1_gib']}
 r.c.save(R/'summary.json',result);status(None,result['status'])
 report=['# Q5 actual 31,400 tokens speed test — K24 / two RTX4090','',f'Status: {result["status"]}','',plan['comparison'],'','1 warmup excluded; 3 sequential measured runs. Actual prompt checked with tokenizer and API. Literal saved Q4 prompts, only model alias changed. Greedy,256 output; no prefix reuse; max context262144. No model download or weights changes. Existing patched runtime/head/build/commands recorded per raw result. Cheap telemetry1Hz; PSS only before/after request; MemAvailable floor12GiB.','']
 if 'median' in result:
  m=result['median'];q=result['Q4_reference_median'];f=result['Q4_reference_fastest']
  report += ['| model | actual prompt | output | PP tok/s | TG tok/s | TTFT s |','|---|---:|---:|---:|---:|---:|',f'| Q4 historical median ×3 | 31400 | 256 | {q["pp_tps"]:.1f} | {q["tg_tps"]:.1f} | {q["ttft_s"]:.3f} |',f'| Q4 historical fastest | 31400 | 256 | {f["pp_tps"]:.1f} | {f["tg_tps"]:.1f} | {f["ttft_s"]:.3f} |',f'| Q5 median ×3 | 31400 | 256 | {m["pp_tps"]:.1f} | {m["tg_tps"]:.1f} | {m["ttft_s"]:.3f} |','','| Q5 run | PP tok/s | TG tok/s | TTFT s |','|---|---:|---:|---:|']
  report += [f'| {i+1} | {a["pp_tps"]:.1f} | {a["tg_tps"]:.1f} | {a["ttft_s"]:.3f} |' for i,a in enumerate(result['measured'])]
  report += ['',f'Delta against Q4 median: PP {result["delta_vs_Q4_median_pct"]["pp_tps"]:.1f}%; TG {result["delta_vs_Q4_median_pct"]["tg_tps"]:.1f}%.','',f'Peak measured RAM(system total minus available):{result["peak_across_measured"]["peak_ram_used_gib"]:.2f}GiB; VRAM0/1:{result["peak_across_measured"]["peak_vram0_gib"]:.2f}/{result["peak_across_measured"]["peak_vram1_gib"]:.2f}GiB.','', 'Q5 routes unsupported Q6_K/Q8_0 layer2 wholly through CPU and reads native Q8_0 PLE with mmap. Q4 used the original runtime/default PLE I/O. This is the same workload/topology/settings comparison, with required model-specific support changes, not an isolated quant-only/runtime-only A/B. No quality conclusion.']
 else:report += [result.get('error',''),'',f'Completed measured requests: {len(result["measured"])}. No fabricated medians.']
 report += ['', 'Raw requests, complete output/streams/stats:raw/. Historical references:references/. Telemetry:telemetry/. Full config:configs/. Plan:plan.json. Summary:summary.json. Earlier smoke and failed loader tests untouched. Both servers stopped after this test.']
 (R/'report.md').write_text('\n'.join(report)+'\n')
if result['status']!='COMPLETE':raise SystemExit(1)
