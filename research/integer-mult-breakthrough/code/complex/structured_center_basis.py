#!/usr/bin/env python3
"""Construct a power-of-two pivot minor for mixed five-subset centers.

An explicit block-triangular minor gives all-h Gaussian-dyadic basis existence.
This is a scalar change of coordinates; arbitrary-dirty implementation and paid
address-frame chronology are intentionally not inferred from its determinant.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
from time import perf_counter

from center_null_basis import identity, multiply, dyadic


def feature(pair, source):
    incidence = int(set(pair) <= set(source))
    return 1-incidence if pair in ((0,1),(0,2)) else incidence


def inverse_square(matrix):
    n = len(matrix)
    a = [[Fraction(x) for x in row] + list(map(Fraction, unit))
         for row, unit in zip(matrix, identity(n))]
    for k in range(n):
        pivot = next(i for i in range(k, n) if a[i][k])
        a[k], a[pivot] = a[pivot], a[k]
        value = a[k][k]
        a[k] = [x/value for x in a[k]]
        for i in range(n):
            if i != k and a[i][k]:
                value = a[i][k]
                a[i] = [x-value*y for x,y in zip(a[i],a[k])]
    assert [row[:n] for row in a] == identity(n)
    return [row[n:] for row in a]


def determinant(matrix):
    """Bareiss exact determinant, with only integer divisions."""
    a = [row[:] for row in matrix]
    sign, previous = 1, 1
    for k in range(len(a)-1):
        if not a[k][k]:
            i = next(i for i in range(k+1,len(a)) if a[i][k])
            a[k], a[i] = a[i], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k+1,len(a)):
            for j in range(k+1,len(a)):
                numerator = a[i][j]*pivot-a[i][k]*a[k][j]
                assert numerator % previous == 0
                a[i][j] = numerator//previous
            a[i][k] = 0
        previous = pivot
    return sign*a[-1][-1]


def new_columns(point):
    base = set(range(5))
    return [tuple(sorted((base-{j})|{point})) for j in range(5)] + [
        (0,1,2,j,point) for j in range(5,point)]


def border_inverse(point):
    # Border is [[J5-I5,U],[0,I]], U has its first three rows equal to 1.
    a = [[Fraction(int(i<5 and j<5),4)-int(i==j)
          if i<5 and j<5 else Fraction(int(i==j and i>=5))
          for j in range(point)] for i in range(point)]
    for i in range(5):
        for j in range(5,point):
            a[i][j] = Fraction(1 if i<3 else -3,4)
    return a


def build(h):
    if h < 7:
        raise ValueError("The base uses seven labels")
    pairs = [(i,j) for j in range(1,7) for i in range(j)]
    columns = list(combinations(range(7),5))
    minor = [[feature(pair,s) for s in columns] for pair in pairs]
    base_det = determinant(minor)
    assert abs(base_det) == 2**15
    inverse = inverse_square(minor)
    stages = [dict(h=7,rows=21,border_determinant=None,
                   absolute_determinant=abs(base_det))]
    for point in range(7,h):
        old = len(pairs)
        additions = new_columns(point)
        row_additions = [(i,point) for i in range(point)]
        top_right = [[feature(pair,s) for s in additions] for pair in pairs]
        bottom_left = [[feature(pair,s) for s in columns] for pair in row_additions]
        assert not any(x for row in bottom_left for x in row)
        border = [[feature(pair,s) for s in additions] for pair in row_additions]
        binv = border_inverse(point)
        assert multiply(border,binv) == identity(point)
        assert multiply(binv,border) == identity(point)
        assert determinant(border) == 4
        correction = multiply(multiply(inverse,top_right),binv)
        inverse = [row+[-x for x in correction[i]] for i,row in enumerate(inverse)] + [
            [Fraction(0)]*old+row for row in binv]
        minor = [row+top_right[i] for i,row in enumerate(minor)] + [
            [0]*old+row for row in border]
        pairs += row_additions
        columns += additions
        stages.append(dict(h=point+1,rows=len(pairs),border_determinant=4,
                           absolute_determinant=2**(2*(point+1)+1)))
    assert len(set(columns)) == len(pairs) == comb(h,2)
    assert all(len(s)==5 and tuple(sorted(s))==s for s in columns)
    assert minor == [[feature(pair,s) for s in columns] for pair in pairs]
    assert multiply(minor,inverse) == identity(len(pairs))
    assert multiply(inverse,minor) == identity(len(pairs))
    assert all(dyadic(x) for row in inverse for x in row)
    return pairs,columns,minor,inverse,stages


def run(h):
    started=perf_counter()
    pairs,columns,minor,inverse,stages=build(h)
    q,volume=len(pairs),comb(h,5)
    # The full basis in pivot/nonpivot order is [[minor,G_other],[0,I]].
    # Its exact inverse formula follows from both verified minor inverses.
    denominators=Counter(str(x.denominator) for row in inverse for x in row)
    data=lambda matrix:json.dumps(matrix,separators=(',',':'),default=str).encode()
    return dict(status='EXPLICIT DYADIC PIVOT BASIS',h=h,volume=volume,
        center_rank=q,null_dimension=volume-q,pair_order=[list(p) for p in pairs],
        pivot_sources=[list(s) for s in columns],stages=stages,
        absolute_pivot_determinant=str(2**(2*h+1)),
        pivot_nonzeros=sum(bool(x) for row in minor for x in row),
        inverse_nonzeros=sum(bool(x) for row in inverse for x in row),
        inverse_denominator_counts=dict(denominators),
        max_inverse_numerator_bits=max(abs(x.numerator).bit_length()
                                       for row in inverse for x in row),
        matrix_sha256={'minor':sha256(data(minor)).hexdigest(),
                       'inverse':sha256(data(inverse)).hexdigest()},
        checked=dict(full_left_right_pivot_inverse=True,
            every_new_border_det_four=True,lower_left_zero_blocks=True,
            entire_square_basis_formula='[[minor,G_nonpivot],[0,I]]',
            entire_inverse_formula='[[minor^-1,-minor^-1 G_nonpivot],[0,I]]'),
        elapsed_seconds=perf_counter()-started,
        scope='Constructive all-h scalar dyadic completion from a finite exact base and explicit determinant-four induction. Physical source/sink basis adapters, arbitrary dirty workspaces, reversible circuit size, precision and exponent remain unpaid.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--h',type=int,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if not 7<=a.h<=32:
        raise ValueError('Initial exact checking is bounded to 7<=h<=32')
    if a.output.exists():raise FileExistsError('Use a fresh output')
    result=run(a.h);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()
                      if k not in ('pair_order','pivot_sources','stages')}))


if __name__=='__main__':main()
