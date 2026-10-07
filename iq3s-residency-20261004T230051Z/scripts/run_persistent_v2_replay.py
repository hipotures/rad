from lab import ROOT,load,save
from persistent_replay import PersistentReplay,bridge
from trace_reader import Trace
from replay import Replay,library
import ctypes,copy,numpy as np
base=ROOT/'experiments/E028-persistent-replay';out=base/'v2-replay';lib=ctypes.CDLL(str(out/'bridge.so'));other=bridge();lib.select_persistent_bridge.argtypes=other.select_persistent_bridge.argtypes;lib.select_persistent_bridge.restype=ctypes.c_int
assert load(base/'policy-v2-predeclared.json')['state']=='PREDECLARED_BEFORE_V2_REPLAY'
rows=[]
for num,name in enumerate(['dev-code','dev-math','cal-prose'],1):
 t=Trace(ROOT/f'experiments/E020-wide-gate-lookahead/v1/episodes/traces/runtime-request{num}');v=copy.copy(t);v.windows=t.windows[:64];v.layers=t.layers[np.isin(t.layers['window'],v.windows['number'])]
 for rate in [1.8,12.6]:
  r=PersistentReplay(v,rate,1.0,64,lib).run();r.update(policy='persistent-v2-horizon64-budget64',policy_parameters={'forecast_windows':64,'bytes_per_device':67108864},replay_view='first64windowdevelopment');save(out/f'{name}-{rate}.json',r)
  current=load(base/f'development-v1/{name}-current-{rate}.json');row={'scope':'development','name':name,'rate':rate,'nonlocals':r['nonlocal_entries'],'current_nonlocals':current['nonlocal_entries'],'wait':r['modeled_pending_wait_s'],'current_wait':current['modeled_pending_wait_s'],'GB':r['promotion_bytes']/1e9,'useful':r['useful_count'],'total':r['promotion_count']};rows.append(row);print(row,flush=True)
save(out/'development-complete.json',{'state':'FROZEN_ONE_REPAIR_NO_GRID','rows':rows,'parameters':load(base/'policy-v2-predeclared.json')})
for profile in ['32k','128k']:
 t=Trace(base/f'signal-v1/{profile}/traces/runtime-request2')
 for rate in [1.8,12.6]:
  r=PersistentReplay(t,rate,1.0,None,lib).run();r.update(policy='persistent-v2-horizon64-budget64',policy_parameters={'forecast_windows':64,'bytes_per_device':67108864});save(out/f'{profile}-{rate}.json',r)
  c=load(base/f'full-v1/{profile}-current-{rate}.json');row={'scope':'full','name':profile,'rate':rate,'nonlocals':r['nonlocal_entries'],'current_nonlocals':c['nonlocal_entries'],'wait':r['modeled_pending_wait_s'],'current_wait':c['modeled_pending_wait_s'],'GB':r['promotion_bytes']/1e9,'useful':r['useful_count'],'total':r['promotion_count'],'victim_entries':r['victim_demand_while_absent']};rows.append(row);print(row,flush=True)
save(out/'summary.json',{'state':'COMPLETE_V2_REPLAY','rows':rows,'policy':load(base/'policy-v2-predeclared.json'),'NoTGclaim':True})
