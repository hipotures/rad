import numpy as np
np.set_printoptions(linewidth=250,suppress=True,precision=2)
W1,b1,W2,b2,W3,b3=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
print('W3.T'); print(W3.T)
print('W2 nonzero per col'); 
for j in range(32):
    nz=np.nonzero(W2[:,j])[0]; print(j, b2[j], [(int(i),round(float(W2[i,j]),2)) for i in nz])
for j in range(32):
    w=W1[:,j].reshape(10,10,6); nz=np.argwhere(w!=0)
    chans=sorted(set(nz[:,2].tolist()))
    print('h1',j,'b1',b1[j],'nnz',len(nz),'chans',chans)
    for c in chans:
        m=w[:,:,c]
        print('  ch',c); print(m)
