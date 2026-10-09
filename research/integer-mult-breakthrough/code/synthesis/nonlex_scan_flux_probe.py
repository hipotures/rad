#!/usr/bin/env python3
"""Exact order-path flux and a small nonlex three-scan discriminator.

An order with dense Hamming jumps escapes the lex/Gray aggregate cut bound.
The finite three-scan reduction tests real dyadic units only. Selected-orbit
layout, native scan endpoints and complete routing costs remain unsupplied.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random

import three_scan_real_dyadic_probe as P


def complement_shear(x,f):
    return x^((x&1)*((1<<f)-2))


def transitions(order,bit):
    return tuple(j for j in range(1,len(order)) if not (order[j-1]>>bit)&1 and (order[j]>>bit)&1)


def flux_controls():
    rows=[]
    rng=random.Random(20261009222)
    for f in range(1,6):
        n=1<<f
        shuffled=list(range(n))
        rng.shuffle(shuffled)
        named=[('natural',tuple(range(n))),('bit-reversal',tuple(P.bit_reverse(x,f) for x in range(n))),
               ('gray',tuple(x^(x>>1) for x in range(n))),
               ('complement-shear',tuple(complement_shear(x,f) for x in range(n))),
               ('seeded-permutation',tuple(shuffled))]
        for name,order in named:
            if sorted(order)!=list(range(n)):
                raise AssertionError('The order is not a complete address permutation')
            counts=[len(transitions(order,b)) for b in range(f)]
            total_distance=sum((a^b).bit_count() for a,b in zip(order,order[1:]))
            weight_change=order[-1].bit_count()-order[0].bit_count()
            if 2*sum(counts)!=total_distance+weight_change:
                raise AssertionError('The exact positive Hamming flux identity failed')
            for kind in ('prefix','difference'):
                matrix=P.S.ordered_scan(order,kind)
                for bit,count in enumerate(counts):
                    cut=[[matrix[i][j] for j in range(n) if not (j>>bit)&1] for i in range(n) if (i>>bit)&1]
                    if len(P.S.R.rref(cut,n//2)[1])!=count:
                        raise AssertionError('The exact scan cross-cut rank disagrees with order flux')
                    steps=transitions(order,bit)
                    minor=tuple(tuple(matrix[order[i]][order[j-1]] for j in steps) for i in steps)
                    expected=tuple(tuple(int(j<=i) if kind=='prefix' else -int(i==j) for j in range(count)) for i in range(count))
                    if minor!=expected:
                        raise AssertionError('The complete unit-minor rank witness failed')
            if name=='complement-shear':
                if any(complement_shear(complement_shear(x,f),f)!=x for x in range(n)):
                    raise AssertionError('The nonlex GF2 shear is not involutive')
                if sum(counts)!=(n*(f-1)//2+1):
                    raise AssertionError('The high-flux closed formula failed')
            rows.append(dict(f=f,name=name,order=order,cross_cut_ranks=counts,
                             sum_positive_hamming_flux=sum(counts),total_hamming_distance=total_distance,
                             target_zeta_required_total_cut_rank=f*n//2,
                             optimistic_scan_count_lower_bound=(f*n//2+sum(counts)-1)//sum(counts)))
    return dict(status='PASS EXACT ORDER-FLUX AND UNIT-MINOR CONTROLS',rows=rows,
                seed=20261009222,scope='Order support/cut ranks, not native routing or endpoint timing')


def selected_tasks():
    result=[]
    for f in (2,3):
        orders=(tuple(range(1<<f)),tuple(complement_shear(x,f) for x in range(1<<f)))
        for chosen in product(orders,repeat=3):
            for kinds in product(('prefix','difference'),repeat=3):
                result.append((f,chosen,kinds))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.workers<1:
        raise ValueError('Positive workers required')
    sources=(Path(__file__).resolve(),Path(P.__file__).resolve(),Path(P.S.__file__).resolve(),Path(P.S.R.__file__).resolve())
    hashes={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}
    args.output.mkdir(parents=True,exist_ok=False)
    selected=selected_tasks()
    (args.output/'protocol.json').write_text(json.dumps(dict(started_utc=datetime.now(timezone.utc).isoformat(),source_closure=hashes,
        workers=args.workers,stdlib_only=True,cases=len(selected),orders=['natural','complement-shear'],
        full_GF3_middle_unit_reductions=True,gaussian_units_and_native_scan_supplier_not_certified=True),indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows=list(pool.map(P.probe,selected))
    controls=flux_controls()
    if hashes!={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}:
        raise AssertionError('The source closure changed')
    counts={str(f):dict(Counter(row['status'] for row in rows if row['f']==f)) for f in (2,3)}
    receipt=dict(status='PASS HIGH-FLUX NONLEX SCAN DISCRIMINATOR',counts=counts,rows=rows,controls=controls,
                 no_asymptotic_or_native_or_exponent_claim=True)
    (args.output/'certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(status=receipt['status'],counts=counts,cases=len(rows),
                         flux_order_controls=len(controls['rows'])),sort_keys=True))


if __name__=='__main__':
    main()
