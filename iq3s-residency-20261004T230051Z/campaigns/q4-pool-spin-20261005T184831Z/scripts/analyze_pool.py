"""Raw-only analysis; no inference and no extra measured repetitions."""
import csv, datetime, hashlib, json, math, pathlib, re, statistics
from lab import load, save
from pool_spin import C, POLICIES

def stats(v):
 v=[x for x in v if x is not None]
 return {'min':min(v),'median':statistics.median(v),'max':max(v),'mean':statistics.mean(v)} if v else None

def phases(r):
 rows=[json.loads(s) for s in pathlib.Path(r['telemetry']['path']).read_text().splitlines()]
 start=r['started_epoch'];first=start+r['TTFT_s'];end=start+r['wall_s'];out={}
 for name,lo,hi in [('prefill',start,first),('decode',first,end)]:
  q=[x for x in rows if lo<=x['wall_time']<hi];cpu=[x for x in q if x is not rows[0]]
  out[name]={'sample_count':len(q),'CPU_VM_pct':stats([x['system_cpu_pct'] for x in cpu]),'CPU_process_one_core100':stats([sum(p['cpu_pct'] for p in x['processes']) for x in cpu if x['processes']]),'RAM_used_GiB':stats([x['ram_used_gib'] for x in q]),'RAM_available_GiB':stats([x['mem_available_gib'] for x in q]),'RSS_sum_GiB':stats([sum(p['rss_gib'] for p in x['processes']) for x in q if x['processes']]),'GPUs':{}}
  for device in [0,1]:
   g=[g for x in q for g in x.get('gpus',[]) if g['index']==device]
   out[name]['GPUs'][str(device)]={k:stats([x[k] for x in g]) for k in ['util_pct','power_w','vram_mib','sm_mhz']}
 return out

def decode_timing(path):
 text=path.read_text();m=re.search(r'(strata decode timing: .*?)\n',text);line=m[1] if m else ''
 patterns={'window_ms':r'([\d.]+) ms/window','GPU_reach_wait_ms':r'GPU-reach wait ([\d.]+)','CPU_completion_ms':r' CPU ([\d.]+)\]','activation_quantization_ms':r'actq ([\d.]+)','CPU_distinct_experts_per_layer_window':r'CPU experts ([\d.]+)','CPU_entries_per_layer_window':r'CPU experts [\d.]+ \(([\d.]+) entries\)','CPU_job_submission_ms':r'jobs ([\d.]+)'}
 return {'line':line,'components':{k:float(m[1]) if (m:=re.search(p,line)) else None for k,p in patterns.items()},'CPU_positive_wait_ms':None,'all_local_wait_floor_ms':None,'missing_note':'The unmodified frozen binary prints an aggregate CPU completion mean, not CPU-positive/all-local conditional waits or worker sleep/wake counters.'}

def analyze():
 runs=[];warm=[]
 for policy in POLICIES:
  for profile in ['32k','128k']:
   for rep in [1,2,3]:
    base=C/'raw'/policy/profile/f'rep{rep}';rs=load(base/'results.json');assert len(rs)==1;r=rs[0]
    assert r['state']=='VALID' and r['actual_output_tokens']==4096 and r['reuse']==0 and r['actual_engine_input_verified']
    w=load(base/'raw/warmup.json');assert w['state']=='VALID' and w['actual_input_tokens']==4096 and w['actual_output_tokens']==64 and w['actual_engine_input_verified']
    resource=load(base/'raw/resource-check.json');env=load(base/'raw/actual-engine-environment.json');perf={k:r.get(k) for k in ['PP','TG','TTFT_s','wall_s','pp_s','decode_s','actual_input_tokens','actual_output_tokens','reuse','finish_reason','mtp_proposed','mtp_accepted','mtp_acceptance_pct','verify_windows','mtp_accepted_per_window','local_vram_entries','local_vram_share_all_pct','cpu_fallback_entries','nonlocal_gpu_entries','all_routed_entries','cpu_share_all_pct']}
    met=load(base/'raw/measured-metrics.json');matches=[x for x in met.get('requests',[]) if x.get('prompt_tokens')==r['actual_input_tokens'] and x.get('output_tokens')==4096]
    perf['expert_file_blobs_decode']=(matches[0].get('file_blobs') if matches else None)
    x={'policy':policy,'profile':profile,'replicate':rep,'path':str(base),'raw':str(base/'raw/measured.json'),'performance':perf,'input_sha256':r['actual_engine_input']['sha256'],'output_sha256':r['actual_output_ids_sha256'],'resource':resource,'environment':env,'system':phases(r),'decode_timing':decode_timing(base/'raw/measured-engine.log')};runs.append(x)
    warm.append({'policy':policy,'profile':profile,'replicate':rep,'input':w['actual_input_tokens'],'output':w['actual_output_tokens'],'input_sha256':w['actual_engine_input']['sha256'],'output_sha256':w['actual_output_ids_sha256']})
 assert len(runs)==24 and len(list((C/'raw').glob('*/*/rep*/results.json')))==24
 assert len({w['input_sha256'] for w in warm})==1
 cells=[]
 for policy in POLICIES:
  for profile in ['32k','128k']:
   rr=[r for r in runs if r['policy']==policy and r['profile']==profile]
   agg={k:stats([r['performance'].get(k) for r in rr]) for k in rr[0]['performance'] if k not in ['finish_reason']}
   for key in ['CPU_VM_pct','CPU_process_one_core100']:
    agg[key]=stats([r['system']['decode'][key]['mean'] if r['system']['decode'][key] else None for r in rr])
   for key in rr[0]['decode_timing']['components']:agg[key]=stats([r['decode_timing']['components'][key] for r in rr])
   for device in ['0','1']:
    for phase in ['prefill','decode']:
     for key in ['util_pct','power_w','vram_mib']:
      agg[f'GPU{device}_{phase}_{key}']=stats([r['system'][phase]['GPUs'][device][key]['mean'] if r['system'][phase]['GPUs'][device][key] else None for r in rr])
   res=rr[0]['resource'];assert all((r['resource']['primary_slots'],r['resource']['helper_or_stage1_slots'])==(res['primary_slots'],res['helper_or_stage1_slots']) for r in rr)
   cells.append({'policy':policy,'profile':profile,'context':32768 if profile=='32k' else 131072,'n':3,'stats':agg,'primary_slots':res['primary_slots'],'GPU1_slots':res['helper_or_stage1_slots'],'cache_MiB_primary':res['cache_MiB_primary'],'cache_MiB_total':res['cache_MiB_total'],'raw_paths':[r['raw'] for r in rr]})
 parity=[];paired=[]
 for profile in ['32k','128k']:
  for policy in POLICIES[1:]:
   ratios={k:[] for k in ['PP','TG','TTFT_s','wall_s','CPU_VM_pct']}
   for rep in [1,2,3]:
    a=next(x for x in runs if x['policy']=='100us' and x['profile']==profile and x['replicate']==rep);b=next(x for x in runs if x['policy']==policy and x['profile']==profile and x['replicate']==rep)
    assert a['input_sha256']==b['input_sha256']
    aa=load(pathlib.Path(a['path'])/'raw/output-ids-request2.json');bb=load(pathlib.Path(b['path'])/'raw/output-ids-request2.json');first=next((i for i,(u,v) in enumerate(zip(aa,bb)) if u!=v),None)
    keys=['mtp_proposed','mtp_accepted','verify_windows','local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries','all_routed_entries']
    parity.append({'policy':policy,'profile':profile,'replicate':rep,'reference':'100us','identical_input_ids':True,'identical_output_ids':aa==bb,'first_diverging_token':first,'positionwise_agreement_pct':100*sum(a==b for a,b in zip(aa,bb))/4096,'counter_equal':{k:a['performance'][k]==b['performance'][k] for k in keys},'counter_delta':{k:(b['performance'][k]-a['performance'][k]) if a['performance'][k] is not None and b['performance'][k] is not None else None for k in keys},'capacity_identical':(a['resource']['primary_slots'],a['resource']['helper_or_stage1_slots'])==(b['resource']['primary_slots'],b['resource']['helper_or_stage1_slots']),'trajectory_note':'MTP aggregate counters/windows checked; no full per-window draft trajectory exposed.'})
    for k in ratios:
     u=a['system']['decode']['CPU_VM_pct']['mean'] if k=='CPU_VM_pct' else a['performance'][k];v=b['system']['decode']['CPU_VM_pct']['mean'] if k=='CPU_VM_pct' else b['performance'][k];ratios[k].append(v/u)
   paired.append({'profile':profile,'policy':policy,'reference':'100us','ratios':{k:{'values':v,'median':statistics.median(v),'delta_pct':100*(statistics.median(v)-1)} for k,v in ratios.items()}})
 summary={'state':'COMPLETE_24_VALID','recommendation':load(C/'decision.json')['recommendation'] if (C/'decision.json').exists() else None,'decision':load(C/'decision.json') if (C/'decision.json').exists() else None,'cells':cells,'runs':runs,'warmups':warm,'parity':parity,'paired':paired,'provenance':load(C/'git/provenance.json'),'model':load(C/'git/model.json'),'protocol':load(C/'protocol.json'),'limitations':['One preserved offline repository workload; no universal domain claim.','Fresh server before each request differs from prior three sequential measured requests/server; previous throughput is historical only.','CPU completion timing includes overlap and waiting, not exclusive expert computation or wake-up latency.','Exact all-local/CPU-positive conditional waits unavailable; no costly instrumentation added.','VM CPU% covers16vCPUs; processCPU uses100%=one core.','NoPSS polling; first telemetry CPU sample excluded because cpu_percent starts with zero.']}
 save(C/'summary.json',summary);save(C/'analysis/run-details.json',runs);save(C/'analysis/parity.json',parity);save(C/'analysis/paired.json',paired)
 rows=[]
 for x in cells:
  row={k:x[k] for k in ['policy','profile','context','n','primary_slots','GPU1_slots','cache_MiB_primary','cache_MiB_total']}
  for k,v in x['stats'].items():
   for st in ['min','median','max']:row[f'{k}_{st}']=v[st] if v else None
  rows.append(row)
 with (C/'summary.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print('ANALYZED24',json.dumps([{'policy':x['policy'],'profile':x['profile'],'TG':x['stats']['TG'],'wall':x['stats']['wall_s'],'CPU':x['stats']['CPU_VM_pct']} for x in cells],indent=2))

if __name__=='__main__':analyze()
