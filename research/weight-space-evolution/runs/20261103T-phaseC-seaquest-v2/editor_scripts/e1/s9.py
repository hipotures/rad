import json,numpy as np
for p in ['pass_2','pass_3']:
  for fn in ['gold','candidate']:
    E=json.load(open('/work/%s/%s_episodes.json'%(p,fn)))
    L=np.array([e['length'] for e in E]); S=np.array([e['score'] for e in E])
    ac=np.array([e['action_counts'] for e in E]).sum(0)
    print(p,fn,'mean',S.mean(),'kps %.4f'%(S.sum()/L.sum()),'len pct',np.percentile(L,[10,25,50,75,90]).round(),'act',(ac/ac.sum()).round(3))
    for e in E:
        if 'trace' in e:
            t=e['trace']; dc=[s['diver_count'] for s in t]
            print('   ep score',e['score'],'len',len(t),'meandiv %.2f'%np.mean(dc),'death', t[-1])
