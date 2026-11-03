import os,json
for root,d,f in os.walk('/work/pass_1'):
    for x in f:
        p=os.path.join(root,x); print(p, os.path.getsize(p))
for x in sorted(os.listdir('/work/pass_1')):
    p='/work/pass_1/'+x
    s=open(p).read()
    print('=====',x); print(s[:1500])
