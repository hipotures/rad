#!/usr/bin/env python3
"""Changed-basis corner repair discovery for an actual problematic source pair.

GPU0 uses both negative bases; GPU1 uses negative23 and I+J25. Controlled
local-corner requirements are preserved; data profiles are sample discoveries
requiring complete family geometry and exact rational checks before promotion.

The controlled permutation and null-corner mechanism is James Chang's PR34,
used at (23,25) in Rohan Arun's PR37. This new search mutates free entries of
the common permutation family while preserving its mandatory local corners.
GPU elimination uses integer modular arithmetic; entropy is only a ranking
heuristic. A promoted profile still needs universal rank cuts, rational pivots,
physical accounting and the complete conditional assembly.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time

import cupy as cp
import numpy as np

CUDA = r'''
__device__ unsigned rng(unsigned *s) { *s^=*s<<13;*s^=*s>>17;*s^=*s<<5;return *s; }
__device__ int mul(int x,int y,int p) { return (long long)x*y%p; }
__device__ int power(int a,int b,int p) {int r=1;while(b){if(b&1)r=mul(r,a,p);a=mul(a,a,p);b>>=1;}return r;}
extern "C" __global__ void search(const int *base,const int *xx,const int *yy,
 int p,unsigned seed,unsigned offset,int mutations,double *scores,int *pivots,int *perms) {
 const int a=23,b=25,d=47,m=575,id=blockIdx.x,t=threadIdx.x;
 __shared__ int perm[575],mat[2209],factors[47],q,inv,valid;
 for(int j=t;j<m;j+=blockDim.x)perm[j]=base[j];
 __syncthreads();
 if(t==0){unsigned s=seed^(offset+id+1)*2654435761u;valid=1;
  for(int k=0;k<mutations;k++) {
   int beta=rng(&s)%b,freec[4],n=0;
   if(beta>=a)freec[n++]=0;
   if(beta<d-b)freec[n++]=1;
   if(beta>=(m-d)%b)freec[n++]=a-2;
   if(beta<b-a)freec[n++]=a-1;
   int alpha=freec[rng(&s)%n],other;
   do {other=rng(&s)%a;}while(other==alpha||(other==0&&beta<a)||(other==a-1&&beta>=b-a));
   int z=perm[beta*a+alpha];perm[beta*a+alpha]=perm[beta*a+other];perm[beta*a+other]=z;
  }
 }
 __syncthreads();
 for(int j=t;j<m;j+=blockDim.x)perms[id*m+j]=perm[j];
 for(int z=t;z<d*d;z+=blockDim.x) {
  int i=z/d,j=z%d,al=i/b,be=i%b,ga=(m-d+j)/b,de=(m-d+j)%b;
  int r=perm[be*a+al],c=perm[de*a+ga];
  int v=(r==c?xx[r]:0)+(be==de?yy[be]:0)-1;
  mat[z]=(v%p+p)%p;
 }
 __syncthreads();
 for(int i=0;i<d;i++) {
  if(t==0){q=-1;for(int j=d-1;j>=0;j--)if(mat[i*d+j]){q=j;break;}
   if(q<0)valid=0;else inv=power(mat[i*d+q],p-2,p);
   pivots[id*d+i]=q;
  }
  __syncthreads();
  if(!valid)break;
  for(int k=i+1+t;k<d;k+=blockDim.x)factors[k]=mul(mat[k*d+q],inv,p);
  __syncthreads();
  for(int z=t;z<(d-i-1)*d;z+=blockDim.x) {
   int k=i+1+z/d,j=z%d;
   int v=mat[k*d+j]-mul(factors[k],mat[i*d+j],p);
   mat[k*d+j]=v<0?v+p:v;
  }
  __syncthreads();
 }
 if(t==0) {
  double score=0;int run=1;
  if(valid){for(int i=1;i<d;i++) {
   if(pivots[id*d+i]==pivots[id*d+i-1]+1)run++;
   else{score+=run*log((double)run);run=1;}
  }score+=run*log((double)run);}
  scores[id]=valid?score:-1;
 }
}
'''


def baseline():
    a,b,d,m=23,25,47,575
    rows=list(range(a))+[a-1]+list(range(a))
    cols=list(range(a))+[0]+list(range(a))
    constraints=[{} for _ in range(b)]
    for words,start in ((rows,0),(cols,m-d)):
        for i,v in enumerate(words):
            al,be=divmod(start+i,b)
            assert al not in constraints[be] and v not in constraints[be].values()
            constraints[be][al]=v
    result=[]
    for c in constraints:
        available=iter(sorted(set(range(a))-set(c.values())))
        result.append([c[i] if i in c else next(available) for i in range(a)])
    return np.asarray(result,dtype=np.int32)


def weights(h,negative,p):
    triple={0,1,22}
    if negative:return [((h-1) if i in triple else -2)*pow(h+3,-1,p)%p for i in range(h)]
    inside,outside=(((31,18),(-5,24)) if h==23 else ((68,39),(-5,26)))
    return [(inside[0]*pow(inside[1],-1,p) if i in triple else outside[0]*pow(outside[1],-1,p))%p for i in range(h)]

def reference(perms,p):
    a,b,d,m=23,25,47,575
    wa=weights(23,True,p);wb=weights(25,ACTIVE_DEVICE==0,p)
    xx=[pow(w,-1,p) for w in wa]
    yy=[pow(w,-1,p) for w in wb]
    rows=[(int(perms[i%b,i//b]),i%b) for i in range(d)]
    cols=[(int(perms[(m-d+j)%b,(m-d+j)//b]),(m-d+j)%b) for j in range(d)]
    mat=[[(xx[r]*(r==c)+yy[be]*(be==de)-1)%p for c,de in cols] for r,be in rows]
    piv=[]
    for i in range(d):
        q=next((j for j in reversed(range(d)) if mat[i][j]),-1)
        if q<0:return None
        piv.append(q);iv=pow(mat[i][q],-1,p)
        for k in range(i+1,d):
            fac=mat[k][q]*iv%p
            mat[k]=[(v-fac*w)%p for v,w in zip(mat[k],mat[i])]
    return piv


def widths(piv):
    runs=[1]
    for old,new in zip(piv,piv[1:]):
        if new==old+1:runs[-1]+=1
        else:runs.append(1)
    return runs


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--device',type=int,required=True)
    parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--seconds',type=int,default=600)
    parser.add_argument('--batch',type=int,default=16384)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    prime=(65521,65537)[args.device]
    cp.cuda.Device(args.device).use();cp.get_default_memory_pool().set_limit(size=8*1024**3)
    kernel=cp.RawKernel(CUDA,'search')
    global ACTIVE_DEVICE
    ACTIVE_DEVICE=args.device
    wa=weights(23,True,prime);wb=weights(25,args.device==0,prime)
    xx=cp.asarray([pow(w,-1,prime) for w in wa],dtype=cp.int32)
    yy=cp.asarray([pow(w,-1,prime) for w in wb],dtype=cp.int32)
    base=baseline();best=base.copy();piv=reference(base,prime)
    assert piv is not None
    bestscore=sum(w*math.log(w) for w in widths(piv))
    outscore=cp.empty(args.batch,dtype=cp.float64)
    outpiv=cp.empty((args.batch,47),dtype=cp.int32)
    outperm=cp.empty((args.batch,25,23),dtype=cp.int32)
    # Both independent modular implementations must agree on the starting fixture.
    kernel((1,),(128,),(cp.asarray(base),xx,yy,np.int32(prime),np.uint32(args.seed),np.uint32(0),np.int32(0),outscore,outpiv,outperm))
    cp.cuda.Stream.null.synchronize()
    assert outpiv[0].get().tolist()==piv and abs(float(outscore[0])-bestscore)<1e-9
    started=time.monotonic();batchid=0;attempts=0;accepted=[]
    protocol=dict(start_utc=datetime.now(timezone.utc).isoformat(),device=args.device,seed=args.seed,
                  prime=prime,seconds=args.seconds,batch=args.batch,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  fixed_dimensions=[23,25],source_triples=[[0,1,22],[0,1,22]],basis_modes=['negative-special','negative-special' if args.device==0 else 'I+J'],method='Valid permutation mutations; exact modular elimination; entropy discovery heuristic',
                  certification='Discovery only; sample-specific finite-field zeros do not prove generic rational identities')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    with (args.output/'progress.jsonl').open('x') as stream:
        while time.monotonic()-started<args.seconds:
            mutations=1+batchid%6
            # Distinct seeds and primes split devices; occasional baseline exploration avoids a single basin.
            parent=base if batchid%7==0 else best
            kernel((args.batch,),(128,),(cp.asarray(parent),xx,yy,np.int32(prime),np.uint32(args.seed),np.uint32(attempts),np.int32(mutations),outscore,outpiv,outperm))
            cp.cuda.Stream.null.synchronize();attempts+=args.batch;batchid+=1
            k=int(cp.argmax(outscore));score=float(outscore[k])
            if score>bestscore+1e-9:
                candidate=outperm[k].get();newpiv=outpiv[k].get().tolist()
                assert reference(candidate,prime)==newpiv
                best=candidate;bestscore=score
                record=dict(utc=datetime.now(timezone.utc).isoformat(),attempts=attempts,entropy=score,
                    runs=widths(newpiv),pivots=newpiv,permutations=best.tolist(),prime=prime,
                    rows=[int(best[i%25,i//25]) for i in range(47)],
                    cols=[int(best[(528+j)%25,(528+j)//25]) for j in range(47)])
                accepted.append(record)
                (args.output/f'candidate-{len(accepted):03d}.json').write_text(json.dumps(record,indent=2)+'\n')
                print(json.dumps({k:v for k,v in record.items() if k not in ('permutations','pivots','rows','cols')}),flush=True)
            stream.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),attempts=attempts,elapsed=time.monotonic()-started,best_entropy=bestscore,batch_max=score,mutations=mutations))+'\n');stream.flush()
    result=dict(**protocol,finish_utc=datetime.now(timezone.utc).isoformat(),attempts=attempts,
                elapsed_seconds=time.monotonic()-started,improvements=len(accepted),best_entropy=bestscore,
                baseline_entropy=sum(w*math.log(w) for w in widths(piv)),best_runs=widths(reference(best,prime)),
                limitations=['Repeated mutation prescriptions are possible; attempts are not unique candidates',
                             'No accepted generic rational profile from sampled finite-field rank alone'])
    (args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)


if __name__=='__main__':main()
