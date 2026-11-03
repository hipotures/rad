import numpy as np
t0=np.tanh(-3.0); w=-3.0
W2=gold('W2').copy(); b2=gold('b2').copy()
pairs=[(16+k-1,8+k) for k in range(1,7)]+[(17+k,16+k) for k in range(0,7)]
for i,j in pairs:
    assert abs(W2[i,j]+0.3)<1e-6
    W2[i,j]=w; b2[j]-=(w+0.3)*t0
reset(); save('W2',W2.astype(gold('W2').dtype)); save('b2',b2.astype(gold('b2').dtype)); print(saved())
