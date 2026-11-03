import json,numpy as np, collections
E=json.load(open('/work/pass_1/gold_episodes.json'))
ac=np.array([e['action_counts'] for e in E]).sum(0); print('actions',ac/ac.sum())
sc=np.array([e['score'] for e in E]); L=np.array([e['length'] for e in E])
print('score pct',np.percentile(sc,[0,10,25,50,75,90,100]),'len pct',np.percentile(L,[0,10,50,90,100]))
for e in E:
    if 'trace' not in e: continue
    t=e['trace']; print('EP seed',e['seed'],'score',e['score'],'len',len(t))
    ys=collections.Counter(s['sub_y'] for s in t); print(' y dist',sorted(ys.items()))
    xs=collections.Counter(s['sub_x'] for s in t); print(' x dist',sorted(xs.items()))
    # surfaces events
    surf=[(i,s['diver_count'],s['oxygen'],s['r']) for i,s in enumerate(t) if s['sub_y']==0 and i>0 and t[i-1]['sub_y']>0]
    print(' surfaces',surf[:40], len(surf))
    big=[(i,s['r']) for i,s in enumerate(t) if s['r']>1]; print(' bonus',big)
    print(' last 12',[(s['a'],s['sub_x'],s['sub_y'],s['oxygen'],s['diver_count'],s['r']) for s in t[-12:]])
    # min oxygen before each surface; diver count over time
    dc=[s['diver_count'] for s in t]; print(' max divers',max(dc), 'mean divers',np.mean(dc))
