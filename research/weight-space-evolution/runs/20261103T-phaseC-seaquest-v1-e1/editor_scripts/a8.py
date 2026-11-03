import json,numpy as np,os
print(os.listdir('/work/pass_2'))
for f in sorted(os.listdir('/work/pass_2')):
    if not f.endswith('episodes.json'): continue
    E=json.load(open('/work/pass_2/'+f))
    ln=np.array([e['length'] for e in E]);sc=np.array([e['score'] for e in E])
    h,b=np.histogram(ln,bins=[0,100,140,175,200,215,300,400,600,1000,1500,2000,2500,3100,4000]);print(f,list(zip(b[:-1].tolist(),h.tolist())))
    print(' rate',sc.sum()/ln.sum())
    for e in E[:3]:
        T=e['trace'];print('  seed',e['seed'],'score',e['score'],'len',e['length'])
        for t in T[-12:]: print('    ',t['a'],t['sub_y'],t['oxygen'],t['diver_count'],t['surface'],t['r'])
