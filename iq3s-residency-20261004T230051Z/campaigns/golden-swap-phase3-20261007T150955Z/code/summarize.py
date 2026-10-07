"""Regenerate paired Phase 3 results from immutable complete requests after GPU work ends."""
import re,csv,statistics,hashlib,collections
import numpy as np
from common import *
from inspect_oracle import E,L
from tape import OBS2
from transactions import reconcile,reconcile_native
from victim_accounting import analyze as victims

def dist(v):return dict(zip(['min','median','max'],map(float,np.quantile(v,[0,.5,1])))) if v else None

def kv(log,name):
 m=re.search(name+r' ([^\n]+)',log)
 if not m:return None
 return {k:float(v) if re.fullmatch(r'\d+(?:\.\d+)?',v) and k!='decision_hash' else v for k,v in re.findall(r'(\w+)=([^\s]+)',m[1])}

def analyze(p):
 ep=load(p/'episode.json');log=(p/'raw/run-engine.log').read_text();r=ep['run'];a=ep['ownership'];oracle=kv(log,'Q4_ORACLE_END');tc=kv(log,'Q4_TC_END');planner=kv(log,'Q4_PLANNER_END');score=kv(log,'Q4_VICTIM_END');wait=[]
 for m in re.finditer('Q4_WAIT_END ([^\n]+)',log):wait.append({k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',m[1])})
 tail=load(C/'inputs/independent-task-manifest.json') if ep['task']=='text-json-rfc8259' else None
 obs=np.fromfile(p/'raw/observations.bin',OBS2) if tail else None
 boundary=tail['main_windows']*48 if tail else None;prefix_time=int(obs[tail['main_windows']-1]['end_ns']) if tail else None
 if ep['arm'] in ['PLANNER_BASELINE','PLANNER_OPT']:
  transaction=reconcile(p,boundary);vt=victims(p.name)
 else:transaction=reconcile_native(p,boundary,prefix_time);vt=victims(p.name)
 e=np.fromfile(p/'raw/oracle-admissions.bin',E);layers=np.fromfile(p/'raw/oracle-layers.bin',L)
 logical=e[['trigger','target','published_at','layer','incoming','victim','slot','oldslot','status','bytes','uses','victim_uses']].copy()
 # Structured multi-field selection preserves padding from original; explicit serialization below.
 h=hashlib.sha256();
 for x in e:
  for key in ['trigger','target','published_at','layer','incoming','victim','slot','oldslot','status','bytes','uses','victim_uses']:h.update(int(x[key]).to_bytes(8,'little',signed=True))
 row={'label':p.name,'task':ep['task'],'arm':ep['arm'],'block':ep.get('block'),'kind':ep.get('kind'),'valid':ep['valid'],'input':r['actual_input_tokens'],'output':r['actual_output_tokens'],'windows':r['verify_windows'],'decode_s':r['decode_s'],'tok_s':r['actual_output_tokens']/r['decode_s'],'wall_s':r['wall_s'],'prefill_s':r['pp_s'],'startup_s':ep['startup_s'],'warmup_s':ep['warmup_s'],'cleanup_s':ep['cleanup_s'],'operating_s':ep['total_operating_s'],'local':a['demand']['local'],'cpu':a['demand']['cpu'],'mapped':a['demand']['mapped'],'main_entries':ep['fidelity']['main_entries'],'mtp_entries':ep['fidelity']['mtp_entries'],'work_sha256':ep['fidelity']['work_sha256'],'initial_state_sha256':ep['fidelity']['initial_state_sha256'],'oracle':oracle,'tc':tc,'planner':planner,'score':score,'wait':wait,'transactions':transaction,'victims':vt,'logical_live_admissions_sha256':h.hexdigest(),'host_plan_ms':float(np.sum(layers['plan_end']-layers['begin'])/1e6),'gpu_plan_wait_ms':sum(x['plan_ns'] for x in wait)/1e6,'gpu_cpu_wait_ms':sum(x['cpu_ns'] for x in wait)/1e6,'gpu_mapped_wait_ms':sum(x['mapped_ns'] for x in wait)/1e6}
 row['information']=kv(log,'Q4_INFORMATION_END');
 row['isolated_plan_wait_exposure_bounds_ms']={'lower':0,'upper':min(row['decode_s']*1000,row['gpu_plan_wait_ms']),'definition':'Contribution of observed plan A stalls holding all other work/dependencies fixed. Shared/peer overlap and absent absolute cross-device alignment prevent a tighter bound. Not an exclusive oracle CPU attribution or counterfactual speedup prediction.'}
 if ep['arm'] in ['PLANNER_BASELINE','PLANNER_OPT']:assert row['information']['victim_next']==0 and row['information']['victim_count']==0
 row['restoration_bytes']=a['copies']['restoration_bytes'];row['copy_GB']=(transaction['completed_bytes']+row['restoration_bytes'])/1e9;row['local_pct']=100*row['local']/row['main_entries']
 assert len(wait)==2 and all(x['plan_count']==24*row['windows'] for x in wait),('wait coverage',p.name,wait)
 assert row['main_entries']==sum(a['demand'].values())
 if tail:
  row['prefix_observation_span_s']=(prefix_time-int(obs[0]['begin_ns']))/1e9;row['prefix_tokens']=tail['main_output_tokens'];row['observed_tail_tokens']=tail['observed_tail_tokens'];row['prefix_tok_s']=row['prefix_tokens']/row['prefix_observation_span_s'];row['prefix_definition']='Verifier observation span through frozen main boundary; not native whole-decode timing. Mandatory tail, final commit/drain/restoration and flush charged in full wall.'
 row['resources']=resources(p)
 return row

def resources(p):
 rows=[]
 for path in (p/'telemetry').glob('*.jsonl'):
  rows.extend(json.loads(line) for line in path.read_text().splitlines() if line.strip())
 def range_of(vals):return dict(zip(['min','median','max'],map(float,np.quantile(vals,[0,.5,1])))) if vals else None
 return {'scope':'Lightweight sampled telemetry; startup, warmup and replay separate log names, aggregate ranges retained without steal correction.','samples':len(rows),'cpu_pct':range_of([x['system_cpu_pct'] for x in rows if 'system_cpu_pct' in x]),'steal_pct':range_of([x['cpu_times_percent']['steal'] for x in rows if 'steal' in x.get('cpu_times_percent',{})]),'process_CPU_pct':range_of([p['cpu_pct'] for x in rows for p in x.get('processes',[]) if 'cpu_pct' in p]),'process_RSS_GiB':range_of([p['rss_gib'] for x in rows for p in x.get('processes',[]) if 'rss_gib' in p]),'available_ram_GiB':range_of([x['mem_available_gib'] for x in rows if 'mem_available_gib' in x]),'swap_used_bytes':range_of([x['swap_memory']['used'] for x in rows if 'swap_memory' in x]),'gpus':{str(d):{k:range_of([g[k] for x in rows for g in x.get('gpus',[]) if int(g['index'])==d and k in g]) for k in ['util_pct','power_w','vram_mib','sm_mhz','temperature_c','memory_mhz','pcie_generation','pcie_width']} for d in [0,1]}}

if __name__=='__main__':
 no_gpu();rows=[]
 with Heartbeat('result regeneration',5):
  for p in sorted((C/'raw').iterdir()):
   if not p.is_dir() or not (p/'episode.json').exists():continue
   ep=load(p/'episode.json')
   if ep.get('kind') not in ['main','independent'] or not ep['valid']:continue
   rows.append(analyze(p));print('SUMMARY',p.name,flush=True)
 save(C/'results/live-attempts.json',rows);paired=[]
 for task in sorted(set(x['task'] for x in rows)):
  for block in sorted(set(x['block'] for x in rows if x['task']==task)):
   arms={x['arm']:x for x in rows if x['task']==task and x['block']==block}
   if set(arms)!=set(['PLANNER_BASELINE','PLANNER_OPT','REPLAY_CURRENT']):continue
   assert len(set(x['work_sha256'] for x in arms.values()))==1 and len(set(x['initial_state_sha256'] for x in arms.values()))==1
   baseline,opt,current=[arms[k] for k in ['PLANNER_BASELINE','PLANNER_OPT','REPLAY_CURRENT']]
   result={'task':task,'block':block,'kind':baseline['kind'],'decode_OPT_BASE_pct':100*(opt['decode_s']/baseline['decode_s']-1),'TG_OPT_BASE_pct':100*(opt['tok_s']/baseline['tok_s']-1),'wall_OPT_BASE_pct':100*(opt['wall_s']/baseline['wall_s']-1),'BASE_CURRENT_decode_pct':100*(baseline['decode_s']/current['decode_s']-1),'OPT_CURRENT_decode_pct':100*(opt['decode_s']/current['decode_s']-1),'BASE_CURRENT_wall_pct':100*(baseline['wall_s']/current['wall_s']-1),'OPT_CURRENT_wall_pct':100*(opt['wall_s']/current['wall_s']-1),'planner_cpu_removed_ms':baseline['planner']['host_cpu_ms']-opt['planner']['host_cpu_ms'],'planner_wall_removed_ms':baseline['oracle']['planner_ms']-opt['oracle']['planner_ms'],'gpu_plan_wait_removed_ms':baseline['gpu_plan_wait_ms']-opt['gpu_plan_wait_ms'],'gpu_wait_attribution':'Actual verifier stream wait for host plan A; includes host scheduling/native plan. Difference is paired observational evidence, not exclusive oracle time.','live_logical_actions_identical':baseline['logical_live_admissions_sha256']==opt['logical_live_admissions_sha256'],'same_required_work':True,'cache_recompute_reduction_pct':100*opt['planner']['hits']/max(1,opt['planner']['lookups'])}
   paired.append(result)
 save(C/'results/paired-blocks.json',paired);summary=[]
 def criterion(v,decode_key,wall_key):
  return len(v)>=3 and statistics.median(x[decode_key] for x in v)<-3 and sum(x[decode_key]<0 for x in v)>=2 and statistics.median(x[wall_key] for x in v)<=1 and sum(x[wall_key]>3 for x in v)<2
 for task in sorted(set(x['task'] for x in rows)):
  pair=[x for x in paired if x['task']==task];s={'task':task,'blocks':len(pair),'kind':pair[0]['kind'] if pair else None,'paired':{k:dist([x[k] for x in pair]) for k in ['decode_OPT_BASE_pct','TG_OPT_BASE_pct','wall_OPT_BASE_pct','BASE_CURRENT_decode_pct','OPT_CURRENT_decode_pct','BASE_CURRENT_wall_pct','OPT_CURRENT_wall_pct','planner_cpu_removed_ms','planner_wall_removed_ms','gpu_plan_wait_removed_ms','cache_recompute_reduction_pct']},'block_signs':{k:[x[k]<0 for x in pair] for k in ['decode_OPT_BASE_pct','wall_OPT_BASE_pct','BASE_CURRENT_decode_pct','OPT_CURRENT_decode_pct']},'optimization_gain_criterion':criterion(pair,'decode_OPT_BASE_pct','wall_OPT_BASE_pct'),'baseline_vs_current_criterion':criterion(pair,'BASE_CURRENT_decode_pct','BASE_CURRENT_wall_pct'),'optimized_vs_current_criterion':criterion(pair,'OPT_CURRENT_decode_pct','OPT_CURRENT_wall_pct'),'arms':{}}
  for arm in ['PLANNER_BASELINE','PLANNER_OPT','REPLAY_CURRENT']:
   a=[x for x in rows if x['task']==task and x['arm']==arm];s['arms'][arm]={'valid':len(a),'attempts':len(a),'metrics':{k:dist([x[k] for x in a]) for k in ['decode_s','wall_s','tok_s','prefill_s','startup_s','warmup_s','cleanup_s','local_pct','cpu','mapped','copy_GB','host_plan_ms','gpu_plan_wait_ms','gpu_cpu_wait_ms','gpu_mapped_wait_ms']},'oracle':{k:dist([x['oracle'][k] for x in a]) for k in ['planner_ms','publication_ms','drain_ms','restoration_ms','setup_ms','published','ready_publications','late_publications']},'planner':{k:dist([x['planner'][k] for x in a]) for k in ['host_cpu_ms','lookups','hits','misses','invalid_lower','invalid_upper','invalid_rewind','opportunities']},'score':{k:dist([x['score'][k] for x in a]) for k in ['feature_ms','score_ms','selection_ms']}}
  summary.append(s)
 save(C/'results/main-summary.json',summary)
 fields=['task','arm','valid','tok_s_min','tok_s_median','tok_s_max','decode_s_median','wall_s_median','local_pct_median','cpu_median','mapped_median','copy_GB_median','planner_wall_ms','planner_CPU_ms','GPU_plan_wait_ms','copy_queries_lookups','copy_queries_hits','copy_queries_misses']
 with (C/'results/primary-table.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fields,lineterminator="\n");w.writeheader()
  for s in summary:
   for arm,z in s['arms'].items():
    row={'task':s['task'],'arm':arm,'valid':z['valid']}
    for k in fields[3:12]:
     metric,stat=k.rsplit('_',1);row[k]=z['metrics'][metric][stat]
    row.update(planner_wall_ms=z['oracle']['planner_ms']['median'],planner_CPU_ms=z['planner']['host_cpu_ms']['median'],GPU_plan_wait_ms=z['metrics']['gpu_plan_wait_ms']['median'],copy_queries_lookups=z['planner']['lookups']['median'],copy_queries_hits=z['planner']['hits']['median'],copy_queries_misses=z['planner']['misses']['median']);w.writerow(row)
 print('RESULTS',len(rows),'blocks',len(paired),flush=True)
