import numpy as np
t0=np.tanh(-3.0)
W2=load('W2').astype(np.float64); b2=load('b2').astype(np.float64)
assert W2[16,9]==-3.0  # edit 1 present
gatep=[(16+k+1,8+k) for k in range(0,7)]+[(16+k-1,16+k) for k in range(1,8)]
for i,j in gatep:
    assert W2[i,j]==0; W2[i,j]=3.0; b2[j]-=3.0*t0
save('W2',W2.astype(gold('W2').dtype)); save('b2',b2.astype(gold('b2').dtype)); print(saved())
d=load('W2')-gold('W2'); print('W2 changed',int((d!=0).sum())); print('b2 changed',int((load('b2')!=gold('b2')).sum()))
