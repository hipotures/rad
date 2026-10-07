"""Two bounded multi-horizon candidates, fit only development; calibration selects operating point."""
import argparse,pickle,hashlib,time,os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='2'
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss
from sklearn.preprocessing import StandardScaler
from common import *
from features import NAMES,HORIZONS

def metrics(y,p,w):
 return {'n':len(y),'positive_fraction':float(np.average(y,weights=w)),'brier':float(brier_score_loss(y,p,sample_weight=w)),'log_loss':float(log_loss(y,p,sample_weight=w,labels=[0,1])),'auc':float(roc_auc_score(y,p,sample_weight=w)) if len(np.unique(y))==2 else None,'average_precision':float(average_precision_score(y,p,sample_weight=w)),'bins':[{'low':float(lo),'high':float(lo+.1),'n':int(np.count_nonzero((p>=lo)&(p<lo+.1))),'prediction':float(np.average(p[(p>=lo)&(p<lo+.1)],weights=w[(p>=lo)&(p<lo+.1)])),'observed':float(np.average(y[(p>=lo)&(p<lo+.1)],weights=w[(p>=lo)&(p<lo+.1)]))} for lo in np.arange(0,1,.1) if np.any((p>=lo)&(p<lo+.1))]}
def export(model,name):
 record={'name':name,'features':NAMES,'horizons':HORIZONS.tolist(),'scaler_mean':model['scaler'].mean_.tolist(),'scaler_scale':model['scaler'].scale_.tolist(),'heads':[]}
 for m in model['heads']:
  if name=='logistic':head={'type':'linear','bias':float(m.intercept_[0]),'coefficients':m.coef_[0].tolist()}
  else:
   head={'type':'boosted_tree','bias':float(m._raw_predict_init(np.zeros((1,len(NAMES))))[0,0]),'learning_rate':m.learning_rate,'trees':[]}
   for est in m.estimators_[:,0]:
    t=est.tree_;head['trees'].append({'left':t.children_left.tolist(),'right':t.children_right.tolist(),'feature':t.feature.tolist(),'threshold':t.threshold.tolist(),'value':t.value[:,0,0].tolist()})
  record['heads'].append(head)
 save(C/'models'/(name+'.json'),record)
def main():
 q=argparse.ArgumentParser();q.add_argument('--evaluate-reserved',action='store_true');args=q.parse_args();no_gpu();tasks=load(P0/'benchmark-manifest.json')['tasks'];train=[np.load(C/'data'/(t['task_id']+'.npz')) for t in tasks if t['split']=='development'];X=np.concatenate([x['X'] for x in train]);Y=np.concatenate([x['Y'] for x in train]);M=np.concatenate([x['M'] for x in train]);weight=np.concatenate([x['weight'] for x in train]);scaler=StandardScaler().fit(X);XX=scaler.transform(X);rng=np.random.default_rng(20261006)
 if not args.evaluate_reserved:
  ledger('Candidate budget frozen: multi-horizon logistic C=1 and GBDT32 depth3; no MLP; uniform candidate decision weights; horizons1/4/16/64 windows. Scope all four families. Reserved results excluded from selection.')
  for name in ['logistic','tree']:
   start=time.monotonic();model={'scaler':scaler,'heads':[]}
   for hi,h in enumerate(HORIZONS):
    valid=np.flatnonzero(M[:,hi]);sel=valid if name=='logistic' else np.sort(rng.choice(valid,min(len(valid),100000),replace=False));weights=weight[sel]*8
    m=LogisticRegression(C=1,max_iter=100,solver='lbfgs') if name=='logistic' else GradientBoostingClassifier(n_estimators=32,max_depth=3,learning_rate=.1,min_samples_leaf=100,subsample=.7,random_state=20261006)
    with Heartbeat(name+' horizon '+str(h),2):m.fit(XX[sel],Y[sel,hi],sample_weight=weights)
    model['heads'].append(m);progress(2,name+' fit H'+str(h)+' complete',model=name,horizon=int(h),fit_s=time.monotonic()-start)
   with (C/'models'/(name+'.pkl')).open('wb') as f:pickle.dump(model,f)
   export(model,name)
 rows=[]
 for name in ['logistic','tree']:
  with (C/'models'/(name+'.pkl')).open('rb') as f:model=pickle.load(f)
  for task in tasks:
   if task['split']=='reserved_evaluation' and not args.evaluate_reserved:continue
   if args.evaluate_reserved and task['split']!='reserved_evaluation':continue
   d=np.load(C/'data'/(task['task_id']+'.npz'));x=model['scaler'].transform(d['X']);pred=np.column_stack([m.predict_proba(x)[:,1] for m in model['heads']]);pred=np.maximum.accumulate(pred,axis=1);np.save(C/'results'/(task['task_id']+'-'+name+'-predictions.npy'),pred.astype(np.float32))
   for hi,h in enumerate(HORIZONS):
    mask=d['M'][:,hi].astype(bool);r=metrics(d['Y'][mask,hi],pred[mask,hi],d['weight'][mask]);r.update(task=task['task_id'],family=task['family'],split=task['split'],model=name,horizon=int(h),censored=int(np.count_nonzero(~mask)));rows.append(r)
   # Within sampled decision sets, compare selected victim true short/long return against a random candidate.
   group=d['meta'][:,0];unique,begin=np.unique(group,return_index=True);risk=pred@np.array([1,.5,.25,.125]);chosen=[];uniform=[]
   for s,e in zip(begin,np.r_[begin[1:],len(group)]):
    chosen.append(d['meta'][s+np.argmin(risk[s:e]),5]);uniform.extend(d['meta'][s:e,5])
   progress(2,'Prediction evaluation '+task['task_id']+' '+name,model=name,task=task['task_id'],sampled_selected_return_le4=float(np.mean(np.array(chosen)<=4)),uniform_return_le4=float(np.mean(np.array(uniform)<=4)))
 save(C/'results'/('reserved-prediction-metrics.json' if args.evaluate_reserved else 'development-calibration-prediction-metrics.json'),rows)
 save(C/'models/identities.json',{str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in (C/'models').glob('*') if p.is_file() and p.name!='identities.json'})
if __name__=='__main__':
 with Heartbeat('fit and prediction evaluation',2):main()
