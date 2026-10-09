#!/usr/bin/env python3
"""Bounded exact replay of the two-scan characteristic-zero obstruction.

For f=2 the scan orders are complete and target labels fixed; outside row
and column gauges are invertible diagonals. All-size f>=3 proofs separately
allow outside permutations. No native or borrowed-bank theorem is checked.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import permutations, combinations_with_replacement
import json
from pathlib import Path

import ordered_scan_products as S
import ordered_scan_same_type_controls as T


def quadratic(a,b):
    return tuple(a[i]*b[j]+(a[j]*b[i] if i!=j else 0)
                 for i,j in combinations_with_replacement(range(len(a)),2))


def survivor_minor(first_order, second_order):
    if first_order!=second_order or tuple(first_order) not in ((0,1,2,3),(0,2,1,3)):
        raise ValueError('The exact survivor identity is restricted to the two retained topological orders')
    target=S.zeta(2)
    L=S.ordered_scan(first_order,'prefix')
    evidence,tensor,nullspace=S.zero_pattern(L,L,target)
    if evidence['status']!='ZERO-PATTERN NECESSARY TEST SURVIVES' or len(nullspace)!=3:
        raise AssertionError('The exact survivor kernel changed')
    zero,one,two,three=first_order
    response=lambda i,j:S.response(tensor[i][j],nullspace)
    left=quadratic(response(one,zero),response(three,one))
    right=quadratic(response(one,one),response(three,zero))
    forced=quadratic(response(zero,zero),response(three,two))
    if tuple(a-b for a,b in zip(left,right))!=forced:
        raise AssertionError('The exact gauge minor factorization failed')
    if not target[three][two] or not any(response(zero,zero)) or not any(response(three,two)):
        raise AssertionError('The required nonzero factors disappeared')
    # Flip the sign of the required factor as a symbolic corruption control.
    if tuple(a-b for a,b in zip(left,right))==tuple(-x for x in forced):
        raise AssertionError('A corrupt survivor identity was accepted')
    return dict(first_order=first_order, nullspace_dimension=3,
                exact_identity='required all-one minor = M[0,0] * M[3,second singleton]',
                factorized_polynomial=S.R.encoded([forced])[0],
                invertible_diagonal_gauges_cannot_repair=True)


def probe():
    target=S.zeta(2)
    counts=Counter()
    survivors=[]
    for first_order in permutations(range(4)):
        for second_order in permutations(range(4)):
            for first_kind in ('prefix','difference'):
                for second_kind in ('prefix','difference'):
                    first=S.ordered_scan(first_order,first_kind)
                    second=S.ordered_scan(second_order,second_kind)
                    evidence,tensor,nullspace=S.zero_pattern(first,second,target)
                    constraints=[tensor[i][j] for i in range(4) for j in range(4) if not target[i][j]]
                    if any(sum(a*b for a,b in zip(row,direction)) for row in constraints for direction in nullspace):
                        raise AssertionError('The exact nullspace fails an original zero equation')
                    if evidence['status']=='EXACT ZERO-PATTERN OBSTRUCTION':
                        if evidence['reason']=='forced_zero_middle_diagonal':
                            k,=evidence['witness']
                            if any(direction[k] for direction in nullspace):
                                raise AssertionError('The claimed forced-zero diagonal is unsupported')
                        else:
                            i,j=evidence['witness']
                            if not target[i][j] or any(S.response(tensor[i][j],nullspace)):
                                raise AssertionError('The claimed forced-zero target entry is unsupported')
                        counts[evidence['reason']]+=1
                    else:
                        if (first_kind,second_kind)!=('prefix','prefix'):
                            raise AssertionError('An unproved mixed/difference case survived')
                        survivors.append(survivor_minor(first_order,second_order))
                        counts['exact_nonzero_gauge_minor_contradiction']+=1
    if dict(counts)!={'forced_zero_required_target_entry':58,'forced_zero_middle_diagonal':2244,
                     'exact_nonzero_gauge_minor_contradiction':2}:
        raise AssertionError('The complete fixed-label order census changed')
    controls=S.structural_controls()
    positive=T.one_axis_positive()
    return dict(status='PASS COMPLETE TWO-SCAN ALGEBRAIC CONTROLS',
                f2_complete_cases=2304, exact_obstruction_counts=dict(counts),
                symbolic_survivors=survivors, f1_positive=positive,
                structural_controls=controls,
                scope='Fixed-label f2 invertible diagonal gauge model; f>=3 analytical support proof, no native/dirty projection')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('A fresh optional output is required')
    sources=(Path(__file__).resolve(),Path(S.__file__).resolve(),Path(T.__file__).resolve(),Path(S.R.__file__).resolve())
    before={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}
    receipt=probe()
    if before!={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}:
        raise AssertionError('The exact verification source closure changed')
    receipt.update(verified_utc=datetime.now(timezone.utc).isoformat(),source_closure=before,stdlib_only=True)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'])


if __name__=='__main__':
    main()
