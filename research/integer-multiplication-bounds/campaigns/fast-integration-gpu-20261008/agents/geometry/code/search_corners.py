#!/usr/bin/env python3
"""Discover controlled-boundary prescriptions by exact finite-field pivots.

This is discovery only: modular witnesses are not generic-basis proofs. All
ordinary first/last factor restrictions and permutation completions are checked.
The independent scalar producer and every rank-one correction stay unchanged.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from hashlib import sha256
import argparse, json, math, os, random, time

PRIME=1000000007

def labels(a,b):
    d=a+b-1
    if b==a+2:
        return list(range(a))+[a-1]+list(range(a)),list(range(a))+[0]+list(range(a))
    raise ValueError('Only the pinned reversed family is initialized')

def completion(a,b,R,C):
    d=a+b-1;m=a*b
    if sorted(R[:a])!=list(range(a)) or sorted(C[-a:])!=list(range(a)):return None
    partial=[{} for _ in range(b)]
    for seq,offset in ((R,0),(C,m-d)):
        for k,label in enumerate(seq):
            alpha,beta=divmod(offset+k,b)
            if alpha in partial[beta] and partial[beta][alpha]!=label:return None
            if label in partial[beta].values() and partial[beta].get(alpha)!=label:return None
            partial[beta][alpha]=label
    perms=[]
    for p in partial:
        unused=iter(x for x in range(a) if x not in p.values())
        perms.append([p[i] if i in p else next(unused) for i in range(a)])
    return perms

def pivot_profile(a,b,R,C,degree=2):
    p=PRIME;d=a+b-1;offset=a*b-d
    wa=[(i+1)**degree+1 for i in range(a)];wb=[(2*i+1)**(degree+1)+2 for i in range(b)]
    sa,sb=sum(wa)%p,sum(wb)%p
    xx=[sa*pow(x,-1,p)%p for x in wa];yy=[sb*pow(x,-1,p)%p for x in wb]
    matrix=[[(xx[r] if r==c else 0)+(yy[i%b] if i%b==(offset+j)%b else 0)-1 for j,c in enumerate(C)] for i,r in enumerate(R)]
    matrix=[[x%p for x in row] for row in matrix];available=list(range(d));pivots=[]
    for i in range(d):
        row=matrix[i];col=next((j for j in reversed(available) if row[j]),None)
        if col is None:return None
        available.remove(col);pivots.append(col);inv=pow(row[col],-1,p)
        active=[j for j in available if row[j]]
        normalized={j:row[j]*inv%p for j in active}
        for k in range(i+1,d):
            value=matrix[k][col]
            if value:
                r=matrix[k]
                for j in active:r[j]=(r[j]-value*normalized[j])%p
                r[col]=0
    widths=[]
    for i,j in enumerate(pivots):
        if i and j==pivots[i-1]+1:widths[-1]+=1
        else:widths.append(1)
    return pivots,widths

def score(widths):return sum(w*math.log(w) for w in widths)

def search(config,outdir):
    rng=random.Random(config['seed']);a,b=config['dimensions'];d=a+b-1
    R,C=labels(a,b);base=pivot_profile(a,b,R,C);base_score=score(base[1]);best_score=base_score
    best=dict(rows=R[:],columns=C[:],pivots=base[0],widths=base[1],score=base_score)
    current=best.copy();completed=valid=singular=improved=0;start=time.monotonic()
    path=Path(outdir)/('worker-'+str(config['worker'])+'.json')
    while time.monotonic()-start<config['seconds']:
        r=current['rows'][:];c=current['columns'][:]
        mode=config['worker']%6
        if rng.random()<0.015:r,c=labels(a,b)
        edits=1 if rng.random()<.8 else rng.randrange(2,5)
        for _ in range(edits):
            side=r if rng.random()<.5 else c
            if side is r:
                if mode>=2 and rng.random()<.18:
                    i,j=rng.sample(range(a),2);side[i],side[j]=side[j],side[i]
                else:side[rng.randrange(a,d)]=rng.randrange(a)
            else:
                if mode>=2 and rng.random()<.4:
                    i,j=rng.sample(range(d-a,d),2);side[i],side[j]=side[j],side[i]
                else:side[rng.randrange(d-a)]=rng.randrange(a)
        completed+=1
        if completion(a,b,r,c) is None:continue
        valid+=1;prof=pivot_profile(a,b,r,c)
        if prof is None:singular+=1;continue
        value=score(prof[1]);candidate=dict(rows=r,columns=c,pivots=prof[0],widths=prof[1],score=value)
        temperature=.08 if mode<2 else .18
        if value>=current['score'] or rng.random()<math.exp((value-current['score'])/temperature):current=candidate
        if value>best_score+1e-10:
            best_score=value;best=candidate;improved+=1
            best['independent_degree3_profile']=pivot_profile(a,b,r,c,3)
        if completed%100==0:
            result=dict(config=config,pid=os.getpid(),completed=completed,valid=valid,singular=singular,improvements=improved,elapsed_seconds=time.monotonic()-start,
                        baseline=base,best=best,utc=datetime.now(timezone.utc).isoformat(),status='modular discovery; generic proof not supplied')
            tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(path)
    result=dict(config=config,pid=os.getpid(),completed=completed,valid=valid,singular=singular,improvements=improved,elapsed_seconds=time.monotonic()-start,
                baseline=base,best=best,utc=datetime.now(timezone.utc).isoformat(),status='modular discovery; generic proof not supplied')
    path.write_text(json.dumps(result,indent=2)+'\n');return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--seconds',type=float,default=480);ap.add_argument('--seed',type=int,default=202610081251);args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    configs=[dict(worker=i,dimensions=[23,25],seed=args.seed+7919*i,seconds=args.seconds,prime=PRIME) for i in range(6)]
    (args.output/'protocol.json').write_text(json.dumps(dict(started_utc=datetime.now(timezone.utc).isoformat(),configs=configs,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(search,configs,[str(args.output)]*6))
    (args.output/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps([dict(worker=r['config']['worker'],cases=r['completed'],valid=r['valid'],widths=r['best']['widths'],score=r['best']['score'],seconds=r['elapsed_seconds']) for r in results]),flush=True)

if __name__=='__main__':main()
