"""Freeze development-only sampled numeric data and reconstructible episode splits."""
import hashlib,json,pathlib,time
import numpy as np
from lab import ROOT,save
from trace_reader import Trace
from predictor_features import frames,NAMES,BASIC,TEMPORAL
out=ROOT/'experiments/E005-expert-jev/v1';data=out/'data';data.mkdir(parents=True,exist_ok=True)
if (data/'development.npz').exists():raise RuntimeError('Refuse overwrite of dataset')
episodes=['dev-code','dev-math','cal-prose','hold-code','hold-structured','hold-math'];manifest=[];xs=[];ys=[];weights=[];seed=20261005
for n,name in enumerate(episodes,2):
 prefix=ROOT/'experiments/E003-diagnostics/v5-portfix/episodes/traces'/f'runtime-request{n}'
 trace=Trace(prefix);assert trace.validate()['state']=='PASS'
 role='development' if n<4 else 'calibration' if n==4 else 'holdout'
 entry={'name':name,'role':role,'prefix':str(prefix),'window_count':len(trace.windows),'output_tokens':len(trace.output_ids),'trace_output_ids_sha256':hashlib.sha256(trace.output_ids.tobytes()).hexdigest(),'feature_frames':0,'sampled_rows':0,'initial_state_source':'observed causal request start; sequential independent episodes retain previous cache history'}
 if role=='development':
  rng=np.random.default_rng(seed+n)
  for i,x,y in frames(trace):
   positive=np.flatnonzero(y>0);negative=np.flatnonzero(y==0)
   picked=rng.choice(negative,size=min(4096,len(negative)),replace=False)
   indices=np.concatenate([positive,picked]);w=np.ones(len(indices),dtype=np.float32);w[len(positive):]=len(negative)/max(1,len(picked))
   xs.append(x[indices]);ys.append(np.log1p(y[indices]));weights.append(w)
   entry['feature_frames']+=1;entry['sampled_rows']+=len(indices)
   save(data/f'{name}-frame{i:04d}.json',{'window_index':i,'row_indices':indices.tolist(),'population_rows':len(y),'future_positive_rows':len(positive),'negative_sampling_weight':float(w[-1]) if len(picked) else None,'target':'next4window routed-entry count, log1p','feature_availability':'after current verify only'})
 manifest.append(entry)
np.savez_compressed(data/'development.npz',X=np.concatenate(xs),y=np.concatenate(ys),weight=np.concatenate(weights))
save(out/'dataset-manifest.json',{'seed':seed,'feature_names':NAMES,'basic_feature_indices':BASIC,'temporal_feature_indices':TEMPORAL,'horizon_windows':4,'episodes':manifest,'sample_policy':'all future positive candidates plus4096uniform negative rows/frame; inverse inclusion weights for negatives','preprocessing':'development only; no calibration/holdout fit','development_file':str(data/'development.npz'),'development_sha256':hashlib.sha256((data/'development.npz').read_bytes()).hexdigest()})
print(json.dumps({'dataset':str(data/'development.npz'),'rows':int(sum(x['sampled_rows'] for x in manifest)),'bytes':(data/'development.npz').stat().st_size,'episodes':manifest},indent=2))
