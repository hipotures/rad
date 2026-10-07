"""Reconstruct protection occupancy and concurrent nonlocal service, not causal opportunity regret."""
import numpy as np,re,collections
from common import *
from transactions import LC
from inspect_oracle import E,L
from tape import Tape

def analyze(p):
 cfg=load(p/'config.json');ctl=cfg['env'].get('STRATA_Q4_TRANSACTION_CONTROL')=='1'
 if not ctl:return None
 e=np.fromfile(p/'raw/oracle-admissions.bin',E);a=np.fromfile(p/'raw/oracle-lifecycle.bin',LC);layers=np.fromfile(p/'raw/oracle-layers.bin',L);length=len(layers);delta=np.zeros((2,3,length+1),np.int32);durations=[];bytes_duration=0
 for x,z in zip(e,a):
  if not x['publish_ns']:continue
  l=int(x['layer']);d=l//24;c={3072000:0,3584000:1,3993600:2}[int(x['bytes'])];start=int(x['published_at']);end=int(z['released_at']) if z['released_at']>=0 else length;end=min(end,length)
  if end<=start:continue
  delta[d,c,start]+=1;delta[d,c,end]-=1;durations.append(end-start);bytes_duration+=int(x['bytes'])*(end-start)
 occupancy=np.cumsum(delta[:,:,:length],axis=2);assert int(occupancy.max(initial=0))<=16
 crowded_nonlocal=0;crowded_events=0;first_target_routed_entries=0
 for row in layers:
  ev,l,n=int(row['event']),int(row['layer']),int(row['n']);c=2 if l==2 else 1 if l in [4,30,46,47] else 0
  if occupancy[l//24,c,ev]>=16:crowded_events+=1;crowded_nonlocal+=int(np.count_nonzero(row['slots'][:n]<0))
 result={'label':p.name,'max_per_device_class':int(occupancy.max(initial=0)),'mean_protected_total':float(occupancy.sum(axis=(0,1)).mean()),'protected_expert_invocations':int(occupancy.sum()),'protected_byte_invocations':bytes_duration,'protected_duration_invocations':{'min':min(durations),'median':float(np.median(durations)),'max':max(durations)} if durations else None,'class_cap_event_samples':int(np.count_nonzero(occupancy>=16)),'nonlocal_entries_at_cap_for_active_class':crowded_nonlocal,'routed_invocations_at_cap':crowded_events,'interpretation':'Required nonlocal service while the class protection cap is full identifies competing opportunity exposure. It is not proven preventable admission or exclusive causal loss: copy worker/eligibility/cost guard also constrain admission. Exact counterfactual opportunity regret is unmeasured.'}
 return result
if __name__=='__main__':
 no_gpu();rows=[analyze(p) for p in sorted((C/'raw').iterdir()) if (p/'episode.json').exists() and load(p/'episode.json')['valid']];rows=[r for r in rows if r];save(C/'results/protection-opportunity-costs.json',rows);print('PROTECTION_COSTS',len(rows),flush=True)
