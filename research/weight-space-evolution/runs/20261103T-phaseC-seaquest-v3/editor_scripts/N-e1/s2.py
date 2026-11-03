import numpy as np
np.set_printoptions(precision=2, suppress=True, linewidth=250)
W1,b1,W2,b2,W3,b3=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
W=W1.reshape(10,10,6,32)
for u in [0,1,8,9,10,15,16,17,23,24,25,26,31]:
    for c in range(6):
        m=W[:,:,c,u]
        if np.abs(m).sum()>0:
            print('unit',u,'chan',c); print(m)
np.set_printoptions(precision=2, suppress=True, linewidth=250, threshold=100000)
for i in range(32):
    nz=np.nonzero(np.abs(W2[i])>1e-9)[0]
    print('h1',i,'->', ' '.join('%d:%.2f'%(j,W2[i,j]) for j in nz))
