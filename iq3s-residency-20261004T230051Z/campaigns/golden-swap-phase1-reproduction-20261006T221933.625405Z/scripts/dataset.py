"""Reconstruct actual native ownership, sample eligible residents and label censored futures."""
import argparse,hashlib,time,bisect,json
import numpy as np
from common import *
from legacy_tape import Tape
from validate_traces import L,N
from features import *
def task_dataset(task,smoke=False):
 start=time.monotonic();name=task['task_id'];p=P0/'raw'/name;t=Tape(p/'tape.bin');validation=t.validate();assert validation['state']=='PASS';a=np.fromfile(p/'raw/native-layers.bin',L);n=np.fromfile(p/'raw/native-native.bin',N);res=t.initial.copy();uses=[[[] for _ in range(512)] for _ in range(48)]
 for wi,w in enumerate(t.ws):
  for l in range(48):
   for e in np.unique(w['routes']['ids'][l,:10*int(w['T'])]):uses[l][e].append(wi*48+l)
 actions=[]
 for x in n:
  actions.append((int(x['issue_ns']),0,int(x['layer']),int(x['victim']),-1))
  if x['publish_ns']:actions.append((int(x['publish_ns']),1,int(x['layer']),int(x['incoming']),int(x['slot'])))
 actions.sort();idx=0;hist=History();rng=np.random.default_rng(20261006);X=[];Y=[];M=[];meta=[];weights=[];observed=0;masked=0;checks=0
 for ev,row in enumerate(a):
  l=ev%48;wi=ev//48;ids=row['ids'][:int(row['n'])];assert np.array_equal(ids,t.ws[wi]['routes']['ids'][l,:len(ids)])
  while idx<len(actions) and actions[idx][0]<=int(row['begin']):
   _,_,ll,ee,slot=actions[idx];res[ll,ee]=slot;idx+=1
  assert np.array_equal(res[l,ids],row['slots'][:len(ids)]),(name,ev,'native ownership mismatch');checks+=len(ids)
  # Every fourth main window, one uniform sample of eight eligible retained residents/layer.
  # Each candidate set is equally weighted; uniform inclusion probability is k/N.
  if wi%4==0:
   protected=np.unique(t.ws[wi]['routes']['ids'][l,:len(ids)]);eligible=np.setdiff1d(np.flatnonzero(res[l]>=0),protected);k=min(8,len(eligible))
   if k:
    es=np.sort(rng.choice(eligible,k,replace=False));xx=hist.features(l,es,ev);yy=np.zeros((k,4),np.uint8);mm=np.zeros((k,4),np.uint8);end=(len(t.ws)-1)*48+l;dist=[]
    for j,e in enumerate(es):
     future=uses[l][e];z=bisect.bisect_right(future,ev);nx=future[z] if z<len(future) else None;d=(nx-ev)/48 if nx is not None else np.inf;dist.append(d)
     for hidx,h in enumerate(HORIZONS):
      positive=d<=h;yy[j,hidx]=positive;mm[j,hidx]=positive or end-ev>=int(h)*48
    X.append(xx);Y.append(yy);M.append(mm);meta.extend([(ev,l,int(e),len(eligible),k,float(d)) for e,d in zip(es,dist)]);weights.extend([1/k]*k);observed+=int(yy.sum());masked+=int((1-mm).sum())
  hist.observe(l,ids,ev)
  if smoke and wi>=16:break
 arrays={'X':np.concatenate(X),'Y':np.concatenate(Y),'M':np.concatenate(M),'meta':np.array(meta,dtype=np.float64),'weight':np.array(weights,dtype=np.float64)}
 dest=C/'data'/(name+('-smoke' if smoke else '')+'.npz');np.savez_compressed(dest,**arrays)
 # A suffix intervention never enters History: compare independent prefix extraction.
 hist2=History();prefix=min(16,len(t.ws))*48
 for ev,row in enumerate(a[:prefix]):hist2.observe(ev%48,row['ids'][:int(row['n'])],ev)
 before=hist2.features(0,np.arange(512),prefix);changed=t.ws.copy();changed['routes']['ids'][min(16,len(t.ws)-1):]=0;after=hist2.features(0,np.arange(512),prefix);assert np.array_equal(before,after)
 r={'task':name,'split':task['split'],'family':task['family'],'rows':len(arrays['X']),'positive_horizon_labels':observed,'censored_horizon_labels':masked,'native_slot_entry_checks':checks,'ownership_reconstruction':'exact issue-removal/publication-admission, timestamp replay validated against every routed entry','sample_probability':'min(8,N)/N uniform eligible residents; decision-normalized weight 1/k','selection_bias':'Uniform samples from native-policy residents; deployment distribution can differ. No victim-only selection. Native eviction labels retained separately in Phase0 reference.','elapsed_s':time.monotonic()-start,'tape_sha256':validation['tape_sha256'],'work_sha256':validation['work_sha256'],'file_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'suffix_invariance':True,'initial_history':'No pre-request last-use known; seen flag marks observed prefix; count/EMA features expressly count request prefix only','horizons_main_windows':HORIZONS.tolist()};save(C/'data'/(name+('-smoke' if smoke else '')+'-manifest.json'),r);progress(1,'Dataset '+name+' ready',completed_task=name,rows=r['rows']);return r
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('--smoke',action='store_true');q.add_argument('--task');args=q.parse_args();no_gpu();tasks=load(P0/'benchmark-manifest.json')['tasks'];tasks=[t for t in tasks if not args.task or t['task_id']==args.task]
 save(C/'data/schema.json',{'features':NAMES,'horizons_windows':HORIZONS.tolist(),'one_window_routed_invocations':48,'labels':'Next batch use strictly after current event, <=H*48 positive; no return negative only with observation to endpoint; otherwise mask=0','features_unavailable_omitted':['native complete dynamic heat','queue state','MTP subdivisions','policy resident age and eviction counters (not needed by prefix-only feature set)'],'simultaneous_batch':'count multiplicity for frequencies; one gap per unique expert, no lane order','seed':20261006,'sampling':'Every fourth window, each layer, uniform 8 eligible native residents excluding declared current-window safety protection'})
 with Heartbeat('causal dataset',1):rows=[task_dataset(t,args.smoke) for t in tasks]
 save(C/'data'/('smoke-manifest.json' if args.smoke else 'dataset-manifest.json'),rows)
