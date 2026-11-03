import numpy as np
np.set_printoptions(precision=2, suppress=True, linewidth=200)
W1,b1,W2,b2,W3,b3=[gold(n) for n in ["W1","b1","W2","b2","W3","b3"]]
W=W1.reshape(10,10,6,32)
for j in [0,1,8,9,10,15,16,17,23,24,25,26,31]:
    for c in range(6):
        idx=np.argwhere(np.abs(W[:,:,c,j])>0.01)
        if len(idx): print(j,c,[(int(r),int(cc),round(float(W[r,cc,c,j]),2)) for r,cc in idx])
print("W2 nonzero")
for k in range(26):
    idx=np.nonzero(np.abs(W2[:,k])>0.01)[0]
    print(k, [(int(i),round(float(W2[i,k]),2)) for i in idx])
