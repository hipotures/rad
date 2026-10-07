import sys,pickle,subprocess,time
import numpy as np
from common import *
sys.path.insert(0,str(P1/'scripts'));from features import History
no_gpu();rng=np.random.default_rng(20261006);d=np.load(P1/'data/math-rational.npz');idx=np.sort(rng.choice(len(d['X']),1000,replace=False));X=d['X'][idx]
with (P1/'models/logistic.pkl').open('rb') as f:model=pickle.load(f)
expected=np.maximum.accumulate(np.column_stack([m.predict_proba(model['scaler'].transform(X))[:,1] for m in model['heads']]),axis=1)
data=''.join('0 0 0 '+' '.join(map(str,x))+'\n' for x in X);p=subprocess.run([str(W/'builds/scorer-fixture'),str(C/'models/logistic.txt')],input=data,text=True,capture_output=True,check=True,timeout=30);actual=np.array([[float(v) for v in line.split()] for line in p.stdout.splitlines()]);error=float(np.max(np.abs(expected-actual)));assert error<2e-5
h=History();lines=[];ex=[]
for ev in range(300):
 l=ev%48;ids=rng.integers(0,30,size=10*(1+ev%4));e=int(rng.integers(0,30));h.observe(l,ids,ev);ex.append(h.features(l,[e],ev+1)[0]);lines.append(f'{l} {len(ids)} {ev} '+' '.join(map(str,ids))+f' {e}\n')
p=subprocess.run([str(W/'builds/history-fixture')],input=''.join(lines),text=True,capture_output=True,check=True,timeout=30);got=np.array([[float(v) for v in line.split()] for line in p.stdout.splitlines()]);he=float(np.max(np.abs(got-np.array(ex))));assert he<2e-6
save(C/'tests/scorer-parity.json',{'state':'PASS','frozen_logistic_predictions':4000,'model_max_abs_error':error,'prefix_batches':300,'history_max_abs_error':he,'source_prefix_implementation':'Unchanged Phase1'});print('SCORER_PARITY_PASS',error,he)
