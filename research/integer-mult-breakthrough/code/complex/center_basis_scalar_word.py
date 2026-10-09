#!/usr/bin/env python3
"""Reversible scalar word for the structured dyadic center/null basis.

This uses existing data banks, without zero initialization or extra banks.
All address frames are abstracted as identical for this component. Physical
source/sink adapters and resulting native rank ledger remain unproved.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import random
from time import perf_counter

from center_null_basis import identity,multiply,smith
from structured_center_basis import build,feature


def factor_word(matrix):
    """M=U^-1 D V^-1; only dyadic scales, shears and swaps are retained."""
    diagonal,u,v,winv,operations=smith(matrix)
    n=len(matrix);word=[]
    for kind,*args in operations:
        if kind=='col_add':
            i,j,c=args;word.append(['add',j,i,Fraction(-c)])
        elif kind=='col_swap':word.append(['swap',*args])
    for i in range(n):
        d=diagonal[i][i]
        assert d and d&(d-1)==0
        if d!=1:word.append(['scale',i,Fraction(d)])
    for kind,*args in reversed(operations):
        if kind=='row_add':
            i,j,c=args;word.append(['add',i,j,Fraction(-c)])
        elif kind=='row_swap':word.append(['swap',*args])
        elif kind=='row_negate':word.append(['scale',args[0],Fraction(-1)])
    # All columns, including arbitrary dirty values, define this exact map.
    actual=[apply(word,[Fraction(int(i==j)) for i in range(n)]) for j in range(n)]
    assert list(map(list,zip(*actual)))==matrix
    return word


def apply(word,values,invert=False):
    values=values[:]
    for kind,*args in reversed(word) if invert else word:
        if kind=='add':
            i,j,c=args;values[i]+=(-c if invert else c)*values[j]
        elif kind=='scale':
            i,c=args;values[i]*=(1/c if invert else c)
        elif kind=='swap':
            i,j=args;values[i],values[j]=values[j],values[i]
        else:raise ValueError(kind)
    return values


def local_words(h):
    pairs,pivots,minor,inverse,stages=build(h)
    base=[row[:21] for row in minor[:21]]
    word0=factor_word(base)
    word5=factor_word([[int(i!=j) for j in range(5)] for i in range(5)])
    borders=[(0,21,word0)]
    offset=21
    for point in range(7,h):
        local=word5[:]+[['add',i,j,Fraction(1)]
                        for j in range(5,point) for i in range(3)]
        borders.append((offset,point,local));offset+=point
    assert offset==len(pairs)
    word=[];cross=0
    for offset,length,local in borders:
        for kind,*args in local:
            if kind=='add':
                i,j,c=args;word.append([kind,offset+i,offset+j,c])
            elif kind=='scale':
                i,c=args;word.append([kind,offset+i,c])
            else:word.append([kind,offset+args[0],offset+args[1]])
        # Future block inputs are still original. Earlier block outputs have
        # already been produced, and the lower-left entries are all zero.
        for i in range(offset,offset+length):
            for j in range(offset+length,len(pairs)):
                if minor[i][j]:
                    word.append(['add',i,j,Fraction(minor[i][j])]);cross+=1
    return pairs,pivots,minor,word,word0,word5,cross


def append_nonpivot(pairs,pivots,word,h):
    """Retain natural source labels explicitly; selected pivots come first."""
    pivot_set=set(pivots)
    nonpivots=[s for s in combinations(range(h),5) if s not in pivot_set]
    sources=pivots+nonpivots
    pair_index={p:i for i,p in enumerate(pairs)}
    for j,s in enumerate(nonpivots,len(pairs)):
        contained=set(combinations(s,2))
        for p in sorted(contained-{(0,1),(0,2)}):
            word.append(['add',pair_index[p],j,Fraction(1)])
        for p in ((0,1),(0,2)):
            if p not in contained:word.append(['add',pair_index[p],j,Fraction(1)])
    return sources


def complete_word(h):
    """Expose the literal reversible word for later independent frame audits."""
    pairs,pivots,minor,word,*_=local_words(h)
    sources=append_nonpivot(pairs,pivots,word,h)
    return dict(pair_order=pairs,source_order=sources,word=word,
                center_rank=len(pairs),nonpivot_source_order=sources[len(pairs):])


def run(h,literal,seed):
    started=perf_counter()
    pairs,pivots,minor,word,word0,word5,cross=local_words(h)
    q,volume=len(pairs),comb(h,5)
    total_bank_nonzeros=12*volume-4*comb(h-2,3)
    pivot_nonzeros=sum(bool(x) for row in minor for x in row)
    nonpivot_adds=total_bank_nonzeros-pivot_nonzeros
    counts=Counter(op[0] for op in word);counts['add']+=nonpivot_adds
    result=dict(status='REVERSIBLE SCALAR CENTER-BASIS WORD',h=h,volume=volume,
        center_rank=q,mode='literal complete operator' if literal else 'exact word counts',
        operation_counts=dict(counts),nonpivot_source_shears=nonpivot_adds,
        cross_block_shears=cross,extra_dirty_banks=0,
        scalar_additions_per_source=str(Fraction(counts['add'],volume)),
        base_factor_counts=dict(Counter(op[0] for op in word0)),
        border_factor_counts=dict(Counter(op[0] for op in word5)),
        swaps_retained_as_paid_scalar_role_exchanges=True,
        scale_values=sorted(set(str(op[2]) for op in word if op[0]=='scale')),
        complete_dirty_chronology='An invertible scalar word on existing banks; no assumed zero temporary or output bank',
        scope='Common-frame scalar component only. Initial differing source frames, target continuation, row movement, phase children, prefix guard and complete recurrence are unpaid.')
    if literal:
        if h>10:raise ValueError('Literal basis replay is initially bounded to h<=10')
        sources=append_nonpivot(pairs,pivots,word,h)
        assert Counter(op[0] for op in word)==counts
        bank=[[feature(p,s) for s in sources] for p in pairs]
        actual=[]
        for j in range(volume):
            original=[Fraction(int(i==j)) for i in range(volume)]
            output=apply(word,original)
            reference=[row[j] for row in bank]+original[q:]
            assert output==reference
            assert apply(word,output,True)==original
            actual.append(output)
        rng=random.Random(seed)
        fields=[[Fraction(rng.randrange(-100,101),1<<rng.randrange(6))
                 for _ in range(volume)] for _ in range(4)]
        for original in fields:
            output=apply(word,original)
            reference=[sum(c*x for c,x in zip(row,original) if c) for row in bank]+original[q:]
            assert output==reference
            assert apply(word,output,True)==original
        # Reversing chronology without inverse coefficients is observably
        # invalid; the exact inverse reverses AND inverts every scalar gate.
        reverse=[op[:] for op in reversed(word)]
        assert any(apply(reverse,original)!=apply(word,original) for original in fields)
        result['checked']=dict(complete_basis_columns=volume,forward_inverse_values=2*volume**2,
            arbitrary_dyadic_dirty_fields=4,wrong_chronology_rejected=True)
        result['word_sha256']=sha256(json.dumps(word,separators=(',',':'),default=str).encode()).hexdigest()
    result['seed']=seed;result['elapsed_seconds']=perf_counter()-started
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--h',type=int,required=True);p.add_argument('--literal',action='store_true')
    p.add_argument('--seed',type=int,default=20261008)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if not 7<=a.h<=32:raise ValueError('Initial bound7<=h<=32')
    if a.output.exists():raise FileExistsError('Use a fresh output')
    result=run(a.h,a.literal,a.seed);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
