import os,json
for root,ds,fs in os.walk('/work/pass_1'):
    for f in fs:
        p=os.path.join(root,f); print(p, os.path.getsize(p))
