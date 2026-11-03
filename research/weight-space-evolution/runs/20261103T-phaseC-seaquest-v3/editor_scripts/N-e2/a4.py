import os,json
for f in sorted(os.listdir('/work/pass_1')):
    p='/work/pass_1/'+f; print(f, os.path.getsize(p))
    print(open(p).read()[:600]); print('---')
