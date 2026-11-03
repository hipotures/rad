import numpy as np
np.set_printoptions(precision=2, suppress=True, linewidth=250)
W1,b1,W2,b2,W3,b3=[gold(n) for n in ["W1","b1","W2","b2","W3","b3"]]
G=W1.reshape(10,10,6,32)
for j in [0,4,9,16,24,25]:
    for c in range(6):
        g=G[:,:,c,j]
        if np.abs(g).max()>1e-3: print("unit",j,"ch",c); print(g)
print("W2 rows (h1 idx) -> nonzero cols")
for i in range(32):
    nz=np.nonzero(np.abs(W2[i])>1e-3)[0]
    print(i, [(int(k),round(float(W2[i,k]),2)) for k in nz])
