import json, os, numpy as np
for k in range(1,6):
    d='/work/pass_%d'%k
    if not os.path.isdir(d): continue
    s=json.load(open(d+'/summary.json'))
    print('pass',k, {kk:(v.get('mean'),v.get('mean_length')) for kk,v in s.items() if isinstance(v,dict) and 'mean' in v})
    for f in sorted(os.listdir(d)):
        if not f.endswith('episodes.json'): continue
        E=json.load(open(os.path.join(d,f)))
        ac=np.array([e['action_counts'] for e in E]).sum(0)
        sc=np.array([e['score'] for e in E]); ln=np.array([e['length'] for e in E])
        print('  ',f,'act',np.round(ac/ac.sum(),3),'frac len<150 %.3f'%(ln<150).mean(), 'kills/step %.4f'%(sc.sum()/ln.sum()))
        for e in E:
            T=e.get('trace')
            if T:
                t=T[-1]; print('     death: oxy',t['oxygen'],'div',t['diver_count'],'y',t['sub_y'],'len',e['length'], 'last y seq',[q['sub_y'] for q in T[-6:]],'a',[q['a'] for q in T[-6:]])
