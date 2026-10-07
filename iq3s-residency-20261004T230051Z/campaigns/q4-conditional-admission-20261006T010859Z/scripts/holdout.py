"""Single sealed task-level evaluation. No threshold/model selection here."""
from pathlib import Path
import numpy as np,hashlib,json,time,datetime
from campaign import C,load,save,status
from data import episode
from train import predict,sigmoid,rule,metrics,aggregate,classification
def run():
 assert not (C/'phase-b/holdout-decision.json').exists(),'No holdout retuning/re-evaluation'
 decision=load(C/'phase-b/frozen-decision.json');assert hashlib.sha256((C/'checkpoints/conditional-logistic.json').read_bytes()).hexdigest()==decision['checkpoint_sha256']
 model=load(C/'checkpoints/conditional-logistic.json');hist=load(C/'checkpoints/history-only-ablation.json');victim=load(C/'checkpoints/victim-hazard-linear.json');episodes=[];all_y=[];all_p=[];all_h=[];all_v=[];all_vp=[];policy_rows={name:[] for name in ('rule-permissive','rule-balanced','rule-conservative','linear-permissive','linear-balanced','linear-conservative')}
 for task in load(C/'datasets/splits.json')['holdout']:
  print('HOLDOUT_ONCE_FROZEN',task,decision['chosen_policy'],flush=True)
  x,y,b,v,m,e,meta=episode(task);p=predict(model,x);platt=model['platt'];p=sigmoid(platt[0]+platt[1]*np.log(np.maximum(p,1e-8)/np.maximum(1-p,1e-8)));h=predict(hist['model'],x[:,hist['features']]);a=np.array(victim['active']);z=(x[:,a]-np.array(victim['mean'])[a])/np.array(victim['std'])[a];vp=np.expm1(np.clip(np.c_[np.ones(len(z)),z]@np.array(victim['beta']),0,np.log(65)))
  all_y.extend(y[m]);all_p.extend(p[m]);all_h.extend(h[m]);all_v.extend(v[m]);all_vp.extend(vp[m])
  results=[]
  for name in policy_rows:
   if name.startswith('rule'):keep=rule(x,name.split('-')[1])
   else:keep=(p>=decision['thresholds'][name.split('-')[1]])&(x[:,32]<=x[:,8]+np.log(3))&(x[:,39]>0)&(x[:,21]==0)&(x[:,22]>0)
   r=metrics(name,meta['prefix'],e,keep,x,y,m);results.append(r);policy_rows[name].append(r)
  selected=next(r for r in results if r['policy']==decision['chosen_policy']);baseline_nonlocal=selected['original_nonlocal_entries'];selected['episode_practical_gate']=selected['unpublished_reduction']>=.5 and min(selected['useful_next4_benefit_recall'],selected['observed_use_recall'])>=.8 and selected['nonlocal_ratio']<=1.02 and selected['victim_ratio']<=1.02
  save(C/'phase-b/holdout'/f'{task}.json',{'task':task,'family':meta['task'].split('-')[0],'selected':selected,'frozen_curve':results,'classification':classification(y,p,m),'victim_hazard':{'mean_label':float(v[m].mean()),'mean_prediction':float(vp[m].mean()),'MAE':float(np.abs(v[m]-vp[m]).mean())},'no_selection_from_this_result':True});episodes.append({'task':task,'selected':selected})
 aggregates=[]
 for name,rs in policy_rows.items():
  agg=aggregate(rs);agg.update(policy=name,unpublished_reduction=1-agg['unpublished_GB']/agg['baseline_unpublished_GB'],benefit_recall=agg['useful_next4_benefit_retained']/agg['baseline_next4_benefit'],observed_use_recall=agg['useful_later_observed_uses_retained']/agg['baseline_observed_uses'],nonlocal_ratio=agg['nonlocal_entries_attributed']/agg['original_nonlocal_entries'],victim_ratio=agg['victim_absent_entries_retained']/max(1,agg['baseline_victim_absent_entries']));aggregates.append(agg)
 selected=next(a for a in aggregates if a['policy']==decision['chosen_policy']);global_gate=selected['unpublished_reduction']>=.5 and min(selected['benefit_recall'],selected['observed_use_recall'])>=.8 and selected['nonlocal_ratio']<=1.02 and selected['victim_ratio']<=1.02
 # A pooled aggregate cannot hide a large family loss. This requirement frozen
 # before the evaluation: require each represented family retains>=.70 benefit,
 # nonlocal<=+2%, and at least half byte reduction, or no live qualification.
 family=[]
 for key in ('code','math','structured'):
  rs=[ep['selected'] for ep in episodes if ep['task'].startswith(key+'-')];a=aggregate(rs);a.update(family=key,benefit_recall=a['useful_next4_benefit_retained']/max(1,a['baseline_next4_benefit']),observed_use_recall=a['useful_later_observed_uses_retained']/max(1,a['baseline_observed_uses']),nonlocal_ratio=a['nonlocal_entries_attributed']/max(1,a['original_nonlocal_entries']),unpublished_reduction=1-a['unpublished_GB']/max(1e-9,a['baseline_unpublished_GB']));family.append(a)
 ay=np.asarray(all_y);ap=np.asarray(all_p);ah=np.asarray(all_h);av=np.asarray(all_v);avp=np.asarray(all_vp)
 result={'evaluated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_policy':decision['chosen_policy'],'pooled_transactional_gate':global_gate,'calibration_gate':decision['chosen_calibration']['qualifies_calibration'],'qualifies_live':bool(global_gate and decision['chosen_calibration']['qualifies_calibration'] and all(min(a['benefit_recall'],a['observed_use_recall'])>=.7 and a['nonlocal_ratio']<=1.02 and a['unpublished_reduction']>=.5 for a in family)),'selected':selected,'family':family,'episodes':episodes,'frozen_precision_traffic_curve':aggregates,'classification':classification(ay,ap),'history_only_ablation':classification(ay,ah),'victim_hazard':{'n':len(av),'positive_fraction':float((av>0).mean()),'MAE':float(np.abs(av-avp).mean()),'R2':float(1-np.sum((av-avp)**2)/np.sum((av-av.mean())**2)),'PR_AUC_nonzero_damage':classification(av>0,np.clip(avp/64,0,1))['PR_AUC_average_precision']},'rules':['No feature/scaler/model/threshold changes after this decision','Failed heldout preserved, not retuned','Attribution/sensitivity are not measured hypothetical TG','Live conditional build allowed only if qualifies_live=true']}
 save(C/'phase-b/holdout-decision.json',result);status('OFFLINE_GATE_PASSED' if result['qualifies_live'] else 'OFFLINE_GATE_FAILED',phase='B',running=None,next_exact_action='integrate frozen gate and safety tests' if result['qualifies_live'] else 'write negative evidence, retain control launchers, audit/cleanup; no full live matrix')
 print('HELDOUT_GATE',result['qualifies_live'],json.dumps(selected),flush=True)
if __name__=='__main__':run()
