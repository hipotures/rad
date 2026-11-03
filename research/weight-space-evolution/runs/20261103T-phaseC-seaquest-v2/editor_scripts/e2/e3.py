import numpy as np
reset()
W1=gold('W1').copy()
i2=(9*10+2)*6+5; i1=(9*10+0)*6+5
print(W1[i2,24],W1[i1,24])
W1[i1,24]=W1[i2,24]; W1[i2,24]=0.0
save('W1',W1)
P=[load(n) for n in ['W1','b1','W2','b2','W3','b3']]
for ox in [40,21,20,19,10]:
    print(ox,[act(st(sub=(5,r),ox=ox),P)[0] for r in range(9)])
