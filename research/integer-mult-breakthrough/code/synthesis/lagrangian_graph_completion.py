#!/usr/bin/env python3
"""Independent graph-completion lemma and a strict chart-boundary witness.

All algebra is over GF(2). A Lagrangian is an isotropic n-dimensional
subspace of the (x,y) symplectic space. This proves an abstract finite
rank-metric result, not a scalar circuit, dirty wrapper or tape transfer.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import time


def basis(vectors,bits):
    rows=list(vectors);r=0
    for column in range(bits):
        pivot=next((i for i in range(r,len(rows)) if rows[i]>>column&1),None)
        if pivot is None:continue
        rows[r],rows[pivot]=rows[pivot],rows[r]
        for i in range(len(rows)):
            if i!=r and rows[i]>>column&1:rows[i]^=rows[r]
        r+=1
    return tuple(rows[:r])


def image(columns,value):
    result=0
    for j,v in enumerate(columns):
        if value>>j&1:result^=v
    return result


def solve(columns,value):
    pivots={}
    for j,vector in enumerate(columns):
        coefficients=1<<j
        while vector:
            bit=vector.bit_length()-1
            if bit not in pivots:
                pivots[bit]=(vector,coefficients);break
            a,c=pivots[bit];vector^=a;coefficients^=c
        if not vector:raise ValueError('Coordinate columns are dependent')
    answer=0
    while value:
        bit=value.bit_length()-1
        if bit not in pivots:raise ValueError('Vector is outside the column span')
        a,c=pivots[bit];value^=a;answer^=c
    return answer


def intersection(left,right,bits):
    left=basis(left,bits);right=basis(right,bits);pivots={};relations=[]
    for j,vector in enumerate(left+right):
        coefficients=1<<j
        while vector:
            bit=vector.bit_length()-1
            if bit not in pivots:
                pivots[bit]=(vector,coefficients);break
            a,c=pivots[bit];vector^=a;coefficients^=c
        if not vector:relations.append(image(left,coefficients&((1<<len(left))-1)))
    result=basis(relations,bits)
    if len(result)!=len(left)+len(right)-len(basis(left+right,bits)):
        raise ValueError('Intersection failed the exact dimension identity')
    return result


def parity(a,b):return (a&b).bit_count()%2


def pairing(a,b,n):
    mask=(1<<n)-1
    return parity(a&mask,b>>n)^parity(a>>n,b&mask)


def require_isotropic(rows,n):
    if any(pairing(a,b,n) for a in rows for b in rows):
        raise ValueError('The proposed partial Lagrangian is not isotropic')


def symmetric_columns(n,code):
    columns=[0]*n;k=0
    for i in range(n):
        for j in range(i,n):
            if code>>k&1:columns[i]^=1<<j;columns[j]^=(1<<i) if i!=j else 0
            k+=1
    return tuple(columns)


def graph(columns):
    n=len(columns)
    if any((columns[i]>>j&1)!=(columns[j]>>i&1) for i in range(n) for j in range(n)):
        raise ValueError('Graph matrix is not symmetric')
    return basis(((1<<j)|(v<<n) for j,v in enumerate(columns)),2*n)


def complete_graph(partial,n):
    """Extend an isotropic subspace transverse to vertical to a graph."""
    partial=basis(partial,2*n);require_isotropic(partial,n);r=len(partial)
    mask=(1<<n)-1;xs=tuple(v&mask for v in partial);ys=tuple(v>>n for v in partial)
    if len(basis(xs,n))!=r:
        raise ValueError('Partial subspace contains a nonzero vertical vector')
    columns=list(xs)
    for j in range(n):
        if len(columns)==n:break
        if len(basis(columns+[1<<j],n))>len(columns):columns.append(1<<j)
    if len(columns)!=n:raise ValueError('Failed to extend the coordinate basis')
    # In the basis T, the first r columns of C=T^T B T are prescribed.
    c=[sum(parity(t,y)<<j for j,t in enumerate(columns)) for y in ys]
    for j in range(r,n):c.append(sum(((c[i]>>j)&1)<<i for i in range(r)))
    if any((c[i]>>j&1)!=(c[j]>>i&1) for i in range(n) for j in range(n)):
        raise ValueError('Isotropic partial map did not have a symmetric extension')
    transpose=tuple(sum(((columns[i]>>j)&1)<<i for i in range(n)) for j in range(n))
    b=tuple(solve(transpose,image(c,solve(columns,1<<j))) for j in range(n))
    if any(image(b,x)!=y for x,y in zip(xs,ys)):
        raise ValueError('Completed graph lost an original partial vector')
    result=graph(b)
    if len(intersection(partial,result,2*n))!=r:
        raise ValueError('Completed graph does not contain the original partial space')
    return b,result


def distance(left,right,n):
    return n-len(intersection(left,right,2*n))


def vertical_part(rows,n):
    return intersection(rows,tuple(1<<(n+j) for j in range(n)),2*n)


def random_lagrangian(n,rng):
    rows=[1<<j for j in range(n)]
    for _ in range(20*n):
        gate=rng.randrange(3);a=rng.randrange(n)
        if gate==0:
            rows=[v^((1<<a)|(1<<(n+a))) if ((v>>a)^(v>>(n+a)))&1 else v for v in rows]
        elif gate==1:rows=[v^((1<<(n+a)) if v>>a&1 else 0) for v in rows]
        else:
            b=(a+1+rng.randrange(n-1))%n
            rows=[v^((1<<b) if v>>a&1 else 0)^((1<<(n+a)) if v>>(n+b)&1 else 0) for v in rows]
    result=basis(rows,2*n);require_isotropic(result,n)
    if len(result)!=n:raise ValueError('Symplectic word lost Lagrangian dimension')
    return result


def completion_cases(n,samples,seed):
    rng=random.Random(seed);digest=sha256();partial_count=0;median_extensions=0;vertical_obstructions=0
    for _ in range(samples):
        b=symmetric_columns(n,rng.randrange(1<<(n*(n+1)//2)))
        parent=graph(b);r=rng.randrange(n+1)
        coefficients=[]
        while len(coefficients)<r:
            candidate=rng.randrange(1<<n)
            if len(basis(coefficients+[candidate],n))>len(coefficients):coefficients.append(candidate)
        partial=tuple(image(parent,c) for c in coefficients)
        completed,g=complete_graph(partial,n)
        digest.update(json.dumps([partial,completed],separators=(',',':')).encode());partial_count+=1
        # Independently test the median criterion on random full frames.
        if n<=5:
            lag=random_lagrangian(n,rng)
            terminals=[graph(symmetric_columns(n,rng.randrange(1<<(n*(n+1)//2)))) for _ in range(4)]
            pieces=[intersection(lag,t,2*n) for t in terminals]
            joint=basis(tuple(v for part in pieces for v in part),2*n)
            vertical=vertical_part(joint,n)
            if vertical:vertical_obstructions+=1
            else:
                _,candidate=complete_graph(joint,n)
                before=[distance(lag,t,n) for t in terminals];after=[distance(candidate,t,n) for t in terminals]
                if any(b>a for a,b in zip(before,after)):
                    raise ValueError('Transverse-intersection completion increased a terminal distance')
                median_extensions+=1
                digest.update(json.dumps([before,after],separators=(',',':')).encode())
    negatives=[]
    for name,partial in [('vertical',((1<<n),)),('nonisotropic',(1,1<<n))]:
        try:complete_graph(partial,n)
        except ValueError as error:negatives.append(dict(name=name,rejection=str(error)))
        else:raise ValueError('Invalid graph completion was accepted')
    return dict(n=n,samples=samples,seed=seed,exact_partial_extensions=partial_count,
                random_median_graph_extensions=median_extensions,
                joint_intersection_vertical_obstructions=vertical_obstructions,
                negative_controls=negatives,result_sha256=digest.hexdigest())


def four_terminal_witness():
    n=3;codes=(3,23,35,56);terminals=[graph(symmetric_columns(n,c)) for c in codes]
    lag=basis((32,19,10),2*n);require_isotropic(lag,n)
    pieces=[intersection(lag,t,2*n) for t in terminals]
    joint=basis(tuple(v for part in pieces for v in part),2*n);vertical=vertical_part(joint,n)
    if vertical!=(32,):raise ValueError('Expected jointly generated vertical direction is absent')
    try:complete_graph(joint,n)
    except ValueError:pass
    else:raise ValueError('Strict-gap witness was incorrectly completed inside the graph chart')
    graph_costs=[sum(distance(graph(symmetric_columns(n,c)),t,n) for t in terminals) for c in range(64)]
    # Independent exhaustive isotropic-subspace enumeration: every basis
    # is among the triples of the 63 nonzero six-dimensional vectors.
    lags=set()
    for a,b,c in combinations(range(1,1<<(2*n)),3):
        if pairing(a,b,n) or pairing(a,c,n) or pairing(b,c,n):continue
        candidate=basis((a,b,c),2*n)
        if len(candidate)==n:lags.add(candidate)
    full_costs=[sum(distance(candidate,t,n) for t in terminals) for candidate in sorted(lags)]
    if len(lags)!=135 or min(graph_costs)!=6 or min(full_costs)!=5:
        raise ValueError('Independent complete finite median optimum failed')
    return dict(n=n,terminal_graph_codes=codes,terminal_bases=terminals,
                nongraph_median_basis=lag,distances=[distance(lag,t,n) for t in terminals],
                intersection_bases=pieces,joint_intersection_basis=joint,
                jointly_generated_vertical_basis=vertical,
                graph_median_optimum=min(graph_costs),full_lagrangian_median_optimum=min(full_costs),
                enumerated_graph_frames=len(graph_costs),enumerated_lagrangians=len(lags),
                graph_cost_histogram={c:graph_costs.count(c) for c in sorted(set(graph_costs))},
                full_cost_histogram={c:full_costs.count(c) for c in sorted(set(full_costs))},
                scope='Complete finite unweighted four-terminal rank metric only. No scalar gate, endpoint maps, dirty restoration, complex precision or integer-multiplication transfer is established.')


def probe(spec):
    if spec[0]=='witness':return dict(kind='four-terminal-witness',result=four_terminal_witness())
    _,n,samples,seed=spec
    return dict(kind='graph-completion',result=completion_cases(n,samples,seed))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',required=True,type=Path);ap.add_argument('--workers',type=int,default=4)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    specs=[('completion',4,512,202610082209),('completion',5,512,202610082210),
           ('completion',16,512,202610082211),('witness',)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
                  native_threads_each=1,specs=specs,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  witness_origin='Complex track Lagrangian median screen; independently replayed from supplied integer bases and symmetric graph codes without importing its code')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    start=time.monotonic();receipts=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();receipts.append(result)
            print(json.dumps(dict(kind=result['kind'],n=result['result']['n'],status='EXACT GRAPH COMPLETION AND CHART-BOUNDARY WITNESS PASS',seconds=time.monotonic()-start)),flush=True)
    certificate=dict(status='EXACT GRAPH COMPLETION AND CHART-BOUNDARY WITNESS PASS',cases=receipts,
                     seconds=time.monotonic()-start,
                     claim='If the sum of median/terminal intersections is transverse to vertical, one symmetric graph preserves every intersection and is no worse. Thus a strict full-Lagrangian improvement requires a jointly generated vertical direction. The supplied n3 four-terminal witness has exact full/graph optima5/6.')
    (args.output/'certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')


if __name__=='__main__':main()
