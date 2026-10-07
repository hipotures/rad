"""Development-only fit, calibration-only three operating points, freeze before holdout."""
import numpy as np,json,time,datetime,hashlib
from pathlib import Path
from campaign import C,load,save
from data import episode,NAMES
from transaction_filter import replay
def sigmoid(z):return 1/(1+np.exp(-np.clip(z,-40,40)))
def fit(X,y,weights=None,penalty=1.):
 X=np.c_[np.ones(len(X)),X];weights=np.ones(len(y)) if weights is None else weights;beta=np.zeros(X.shape[1]);reg=np.diag([1e-6]+[penalty]*(X.shape[1]-1));history=[]
 for n in range(60):
  p=sigmoid(X@beta);grad=X.T@(weights*(p-y))+reg@beta;curv=weights*np.maximum(p*(1-p),1e-8);h=X.T@(X*curv[:,None])+reg;step=np.linalg.solve(h,grad);beta-=np.clip(step,-2,2);history.append(float(np.linalg.norm(step)))
  if np.max(np.abs(step))<1e-7:break
 return beta,history
def classifier(X,y):
 mean=X.mean(axis=0);std=X.std(axis=0);std=np.maximum(std,1e-5);active=X.std(axis=0)>1e-5
 beta,curve=fit((X[:,active]-mean[active])/std[active],y)
 return {'mean':mean.tolist(),'std':std.tolist(),'active':np.where(active)[0].tolist(),'beta':beta.tolist(),'iterations':curve,'fit_penalty':1.,'kind':'logistic-conditional-publication'}
def predict(model,X):
 a=np.array(model['active']);Z=(X[:,a]-np.array(model['mean'])[a])/np.array(model['std'])[a];return sigmoid(np.c_[np.ones(len(X)),Z]@np.array(model['beta']))
def classification(y,p,mask=None):
 if mask is not None:y,p=y[mask],p[mask]
 order=np.argsort(-p,kind='stable');yy=y[order];tp=np.cumsum(yy);fp=np.cumsum(~yy);precision=tp/np.maximum(1,tp+fp);recall=tp/max(1,int(y.sum()));ap=float(np.sum(precision*yy)/max(1,int(y.sum())))
 bins=[]
 for lo,hi in zip(np.linspace(0,1,11)[:-1],np.linspace(0,1,11)[1:]):
  m=(p>=lo)&(p<=hi if hi==1 else p<hi);bins.append({'lo':float(lo),'hi':float(hi),'n':int(m.sum()),'predicted':float(p[m].mean()) if m.any() else None,'observed':float(y[m].mean()) if m.any() else None})
 return {'n':len(y),'positives':int(y.sum()),'positive_fraction':float(y.mean()),'PR_AUC_average_precision':ap,'Brier':float(np.mean((p-y)**2)),'calibration_bins':bins,'precision_recall_curve':{'precision':precision[::max(1,len(precision)//250)].tolist(),'recall':recall[::max(1,len(recall)//250)].tolist()}}
def rule(X,level):
 # Three factor-separated gates; causal repeat failures + minimum reuse proxy,
 # conservative victim hysteresis. Deadline guard remains scheduler-owned.
 share={'permissive':.015,'balanced':.03,'conservative':.06}[level]
 recent=np.expm1(X[:,9]);wrong=np.expm1(X[:,45]);good_recent=np.expm1(X[:,7])
 return (X[:,1]>=share)&~((wrong>=3)&(recent==0)&(X[:,1]<.08))&~((X[:,47]>0)&(good_recent==0)&(X[:,1]<share*2))&(X[:,32]<=X[:,8]+np.log(3))&(X[:,39]>0)&(X[:,21]==0)&(X[:,22]>0)&(X[:,25]==1)
def metrics(name,prefix,e,keep,X,y,valid):
 end=max(x['window'] for x in e)-3;r=replay(prefix,e,keep,evaluation_windows=end);r['policy']=name;r['unpublished_reduction']=1-r['unpublished_GB']/max(1e-9,r['baseline_unpublished_GB']);r['nonlocal_ratio']=r['nonlocal_entries_attributed']/r['original_nonlocal_entries'];r['CPU_ratio']=r['CPU_entries_attributed']/r['original_CPU_entries'];r['victim_ratio']=r['victim_absent_entries_retained']/max(1,r['baseline_victim_absent_entries'])
 k=keep[valid];yv=y[valid];tp=int((k&yv).sum());fp=int((k&~yv).sum());fn=int((~k&yv).sum());tn=int((~k&~yv).sum());r['confusion_matrix']={'TP':tp,'FP':fp,'FN':fn,'TN':tn};r['precision']=tp/max(1,tp+fp);r['recall']=tp/max(1,tp+fn)
 r['observed_use_recall']=r['useful_later_observed_uses_retained']/max(1,r['baseline_observed_uses']);return r
def aggregate(results):
 fields=['issued_copies','staged_GB','target_ready_publications','unpublished_GB','useful_next4_benefit_retained','victim_absent_entries_retained','baseline_victim_absent_entries','original_nonlocal_entries','nonlocal_entries_attributed','original_CPU_entries','CPU_entries_attributed','original_mapped_entries','mapped_entries_attributed','useful_later_observed_uses_retained','conservative_lost_observed_use_upper','baseline_unpublished_GB','baseline_next4_benefit','baseline_observed_uses']
 a={f:sum(r[f] for r in results) for f in fields};a['episode_count']=len(results);return a
def main():
 assert not (C/'phase-b/frozen-decision.json').exists(),'Do not retune after freezing'
 splits=load(C/'datasets/splits.json');assert len(splits['development'])==4 and len(splits['calibration'])==2
 dev=[episode(n) for n in splits['development']];cal=[episode(n) for n in splits['calibration']]
 print('FIT_DEVELOPMENT_ONLY',splits['development'],flush=True);X=np.concatenate([x[m] for x,y,b,v,m,e,meta in dev]);y=np.concatenate([y[m] for x,y,b,v,m,e,meta in dev]);t=time.perf_counter();model=classifier(X,y)
 # Same causal feature set, history/state/victim only: H4 evidence ablation,
 # not a separate broad policy search.
 historical=[i for i in range(48) if i not in range(7)];history=classifier(X[:,historical],y)
 model['training_wall_ms']=(time.perf_counter()-t)*1000
 # Platt calibration, ONLY complete labels in two cal tasks.
 cx=np.concatenate([x[m] for x,y,b,v,m,e,meta in cal]);cy=np.concatenate([y[m] for x,y,b,v,m,e,meta in cal]);raw=predict(model,cx);logits=np.log(np.maximum(raw,1e-8)/np.maximum(1-raw,1e-8));platt,curve=fit(logits[:,None],cy,penalty=1.)
 model['platt']=platt.tolist();model['platt_fit_episodes']=splits['calibration'];model['development_episodes']=splits['development'];model['calibration_iterations']=curve
 save(C/'checkpoints/conditional-logistic.json',model);save(C/'checkpoints/history-only-ablation.json',{'features':historical,'model':history})
 # Victim hazard: one regularized log-count head, development only. This is
 # auxiliary harm estimation, not a generic admission/future model competition.
 vv=np.concatenate([v[m] for x,y,b,v,m,e,meta in dev]);z=(X-np.array(model['mean']))/np.array(model['std']);active=np.array(model['active']);z=np.c_[np.ones(len(z)),z[:,active]];reg=np.diag([1e-6]+[5.]*(z.shape[1]-1));coef=np.linalg.solve(z.T@z+reg,z.T@np.log1p(vv));victim={'beta':coef.tolist(),'active':active.tolist(),'mean':model['mean'],'std':model['std'],'target':'prospective victim next4 demand log1p; right-censored excluded','fit_penalty':5.};save(C/'checkpoints/victim-hazard-linear.json',victim)
 # Victim recent-use hard protection and modeled staging/resource feasibility
 # included in both rule and logistic arms. Numeric utility values reported,
 # not falsely equated to additive request latency.
 points=[];byname={}
 for name in ['rule-permissive','rule-balanced','rule-conservative','linear-permissive','linear-balanced','linear-conservative']:
  print('CALIBRATION_OPERATING_POINT',name,flush=True);rs=[];probs=[];ys=[]
  for x,yy,b,v,m,e,meta in cal:
   p=predict(model,x);p=sigmoid(platt[0]+platt[1]*np.log(np.maximum(p,1e-8)/np.maximum(1-p,1e-8)))
   if name.startswith('rule'):keep=rule(x,name.split('-')[1])
   else:
    threshold={'permissive':.05,'balanced':.12,'conservative':.25}[name.split('-')[1]]
    keep=(p>=threshold)&(x[:,32]<=x[:,8]+np.log(3))&(x[:,39]>0)&(x[:,21]==0)&(x[:,22]>0)
   r=metrics(name,meta['prefix'],e,keep,x,yy,m);rs.append(r);probs.extend(p[m]);ys.extend(yy[m])
  a=aggregate(rs);base=a['baseline_unpublished_GB'];full=a['baseline_next4_benefit'];uses=a['baseline_observed_uses']
  a.update(policy=name,unpublished_reduction=1-a['unpublished_GB']/base,benefit_recall=a['useful_next4_benefit_retained']/max(1,full),observed_use_recall=a['useful_later_observed_uses_retained']/max(1,uses),nonlocal_ratio=a['nonlocal_entries_attributed']/a['original_nonlocal_entries'],victim_ratio=a['victim_absent_entries_retained']/max(1,a['baseline_victim_absent_entries']))
  a['qualifies_calibration']=a['unpublished_reduction']>=.5 and min(a['benefit_recall'],a['observed_use_recall'])>=.8 and a['nonlocal_ratio']<=1.02 and a['victim_ratio']<=1.02
  points.append(a);byname[name]=rs;save(C/'phase-b/calibration'/f'{name}.json',{'aggregate':a,'episodes':rs})
 candidates=[a for a in points if a['qualifies_calibration']]
 if candidates:chosen=max(candidates,key=lambda a:a['unpublished_reduction'])
 else:
  # Predeclared no-retuning fallback: closest constrained tradeoff atcal only.
  chosen=max(points,key=lambda a:min(a['benefit_recall'],a['observed_use_recall'],.8)+min(a['unpublished_reduction'],.5)-max(0,a['nonlocal_ratio']-1.02)*10)
 calibration={'raw':classification(cy,raw),'calibrated':classification(cy,sigmoid(platt[0]+platt[1]*logits)),'history_only':classification(cy,predict(history,cx[:,historical])),'points':points,'scorer_CPU_ns_per_action':None}
 t=time.perf_counter()
 for _ in range(100):predict(model,cx)
 calibration['batched_scorer_CPU_ns_per_action']=(time.perf_counter()-t)*1e9/(100*len(cx));save(C/'phase-b/calibration.json',calibration)
 decision={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'chosen_policy':chosen['policy'],'chosen_calibration':chosen,'checkpoint_sha256':hashlib.sha256((C/'checkpoints/conditional-logistic.json').read_bytes()).hexdigest(),'holdout_not_read_by_fit_selection':True,'thresholds':{'permissive':.05,'balanced':.12,'conservative':.25},'rule_thresholds':{'permissive':.015,'balanced':.03,'conservative':.06},'gate':{'unpublished_reduction':.5,'benefit_recall':.8,'observed_use_recall':.8,'max_nonlocal_ratio':1.02,'max_victim_ratio':1.02},'nonlinear':'Not automatic; only ifcal shows useful signal insufficient tradeoff and independent data justify it. No model changes after holdout.'}
 save(C/'phase-b/frozen-decision.json',decision);print('FROZEN_BEFORE_HOLDOUT',json.dumps(decision),flush=True)
if __name__=='__main__':main()
