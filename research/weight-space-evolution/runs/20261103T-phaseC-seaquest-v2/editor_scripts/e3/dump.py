import numpy as np
np.set_printoptions(linewidth=200, precision=3, suppress=True)
W1=gold('W1');b1=gold('b1');W2=gold('W2');b2=gold('b2')
ch=['P','D','R','B','T','G']
for j in range(32):
    nz=np.nonzero(W1[:,j])[0]
    items=[]
    for i in nz:
        cell=i//6; c=i%6; r=cell//10; col=cell%10
        items.append(f"{ch[c]}({r},{col})={W1[i,j]:g}")
    print(f"h1[{j}] b={b1[j]:g}: "+" ".join(items))
print("W2 nonzero:")
for k in range(32):
    nz=np.nonzero(W2[:,k])[0]
    print(f"h2[{k}] b={b2[k]:g}: "+" ".join(f"h1[{i}]={W2[i,k]:g}" for i in nz))
