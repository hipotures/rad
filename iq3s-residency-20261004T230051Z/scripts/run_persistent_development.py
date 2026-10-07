"""Only alpha .5/1 on the preserved first three development episodes, first64windows."""
from lab import ROOT,save
from trace_reader import Trace
from persistent_replay import PersistentReplay,bridge
from replay import Replay,library
import copy, numpy as np
base=ROOT/'experiments/E028-persistent-replay';out=base/'development-v1';assert not out.exists();out.mkdir()
policy={'alphas':[.5,1.],'fixed':{'miss_entry_us':80,'forecast_windows':16,'copy_cost_GB_s':1.8,'launch_us':4.2,'margin':1.5,'bytes_per_device':16777216,'minimum_age':8,'protect_recent':2,'candidate_recent':8,'adapt_every':4,'decay':.7},'selection':'Mean development nonlocal entries with pending-wait penalty at80us/miss entry; ties favor .5; report sensitivity without choosing on holdouts.','episodes':['dev-code','dev-math','cal-prose'],'first_windows':64,'future_information':False}
save(base/'policy-v1.json',policy);results=[]
for number,name in enumerate(policy['episodes'],1):
 t=Trace(ROOT/f'experiments/E020-wide-gate-lookahead/v1/episodes/traces/runtime-request{number}');assert t.validate()['state']=='PASS'
 # A view limits demand, windows, and observed promotion events consistently; real initial state unchanged.
 view=copy.copy(t);view.windows=t.windows[:64];numbers=set(int(x) for x in view.windows['number']);view.layers=t.layers[np.isin(t.layers['window'],list(numbers))]
 for rate in [1.8,12.6]:
  current=Replay(view,'current',rate,library()).run();save(out/f'{name}-current-{rate}.json',current)
  for alpha in policy['alphas']:
   r=PersistentReplay(view,rate,alpha,64,bridge()).run();save(out/f'{name}-alpha{alpha}-{rate}.json',r);results.append({'episode':name,'alpha':alpha,'rate':rate,'nonlocal':r['nonlocal_entries'],'wait':r['modeled_pending_wait_s'],'traffic':r['promotion_bytes'],'score':r['nonlocal_entries']+r['modeled_pending_wait_s']/80e-6,'current_nonlocal':current['nonlocal_entries'],'current_wait':current['modeled_pending_wait_s']});print(results[-1],flush=True)
scores={a:float(np.mean([x['score'] for x in results if x['alpha']==a and x['rate']==1.8])) for a in policy['alphas']};selected=min(scores,key=lambda a:(scores[a],a));save(base/'selected-policy.json',{'state':'FROZEN_BEFORE_FULL_TRACE_RANKING','selected_alpha':selected,'development_scores':scores,'results':results,'policy':policy});print('SELECTED',selected,flush=True)
