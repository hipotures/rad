import os, json, numpy as np
d='/work/pass_1'
for f in sorted(os.listdir(d)): print(f, os.path.getsize(os.path.join(d,f)))
for f in sorted(os.listdir(d)):
    p=os.path.join(d,f)
    txt=open(p).read()
    print('=====',f); print(txt[:1500])
