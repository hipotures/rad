#!/usr/bin/env python3
"""Enclose the complete independently recounted binary paid moment.

Uses only this reviewer's retained rational log/exp code. No producer,
candidate interval endpoints, saved verdict or upstream Python is imported.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
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
    args=ap.parse_args();need(not args.output.exists(),'fresh output required')
    start=time.monotonic();profile=json.loads(args.profile.read_text());receipt=json.loads(args.finite_receipt.read_text())
    need(profile==receipt['profile'],'independent finite receipt/profile binding')
    H=Counter()
    for name in ('local_histogram','source_data_histogram','target_data_histogram'):
        H.update({int(r):3*n for r,n in profile[name].items() if int(r) and n})
    H.update({3*int(r):n for r,n in profile['selected_rank_histogram'].items() if int(r) and n})
    H[2]+=2*profile['v']
    need(dict(H)=={int(r):n for r,n in profile['child_histogram'].items()},'complete independently recounted histogram')
    m,W=profile['m'],profile['W_per_vertex'];edges=sum(H.values());mass=sum(r*n for r,n in H.items())
    need((m,W,edges,mass,m*W-mass)==(72,26888,317916,1934000,1936),'frozen full inventory')
    BAD=Q(1,10**16);a0=Q(594996721,10**12);atom=Q(1,1000);old=Q(384599,10**10)
    need(Q(2*m**3,2**80)<BAD,'retained rare-prime allowance')
    results={}
    for label,saving in [('accepted',a0),('successor',a0+Q(1,10**12))]:
        lo,hi=interval.moment(m,W,dict(H),saving)
        l,h=interval.log_bounds(Q(m));el,eh=interval.exp_bounds(saving*l,saving*h)
        weight=BAD*Q(32*m*m*edges,m*W)
        lo=interval.down(lo+weight*el);hi=interval.up(hi+weight*eh)
        results[label]=dict(saving=saving,lower=lo,upper=hi,gap_lower=1-hi,excess_lower=lo-1,
                            full_positive_edge_fallback_weight=weight)
    need(results['accepted']['upper']<1 and results['successor']['lower']>1,'exact coarse/grid boundary')
    ordinary=atom*old+(1-atom)*a0
    need(ordinary==Q(594440184179,10**15),'retained atom bridge')
    result=dict(status='PASS_INDEPENDENT_BINARY_PAID_MOMENT',coarse_saving=a0,atom=atom,old_ordinary_saving=old,
        ordinary_saving=ordinary,beta=Q(1,10**9),bad_fraction=BAD,results=results,
        profile_sha256=sha256(args.profile.read_bytes()).hexdigest(),
        finite_receipt_sha256=sha256(args.finite_receipt.read_bytes()).hexdigest(),
        checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        interval_code_sha256=sha256(Path(interval.__file__).read_bytes()).hexdigest(),
        completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,
        method='40 positive atanh terms, degree-nine exp, explicit tails, outward 2^-180 rounding. '
               'Every positive ideal child additionally pays 32m^2 singleton fallback on bad fraction 10^-16; no ideal work is subtracted.',
        scope='Moment and retained fixed atom bridge on this freshly recounted finite word. Unified balanced layout and 47+7 assembly are independently reviewed by the assembly lane.')
    args.output.write_text(json.dumps(interval.js(result),indent=2)+'\n')
    print(json.dumps(interval.js(result),indent=2))


if __name__=='__main__':main()
