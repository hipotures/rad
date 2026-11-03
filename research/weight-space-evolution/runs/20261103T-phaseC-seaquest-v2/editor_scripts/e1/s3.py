import os,json,numpy as np
d='/work/pass_1'
fs=sorted(os.listdir(d)); print(fs)
for f in fs:
    p=os.path.join(d,f); print(f, os.path.getsize(p))
    s=open(p).read(1500); print(s[:1500]); print('----')
