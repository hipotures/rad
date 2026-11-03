import numpy as np
np.set_printoptions(precision=1, suppress=True, linewidth=220)
W1,b1,W2,b2,W3,b3=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
W=W1.reshape(10,10,6,32)
for u in [0,4,8,9,12,15,16,19,23,24,25,28,31]:
    for c in range(6):
        if np.abs(W[:,:,c,u]).sum()>0:
            print('unit',u,'chan',c);print(W[:,:,c,u])
print('W2 (rows=h1 unit, cols=h2 unit)')
nz=np.nonzero(np.abs(W2).sum(0))[0]
print('nonzero h2 cols',nz)
print(W2)
