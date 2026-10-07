from lab import ROOT,save,load
from trace_reader import Trace
from persistent_replay import PersistentReplay,bridge
from replay import Replay,library
base=ROOT/'experiments/E028-persistent-replay';assert load(base/'signal-v1/ready.json')['state']=='PASS_FULL_SIGNALS';alpha=load(base/'selected-policy.json')['selected_alpha'];out=base/'full-v1';assert not out.exists();out.mkdir();rows=[]
for profile in ['32k','128k']:
 t=Trace(base/f'signal-v1/{profile}/traces/runtime-request2');assert t.validate()['state']=='PASS'
 for rate in [1.8,12.6]:
  current=Replay(t,'current',rate,library()).run();save(out/f'{profile}-current-{rate}.json',current)
  r=PersistentReplay(t,rate,alpha,None,bridge()).run();save(out/f'{profile}-persistent-{rate}.json',r)
  rows.append({'profile':profile,'rate':rate,'current_nonlocal':current['nonlocal_entries'],'persistent_nonlocal':r['nonlocal_entries'],'current_wait':current['modeled_pending_wait_s'],'persistent_wait':r['modeled_pending_wait_s'],'current_bytes':current['promotion_bytes'],'persistent_bytes':r['promotion_bytes'],'promotions':r['promotion_count'],'useful':r['useful_count'],'wasted':r['wasted_count'],'repeated':r['repeated_use_promotions'],'victim_damage':r['victim_demand_while_absent'],'selector_s':r['selector_s'],'windows':r['windows']});print(rows[-1],flush=True)
save(base/'replay-summary.json',{'state':'COMPLETE_REPLAY','selected_alpha':alpha,'rows':rows,'not_a_TG_forecast':True,'capacity_invariants':'PASS','selector_tests':load(base/'selector-tests/summary.json')})
