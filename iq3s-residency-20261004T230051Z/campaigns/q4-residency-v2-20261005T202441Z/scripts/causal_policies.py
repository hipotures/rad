"""Bounded causal scorers share one physical scheduler and incoming/victim costs."""
import os
for name in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[name]='1'
import time, numpy as np
from q4_features import Features
from train_q4 import Scorer
from campaign import C
class Provider:
    def __init__(self,t,name):
        self.t=t;self.name=name;self.f=Features(t);self.update_ns=0;self.feature_ns=0;self.scoring_ns=0
        self.model=Scorer(C/'checkpoints'/f'{name[4:]}.npz') if name.startswith('jev-') else None
        self.transition=np.zeros((t.nl,t.ne,t.ne),np.float32) if name=='markov' else None
        self.row=np.zeros(t.initial.shape,np.float32) if self.transition is not None else None
        self.previous=None
    def observe(self,c,i,w):
        begin=time.perf_counter_ns();self.f.observe(c,i)
        if self.transition is not None and self.previous is not None:
            for l in range(self.t.nl):
                src=np.flatnonzero(self.previous[l]>0);dst=np.flatnonzero(c[l]>0)
                if not len(src) or not len(dst):continue
                # Count-conditioned adjacency, only already completed windows.
                self.transition[l][np.ix_(src,dst)]+=self.previous[l,src][:,None]*c[l,dst]
                self.row[l,src]+=self.previous[l,src]*c[l].sum()
        self.previous=c;self.update_ns+=time.perf_counter_ns()-begin
    def decay(self):self.f.decay()
    def __call__(self,r,i):
        begin=time.perf_counter_ns();c=self.previous
        if self.name=='ema':score=r.heat*.3
        elif self.name=='recency':score=self.f.fast*2
        elif self.name=='frequency':score=r.freq*4/(i+1)
        elif self.name=='least-stale-inspired':
            # Explicit stale-last4 approximation, not SpecMD's global FIFO
            # prefetch-marked implementation. Still charge victim expected use.
            score=r.heat*.3;score[self.f.last<i-3]*=.25
        elif self.name=='markov':
            predicted=np.einsum('li,lij->lj',c/np.maximum(1,self.row),self.transition,optimize=False)
            score=r.heat*.15+predicted*2
        elif self.name.startswith('jev-'):
            feature_begin=time.perf_counter_ns();x=self.f.matrix(i);self.feature_ns+=time.perf_counter_ns()-feature_begin
            score=self.model.predict(x).reshape(r.state.shape)
        elif self.name=='hybrid-history':score=r.heat*.2+self.f.fast*(2/3)
        else:raise ValueError(self.name)
        self.scoring_ns+=time.perf_counter_ns()-begin
        return np.asarray(score,np.float32)
    def costs(self):
        return {'state_update_s':self.update_ns/1e9,'feature_s':self.feature_ns/1e9,'scoring_including_features_s':self.scoring_ns/1e9,
                'memory_bytes':sum(x.nbytes for x in [self.f.heat,self.f.fast,self.f.slow,self.f.freq,self.f.last])+
                (0 if self.transition is None else self.transition.nbytes+self.row.nbytes),
                'cost_in_timeline':False,'scope':'Offline CPU replay; full live contention/selection cost still required'}
