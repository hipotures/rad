def mk(row=4, ox=200, dc=2, ents=()):
    e=Env(0); e.sub_y=row; e.oxygen=ox; e.diver_count=dc
    for kind,x,y,lr in ents:
        if kind=='f': e.e_fish.append([x,y,lr,5])
        elif kind=='s': e.e_subs.append([x,y,lr,5,10])
        elif kind=='d': e.divers.append([x,y,lr,5])
        elif kind=='b': e.e_bullets.append([x,y,lr])
    return e.obs()
def probs(P,x):
    L=logits_of(P,x[None])[0]; L=L-L.max(); p=np.exp(L); p/=p.sum(); return p
def show(P,label,x):
    W1,b1,W2,b2,W3,b3=P
    print('%-28s'%label, ' '.join('%.2f'%v for v in probs(P,x)))
