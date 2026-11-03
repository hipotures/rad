import json,numpy as np
E=json.load(open('/work/pass_1/gold_episodes.json'))
ln=np.array([e['length'] for e in E]);sc=np.array([e['score'] for e in E])
h,b=np.histogram(ln,bins=[0,50,100,150,190,215,300,400,600,1000,1500,2000,2500,3100]);print(list(zip(b[:-1],h)))
m=(ln>=195)&(ln<=215);print('len~200 count',m.sum(),'scores',sc[m])
print(sorted(ln)[:40])
