"""Causal numeric expert features. Later demand is used only for explicit labels."""
import numpy as np
NAMES=['heat','fast_heat','slow_heat','last_window','recent4','previous4','recent8','frequency','age','ever_seen','initial_resident','initial_heat','expert_id_fraction','layer_fraction','stage1','blob_fraction','momentum']
BASIC=[0,1,2,4,7,8,9,10,11,12,13,14,15]
TEMPORAL=list(range(len(NAMES)))
class Features:
 def __init__(self,trace):
  self.t=trace;self.heat=trace.initial_usage.copy();self.fast=np.zeros(trace.initial.shape,dtype=np.float32);self.slow=self.fast.copy();self.frequency=self.fast.copy();self.last=np.full(trace.initial.shape,-10000,dtype=np.int32);self.history=[]
 def observe(self,count,i):
  self.heat+=count;self.fast=self.fast*.5+count;self.slow=self.slow*.95+count;self.frequency+=count;self.last[count>0]=i;self.history.append(count)
 def matrix(self,i):
  shape=self.t.initial.shape;recent=np.sum(self.history[max(0,i-3):i+1],axis=0);previous=np.sum(self.history[max(0,i-7):max(0,i-3)],axis=0) if i>=4 else np.zeros(shape)
  columns=[np.log1p(self.heat),np.log1p(self.fast*2),np.log1p(self.slow*.2),np.log1p(self.history[-1]),np.log1p(recent),np.log1p(previous),np.log1p(recent+previous),np.log1p(self.frequency*4/(i+1)),np.log1p(np.minimum(10000,i-self.last)),self.last>=0,self.t.initial>=0,np.log1p(self.t.initial_usage),np.broadcast_to(np.arange(shape[1])/max(1,shape[1]-1),shape),np.broadcast_to((np.arange(shape[0])/max(1,shape[0]-1))[:,None],shape),np.broadcast_to((np.arange(shape[0])>=25)[:,None],shape),np.broadcast_to((self.t.blob_bytes/2662400)[:,None],shape),(recent-previous)/(1+recent)]
  return np.stack(columns,axis=-1).reshape(-1,len(NAMES)).astype(np.float32)
 def decay(self):self.heat*=np.float32(.7)
def frames(trace,horizon=4):
 counts=trace.counts();features=Features(trace)
 for i,w in enumerate(trace.windows):
  features.observe(counts[i],i)
  if (int(w['number'])+1)%4==0:
   if i+horizon<len(counts):yield i,features.matrix(i),counts[i+1:i+horizon+1].sum(axis=0).ravel()
   features.decay()
