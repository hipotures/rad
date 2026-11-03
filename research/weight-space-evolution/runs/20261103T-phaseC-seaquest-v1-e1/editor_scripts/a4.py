import json,numpy as np
E=json.load(open('/work/pass_1/gold_episodes.json'))
sc=np.array([e['score'] for e in E]);ln=np.array([e['length'] for e in E])
print('score pct',np.percentile(sc,[0,10,25,50,75,90,100]),'len pct',np.percentile(ln,[0,10,25,50,75,90,100]))
print('score/len',sc.sum()/ln.sum())
ac=np.array([e['action_counts'] for e in E]).sum(0);print('actions',ac/ac.sum())
print('corr',np.corrcoef(sc,ln)[0,1])
for e in E:
    if 'trace' not in e or not e['trace']: continue
    T=e['trace'];print('--- seed',e['seed'],'score',e['score'],'len',e['length'])
    last=T[-6:]
    for t in last: print('  ',t)
    surf=[i for i,t in enumerate(T) if t['surface'] and i>0 and not T[i-1]['surface']]
    print('  surfacings at',surf)
    big=[(i,t['r']) for i,t in enumerate(T) if t['r']>1]; print('  bonus rewards',big)
    ys=np.bincount([t['sub_y'] for t in T],minlength=10);print('  row hist',ys)
    dcs=[t['diver_count'] for t in T]; print('  dc max',max(dcs),' dc at surfacings',[T[i-1]['diver_count'] for i in surf])
    print('  oxygen at surfacings',[T[i-1]['oxygen'] for i in surf])
    rw=np.cumsum([t['r'] for t in T]); print('  cum reward each 200',rw[::200])
