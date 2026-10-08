#!/usr/bin/env python3
"""Exact optimistic screen of the degree-two five-subset bit motif.

This retains three shear stages, h incidence-center wires, and uniform
ambient dimension r=C(h,2). It excludes that specific motif even before
charging a single side role. It is not a bound on general fitting matrices.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys
import time


def dense_control(h):
    from sympy import Matrix, QQ
    from sympy.polys.matrices import DomainMatrix
    sets = list(map(frozenset,combinations(range(h),5)))
    matrix = Matrix([[(len(s&t)-1)*(len(s&t)-3) for t in sets] for s in sets])
    rank = DomainMatrix.from_Matrix(matrix).convert_to(QQ).rank()
    assert rank == comb(h,2)
    # These complete entries independently exercise the diagonal and every
    # odd-neighbor zero required by the characteristic-two scalar correction.
    assert all(matrix[i,i] == 8 for i in range(len(sets)))
    zeros = sum(len(s&t) in (1,3) for s in sets for t in sets)
    assert all(matrix[i,j] == 0 for i,s in enumerate(sets)
               for j,t in enumerate(sets) if len(s&t) in (1,3))
    eigenspaces = [1,h-1,comb(h,2)-h]
    eigenvalues = [20*comb(h-2,3)-15*comb(h-1,4)+3*comb(h,5),
                  8*comb(h-3,3)-3*comb(h-2,4),2*comb(h-4,3)]
    assert all(x != 0 for x in eigenvalues)
    assert sum(eigenspaces) == rank
    return dict(h=h,subsets=len(sets),entries=len(sets)**2,exact_rank=rank,
                odd_neighbor_zero_entries=zeros,nonzero_eigenvalues=eigenvalues,
                nonzero_eigenspace_dimensions=eigenspaces)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--dense-h',type=int,nargs='+',default=[7,8,9])
    parser.add_argument('--accepted-bit-saving',type=Q,default=Q(3111,10**12))
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    assert 1 <= args.workers <= 16 and all(h>=7 for h in args.dense_h)
    started = time.monotonic()
    if args.workers == 1:
        controls = []
        for h in args.dense_h:
            controls.append(dense_control(h))
            args.output.parent.mkdir(parents=True,exist_ok=True)
            checkpoint = args.output.with_name(args.output.stem+'-checkpoint.json')
            checkpoint.write_text(json.dumps(dict(status='Running',dense_controls=controls),indent=2)+'\n')
            print('PASS complete rational rank control h',h,flush=True)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            controls = list(pool.map(dense_control,args.dense_h))
    rows = []
    for h in range(7,101):
        v, r = comb(h,5),comb(h,2)
        deficit_fraction = Q(v-6*h*r,v)
        assert (deficit_fraction > 0) == (h >= 24)
        rows.append(dict(h=h,v=v,r=r,normalized_bit_deficit=str(deficit_fraction)))
    # At h=5,6 the row rank is respectively1,6; the retained uniform loss
    # already exceeds N. For h>=24, r>=276 and ln(r^3)>16. Even with W=2N
    # and no side/center roles, eta<=1/(2r^3); -ln(1-eta)<=eta/(1-eta).
    r0 = comb(24,2)
    universal_scoped_upper = Q(1,16*(2*r0**3-1))
    assert r0**3 >= 2**24 and args.accepted_bit_saving > universal_scoped_upper
    value = dict(status='PASS scoped negative for the degree-two five-subset three-stage motif',
                 dense_controls=controls,rank_formula='C(h,2) for h>=7; h5=1,h6=6',
                 positivity_first_ground=24,normalized_loss='6*h*C(h,2)/C(h,5)',
                 no_side_role_optimistic_primitive_upper=str(universal_scoped_upper),
                 existing_supported_bit_saving=str(args.accepted_bit_saving),
                 strict_comparison_gap=str(args.accepted_bit_saving-universal_scoped_upper),
                 all_size_scope='Fixed fitting polynomial (j-1)(j-3), h incidence center wires, three uniform tensor shear stages; even the free-side-role bound is smaller than the existing bit primitive',
                 finite_count_controls=rows,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                 interpreter=sys.version,elapsed_seconds=time.monotonic()-started,
                 unknown='Different higher-degree fitting maps, fewer central decreases, or nonuniform networks are not excluded')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print('PASS five-subset scoped ceiling',universal_scoped_upper,'below',args.accepted_bit_saving)


if __name__ == '__main__':
    main()
