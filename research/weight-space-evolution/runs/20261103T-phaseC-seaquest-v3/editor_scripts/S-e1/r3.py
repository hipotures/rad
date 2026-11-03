import numpy as np
np.set_printoptions(linewidth=250,suppress=True,precision=2)
W1=gold('W1'); b1=gold('b1')
for j in range(9,32):
    w=W1[:,j].reshape(10,10,6); nz=np.argwhere(w!=0)
    print('h1',j,'b1',b1[j],'nnz',len(nz), [(int(r),int(c),int(ch),round(float(w[r,c,ch]),2)) for r,c,ch in nz] if j>=16 else [(int(r),int(ch)) for r,c,ch in nz[:3]])
