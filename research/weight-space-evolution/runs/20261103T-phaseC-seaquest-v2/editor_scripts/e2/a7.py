import json,os,numpy as np
print(os.listdir('/work/pass_2'))
for fn in ['gold_episodes.json','candidate_episodes.json']:
    if not os.path.exists('/work/pass_2/'+fn): continue
    E=json.load(open('/work/pass_2/'+fn))
    sc=np.array([e['score'] for e in E]); L=np.array([e['length'] for e in E])
    print(fn,'score pct',np.percentile(sc,[10,25,50,75,90]),'len pct',np.percentile(L,[10,25,50,75,90]))
    for e in E:
        if 'trace' not in e: continue
        T=e['trace']
        ns=sum(1 for i,t in enumerate(T) if t['surface'] and i>0 and not T[i-1]['surface'])
        print(' ep',e['score'],e['length'],'surfacings',ns,'last:',' '.join('%s%d,%d/o%d/d%d'%('nlurdf'[t['a']],t['sub_y'],t['r'],t['oxygen'],t['diver_count']) for t in T[-12:]))
