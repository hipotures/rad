import numpy as np
np.set_printoptions(precision=2, suppress=True, linewidth=200)
W1,b1,W2,b2,W3,b3=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
print('b3',b3)
print('W3.T');print(W3.T)
print('b2',b2)
print('b1',b1)
# W1 per unit: summarize by channel: sum of abs weight per channel, and top rows
W=W1.reshape(10,10,6,32)
for u in range(32):
    s=[np.abs(W[:,:,c,u]).sum() for c in range(6)]
    print('u%d'%u,'chan absum',np.round(s,1),'b1=%.2f'%b1[u])
