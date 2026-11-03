import json,numpy as np,os
print(os.listdir('/work/pass_2'))
for f in ['/work/pass_1/gold_episodes.json']+['/work/pass_2/'+x for x in os.listdir('/work/pass_2') if x.endswith('episodes.json')]:
    E=json.load(open(f)); L=np.array([e['length'] for e in E])
    print(f, "len<100",(L<100).mean(),"190-215",((L>=190)&(L<=215)).mean(), np.histogram(L,bins=[0,50,100,150,190,215,300,500,1000,2000,4000])[0])
    for e in E:
        if 'trace' in e:
            T=e['trace']; t=T[-1]
            print("  death len",e['length'],"y",t['sub_y'],"oxy",t['oxygen'],"div",t['diver_count'],"last acts",[x['a'] for x in T[-6:]],"ys",[x['sub_y'] for x in T[-6:]])
