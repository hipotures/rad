import numpy as np
reset()
W2=gold('W2').copy(); b2=gold('b2').copy()
old=W2[25:32].copy(); W2[25:32]=old*2.0; b2=b2+old.sum(0)
old=W2[9:16].copy(); W2[9:16]=old*0.5; b2=b2-0.5*old.sum(0)
save('W2',W2); save('b2',b2)
print(saved(), int((W2!=gold('W2')).sum()), int((b2!=gold('b2')).sum()))
