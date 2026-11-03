import json,numpy as np, collections
np.set_printoptions(precision=3, suppress=True, linewidth=200)
E=json.load(open('/work/pass_1/gold_episodes.json'))
L=np.array([e['length'] for e in E]); S=np.array([e['score'] for e in E])
h=np.histogram(L,bins=[0,50,100,150,190,215,250,300,400,600,1000,1500,2000,2500,3000,3500]); print(list(zip(h[1][:-1],h[0])))
print('len 199..203 count', ((L>=199)&(L<=203)).sum())
print('kills per step', S.sum()/L.sum())
W1,b1,W2,b2,W3,b3=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
def pol(x):
    h1=np.tanh(x@W1+b1); h2=np.tanh(h1@W2+b2); l=h2@W3+b3; p=np.exp(l-l.max()); return p/p.sum()
def st(sy,sx=5,orr=False,oxy=150,div=0,ent=()):
    s=np.zeros((10,10,6))
    s[sy,sx,0]=1; bx=sx-1 if orr else sx+1; s[sy,bx,0]=1; s[sy,bx,4]=1
    s[9,0:oxy*10//200,5]=1; s[9,9-div:9,5]=1
    for (y,x,kind,lr) in ent:
        if kind in('fish','sub'): s[y,x,1]=1; s[y,x,2]=1
        if kind=='bullet': s[y,x,1]=1
        if kind=='diver': s[y,x,2]=1
        if kind!='bullet':
            bx=x-1 if lr else x+1
            if 0<=bx<=9: s[y,bx,4]=1
    return s.reshape(-1)
A='n l u r d f'.split()
print('empty water, rows; cols: probs n l u r d f')
for oxy,div in [(150,0),(150,2),(50,0),(50,2),(30,6)]:
    print('oxy',oxy,'div',div)
    for y in range(9): print('  y',y,pol(st(y,oxy=oxy,div=div)))
print('diver in row 6 (moving left at x=8), sub row 3:',pol(st(3,ent=[(6,8,'diver',False)])))
for y in [3,6]:
  for ex in [0,2,3,4,6,7,8,9]:
    print('sub y',y,'fish own row x',ex,pol(st(y,ent=[(y,ex,'fish',ex<5)])))
  print('sub y',y,'fish row below x5',pol(st(y,ent=[(y+1,5,'fish',True)])), 'above',pol(st(y,ent=[(y-1,5,'fish',True)])))
