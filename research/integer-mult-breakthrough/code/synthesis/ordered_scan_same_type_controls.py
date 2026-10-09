#!/usr/bin/env python3
"""Separate f=2 same-type controls for the two one-bank scan model.

Exact zero-pattern obstructions are certificates. A bounded rational gauge
search on the surviving kernels is discovery only; no unseen gauge is excluded.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import time

import ordered_scan_products as S


def dyadic_unit(value):
    value = Q(value)
    numerator, denominator = abs(value.numerator), value.denominator
    return bool(numerator) and numerator & (numerator-1) == 0 and denominator & (denominator-1) == 0


def probe_order(first_order):
    started = time.monotonic()
    target, rows = S.zeta(2), []
    for second_order in permutations(range(4)):
        for kind in ('prefix', 'difference'):
            first, second = S.ordered_scan(first_order, kind), S.ordered_scan(second_order, kind)
            evidence, tensor, nullspace = S.zero_pattern(first, second, target)
            row = dict(first_order=first_order, second_order=second_order, kinds=[kind,kind], **evidence)
            if evidence['status'] != 'EXACT ZERO-PATTERN OBSTRUCTION':
                found = None
                for coefficients in product((-2,-1,1,2), repeat=len(nullspace)):
                    middle = tuple(sum(c*direction[k] for c,direction in zip(coefficients,nullspace)) for k in range(4))
                    if not all(middle):
                        continue
                    gauges = S.gauged_zeta(S.evaluate(tensor,middle), target)
                    if gauges is not None:
                        found = dict(middle=S.R.encoded([middle])[0], row=S.R.encoded([gauges[0]])[0],
                                     column=S.R.encoded([gauges[1]])[0],
                                     all_invertible_dyadic_units=all(dyadic_unit(x) for x in middle+gauges[0]+gauges[1]))
                        break
                row.update(status='EXACT RATIONAL GAUGE FACTORIZATION' if found else 'UNRESOLVED GAUGE COMPATIBILITY',
                           witness_gauges=found, bounded_discovery_coefficient_values=[-2,-1,1,2])
            rows.append(row)
    return dict(first_order=first_order, rows=rows, seconds=time.monotonic()-started)


def one_axis_positive():
    L = S.ordered_scan((0,1),'prefix')
    matrix = S.multiply(L,L)
    target = S.zeta(1)
    row_inverse, column_inverse = (Q(1),Q(1,2)), (Q(1),Q(2))
    repaired = tuple(tuple(row_inverse[i]*matrix[i][j]*column_inverse[j] for j in range(2)) for i in range(2))
    if repaired != target:
        raise AssertionError('The literal one-axis positive control failed')
    if dyadic_unit(0) or dyadic_unit(Q(3,2)) or not dyadic_unit(Q(-1,4)):
        raise AssertionError('The invertible dyadic scalar domain control failed')
    return dict(status='EXACT ONE-AXIS TWO-PREFIX POSITIVE CONTROL',
                row_inverse=S.R.encoded([row_inverse])[0], column_inverse=S.R.encoded([column_inverse])[0],
                all_diagonals_invertible_dyadic_units=True,
                negative_controls=['zero_scalar_unit', 'odd_norm_scalar_unit'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.workers<1:
        raise ValueError('Positive workers required')
    sources=(Path(__file__).resolve(),Path(S.__file__).resolve(),Path(S.R.__file__).resolve())
    hashes={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'protocol.json').write_text(json.dumps(dict(started_utc=datetime.now(timezone.utc).isoformat(),
        source_closure=hashes,workers=args.workers,f=2,stdlib_only=True,
        complete_orders=24,nonzero_invertible_external_and_middle_diagonals=True,
        unresolved_nonlinear_gauges_are_not_excluded=True,native_or_supplier_claim=False),indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        groups=list(pool.map(probe_order,permutations(range(4))))
    control=one_axis_positive()
    rows=[r for g in groups for r in g['rows']]
    counts=dict(Counter(r['status'] for r in rows))
    if hashes!={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}:
        raise AssertionError('The source closure changed')
    certificate=dict(status='PASS SAME-TYPE TWO-SCAN NECESSARY CONTROLS',counts=counts,
                     complete_order_cases=len(rows),positive=control,groups=groups)
    (args.output/'certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps(dict(status=certificate['status'],counts=counts,complete_order_cases=len(rows)),sort_keys=True))


if __name__=='__main__':
    main()
