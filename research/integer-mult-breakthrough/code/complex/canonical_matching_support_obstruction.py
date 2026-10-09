#!/usr/bin/env python3
"""Import-free exact support obstruction for canonical matched-pair kernels.

For A_M=alpha I+beta M and canonical F=C_full, a single C^(h-1) child
between monomial/diagonal wrappers requires all matching differences to be
one fixed odd translation. The proof uses support blocks and remains valid
under tensor columns and arbitrary entangled monomial wrappers.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time


UNITS = ((1,0),(0,1),(-1,0),(0,-1))


def multiply(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def power_alpha_numerator(n):
    result = (1,0)
    for _ in range(n):
        result = multiply(result,(1,1))
    return result


def kernel_numerator(n,x,y,mate):
    alpha = power_alpha_numerator(n)
    a = multiply(multiply(alpha,UNITS[-(y^x).bit_count() % 4]),(1,-1))
    b = multiply(multiply(alpha,UNITS[-(y^mate).bit_count() % 4]),(1,1))
    return a[0]+b[0],a[1]+b[1]


def support_formula(x,y,mate):
    difference = x^mate
    weight = difference.bit_count()
    return not weight & 1 or ((y&difference).bit_count() & 1)==(
        ((x&difference).bit_count()+((weight-1)//2)) & 1)


def matchings(remaining):
    if not remaining:
        yield ()
        return
    a = remaining[0]
    for j in range(1,len(remaining)):
        b = remaining[j]
        for rest in matchings(remaining[1:j]+remaining[j+1:]):
            yield ((a,b),)+rest


def mapping(pairs,size):
    result = [-1]*size
    for a,b in pairs:
        result[a],result[b] = b,a
    if any(v<0 for v in result) or any(result[result[x]]!=x or result[x]==x for x in range(size)):
        raise AssertionError('input is not a complete fixed-point-free matching')
    return result


def test_matching(n,pairs):
    size = 1 << n
    M = mapping(pairs,size)
    columns = []
    for x,mate in enumerate(M):
        support = 0
        for y in range(size):
            nonzero = kernel_numerator(n,x,y,mate)!=(0,0)
            if nonzero != support_formula(x,y,mate):
                raise AssertionError('literal Gaussian cancellation disagrees with the hyperplane formula')
            if nonzero:
                support |= 1 << y
        columns.append(support)
    q = 1 << (n-1)
    blocks = set(columns)
    necessary = (all(v.bit_count()==q for v in columns) and len(blocks)==2
                 and not (next(iter(blocks)) & next(v for v in blocks if v!=next(iter(blocks)))))
    differences = {x^mate for x,mate in enumerate(M)}
    translated = len(differences)==1 and next(iter(differences)).bit_count() & 1
    if bool(necessary)!=bool(translated):
        raise AssertionError('necessary complete support blocks admit a nonlinear matching')
    return dict(pairs=[list(p) for p in pairs],support_block_necessary=bool(necessary),
                fixed_odd_translation=next(iter(differences)) if translated else None,
                all_columns_halfsize=all(v.bit_count()==q for v in columns),
                column_masks=columns)


def small_probe(n):
    if n==3:
        cases = [test_matching(n,pairs) for pairs in matchings(tuple(range(8)))]
    else:
        size = 1 << n
        even = [x for x in range(size) if not x.bit_count() & 1]
        odd = [x for x in range(size) if x.bit_count() & 1]
        rng = Random(202610090418)
        samples = []
        for _ in range(24):
            shuffled = odd[:]
            rng.shuffle(shuffled)
            samples.append(tuple(zip(even,shuffled)))
        for delta in range(1,size):
            if delta.bit_count() & 1:
                samples.append(tuple((x,x^delta) for x in range(size) if x<(x^delta)))
        cases = [test_matching(n,pairs) for pairs in samples]
    return dict(kind='complete-literal-Gaussian-supports',n=n,matchings=len(cases),
                support_block_passes=sum(c['support_block_necessary'] for c in cases),
                complete_column_entries=len(cases)*(1 << (2*n)),cases=cases,
                scope='All105 matchings only at n3; n4 is a seeded sample plus all odd translations.')


def implicit_mate(n,x):
    c = (1 << (n-1))|2
    special = {0:c^1,c^1:0,1:c,c:1}
    return special.get(x,x^1)


def large_probe(n):
    # Replace two translation pairs by two crossed pairs. All differences
    # remain odd, but some normals are1 and others are c xor1 of weight3.
    rng = Random(202610090418+n)
    samples = 512
    for j in range(samples):
        x = (0,1,2,(1 << (n-1))|2)[j % 4] if j<32 else rng.getrandbits(n)
        y = rng.getrandbits(n)
        if (kernel_numerator(n,x,y,implicit_mate(n,x))!=(0,0)) != support_formula(x,y,implicit_mate(n,x)):
            raise AssertionError('large exact Gaussian support formula failed')
    # These three rows prove two column neighborhoods overlap and differ.
    first,second = 0,2
    witnesses = []
    for y,expected in ((2,(True,True)),(1,(True,False)),(0,(False,True))):
        observed = tuple(kernel_numerator(n,x,y,implicit_mate(n,x))!=(0,0) for x in (first,second))
        if observed!=expected:
            raise AssertionError('partial-overlap support witness failed')
        witnesses.append(dict(row=y,column_support_membership=list(observed)))
    return dict(kind='large-implicit-nonlinear-matching-witness',n=n,exact_gaussian_samples=samples,
                column_labels=[first,second],row_witnesses=witnesses,
                full_matching_formula='Start x xor1; replace pairs(0,1),(c,c xor1) by(0,c xor1),(1,c), c=2^(n-1) xor2.',
                tensor_extension='For any positive f, fix identical other-column labels and tensor the three witnesses with any nonzero spectator output. Partial overlap persists, forbidding disjoint complete blocks.',
                full_address_arrays=False)


def dispatch(task):
    return small_probe(task) if task in (3,4) else large_probe(task)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive worker count required')
    before = sha256(Path(__file__).read_bytes()).hexdigest()
    utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [3] if args.bounded else [3,4,16,64]
    if args.workers == 1:
        cases = [dispatch(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(dispatch,tasks))
    if sha256(Path(__file__).read_bytes()).hexdigest()!=before:
        raise AssertionError('source changed during execution')
    result = dict(status='PASS EXACT CANONICAL MATCHING SUPPORT OBSTRUCTION',started_utc=utc,
                  completed_utc=datetime.now(timezone.utc).isoformat(),source_sha256=before,
                  workers=args.workers,bounded=args.bounded,cases=cases,seconds=time.monotonic()-started,
                  theorem='For any dimension h and fixed-point-free matching M, F*A_M^-1 can be a single C^(h-1) between invertible monomial/diagonal wrappers only if M is an odd translation. The support necessity survives tensor columns.',
                  scope='Canonical full F, matched-pair A_M, one child. Multiple children, altered product/output representation, new helpers and changed canonical endpoints are not excluded.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(cases),seconds=result['seconds'])),flush=True)


if __name__ == '__main__':
    main()
