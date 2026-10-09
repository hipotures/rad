#!/usr/bin/env python3
"""Same-size convolution gauge tests and an explicit padded embedding.

Walsh/C tensors at N>=3 cannot become a same-size Toeplitz, circulant or
twisted-circulant operator by invertible diagonal gauges and permutations.
The analytic proof is separate; finite scans and padded counterexamples
verify its premises. Bigger embeddings and sums of convolutions are open.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
from itertools import permutations
import json
from math import lcm
from pathlib import Path
import time

from lagrangian_graph_completion import basis,image,solve
import pauli_tensor_discriminator as g


def canonical_order(order,n):
    independent=[]
    for x in order:
        if len(basis(tuple(independent)+(x,),n))>len(independent):independent.append(x)
    return tuple(solve(tuple(independent),x) for x in order)


def gauge_test(xs,ys,n):
    d=1<<n;dx=[a^b for a,b in zip(xs,xs[1:])];dy=[a^b for a,b in zip(ys,ys[1:])];rho={}
    for i,a in enumerate(dx):
        for j,b in enumerate(dy):
            value=(a&b).bit_count()%2;t=i-j
            if t in rho and rho[t]!=value:return None
            rho[t]=value
    # Cross ratios constant on diagonals are sufficient. Seeds+recurrence
    # construct a sign Toeplitz kernel and sign row/column gauges.
    kernel={0:1,1:1}
    for t in range(1,d-1):kernel[t+1]=kernel[t-1]*((-1)**rho[t])
    for t in range(0,-d+1,-1):kernel[t-1]=kernel[t+1]*((-1)**rho[t])
    W=lambda i,j:(-1)**((xs[i]&ys[j]).bit_count()%2)
    rows=[kernel[i]*W(i,0) for i in range(d)];cols=[kernel[-j]*rows[0]*W(0,j) for j in range(d)]
    if any(rows[i]*cols[j]*W(i,j)!=kernel[i-j] for i in range(d) for j in range(d)):
        raise ValueError('Cross-ratio gauge reconstruction failed')
    if any(sum(kernel[i-j]*kernel[k-j] for j in range(d))!=(d if i==k else 0) for i in range(d) for k in range(d)):
        raise ValueError('Reconstructed sign Toeplitz is not Hadamard')
    wraps={kernel[i]*kernel[i-d] for i in range(1,d)}
    if len(wraps)!=1:raise ValueError('Toeplitz Hadamard failed uniform cyclic/negacyclic wrap')
    return dict(row_order=xs,column_order=ys,kernel={str(k):v for k,v in sorted(kernel.items())},
                sign_row_gauges=rows,sign_column_gauges=cols,sign_wrap_unit=wraps.pop())


def inverse(z):
    norm=z[0]*z[0]+z[1]*z[1]
    if not norm:raise ValueError('Gauge coefficient is zero')
    return z[0]/norm,-z[1]/norm


def power(z,k):return g.power(z,k) if k>=0 else g.power(inverse(z),-k)


def dyadic_unit_gauges(witness,n):
    d=1<<n;xs=witness['row_order'];ys=witness['column_order'];signs={int(k):v for k,v in witness['kernel'].items()}
    seeds=[g.ONE,(g.Q(0),g.Q(1)),g.ALPHA,(g.Q(1),g.Q(1)),(g.Q(1),g.Q(-1)),g.BETA]
    checks=[]
    for a in seeds:
        for b in seeds:
            ratio=g.mul(b,inverse(a));kernel={t:g.scale(g.mul(a,power(ratio,t)),z) for t,z in signs.items()}
            rows=[g.scale(kernel[i],(-1)**((xs[i]&ys[0]).bit_count()%2)) for i in range(d)]
            cols=[g.mul(kernel[-j],inverse(g.scale(rows[0],(-1)**((xs[0]&ys[j]).bit_count()%2)))) for j in range(d)]
            if any(g.scale(g.mul(rows[i],cols[j]),(-1)**((xs[i]&ys[j]).bit_count()%2))!=kernel[i-j] for i in range(d) for j in range(d)):
                raise ValueError('Gaussian-dyadic nonunit gauge reconstruction failed')
            if any(z.denominator & (z.denominator-1) for value in list(rows)+list(cols)+list(kernel.values()) for z in value):
                raise ValueError('Selected Gaussian unit gauges left the dyadic ring')
            wraps={g.mul(kernel[i],inverse(kernel[i-d])) for i in range(1,d)}
            if len(wraps)!=1:raise ValueError('General gauge does not preserve a uniform shift unit')
            checks.append(dict(kernel_seed_zero=g.text_complex(a),kernel_seed_one=g.text_complex(b),
                               cyclic_shift_wrap_unit=g.text_complex(wraps.pop())))
    return checks


def toeplitz_scan(n):
    started=time.monotonic();d=1<<n;orders=sorted({canonical_order((0,)+p,n) for p in permutations(range(1,d))})
    columns=[(0,)+p for p in permutations(range(1,d))];count=0;hits=0;witnesses=[];digest=sha256()
    for xs in orders:
        for ys in columns:
            witness=gauge_test(xs,ys,n);count+=1
            if witness:
                hits+=1
                if len(witnesses)<4:
                    witness['Gaussian_dyadic_unit_gauge_controls']=dyadic_unit_gauges(witness,n);witnesses.append(witness)
            digest.update(bytes((int(witness is not None),)))
    if bool(hits)!=(n<=2):raise ValueError('Finite same-size Toeplitz scan contradicts declared small-size obstruction')
    return dict(status='EXACT FINITE TOEPLITZ GAUGE SCAN PASS',active_bits=n,dimension=d,
                canonical_row_orders=len(orders),all_column_orders=len(columns),representative_cases=count,
                Toeplitz_gauge_hits=hits,witnesses=witnesses,decision_sha256=digest.hexdigest(),seconds=time.monotonic()-started,
                scope='Complete n<=3 arbitrary permutation/sign-gauge screen modulo row/column translations and simultaneous dual linear maps. General nonzero diagonal gauges reduce to this sign cross-ratio criterion. No larger padded embedding is excluded.')


def all_linear(n):
    def descend(columns):
        if len(columns)==n:
            yield tuple(columns);return
        for x in range(1,1<<n):
            if len(basis(tuple(columns)+(x,),n))>len(columns):yield from descend(columns+[x])
    yield from descend([])


def affine_cycles(n):
    started=time.monotonic();d=1<<n;count=0;hist=Counter();full=0;two_power=0;digest=sha256()
    for A in all_linear(n):
        linear=[image(A,x) for x in range(d)]
        for translation in range(d):
            mapping=[x^translation for x in linear];seen=set();cycles=[]
            for x in range(d):
                if x in seen:continue
                y=x;length=0
                while y not in seen:seen.add(y);length+=1;y=mapping[y]
                cycles.append(length)
            order=1
            for length in cycles:order=lcm(order,length)
            hist[order]+=1;count+=1;full+=int(cycles==[d])
            if not order&(order-1):two_power=max(two_power,order)
            digest.update(f'{A},{translation}:{cycles};'.encode())
    expected=d
    for j in range(n):expected*=d-(1<<j)
    theoretical=1<<(n.bit_length()) # smallest power of two >= n+1
    if count!=expected or two_power>theoretical or full!=(1 if n==1 else 6 if n==2 else 0):
        raise ValueError('Complete affine-cycle/order control failed')
    return dict(status='EXACT FINITE AFFINE CYCLE SCAN PASS',active_bits=n,dimension=d,
                all_affine_maps=count,full_dimension_cycles=full,order_histogram=dict(sorted(hist.items())),
                maximum_power_of_two_order=two_power,homogeneous_unipotent_order_bound=theoretical,
                result_sha256=digest.hexdigest(),seconds=time.monotonic()-started,
                scope='All invertible binary affine address maps enumerated. Absence of a full cycle supports the separate monomial-automorphism proof; arbitrary padded/nonmonomial algorithms are outside it.')


def padding_probe(n):
    started=time.monotonic();d=1<<n;A=g.tensor_c(n);kernel=[g.ZERO]*(d*d)
    for a in range(d):
        for b in range(d):kernel[a+d*(d-1-b)]=A[a][b]
    inputs=[d*b for b in range(d)];outputs=[d*(d-1)+a for a in range(d)]
    digest=sha256();entries=0
    for source,pos in enumerate(inputs):
        # Ordinary polynomial convolution, with zero padded input coefficients.
        product=[g.ZERO]*(2*d*d-d)
        for k,z in enumerate(kernel):product[pos+k]=z
        for a,out in enumerate(outputs):
            if product[out]!=A[a][source]:raise ValueError('Padded one-convolution embedding failed a source column')
            digest.update(json.dumps([a,source,g.text_complex(product[out])],separators=(',',':')).encode());entries+=1
    return dict(status='EXACT PADDED EMBEDDING COUNTEREXAMPLE PASS',active_bits=n,dimension=d,
                input_positions=inputs,output_positions=outputs,kernel_coefficients=d*d,
                input_extent=d*(d-1)+1,convolution_product_extent=2*d*d-d,
                complete_target_coefficients=entries,source_columns=d,result_sha256=digest.hexdigest(),
                kernel_sha256=sha256(json.dumps([g.text_complex(z) for z in kernel]).encode()).hexdigest(),seconds=time.monotonic()-started,
                scope='Exact clean polynomial linear embedding with quadratic address expansion. It disproves extrapolation of the same-size obstruction to arbitrary padding. Clean zeros, extraction, coefficient encoding, dirty restoration and native multiplication costs are not certified.')


def task(spec):
    kind,n=spec
    return toeplitz_scan(n) if kind=='Toeplitz' else affine_cycles(n) if kind=='affine' else padding_probe(n)


def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output',type=Path,required=True)
    a.add_argument('--workers',type=int,default=4);args=a.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(g.__file__),Path(__file__).with_name('lagrangian_graph_completion.py')]
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in sources}
    specs=[('Toeplitz',2),('Toeplitz',3),('affine',4),('padding',3)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,specs=specs,seed=None,
                  source_sha256={p.name:v for p,v in hashes.items()},method='Exact permutation quotient, gauge-free adjacent minors, complete affine maps, complete polynomial source columns')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');cases=[]
    # The smallest cyclic/negacyclic Gaussian gauge case is an additional cheap control.
    cases.append(toeplitz_scan(1))
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(task,spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();cases.append(result)
            print(json.dumps({k:result[k] for k in ('status','active_bits','dimension','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=v for p,v in hashes.items()):raise ValueError('Effective source changed during run')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=cases),indent=2)+'\n')


if __name__=='__main__':main()
