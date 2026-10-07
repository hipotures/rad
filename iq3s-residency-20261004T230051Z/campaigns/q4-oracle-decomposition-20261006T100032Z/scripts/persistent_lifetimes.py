"""Separate routed-entry multiplicity from persistent reuse across distinct logical layer invocations."""
from pathlib import Path
import argparse,json,collections,bisect,numpy as np
from inspect_oracle import L,E
C=Path(__file__).resolve().parents[1]
def analyze(label):
 p=C/'raw'/label;a=np.fromfile(p/'raw/oracle-layers.bin',L);e=np.fromfile(p/'raw/oracle-admissions.bin',E);incoming=collections.defaultdict(list);victims=collections.defaultdict(list)
 for i,x in enumerate(e):
  if not x['publish_ns']:continue
  incoming[(int(x['layer']),int(x['incoming']))].append((int(x['published_at']),i));victims[(int(x['layer']),int(x['victim']))].append((int(x['published_at']),i))
 for d in [incoming,victims]:
  for v in d.values():v.sort()
 count=np.zeros(len(e),np.int64);entry=np.zeros(len(e),np.int64);later=np.zeros(len(e),np.int64);first=np.full(len(e),-1,np.int64);last=first.copy()
 for r in a:
  l,ev,n=map(int,[r['layer'],r['event'],r['n']]);ids=r['ids'][:n];slots=r['slots'][:n]
  for expert in np.unique(ids[slots>=0]):
   v=incoming.get((l,int(expert)),[]);j=bisect.bisect_right(v,(ev,2**63))-1
   if j<0:continue
   i=v[j][1];mask=(ids==expert)&(slots==int(e[i]['slot']));entries=int(np.count_nonzero(mask))
   if not entries:continue
   count[i]+=1;entry[i]+=entries;later[i]+=ev>int(e[i]['target']);last[i]=ev
   if first[i]<0:first[i]=ev
 assert np.array_equal(entry,e['uses']),'Distinct lifetime accounting must conserve actual routed-entry uses'
 evicted=np.full(len(e),-1,np.int64)
 for i,x in enumerate(e):
  if not x['publish_ns']:continue
  v=victims.get((int(x['layer']),int(x['incoming'])),[]);j=bisect.bisect_right(v,(int(x['published_at']),2**63))
  if j<len(v):evicted[i]=v[j][0]
 out={'label':label,'published':int(np.count_nonzero(e['publish_ns'])),'admissions_with_one_distinct_invocation':int(np.count_nonzero(count==1)),'admissions_with_repeated_distinct_invocations':int(np.count_nonzero(count>=2)),'admissions_with_use_after_intended_target':int(np.count_nonzero(later>0)),'total_distinct_resident_uses':int(count.sum()),'routed_entry_uses':int(entry.sum()),'median_distinct_invocations_per_published':float(np.median(count[e['publish_ns']>0])) if len(e) else None,'p95_distinct_invocations_per_published':float(np.quantile(count[e['publish_ns']>0],.95)) if len(e) else None,'evicted_before_end':int(np.count_nonzero(evicted>=0)),'resident_lifetime_right_censored_at_end':int(np.count_nonzero((e['publish_ns']>0)&(evicted<0))),'units':'Distinct main routed-layer invocation, not speculative lane multiplicity. Each batch can contribute multiple routed entries but only one distinct use per expert. End survivors are censored.'}
 out['admissions_evicted_without_observed_use']=int(np.count_nonzero((e['publish_ns']>0)&(count==0)&(evicted>=0)))
 out['unused_end_censored_admissions']=int(np.count_nonzero((e['publish_ns']>0)&(count==0)&(evicted<0)))
 out['scope']='Oracle admission lifetimes only; empty current oracle journal is not zero native lifetime.'
 (C/'analysis'/f'{label}-persistent-lifetimes.json').write_text(json.dumps(out,indent=2)+'\n');np.savez_compressed(C/'analysis'/f'{label}-persistent-lifetimes.npz',distinct_uses=count,routed_entries=entry,later_invocations=later,first_use=first,last_use=last,evicted_event=evicted)
 print('PERSISTENT_REUSE_AUDIT',label,out['admissions_with_repeated_distinct_invocations'],'of',out['published'],flush=True);return out
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('labels',nargs='+');args=q.parse_args()
 for label in args.labels:analyze(label)
