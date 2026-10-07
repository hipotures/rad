"""Deterministic tests of physical fit, age, recency, utility, budget, and reservations."""
import numpy as np
from lab import ROOT,save
from persistent_replay import bridge,ROW
lib=bridge();never=2**64-1
r=np.full((48,512),-1,dtype=np.int32);h=np.zeros_like(r,dtype=np.float32);p=h.copy();last=np.full(r.shape,never,dtype=np.uint64);born=last.copy()
bb=np.full(48,1024*1024,dtype=np.uint64);s0=np.array([1024*1024,2*1024*1024],dtype=np.uint64);s1=s0.copy();out=np.zeros(96,ROW)
r[0,0]=0;r[1,0]=1;r[25,0]=0;r[26,0]=1
h[2,2]=40;last[2,2]=20;h[27,3]=40;last[27,3]=20
checks={}
def select(window=20,alpha=.5):
 n=lib.select_persistent_bridge(h.ctypes.data,p.ctypes.data,last.ctypes.data,born.ctypes.data,r.ctypes.data,bb.ctypes.data,s0.ctypes.data,len(s0),s1.ctypes.data,len(s1),window,alpha,out.ctypes.data);return out[:n].copy()
a=select();checks['same_device_cross_layer']=len(a)==2 and all((x['layer']<25)==(x['out_layer']<25) for x in a)
checks['distinct_slots']=len(set((int(x['layer']>=25),int(x['slot'])) for x in a))==len(a)
last[0,0]=20;last[1,0]=20;checks['protect_recent_victim']=len(select())==1
last[0,0]=never;last[1,0]=never;born[0,0]=19;born[1,0]=19;checks['minimum_resident_age']=len(select())==1
born.fill(never);last[2,2]=10;checks['candidate_recent']=len(select())==1
last[2,2]=20;bb[2]=3*1024*1024;checks['reject_oversize']=len(select())==1
bb[2]=1024*1024;h[2,2]=2;checks['charge_copy_utility']=len(select())==1
p[2,2]=100;checks['prediction_changes_admission']=len(select())==2
r[0,0]=-1;r[1,0]=-1;checks['reserved_unpublished_slots_not_victims']=len(select())==1
h[2,2]=np.nan;checks['reject_nonfinite']=len(select())==0
# Bounded stress with all slots unique and mixed byte classes.
r.fill(-1);h.fill(0);p.fill(0);last.fill(never);born.fill(never);bb.fill(1024*1024)
s0=np.full(32,1024*1024,dtype=np.uint64);s1=s0.copy()
for gpu,base in enumerate([0,25]):
 for e in range(32):r[base,e]=e
 for e in range(32,100):h[base,e]=100;last[base,e]=100
rows=select(100);checks['budget_per_device']=all(int(rows[rows['layer']>=25 if g else rows['layer']<25]['bytes'].sum())<=16*1024*1024 for g in [0,1]);checks['unique_incoming']=len(set((int(x['layer']),int(x['in'])) for x in rows))==len(rows)
checks['deterministic']=rows.tobytes()==select(100).tobytes()
assert all(checks.values()),checks
save(ROOT/'experiments/E028-persistent-replay/selector-tests/summary.json',{'state':'PASS','checks':checks,'scope':'Pure selector; asynchronous publication/reader safety requires separate runtime tests.'});print(checks)
