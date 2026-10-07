"""Admission-generation outcomes from buffered journals, with exact byte conservation."""
import collections,hashlib
import numpy as np
from common import *
from inspect_oracle import E,L,N
LC=np.dtype([(k,'<i4') for k in ['generation','first_use','last_use','distinct_uses','evicted_at','released_at','expiry','reason']]);assert LC.itemsize==32

def reconcile(p,main_events=None):
 e=np.fromfile(p/'raw/oracle-admissions.bin',E);a=np.fromfile(p/'raw/oracle-lifecycle.bin',LC);layers=np.fromfile(p/'raw/oracle-layers.bin',L);assert len(e)==len(a)
 live={};k=0;timeline=sorted((int(x['publish_ns']),i) for i,x in enumerate(e) if x['publish_ns']);uses=np.zeros(len(e),np.int64);distinct=uses.copy();first=np.full(len(e),-1,np.int64);last=first.copy();evicted=first.copy();target=uses.copy();prefix_uses=uses.copy()
 for row in layers:
  while k<len(timeline) and timeline[k][0]<=int(row['plan_end']):
   _,i=timeline[k];x=e[i];old=live.pop((int(x['layer']),int(x['victim'])),None)
   if old is not None:evicted[old]=int(x['published_at'])
   key=(int(x['layer']),int(x['incoming']));assert key not in live;live[key]=i;k+=1
  l,ev,n=map(int,[row['layer'],row['event'],row['n']]);counts=collections.Counter()
  for ex,sl,path in zip(row['ids'][:n],row['slots'][:n],row['path'][:n]):
   i=live.get((l,int(ex)))
   if i is not None and sl>=0:assert sl==e[i]['slot'] and path==0;counts[i]+=1
  for i,c in counts.items():
   uses[i]+=c;distinct[i]+=1;last[i]=ev
   if first[i]<0:first[i]=ev
   if ev==e[i]['target']:target[i]+=c
   if main_events is not None and ev<main_events:prefix_uses[i]+=c
 assert np.array_equal(uses,e['uses']) and np.array_equal(distinct,a['distinct_uses']) and np.array_equal(first,a['first_use']) and np.array_equal(evicted,a['evicted_at'])
 complete=e['copy_end']>0;pub=e['publish_ns']>0;used=uses>0
 masks={'completed_unpublished':complete&~pub,'published_used_before_eviction':complete&pub&used,'published_evicted_without_use':complete&pub&~used&(evicted>=0),'published_no_use_resident_at_end':complete&pub&~used&(evicted<0)}
 partition={k:{'transactions':int(m.sum()),'bytes':int(e['bytes'][m].sum())} for k,m in masks.items()};assert sum(x['bytes'] for x in partition.values())==int(e['bytes'][complete].sum())
 repeated=collections.Counter((int(x['layer']),int(x['incoming'])) for x in e if x['publish_ns']);lifetime_durations=(np.where(evicted>=0,evicted,len(layers))-e['published_at'])[pub]
 protected=(a['released_at']-e['published_at'])[(a['released_at']>=0)&pub];result={'partition':partition,'completed_bytes':int(e['bytes'][complete].sum()),'staged_bytes':int(e['bytes'][e['stage_end']>0].sum()),'incomplete_bytes':int(e['bytes'][~complete].sum()),'unused_completed_bytes':int(e['bytes'][complete&~used].sum()),'evicted_before_first_target_bytes':int(e['bytes'][masks['published_evicted_without_use']&(evicted<e['target'])].sum()),'actual_used_bytes':int(e['bytes'][complete&used].sum()),'target_served_transactions':int((target>0).sum()),'late_publications':int((pub&(e['published_at']>e['target'])).sum()),'repeat_admissions_beyond_first':sum(max(0,n-1) for n in repeated.values()),'distinct_resident_uses':int(distinct.sum()),'repeated_distinct_admissions':int((distinct>=2).sum()),'service_entries':int(uses.sum()),'protection_duration_invocations':{'median':float(np.median(protected)),'max':int(max(protected))} if len(protected) else None,'end_protected':int((pub&(a['released_at']<0)&(a['reason']==0)).sum()),'unknowns':['DMA-only time; exclusive CPU latency; natural output quality; MTP residency path subdivisions'], 'reconciled_generations':len(e)}
 if main_events is not None:
  resident_at_boundary=pub&(e['published_at']<main_events)&((evicted<0)|(evicted>=main_events));no_prefix_use=resident_at_boundary&(prefix_uses==0)
  result['prefix']={'event_boundary':main_events,'no_use_yet_resident_bytes':int(e['bytes'][no_prefix_use].sum()),'later_observed_use_bytes':int(e['bytes'][no_prefix_use&(uses>prefix_uses)].sum()),'no_observed_tail_use_bytes':int(e['bytes'][no_prefix_use&(uses==prefix_uses)].sum()),'observation':'Finite tail only; untouched restoration separate'}
 return result

def reconcile_native(p,main_events=None,prefix_time_ns=None):
 """Native victim withdrawal is at copy issue; incoming ownership starts at publication."""
 e=np.fromfile(p/'raw/oracle-native.bin',N);layers=np.fromfile(p/'raw/oracle-layers.bin',L);timeline=[]
 for i,x in enumerate(e):
  timeline.append((int(x['issue_ns']),0,i))
  if x['publish_ns']:timeline.append((int(x['publish_ns']),1,i))
 timeline.sort();live={};evicted=np.full(len(e),-1,np.int64);first=evicted.copy();distinct=np.zeros(len(e),np.int64);uses=distinct.copy();prefix=uses.copy();k=0;pub_event=np.full(len(e),-1,np.int64)
 for row in layers:
  ev=int(row['event'])
  while k<len(timeline) and timeline[k][0]<=int(row['plan_end']):
   _,action,i=timeline[k];x=e[i];l=int(x['layer'])
   if action==0:
    old=live.pop((l,int(x['victim'])),None)
    if old is not None:evicted[old]=ev
   else:
    key=(l,int(x['incoming']));assert key not in live;live[key]=i;pub_event[i]=ev
   k+=1
  l=int(row['layer']);counts=collections.Counter()
  for expert,slot,path in zip(row['ids'][:int(row['n'])],row['slots'][:int(row['n'])],row['path'][:int(row['n'])]):
   i=live.get((l,int(expert)))
   if i is not None and slot>=0:assert slot==e[i]['slot'] and path==0;counts[i]+=1
  for i,c in counts.items():
   uses[i]+=c;distinct[i]+=1
   if first[i]<0:first[i]=ev
   if main_events is not None and ev<main_events:prefix[i]+=c
 # Complete the chronological ownership ledger through request finish. There is no
 # routed service after the last observation; later publications are end-censored,
 # but a later withdrawal can still terminate an older unused generation.
 while k<len(timeline):
  _,action,i=timeline[k];x=e[i];l=int(x['layer'])
  if action==0:
   old=live.pop((l,int(x['victim'])),None)
   if old is not None:evicted[old]=len(layers)
  else:
   key=(l,int(x['incoming']));assert key not in live;live[key]=i;pub_event[i]=len(layers)
  k+=1
 # Finish may publish queued native copies after last routed service; those are end-censored.
 pub=e['publish_ns']>0;used=uses>0;masks={'completed_unpublished':np.zeros(len(e),bool),'published_used_before_eviction':pub&used,'published_evicted_without_use':pub&~used&(evicted>=0),'published_no_use_resident_at_end':pub&~used&(evicted<0)}
 part={k:{'transactions':int(m.sum()),'bytes':int(e['bytes'][m].sum())} for k,m in masks.items()};assert sum(x['bytes'] for x in part.values())==int(e['bytes'][pub].sum())
 repeats=collections.Counter((int(x['layer']),int(x['incoming'])) for x in e if x['publish_ns'])
 result={'partition':part,'completed_bytes':int(e['bytes'][pub].sum()),'staged_bytes':None,'incomplete_bytes':None if np.any(~pub) else 0,'unpublished_completion_unknown_bytes':int(e['bytes'][~pub].sum()),'unused_completed_bytes':int(e['bytes'][pub&~used].sum()),'evicted_before_first_target_bytes':None,'actual_used_bytes':int(e['bytes'][pub&used].sum()),'target_served_transactions':None,'late_publications':None,'repeat_admissions_beyond_first':sum(max(0,n-1) for n in repeats.values()),'distinct_resident_uses':int(distinct.sum()),'repeated_distinct_admissions':int((distinct>=2).sum()),'service_entries':int(uses.sum()),'protection_duration_invocations':None,'end_protected':0,'reconciled_generations':len(e),'authority':'Native issue withdrawal/publication; no native intended oracle target. Publication certifies completion; unpublished completion lacks independent marker. End publication after last service is censored.'}
 if main_events is not None:
  boundary=int(prefix_time_ns) if prefix_time_ns is not None else int(layers[main_events-1]['plan_end']);withdrawals=collections.defaultdict(list)
  for x in e:withdrawals[(int(x['layer']),int(x['victim']))].append(int(x['issue_ns']))
  censored=[]
  for i,x in enumerate(e):
   if not pub[i] or int(x['publish_ns'])>boundary or prefix[i]>0:continue
   if any(int(x['publish_ns'])<t<=boundary for t in withdrawals[(int(x['layer']),int(x['incoming']))]):continue
   censored.append(i)
  result['prefix']={'event_boundary':main_events,'no_use_yet_resident_bytes':sum(int(e[i]['bytes']) for i in censored),'later_observed_use_bytes':sum(int(e[i]['bytes']) for i in censored if uses[i]>prefix[i]),'no_observed_tail_use_bytes':sum(int(e[i]['bytes']) for i in censored if uses[i]==prefix[i]),'observation':'Native completed publication generations only; finite tail.'}
 return result
