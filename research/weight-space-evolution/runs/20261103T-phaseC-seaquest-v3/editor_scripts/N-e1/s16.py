import numpy as np
W2=load('W2').copy(); W2[24,9]=gold('W2')[24,9]+3.0; save('W2',W2)
print('W2 changed',(W2!=gold('W2')).sum(),'b2',(load('b2')!=gold('b2')).sum(),'b3',(load('b3')!=gold('b3')).sum(), W2[24,9])
