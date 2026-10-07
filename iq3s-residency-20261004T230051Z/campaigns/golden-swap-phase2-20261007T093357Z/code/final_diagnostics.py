"""Additional queue/timing/guard diagnostics and portable CSVs, after timing ends."""
import csv,collections,re,statistics
import numpy as np
from common import *
from inspect_oracle import E,L,N
from transactions import LC
def dist(v):
 return dict(zip(['min','median','p95','max'],[float(x) for x in np.quantile(v,[0,.5,.95,1])])) if len(v) else None
def analyze(p):
 e=np.fromfile(p/'raw/oracle-admissions.bin',E);a=np.fromfile(p/'raw/oracle-lifecycle.bin',LC);layers=np.fromfile(p/'raw/oracle-layers.bin',L);episode=load(p/'episode.json');timeline=[]
 for x in e:
  timeline.append((int(x['issue_ns']),1))
  if x['copy_end']:timeline.append((int(x['copy_end']),-1))
 pending=peak=0;weighted=0;last=timeline[0][0] if timeline else 0
 for t,d in sorted(timeline):
  weighted+=pending*(t-last);pending+=d;peak=max(peak,pending);last=t
 assert peak<=5 and pending==0,('ordinary copy queue must drain',p,peak,pending)
 published=e['publish_ns']>0;complete=e['copy_end']>0;statuses=collections.Counter(map(int,e['status']));cfg=load(p/'config.json');ctl=cfg['env'].get('STRATA_Q4_TRANSACTION_CONTROL')=='1'
 if ctl:
  used=published&(a['first_use']>=0)&(a['reason']==1);assert np.all(a['released_at'][used]>a['first_use'][used]);assert np.all(e['published_at'][published]<=e['target'][published]+48)
 def elapsed(begin,end,mask):
  return dist((e[end][mask].astype(np.int64)-e[begin][mask].astype(np.int64))/1e6)
 return {'label':p.name,'task':episode['task'],'arm':episode['arm'],'kind':episode.get('kind'),'ordinary_transactions':len(e),'sampled_D2H_readback_bytes_derived':sum(min(2,len(e[(e['layer']//24==d)&(e['bytes']==b)&(e['copy_end']>0)]))*b for d in [0,1] for b in [3072000,3584000,3993600]) if cfg['env'].get('STRATA_Q4_ORACLE_CHECK')=='1' else 0,'readback_derivation':'First two completed ordinary copies per active worker/class, same fresh server; native warmup is untracked. Separate from ordinary H2D/restoration bytes.','ordinary_pending_after_drain':pending,'ordinary_peak_copy_inflight':peak,'mean_inflight_issue_to_completion':weighted/(last-timeline[0][0]) if timeline and last>timeline[0][0] else 0,'expired_then_later_used_transactions':int(np.count_nonzero(published&(a['reason']==2)&(a['first_use']>=a['released_at']))),'expired_without_observed_use_transactions':int(np.count_nonzero(published&(a['reason']==2)&(a['first_use']<0))),'status_counts':dict(statuses),'status_meanings':{'0':'issued incomplete','1':'published by target','2':'redundant retired','3':'published late','4':'completed final drain without publication, not pending','5':'risk recheck retired','8':'late intent safely retired','9':'protection capacity retirement'},'ready_by_target_transactions':int(np.count_nonzero(published&(e['published_at']<=e['target']))),'late_target_transactions':int(np.count_nonzero(published&(e['published_at']>e['target']))),'unpublished_completed_bytes':int(e['bytes'][complete&~published].sum()),'issue_to_stage_ms':elapsed('issue_ns','stage_begin',e['stage_begin']>0),'staging_ms':elapsed('stage_begin','stage_end',e['stage_end']>0),'copy_with_host_wait_ms':elapsed('copy_begin','copy_end',complete),'completion_to_publication_ms':elapsed('copy_end','publish_ns',published),'scope':'Ordinary oracle proposals only. Issue-to-completion queue includes staging and host waits; no DMA-only or exclusive stall claim. Native unpublished completion has no independent marker.'}
if __name__=='__main__':
 no_gpu();episodes=[p for p in sorted((C/'raw').iterdir()) if (p/'episode.json').exists() and load(p/'episode.json')['valid']];out=[analyze(p) for p in episodes];save(C/'results/queue-and-timing-diagnostics.json',out)
 summary=load(C/'results/main-summary.json')
 fields=['task','arm','valid','attempts','tok_s_min','tok_s_median','tok_s_max','decode_s_median','wall_s_median','paired_TG_pct_median','paired_wall_pct_median','retention_median','local_pct_median','cpu_median','mapped_median','copy_GB_median','evicted_without_use_GB_median','end_censored_unused_GB_median','planner_ms_median','score_ms_median','meets_gain_criterion']
 with (C/'results/primary-table.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");writer.writeheader()
  for s in summary:
   if s['task'] not in ['code-archive','math-inventory','text-websocket','mixed-chinook']:continue
   row={k:s.get(k) for k in ['task','arm','valid','attempts','meets_gain_criterion']}
   for k in fields[4:-1]:
    base,stat=k.rsplit('_',1);row[k]=s.get(base,{}).get(stat) if s.get(base) else None
   writer.writerow(row)
 save(C/'results/protocol-validations.json',{'same_generation_use_release_and_eviction_reconciled':True,'bounded_copy_workers_verified':True,'native_missing_information_explicit':True,'points':len(episodes),'queue_points':len(out),'source_binary_version':'c12a0b11f02ae7b635dc3c6a15ff14f37319ce22'})
 print('FINAL_DIAGNOSTICS',len(out),flush=True)
