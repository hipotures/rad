import json,numpy as np
for p in (3,):
  for f in ('gold','candidate'):
    try: E=json.load(open(f'/work/pass_{p}/{f}_episodes.json'))
    except Exception: continue
    xs=sorted((e['length'],int(e['score'])) for e in E if 100<=e['length']<=230)
    print(p,f,xs)
for f in ('gold','candidate'):
    E=json.load(open(f'/work/pass_3/{f}_episodes.json'))
    ln=np.array([e['length'] for e in E]);sc=np.array([e['score'] for e in E])
    h,b=np.histogram(ln,bins=[0,100,140,175,200,215,300,400,600,1000,1500,2000,2500,3100,4000]);print(f,list(zip(b[:-1].tolist(),h.tolist())),'rate',sc.sum()/ln.sum())
    ac=np.array([e['action_counts'] for e in E]).sum(0);print(' actions',np.round(ac/ac.sum(),3))
    for e in E[:3]:
        T=e['trace'];print('  seed',e['seed'],'score',e['score'],'len',e['length'])
        for t in T[-10:]: print('    ',t['a'],t['sub_y'],t['oxygen'],t['diver_count'],t['surface'],t['r'])
