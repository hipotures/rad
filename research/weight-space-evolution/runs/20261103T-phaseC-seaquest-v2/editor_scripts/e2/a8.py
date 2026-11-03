import json,numpy as np
for k in (2,3):
  for fn in ['gold','candidate']:
    E=json.load(open('/work/pass_%d/%s_episodes.json'%(k,fn)))
    L=np.array([e['length'] for e in E]); S=np.array([e['score'] for e in E])
    print(k,fn,'frac len<150',np.mean(L<150),'len<60',np.mean(L<60),'mean score of those',S[L<150].mean(), 'hist len/150',np.bincount(np.minimum(L//150,20),minlength=21)[:21])
