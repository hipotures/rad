import numpy as np
W1=gold('W1');W2=gold('W2')
for j in range(32):
    nz=np.nonzero(W1[:,j])[0]
    items=[]
    for i in nz:
        cell,ch=divmod(i,6); r,c=divmod(cell,10); items.append(f"r{r}c{c}ch{ch}:{W1[i,j]:g}")
    print('h1',j,len(nz),' '.join(items[:40]), '...' if len(items)>40 else '')
for j in range(32):
    nz=np.nonzero(W2[:,j])[0]
    print('h2',j,' '.join(f"{i}:{W2[i,j]:g}" for i in nz))
