"""Find the earliest observed input, residency, routing and path divergence."""
import json
import numpy as np
from lab import ROOT, save
from trace_reader import Trace
out=ROOT/'experiments/E016-device-plan-ids/divergence-v1'
if out.exists():raise RuntimeError('Existing divergence report')
out.mkdir()
summary={}
for p in ['32k','128k']:
 for request in [1,2]:
  a=Trace(ROOT/'experiments/E008-router-boundary/v2'/p/f'traces/runtime-request{request}')
  b=Trace(ROOT/'experiments/E016-device-plan-ids/diagnostic-v1'/p/f'traces/runtime-request{request}')
  res={'initial_residency_identical':bool(np.array_equal(a.initial,b.initial)), 'initial_heat_identical':bool(np.array_equal(a.initial_usage,b.initial_usage)), 'windows':[len(a.windows),len(b.windows)],'first_output_divergence':None,'common_windows':[]}
  n=min(len(a.output_ids),len(b.output_ids));bad=np.flatnonzero(a.output_ids[:n]!=b.output_ids[:n]);res['first_output_divergence']=int(bad[0]) if len(bad) else None
  for n,(aw,bw) in enumerate(zip(a.windows,b.windows)):
   t=int(aw['T']);same=t==int(bw['T']) and np.array_equal(aw['tokens'][:t],bw['tokens'][:t])
   r={'ordinal':n,'same_input_ids':bool(same),'tokens':[aw['tokens'][:t].tolist(),bw['tokens'][:int(bw['T'])].tolist()], 'T':[t,int(bw['T'])], 'accepted':[int(aw['accepted']),int(bw['accepted'])]}
   if not same:res['common_windows'].append(r);break
   al=a.layers[a.layers['window']==aw['number']];bl=b.layers[b.layers['window']==bw['number']]
   r['first_route_divergence']=None;r['first_path_divergence']=None;r['route_difference_entries']=0;r['path_difference_entries']=0
   for x,y in zip(al,bl):
    xe=a.entries[int(x['offset']):int(x['offset'])+int(x['tokens'])*10];ye=b.entries[int(y['offset']):int(y['offset'])+int(y['tokens'])*10]
    d=int(np.count_nonzero(xe['expert']!=ye['expert']));q=int(np.count_nonzero(xe['path']!=ye['path']))
    r['route_difference_entries']+=d;r['path_difference_entries']+=q
    if d and r['first_route_divergence'] is None:r['first_route_divergence']={'layer':int(x['layer']), 'old':xe['expert'].tolist(),'new':ye['expert'].tolist(),'old_paths':xe['path'].tolist(),'new_paths':ye['path'].tolist()}
    if q and r['first_path_divergence'] is None:r['first_path_divergence']={'layer':int(x['layer']), 'old':xe['path'].tolist(),'new':ye['path'].tolist()}
   res['common_windows'].append(r)
   if n>=15:break
  summary[p+'-request'+str(request)]=res
save(out/'summary.json',summary)
print(json.dumps(summary,indent=2))
