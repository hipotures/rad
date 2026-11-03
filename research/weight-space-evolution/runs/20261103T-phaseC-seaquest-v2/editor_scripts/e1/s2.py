import numpy as np
W1=gold('W1')
W=W1.reshape(10,10,6,32)
for j in list(range(0,10))+[16,17,24,25,26,31]:
    for c in range(6):
        m=W[:,:,c,j]
        idx=np.argwhere(np.abs(m)>1e-6)
        if len(idx): print(j,'ch',c,[(int(r),int(cc),round(float(m[r,cc]),2)) for r,cc in idx])
