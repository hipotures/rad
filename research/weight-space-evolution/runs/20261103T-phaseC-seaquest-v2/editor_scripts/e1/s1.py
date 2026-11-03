import numpy as np
np.set_printoptions(precision=2, suppress=True, linewidth=200)
W1=gold('W1');b1=gold('b1');W2=gold('W2');b2=gold('b2');W3=gold('W3');b3=gold('b3')
print('b3',b3)
print('W3.T');print(W3.T)
print('b2',b2)
print('b1',b1)
W=W1.reshape(10,10,6,32)
for j in range(32):
    nz=[]
    for c in range(6):
        m=W[:,:,c,j]
        if np.abs(m).max()>1e-6:
            nz.append((c,np.round(m.min(),2),np.round(m.max(),2),int((np.abs(m)>1e-6).sum())))
    print('h1',j,'b',round(float(b1[j]),2),nz)
print('W2 nonzero per h2 unit')
for k in range(32):
    idx=np.where(np.abs(W2[:,k])>1e-6)[0]
    print('h2',k,'b',round(float(b2[k]),2),[(int(i),round(float(W2[i,k]),2)) for i in idx], 'W3', W3[k])
