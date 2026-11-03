P=gp(); R=run(P,200,seed0=0,tlimit=100); summ('gold',R)
import numpy as np
print(np.sort(R['score'])[::10])
