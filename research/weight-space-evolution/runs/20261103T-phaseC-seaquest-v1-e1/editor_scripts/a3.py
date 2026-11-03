import os,json
for root,ds,fs in os.walk('/work/pass_1'):
    for f in fs:
        p=os.path.join(root,f); print(p, os.path.getsize(p))
import glob
for p in sorted(glob.glob('/work/pass_1/*'))[:20]:
    if os.path.isfile(p):
        s=open(p).read(); print('====',p); print(s[:1500])
