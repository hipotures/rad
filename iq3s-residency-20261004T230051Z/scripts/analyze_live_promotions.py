"""Actual publication lifetimes/use and eviction demand, not counterfactual speed savings."""
import argparse,bisect,collections
import numpy as np
from lab import ROOT,load,save
from trace_reader import Trace
ap=argparse.ArgumentParser();ap.add_argument('profile',choices=['32k','128k']);ap.add_argument('--experiment',default='E012-compatible-diagnostic');ap.add_argument('--attempt',default='v1');a=ap.parse_args()
folder=ROOT/'experiments'/a.experiment/a.attempt/a.profile;t=Trace(folder/'traces/runtime-request2');assert t.validate()['state']=='PASS'
demand=collections.defaultdict(list);evictions=collections.defaultdict(list);publications=collections.defaultdict(list)
unique_groups=0;local_unique_groups=0;local_group_blob_bytes=0;CPU_unique_groups=0;mapped_unique_groups=0
for r,e in t.grouped():
    layer=int(r['layer']);at=int(r['t0']);unique_groups+=len(np.unique(e['expert']))
    for path in [-1,0,1]:
        n=len(np.unique(e['expert'][e['path']==path]))
        if path==0:local_unique_groups+=n;local_group_blob_bytes+=n*int(t.blob_bytes[layer])
        elif path==-1:CPU_unique_groups+=n
        else:mapped_unique_groups+=n
    for expert in np.unique(e['expert']):
        entries=e[e['expert']==expert];demand[(layer,int(expert))].append((at,int(np.count_nonzero(entries['path']==0)),int(np.count_nonzero(entries['path']!=0)),int(entries['slot'][0])))
for p in t.promotions:
    incoming=(int(p['layer']),int(p['incoming']));outgoing=(int(p['outgoing_layer']) if 'outgoing_layer' in p.dtype.names else int(p['layer']),int(p['outgoing']))
    evictions[outgoing].append(int(p['issue']))
    if p['observed_ready']:publications[incoming].append(int(p['observed_ready']))
for d in [evictions,publications]:
    for v in d.values():v.sort()
request_end=int(t.windows[-1]['end']);promotions=[]
for p in t.promotions:
    incoming=(int(p['layer']),int(p['incoming']));outgoing=(int(p['outgoing_layer']) if 'outgoing_layer' in p.dtype.names else int(p['layer']),int(p['outgoing']));ready=int(p['observed_ready']);issue=int(p['issue'])
    uses=None;until=None
    if ready:
        times=evictions[incoming];ix=bisect.bisect_right(times,ready);until=times[ix] if ix<len(times) else request_end+1
        uses=sum(local for at,local,nonlocal_count,slot in demand[incoming] if ready<=at<until and slot==int(p['slot']))
    returns=publications[outgoing];ix=bisect.bisect_right(returns,issue);return_at=returns[ix] if ix<len(returns) else request_end+1
    damage=sum(nonlocal_count for at,local,nonlocal_count,slot in demand[outgoing] if issue<=at<return_at)
    promotions.append({'layer':incoming[0],'expert':incoming[1],'outgoing_layer':outgoing[0],'outgoing_expert':outgoing[1],'slot':int(p['slot']),'bytes':int(p['bytes']),'published':bool(ready),'local_entries_before_next_eviction':uses,'victim_nonlocal_entries_until_next_publication':damage,'observed_resident_lifetime_us':(until-ready)/1000 if until and ready else None,'cross_layer':incoming[0]!=outgoing[0]})
published=[p for p in promotions if p['published']];useful=sum(p['bytes'] for p in published if p['local_entries_before_next_eviction']>0);unused=sum(p['bytes'] for p in published if p['local_entries_before_next_eviction']==0)
summary={'state':'PASS','profile':a.profile,'schema':t.schema,'trace_validation':t.validate(),'promotion_count':len(promotions),'promotion_bytes':sum(p['bytes'] for p in promotions),'published_useful_bytes':useful,'published_unused_bytes':unused,'unpublished_bytes':sum(p['bytes'] for p in promotions if not p['published']),'cross_layer_promotion_count':sum(p['cross_layer'] for p in promotions),'victim_nonlocal_entries':sum(p['victim_nonlocal_entries_until_next_publication'] for p in promotions),'native_group_proxy':{'all_unique_expert_groups':unique_groups,'local_unique_expert_groups':local_unique_groups,'CPU_unique_expert_groups':CPU_unique_groups,'mapped_unique_expert_groups':mapped_unique_groups,'local_unique_blob_bytes_sum':local_group_blob_bytes,'local_unique_groups_per_verify_window':local_unique_groups/len(t.windows),'local_unique_groups_per_output_token':local_unique_groups/len(t.output_ids),'semantics':'Distinct expert IDs within each actual layer/group. Blob-byte sum is a logical group work proxy, not measured DRAM or PCIe bytes; GPU caching and kernel reuse differ.'},'limits':['Observed-ready timestamps include delayed host observation; they are conservative residency intervals, not exact DMA completion.','Victim nonlocal demand is observed during absence, not a causal count of extra misses vs an alternative policy.','Useful bytes label at least one observed local use before the next withdrawal; not latency saved.','Whole trajectories differ under CPU/GPU rounding; input/window-common-prefix comparison is required.']}
save(folder/'promotion-analysis.json',summary);save(folder/'promotion-rows.json',promotions)
print({k:v for k,v in summary.items() if k not in ['trace_validation']},flush=True)
