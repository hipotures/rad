import numpy as np
np.set_printoptions(precision=2, suppress=True, linewidth=200)
W1,b1,W2,b2,W3,b3=[gold(n) for n in ["W1","b1","W2","b2","W3","b3"]]
print("b3",b3); print("W3\n",W3.T)
print("b1",b1); print("b2",b2)
W=W1.reshape(10,10,6,32)
for j in range(32):
    s=[]
    for c in range(6):
        m=W[:,:,c,j]
        if np.abs(m).max()>0.05:
            s.append(f"c{c}: max{m.max():.2f} min{m.min():.2f} nnz{(np.abs(m)>0.05).sum()}")
    print(j, "; ".join(s))
print("W2 abs>0.05 per col", (np.abs(W2)>0.05).sum(0))
