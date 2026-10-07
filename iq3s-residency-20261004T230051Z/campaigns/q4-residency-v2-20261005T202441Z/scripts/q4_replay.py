"""Q4 same-layer physical-slot replay. No simulated throughput claims.

Integer timestamps avoid lost publications. Copies reserve/withdraw a victim,
serialize on per-device plus shared staged-link resources, then publish at the
existing next-window join. Fixed CPU/GPU work is not a latency counterfactual.
"""
from pathlib import Path
import argparse, ctypes, heapq, json, time
import numpy as np
from trace_reader import Trace
C=Path(__file__).resolve().parents[1]
SWAP=np.dtype([('gain','<f4'),('layer','<i4'),('incoming','<i4'),('outgoing','<i4')])
def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2)+'\n')
def library():
    lib=ctypes.CDLL(str(C/'analysis/current-selector/selector.so'))
    lib.select_current.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_void_p]
    lib.update_usage.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int]
    return lib

class Replay:
    def __init__(self,t,policy,rate=6.8,score_provider=None,parallel_copy=False):
        self.t=t;self.policy=policy;self.rate=rate;self.provider=score_provider
        self.parallel_copy=parallel_copy
        self.counts=t.counts();self.W=len(t.windows);self.state=t.initial.copy()
        self.cap=(self.state>=0).sum(axis=1);self.heat=t.initial_usage.copy()
        self.lib=library();self.swaps=np.zeros(96,SWAP)
        self.queue=[];self.gpu_ready=[0,0];self.link_ready=0
        self.delay=0;self.wait=0;self.rows=[];self.frames=[];self.selector_ns=0
        self.byin={};self.byout={};self.local=0;self.nonlocal_entries=0
        self.last=np.full(t.initial.shape,-10000,dtype=np.int32)
        self.freq=np.zeros(t.initial.shape,dtype=np.float32)
        self.born=np.full(t.initial.shape,-10000,dtype=np.int32)
        self.layers=[[] for _ in range(self.W)]
        for layer,entries in t.grouped():self.layers[t.window_index[int(layer['window'])]].append((layer,entries))
        self.future=None
        if policy.startswith('future'):
            self.future=np.empty(self.counts.shape,dtype=np.int32)
            n=np.full(t.initial.shape,self.W+1,dtype=np.int32)
            for i in range(self.W-1,-1,-1):
                n[self.counts[i]>0]=i;self.future[i]=n
    def publish(self,now):
        while self.queue and self.queue[0][0]<=now:
            ready,pid=heapq.heappop(self.queue);r=self.rows[pid]
            assert self.state[r['layer'],r['incoming']]<0
            assert not np.any(self.state[r['layer']]==r['slot'])
            self.state[r['layer'],r['incoming']]=r['slot'];r['published_ns']=now
            self.born[r['layer'],r['incoming']]=r['window']
    def issue(self,actions,now,i,instant=False):
        assert not self.queue
        for ordinal,(l,inc,out) in enumerate(actions):
            slot=int(self.state[l,out]);dev=int(l>=self.t.split);bb=int(self.t.blob_bytes[l])
            assert slot>=0 and self.state[l,inc]<0 and bb<=self.t.slot_bytes[dev][slot]
            self.state[l,out]=-1
            old=self.byin.pop((l,out),None)
            if old is not None:self.rows[old]['evicted_window']=i
            # Q4 canonical arena is pinned; the two actual adapt streams can
            # run concurrently. Parallel mode charges sampled3us host issue
            # per copy and measured per-device durations, rather than falsely
            # serialize two PCIe links into a single6.8GB/s staged queue.
            enqueued=now+(ordinal*3000 if self.parallel_copy and not instant else 0)
            start=max(enqueued,self.gpu_ready[dev],0 if self.parallel_copy else self.link_ready)
            end=start if instant else start+int(np.ceil(bb/self.rate))+4200
            self.link_ready=max(self.link_ready,end);self.gpu_ready[dev]=end
            r={'window':i,'layer':l,'incoming':inc,'outgoing':out,'slot':slot,'bytes':bb,
               'issue_ns':now,'copy_begin_ns':start,'ready_ns':end,'published_ns':None,
               'uses':0,'use_windows':0,'victim_entries':0,'first_use_window':None,
               'evicted_window':None,'classification':'pending'}
            pid=len(self.rows);self.rows.append(r);self.byin[l,inc]=pid;self.byout[l,out]=pid
            heapq.heappush(self.queue,(end,pid))
        if instant:self.publish(max(now,self.link_ready))
    def future_actions(self,i,capacity=False):
        if not capacity and i+1>=self.W:return []
        future=self.future[i if capacity else min(i+1,self.W-1)]
        actions=[]
        for l in range(self.t.nl):
            if capacity:
                order=np.lexsort((np.arange(self.t.ne),-(self.state[l]>=0).astype(int),future[l]))
                desired=order[:self.cap[l]]
                incoming=desired[self.state[l,desired]<0]
                victim=np.flatnonzero((self.state[l]>=0)&~np.isin(np.arange(self.t.ne),desired))
            else:
                missing=np.flatnonzero((self.state[l]<0)&(future[l]<=i+16))
                resident=np.flatnonzero(self.state[l]>=0)
                incoming=missing[np.argsort(future[l,missing],kind='stable')]
                victim=resident[np.argsort(-future[l,resident],kind='stable')]
            for inc,out in zip(incoming,victim):
                if not capacity and future[l,inc]>=future[l,out]:continue
                actions.append((int(future[l,inc]),-int(future[l,out]),l,int(inc),int(out)))
        actions.sort()
        return [(l,inc,out) for _,__,l,inc,out in actions[:None if capacity else 96]]
    def selection(self,i):
        if self.policy=='static':return []
        if self.policy=='current':
            n=self.lib.select_current(self.heat.ctypes.data,self.state.ctypes.data,self.t.nl,self.t.ne,96,self.swaps.ctypes.data)
            return [(int(x['layer']),int(x['incoming']),int(x['outgoing'])) for x in self.swaps[:n]]
        if self.policy.startswith('future') and not self.policy.startswith('future-utility'):return self.future_actions(i)
        score=self.counts[i+1:min(self.W,i+5)].sum(axis=0) if self.policy.startswith('future-utility') else self.provider(self,i)
        # All causal families share the same replacement mechanism. Score is
        # expected next4-window demand, not independent gate probabilities.
        choices=[]
        for l in range(self.t.nl):
            ins=np.flatnonzero((self.state[l]<0)&(score[l]>=1.0))
            outs=np.flatnonzero(self.state[l]>=0)
            ins=ins[np.argsort(-score[l,ins],kind='stable')]
            outs=outs[np.argsort(score[l,outs],kind='stable')]
            copy_ms=int(self.t.blob_bytes[l])/(self.rate*1e6)+.0042
            for inc,out in zip(ins,outs):
                # A transparent proxy: 0.25ms exposed cost per entry is a
                # sensitivity assumption, not a measured exclusive cost.
                benefit=float(score[l,inc]-score[l,out])*.25-copy_ms
                if benefit<=.125:break
                choices.append((benefit/int(self.t.blob_bytes[l]),l,int(inc),int(out)))
        choices.sort(key=lambda x:(-x[0],x[1],x[2],x[3]))
        # The initially narrow reference deliberately budgets32MiB/device.
        # The wide reference and causal competition retain the original96
        # total exchanges and up to160MiB/device, without additional slots.
        limit=32 if self.policy=='future-utility' else 160
        chosen=[];budget=[0,0]
        for gain,l,inc,out in choices:
            dev=int(l>=self.t.split);bb=int(self.t.blob_bytes[l])
            if len(chosen)>=96:break
            if budget[dev]+bb>limit*1024*1024:continue
            budget[dev]+=bb;chosen.append((l,inc,out))
        return chosen
    def run(self):
        origin=int(self.t.windows[0]['begin']);removed=0
        for i,w in enumerate(self.t.windows):
            base=int(w['begin'])-origin-removed;original_wait=int(w['pending_end'])-int(w['pending_begin'])
            if self.queue:
                end=max(self.gpu_ready);extra=max(0,end-(base+self.delay))
                self.delay+=extra;self.wait+=extra;self.publish(max(end,base+self.delay));assert not self.queue
            c=self.counts[i]
            if self.policy=='future-capacity-free':self.issue(self.future_actions(i,True),base+self.delay,i,True)
            local=int(c[self.state>=0].sum());bad=int(c.sum())-local
            self.local+=local;self.nonlocal_entries+=bad
            for key,pid in list(self.byin.items()):
                l,e=key
                if self.state[l,e]>=0 and c[l,e]:
                    r=self.rows[pid];r['uses']+=int(c[l,e]);r['use_windows']+=1
                    if r['first_use_window'] is None:r['first_use_window']=i
            for (l,e),pid in self.byout.items():
                if self.state[l,e]<0:self.rows[pid]['victim_entries']+=int(c[l,e])
            for layer,entries in self.layers[i]:
                l=int(layer['layer']);ids=np.ascontiguousarray(entries['expert'])
                self.lib.update_usage(self.heat[l].ctypes.data,ids.ctypes.data,len(ids))
            self.freq+=c;self.last[c>0]=i
            if self.provider is not None and hasattr(self.provider,'observe'):self.provider.observe(c,i,w)
            regular=(int(w['number'])+1)%4==0
            if (regular or self.policy=='future-feasible') and self.policy!='future-capacity-free':
                begin=time.perf_counter_ns();actions=self.selection(i);self.selector_ns+=time.perf_counter_ns()-begin
                issue=int(w['verify_end'])-origin-removed-original_wait+self.delay
                self.issue(actions,issue,i)
            if regular:
                self.heat*=np.float32(.7)
                if self.provider is not None and hasattr(self.provider,'decay'):self.provider.decay()
            self.frames.append({'window':i,'output':int(w['produced']),'nonlocal_entries':bad,'local_entries':local,'modeled_pending_wait_ns_cumulative':self.wait})
            removed+=original_wait
        for r in self.rows:
            r['classification']='target-ready' if r['first_use_window'] is not None and r['first_use_window']>r['window'] else ('unused' if r['published_ns'] is not None else 'pending')
        total=int(self.counts.sum());wall=int(self.t.windows[-1]['end'])-origin
        return {'policy':self.policy,'trace':self.t.prefix,'rate_GB_s':None if self.policy=='future-capacity-free' else self.rate,
                'queue_model':'two independent sampled pinned links' if self.parallel_copy else 'conservative shared staged link',
                'all_entries':total,'nonlocal_entries':self.nonlocal_entries,'all_routed_local_pct':100*self.local/total,
                'promotions':len(self.rows),'promotion_bytes':sum(r['bytes'] for r in self.rows),
                'used_promotion_bytes':sum(r['bytes'] for r in self.rows if r['uses']),
                'unused_promotion_bytes':sum(r['bytes'] for r in self.rows if not r['uses']),
                'victim_entries':sum(r['victim_entries'] for r in self.rows),'pending_at_end':len(self.queue),
                'modeled_pending_wait_s':self.wait/1e9,'observed_pending_wait_removed_s':removed/1e9,
                'fixed_nonpromotion_work_plus_modeled_wait_s':(wall-removed+self.wait)/1e9,
                'selector_wall_s':self.selector_ns/1e9,'selector_cost_in_timeline':False,
                'per_layer_capacity':self.cap.tolist(),'resource_bytes':[int(x.sum()) for x in self.t.slot_bytes],
                'future_information_used':self.policy.startswith('future'),'rows':self.rows,'frames':self.frames,
                'limitations':['Fixed observed mathematical/MTP trajectory; not a TG prediction',
                    'CPU/mapped/resident work is held fixed, including current-copy interference',
                    'Queue/copy/publication costs modeled; absolute GPU completion is unavailable',
                    'Same-layer physical classes; no pooled GPU memory or multi-victim allocator',
                    'Future schedules are feasible under modeled queues only, not proven optima',
                    'Causal transaction0.25ms/entry exposure and0.125ms margin are explicit proxies']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('prefix');ap.add_argument('--output',required=True);ap.add_argument('--rate',type=float,default=6.8)
    ap.add_argument('--policies',nargs='+',default=['static','current','future-capacity-free','future-feasible']);a=ap.parse_args()
    t=Trace(a.prefix);assert t.validate()['state']=='PASS'
    output=Path(a.output);output.mkdir(parents=True,exist_ok=True)
    for policy in a.policies:
        path=output/(policy+'.json');assert not path.exists()
        result=Replay(t,policy,a.rate).run();save(path,result)
        print('REPLAY',policy,result['nonlocal_entries'],result['promotion_bytes'],result['modeled_pending_wait_s'],flush=True)
if __name__=='__main__':main()
