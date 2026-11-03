import json, numpy as np
E=json.load(open('/work/pass_1/gold_episodes.json'))
sc=np.array([e['score'] for e in E]); ln=np.array([e['length'] for e in E])
#, np.percentile(sc,[10,25,50,75,90]), 'len pct', np.percentile(ln,[10,25,50,75,90]))
print('corr', np.corrcoef(sc,ln)[0,1], 'score/len', sc.sum()/ln.sum())
ac=np.array([e['action_counts'] for e in E]).sum(0); print('actions', ac/ac.sum())
for e in E:
    if 'trace' not in e or not e['trace']: continue
    T=e['trace']; print('--- seed',e['seed'],'score',e['score'],'len',e['length'])
    surf=[]; prev=None
    for i,t in enumerate(T):
        if t['surface'] and (prev is None or not prev['surface']): surf.append((i,prev['oxygen'] if prev else None, prev['diver_count'] if prev else None, t['diver_count']))
        prev=t
    print(' surfacings (step, oxy_before, div_before, div_after):', surf)
    print(' last 6 steps:', [(t['a'],t['r'],t['sub_x'],t['sub_y'],t['oxygen'],t['diver_count'],t['surface']) for t in T[-6:]])
    ys=np.array([t['sub_y'] for t in T]); print(' y hist', np.bincount(ys,minlength=10))
    xs=np.array([t['sub_x'] for t in T]); print(' x hist', np.bincount(xs,minlength=10))
    rs=np.array([t['r'] for t in T]); print(' rewards>1', [(i,r) for i,r in enumerate(rs) if r>1])
    print(' last 12 actions', [t['a'] for t in T[-12:]], [t['sub_y'] for t in T[-12:]])
