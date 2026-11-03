import numpy as np
np.set_printoptions(precision=2, suppress=True, linewidth=200)
W1,b1,W2,b2,W3,b3=[gold(n) for n in ["W1","b1","W2","b2","W3","b3"]]
print("b3",b3)
print("W3\n",W3.T)
print("b2",b2); print("b1",b1)
# per hidden unit: summarize W1 by channel/row/col: top weights
G=W1.reshape(10,10,6,32)
for j in range(32):
    s=[]
    for c in range(6):
        g=G[:,:,c,j]
        if np.abs(g).max()>0.05: s.append(f"c{c}:max{g.max():.2f}@{np.unravel_index(g.argmax(),g.shape)} min{g.min():.2f}@{np.unravel_index(g.argmin(),g.shape)} mean{g.mean():.2f}")
    print(j, "b1=%.2f"%b1[j], "; ".join(s))
print("W2 nonzero frac", (np.abs(W2)>1e-3).mean())
print(W2)
def fwd(x):
    h1=np.tanh(x@W1+b1); h2=np.tanh(h1@W2+b2); return h1,h2,h2@W3+b3
x=np.zeros(600)
h1,h2,l=fwd(x); print("empty logits",l)
