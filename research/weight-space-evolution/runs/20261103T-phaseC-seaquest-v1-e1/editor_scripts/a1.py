import numpy as np
W1=gold('W1');b1=gold('b1');W2=gold('W2');b2=gold('b2')
for j in range(32):
    nz=np.nonzero(W1[:,j])[0]
    items=[]
    for i in nz:
        cell,ch=divmod(i,6);r,c=divmod(cell,10)
        items.append(f"r{r}c{c}ch{ch}:{W1[i,j]:g}")
    print(f"H1[{j}] b={b1[j]:g} n={len(nz)}: "+" ".join(items))
print()
for k in range(32):
    nz=np.nonzero(W2[:,k])[0]
    print(f"H2[{k}] b={b2[k]:g}: "+" ".join(f"{i}:{W2[i,k]:g}" for i in nz))
