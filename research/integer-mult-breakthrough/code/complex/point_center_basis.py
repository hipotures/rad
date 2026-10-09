#!/usr/bin/env python3
"""Dyadic point-center bases and the distinct small-h linear completion.

The basis exists for every h>=6. The linear central fitting matrix is valid
only for five-subsets at h<=8; a complete odd-intersection counterexample is
retained at h10. All scalar data-bank words are reversible and arbitrary-dirty.
No paid initial/final address chronology or favorable native moment is given.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import random
from time import perf_counter

from center_basis_scalar_word import factor_word,apply
from center_null_basis import identity,multiply
from structured_center_basis import determinant,inverse_square
from lagrangian_phase_screen import basis


def source_mask(source):
    return sum(1<<i for i in source)


def point_feature(i,source):
    return int(i not in source) if i==0 else int(i in source)


def pivot_basis(h):
    pivots=[tuple(i for i in range(6) if i!=j) for j in range(6)] + [
        (0,1,2,3,j) for j in range(6,h)]
    minor=[[point_feature(i,s) for s in pivots] for i in range(h)]
    assert determinant(minor)==4
    inverse=inverse_square(minor)
    assert multiply(minor,inverse)==identity(h)
    assert multiply(inverse,minor)==identity(h)
    assert all(x.denominator in (1,2,4) for row in inverse for x in row)
    return pivots,minor,inverse


def complete_word(h):
    pivots,minor,inverse=pivot_basis(h)
    pivot_set=set(pivots)
    sources=pivots+[s for s in combinations(range(h),5) if s not in pivot_set]
    five=factor_word([[int(i!=j) for j in range(5)] for i in range(5)])
    word=[]
    for kind,*args in five:
        if kind=='add':
            i,j,c=args;word.append([kind,i+1,j+1,c])
        elif kind=='scale':
            i,c=args;word.append([kind,i+1,c])
        else:word.append([kind,args[0]+1,args[1]+1])
    word.extend(['add',i,0,Q(1)] for i in range(1,6))
    for j in range(6,h):
        for i in (1,2,3):word.append(['add',i,j,Q(1)])
    for j,s in enumerate(sources[h:],h):
        for i in s:
            if i:word.append(['add',i,j,Q(1)])
        if 0 not in s:word.append(['add',0,j,Q(1)])
    return dict(source_order=sources,pivot_sources=pivots,word=word,
                features=['D0']+[f'G{i}' for i in range(1,h)],center_rank=h)


def decoder(target,h):
    s=set(target);contains=int(0 in s)
    # T=(sum_i>0 Gi-D0)/4 and G0=T-D0.
    total_coefficient=Q(contains-3,2)
    return [-Q(contains,2)-total_coefficient/4] + [
        Q(int(i in s),2)+total_coefficient/4 for i in range(1,h)]


def run(h,seed):
    started=perf_counter();spec=complete_word(h)
    sources=spec['source_order'];word=spec['word'];v=len(sources)
    bank=[[point_feature(i,s) for s in sources] for i in range(h)]
    expected_adds=6*v-2*comb(h-1,4)+3-h
    counts=Counter(op[0] for op in word)
    assert counts['add']==expected_adds
    assert counts['swap']==3 and counts['scale']==2
    for j in range(v):
        original=[Q(int(i==j)) for i in range(v)]
        output=apply(word,original)
        assert output==[row[j] for row in bank]+original[h:]
        assert apply(word,output,True)==original
    rng=random.Random(seed)
    for field in range(4):
        original=[Q(rng.randrange(-100,101),1<<rng.randrange(6)) for _ in range(v)]
        output=apply(word,original)
        assert output==[sum(x*c for x,c in zip(original,row) if c) for row in bank]+original[h:]
        assert apply(word,output,True)==original
    central=multiply([decoder(s,h) for s in sources],bank)
    forbidden=[]
    for i,s in enumerate(sources):
        for j,t in enumerate(sources):
            intersection=len(set(s)&set(t))
            assert central[i][j]==Q(intersection-3,2)
            if i==j:assert central[i][j]==1
            elif intersection%2 and central[i][j] and len(forbidden)<4:
                forbidden.append(dict(source=s,target=t,intersection=intersection,
                                      central_coefficient=str(central[i][j])))
    fitting=not forbidden
    assert fitting==(h<=8)
    spans=[]
    for i,row in enumerate(bank):
        vectors=basis(tuple(source_mask(s) for s,c in zip(sources,row) if c))
        gram=[sum(((a&b).bit_count()%2)<<j for j,b in enumerate(vectors)) for a in vectors]
        spans.append(dict(feature=spec['features'][i],dimension=len(vectors),
                          gram_rank=len(basis(tuple(gram))),
                          radical_dimension=len(vectors)-len(basis(tuple(gram)))))
    scaled_pivot_kernel=[[int(2*central[i][j]) for j in range(h)] for i in range(h)]
    # Original point-incidence pivot det is +/-5; its columns sum to five.
    # Therefore det(2K_pivot)=25*det(I-(3/25)J)=25-3h.
    assert determinant(scaled_pivot_kernel)==25-3*h
    return dict(status='EXACT SMALL-H POINT-CENTER SCALAR COMPONENT',h=h,volume=v,
        pivot_determinant=4,inverse_denominator_bound=4,center_rank=h,
        central_rank_witness_scaled_minor_determinant=25-3*h,
        linear_completion_is_fitting=fitting,odd_intersection_counterexamples=forbidden,
        scalar_operation_counts=dict(counts),extra_dirty_banks=0,
        feature_spans=spans,checked=dict(complete_basis_columns=v,
            forward_inverse_basis_values=2*v*v,complete_kernel_entries=v*v,
            arbitrary_dirty_fields=4),seed=seed,elapsed_seconds=perf_counter()-started,
        source_order_sha256=sha256(json.dumps(sources).encode()).hexdigest(),
        word_sha256=sha256(json.dumps(word,default=str).encode()).hexdigest(),
        scope='Exact scalar basis and valid linear fitting completion onlyh6/7/8. No native frame transitions, center-loss profile, multiplication characteristic or exponent. Degenerate/alternating spans need the paid general-frame interface.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--h',type=int,required=True);p.add_argument('--seed',type=int,default=20261008)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.h not in (6,7,8,10):raise ValueError('First discriminator uses6/7/8/10')
    if a.output.exists():raise FileExistsError('Use a fresh output')
    result=run(a.h,a.seed);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
