"""Corrected replay protocol: policy-specific warmup state, prediction heat, recency, pending drain."""
from lab import ROOT,load,save
from trace_reader import Trace
from persistent_replay import PersistentReplay,bridge
from replay import Replay,library
import ctypes,numpy as np
base=ROOT/'experiments/E028-persistent-replay';out=base/'warm-chain-v1';assert not out.exists();out.mkdir();lib=ctypes.CDLL(str(base/'v2-replay/bridge.so'));v1=bridge();lib.select_persistent_bridge.argtypes=v1.select_persistent_bridge.argtypes;lib.select_persistent_bridge.restype=ctypes.c_int;rows=[]
for profile in ['32k','128k']:
 warm=Trace(base/f'signal-v1/{profile}/traces/runtime-request1');main=Trace(base/f'signal-v1/{profile}/traces/runtime-request2');assert warm.validate()['state']==main.validate()['state']=='PASS'
 delta=main.initial_usage-warm.final_usage;assert np.min(delta)>-1e-4,delta.min()
 for rate in [1.8,12.6]:
  first=PersistentReplay(warm,rate,1.0,None,lib);wr=first.run();first.wait_for_pending(1e6) # betweenrequests allpendingdrained before batchedprefill, outside measureddecode
  next_=PersistentReplay(main,rate,1.0,None,lib);next_.state=first.state.copy();next_.usage=first.usage+delta;next_.predheat=first.predheat.copy();next_.last_use=first.last_use.copy();next_.birth_use=first.birth_use.copy();r=next_.run();r.update(policy='persistent-v2-policy-specific-warmchain',warmup={'output':len(warm.output_ids),'actualwindows':len(warm.windows),'promotions':wr['promotion_count'],'copy_bytes':wr['promotion_bytes'],'pending_drained_between_requests':True,'prediction_heat_and_recency_retained':True},protocol_difference='Earlier E028fullreplay started from P1afterwarm state withzero prediction andunknown recency. This correctedreplay appliespersistentpolicy torealwarm trajectory andretainsitsstate; stillfixedtrue-routing/mathtrajectory. No newlive requests.');save(out/f'{profile}-{rate}.json',r)
  rows.append({'profile':profile,'rate':rate,'nonlocals':r['nonlocal_entries'],'bytes':r['promotion_bytes'],'wait':r['modeled_pending_wait_s'],'useful':r['useful_count'],'wasted':r['wasted_count'],'victim':r['victim_demand_while_absent'],'warmup_promotions':wr['promotion_count']});print(rows[-1],flush=True)
save(out/'summary.json',{'state':'COMPLETE_CORRECTED_CAUSAL_WARMUP_REPLAY','rows':rows,'limits':['Warmup fixedrealP1trajectory, not regenerated candidateoutput.','Betweenrequests drain excludedfromdecode; nextprefill originalheatdelta heldfixed.','No exactTGprediction.']})
