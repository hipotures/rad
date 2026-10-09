#!/usr/bin/env python3
"""Hypothetical complete-moment leverage for the scalar center-basis word.

Every profile is declared rather than produced by a native compiler. A scalar
gate count is used only as an explicit conservative helper-budget proxy; it is
not equated to actual physical auxiliary roles. Rank-loss tolerance quantifies
how much unpaid chronology could be afforded if this entire ledger held.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
from time import perf_counter

from characteristic import moment_interval,rational_root_bracket,serializable
from five_subset_envelope import pair_center_loss
from center_basis_scalar_word import run as scalar_word


TARGET=Q(20,189981)
LARGER=Q(20,18981)


def profile(h,R,loss,local):
    v=comb(h,5);N=v*v;m=h*h;W=2*N+2*v*R
    children=Counter({m-h:2*v*R,(h-1)**2:2*N,h-1:4*N,1:N})
    if not children[m-h]:del children[m-h]
    mass=h*R+loss
    if local=='rank1':children[1]+=2*v*mass
    elif local=='rankh':
        copies,remainder=divmod(mass,h)
        if copies:children[h]+=2*v*copies
        if remainder:children[remainder]+=2*v
    else:raise ValueError(local)
    total=sum(t*n for t,n in children.items())
    assert total==W*m-N+2*v*loss
    assert all(0<t<m and n>0 for t,n in children.items())
    return dict(m=m,W=W,N=N,ambient_h=h,assumed_auxiliary_roles=R,
                assumed_center_loss=loss,local_distribution=local,total_rank=total,
                deficit=N-2*v*loss,child_multiplicities=dict(sorted(children.items())))


def run(h):
    started=perf_counter();v=comb(h,5);loss=pair_center_loss(h)
    word=scalar_word(h,False,20261008)
    counts=word['operation_counts']
    proxy=counts.get('add',0)+4*counts.get('swap',0)+counts.get('scale',0)
    rows=[]
    for budget,R in [('zero-extra-helper idealization',0),
                     ('expanded-scalar-gate helper proxy',proxy)]:
        for local in ('rank1','rankh'):
            p=profile(h,R,loss,local)
            root=rational_root_bracket(p)
            target=moment_interval(p,TARGET);larger=moment_interval(p,LARGER)
            # An additional local loss Delta adds 2v*Delta rank-one calls.
            # The tolerance below uses this worst residual placement even
            # when the base distribution is optimistic rankh.
            unit=profile(h,R,loss+1,local='rank1')
            baseline_worst=profile(h,R,loss,local='rank1')
            u=moment_interval(unit,TARGET);base=moment_interval(baseline_worst,TARGET)
            # Exact linear slope: only 2v rank-one calls are added.
            slope_low=u[0]-base[1];slope_high=u[1]-base[0]
            assert slope_low>0
            candidates=[(1-value)/slope for value in target
                        for slope in (slope_low,slope_high)]
            tolerance=[min(candidates),max(candidates)]
            assert tolerance[0]<=tolerance[1]
            rows.append(dict(budget_hypothesis=budget,profile=p,complex_root_bracket=root,
                target_saving=TARGET,target_moment_interval=target,
                target_crossing_status=('below1' if target[1]<1 else 'above1' if target[0]>1 else 'unresolved'),
                larger_complex_saving=LARGER,larger_moment_interval=larger,
                extra_local_rank_loss_per_source_interval=[x/v for x in tolerance]))
    return dict(status='HYPOTHETICAL NATIVE CAPACITY ASSESSMENT',h=h,volume=v,
        scalar_word_counts=counts,expanded_scalar_gate_proxy=proxy,proxy_per_source=Q(proxy,v),
        rows=rows,elapsed_seconds=perf_counter()-started,
        assumptions=['Existing two-stage k5 master profile extends to an actual compiled word',
                     'Complete auxiliary count equals the declared R hypothesis',
                     'Copied-center loss q*(h-2)+4 remains valid for that same chronology',
                     'Every extra phase, dirty-copy, inverse and endpoint call is in the profile or paid loss',
                     'Worst local residuals can be bounded by rank-one placement'],
        scope='Exact finite moments of explicit unattained profiles only. Gate counts do not prove auxiliary counts, loss or native phase semantics. No exponent, end-to-end kappa or favorable actual compiler is supplied.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--h',type=int,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.h not in (16,20,24,28):raise ValueError('First discriminator uses only16/20/24/28')
    if a.output.exists():raise FileExistsError('Use a fresh output')
    result=run(a.h);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(serializable(result),indent=2)+'\n')
    for row in result['rows']:
        root=row['complex_root_bracket'];delta=row['extra_local_rank_loss_per_source_interval']
        print(json.dumps(dict(h=a.h,budget=row['budget_hypothesis'],local=row['profile']['local_distribution'],
            root=[float(root['lower']),float(root['upper'])],target=row['target_crossing_status'],
            extra_loss_per_source=[float(x) for x in delta])))


if __name__=='__main__':main()
