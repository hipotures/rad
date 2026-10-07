"""Bounded local scalar count scorers; whole-task train/calibration/holdout isolation."""
import os
for key in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[key]='1'
import argparse,hashlib,json,pathlib,time
import numpy as np
from lab import ROOT,save,deadline
from trace_reader import Trace
from predictor_features import frames,NAMES,BASIC,TEMPORAL

OUT=ROOT/'experiments/E005-expert-jev/v1'
class Scorer:
 def __init__(self,path):
  z=np.load(path);self.p={k:z[k] for k in z.files}
 def logits(self,x):
  p=self.p;z=(x[:,p['indices']]-p['mean'])/p['std']
  if 'W1' in p:return np.maximum(z@p['W1']+p['b1'],0)@p['W2']+p['b2']
  return z@p['coef']+p['intercept']
 def predict(self,x):
  p=np.expm1(np.clip(self.logits(x),0,np.log(17)))
  return np.maximum(0,p*float(self.p.get('cal_slope',1))+float(self.p.get('cal_intercept',0)))

def persist(path,parameters):
 if path.exists():raise RuntimeError('Refuse checkpoint overwrite')
 path.parent.mkdir(parents=True,exist_ok=True);np.savez(path,**parameters)

def train(kind,indices,X,y,weights,mean,std):
 rng=np.random.default_rng(20261005);z=((X[:,indices]-mean[indices])/std[indices]).astype(np.float32)
 params={'indices':np.asarray(indices,dtype=np.int32),'mean':mean[indices],'std':std[indices]};history=[]
 start=time.perf_counter()
 if kind=='linear':
  design=np.concatenate([z,np.ones((len(z),1),dtype=np.float32)],axis=1)
  xtx=design.T@(design*weights[:,None]);xty=design.T@(y*weights)
  beta=np.linalg.solve(xtx+np.eye(xtx.shape[0])*10,xty).astype(np.float32)
  params.update(coef=beta[:-1],intercept=beta[-1])
 else:
  width=16;params.update(W1=rng.normal(0,np.sqrt(2/len(indices)),(len(indices),width)).astype(np.float32),b1=np.zeros(width,dtype=np.float32),W2=rng.normal(0,.05,width).astype(np.float32),b2=np.asarray(float(np.average(y,weights=weights)),dtype=np.float32))
  keys=['W1','b1','W2','b2'];mom={k:np.zeros_like(params[k]) for k in keys};vel={k:np.zeros_like(params[k]) for k in keys}
  for step in range(1,601):
   if time.perf_counter()-start>120 or time.time()>deadline()-2700:raise RuntimeError('Bounded training time exhausted; preserve original attempt')
   ix=rng.integers(0,len(z),4096);xb=z[ix];yb=y[ix];wb=weights[ix];h=np.maximum(xb@params['W1']+params['b1'],0);pred=h@params['W2']+params['b2'];err=pred-yb;d=2*wb*err/wb.sum()
   hidden=d[:,None]*params['W2'][None,:];hidden[h<=0]=0
   grad={'W1':xb.T@hidden+1e-5*params['W1'],'b1':hidden.sum(axis=0),'W2':h.T@d+1e-5*params['W2'],'b2':np.asarray(d.sum(),dtype=np.float32)}
   for k in keys:
    assert np.all(np.isfinite(grad[k])),k
    mom[k]=.9*mom[k]+.1*grad[k];vel[k]=.999*vel[k]+.001*grad[k]**2
    params[k]-=.001*(mom[k]/(1-.9**step))/(np.sqrt(vel[k]/(1-.999**step))+1e-8)
   if step%50==0:history.append({'step':step,'batch_weighted_logcount_MSE':float(np.sum(wb*err**2)/wb.sum()),'wall_s':time.perf_counter()-start})
 params['seed']=np.asarray(20261005);return params,{'kind':kind,'feature_names':[NAMES[i] for i in indices],'training_wall_s':time.perf_counter()-start,'steps':1 if kind=='linear' else 600,'history':history,'parameter_bytes':sum(x.nbytes for x in params.values() if isinstance(x,np.ndarray)),'objective':'weighted squared log1p next4window count, no softmax/probability interpretation'}

def calibrate(model,trace):
 xx=xy=xsum=ysum=n=0.
 for i,x,y in frames(trace):
  pred=model.predict(x).astype(np.float64);y=y.astype(np.float64)
  xx+=float(pred@pred);xy+=float(pred@y);xsum+=float(pred.sum());ysum+=float(y.sum());n+=len(y)
 slope=(xy-xsum*ysum/n)/max(1e-12,xx-xsum*xsum/n)
 slope=max(0,slope);intercept=(ysum-slope*xsum)/n
 return slope,intercept,{'calibration_rows':int(n),'cal_slope':slope,'cal_intercept':intercept,'semantics':'affine expected-count least squares fitted only on calibration episode; clamped nonnegative; not probability calibration'}

def ranking_coverage(score,y,capacity):
 score=score.reshape(capacity.shape[0],-1);y=y.reshape(score.shape)
 hit=0
 for l,k in enumerate(capacity):
  ids=np.argsort(-score[l],kind='stable')[:int(k)];hit+=float(y[l,ids].sum())
 return hit/max(1,float(y.sum()))

def evaluate(models,manifest):
 results=[]
 for episode in manifest['episodes']:
  trace=Trace(episode['prefix']);cap=(trace.initial>=0).sum(axis=1);totals={name:{'MSE':0.,'MAE':0.,'rows':0,'coverage':[],'inference_s':0.,'frames':0} for name in models}
  cheap={name:[] for name in ['static','EMA','recency','recent4','frequency']};feature_time=0.;frame_count=0
  for i,x,y in frames(trace):
   frame_count+=1
   for name,model in models.items():
    start=time.perf_counter();pred=model.predict(x);elapsed=time.perf_counter()-start
    row=totals[name];row['inference_s']+=elapsed;row['MSE']+=float(np.sum((pred-y)**2));row['MAE']+=float(np.sum(np.abs(pred-y)));row['rows']+=len(y);row['coverage'].append(ranking_coverage(pred,y,cap));row['frames']+=1
   scores={'static':x[:,10],'EMA':x[:,0],'recency':-x[:,8],'recent4':x[:,4],'frequency':x[:,7]}
   for name,score in scores.items():
    if name=='static':cheap[name].append(float(y[trace.initial.ravel()>=0].sum())/max(1,float(y.sum())))
    else:cheap[name].append(ranking_coverage(score,y,cap))
  record={'episode':episode['name'],'role':episode['role'],'frame_count':frame_count,'label_horizon':4,'capacity_ranking_only':'cost-free resident-set selection proxy; finite-transfer replay required before runtime claim','cheap_baselines':{k:float(np.mean(v)) for k,v in cheap.items()}}
  record['models']={name:{'population_count_MSE':row['MSE']/row['rows'],'population_count_MAE':row['MAE']/row['rows'],'mean_future_demand_coverage_at_layer_capacity':float(np.mean(row['coverage'])),'numeric_inference_ms_per_full24576candidate_frame':1000*row['inference_s']/row['frames'],'rows':row['rows']} for name,row in totals.items()}
  results.append(record);save(OUT/'evaluation-progress.json',results)
 return results

if __name__=='__main__':
 manifest=json.loads((OUT/'dataset-manifest.json').read_text());data=np.load(manifest['development_file']);X=data['X'];y=data['y'];weights=data['weight'];w=weights.astype(np.float64);mean=np.average(X,axis=0,weights=w).astype(np.float32);std=np.sqrt(np.average((X-mean)**2,axis=0,weights=w)).astype(np.float32);std=np.maximum(std,.05)
 stats={};models={};checkpoints=OUT/'checkpoints'
 for name,kind,indices in [('linear','linear',BASIC),('mlp','mlp',BASIC),('temporal-mlp','mlp',TEMPORAL)]:
  params,record=train(kind,indices,X,y,weights,mean,std);raw=checkpoints/(name+'-uncalibrated.npz');persist(raw,params);model=Scorer(raw)
  calibration=next(e for e in manifest['episodes'] if e['role']=='calibration');slope,intercept,cal=calibrate(model,Trace(calibration['prefix']));params.update(cal_slope=np.asarray(slope,dtype=np.float32),cal_intercept=np.asarray(intercept,dtype=np.float32));path=checkpoints/(name+'.npz');persist(path,params)
  models[name]=Scorer(path);record.update(calibration=cal,checkpoint=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),total_checkpoint_bytes=path.stat().st_size);stats[name]=record
  save(OUT/'training.json',stats);print(name,'trained',round(record['training_wall_s'],2),'s',flush=True)
 results=evaluate(models,manifest);save(OUT/'evaluation.json',{'training':stats,'episodes':results,'limitations':['only two development tasks, one calibration, three holdouts; no universal generalization claim','ranking capacity proxy ignores transfers/admission/readiness; not TG','numeric scorer time excludes feature extraction/update/selection/CPU contention, which require runtime measurement','initial cache/history continues across independent tasks; all carried state is causal']});print(json.dumps(results,indent=2))
