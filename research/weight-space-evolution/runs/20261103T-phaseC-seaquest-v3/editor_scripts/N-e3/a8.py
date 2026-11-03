import json, numpy as np
for nm in ['gold','candidate']:
    eps=json.load(open(f'/work/pass_1/{nm}_episodes.json'))
    S=np.array([e['score'] for e in eps]); Lg=np.array([e['length'] for e in eps])
    ac=np.array([e['action_counts'] for e in eps]).sum(0)
    print(nm,"score",S.mean(),"len",Lg.mean(),"score/1000steps",1000*S.sum()/Lg.sum(),"actfrac",np.round(ac/ac.sum(),3))
    print(" len pct",np.percentile(Lg,[10,25,50,75,90]), "score pct",np.percentile(S,[10,25,50,75,90]))
    for e in [x for x in eps if 'trace' in x]:
        t=e['trace']; y=np.array([s['sub_y'] for s in t]); r=np.array([s['r'] for s in t]); ox=np.array([s['oxygen'] for s in t]); dc=np.array([s['diver_count'] for s in t]); sf=np.array([s['surface'] for s in t])
        rowocc=np.bincount(y,minlength=10)[:9]/len(y); rowrew=np.bincount(y,weights=r,minlength=10)[:9]
        big=[(i,r[i],dc[i-1],ox[i-1]) for i in range(1,len(t)) if r[i]>1]
        surf=[(i,int(dc[i-1]),int(dc[i]),int(ox[i-1])) for i in range(1,len(t)) if y[i]==0 and y[i-1]!=0]
        print(" ep len",len(t),"score",r.sum(),"rowocc",np.round(rowocc,2),"rowrew",rowrew)
        print("   bigrewards",big[:10]); print("   surfacings (step,dc_before,dc_after,oxy)",surf[:15])
        print("   end y",y[-1],"oxy",ox[-1],"dc",dc[-1])
