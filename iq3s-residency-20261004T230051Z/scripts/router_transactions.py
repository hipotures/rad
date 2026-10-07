"""Conservative temporary within-window placement under measured slot and copy budgets.

This is a fixed observed trajectory feasibility model, not a latency/TG prediction.
The immutable baseline resident set is restored after each window. All true future
expert IDs are evaluation labels, never used for admission or victim selection.
"""
import os
for key in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[key]='1'
import argparse,json
import numpy as np
from lab import ROOT,load,save
from trace_reader import Trace
ap=argparse.ArgumentParser();ap.add_argument('analysis');ap.add_argument('--output',required=True);a=ap.parse_args()
analysis=load(a.analysis);assert analysis['state']=='PASS';t=Trace(analysis['prefix']);assert t.validate()['state']=='PASS'
# Replay actual state/heat at the first CPU observation of each GPU prediction.
observations={};groups={};windowmap={int(w['number']):w for w in t.windows}
for layer,entries in t.grouped():
 w,l=int(layer['window']),int(layer['layer']);observations[w,l]=int(layer['t0']);groups[w,l]=entries
points={}
for r in analysis['records']:points.setdefault((r['window'],r['current_layer']),[]).append(r)
events=[]
for p in t.promotions:
 events.append((int(p['issue']),0,'issue',p))
 if p['observed_ready']:events.append((int(p['observed_ready']),1,'publish',p))
for layer,entries in t.grouped():events.append((int(layer['t0']),2,'heat',(int(layer['layer']),entries['expert'])))
for w in t.windows:
 if (int(w['number'])+1)%4==0:events.append((int(w['end']),3,'decay',None))
events.sort(key=lambda x:(x[0],x[1]));events_index=0;state=t.initial.copy();heat=t.initial_usage.copy();snapshots=[]
for key,rows in sorted(points.items(),key=lambda item:item[1][0]['available_ns']):
 r=rows[0];now=r['available_ns']
 while events_index<len(events) and events[events_index][0]<=now:
  _,_,kind,p=events[events_index]
  if kind=='issue':state[int(p['layer']),int(p['outgoing'])]=-1
  elif kind=='publish':state[int(p['layer']),int(p['incoming'])]=int(p['slot'])
  elif kind=='heat':np.add.at(heat[p[0]],p[1],np.float32(1))
  else:heat*=np.float32(.7)
  events_index+=1
 current,target=r['current_layer'],r['target_layer'];gpu=int(current>=25)
 # Aggregate predicted demand counts and preserve native top10 ordering for ties.
 predicted={}
 for row in rows:
  for rank,expert in enumerate(row['predicted_IDs']):
   v=predicted.setdefault(expert,{'count':0,'first_rank':rank});v['count']+=1;v['first_rank']=min(v['first_rank'],rank)
 cold=[e for e in predicted if state[target,e]<0]
 cold.sort(key=lambda e:(-predicted[e]['count'],predicted[e]['first_rank'],e))
 low=0 if gpu==0 else 25
 victims=[(float(heat[l,e]),l,int(e),int(state[l,e])) for l in range(low,current) for e in np.flatnonzero(state[l]>=0)]
 victims.sort()
 truth=groups[r['window'],target]
 snapshots.append({'window':r['window'],'current':current,'target':target,'gpu':gpu,'now':now,'deadline':observations[r['window'],target],'end':int(windowmap[r['window']]['verify_end']),'next_start':int(t.windows[t.window_index[r['window']]+1]['begin']) if t.window_index[r['window']]+1<len(t.windows) else None,'cold':cold,'predicted':predicted,'heat':heat[target].copy(),'victims':victims,'true_nonlocal':truth[truth['path']!=0]['expert'].tolist(),'truth':truth['expert'].tolist(),'bytes':int(t.blob_bytes[target]),'cold_window':r['cold_window'],'GPUcost_us':r['GPU_score_top10_publish_us']})
results=[]
baseissues=sorted([(int(p['issue']),int(p['bytes'])) for p in t.promotions])
for policy in ['rank-first','heat-guarded']:
 for rate in [1.8,12.6]:
  timeline=[];reserved={};choices=[];noslot=0;noguard=0
  for s in snapshots:
   used=reserved.setdefault(s['window'],set());chosen=None
   for incoming in s['cold']:
    for cold_heat,l,victim,slot in s['victims']:
     if (s['gpu'],slot) in used or s['bytes']>int(t.slot_bytes[s['gpu']][slot]):continue
     if policy=='heat-guarded' and (s['heat'][incoming]<2 or s['heat'][incoming]-cold_heat<1.5):continue
     chosen={'window':s['window'],'current_layer':s['current'],'target_layer':s['target'],'gpu':s['gpu'],'incoming':incoming,'victim_layer':l,'victim':victim,'slot':slot,'bytes':s['bytes'],'victim_bytes':int(t.blob_bytes[l]),'issue':s['now'],'deadline':s['deadline'],'verify_end':s['end'],'next_start':s['next_start'],'useful_nonlocal_entries':s['true_nonlocal'].count(incoming),'actual_demand_entries':s['truth'].count(incoming),'cold_window':s['cold_window'],'GPU_score_us':s['GPUcost_us'],'incoming_causal_heat':float(s['heat'][incoming]),'victim_causal_heat':cold_heat}
     assert chosen['victim_bytes']<=int(t.slot_bytes[s['gpu']][slot]);break
    if chosen:break
   if not chosen:
    if s['cold']:
     if policy=='heat-guarded':noguard+=1
     else:noslot+=1
    continue
   used.add((s['gpu'],chosen['slot']));choices.append(chosen);i=len(choices)-1
   timeline.append((chosen['issue'],0,'candidate',i))
   timeline.append((chosen['verify_end'],2,'restore',i))
  end_capture=max(s['end'] for s in snapshots)
  for issue,bb in baseissues:
   if issue<=end_capture:timeline.append((issue,1,'baseline',bb))
  timeline.sort(key=lambda x:(x[0],x[1]));link=0;queue=0;restorewait={}
  for issue,_,kind,p in timeline:
   if kind=='baseline':bb=p
   elif kind=='candidate':bb=choices[p]['bytes']
   else:bb=choices[p]['victim_bytes'];issue=max(issue,choices[p]['copy_ready'])
   start=max(issue,link);finish=start+round(bb/(rate*1e9)*1e9)+4200;link=finish
   if kind=='candidate':
    choices[p]['copy_start']=start;choices[p]['copy_ready']=finish;choices[p]['ready_before_observed_dispatch']=finish<=choices[p]['deadline'];choices[p]['queue_wait_us']=(start-issue)/1000
   elif kind=='restore':
    choices[p]['restore_ready']=finish
    if choices[p]['next_start'] is not None:restorewait[choices[p]['window']]=max(restorewait.get(choices[p]['window'],0),max(0,finish-choices[p]['next_start']))
  warm=[c for c in choices if not c['cold_window']];useful=[c for c in warm if c['ready_before_observed_dispatch'] and c['useful_nonlocal_entries']>0]
  totalbad=sum(len(s['true_nonlocal']) for s in snapshots if not s['cold_window'])
  r={'policy':policy,'rate_GB_s':rate,'opportunity_points':len(snapshots),'admissions':len(choices),'warm_admissions':len(warm),'no_slot':noslot,'no_heat_guard_or_slot':noguard,'warm_true_nonlocal_entries':totalbad,'covered_nonlocal_entries_before_host_deadline':sum(c['useful_nonlocal_entries'] for c in useful),'warm_tail_coverage_pct':100*sum(c['useful_nonlocal_entries'] for c in useful)/totalbad if totalbad else None,'promotion_bytes':sum(c['bytes'] for c in choices),'restore_bytes':sum(c['victim_bytes'] for c in choices),'warm_useful_promotion_bytes':sum(c['bytes'] for c in useful),'warm_not_useful_in_target_bytes':sum(c['bytes'] for c in warm if not(c['ready_before_observed_dispatch'] and c['actual_demand_entries']>0)),'modeled_restore_wait_s':sum(restorewait.values())/1e9,'recorded_GPU_score_us_sum_selected':sum(c['GPU_score_us'] for c in choices),'choices':choices}
  results.append(r)
save(a.output,{'state':'COMPLETE_FEASIBILITY_MODEL','episode':analysis['episode'],'prefix':t.prefix,'results':results,'limitations':['Not a full counterfactual runtime simulation: observedtrajectory, baselinepromotionissues, hostdeadlines fixed. Delays do notfeedfuturegeneration.','CPUobserveddeadline isoptimistic forGPUready; restorewait model isnot additive with allCPU/GPUspans andisnot a TGprojection.','Temporary swaps restorebaselinecapacity/identityatboundaries andchargebothcopies; persistentpromotioncouldbehavedifferently.','Globalserializedrate1.8is a conservativecontendedscenario,12.6optimisticisolated; baselinecopypollingnotDMAcost.','SnapshotfullGPUpredictor onlyfirst64windows/fivepairs. TruefutureexpertIDs used only tolabel usefuladmissions.']})
print(analysis['episode'],json.dumps([{k:v for k,v in r.items() if k!='choices'} for r in results]))
