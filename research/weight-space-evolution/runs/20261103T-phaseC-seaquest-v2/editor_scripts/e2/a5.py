import json,numpy as np
E=json.load(open('/work/pass_1/gold_episodes.json'))
sc=np.array([e['score'] for e in E]); L=np.array([e['length'] for e in E])
print('score pct',np.percentile(sc,[0,10,25,50,75,90,100]),'len pct',np.percentile(L,[0,10,25,50,75,90,100]))
print('corr score/len',np.corrcoef(sc,L)[0,1], 'score per step', sc.sum()/L.sum())
ac=np.array([e['action_counts'] for e in E]).sum(0); print('actions',ac/ac.sum())
for e in E:
    if 'trace' not in e: continue
    T=e['trace']; print('--- ep score',e['score'],'len',e['length'])
    last=T[-4:]
    for t in last: print(t)
    # surfacing events
    surf=[(i,t['r'],t['diver_count'],T[i-1]['oxygen']) for i,t in enumerate(T) if t['surface'] and i>0 and not T[i-1]['surface']]
    print('surfacings (step,r,divers after,ox before):',surf[:40], 'n',len(surf))
    big=[(i,t['r']) for i,t in enumerate(T) if t['r']>1]; print('big rewards',big)
    ys=np.array([t['sub_y'] for t in T]); print('row hist',np.bincount(ys,minlength=10))
    dc=np.array([t['diver_count'] for t in T]); print('divercount hist',np.bincount(dc+1,minlength=8))
    ox=np.array([t['oxygen'] for t in T]); print('min oxygen',ox.min())
