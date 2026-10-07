"""Causal Q4 per-expert state; expected future counts are explicit censored labels."""
import numpy as np
NAMES=['heat','fast','slow','last_count','recent4','previous4','recent8','frequency',
       'age','seen','initial_resident','initial_heat','layer','stage','blob','trend']
BASIC=[0,1,2,3,4,7,8,9,10,11,12,13,14]
TEMPORAL=list(range(len(NAMES)))
class Features:
    def __init__(self,trace):
        self.t=trace;self.heat=trace.initial_usage.copy();self.fast=np.zeros_like(self.heat)
        self.slow=self.fast.copy();self.freq=self.fast.copy();self.last=np.full(self.heat.shape,-10000,np.int32);self.history=[]
    def observe(self,c,i):
        self.heat+=c;self.fast=self.fast*.5+c;self.slow=self.slow*.95+c
        self.freq+=c;self.last[c>0]=i;self.history.append(c)
    def matrix(self,i):
        shape=self.heat.shape;recent=np.sum(self.history[max(0,i-3):i+1],axis=0)
        previous=np.sum(self.history[max(0,i-7):max(0,i-3)],axis=0) if i>=4 else np.zeros(shape)
        columns=[np.log1p(self.heat),np.log1p(self.fast*2),np.log1p(self.slow*.2),
                 np.log1p(self.history[-1]),np.log1p(recent),np.log1p(previous),np.log1p(recent+previous),
                 np.log1p(self.freq*4/(i+1)),np.log1p(np.minimum(10000,i-self.last)),self.last>=0,
                 self.t.initial>=0,np.log1p(self.t.initial_usage),
                 np.broadcast_to((np.arange(shape[0])/47)[:,None],shape),
                 np.broadcast_to((np.arange(shape[0])>=self.t.split)[:,None],shape),
                 np.broadcast_to((self.t.blob_bytes/3072000)[:,None],shape),
                 (recent-previous)/(1+recent)]
        return np.stack(columns,axis=-1).reshape(-1,len(NAMES)).astype(np.float32)
    def decay(self):self.heat*=np.float32(.7)
def frames(t,horizon=4):
    counts=t.counts();f=Features(t)
    for i,w in enumerate(t.windows):
        f.observe(counts[i],i)
        if (int(w['number'])+1)%4==0:
            if i+horizon<len(counts):yield i,f.matrix(i),counts[i+1:i+horizon+1].sum(axis=0).ravel()
            f.decay()
