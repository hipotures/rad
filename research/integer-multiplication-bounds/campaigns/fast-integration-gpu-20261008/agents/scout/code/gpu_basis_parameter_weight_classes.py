#!/usr/bin/env python3
"""New exact source-weight classes, conjugacy deduplicated; sampled Q checks."""
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

HELPER = Path(__file__).with_name('gpu_basis_parameter_discovery.py')
spec=importlib.util.spec_from_file_location('basis_discovery_helper',HELPER)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)

def excluded(h):
    return base.forbidden(h)|{F(h-7,3*(h-3)),F(2,3*(h-1))}

def prime(p):
    return p>=2 and all(p%d for d in range(2,math.isqrt(p)+1))

def exact_reference(perms,pair,source):
    weights=[base.rational_weights(h,beta) for h,beta in zip((23,25),pair)]
    xx=[1/weights[0][0 if i in source[0] else 1] for i in range(23)]
    yy=[1/weights[1][0 if i in source[1] else 1] for i in range(25)]
    rows=[(int(perms[i%25,i//25]),i%25) for i in range(47)]
    cols=[(int(perms[(528+j)%25,(528+j)//25]),(528+j)%25) for j in range(47)]
    M=[[xx[r]*(r==c)+yy[be]*(be==de)-1 for c,de in cols] for r,be in rows]
    piv=[]
    for i in range(47):
        q=next((j for j in range(46,-1,-1) if M[i][j]),-1)
        if q<0:return None
        piv.append(q)
        for k in range(i+1,47):
            if M[k][q]:
                ratio=M[k][q]/M[i][q]
                M[k]=[v-ratio*w for v,w in zip(M[k],M[i])]
    return piv

def source_class(pair):
    return tuple(base.rational_weights(h,beta)[1] for h,beta in zip((23,25),pair))

def candidates(device):
    # Discard all prior exact weight classes, including conjugate beta roots.
    spec=importlib.util.spec_from_file_location('prior_weight_catalogues',Path(__file__).with_name('source_weight_class_audit.py'))
    audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    prior_pairs=set()
    for previous in range(2):
        prior_pairs.update(audit.initial_catalogue(previous,base))
    for name in ('gpu_basis_parameter_vectorized.py','gpu_basis_parameter_gamma.py'):
        spec=importlib.util.spec_from_file_location('prior_'+name.replace('.','_'),Path(__file__).with_name(name))
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        for previous in range(2):prior_pairs.update(module.candidates(previous))
    prior_classes={source_class(pair) for pair in prior_pairs}
    gamma=sorted({F(n,d) for d in (43,47,53,59,61,67,71,73,79,83,89,97)
                  for n in range(-4*d,4*d+1) if n and n%d})
    def beta(h,g):
        return (1+3*g)/(3*(h*g+3)) if h*g+3 else None
    if device==0:
        pairs=[(F(2,39),beta(25,g)) for g in gamma]
    else:
        pairs=[(beta(23,g),beta(25,g)) for g in gamma]
        left=[F(n,43) for n in range(-129,130,2) if n and n%43]
        right=[F(n,47) for n in range(-141,142,3) if n and n%47]
        pairs += [(beta(23,g),beta(25,k)) for g in left for k in right]
    representatives={}
    for pair in sorted(set(pairs)):
        if None in pair or any(pair[k] in excluded(h) for k,h in enumerate((23,25))):continue
        key=source_class(pair)
        if key not in prior_classes:representatives.setdefault(key,pair)
    pairs=sorted(representatives.values())
    assert pairs and len({source_class(pair) for pair in pairs})==len(pairs)
    assert all(source_class(pair) not in prior_classes for pair in pairs)
    return pairs

def table(pairs,p):
    masks=[np.asarray([[i in source[k] for i in range(h)] for source in base.SOURCES]) for k,h in enumerate((23,25))]
    arrays=[np.empty((len(pairs),2,h),np.int32) for h in (23,25)]
    valid=np.ones(len(pairs),bool)
    for i,pair in enumerate(pairs):
        for k,h in enumerate((23,25)):
            vals=[]
            for w in base.rational_weights(h,pair[k]):
                if w.denominator%p==0 or w.numerator%p==0:
                    valid[i]=False;vals.append(0)
                else:vals.append(w.denominator*pow(w.numerator,-1,p)%p)
            arrays[k][i]=np.where(masks[k],vals[0],vals[1])
    return arrays,valid

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--device',type=int,required=True)
    parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--seconds',type=int,default=600)
    parser.add_argument('--batch',type=int,default=8192)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assert args.device in (0,1) and args.batch%2==0
    assert not args.output.exists();args.output.mkdir(parents=True)
    cp.cuda.Device(args.device).use()
    cp.get_default_memory_pool().set_limit(size=8*1024**3)
    primes=((65521,1000003),(65537,1000033))[args.device]
    assert all(prime(p) for p in primes)
    pairs=candidates(args.device);tables=[];valid=np.ones(len(pairs),bool)
    for p in primes:
        values,ok=table(pairs,p);tables.append(values);valid &= ok
    pairs=[pair for pair,ok in zip(pairs,valid) if ok];assert pairs
    tables=[[cp.asarray(x[valid].reshape(-1,x.shape[-1])) for x in values] for values in tables]
    kernel=cp.RawKernel(base.CUDA,'search');parent=base.upstream.baseline();parent_gpu=cp.asarray(parent)
    outscore=[cp.empty(args.batch,cp.float64) for _ in primes]
    outpiv=[cp.empty((args.batch,47),cp.int32) for _ in primes]
    outperm=cp.empty((args.batch,25,23),cp.int32)
    rng=np.random.default_rng(args.seed);source_ids=np.arange(args.batch,dtype=np.int32)%2
    special=(F(2,39),F(1,21));baseline=[]
    for source_id,source in enumerate(base.SOURCES):
        exact=exact_reference(parent,special,source);assert exact is not None
        runs=base.upstream.widths(exact);score=sum(w*math.log(w) for w in runs)
        for pi,p in enumerate(primes):
            x=base.modular_inverse_weights(23,special[0],source[0],p)
            y=base.modular_inverse_weights(25,special[1],source[1],p)
            assert base.reference(parent,x,y,p)==exact
            kernel((1,),(128,),(parent_gpu,cp.asarray(x,cp.int32),cp.asarray(y,cp.int32),np.int32(p),np.uint32(args.seed),np.uint32(source_id),np.int32(0),outscore[pi],outpiv[pi],outperm))
            cp.cuda.Stream.null.synchronize()
            assert outpiv[pi][0].get().tolist()==exact and abs(float(outscore[pi][0])-score)<1e-9
        baseline.append({'source_id':source_id,'entropy':score,'runs':runs,'pivots':exact})
    protocol={'start_utc':datetime.now(timezone.utc).isoformat(),'device':args.device,'seed':args.seed,'seconds':args.seconds,'batch':args.batch,'primes':primes,'parameter_pairs':len(pairs),'parameter_partition':'Fresh gamma denominators43..97 plus independent denominator43/47 grid; ALL prior source-weight class supersets excluded and new catalogues conjugacy deduplicated.', 'parameter_rng_dtype':'int32','source_weight_classes_deduplicated':True,'source_weight_class_key':'Exact rational pair (z_out23,z_out25)','basis_family':'L_h=I-beta_h J','source_triples':base.SOURCES,'method':'GPU-resident inverse-weight tables; vectorized indexed gathering; two independent modular fields; exact Q on improvements.','excluded_beta':{str(h):[base.serial_fraction(x) for x in sorted(excluded(h))] for h in (23,25)},'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'helper_sha256':hashlib.sha256(HELPER.read_bytes()).hexdigest(),'inherited_source_sha256':hashlib.sha256(base.ROOT_SOURCE.read_bytes()).hexdigest(),'cuda_sha256':hashlib.sha256(base.CUDA.encode()).hexdigest(),'cupy':cp.__version__,'numpy':np.__version__,'baseline':baseline,'classification':'DISCOVERY ONLY; exact sampled Q checks do not certify full family/local frames/bridges.'}
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    best=[x['entropy'] for x in baseline];accepted=[];rejected=[];attempts=0;batches=0;started=time.monotonic()
    with (args.output/'progress.jsonl').open('x') as progress:
        while time.monotonic()-started<args.seconds:
            ids=rng.integers(0,len(pairs),size=args.batch,dtype=np.int32)
            index=cp.asarray(2*ids+source_ids);mutations=0 if batches%3 else 1+(batches//3)%2
            gathered=[]
            for pi,p in enumerate(primes):
                x=cp.take(tables[pi][0],index,axis=0);y=cp.take(tables[pi][1],index,axis=0);gathered.append((x,y))
                kernel((args.batch,),(128,),(parent_gpu,x,y,np.int32(p),np.uint32(args.seed),np.uint32(attempts%(2**32)),np.int32(mutations),outscore[pi],outpiv[pi],outperm))
            cp.cuda.Stream.null.synchronize();attempts+=args.batch;batches+=1
            agreement=cp.all(outpiv[0]==outpiv[1],axis=1)&(outscore[0]>=0)&(outscore[1]>=0)
            score=cp.where(agreement,outscore[0],-1)
            for source_id in range(2):
                at=2*int(cp.argmax(score[source_id::2]))+source_id;value=float(score[at])
                if value<=best[source_id]+1e-9:continue
                perm=outperm[at].get();pv=outpiv[0][at].get().tolist();pair=pairs[int(ids[at])]
                modular=[]
                for pi,p in enumerate(primes):
                    x=gathered[pi][0][at].get().tolist();y=gathered[pi][1][at].get().tolist()
                    assert base.reference(perm,x,y,p)==pv;modular.append({'prime':p,'inverse_weights23':x,'inverse_weights25':y})
                qpv=exact_reference(perm,pair,base.SOURCES[source_id])
                record={'utc':datetime.now(timezone.utc).isoformat(),'classification':'DISCOVERY ONLY','source_id':source_id,'source_triples':base.SOURCES[source_id],'beta23':base.serial_fraction(pair[0]),'beta25':base.serial_fraction(pair[1]),'entropy':value,'baseline_entropy':baseline[source_id]['entropy'],'runs':base.upstream.widths(pv),'pivots':pv,'permutations':perm.tolist(),'modular_checks':modular,'sample_rational_pivots':qpv,'sample_rational_check':qpv==pv,'attempts':attempts,'mutations':mutations}
                if qpv!=pv:
                    rejected.append(record);(args.output/f'rejected-{len(rejected):03d}.json').write_text(json.dumps(record,indent=2)+'\n');continue
                best[source_id]=value;accepted.append(record);(args.output/f'candidate-{len(accepted):03d}.json').write_text(json.dumps(record,indent=2)+'\n')
                print(json.dumps({k:v for k,v in record.items() if k not in ('permutations','pivots','sample_rational_pivots','modular_checks')}),flush=True)
            progress.write(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'elapsed':time.monotonic()-started,'attempts':attempts,'best_entropy':best,'mutations':mutations,'field_profile_disagreements':int(cp.count_nonzero(~agreement)),'rejected_rational_candidates':len(rejected)})+'\n');progress.flush()
    summary={**protocol,'finish_utc':datetime.now(timezone.utc).isoformat(),'attempts':attempts,'batches':batches,'elapsed_seconds':time.monotonic()-started,'improvements':len(accepted),'rejected_rational_candidates':len(rejected),'best_entropy':best}
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
