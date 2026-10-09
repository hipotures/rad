#!/usr/bin/env python3
"""Exact rational row spaces from arbitrary integer row order.

Primitive fraction-free elimination clears every pivot before constructing
the nullspace. No modular rank assumptions or sampled primes are used.
"""
from functools import lru_cache
from math import gcd,lcm


def need(ok,message):
    if not ok:raise ValueError(message)


def primitive(row):
    divisor=0
    for value in row:divisor=gcd(divisor,abs(value))
    if not divisor:return tuple(row)
    sign=1 if next(x for x in row if x)>0 else -1
    return tuple(sign*x//divisor for x in row)


@lru_cache(maxsize=60000)
def reduce_rows(rows,h):
    pivots={}
    for original in rows:
        need(len(original)==h and all(type(x)is int for x in original),'integer row domain')
        row=primitive(original)
        while any(row):
            pivot=next(i for i,x in enumerate(row) if x)
            if pivot not in pivots:break
            old=pivots[pivot];row=primitive(tuple(old[pivot]*x-row[pivot]*y for x,y in zip(row,old)))
        if not any(row):continue
        # Existing pivots can occur to the right of the new leading pivot.
        # They must be eliminated from the new row too; otherwise the direct
        # free-coordinate nullspace formula would not apply to that row.
        for later in sorted(pivots):
            if later>pivot and row[later]:
                old=pivots[later];row=primitive(tuple(old[later]*x-row[later]*y for x,y in zip(row,old)))
        for old_pivot,old in list(pivots.items()):
            if old[pivot]:pivots[old_pivot]=primitive(tuple(row[pivot]*x-old[pivot]*y for x,y in zip(old,row)))
        pivots[pivot]=row
    result=tuple(pivots[p] for p in sorted(pivots))
    need(all(row[p]==0 for row in result for p in pivots if p!=next(i for i,x in enumerate(row) if x)),
         'exact reduced pivot columns')
    return result


@lru_cache(maxsize=60000)
def nullspace(rows,h):
    rows=reduce_rows(rows,h);pivots=[next(i for i,x in enumerate(row) if x) for row in rows];result=[]
    for free in range(h):
        if free in pivots:continue
        denominator=1
        for row,pivot in zip(rows,pivots):
            if row[free]:denominator=lcm(denominator,abs(row[pivot]))
        vector=[0]*h;vector[free]=denominator
        for row,pivot in zip(rows,pivots):vector[pivot]=-row[free]*denominator//row[pivot]
        result.append(primitive(vector))
    result=reduce_rows(tuple(result),h)
    need(len(result)+len(rows)==h and all(sum(a*b for a,b in zip(row,vector))==0 for row in rows for vector in result),
         'exact nullspace rank and annihilation')
    return result
