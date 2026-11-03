f=net(gold)
A='n l u r d f'.split()
names=['fire%d'%i for i in range(8)]+['up%d'%i for i in range(8)]+['dn%d'%i for i in range(8)]+['u24','d25']+['x']*6
def show(tag,x):
    p,l,h1,h2=f(x); act=[(names[i],round(float(h2[i]),2)) for i in range(26) if h2[i]>-0.9]
    print(tag,'p',p,'l',l-l.max(),act)
for y in [3,5,8]:
    show('ascend y%d clear'%y, st(y,oxy=50,div=2))
    for ex in [3,4,5,6,7]:
        show('ascend y%d fish above x%d'%(y,ex), st(y,oxy=50,div=2,ent=[(y-1,ex,'fish',ex<5)]))
    for ex in [4,6,7]:
        show('ascend y%d fish own x%d'%(y,ex), st(y,oxy=50,div=2,ent=[(y,ex,'fish',ex<5)]))
    show('ascend y%d bullet above x5'%y, st(y,oxy=50,div=2,ent=[(y-1,5,'bullet',True)]))
show('normal y5 bullet own x6', st(5,ent=[(5,6,'bullet',False)]))
show('normal y5 bullet own x4', st(5,ent=[(5,4,'bullet',True)]))
