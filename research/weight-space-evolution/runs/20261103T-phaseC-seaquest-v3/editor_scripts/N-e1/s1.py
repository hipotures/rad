import numpy as np
np.set_printoptions(precision=2, suppress=True, linewidth=200)
W1,b1,W2,b2,W3,b3=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
print('b1',b1); print('b2',b2); print('b3',b3)
print('W3\n',W3.T)
W=W1.reshape(10,10,6,32)
for c in range(6):
    print('chan',c,'abs sum per unit', np.abs(W[:,:,c,:]).sum((0,1)))
for u in range(32):
    nz=[(c, np.abs(W[:,:,c,u]).sum()) for c in range(6)]
    print('unit',u,' '.join('c%d:%.1f'%x for x in nz), 'b1=%.2f'%b1[u])
print('W2 nonzero count', (np.abs(W2)>1e-6).sum())
print('W2\n',W2)
