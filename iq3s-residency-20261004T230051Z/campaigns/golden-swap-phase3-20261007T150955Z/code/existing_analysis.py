"""Read-only Phase 2 journals. Never regenerate a prior campaign in-place."""
import collections,csv,re,statistics
import numpy as np
from common import *
from inspect_oracle import E,L
from transactions import LC
P2=INPUT_PARENT/'golden-swap-phase2-20261007T093357Z'
def dist(v):
 return dict(zip(['min','median','p95','max'],map(float,np.quantile(v,[0,.5,.95,1])))) if len(v) else None
rows=[]
with Heartbeat('existing journal analysis',1):
 for p in sorted((P2/'raw').iterdir()):
  if not (p/'episode.json').exists():continue
  ep=load(p/'episode.json')
  if not ep['valid'] or ep.get('kind') not in ['main','independent']:continue
  e=np.fromfile(p/'raw/oracle-admissions.bin',E);a=np.fromfile(p/'raw/oracle-lifecycle.bin',LC);l=np.fromfile(p/'raw/oracle-layers.bin',L)
  pub=e['publish_ns']>0;used=pub&(a['first_use']>=0);dead=pub&(a['evicted_at']>=0);alive=pub&~dead
  n=sum(map(int,l['n']));slots=l['slots'];path=l['path'];mask=np.arange(40)[None,:]<l['n'][:,None];nonlocal_entries=int(np.count_nonzero(mask&(slots<0)))
  log=(p/'raw/run-engine.log').read_text();tc=re.search('Q4_TC_END ([^\n]+)',log);oracle=re.search('Q4_ORACLE_END ([^\n]+)',log)
  def numbers(m):return {k:float(v) for k,v in re.findall(r'(\w+)=([\d.]+)',m[1])} if m else {}
  cfg=load(p/'config.json');t=cfg['env']['STRATA_Q4_TAPE'];counts=collections.Counter(zip(map(int,e['layer'][pub]),map(int,e['incoming'][pub])))
  r={'label':p.name,'task':ep['task'],'arm':ep['arm'],'kind':ep['kind'],'input':ep['run']['actual_input_tokens'],'output':ep['run']['actual_output_tokens'],'windows':len(l)//48,'main_entries':n,'local':int(np.count_nonzero(mask&(slots>=0))),'cpu':int(np.count_nonzero(mask&(path==-1))),'mapped':int(np.count_nonzero(mask&(path==1))),'nonlocal':nonlocal_entries,'planner_counters':numbers(tc),'oracle_counters':numbers(oracle),'tape':t}
  if len(e):
   assert len(e)==len(a)
   r.update(publications=int(pub.sum()),completed_bytes=int(e['bytes'][e['copy_end']>0].sum()),useful_bytes=int(e['bytes'][used].sum()),copy_bytes_per_useful_admission=float(e['bytes'][e['copy_end']>0].sum()/max(1,used.sum())),publication_to_first_use=dist(a['first_use'][used]-e['published_at'][used]),resident_lifetime_evicted=dist(a['evicted_at'][dead]-e['published_at'][dead]),resident_age_end_censored=dist(len(l)-e['published_at'][alive]),protected_lifetime_released=dist(a['released_at'][(a['released_at']>=0)&pub]-e['published_at'][(a['released_at']>=0)&pub]),distinct_uses=dist(a['distinct_uses'][pub]),repeated_distinct_admissions=int(np.count_nonzero(pub&(a['distinct_uses']>1))),reloads_beyond_first=sum(max(0,x-1) for x in counts.values()),victim_absent_entries=int(e['victim_uses'].sum()),publication_to_target_slack=dist(e['target'][pub]-e['published_at'][pub]),ready=int(np.count_nonzero(pub&(e['published_at']<=e['target']))),late=int(np.count_nonzero(pub&(e['published_at']>e['target']))),evicted_unused_bytes=int(e['bytes'][pub&~used&dead].sum()),end_censored_unused_bytes=int(e['bytes'][pub&~used&~dead].sum()),transactions_per_window=dist(np.bincount(e['trigger']//48,minlength=len(l)//48)),publications_per_window=dist(np.bincount(e['published_at'][pub]//48,minlength=len(l)//48)))
   for key,beg,end in [('issue_stage','issue_ns','stage_begin'),('stage','stage_begin','stage_end'),('copy_host_wait','copy_begin','copy_end'),('completion_publication','copy_end','publish_ns')]:
    m=e[end]>0;r[key+'_ms']=dist((e[end][m].astype(np.int64)-e[beg][m].astype(np.int64))/1e6)
   # Reconstruct next required main occurrence from recorded route IDs; label finite tail.
   future=collections.defaultdict(list)
   for row in l:
    for ex in set(map(int,row['ids'][:int(row['n'])])):future[(int(row['layer']),ex)].append(int(row['event']))
   future={k:np.array(v) for k,v in future.items()};distances=[];censored=0
   for x in e[pub]:
    v=future.get((int(x['layer']),int(x['victim'])),np.array([],dtype=int));i=np.searchsorted(v,int(x['published_at']))
    if i<len(v):distances.append(int(v[i])-int(x['published_at']))
    else:censored+=1
   r['victim_next_required_distance']=dist(distances);r['victim_next_required_end_censored']=censored;r['victim_return_definition']='Next recorded main requirement after eviction, including if readmitted before demand; absence entries separately measured.'
  rows.append(r);print('EXISTING',p.name,flush=True)
# Compare demand savings with adjacent current in the same historical block.
for r in rows:
 if 'completed_bytes' not in r:continue
 ep=load(P2/'raw'/r['label']/'episode.json');ref=next(x for x in rows if x['task']==r['task'] and x['arm']=='REPLAY_CURRENT' and load(P2/'raw'/x['label']/'episode.json')['block']==ep['block'])
 r['avoided_nonlocal_entries']=ref['nonlocal']-r['nonlocal'];r['avoided_entries_per_GB']=r['avoided_nonlocal_entries']/r['completed_bytes']*1e9
save(C/'results/existing-data-analysis.json',{'rows':rows,'censoring':'Survivors are right-censored. Lifetime statistics separate evicted generations from end survivors.','missing':['Exact DMA duration: no timing-enabled CUDA transfer events.','GPU consumer dependency readiness: no timestamp around GPU plan polling.','Native target and lifecycle generation fields: not present in NativeCopy.','Exact prevented admissions: cap scan counters lack eligible counterfactual candidate identity.'],'authority':str(P2)})
fields=['task','arm','input','output','windows','publications','completed_bytes','avoided_entries_per_GB','late','reloads_beyond_first','victim_absent_entries','nonlocal']
with (C/'results/existing-data-summary.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator="\n");w.writeheader();w.writerows(rows)
progress(1,'Existing journal analysis complete',completed=len(rows),remaining=0,next_action='Audit dependencies and implement bounded query cache')
