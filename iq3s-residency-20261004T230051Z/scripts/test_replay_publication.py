"""Blocking completion must publish a finished batch despite floating-point cancellation."""
import random
import numpy as np
from replay import Replay
rng=random.Random(5);example=None
for _ in range(10000):
    base=rng.uniform(1,30);delay=rng.uniform(0,10);ready=base+delay+rng.uniform(0,1)
    reconstructed=base+(delay+max(0,ready-(base+delay)))
    if reconstructed<ready:example=(base,delay,ready);break
assert example is not None
base,delay,ready=example
r=Replay.__new__(Replay);r.delay=delay;r.wait=0.;r.gpu_ready=[ready,0.]
r.queues=[(ready,0)];r.state=np.array([[-1]],dtype=np.int32);r.birth=np.array([[0.]])
r.promotions=[{'layer':0,'incoming':0,'slot':0,'window':0,'published':None}]
now=r.wait_for_pending(base)
assert not r.queues and r.state[0,0]==0 and now>=ready
assert r.promotions[0]['published']==ready and r.wait>0
print('PASS: completed batch published, cancellation example',example)
