"""Persistent boundary admission on real horizon8 signals; queue/capacity charged."""
import argparse,ctypes,heapq,pathlib,time
import numpy as np
from lab import ROOT,load,save
from replay import Replay,library
from placement_replay import CompatibleReplay
from trace_reader import Trace
ROW=np.dtype([('utility','<f8')]+[(k,'<i4') for k in ['layer','in','out_layer','out','slot','pad']]+[('bytes','<u8')]);assert ROW.itemsize==40
PRED=np.dtype([(k,'<u8') for k in ['window','available_ns','offset']]+[(k,'<i4') for k in ['current_layer','target_layer','tokens','k']])
class PersistentReplay(CompatibleReplay):
 def __init__(self,t,rate,alpha,limit,bridge):
  super().__init__(t,'global-compatible-ema',rate,library());self.policy='persistent-router-alpha'+str(alpha);self.alpha=alpha;self.bridge=bridge;self.limit=limit
  self.predheat=np.zeros_like(self.usage);self.last.fill(-1);self.last_use=np.full(t.initial.shape,2**64-1,dtype=np.uint64);self.birth_use=self.last_use.copy();self.rows=np.zeros(96,ROW)
  self.signal={};self.signal_time={};self.selection_calls=0
  pred=np.fromfile(t.prefix+'-gpu-router-predictions.bin',PRED);ids=np.fromfile(t.prefix+'-gpu-router-values.bin','<i4');prob=np.fromfile(t.prefix+'-gpu-router-confidence.bin','<f4')
  assert len(ids)==len(prob) and np.isfinite(prob).all()
  for p in pred:
   if int(p['target_layer']-p['current_layer'])!=8:continue
   w=int(p['window']);target=int(p['target_layer']);origin=int(p['current_layer']);assert (origin<25)==(target<25)
   at=int(p['offset']);n=int(p['tokens']*p['k']);values=ids[at:at+n];weights=prob[at:at+n];assert np.all((values>=0)&(values<512))
   self.signal.setdefault(w,[]).append((target,values,weights));self.signal_time[w]=max(self.signal_time.get(w,0),int(p['available_ns']))
 def publish(self,now):
  pending=[pid for ready,pid in self.queues if ready<=now]
  super().publish(now)
  for pid in pending:
   self.promotions[pid]["copy_completed_at"]=self.promotions[pid]["ready"]
   self.promotions[pid]["published"]=now
 def choose(self,w):
  args=[self.usage.ctypes.data,self.predheat.ctypes.data,self.last_use.ctypes.data,self.birth_use.ctypes.data,self.state.ctypes.data,self.t.blob_bytes.ctypes.data,self.t.slot_bytes[0].ctypes.data,len(self.t.slot_bytes[0]),self.t.slot_bytes[1].ctypes.data,len(self.t.slot_bytes[1]),w,self.alpha,self.rows.ctypes.data]
  n=self.bridge.select_persistent_bridge(*args);self.selection_calls+=1
  return [(int(x['layer']),int(x['in']),int(x['out_layer']),int(x['out'])) for x in self.rows[:n]]
 def run(self):
  t=self.t;t0=int(t.windows[0]['begin']);removed=0.;by_in={};by_out={};W=min(self.W,self.limit or self.W);start=time.perf_counter()
  for i,w in enumerate(t.windows[:W]):
   number=int(w['number']);base=(int(w['begin'])-t0)/1e9-removed;oldwait=(int(w['pending_end'])-int(w['pending_begin']))/1e9
   now=self.wait_for_pending(base);c=self.counts[i];bad_total=0
   for gpu,(lo,hi) in enumerate([(0,25),(25,t.nl)]):
    used=self.state[lo:hi][self.state[lo:hi]>=0];assert len(used)==len(np.unique(used))
    for l in range(lo,hi):
     resident=self.state[l][self.state[l]>=0];assert np.all(t.blob_bytes[l]<=t.slot_bytes[gpu][resident])
   for row,es in self.layers[i]:
    l=int(row['layer']);bad=self.state[l,es['expert']]<0;bad_total+=int(bad.sum());self.nonlocal_entries+=int(bad.sum());u=np.unique(es['expert'][bad]);self.nonlocal_distinct+=len(u);self.nonlocal_bytes+=len(u)*int(t.blob_bytes[l])
    self.lib.update_usage(self.usage[l].ctypes.data,np.ascontiguousarray(es['expert']).ctypes.data,len(es))
   self.last_use[c>0]=number
   # Predictions consumed only after their CPU observation, before safe verify-end issue.
   assert not self.signal.get(number) or self.signal_time[number]<=int(w['verify_end'])
   for l,ids,weights in self.signal.get(number,[]):
    for e,p in zip(ids,weights):self.predheat[l,int(e)]+=np.float32(p*10)
   for (l,e),pid in by_in.items():
    p=self.promotions[pid]
    if self.state[l,e]>=0:p['used_entries']+=int(c[l,e]);p.setdefault('use_windows',[])
    if self.state[l,e]>=0 and c[l,e]>0:
     p['use_windows'].append(number)
     if p.get('first_actual_demand_window') is None:
      p['first_actual_demand_window']=number;p['first_actual_demand_time']=now;p['ready_for_first_subsequent_demand']=p['published'] is not None and p['published']<=now
   for (l,e),pid in by_out.items():
    if self.state[l,e]<0:self.promotions[pid]['victim_entries_while_absent']+=int(c[l,e])
   self.frames.append({'window':number,'output':int(w['produced']),'nonlocal_entries':bad_total,'wait_s_cumulative':self.wait})
   if (number+1)%4==0:
    st=time.perf_counter();swaps=self.choose(number);self.wall_selector+=time.perf_counter()-st
    issue=(int(w['verify_end'])-t0)/1e9-removed-oldwait+self.delay
    self.issue(swaps,issue,i)
    for pid in self.current_used:
     p=self.promotions[pid];p['runtime_window']=number;p['prediction_observation_ns']=self.signal_time.get(number);p['prediction_window_targets_already_executed']=True;p['prediction_available_window']=number if self.signal.get(number) else None;p['publication_protocol']='Next window after completion; no current-window early-hit claim';p['first_actual_demand_window']=None;p['use_windows']=[]
     by_in[p['layer'],p['incoming']]=pid;by_out[p['outgoing_layer'],p['outgoing']]=pid;self.birth_use[p['layer'],p['incoming']]=number
    self.usage*=np.float32(.7);self.predheat*=np.float32(.7)
   removed+=oldwait
  total=int(self.counts[:W].sum());useful=[p for p in self.promotions if p['used_entries']>0];wasted=[p for p in self.promotions if not p['used_entries']];repeated=[p for p in useful if len(p['use_windows'])>1]
  result={'state':'COMPLETE_PERSISTENT_REPLAY','policy':self.policy,'alpha':self.alpha,'trace':t.prefix,'windows':W,'signal_windows':sum(int(w['number']) in self.signal for w in t.windows[:W]),'demand_entries':total,'nonlocal_entries':self.nonlocal_entries,'promotion_count':len(self.promotions),'promotion_bytes':sum(p['bytes'] for p in self.promotions),'useful_count':len(useful),'useful_bytes':sum(p['bytes'] for p in useful),'wasted_count':len(wasted),'wasted_bytes':sum(p['bytes'] for p in wasted),'repeated_use_promotions':len(repeated),'victim_demand_while_absent':sum(p['victim_entries_while_absent'] for p in self.promotions),'modeled_pending_wait_s':self.wait,'aggregate_transfer_budget_GB_s':self.rate,'resources_per_GPU_bytes':[int(x.sum()) for x in t.slot_bytes],'selector_s':self.wall_selector,'replay_wall_s':time.perf_counter()-start,'future_information_used':False,'copy_cost_used_for_selection_GB_s':1.8,'ready_for_first_subsequent_demand':sum(bool(p.get('ready_for_first_subsequent_demand')) for p in self.promotions),'unpublished_at_trace_end':sum(p['published'] is None for p in self.promotions),'capacity_owner_byte_invariants':'PASS every window','frames':self.frames,'promotions':self.promotions,'limits':['Fixed real routing/MTP/output trajectory, not aTGforecast.','Boundary publication intentionally cannot help firstcurrent-window target demand. Subsequentuses are measured.','Missentry utility80us and16window horizon are conservative approximate designunits, not a separatelyidentified causal kernel time.','SelectorCPU measured offline but not charged into GPUtimeline; live measurement required.','Birth/recency guarded, sameGPU fittingclass,16MiB/device/adaptbatch; immutableweights require no restore.']}
  return result
def bridge():
 path=ROOT/'experiments/E028-persistent-replay/selector-tests/bridge.so';lib=ctypes.CDLL(str(path));lib.select_persistent_bridge.argtypes=[ctypes.c_void_p]*7+[ctypes.c_int,ctypes.c_void_p,ctypes.c_int,ctypes.c_uint64,ctypes.c_float,ctypes.c_void_p];lib.select_persistent_bridge.restype=ctypes.c_int;return lib
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('prefix');ap.add_argument('--output',required=True);ap.add_argument('--alpha',type=float,choices=[.5,1.],required=True);ap.add_argument('--rate',type=float,choices=[1.8,12.6],default=1.8);ap.add_argument('--limit',type=int);a=ap.parse_args();assert not pathlib.Path(a.output).exists()
 t=Trace(a.prefix);assert t.validate()['state']=='PASS';r=PersistentReplay(t,a.rate,a.alpha,a.limit,bridge()).run();save(a.output,r);print({k:r[k] for k in ['policy','windows','nonlocal_entries','promotion_count','promotion_bytes','useful_count','wasted_count','victim_demand_while_absent','modeled_pending_wait_s']},flush=True)
