#!/usr/bin/env python3
"""Vary actual rational basis pairs on GPUs; retain sample discoveries only."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import time
import cupy as cp
import numpy as np

ROOT_SOURCE = Path(__file__).resolve().parents[3] / 'code/gpu_changed_basis_repair.py'
spec = importlib.util.spec_from_file_location('campaign_cuda_source', ROOT_SOURCE)
upstream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upstream)
old = '(r==c?xx[r]:0)+(be==de?yy[be]:0)'
new = '(r==c?xx[id*a+r]:0)+(be==de?yy[id*b+be]:0)'
assert upstream.CUDA.count(old) == 1
CUDA = upstream.CUDA.replace(old, new)
SOURCES = (([0,1,22],[0,2,24]), ([0,1,22],[0,1,22]))

def forbidden(h):
    return {F(0), F(1,3), F(1,9), F(1,h), F(2,3*(h-3))}

def rational_weights(h, beta):
    assert beta not in forbidden(h)
    gamma = (9*beta-1)/(3*(1-h*beta))
    inside = (1-3*beta)*(1+gamma)/2
    outside = -3*beta*gamma/2
    assert inside and outside and 3*inside+(h-3)*outside == 1
    return inside, outside

def modular_inverse_weights(h, beta, triple, prime):
    inside, outside = rational_weights(h,beta)
    values=[]
    for w in (inside,outside):
        if w.denominator % prime == 0 or w.numerator % prime == 0:
            return None
        values.append(w.denominator*pow(w.numerator,-1,prime)%prime)
    return [values[0] if i in triple else values[1] for i in range(h)]

def reference(perms, xx, yy, prime):
    rows=[(int(perms[i%25,i//25]),i%25) for i in range(47)]
    cols=[(int(perms[(528+j)%25,(528+j)//25]),(528+j)%25) for j in range(47)]
    matrix=[[(xx[r]*(r==c)+yy[be]*(be==de)-1)%prime for c,de in cols] for r,be in rows]
    pivots=[]
    for i in range(47):
        q=next((j for j in range(46,-1,-1) if matrix[i][j]),-1)
        if q<0:return None
        pivots.append(q);inverse=pow(matrix[i][q],-1,prime)
        for k in range(i+1,47):
            if matrix[k][q]:
                factor=matrix[k][q]*inverse%prime
                matrix[k]=[(v-factor*w)%prime for v,w in zip(matrix[k],matrix[i])]
    return pivots

def serial_fraction(x):
    return {'numerator':x.numerator,'denominator':x.denominator}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--device',type=int,required=True)
    p.add_argument('--seed',type=int,required=True)
    p.add_argument('--seconds',type=int,default=600)
    p.add_argument('--batch',type=int,default=8192)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();assert args.device in (0,1) and args.batch%2==0
    assert not args.output.exists();args.output.mkdir(parents=True)
    prime=(65521,65537)[args.device]
    cp.cuda.Device(args.device).use();cp.get_default_memory_pool().set_limit(size=8*1024**3)
    kernel=cp.RawKernel(CUDA,'search')
    rng=np.random.default_rng(args.seed)
    lambdas=sorted({F(n,d) for d in range(1,25) for n in range(-8*d,12*d+1) if n})
    pairs=[]
    special={h:F(4,3*(h+3)) for h in (23,25)}
    if args.device==0:
        pairs=[(special[23],x/F(84)) for x in lambdas]+[(special[23],F(-1))]
    else:
        pairs=[(x/F(78),x/F(84)) for x in lambdas]
        grid=[F(x,4) for x in range(-16,49) if x]
        pairs += [(x/F(78),y/F(84)) for x in grid for y in grid]
        pairs += [(F(-1),special[25]),(special[23],F(-1)),(F(-1),F(-1))]
    pairs=sorted(set(pair for pair in pairs if all(pair[k] not in forbidden(h) for k,h in enumerate((23,25)))))
    cache={}
    for pair in pairs:
        rows=[]
        for source in SOURCES:
            x=modular_inverse_weights(23,pair[0],source[0],prime)
            y=modular_inverse_weights(25,pair[1],source[1],prime)
            rows.append((x,y))
        if all(x is not None and y is not None for x,y in rows):cache[pair]=rows
    pairs=list(cache);assert pairs
    base=upstream.baseline();base_gpu=cp.asarray(base)
    scores=cp.empty(args.batch,cp.float64);pivots=cp.empty((args.batch,47),cp.int32)
    perms=cp.empty((args.batch,25,23),cp.int32)
    baseline=[]
    for sourceid,source in enumerate(SOURCES):
        x=modular_inverse_weights(23,special[23],source[0],prime)
        y=modular_inverse_weights(25,special[25],source[1],prime)
        pv=reference(base,x,y,prime);assert pv is not None
        runs=upstream.widths(pv);entropy=sum(w*math.log(w) for w in runs)
        kernel((1,),(128,),(base_gpu,cp.asarray(x,cp.int32),cp.asarray(y,cp.int32),np.int32(prime),np.uint32(args.seed),np.uint32(sourceid),np.int32(0),scores,pivots,perms))
        cp.cuda.Stream.null.synchronize()
        assert pivots[0].get().tolist()==pv and abs(float(scores[0])-entropy)<1e-9
        baseline.append({'source_id':sourceid,'source_triples':source,'entropy':entropy,'runs':runs,'pivots':pv})
    protocol={'start_utc':datetime.now(timezone.utc).isoformat(),'device':args.device,'seed':args.seed,'seconds':args.seconds,'batch':args.batch,'prime':prime,'basis_family':'L_h=I-beta_h J','source_triples':SOURCES,'parameter_pairs':len(pairs),'excluded_beta':'0,1/3,1/9,1/h,2/[3(h-3)]','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inherited_cuda_source':str(ROOT_SOURCE),'inherited_source_sha256':hashlib.sha256(ROOT_SOURCE.read_bytes()).hexdigest(),'cuda_sha256':hashlib.sha256(CUDA.encode()).hexdigest(),'cupy':cp.__version__,'numpy':np.__version__,'baseline':baseline,'classification':'DISCOVERY ONLY: sampled finite-field profiles; no full rational, local-frame, bridge or family certificate'}
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    best=[x['entropy'] for x in baseline];accepted=[];attempts=0;batches=0;started=time.monotonic()
    with (args.output/'progress.jsonl').open('x') as log:
        while time.monotonic()-started<args.seconds:
            ids=rng.integers(0,len(pairs),size=args.batch)
            # Every block has its own parameter-dependent source weights.
            xx=np.asarray([cache[pairs[int(k)]][i%2][0] for i,k in enumerate(ids)],np.int32)
            yy=np.asarray([cache[pairs[int(k)]][i%2][1] for i,k in enumerate(ids)],np.int32)
            mutations=0 if batches%3 else 1+(batches//3)%2
            kernel((args.batch,),(128,),(base_gpu,cp.asarray(xx),cp.asarray(yy),np.int32(prime),np.uint32(args.seed),np.uint32(attempts%(2**32)),np.int32(mutations),scores,pivots,perms))
            cp.cuda.Stream.null.synchronize();attempts+=args.batch;batches+=1
            for sourceid in range(2):
                index=2*int(cp.argmax(scores[sourceid::2]))+sourceid;score=float(scores[index])
                if score<=best[sourceid]+1e-9:continue
                perm=perms[index].get();pv=pivots[index].get().tolist()
                assert reference(perm,xx[index].tolist(),yy[index].tolist(),prime)==pv
                pair=pairs[int(ids[index])];best[sourceid]=score
                record={'utc':datetime.now(timezone.utc).isoformat(),'classification':'DISCOVERY ONLY','source_id':sourceid,'source_triples':SOURCES[sourceid],'beta23':serial_fraction(pair[0]),'beta25':serial_fraction(pair[1]),'entropy':score,'baseline_entropy':baseline[sourceid]['entropy'],'runs':upstream.widths(pv),'pivots':pv,'permutations':perm.tolist(),'prime':prime,'attempts':attempts,'mutations':mutations,'inverse_weights23':xx[index].tolist(),'inverse_weights25':yy[index].tolist()}
                accepted.append(record);(args.output/f'candidate-{len(accepted):03d}.json').write_text(json.dumps(record,indent=2)+'\n')
                print(json.dumps({k:v for k,v in record.items() if k not in ('permutations','pivots','inverse_weights23','inverse_weights25')}),flush=True)
            log.write(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'elapsed':time.monotonic()-started,'attempts':attempts,'best_entropy':best,'batch_max':float(cp.max(scores)),'mutations':mutations})+'\n');log.flush()
    summary={**protocol,'finish_utc':datetime.now(timezone.utc).isoformat(),'attempts':attempts,'batches':batches,'elapsed_seconds':time.monotonic()-started,'improvements':len(accepted),'best_entropy':best,'limitations':['Attempts may repeat parameter/permutation pairs.','Candidate promotion requires exact rational pivots, full source family, actual local frames, bridges, physical costs and full conditional assembly.']}
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
