"""Causal bounded token-bigram history. Predict residency, never mathematical routing."""
from collections import OrderedDict
import time
import numpy as np
class TokenHistory:
    def __init__(self,trace,grouped_layers,capacity=256):
        self.t=trace;self.layers=grouped_layers;self.capacity=capacity
        self.table=OrderedDict();self.previous=None;self.queries=0;self.hits=0
        self.current=np.zeros(trace.initial.shape,dtype=np.float32)
        self.wall_update=0.;self.payload_peak_bytes=0
    def observe(self,index):
        start=time.perf_counter();window=self.t.windows[index]
        # All routed rows remain in demand, including rejected drafts. Only
        # committed rows teach the next-input-token dictionary.
        accepted=int(window['accepted']);T=int(window['T'])
        rows=np.empty((T,self.t.nl,10),dtype=np.int16)
        counts=np.zeros((T,self.t.nl),dtype=np.int32)
        for layer,entries in self.layers[index]:
            l=int(layer['layer'])
            for row in np.unique(entries['token']):
                ids=entries['expert'][entries['token']==row]
                if len(ids)!=10:raise ValueError('Expected ten true routed experts per global row/layer')
                rows[int(row),l]=ids;counts[int(row),l]=10
        if not np.all(counts==10):raise ValueError('Incomplete routed row')
        for row in range(accepted+1):
            token=int(window['tokens'][row])
            if self.previous is not None:
                key=(self.previous,token)
                self.table[key]=rows[row].copy();self.table.move_to_end(key)
                if len(self.table)>self.capacity:self.table.popitem(last=False)
            self.previous=token
        self.payload_peak_bytes=max(self.payload_peak_bytes,sum(x.nbytes for x in self.table.values()))
        self.current.fill(0)
        if index+1<len(self.t.windows):
            next_token=int(self.t.output_ids[int(window['produced'])-1])
            # Future rows are consulted only by this assertion, never features.
            assert next_token==int(self.t.windows[index+1]['tokens'][0])
            self.queries+=1;key=(self.previous,next_token)
            if key in self.table:
                self.hits+=1;prediction=self.table[key];self.table.move_to_end(key)
                for l in range(self.t.nl):self.current[l,prediction[l]]=1
        self.wall_update+=time.perf_counter()-start
    def metadata(self):
        return {'available_signal':'Known outv[a] after verify plus last committed input token; historical committed rows only. No future router IDs or rejected rows are used as features.',
                'capacity_bigrams':self.capacity,'dictionary_queries':self.queries,'dictionary_hits':self.hits,
                'dictionary_payload_peak_bytes':self.payload_peak_bytes,'update_wall_s':self.wall_update,
                'memory_limits':'Payload bytes exclude Python container overhead. C++ deployment memory and cost not yet measured; no GPU state.',
                'score':'Causal heat + predicted next-row count / 0.3; bounded same-layer admission, no routing changes.'}
