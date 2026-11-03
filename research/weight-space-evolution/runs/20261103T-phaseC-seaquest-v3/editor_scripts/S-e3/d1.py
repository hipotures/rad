import time
W=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
for n,w in zip(['W1','b1','W2','b2','W3','b3'],W): print(n,w.shape,float(np.abs(w).max()), int((w!=0).sum()))
print('b3',np.round(W[5],2))
print('W3\n',np.round(W[4],2))
print('b1',np.round(W[1],2)); print('b2',np.round(W[3],2))
t=time.time(); res=run(W,60,seed0=0); print('time',time.time()-t)
summarize(res,'gold')
