"""Required Q4 Expert-Jev-inspired branch; independent numeric candidate scoring.

Not the published Jev checkpoint/backbone. CPU-only ridge and32-unit MLP,
shared causal state, horizon4 multilabel counts. Dev/calibration/holdout tasks
are disjoint; censored endpoints never become negative training labels.
"""
import os
for name in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[name]='1'
from pathlib import Path
import hashlib, json, time
import numpy as np
from campaign import C, load, save, guard, status
from trace_reader import Trace
from q4_features import frames, NAMES, BASIC, TEMPORAL
OUT=C/'phase-b/learned'
class Scorer:
    def __init__(self,path):
        z=np.load(path);self.p={name:z[name] for name in z.files}
    def logits(self,x):
        p=self.p;z=(x[:,p['indices']]-p['mean'])/p['std']
        return np.maximum(z@p['W1']+p['b1'],0)@p['W2']+p['b2'] if 'W1' in p else z@p['coef']+p['intercept']
    def predict(self,x):
        p=self.p;y=np.expm1(np.clip(self.logits(x),0,np.log(33)))
        return np.maximum(0,y*float(p.get('cal_slope',1))+float(p.get('cal_intercept',0)))
def persist(path,values):
    assert not path.exists();path.parent.mkdir(parents=True,exist_ok=True);np.savez(path,**values)
def build_dataset():
    splits=load(C/'datasets/splits.json');manifest=[];xs=[];ys=[];ys16=[];episodes=[]
    rng=np.random.default_rng(20261005)
    for role in ['development','calibration','holdout']:
        for name in splits[role]:
            result=C/'traces/diagnostic/32k'/name/'results.json';r=load(result);t=Trace(r['trace_prefix'])
            assert t.validate()['state']=='PASS';row={'name':name,'role':role,'prefix':t.prefix,
                'payload':r['runs'][0]['payload'],'output_tokens':len(t.output_ids),'windows':len(t.windows),
                'right_censored_last_windows':4,'label':'next4 complete windows count over all routed MTP branches'}
            manifest.append(row)
            if role=='development':
                xx=[];yy=[];yy16=[];counts=t.counts()
                for i,x,y in frames(t):
                    # Uniform candidates preserve natural zero/nonzero density.
                    pick=rng.choice(len(x),4096,replace=False);xx.append(x[pick]);yy.append(y[pick])
                    future16=counts[i+1:i+17].sum(0).ravel()/4 if i+16<len(counts) else np.full(len(x),np.nan)
                    yy16.append(future16[pick])
                x=np.concatenate(xx);y=np.concatenate(yy);xs.append(x);ys.append(y);ys16.append(np.concatenate(yy16));episodes.extend([name]*len(y))
    X=np.concatenate(xs);y=np.concatenate(ys)
    y16=np.concatenate(ys16)
    file=C/'datasets/q4-development.npz';assert not file.exists();np.savez_compressed(file,X=X,y=y,y16=y16)
    save(C/'datasets/manifest.json',{'episodes':manifest,'development_file':str(file),'rows':len(y),
        'feature_names':NAMES,'seed':20261005,'positive_fraction':float(np.mean(y>0)),
        'dataset_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
        'normalization':'development only; calibration affine counts; holdout never fits anything',
        'coverage':'Six independent short tasks with1024 output, not long-document or language generalization'})
    return manifest,X,y,y16
def train(kind,indices,X,y,mean,std):
    z=((X[:,indices]-mean[indices])/std[indices]).astype(np.float32);target=np.log1p(y)
    p={'indices':np.array(indices,np.int32),'mean':mean[indices],'std':std[indices],
       'seed':np.array(20261005),'horizon':np.array(4)};start=time.perf_counter();curve=[]
    if kind=='linear':
        design=np.concatenate([z,np.ones((len(z),1),np.float32)],axis=1)
        beta=np.linalg.solve(design.T@design+np.eye(design.shape[1])*10,design.T@target).astype(np.float32)
        p.update(coef=beta[:-1],intercept=beta[-1]);curve=[{'step':1,'population_logcount_MSE':float(np.mean((design@beta-target)**2))}]
    else:
        rng=np.random.default_rng(20261005);width=32
        p.update(W1=rng.normal(0,np.sqrt(2/len(indices)),(len(indices),width)).astype(np.float32),
                 b1=np.zeros(width,np.float32),W2=rng.normal(0,.05,width).astype(np.float32),b2=np.array(target.mean(),np.float32))
        keys=['W1','b1','W2','b2'];mom={k:np.zeros_like(p[k]) for k in keys};vel={k:np.zeros_like(p[k]) for k in keys}
        for step in range(1,1001):
            guard();assert time.perf_counter()-start<180,'Bounded training timeout'
            ix=rng.integers(0,len(z),4096);xb=z[ix];yb=target[ix]
            h=np.maximum(xb@p['W1']+p['b1'],0);err=h@p['W2']+p['b2']-yb;d=2*err/len(ix)
            back=d[:,None]*p['W2'];back[h<=0]=0
            grads={'W1':xb.T@back+1e-5*p['W1'],'b1':back.sum(0),'W2':h.T@d+1e-5*p['W2'],'b2':np.array(d.sum(),np.float32)}
            for k,g in grads.items():
                assert np.isfinite(g).all();mom[k]=.9*mom[k]+.1*g;vel[k]=.999*vel[k]+.001*g*g
                p[k]-=.001*(mom[k]/(1-.9**step))/(np.sqrt(vel[k]/(1-.999**step))+1e-8)
            if step%100==0:curve.append({'step':step,'batch_logcount_MSE':float(np.mean(err**2)),'wall_s':time.perf_counter()-start})
    return p,{'kind':kind,'feature_names':[NAMES[i] for i in indices],'learning_curve':curve,
              'training_wall_s':time.perf_counter()-start,'objective':'natural-population squared log1p count; affine calibrated count output',
              'width':0 if kind=='linear' else 32,'CPU_only':True}
def calibrate(model,t):
    xx=xy=xsum=ysum=n=0.
    horizon=int(model.p['horizon'])
    for i,x,y in frames(t,horizon):
        y=y*(4/horizon)
        p=model.predict(x).astype(np.float64);y=y.astype(np.float64)
        xx+=float(p@p);xy+=float(p@y);xsum+=float(p.sum());ysum+=float(y.sum());n+=len(y)
    slope=max(0,(xy-xsum*ysum/n)/max(1e-12,xx-xsum*xsum/n));intercept=(ysum-slope*xsum)/n
    return slope,intercept,int(n)
def evaluate(manifest,models):
    results=[]
    for row in manifest:
        t=Trace(row['prefix']);cap=(t.initial>=0).sum(1);stat={name:{'squared_error':0,'abs_error':0,'rows':0,'coverage':[],'inference_s':0,'frames':0} for name in models}
        feature_s=0
        counts=t.counts()
        for i,x,y in frames(t):
            for name,model in models.items():
                horizon=int(model.p['horizon'])
                if i+horizon>=len(counts):continue
                target=counts[i+1:i+horizon+1].sum(0).ravel()*(4/horizon)
                start=time.perf_counter();p=model.predict(x);r=stat[name];r['inference_s']+=time.perf_counter()-start
                r['squared_error']+=float(np.sum((p-target)**2));r['abs_error']+=float(np.sum(abs(p-target)));r['rows']+=len(target);r['frames']+=1
                pp=p.reshape(t.initial.shape);yy=target.reshape(pp.shape);hit=0
                for l,k in enumerate(cap):hit+=float(yy[l,np.argsort(-pp[l],kind='stable')[:k]].sum())
                r['coverage'].append(hit/max(1,float(target.sum())))
        results.append({'episode':row['name'],'role':row['role'],'models':{name:{
            'target_horizon':int(models[name].p['horizon']),
            'count_MSE':r['squared_error']/r['rows'],'count_MAE':r['abs_error']/r['rows'],
            'cost_free_demand_coverage_at_layer_capacity':float(np.mean(r['coverage'])),
            'CPU_inference_ms_per24576_candidates':1000*r['inference_s']/r['frames'],'frames':r['frames']}
            for name,r in stat.items()},'feature_extraction_cost':'measured separately in causal replay/live; not free'})
        save(OUT/'evaluation-progress.json',results)
    return results
def main():
    assert (C/'phase-a/report.md').exists(),'Finish Phase A before Phase B'
    assert not OUT.exists(),'Do not overwrite a trained/evaluated branch'
    OUT.mkdir();manifest,X,y,y16=build_dataset();mean=X.mean(0);std=np.maximum(X.std(0),.05)
    models={};stats={}
    for name,kind,indices in [('linear','linear',BASIC),('mlp','mlp',BASIC),('temporal-mlp','mlp',TEMPORAL)]:
        target=y16 if name=='temporal-mlp' else y;mask=np.isfinite(target)
        p,r=train(kind,indices,X[mask],target[mask],mean,std)
        p['horizon']=np.array(16 if name=='temporal-mlp' else 4)
        r['target_horizon']=int(p['horizon']);r['target_normalization']='future count multiplied by4/horizon; same four-window units'
        raw=C/'checkpoints'/f'{name}-uncalibrated.npz';persist(raw,p)
        calibration=next(row for row in manifest if row['role']=='calibration');a,b,n=calibrate(Scorer(raw),Trace(calibration['prefix']))
        p.update(cal_slope=np.array(a,np.float32),cal_intercept=np.array(b,np.float32));path=C/'checkpoints'/f'{name}.npz';persist(path,p)
        models[name]=Scorer(path);r.update(calibration={'slope':a,'intercept':b,'rows':n},checkpoint=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        stats[name]=r;save(OUT/'training.json',stats);print('TRAINED',name,r['training_wall_s'],flush=True)
    save(OUT/'evaluation.json',evaluate(manifest,models))
    print('LEARNED_COMPLETE',flush=True)
if __name__=='__main__':main()
