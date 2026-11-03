import numpy as np
W1,b1,W2,b2,W3,b3=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
for j in range(32):
    nz=np.nonzero(W2[:,j])[0]
    print('h2_%d b=%.2f :'%(j,b2[j]), ' '.join('h1_%d:%.2f'%(i,W2[i,j]) for i in nz))
W=W1.reshape(10,10,6,32)
for u in [16,25,26]:
    print(u, 'danger rows nonzero', [(r,list(np.round(W[r,:,1,u],1))) for r in range(10) if np.abs(W[r,:,1,u]).sum()>0])
print('other channels anywhere?', [(c, np.abs(W[:,:,c,:]).sum()) for c in range(6)])
