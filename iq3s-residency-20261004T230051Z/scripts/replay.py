"""Byte/slot-aware causal policy replay and explicitly future-informed references.

This holds the observed router/MTP trajectory and non-promotion work fixed.
Queue waits and misses are projections, never measured decode improvements.
"""
import argparse,ctypes,heapq,json,pathlib,time,os
for key in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[key]='1'
import numpy as np
from trace_reader import Trace
from lab import ROOT,save

SWAP=np.dtype([('gain','<f4'),('layer','<i4'),('incoming','<i4'),('outgoing','<i4')])

class Replay:
 def __init__(self,trace,policy,rate,selector_lib):
  self.t=trace;self.policy=policy;self.rate=rate;self.lib=selector_lib
  self.counts=trace.counts();self.W=len(trace.windows)
  self.state=trace.initial.copy();self.initial_capacity=(self.state>=0).sum(axis=1)
  self.usage=trace.initial_usage.copy();self.freq=self.usage.copy();self.last=np.full(self.state.shape,-10000,dtype=np.float32)
  self.birth=np.broadcast_to(-np.arange(trace.ne,dtype=float)/trace.ne,self.state.shape).copy()
  self.queues=[];self.gpu_ready=[0.,0.];self.link_ready=0.;self.delay=0.;self.wait=0.
  self.promotions=[];self.current_used=[];self.nonlocal_entries=0;self.nonlocal_distinct=0;self.nonlocal_bytes=0
  self.demands=[];self.frames=[];self.eviction_damage=0;self.wall_selector=0.
  self.layers=[[] for _ in range(self.W)]
  for layer,entries in trace.grouped():self.layers[trace.window_index[int(layer['window'])]].append((layer,entries))
  self.buffer=np.zeros(96,dtype=SWAP)
  self.transitions=np.zeros((trace.nl,trace.ne,trace.ne),dtype=np.float32) if policy.startswith('markov') else None
  self.transition_rows=np.zeros(trace.initial.shape,dtype=np.float32) if policy.startswith('markov') else None
  self.future=np.zeros(self.counts.shape,dtype=np.int32) if policy.startswith('future') else None
  if self.future is not None:
   next_use=np.full(self.state.shape,self.W+1,dtype=np.int32)
   for i in range(self.W-1,-1,-1):
    next_use[self.counts[i]>0]=i;self.future[i]=next_use
  self.scores=np.zeros(self.state.shape,dtype=np.float32)
  self.features=None;self.scorer=None
  self.token_history=None;self.transition_update_wall_s=0.
  if policy=='token-bigram-hybrid':
   from token_history import TokenHistory
   self.token_history=TokenHistory(trace,self.layers)
  if policy.startswith('jev-'):
   from predictor_features import Features
   from train_predictors import Scorer
   self.features=Features(trace)
   self.scorer=Scorer(ROOT/'experiments/E005-expert-jev/v1/checkpoints'/(policy[4:]+'.npz'))

 def publish(self,now):
  while self.queues and self.queues[0][0]<=now:
   ready,pid=heapq.heappop(self.queues);p=self.promotions[pid]
   assert self.state[p['layer'],p['incoming']]<0
   assert not np.any(self.state[p['layer']]==p['slot'])
   self.state[p['layer'],p['incoming']]=p['slot'];p['published']=ready
   self.birth[p['layer'],p['incoming']]=p['window']

 def wait_for_pending(self,base):
  if self.queues:
   pending_finish=max(self.gpu_ready)
   extra=max(0.,pending_finish-(base+self.delay))
   self.wait+=extra;self.delay+=extra
   # Use the actual completion endpoint, not a cancellation-prone reconstructed
   # base+delay. A blocking wait must publish the entire completed batch.
   self.publish(max(pending_finish,base+self.delay))
   assert not self.queues
   return max(pending_finish,base+self.delay)
  return base+self.delay

 def issue(self,swaps,now,w):
  assert not self.queues
  for l,inc,out in swaps:
   slot=int(self.state[l,out]);assert slot>=0 and self.state[l,inc]<0
   gpu=int(l>=25);bb=int(self.t.blob_bytes[l]);assert bb<=self.t.slot_bytes[gpu][slot]
   self.state[l,out]=-1
   # Shared-link and per-device queues; conservative aggregate budget. Hardware
   # pinned2MB interpolation supports a ~4.2us launch floor, not free transfers.
   start=max(now,self.link_ready,self.gpu_ready[gpu])
   finish=start+bb/(self.rate*1e9)+4.2e-6
   self.link_ready=finish;self.gpu_ready[gpu]=finish
   pid=len(self.promotions)
   self.promotions.append({'window':w,'layer':l,'incoming':inc,'outgoing':out,'slot':slot,'bytes':bb,'issue':now,'copy_begin':start,'ready':finish,'published':None,'used_entries':0,'victim_entries_while_absent':0})
   heapq.heappush(self.queues,(finish,pid))
  self.current_used=list(range(len(self.promotions)-len(swaps),len(self.promotions)))

 def select(self,score,i,least_stale=False):
  choices=[]
  for l in range(self.t.nl):
   missing=np.flatnonzero((self.state[l]<0)&(score[l]>=2))
   resident=np.flatnonzero(self.state[l]>=0)
   if not len(missing) or not len(resident):continue
   incoming=missing[np.argsort(-score[l,missing],kind='stable')]
   if least_stale:
    # Paper-inspired adaptation: stale-before-current, then FIFO admission age.
    # Slots remain in their original layer; this is not SpecMD's global cache.
    stale=self.last[l,resident]<i-3
    victim=resident[np.lexsort((resident,self.birth[l,resident],~stale))]
   else:victim=resident[np.argsort(score[l,resident],kind='stable')]
   for inc,out in zip(incoming,victim):
    gain=float(score[l,inc]-score[l,out])
    if least_stale:
     if self.last[l,inc]<i-3:continue
     gain=float(score[l,inc])
    elif gain<1.5:break
    choices.append((gain,l,int(inc),int(out)))
  choices.sort(key=lambda x:(-x[0],x[1],x[2],x[3]))
  return [(l,inc,out) for _,l,inc,out in choices[:96]]

 def nextuse(self,i):
  if i+1>=self.W:return []
  upcoming=self.future[i+1];choices=[]
  for l in range(self.t.nl):
   missing=np.flatnonzero((self.state[l]<0)&(upcoming[l]<=i+16))
   resident=np.flatnonzero(self.state[l]>=0)
   incoming=missing[np.argsort(upcoming[l,missing],kind='stable')]
   victim=resident[np.argsort(-upcoming[l,resident],kind='stable')]
   for inc,out in zip(incoming,victim):
    if upcoming[l,inc]>=upcoming[l,out]:continue
    choices.append((int(upcoming[l,inc]),-int(upcoming[l,out]),l,int(inc),int(out)))
  choices.sort()
  return [(l,inc,out) for _,__,l,inc,out in choices[:96]]

 def run(self):
  t0=int(self.t.windows[0]['begin']);removed_wait=0.;last_frame=np.zeros(self.state.shape,dtype=np.float32)
  by_expert_promotion={};by_evicted={}
  for i,w in enumerate(self.t.windows):
   base=(int(w['begin'])-t0)/1e9-removed_wait
   original_wait=(int(w['pending_end'])-int(w['pending_begin']))/1e9
   now=self.wait_for_pending(base)
   c=self.counts[i]
   if self.policy=='future-capacity-free':
    # Clairvoyant Belady-style per-layer resident-set replacement immediately
    # before this window. Timing/issue/copy budgets are deliberately relaxed.
    for l in range(self.t.nl):
     demand=np.flatnonzero(c[l]>0)
     rank=np.lexsort((np.arange(self.t.ne),-(self.state[l]>=0).astype(int),self.future[i,l]))
     wanted=rank[:self.initial_capacity[l]]
     assert np.all(np.isin(demand,wanted))
     missing=wanted[self.state[l,wanted]<0];old=np.flatnonzero((self.state[l]>=0)&~np.isin(np.arange(self.t.ne),wanted))
     for inc,out in zip(missing,old):
      slot=int(self.state[l,out]);self.state[l,out]=-1;self.state[l,inc]=slot
      self.promotions.append({'window':i,'layer':l,'incoming':int(inc),'outgoing':int(out),'slot':slot,'bytes':int(self.t.blob_bytes[l]),'issue':now,'ready':now,'published':now,'used_entries':0,'victim_entries_while_absent':0})
   frame_bad=0;frame_distinct=0
   for layer,es in self.layers[i]:
    l=int(layer['layer']);bad=self.state[l,es['expert']]<0
    self.nonlocal_entries+=int(bad.sum());frame_bad+=int(bad.sum())
    unique=np.unique(es['expert'][bad]);self.nonlocal_distinct+=len(unique);frame_distinct+=len(unique);self.nonlocal_bytes+=len(unique)*int(self.t.blob_bytes[l])
    ids=np.ascontiguousarray(es['expert']);self.lib.update_usage(self.usage[l].ctypes.data,ids.ctypes.data,len(ids))
   self.freq+=c;self.last[c>0]=i
   if self.features is not None:self.features.observe(c,i)
   if self.token_history is not None:self.token_history.observe(i)
   for (l,e),pid in list(by_expert_promotion.items()):
    if self.state[l,e]>=0:self.promotions[pid]['used_entries']+=int(c[l,e])
   for (l,e),pid in list(by_evicted.items()):
    if self.state[l,e]<0:self.promotions[pid]['victim_entries_while_absent']+=int(c[l,e])
   self.frames.append({'window':int(w['number']),'output':int(w['produced']),'nonlocal_entries':frame_bad,'nonlocal_distinct_jobs':frame_distinct,'transfer_wait_s_cumulative':self.wait})
   if self.transitions is not None:
    update_start=time.perf_counter()
    for l in range(self.t.nl):
     src=np.flatnonzero(last_frame[l]>0);dst=np.flatnonzero(c[l]>0)
     if len(src) and len(dst):
      self.transitions[l][np.ix_(src,dst)]+=last_frame[l,src][:,None]*c[l,dst][None,:]
      self.transition_rows[l,src]+=last_frame[l,src]*c[l].sum()
    self.transition_update_wall_s+=time.perf_counter()-update_start
   regular_adapt=(int(w['number'])+1)%4==0
   if (regular_adapt or self.policy=='future-nextuse') and self.policy not in ['static','future-capacity-free']:
    start=time.perf_counter()
    if self.policy=='global-compatible-ema':
     swaps=self.compatible(i)
    elif self.policy=='current':
     n=self.lib.select_current(self.usage.ctypes.data,self.state.ctypes.data,self.t.nl,self.t.ne,96,self.buffer.ctypes.data)
     swaps=[(int(p['layer']),int(p['incoming']),int(p['outgoing'])) for p in self.buffer[:n]]
    elif self.policy=='future-nextuse':swaps=self.nextuse(i)
    else:
     if self.policy=='frequency':score=self.freq
     elif self.policy=='recency':score=self.last+2
     elif self.policy=='least-stale-adapted':score=self.usage
     elif self.policy.startswith('markov'):
      predicted=np.einsum('li,lij->lj',c/(self.transition_rows+1),self.transitions,optimize=False)
      score=np.asarray(self.usage*.5+predicted*(.5*4/.3 if self.policy=='markov-scaled' else 2),dtype=np.float32)
     elif self.policy=='token-bigram-hybrid':score=self.usage+self.token_history.current/.3
     elif self.policy=='future-feasible':score=self.counts[i+1:min(self.W,i+5)].sum(axis=0)
     elif self.policy.startswith('jev-'):
      # Expected next4-window count is put into the baseline heat's steady-state
      # units: one4-window block contributes 1/(1-decay) blocks of heat.
      score=self.scorer.predict(self.features.matrix(i)).reshape(self.state.shape)/.3
     else:raise ValueError(self.policy)
     swaps=self.select(score,i,self.policy=='least-stale-adapted')
    self.wall_selector+=time.perf_counter()-start
    # All demands are available only after verify. Immutable slots have no
    # in-flight readers here. Copy issue can overlap commit/draft work.
    issue=(int(w['verify_end'])-t0)/1e9-removed_wait-original_wait+self.delay
    self.issue(swaps,issue,i)
    for pid in self.current_used:
     p=self.promotions[pid];by_expert_promotion[p['layer'],p['incoming']]=pid;by_evicted[p.get('outgoing_layer',p['layer']),p['outgoing']]=pid
   if regular_adapt:
    self.usage*=np.float32(.7)
    if self.features is not None:self.features.decay()
   last_frame=c;removed_wait+=original_wait
  total=int(self.counts.sum());used=[p for p in self.promotions if p['used_entries']>0]
  wall=(int(self.t.windows[-1]['end'])-t0)/1e9
  return {'policy':self.policy,'aggregate_transfer_budget_GB_s':None if self.policy=='future-capacity-free' else self.rate,'trace':self.t.prefix,'demand_entries':total,'nonlocal_entries':self.nonlocal_entries,'all_demand_local_hit_pct':100*(1-self.nonlocal_entries/total),'nonlocal_distinct_group_jobs':self.nonlocal_distinct,'nonlocal_weight_bytes_per_group':self.nonlocal_bytes,'promotion_count':len(self.promotions),'promotion_bytes':sum(p['bytes'] for p in self.promotions),'useful_promotion_bytes':sum(p['bytes'] for p in used) if self.policy!='future-capacity-free' else None,'unused_promotion_bytes':sum(p['bytes'] for p in self.promotions if p['used_entries']==0) if self.policy!='future-capacity-free' else None,'victim_demand_while_absent':sum(p['victim_entries_while_absent'] for p in self.promotions) if self.policy!='future-capacity-free' else None,'modeled_pending_wait_s':self.wait,'observed_window_wall_s':wall,'observed_pending_wait_removed_s':removed_wait,'fixed_nonpromotion_work_plus_modeled_wait_s':wall-removed_wait+self.wait,'offline_Python_selector_wall_s':self.wall_selector,'selector_time_charged_to_timeline':False,'resource_bytes_per_GPU':[int(b.sum()) for b in self.t.slot_bytes],'per_layer_capacity':self.initial_capacity.tolist(),'future_information_used':self.policy.startswith('future'),'frames':self.frames,'promotions':self.promotions,'limitations':['fixed observed demand/MTP/numerical trajectory','queue waits are modeled; CPU/mapped/resident execution cost remains fixed','selector measured in external Python/NumPy replay; not deployable runtime cost and not hidden in claimed TG','same-layer capacities and original physical slot classes; no extra VRAM','copy queues serialize on a conservative aggregate link and two per-device resources','free-transfer reference is intentionally optimistic; future-feasible and future-nextuse are heuristics under assumed measured-range costs, not optimum or proven upper bound']}

def library():
 path=ROOT/'experiments/E004-replay/v1/current-validation-32k/selector.so'
 lib=ctypes.CDLL(str(path));lib.select_current.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_void_p];lib.update_usage.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int]
 return lib
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('prefix');ap.add_argument('--output',required=True);ap.add_argument('--policies',nargs='+',default=['static','current','recency','frequency','least-stale-adapted','markov','future-capacity-free','future-feasible']);ap.add_argument('--rate',type=float,default=12.6);a=ap.parse_args()
 out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=True);trace=Trace(a.prefix);assert trace.validate()['state']=='PASS'
 for policy in a.policies:
  target=out/(policy+'.json')
  if target.exists():raise RuntimeError('Refuse overwrite of deterministic replay')
  runner=Replay(trace,policy,a.rate,library());result=runner.run()
  if runner.token_history is not None:result['causal_prediction']=runner.token_history.metadata()
  if runner.transitions is not None:result['transition_state_bytes']=runner.transitions.nbytes+runner.transition_rows.nbytes;result['transition_state_update_wall_s']=runner.transition_update_wall_s
  save(target,result)
  print(json.dumps({k:result[k] for k in ['policy','nonlocal_entries','promotion_bytes','modeled_pending_wait_s','offline_Python_selector_wall_s']}),flush=True)
