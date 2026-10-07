"""Regenerate descriptive diagnostics and reproduction references after all live work ends."""
import hashlib,statistics
from common import *
no_gpu()
attempts=load(C/'results/live-attempts.json');summaries=load(C/'results/main-summary.json')
def span(values):
 values=[v for v in values if v is not None]
 return None if not values else {'min':min(values),'median':statistics.median(values),'max':max(values)}
rows=[]
for s in summaries:
 rr=[r for r in attempts if r['task']==s['task'] and r['arm']==s['mode']]
 row={'task':s['task'],'arm':s['mode']}
 for key in ['startup_s','warmup_s','cleanup_s','total_operating_s','prefill_s','TTFT_s','host_peak_rss_GiB','native_head_agreement']:
  row[key]=span([r[key] for r in rr])
 for key in ['setup_ms','publication_ms','drain_ms','restoration_ms']:
  row[key]=span([r['planner'][key] for r in rr])
 row['activation_relative_L2']=span([r['activation_diagnostic']['relative_L2'] for r in rr])
 row['activation_max_abs_error']=span([r['activation_diagnostic']['max_abs_error'] for r in rr])
 row['cpu_steal_sample_medians_pct']=span([r['cpu_steal_pct']['median'] for r in rr])
 row['copy_unused_pct']=span([100*r['copy']['unused_bytes']/r['copy']['completed_bytes'] for r in rr if r['copy']['completed_bytes']])
 row['observed_victim_returns']=span([r['return_labels']['observed_returns'] for r in rr])
 row['right_censored_evictions']=span([r['return_labels']['right_censored'] for r in rr])
 row['repeat_admissions_beyond_first']=span([r['victim_absence']['repeat_admissions_beyond_first'] for r in rr])
 for key in ['ready_publications','late_publications','pending_at_end','unpublished_bytes','native_pending_bytes']:
  row[key]=span([r['copy'][key] for r in rr])
 rows.append(row)
save(C/'results/final-diagnostics.json',rows)
groups=[]
for task in ['code-archive','math-inventory','text-websocket','mixed-chinook']:
 current=next(s for s in summaries if s['task']==task and s['mode']=='REPLAY_CURRENT')
 learned=next(s for s in summaries if s['task']==task and s['mode']=='ORACLE_IN_LEARNED_VICTIM')
 nonlocal_current=current['cpu_entries']['median']+current['mapped_entries']['median']
 nonlocal_learned=statistics.median(r['cpu_entries']+r['mapped_entries'] for r in attempts if r['task']==task and r['arm']==learned['mode'])
 groups.append({'task':task,'median_nonlocal_reduction_pct':100*(1-nonlocal_learned/nonlocal_current),'median_copy_increase_pct':100*(learned['copy_GB']['median']/current['copy_GB']['median']-1),'paired_TG_change_pct':learned['paired_TG_change_pct'],'paired_wall_change_pct':learned['paired_wall_change_pct'],'planner_ms':learned['planner_ms']})
save(C/'results/mechanism-diagnostics.json',groups)
# Confirm whether the two calibration thresholds actually changed the action accounting.
competition=load(C/'results/offline-competition.json');comparisons=[]
keys=['cpu','mapped','copied_bytes','victim_absent_observations','rejections']
for a in competition:
 if a['threshold']!=.2:continue
 b=next(r for r in competition if r['task']==a['task'] and r['policy']==a['policy'] and r['threshold']==.5)
 comparisons.append({'task':a['task'],'policy':a['policy'],'action_accounting_equal':all(a.get(k)==b.get(k) for k in keys),'checked_fields':keys})
save(C/'results/operating-point-diagnostics.json',{'comparisons':comparisons,'equal_points':sum(r['action_accounting_equal'] for r in comparisons),'total_points':len(comparisons),'interpretation':'Where actions are identical, small proxy differences come from CPU evaluator selection timing, not a demonstrated threshold advantage. The frozen threshold was not revised.'})
repro=load(C/'tests/reproduction-checks.json');references=[]
with Heartbeat('preserve isolated reproducer artifact references',5):
 for check in repro['checks']:
  if 'directory' not in check:continue
  d=pathlib.Path(check['directory']);files={}
  for p in d.rglob('*'):
   if not p.is_file() or p.is_symlink():continue
   relative=str(p.relative_to(d))
   files[relative]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
  references.append({'directory':str(d),'arm':check['arm'],'episode':check['episode'],'files':files})
save(C/'references/reproduction-artifacts.json',references)
ledger('Final descriptive diagnostics regenerated after live measurements; no model or scheduler changes',main_requests=len(attempts),reproduction_checks=repro['state'],threshold_accounting_equal=sum(r['action_accounting_equal'] for r in comparisons),threshold_points=len(comparisons))
progress(5,'Final descriptive diagnostics and isolated reproduction references ready',next_action='regenerate report and complete preservation audit',completed_requests=36,remaining_requests=0,owned_pid=None)
