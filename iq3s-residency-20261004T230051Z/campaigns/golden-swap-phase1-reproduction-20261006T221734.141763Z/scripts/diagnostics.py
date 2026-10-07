"""Bounded learning-curve and feature diagnostics; no candidate/checkpoint changes."""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='2'
import pickle,time,numpy as np
from sklearn.metrics import brier_score_loss
from sklearn.linear_model import LogisticRegression
from common import *
from features import NAMES
no_gpu();tasks=load(P0/'benchmark-manifest.json')['tasks'];dev=[np.load(C/'data'/(t['task_id']+'.npz')) for t in tasks if t['split']=='development'];X=np.concatenate([d['X'] for d in dev]);Y=np.concatenate([d['Y'] for d in dev]);M=np.concatenate([d['M'] for d in dev]);weights=np.concatenate([d['weight'] for d in dev]);curves=[];importance=[]
with Heartbeat('bounded learning curves, frozen weights unchanged',2):
 for name in ['logistic','tree']:
  with (C/'models'/(name+'.pkl')).open('rb') as f:m=pickle.load(f)
  h=m['heads'][1];valid=np.flatnonzero(M[:,1]);subset=valid[::4]
  partial=LogisticRegression(C=1,max_iter=100,solver='lbfgs').fit(m['scaler'].transform(X[subset]),Y[subset,1],sample_weight=weights[subset]*8) if name=='logistic' else None
  for task in [t for t in tasks if t['split']=='calibration']:
   d=np.load(C/'data'/(task['task_id']+'.npz'));mask=d['M'][:,1].astype(bool);xx=m['scaler'].transform(d['X'][mask]);yy=d['Y'][mask,1];ww=d['weight'][mask]
   if name=='logistic':
    for fraction,head in [(.25,partial),(1.,h)]:curves.append({'model':name,'task':task['task_id'],'fit_fraction':fraction,'horizon':4,'brier':float(brier_score_loss(yy,head.predict_proba(xx)[:,1],sample_weight=ww))})
   else:
    for i,p in enumerate(h.staged_predict_proba(xx),1):
     if i in [8,16,32]:curves.append({'model':name,'task':task['task_id'],'trees':i,'horizon':4,'brier':float(brier_score_loss(yy,p[:,1],sample_weight=ww))})
  values=h.coef_[0] if name=='logistic' else h.feature_importances_;importance.append({'model':name,'horizon':4,'features':dict(zip(NAMES,map(float,values)))})
save(C/'results/learning-curves.json',curves);save(C/'results/feature-diagnostics.json',importance);print('LEARNING CURVES COMPLETE; no model/threshold changes',flush=True)
