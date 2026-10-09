#!/usr/bin/env python3
"""Paid binary moment from this lane's freshly recounted native profile.

No upstream/discovery Python or saved moment endpoint is imported. The
reviewer's explicit rational interval method is shared with its first audit.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
import independent_arithmetic as interval


def need(ok,message):
    if not ok:raise ValueError(message)


def main():
    need(not sys.flags.optimize,'assertion-disabled execution rejected')
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('profile','finite-receipt','output'):ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--coarse',type=Q,required=True);ap.add_argument('--grid',type=Q,required=True)
    ap.add_argument('--atom',type=Q,default=Q(1,1000));args=ap.parse_args()
    need(not args.output.exists(),'fresh output required');start=time.monotonic()
    profile=json.loads(args.profile.read_text());receipt=json.loads(args.finite_receipt.read_text())
    need(profile==receipt['profile'],'finite reconstruction/profile identity')
    H=Counter()
    for name in ('local_histogram','source_data_histogram','target_data_histogram'):
        H.update({int(r):3*n for r,n in profile[name].items() if int(r) and n})
    gauge=profile.get('physical_gauge_histogram',profile['selected_rank_histogram'])
    H.update({3*int(r):n for r,n in gauge.items() if int(r) and n});H[2]+=2*profile['v']
    need(dict(H)=={int(r):n for r,n in profile['child_histogram'].items()},'complete native child ledger')
    m,W=profile['m'],profile['W_per_vertex'];mass=sum(r*n for r,n in H.items());edges=sum(H.values())
    need(m==3*profile['h'] and W==2*profile['v']+profile.get('physical_R',profile['R']) and
         mass==profile['rank_per_vertex'] and m*W-mass==profile['deficit_per_vertex']==2*profile['v']-3*profile['loss'],
         'physical native normalization and telescoping deficit')
    BAD=Q(1,10**16);old=Q(384599,10**10);need(Q(2*m**3,2**80)<BAD,'retained rare-prime bound')
    results={}
    for name,saving in [('accepted',args.coarse),('successor',args.coarse+args.grid)]:
        lo,hi=interval.moment(m,W,dict(H),saving)
        l,h=interval.log_bounds(Q(m));el,eh=interval.exp_bounds(saving*l,saving*h)
        weight=BAD*Q(32*m*m*edges,m*W);lo=interval.down(lo+weight*el);hi=interval.up(hi+weight*eh)
        results[name]=dict(saving=saving,lower=lo,upper=hi,gap_lower=1-hi,excess_lower=lo-1,
                           full_fallback_weight=weight)
    need(results['accepted']['upper']<1 and results['successor']['lower']>1,'coarse acceptance and successor rejection')
    record=dict(status='PASS_INDEPENDENT_NATIVE_BINARY_MOMENT',m=m,W=W,edge_count=edges,rank_mass=mass,
        coarse=args.coarse,grid=args.grid,atom=args.atom,old_ordinary_saving=old,
        ordinary_saving=args.atom*old+(1-args.atom)*args.coarse,bad_fraction=BAD,beta=Q(1,10**9),results=results,
        profile_sha256=sha256(args.profile.read_bytes()).hexdigest(),finite_receipt_sha256=sha256(args.finite_receipt.read_bytes()).hexdigest(),
        checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),interval_code_sha256=sha256(Path(interval.__file__).read_bytes()).hexdigest(),
        completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,
        method='40-term atanh, degree-nine exponential, explicit tails, outward 2^-180 rounding. Full additional 32m^2 singleton fallback on every positive edge and bad fraction10^-16.',
        scope='Finite paid binary moment and fixed atom bridge only. Full bridge and balanced assembly retain their independent source-bound review.')
    args.output.write_text(json.dumps(interval.js(record),indent=2)+'\n');print(json.dumps(interval.js(record),indent=2))


if __name__=='__main__':main()
