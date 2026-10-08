#!/usr/bin/env python3
"""Optimistic complete-moment envelopes for the weight-five hypothesis.

No scalar side DAG or exponent is certified. Assumes the inherited two-stage
macros extend to these norm-one labels; gives a necessary role budget even
if every unspecified local phase residual is batched at maximal rank h.
"""
import argparse
from fractions import Fraction as Q
import json
from math import comb
from pathlib import Path

from characteristic import exp_interval, log_interval, serializable


def pair_center_loss(h):
    # Pair sums P have rank h-2. Replacing two by T-P permits division by
    # 10-2=8, eliminates the explicit total and singleton retained centers,
    # and raises exactly two center ranks by two each.
    return comb(h,2)*(h-2)+4


def old_center_loss(h):
    return comb(h,2)*(h-2)+h*(h-1)+h


def gaussian_dyadic_center_identities():
    # For one source five-subset there are ten included pairs and four
    # included pairs incident to each contained point. This is independent
    # of the selected replacement pairs and avoids enumerating v^2 entries.
    chosen_count=2
    total_coefficient=Q(10-chosen_count,10-chosen_count)
    singleton_coefficient=Q(4,4)
    polynomial=[]
    for intersection in range(6):
        center=Q((intersection-1)*(intersection-3),8)
        expanded=Q(2*comb(intersection,2)-3*intersection+3,8)
        side=-center if intersection%2==0 else Q(0)
        if center!=expanded or center+side!=int(intersection==5):
            raise ValueError('five-subset correction identity failed')
        polynomial.append(dict(intersection=intersection,center=center,side=side))
    if total_coefficient!=1 or singleton_coefficient!=1:
        raise ValueError('pair feature recovery failed')
    # The dense substituted scatter pays finer scalar coefficients than
    # the inherited triple centers. Independent track C identified this
    # explicit denominator-256 witness; retaining dyadicity alone misses it.
    replaced=((0,1),(0,2))
    target={1,4,5,6,7}
    def alpha(pair):
        intersection=len(set(pair)&target)
        return Q(int(intersection==2),4)-Q(3*intersection,32)
    gamma=Q(3,8)+sum((alpha(pair) for pair in replaced),Q(0))
    outside=(0,3)
    witness=alpha(outside)+gamma/8
    if witness!=Q(9,256):raise ValueError('dense scatter precision witness failed')
    return dict(replaced_pair_count=chosen_count,total_recovery_denominator=8,
                singleton_recovery_denominator=4,polynomial=polynomial,
                dense_scatter_denominator_bits=8,
                denominator_256_witness=dict(replaced_pairs=replaced,target=sorted(target),
                    unreplaced_pair=outside,gamma=gamma,scatter_coefficient=witness),
                scope='Exact scalar identities; phase labels and tape realization separate')


def envelope(h,loss,target=Q(20,189981)):
    m=h*h
    v=comb(h,5)
    N=v*v
    cache={}
    for t in (m-h,(h-1)**2,h-1,1,h):
        l,u=log_interval(Q(m,t))
        cache[t]=exp_interval(target*l,target*u)
    # F(R)=sum n*t*(m/t)^b - W*m. Every missing local child has t<=h,
    # so its moment is at least its rank mass*(m/h)^b. Positive F excludes
    # the target saving in any distribution satisfying this frozen ledger.
    def values(index):
        exp={t:bounds[index] for t,bounds in cache.items()}
        slope=2*v*((m-h)*exp[m-h]+h*exp[h]-m)
        intercept=(2*N*(h-1)**2*exp[(h-1)**2]+4*N*(h-1)*exp[h-1]
                   +N*exp[1]+2*v*loss*exp[h]-2*N*m)
        return slope,intercept
    lo_slope,lo_intercept=values(0)
    hi_slope,hi_intercept=values(1)
    if lo_slope<=0 or lo_intercept>=0:
        raise ValueError('no positive optimistic role allowance')
    grid=1<<160
    def downward(x):return Q(x.numerator*grid//x.denominator,grid)
    def upward(x):return Q(-(-x.numerator*grid//x.denominator),grid)
    cap_lo=downward(-hi_intercept/(hi_slope*v))
    cap_hi=upward(-lo_intercept/(lo_slope*v))
    return dict(h=h,m=m,v=v,center_loss=loss,zero_saving_deficit=N-2*v*loss,
                optimistic_role_per_source_cap_interval=[cap_lo,cap_hi],
                cap_decimal=float(cap_hi),
                assumed_external_children=[dict(width=m-h,count='2*v*R'),
                    dict(width=(h-1)**2,count=2*N),dict(width=h-1,count=4*N),
                    dict(width=1,count=N)],
                unspecified_internal_rank_mass='2*v*(h*R+center_loss)',
                optimistic_internal_child_width=h,
                scope='Necessary budget in a hypothetical ledger; no five-subset network exists here')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('output must be new')
    result=dict(hypothesis='Weight-five norm-one labels with mixed pair centers',
                target_complex_saving=Q(20,189981),
                center_identities=gaussian_dyadic_center_identities(),
                mixed_pair_envelopes=[envelope(h,pair_center_loss(h))
                                     for h in (16,18,20,22,24,26,28,30,32,36,40)],
                explicit_feature_envelopes=[envelope(h,old_center_loss(h))
                                     for h in (16,18,20,22,24,26,28,30,32,36,40)])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(serializable(result),indent=2)+'\n')
    for row in result['mixed_pair_envelopes']:
        print(row['h'],row['v'],row['center_loss'],row['cap_decimal'])


if __name__=='__main__':main()
