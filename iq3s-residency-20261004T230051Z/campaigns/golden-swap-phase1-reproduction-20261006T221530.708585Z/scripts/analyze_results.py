"""Regenerate task/block summaries from all preserved attempts; no run filtering."""
import csv,re,statistics,bisect,collections,hashlib,time
import numpy as np
from common import *
from inspect_oracle import L,E,N
from tape import Tape
import victim_accounting

def ranges(values):
 values=[float(x) for x in values if x is not None];return {'min':min(values),'median':statistics.median(values),'max':max(values)} if values else None
def parse_fields(line):return {k:(float(v) if '.' in v else int(v)) for k,v in re.findall(r'(\w+)=([0-9.]+)',line)}
def returns(label,tape):
 p=C/'raw'/label;ev=np.fromfile(p/'raw/oracle-admissions.bin',E);native=np.fromfile(p/'raw/oracle-native.bin',N);t=Tape(tape);uses=collections.defaultdict(list)
 for wi,w in enumerate(t.ws):
  for l in range(48):
   for e in np.unique(w['routes']['ids'][l,:10*int(w['T'])]):uses[l,int(e)].append(wi)
 victims=[(int(x['published_at'])//48,int(x['layer']),int(x['victim'])) for x in ev if x['publish_ns']];victims += [(int(x['window']),int(x['layer']),int(x['victim'])) for x in native];rows=[]
 for wi,l,e in victims:
  u=uses[l,e];j=bisect.bisect_right(u,wi);gap=u[j]-wi if j<len(u) else None;remaining=len(t.ws)-1-wi;rows.append({'window':wi,'layer':l,'victim':e,'return_gap_windows':gap,'right_censored':gap is None,'observation_windows':remaining,'horizon_labels':[(int(gap<=h) if gap is not None and gap<=h else 0 if remaining>=h else None) for h in [1,4,16,64]]})
 out={'evictions':len(rows),'observed_returns':sum(not r['right_censored'] for r in rows),'right_censored':sum(r['right_censored'] for r in rows),'return_gap_windows':ranges([r['return_gap_windows'] for r in rows]),'convention':'Native removal after named window; oracle publication at boundary with common current-window victim protection. Strictly later batch search. Finite tail censored.','records':rows};save(C/'analysis'/(label+'-return-labels.json'),out);return {k:v for k,v in out.items() if k!='records'}

def main():
 no_gpu();progress(5,'Regenerate all raw live results and paired summaries');attempts=[];order=load(C/'run-order.json')['main'];tasks={t['task_id']:t for t in load(P0/'benchmark-manifest.json')['tasks']}
 with Heartbeat('live result analysis',5):
  for run in order:
   p=C/'raw'/run['label'];
   if not (p/'episode.json').exists():continue
   ep=load(p/'episode.json');row={**run,**{k:ep.get(k) for k in ['valid','error','startup_s','warmup_s','cleanup_s','total_operating_s']}}
   if ep.get('valid'):
    r=ep['run'];log=(p/'raw/run-engine.log').read_text();scorer=next((parse_fields(x) for x in log.splitlines() if x.startswith('Q4_VICTIM_END')),{});planner=next((parse_fields(x) for x in log.splitlines() if x.startswith('Q4_ORACLE_END')),{});information=next((parse_fields(x) for x in log.splitlines() if x.startswith('Q4_INFORMATION_END')),{});ownership=load(C/'analysis'/(run['label']+'-oracle.json'));va=victim_accounting.analyze(run['label']);ret=returns(run['label'],tasks[run['task']]['trace_path']);telemetry=[__import__('json').loads(line) for line in (p/'telemetry/run.jsonl').read_text().splitlines()];o=np.fromfile(p/'raw/observations.bin',Tape(tasks[run['task']]['trace_path']).obs_dtype);telemetry=[x for x in telemetry if int(o[0]['begin_ns'])/1e9<=x['monotonic']<=int(o[-1]['end_ns'])/1e9]
    cpu_steal=[x['cpu_times_percent'].get('steal',0) for x in telemetry];gpu={str(d):{k:ranges([g[k] for x in telemetry for g in x.get('gpus',[]) if int(g['index'])==d]) for k in ['util_pct','power_w','sm_mhz','vram_mib']} for d in [0,1]}
    copy=ownership['copies'];row.update(emitted_tokens=r['actual_output_tokens'],windows=ep['fidelity']['windows'],main_entries=ep['fidelity']['main_entries'],mtp_entries=ep['fidelity']['mtp_entries'],work_sha256=ep['fidelity']['work_sha256'],initial_state_sha256=ep['fidelity']['initial_state_sha256'],decode_s=r['decode_s'],tok_s=r['actual_output_tokens']/r['decode_s'],wall_s=r['wall_s'],prefill_s=r['pp_s'],TTFT_s=r['TTFT_s'],local_pct=100*ownership['demand']['local']/ep['fidelity']['main_entries'],cpu_entries=ownership['demand']['cpu'],mapped_entries=ownership['demand']['mapped'],copy_GB=(copy['completed_bytes']+copy['native_published_bytes']+copy['restoration_bytes'])/1e9,copy=copy,scorer=scorer,planner=planner,information=information,victim_absence=va,return_labels=ret,cpu_steal_pct=ranges(cpu_steal),gpu=gpu,host_peak_rss_GiB=r['telemetry']['peak_rss_gib'],mtp_path_counts=None,activation_diagnostic=ep['fidelity']['selected_activation'],native_head_agreement=ep['fidelity']['native_head_agreement'])
    if run['arm']=='ORACLE_IN_LEARNED_VICTIM':assert information['victim_next']==0 and information['victim_count']==0,'Victim future leakage';assert scorer['invalid']==0,'Invalid scorer runtime predictions'
   attempts.append(row);save(C/'results/live-attempts.json',attempts)
 paired=[]
 for task in tasks:
  for block in range(1,4):
   rr=[r for r in attempts if r['task']==task and r['block']==block and r['valid']];arms={r['arm']:r for r in rr}
   if len(arms)!=3:continue
   c,f,l=[arms[a] for a in ['REPLAY_CURRENT','ORACLE_FULL','ORACLE_IN_LEARNED_VICTIM']];assert len({r['work_sha256'] for r in rr})==1 and len({r['initial_state_sha256'] for r in rr})==1
   denominator=c['decode_s']-f['decode_s'];gain=c['decode_s']-l['decode_s'];paired.append({'task':task,'block':block,'current_decode_s':c['decode_s'],'full_decode_s':f['decode_s'],'learned_decode_s':l['decode_s'],'full_time_saving_s':denominator,'learned_time_saving_s':gain,'learned_decode_change_pct':100*(l['decode_s']/c['decode_s']-1),'full_decode_change_pct':100*(f['decode_s']/c['decode_s']-1),'learned_TG_change_pct':100*(c['decode_s']/l['decode_s']-1),'full_TG_change_pct':100*(c['decode_s']/f['decode_s']-1),'learned_wall_change_pct':100*(l['wall_s']/c['wall_s']-1),'full_wall_change_pct':100*(f['wall_s']/c['wall_s']-1),'retention':gain/denominator if denominator>0 else None,'retention_unstable':denominator<=.01*c['decode_s'],'full_reference_benefit':denominator>0})
 save(C/'results/paired-blocks.json',paired);summary=[]
 for task in ['code-archive','math-inventory','text-websocket','mixed-chinook']:
  pp=[p for p in paired if p['task']==task]
  for arm in ['REPLAY_CURRENT','ORACLE_FULL','ORACLE_IN_LEARNED_VICTIM']:
   rr=[r for r in attempts if r['task']==task and r['arm']==arm];valid=[r for r in rr if r['valid']];s={'task':task,'profile':tasks[task]['profile'],'actual_input_tokens':tasks[task]['actual_input_tokens'],'mode':arm,'valid':len(valid),'attempts':len(rr),'decode_s':ranges([r['decode_s'] for r in valid]),'tok_s':ranges([r['tok_s'] for r in valid]),'wall_s':ranges([r['wall_s'] for r in valid]),'local_pct':ranges([r['local_pct'] for r in valid]),'cpu_entries':ranges([r['cpu_entries'] for r in valid]),'mapped_entries':ranges([r['mapped_entries'] for r in valid]),'copy_GB':ranges([r['copy_GB'] for r in valid]),'reloads':ranges([r['victim_absence']['chronological_victim_reloads'] for r in valid]),'victim_absent_entries':ranges([r['victim_absence']['victim_absent_entries'] for r in valid]),'scorer_feature_ms':ranges([r['scorer'].get('feature_ms',0) for r in valid]),'scorer_model_ms':ranges([r['scorer'].get('score_ms',0) for r in valid]),'scorer_selection_ms':ranges([r['scorer'].get('selection_ms',0) for r in valid]),'planner_ms':ranges([r['planner'].get('planner_ms',0) for r in valid]),'host_model_bytes':ranges([r['scorer'].get('host_bytes',0) for r in valid])}
   if arm!='REPLAY_CURRENT':
    prefix='full' if arm=='ORACLE_FULL' else 'learned';s.update(paired_decode_change_pct=ranges([p[prefix+'_decode_change_pct'] for p in pp]),paired_TG_change_pct=ranges([p[prefix+'_TG_change_pct'] for p in pp]),paired_wall_change_pct=ranges([p[prefix+'_wall_change_pct'] for p in pp]),decode_faster_pairs=sum(p[prefix+'_decode_change_pct']<0 for p in pp),wall_faster_pairs=sum(p[prefix+'_wall_change_pct']<0 for p in pp),paired_blocks=len(pp));s['retention']=ranges([p['retention'] for p in pp]) if prefix=='learned' else None
   summary.append(s)
 save(C/'results/main-summary.json',summary)
 with (C/'results/live-attempts.csv').open('w') as f:
  fields=['task','block','arm','label','valid','error','emitted_tokens','windows','decode_s','tok_s','prefill_s','wall_s','startup_s','warmup_s','cleanup_s','total_operating_s','local_pct','cpu_entries','mapped_entries','copy_GB'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(attempts)
 with (C/'results/paired-blocks.csv').open('w') as f:
  if paired:w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
 print('ANALYZED',len(attempts),'attempts',len(paired),'complete paired blocks',flush=True)
if __name__=='__main__':main()
