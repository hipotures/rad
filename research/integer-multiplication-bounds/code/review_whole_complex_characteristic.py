#!/usr/bin/env python3
"""Independent coarse exact whole-residual characteristic for accepted h28.

The numerical batching producer is not imported. A simple b=10^-6 uses
independently enclosed natural logs with the coarse bounds ln m<10 and
ln r>99/10, sufficient for the bit-limited beta1/2 construction.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import time

from review_parameter_audit import log_integer


def convert(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):convert(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [convert(v) for v in x]
    return x


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--finite-review',type=Path,required=True)
    ap.add_argument('--generic-bit-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();start=time.monotonic()
    full=json.loads(args.finite_review.read_text())['full'];stored=full['counts'];h=stored['h']
    assert h==28 and stored['R']==88377
    R=stored['R'];v=comb(h,3);m=h**3;N=v**3
    W=2*N+2*v*v*(R+h+1);L=3*v*v*(h+1)*h;D=2*N-2*L;s=W*m-D
    values=dict(h=h,R=R,v=v,m=m,N=N,W=W,L=L,D=D,s=s)
    assert values==stored
    J=(R+h+1)*v*v
    ranks=dict(middle=m-h*h,joined=m-2*h,data=(h*h-1)*(h-1))
    copies=dict(middle=J,joined=J,data=2*N)
    credited=sum(ranks[k]*copies[k] for k in ranks)
    singleton=s-credited;assert singleton>0
    histogram={1:singleton}
    for k in ranks:histogram[ranks[k]]=histogram.get(ranks[k],0)+copies[k]
    assert sum(r*n for r,n in histogram.items())==s and max(histogram)<m
    logs={r:log_integer(r,80) for r in [m,*ranks.values()]}
    assert logs[m][1]<10
    assert all(logs[r][0]>Q(99,10) for r in ranks.values())
    # Every other residual retains its old individual children.
    moment_lower=Q(99,10)*credited;linear_upper=10*s-moment_lower
    quadratic_upper=Q(100*s,2)
    b=Q(1,10**6)
    gap=D-b*linear_upper-b*b*quadratic_upper/(1-10*b)
    assert gap>0 and 0<10*b<1
    fine_moment=sum(copies[k]*ranks[k]*logs[ranks[k]][0] for k in ranks)
    fine_linear=s*logs[m][1]-fine_moment
    fine_gap=D-b*fine_linear-b*b*s*logs[m][1]**2/(2*(1-b*logs[m][1]))
    assert fine_gap>=gap>0
    bit=json.loads(args.generic_bit_review.read_text())
    # The accepted constructor pilot contains an independently certified
    # explicit rational bit characteristic; no giant h51 table is claimed.
    a=Q(bit['row']['explicit_saving'])
    assert 0<2*a<b<1
    maxchild=max(ranks.values());assert m**272>2*maxchild**272 and W<2**41
    output=dict(status='PASS independent exact b_phase=10^-6 on accepted changed h28',
        generated_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        dependency_sha256={'review_parameter_audit.py':sha256(Path(__file__).with_name('review_parameter_audit.py').read_bytes()).hexdigest()},
        inputs={str(p):sha256(p.read_bytes()).hexdigest() for p in (args.finite_review,args.generic_bit_review)},
        counts=values,grouped_ranks=ranks,family_multiplicities=copies,
        total_grouped_rank=credited,all_other_individual_pivots=singleton,child_histogram=histogram,
        saving=b,sigma=1-b,coarse_log_m_upper=Q(10),coarse_grouped_log_lower=Q(99,10),
        rank_log_moment_lower=moment_lower,normalized_linear_upper=linear_upper,
        normalized_quadratic_upper=quadratic_upper,strict_normalized_gap=gap,
        fine_positive_gap=fine_gap,exact_log_intervals=logs,
        exact_log_terms=80,accepted_generic_bit_saving=a,phase_above_twice_bit=b-2*a,
        beta_half_leaf_above_bit_margin=b/2-a,
        maximum_child=maxchild,exact_half_shrink_power=272,
        scope='New whole-rank phase branching exponent under the independently reviewed tape/phase/volume/tail interface. Paid bit adapters remain at tau; no standalone complex runtime exponent below tau is claimed.',
        wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(convert(output),indent=2,sort_keys=True)+'\n')
    print(output['status'],'gap',gap,flush=True)


if __name__=='__main__':main()
