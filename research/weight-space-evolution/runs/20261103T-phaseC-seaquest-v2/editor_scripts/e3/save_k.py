import numpy as np
reset()
W2=gold('W2').copy(); b2=gold('b2').copy(); W1=gold('W1').copy()
old=W2[25:32].copy(); W2[25:32]=old*2.0; b2=b2+old.sum(0)
for j in range(9,16): W1[(9*10+8)*6+5,j]=-4.0
save('W1',W1); save('W2',W2); save('b2',b2)
print(saved(), int((W1!=gold('W1')).sum()), int((W2!=gold('W2')).sum()), int((b2!=gold('b2')).sum()))
