"""Summarize observable demand/critical-path brackets without adding overlapping waits."""
import argparse,collections,json,pathlib
import numpy as np
from trace_reader import Trace
from lab import ROOT,save
ap=argparse.ArgumentParser();ap.add_argument('prefix');ap.add_argument('--output',required=True);a=ap.parse_args()
t=Trace(a.prefix);v=t.validate();assert v['state']=='PASS'
def distribution(x):
 x=np.asarray(x,dtype=float)
 return {'n':len(x),'sum':float(x.sum()),'median':float(np.median(x)),'p95':float(np.percentile(x,95)),'max':float(x.max())} if len(x) else None
counts=t.counts();miss=np.zeros(counts.shape[:2],dtype=np.int32);cpu=miss.copy();mapped=miss.copy();distinct=miss.copy();miss_ids=collections.Counter();all_ids=collections.Counter();per_layer=[]
for layer,entries in t.grouped():
 w=t.window_index[int(layer['window'])];l=int(layer['layer']);bad=entries['path']!=0
 miss[w,l]+=int(bad.sum());cpu[w,l]+=int((entries['path']<0).sum());mapped[w,l]+=int((entries['path']==1).sum());distinct[w,l]+=len(np.unique(entries['expert'][bad]))
 miss_ids.update((l,int(e)) for e in entries['expert'][bad]);all_ids.update((l,int(e)) for e in entries['expert'])
reach=np.zeros(miss.shape);host=reach.copy()
for r in t.reach:
 w=t.window_index[int(r['window'])];l=int(r['layer']);reach[w,l]+=(int(r['reached'])-int(r['begin']))/1e6;host[w,l]+=(int(r['released'])-int(r['reached']))/1e6
def correlation(x,y):
 x=np.asarray(x).ravel();y=np.asarray(y).ravel()
 return float(np.corrcoef(x,y)[0,1]) if np.std(x)>0 and np.std(y)>0 else None
for l in range(t.nl):
 per_layer.append({'layer':l,'gpu':int(l>=25),'slots':int((t.initial[l]>=0).sum()),'blob_bytes':int(t.blob_bytes[l]),'demand_entries':int(counts[:,l].sum()),'CPU_entries':int(cpu[:,l].sum()),'mapped_entries':int(mapped[:,l].sum()),'nonlocal_distinct_group_jobs':int(distinct[:,l].sum()),'GPU_reach_wait_ms':distribution(reach[:,l]),'host_pool_plan_release_ms':distribution(host[:,l])})
windows=[]
for i,w in enumerate(t.windows):
 pp=t.promotions[t.promotions['window']==w['number']];windows.append({'window':int(w['number']),'produced':int(w['produced']),'T':int(w['T']),'accepted':int(w['accepted']),'wall_ms':(int(w['end'])-int(w['begin']))/1e6,'pending_wait_ms':(int(w['pending_end'])-int(w['pending_begin']))/1e6,'CPU_entries':int(cpu[i].sum()),'mapped_entries':int(mapped[i].sum()),'distinct_nonlocal_jobs':int(distinct[i].sum()),'promotion_bytes':int(pp['bytes'].sum())})
progression=[];previous_produced=0
for lo,hi in [(0,512),(512,1024),(1024,2048),(2048,4096)]:
 mask=(t.windows['produced']>lo)&(t.windows['produced']<=hi)
 ww=t.windows[mask];d=counts[mask].sum();m=miss[mask].sum();c=cpu[mask].sum();p=mapped[mask].sum()
 if not len(ww):continue
 elapsed=(int(ww[-1]['end'])-int(ww[0]['begin']))/1e9;produced=int(ww[-1]['produced'])-(int(t.windows[np.flatnonzero(mask)[0]-1]['produced']) if np.flatnonzero(mask)[0] else 0)
 progression.append({'requested_range':[lo,hi],'aligned_output_count':produced,'window_aligned_TG':produced/elapsed,'elapsed_s':elapsed,'local_all_demand_hit_pct':100*(1-m/d),'CPU_entries':int(c),'mapped_entries':int(p),'MTP_accept_pct':100*ww['accepted'].sum()/max(1,int(ww['T'].sum())-len(ww)),'mean_committed_per_window':produced/len(ww),'boundary_uncertainty':'bounded by a verify window, at most4tokens; no interpolation fabricated'})
result={'prefix':a.prefix,'validation':v,'layers':per_layer,'windows':windows,'progression':progression,'pending_wait_ms':distribution([w['pending_wait_ms'] for w in windows]),'observed_issue_to_publication_ms':distribution([(int(p['observed_ready'])-int(p['issue']))/1e6 for p in t.promotions if p['observed_ready']]),'top_repeated_nonlocal_experts':[{'layer':l,'expert':e,'nonlocal_entries':n,'all_entries':all_ids[l,e]} for (l,e),n in miss_ids.most_common(30)],'lagged_correlations':{'previous_layer_nonlocal_vs_next_GPU_reach_wait':correlation(miss[:,:-1],reach[:,1:]),'previous_layer_mapped_vs_next_GPU_reach_wait':correlation(mapped[:,:-1],reach[:,1:]),'same_layer_nonlocal_vs_host_work':correlation(miss,host)},'interpretation':['host clocks only; issue-to-publication includes delayed observation and is not device DMA duration','GPU reach includes resident expert, dense, KV and dispatch dependencies; no all-wait miss attribution','lagged correlations are observational, confounded by T/output/layer; not causal cost-per-miss','window-aligned diagnostic progression is more resolved than1Hz but contains instrumentation overhead']}
save(a.output,result);print(json.dumps({k:result[k] for k in ['prefix','progression','pending_wait_ms','observed_issue_to_publication_ms','lagged_correlations']},indent=2))
