import json,os,numpy as np,collections
print(os.listdir('/work/pass_2'))
for fn in sorted(os.listdir('/work/pass_2')):
    if not fn.endswith('episodes.json'): continue
    E=json.load(open('/work/pass_2/'+fn))
    L=np.array([e['length'] for e in E]); S=np.array([e['score'] for e in E])
    print(fn,'mean',S.mean(),'len pct',np.percentile(L,[10,25,50,75,90,99,100]),'kps',S.sum()/L.sum())
    for e in E:
        if 'trace' not in e: continue
        t=e['trace']
        surf=[(i,t[i-1]['diver_count'],t[i-1]['oxygen']) for i,s in enumerate(t) if s['sub_y']==0 and i>0 and t[i-1]['sub_y']>0]
        # kills per cycle
        rs=np.array([s['r'] for s in t]); cum=np.cumsum(rs)
        bounds=[0]+[s[0] for s in surf]+[len(t)]
        kc=[int((rs[a:b]==1).sum()) for a,b in zip(bounds[:-1],bounds[1:])]
        print(' ep',e['seed'],'score',e['score'],'len',len(t),'nsurf',len(surf),'kills/cycle',kc)
        print('  last 8',[(s['a'],s['sub_y'],s['oxygen'],s['diver_count']) for s in t[-8:]])
