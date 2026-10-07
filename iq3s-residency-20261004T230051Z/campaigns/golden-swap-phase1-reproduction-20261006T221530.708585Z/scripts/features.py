"""Features are functions solely of completed main routed batches in this request.
No native dynamic heat/queue/protection placeholders. Initial history is explicitly unknown.
"""
import numpy as np
NAMES=['layer_fraction','device','class_3584','class_3993','seen_in_prefix','log_recency_windows','log_ema4_entries','log_ema64_entries','log_prefix_entries','log_last_gap_windows','log_mean_gap_windows','gap_cv','log_observed_windows']
HORIZONS=np.array([1,4,16,64],dtype=np.int32)
def byteclass(l):return 2 if l==2 else 1 if l in [4,30,46,47] else 0
class History:
 def __init__(self):
  self.last=np.full((48,512),-1,dtype=np.int32);self.total=np.zeros((48,512),dtype=np.float64);self.fast=self.total.copy();self.slow=self.total.copy();self.lastgap=self.total.copy();self.gaps=self.total.copy();self.gapsum=self.total.copy();self.gapsq=self.total.copy();self.updated=np.full(48,-1,dtype=np.int32)
 def features(self,l,es,at):
  es=np.asarray(es,dtype=np.int32);wi=at/48;seen=self.last[l,es]>=0;rec=np.where(seen,wi-self.last[l,es],wi+1);dt=wi-max(0,int(self.updated[l]));fast=self.fast[l,es]*np.exp(-dt/4);slow=self.slow[l,es]*np.exp(-dt/64);g=self.gaps[l,es];mu=np.divide(self.gapsum[l,es],g,out=np.zeros(len(es)),where=g>0);variance=np.maximum(0,np.divide(self.gapsq[l,es],g,out=np.zeros(len(es)),where=g>0)-mu*mu);cv=np.divide(np.sqrt(variance),mu,out=np.zeros(len(es)),where=mu>0)
  return np.column_stack([np.full(len(es),l/47),np.full(len(es),l//24),np.full(len(es),byteclass(l)==1),np.full(len(es),byteclass(l)==2),seen,np.log1p(np.maximum(0,rec)),np.log1p(fast),np.log1p(slow),np.log1p(self.total[l,es]),np.log1p(self.lastgap[l,es]),np.log1p(mu),cv,np.full(len(es),np.log1p(wi))]).astype(np.float32)
 def observe(self,l,ids,ev):
  wi=ev//48;dt=wi-max(0,int(self.updated[l]));self.fast[l]*=np.exp(-dt/4);self.slow[l]*=np.exp(-dt/64);self.updated[l]=wi
  counts=np.bincount(ids,minlength=512);es=np.flatnonzero(counts);previous=self.last[l,es];valid=previous>=0;ees=es[valid];gap=wi-previous[valid];self.lastgap[l,ees]=gap;self.gaps[l,ees]+=1;self.gapsum[l,ees]+=gap;self.gapsq[l,ees]+=gap*gap;self.last[l,es]=wi;self.total[l]+=counts;self.fast[l]+=counts;self.slow[l]+=counts
