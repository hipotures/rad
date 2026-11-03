import numpy as np
np.set_printoptions(precision=3, suppress=True, linewidth=220)
def net(get):
    W1,b1,W2,b2,W3,b3=[get(n) for n in ['W1','b1','W2','b2','W3','b3']]
    def f(x):
        h1=np.tanh(x@W1+b1); h2=np.tanh(h1@W2+b2); l=h2@W3+b3; p=np.exp(l-l.max()); return p/p.sum(), l, h1, h2
    return f
def st(sy,sx=5,orr=False,oxy=150,div=0,ent=()):
    s=np.zeros((10,10,6))
    s[sy,sx,0]=1; bx=sx-1 if orr else sx+1
    if 0<=bx<=9: s[sy,bx,0]=1; s[sy,bx,4]=1
    s[9,0:oxy*10//200,5]=1; s[9,9-div:9,5]=1
    for (y,x,kind,lr) in ent:
        if kind in('fish','sub'): s[y,x,1]=1; s[y,x,2]=1
        if kind=='bullet': s[y,x,1]=1
        if kind=='diver': s[y,x,2]=1
        if kind!='bullet':
            bx=x-1 if lr else x+1
            if 0<=bx<=9: s[y,bx,4]=1
    return s.reshape(-1)
import json,numpy as np,collections
E=json.load(open('/work/pass_6/candidate_episodes.json'))
ac=np.array([e['action_counts'] for e in E]).sum(0); print('actions',(ac/ac.sum()).round(3))
for e in E:
    if 'trace' not in e: continue
    t=e['trace']; print('ep',e['score'],len(t),'x dist',sorted(collections.Counter(s['sub_x'] for s in t).items()),'or',collections.Counter(s['sub_or'] for s in t))
    print('  first 40',[(s['a'],s['sub_x'],s['sub_y'],int(s['sub_or'])) for s in t[:40]])
    print('  last 10',[(s['a'],s['sub_x'],s['sub_y'],s['oxygen'],s['diver_count']) for s in t[-10:]])
