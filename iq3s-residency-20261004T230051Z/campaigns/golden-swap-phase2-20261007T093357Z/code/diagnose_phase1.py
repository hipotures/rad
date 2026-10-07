"""Read-only generation/slot reconciliation of original Phase 1 evidence."""
import sys,json,hashlib,time,collections,bisect
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];P1=ROOT.parent/'golden-swap-phase1-20261006T200037Z';P0=ROOT.parent/'golden-swap-phase0-20261006T185015Z'
sys.path.insert(0,str(P1/'scripts'))
from inspect_oracle import E,L
from tape import Tape
from progress import update

def analyze(p):
 e=np.fromfile(p/'raw/oracle-admissions.bin',E);layers=np.fromfile(p/'raw/oracle-layers.bin',L)
 cfg=json.loads((p/'config.json').read_text());t=Tape(cfg['env']['STRATA_Q4_TAPE'])
 timeline=sorted((int(x['publish_ns']),i) for i,x in enumerate(e) if x['publish_ns'])
 live={};evict=np.full(len(e),-1,np.int64);uses=np.zeros(len(e),np.int64);distinct=uses.copy();first=np.full(len(e),-1,np.int64);target_uses=uses.copy();k=0;stale=0
 for row in layers:
  while k<len(timeline) and timeline[k][0]<=int(row['plan_end']):
   _,i=timeline[k];x=e[i];key=(int(x['layer']),int(x['victim']));old=live.pop(key,None)
   if old is not None: evict[old]=int(x['published_at'])
   key=(int(x['layer']),int(x['incoming']));assert key not in live,'duplicate resident admission';live[key]=i;k+=1
  l,ev,n=map(int,[row['layer'],row['event'],row['n']]);counts=collections.Counter()
  for ex,sl,pa in zip(row['ids'][:n],row['slots'][:n],row['path'][:n]):
   i=live.get((l,int(ex)))
   if i is not None and sl>=0:
    assert int(sl)==int(e[i]['slot']),'generation/slot mismatch'
    counts[i]+=1;stale+=int(pa)!=0
  for i,c in counts.items():
   uses[i]+=c;distinct[i]+=1
   if first[i]<0:first[i]=ev
   if ev==int(e[i]['target']):target_uses[i]+=c
 assert np.array_equal(uses,e['uses']),'host unused counter differs from service journal'
 complete=e['copy_end']>0;pub=e['publish_ns']>0;used=uses>0
 masks={'completed_unpublished':complete&~pub,'published_used_before_eviction':complete&pub&used,'published_evicted_without_use':complete&pub&~used&(evict>=0),'published_no_use_resident_at_end':complete&pub&~used&(evict<0)}
 partition={name:{'transactions':int(mask.sum()),'bytes':int(e['bytes'][mask].sum())} for name,mask in masks.items()}
 assert sum(x['bytes'] for x in partition.values())==int(e['bytes'][complete].sum())
 unused=complete&~used;early=masks['published_evicted_without_use']&(evict<e['target'])
 late_unused=unused&pub&(e['published_at']>e['target']);mismatch=0
 for x in e:
  wi,l=divmod(int(x['target']),48)
  mismatch+=int(x['incoming']) not in t.ws[wi]['routes']['ids'][l,:int(t.ws[wi]['T'])*10]
 out={'label':p.name,'completed_bytes':int(e['bytes'][complete].sum()),'completed_transactions':int(complete.sum()),'partition':partition,'incomplete':{'transactions':int((~complete).sum()),'bytes':int(e['bytes'][~complete].sum())},'unused_completed_bytes':int(e['bytes'][unused].sum()),'source_unused_issued_bytes':int(e['bytes'][~used].sum()),'evicted_before_intended_first_target_bytes':int(e['bytes'][early].sum()),'evicted_without_use_not_before_target_bytes':int(e['bytes'][masks['published_evicted_without_use']&~early].sum()),'late_published_unused_bytes':int(e['bytes'][late_unused].sum()),'target_mismatch_transactions':mismatch,'duplicate_retired_bytes':int(e['bytes'][complete&(e['status']==2)].sum()),'service_map_mismatches':stale,'distinct_resident_invocations':int(distinct.sum()),'repeated_distinct_admissions':int((distinct>=2).sum()),'target_served_transactions':int((target_uses>0).sum()),'uses_entries':int(uses.sum()),'early_eviction_examples':[{'generation':int(i),'layer':int(e[i]['layer']),'incoming':int(e[i]['incoming']),'slot':int(e[i]['slot']),'trigger':int(e[i]['trigger']),'publication':int(e[i]['published_at']),'eviction':int(evict[i]),'target':int(e[i]['target'])} for i in np.flatnonzero(early)[:4]]}
 return out
if __name__=='__main__':
 rows=[]
 for p in sorted((P1/'raw').iterdir()):
  if not '-block' in p.name or p.name.endswith('REPLAY_CURRENT'):continue
  rows.append(analyze(p));print('RECONCILED',p.name,rows[-1]['partition'],flush=True)
 (ROOT/'results/phase1-transaction-reconciliation.json').write_text(json.dumps(rows,indent=2)+'\n')
 totals={}
 for arm in ['ORACLE_FULL','ORACLE_IN_LEARNED_VICTIM']:
  rs=[r for r in rows if r['label'].endswith(arm)];totals[arm]={k:sum(r[k] for r in rs) for k in ['completed_bytes','unused_completed_bytes','evicted_before_intended_first_target_bytes','late_published_unused_bytes','target_mismatch_transactions','duplicate_retired_bytes','service_map_mismatches']}
  totals[arm]['partition']={k:{f:sum(r['partition'][k][f] for r in rs) for f in ['transactions','bytes']} for k in rs[0]['partition']}
 (ROOT/'results/phase1-transaction-totals.json').write_text(json.dumps(totals,indent=2)+'\n');print(json.dumps(totals,indent=2))
