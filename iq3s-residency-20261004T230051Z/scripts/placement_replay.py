"""One causal compatible-slot placement policy, same per-device physical memory."""
import argparse, heapq, time
import numpy as np
from lab import save
from trace_reader import Trace
from replay import Replay,library

class CompatibleReplay(Replay):
    def compatible(self,index):
        choices=[]
        for gpu,(begin,end) in enumerate([(0,25),(25,self.t.nl)]):
            victims={};incoming=[]
            for layer in range(begin,end):
                for expert in np.flatnonzero(self.state[layer]>=0):
                    slot=int(self.state[layer,expert]);size=int(self.t.slot_bytes[gpu][slot])
                    heapq.heappush(victims.setdefault(size,[]),(float(self.usage[layer,expert]),layer,int(expert),slot))
                incoming.extend((float(self.usage[layer,e]),layer,int(e)) for e in np.flatnonzero((self.state[layer]<0)&(self.usage[layer]>=2)))
            incoming.sort(key=lambda x:(-x[0],x[1],x[2]))
            for heat,layer,expert in incoming:
                fitting=[size for size,bucket in victims.items() if size>=int(self.t.blob_bytes[layer]) and bucket]
                if not fitting:continue
                size=min(fitting,key=lambda size:(victims[size][0][0],size))
                cold,vl,ve,slot=victims[size][0]
                if heat<cold+1.5:continue
                heapq.heappop(victims[size]);choices.append((heat-cold,layer,expert,vl,ve))
        choices.sort(key=lambda x:(-x[0],x[1],x[2],x[3],x[4]))
        return [(l,e,vl,ve) for _,l,e,vl,ve in choices[:96]]
    def publish(self,now):
        while self.queues and self.queues[0][0]<=now:
            ready,pid=heapq.heappop(self.queues);p=self.promotions[pid];l=p['layer'];gpu=int(l>=25)
            assert self.state[l,p['incoming']]<0
            assert not np.any(self.state[(0 if gpu==0 else 25):(25 if gpu==0 else self.t.nl)]==p['slot'])
            self.state[l,p['incoming']]=p['slot'];p['published']=ready;self.birth[l,p['incoming']]=p['window']
    def issue(self,swaps,now,window):
        assert not self.queues
        start_count=len(self.promotions)
        for layer,expert,vl,ve in swaps:
            assert (layer>=25)==(vl>=25)
            slot=int(self.state[vl,ve]);gpu=int(layer>=25);bb=int(self.t.blob_bytes[layer])
            assert slot>=0 and self.state[layer,expert]<0 and bb<=int(self.t.slot_bytes[gpu][slot])
            self.state[vl,ve]=-1
            begin=max(now,self.link_ready,self.gpu_ready[gpu]);ready=begin+bb/(self.rate*1e9)+4.2e-6
            self.link_ready=ready;self.gpu_ready[gpu]=ready;pid=len(self.promotions)
            self.promotions.append({'window':window,'layer':layer,'incoming':expert,'outgoing_layer':vl,'outgoing':ve,'slot':slot,'bytes':bb,'physical_slot_bytes':int(self.t.slot_bytes[gpu][slot]),'issue':now,'copy_begin':begin,'ready':ready,'published':None,'used_entries':0,'victim_entries_while_absent':0})
            heapq.heappush(self.queues,(ready,pid))
        self.current_used=list(range(start_count,len(self.promotions)))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('prefix');ap.add_argument('--output',required=True);ap.add_argument('--rate',type=float,default=12.6);a=ap.parse_args()
    import pathlib
    if pathlib.Path(a.output).exists():raise RuntimeError('Existing placement replay')
    t=Trace(a.prefix);assert t.validate()['state']=='PASS'
    runner=CompatibleReplay(t,'global-compatible-ema',a.rate,library());r=runner.run()
    r['final_per_layer_capacity']=(runner.state>=0).sum(axis=1).tolist()
    r['cross_layer_promotions']=sum(p['outgoing_layer']!=p['layer'] for p in r['promotions'])
    r['physical_slot_wasted_bytes_per_promotion_sum']=sum(p['physical_slot_bytes']-p['bytes'] for p in r['promotions'])
    r['placement_constraints']='Original physical variable-size slots; same GPU layer ownership. No additional memory or cross-GPU experts. Victim may be in another layer only when incoming blob fits.'
    r['limitations']=[x for x in r['limitations'] if 'same-layer capacities' not in x]+['Per-layer capacities can change inside the original per-GPU physical slot classes. The policy is causal EMA global-compatible admission, not a future oracle. Heap matcher is a bounded heuristic, not optimal variable-byte packing.']
    save(a.output,r)
    print({k:r[k] for k in ['policy','nonlocal_entries','promotion_bytes','modeled_pending_wait_s','offline_Python_selector_wall_s','cross_layer_promotions']})
