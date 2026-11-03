import json, os, numpy as np
d='/work/pass_2'; print(os.listdir(d))
for f in sorted(os.listdir(d)):
    if not f.endswith('episodes.json'): continue
    E=json.load(open(os.path.join(d,f)))
    ac=np.array([e['action_counts'] for e in E]).sum(0); print(f,'actions',np.round(ac/ac.sum(),3))
    ln=np.array([e['length'] for e in E]); print(' len pct', np.percentile(ln,[10,25,50,75,90]))
    for e in E:
        T=e.get('trace')
        if not T: continue
        surf=sum(1 for i in range(1,len(T)) if T[i]['surface'] and not T[i-1]['surface'])
        print(' seed',e['seed'],'score',e['score'],'len',e['length'],'surf',surf,'last',[(t['a'],t['sub_y'],t['oxygen'],t['diver_count']) for t in T[-5:]])
