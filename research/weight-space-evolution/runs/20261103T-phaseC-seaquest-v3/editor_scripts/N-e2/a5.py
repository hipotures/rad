import json,numpy as np
E=json.load(open('/work/pass_1/gold_episodes.json'))
s=np.array([e['score'] for e in E]); L=np.array([e['length'] for e in E])
print("score pct",np.percentile(s,[0,10,25,50,75,90,100]),"len pct",np.percentile(L,[0,10,50,90,100]))
print("corr",np.corrcoef(s,L)[0,1], "score/len", s.sum()/L.sum())
for e in E:
    if 'trace' not in e: continue
    T=e['trace']; print("EP seed",e['seed'],"score",e['score'],"len",e['length'])
    last=T[-6:]; print(" last:",[(t['a'],t['sub_y'],t['oxygen'],t['diver_count'],t['surface']) for t in last])
    # surfacing events
    prev=None; ev=[]
    for i,t in enumerate(T):
        if t['surface'] and (prev is None or not prev['surface']):
            ev.append((i,prev['diver_count'] if prev else None, prev['oxygen'] if prev else None, t['r']))
        prev=t
    print(" surfacings (step,divers_before,oxy_before,r):",ev)
    rw=[(i,t['r']) for i,t in enumerate(T) if t['r']>1]; print(" big rewards",rw[:10])
    dc=[t['diver_count'] for t in T]; print(" max divers",max(dc), "ys hist",np.bincount([t['sub_y'] for t in T],minlength=10))
    xs=set(t['sub_x'] for t in T); print(" xs",xs)
    # oxygen min before each surfacing
