"""Regenerate compact per-request and paired-block evidence from retained raw results."""
import json,re,statistics,collections,hashlib
import numpy as np
from common import *
from transactions import reconcile,reconcile_native
from inspect_oracle import L
from victim_accounting import analyze as victim_analyze
from tape import Tape
ARMS=['REPLAY_CURRENT','ORACLE_FULL','ORACLE_IN_HISTORY_TC','ORACLE_IN_LOGISTIC_TC']
def numbers(line):
 r={}
 for k,v in re.findall(r'(\w+)=([^\s]+)',line):
  try:r[k]=float(v) if '.' in v else int(v)
  except ValueError:r[k]=v
 return r

def row(p):
 episode=load(p/'episode.json');r={k:episode.get(k) for k in ['task','arm','label','block','kind','valid','error','startup_s','warmup_s','cleanup_s','total_operating_s']}
 if not episode['valid']:return r
 run=episode['run'];proof=episode['fidelity'];ownership=episode['ownership'];cfg=load(p/'config.json');log=(p/'raw/run-engine.log').read_text();records={}
 for prefix in ['Q4_ORACLE_END','Q4_VICTIM_END','Q4_INFORMATION_END','Q4_TC_END']:
  lines=[line for line in log.splitlines() if line.startswith(prefix)];records[prefix]=numbers(lines[-1]) if lines else None
 r.update(emitted_tokens=proof['emitted_tokens'],actual_input_tokens=run['actual_input_tokens'],windows=proof['windows'],main_entries=proof['main_entries'],mtp_entries=proof['mtp_entries'],work_sha256=proof['work_sha256'],initial_state_sha256=proof['initial_state_sha256'],decode_s=run['decode_s'],tok_s=proof['emitted_tokens']/run['decode_s'],wall_s=run['wall_s'],prefill_s=run['pp_s'],TTFT_s=run['TTFT_s'],demand=ownership['demand'],copy=ownership['copies'],planner=records['Q4_ORACLE_END'],scorer=records['Q4_VICTIM_END'],information=records['Q4_INFORMATION_END'],tc=records['Q4_TC_END'],activation=proof['selected_activation'],telemetry=run['telemetry'],stage_timings=run.get('stage_timings'))
 r['local_pct']=100*r['demand']['local']/r['main_entries'];r['copy_GB']=(r['copy']['completed_bytes']+r['copy']['native_published_bytes']+r['copy']['restoration_bytes'])/1e9
 # This measured host interval includes oracle hook, begin-layer and native per-layer planning/publication.
 layers=np.fromfile(p/'raw/oracle-layers.bin',L);r['host_plan_interval_ms']=float((layers['plan_end']-layers['begin']).sum()/1e6);r['host_cpu_interval_ms']=float((layers['cpu_end']-layers['plan_end']).sum()/1e6)
 tail_task=load(C/'inputs/independent-task-manifest.json') if r['task']=='text-json-rfc8259' else None
 prefix_time=None
 if tail_task:
  tt=Tape(tail_task['trace_path']);oo=np.fromfile(p/'raw/observations.bin',tt.obs_dtype);prefix_time=int(oo[tail_task['main_windows']-1]['end_ns'])
 r['transactions']=reconcile_native(p,tail_task['main_windows']*48 if tail_task else None,prefix_time) if r['arm']=='REPLAY_CURRENT' else reconcile(p,tail_task['main_windows']*48 if tail_task else None)
 if not int(cfg['env'].get('STRATA_Q4_TRANSACTION_CONTROL','0')):r['transactions']['end_protected']=0
 if r['information'] and r['scorer']['policy']>0:assert r['information']['victim_next']==r['information']['victim_count']==0 and r['scorer']['invalid']==0
 # Existing raw ownership audit validated native route/path state. Victim absence uses chronological journal.
 va=victim_analyze(p.name);r['victim_absence']=va
 ts=[];gp={0:[],1:[]};rss=[];swap=[]
 for line in (p/'telemetry/run.jsonl').read_text().splitlines():
  x=json.loads(line);ts.append(x.get('cpu_times_percent',{}).get('steal'));rss.append(sum(z['rss_gib'] for z in x.get('processes',[])))
  for g in x.get('gpus',[]):gp[int(g['index'])].append(g)
 r['resources']={'cpu_steal_pct':trip([x for x in ts if x is not None]),'host_peak_rss_GiB':max(rss,default=None),'GPU':{str(i):{k:trip([x[k] for x in gp[i]]) for k in ['vram_mib','power_w','sm_mhz','util_pct','pcie_generation','pcie_width']} for i in [0,1]},'swap':'Sampler records available RAM; per-request swap activity unavailable'}
 if tail_task:
  t=Tape(tail_task['trace_path']);obs=np.fromfile(p/'raw/observations.bin',t.obs_dtype);n=tail_task['main_windows'];r['prefix_observation_span_s']=(int(obs[n-1]['end_ns'])-int(obs[0]['begin_ns']))/1e9 if n else None;r['prefix_tokens']=tail_task['main_output_tokens'];r['observed_tail_tokens']=tail_task['observed_tail_tokens'];r['prefix_tok_s']=r['prefix_tokens']/r['prefix_observation_span_s'] if n else None
 return r

def trip(v):
 return {'min':min(v),'median':statistics.median(v),'max':max(v)} if v else None

def pair(rows):
 blocks=[];direct=[]
 keys=sorted({(r['task'],r.get('block')) for r in rows if r.get('kind') in ['main','independent']})
 for task,b in keys:
  group={r['arm']:r for r in rows if r['task']==task and r.get('block')==b and r['valid']}
  if not all(a in group for a in ARMS):continue
  current=group[ARMS[0]];full=group[ARMS[1]];saving=current['decode_s']-full['decode_s']
  for arm in ARMS[2:]:
   x=group[arm];r={'task':task,'block':b,'arm':arm,'current_decode_s':current['decode_s'],'full_decode_s':full['decode_s'],'candidate_decode_s':x['decode_s'],'TG_ratio':x['tok_s']/current['tok_s'],'decode_ratio':x['decode_s']/current['decode_s'],'wall_ratio':x['wall_s']/current['wall_s'],'full_saving_s':saving,'retention':(current['decode_s']-x['decode_s'])/saving if saving>0 else None,'retention_stable':saving>.01*current['decode_s']};blocks.append(r)
  h=group[ARMS[2]];l=group[ARMS[3]];direct.append({'task':task,'block':b,'history_TG_over_logistic':h['tok_s']/l['tok_s'],'history_decode_over_logistic':h['decode_s']/l['decode_s'],'history_wall_over_logistic':h['wall_s']/l['wall_s'],'history_nonlocal':h['demand']['cpu']+h['demand']['mapped'],'logistic_nonlocal':l['demand']['cpu']+l['demand']['mapped'],'history_copy_GB':h['copy_GB'],'logistic_copy_GB':l['copy_GB']})
 return blocks,direct

def summarize(rows,blocks):
 summaries=[]
 for task,arm in sorted({(r['task'],r['arm']) for r in rows}):
  allrs=[r for r in rows if r['task']==task and r['arm']==arm];rs=[r for r in allrs if r['valid']];bs=[b for b in blocks if b['task']==task and b['arm']==arm];out={'task':task,'arm':arm,'valid':len(rs),'attempts':len(allrs)}
  if not rs:summaries.append(out);continue
  out.update(tok_s=trip([r['tok_s'] for r in rs]),decode_s=trip([r['decode_s'] for r in rs]),wall_s=trip([r['wall_s'] for r in rs]),prefill_s=trip([r['prefill_s'] for r in rs]),local_pct=trip([r['local_pct'] for r in rs]),cpu=trip([r['demand']['cpu'] for r in rs]),mapped=trip([r['demand']['mapped'] for r in rs]),copy_GB=trip([r['copy_GB'] for r in rs]),evicted_without_use_GB=trip([r['transactions']['partition']['published_evicted_without_use']['bytes']/1e9 for r in rs]),end_censored_unused_GB=trip([r['transactions']['partition']['published_no_use_resident_at_end']['bytes']/1e9 for r in rs]),planner_ms=trip([r['planner']['planner_ms'] for r in rs]),score_ms=trip([r['scorer']['score_ms'] for r in rs]),feature_ms=trip([r['scorer']['feature_ms'] for r in rs]),history_ms=trip([r['tc']['history_ms'] for r in rs]),host_plan_interval_ms=trip([r['host_plan_interval_ms'] for r in rs]),reloads=trip([r['victim_absence']['chronological_victim_reloads'] for r in rs]),victim_absent_entries=trip([r['victim_absence']['victim_absent_entries'] for r in rs]))
  if bs:
   tg=[100*(b['TG_ratio']-1) for b in bs];dec=[100*(b['decode_ratio']-1) for b in bs];wall=[100*(b['wall_ratio']-1) for b in bs];out.update(paired_TG_pct=trip(tg),paired_decode_pct=trip(dec),paired_wall_pct=trip(wall),decode_gain_blocks=sum(x<0 for x in dec),wall_gain_blocks=sum(x<0 for x in wall),retention=trip([b['retention'] for b in bs if b['retention'] is not None]),paired_blocks=len(bs),meets_gain_criterion=len(bs)==3 and statistics.median(dec)<-3 and sum(x<0 for x in dec)>=2 and statistics.median(wall)<=1 and sum(x>3 for x in wall)<2)
  summaries.append(out)
 return summaries
if __name__=='__main__':
 no_gpu();rows=[]
 for p in sorted((C/'raw').iterdir()):
  if (p/'episode.json').exists():rows.append(row(p));print('REGENERATED',p.name,flush=True)
 save(C/'results/live-attempts.json',rows);blocks,direct=pair(rows);save(C/'results/paired-blocks.json',blocks);save(C/'results/history-versus-logistic.json',direct);summary=summarize(rows,blocks);save(C/'results/main-summary.json',summary)
 dev=[]
 for b,off,on in [(1,'dev-math-rational-OFF1','dev-math-rational-ON2'),(2,'dev-math-rational-OFF2','dev-math-rational-ON3')]:
  a=next((r for r in rows if r['label']==off and r['valid']),None);z=next((r for r in rows if r['label']==on and r['valid']),None)
  if a and z:dev.append({'block':b,'OFF_decode_s':a['decode_s'],'ON_decode_s':z['decode_s'],'TG_ON_over_OFF':z['tok_s']/a['tok_s'],'wall_ON_over_OFF':z['wall_s']/a['wall_s'],'OFF_copy_GB':a['copy_GB'],'ON_copy_GB':z['copy_GB'],'OFF_unused_GB':a['transactions']['unused_completed_bytes']/1e9,'ON_unused_GB':z['transactions']['unused_completed_bytes']/1e9})
 save(C/'results/development-ablation.json',dev)
 gained=[s for s in summary if s.get('meets_gain_criterion') and s['task']!='text-json-rfc8259'];tasks={s['task'] for s in gained};conclusion='CONDITIONAL_REPLAY_GAIN_WITH_TRANSACTION_CONTROL' if len(tasks)==4 else 'DOMAIN_SCOPED_CONDITIONAL_REPLAY_GAIN' if tasks else 'LIFECYCLE_IMPROVED_NO_CONFIRMED_LATENCY_GAIN'
 h=[x for x in direct if x['task']!='text-json-rfc8259'];ratio=statistics.median(x['history_decode_over_logistic'] for x in h) if h else None;scorer='HISTORY_PREFERRED' if ratio is not None and ratio<.97 and sum(x['history_decode_over_logistic']<1 for x in h)>=8 else 'LOGISTIC_PREFERRED' if ratio is not None and ratio>1/.97 and sum(x['history_decode_over_logistic']>1 for x in h)>=8 else 'NO_CONFIRMED_SCORER_DIFFERENCE' if h else 'SCORER_COMPARISON_INCOMPLETE'
 save(C/'results/conclusion.json',{'primary':conclusion,'scorer':scorer,'gain_tasks':sorted(tasks),'valid_main':sum(r['valid'] for r in rows if r.get('kind')=='main'),'attempted_main':sum(r.get('kind')=='main' for r in rows),'direct_history_decode_ratio_median':ratio,'scorer_rule':'Descriptive campaign preference: >3% median direct paired decode advantage and same sign in at least8/12 blocks; not a significance test. Otherwise no confirmed difference. Lower-cost frontier may still motivate cheap history.','limitations':'Regression tasks previously evaluated; small N; incoming/current-window privileges; no natural-generation quality or deployment claim'})
