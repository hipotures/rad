import subprocess,pickle,numpy as np,time
from common import *
from features import History
no_gpu();rng=np.random.default_rng(20261006);results=[]
for name in ['logistic','tree']:
 d=np.load(C/'data/math-rational.npz');idx=np.sort(rng.choice(len(d['X']),1000,replace=False));X=d['X'][idx]
 with (C/'models'/(name+'.pkl')).open('rb') as f:model=pickle.load(f)
 python=np.maximum.accumulate(np.column_stack([m.predict_proba(model['scaler'].transform(X))[:,1] for m in model['heads']]),axis=1)
 data=''.join('0 0 0 '+' '.join(map(str,x))+'\n' for x in X);t=time.monotonic();p=subprocess.run([str(C/'builds/scorer-fixture'),str(C/'models'/(name+'.txt'))],input=data,text=True,capture_output=True,check=True,timeout=30);cpp=np.array([[float(v) for v in line.split()] for line in p.stdout.splitlines()]);error=float(np.max(np.abs(python-cpp)));assert error<2e-5,(name,error);results.append({'name':name,'predictions':len(X)*4,'max_abs_error':error,'fixture_wall_s':time.monotonic()-t})
# Compare actual prefix extraction across 300 completed simultaneous batches, including gap/EMA decay.
h=History();lines=[];expected=[]
for ev in range(300):
 l=ev%48;ids=rng.integers(0,30,size=10*(1+ev%4));e=int(rng.integers(0,30));h.observe(l,ids,ev);expected.append(h.features(l,[e],ev+1)[0]);lines.append(f'{l} {len(ids)} {ev} '+' '.join(map(str,ids))+f' {e}\n')
p=subprocess.run([str(C/'builds/history-fixture')],input=''.join(lines),text=True,capture_output=True,check=True,timeout=30);got=np.array([[float(v) for v in line.split()] for line in p.stdout.splitlines()]);error=float(np.max(np.abs(got-np.array(expected))));assert error<2e-6,error
save(C/'tests/scorer-parity.json',{'state':'PASS','models':results,'history_batches':300,'history_max_abs_error':error});print('SCORER PARITY PASS',results,error,flush=True)
