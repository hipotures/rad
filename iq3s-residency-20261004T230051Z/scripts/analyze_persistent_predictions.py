"""Analyze real router signal versus current and subsequent demands; no timing forecast."""
from lab import ROOT,save
from trace_reader import Trace
from persistent_replay import PRED
import numpy as np
base=ROOT/'experiments/E028-persistent-replay';rows=[]
for profile in ['32k','128k']:
 t=Trace(base/f'signal-v1/{profile}/traces/runtime-request2');counts=t.counts();records=np.fromfile(t.prefix+'-gpu-router-predictions.bin',PRED);ids=np.fromfile(t.prefix+'-gpu-router-values.bin','<i4');weights=np.fromfile(t.prefix+'-gpu-router-confidence.bin','<f4');state=t.initial.copy();events=[]
 for a in t.promotions:
  events.extend([(int(a['issue']),0,a),(int(a['observed_ready']),1,a)] if a['observed_ready'] else [(int(a['issue']),0,a)])
 events.sort(key=lambda x:(x[0],x[1]));at=0;total=hits=future=miss_predictions=already_missed=0
 for p in records:
  now=int(p['available_ns']);l=int(p['target_layer']);i=t.window_index[int(p['window'])];off=int(p['offset']);v=ids[off:off+int(p['tokens']*p['k'])].reshape(int(p['tokens']),10);w=weights[off:off+v.size].reshape(v.shape)
  assert np.isfinite(w).all() and np.all(w>=0) and np.allclose(w.sum(axis=1),1,atol=1e-4) and all(len(set(row))==10 for row in v)
  while at<len(events) and events[at][0]<=now:
   _,kind,a=events[at];state[int(a['layer']),int(a['incoming'])]=int(a['slot']) if kind else state[int(a['layer']),int(a['incoming'])]
   if not kind:state[int(a['layer']),int(a['outgoing'])]=-1
   at+=1
  for e in v.ravel():
   total+=1;actual=counts[i,l,e]>0;hits+=actual;future+=np.any(counts[i+1:min(len(counts),i+17),l,e]>0);nonlocal_=state[l,e]<0;miss_predictions+=nonlocal_;already_missed+=nonlocal_ and actual
 rows.append({'profile':profile,'prediction_entries':total,'current_window_any_branch_membership_pct':100*hits/total,'subsequent16window_membership_pct':100*future/total,'predicted_nonlocal_entries':int(miss_predictions),'current_window_nonlocal_prediction_hits_already_executed_by_safe_admission_boundary':int(already_missed),'confidence_sums_unique_finite':'PASS','scope':'Any-token/branch membership, not tokenwise calibration or deployed early-hit count.'})
save(base/'prediction-analysis.json',{'state':'PASS','rows':rows});print(rows)
