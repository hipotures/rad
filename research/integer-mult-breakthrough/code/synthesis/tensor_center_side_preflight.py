#!/usr/bin/env python3
"""All-h scoped exclusion of the naive edge side for a K tensor K center.

The product center remains a valid fitting-factor hypothesis. This rejects
only one dirty side helper per nonzero product-side edge and the specified
closed full-width center releases. No enormous graph is instantiated.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import sys

COMPLEX=Path(__file__).resolve().parents[1]/'complex'
sys.path.insert(0,str(COMPLEX))
import characteristic as intervals


def base_nonzeros(h):
    # For weight5 K(t)=(t-1)(t-3)/8. It is nonzero at t0,2,4,5.
    def choose(n,k):return comb(n,k) if n>=k>=0 else 0
    return choose(h-5,5)+10*choose(h-5,3)+5*(h-5)+1


def lower_profile(h):
    if h<7:raise ValueError('The single-total basis is supported at h>=7')
    v,q=comb(h,5),comb(h,2);N,m=v*v,h*h;c=base_nonzeros(h)
    M=N*(c*c-1);W=3*N+M
    hist={1:N+M,m-1:3*N+M,m:2*q*q}
    rank=sum(width*count for width,count in hist.items())
    if rank != W*m-2*N+2*q*q*m:
        raise ValueError('Product fitting center plus side endpoint accounting failed')
    return dict(h=h,v=v,q=q,N=N,m=m,M=M,W=W,base_nonzero_K_row_entries=c,
                side_helpers_per_product_source=c*c-1,
                child_multiplicities=hist,rank_charge=rank,deficit=W*m-rank,
                scope='Optimistic LOWER moment bound for the naive one-dirty-helper-per-product-side-edge chronology; not a realizable improved profile.')


def verify():
    saving=Q(1,10000)
    rows=[]
    for h in (13,16,20):
        profile=lower_profile(h);moment=intervals.moment_interval(profile,saving)
        if moment[0]<=1:raise ValueError('The scoped product-side target exclusion failed')
        rows.append(dict(profile=profile,saving=saving,exact_lower_moment_interval=moment,
                         exact_positive_lower_gap=moment[0]-1))
    first_c=base_nonzeros(13)
    logarithm=intervals.log_interval(Q(169))
    sufficient_margin=saving*(first_c*first_c-1)-2
    if first_c!=657 or logarithm[0]<=1 or sufficient_margin<=0:
        raise ValueError('The all-h sufficient inequality is not strict')
    small=[]
    for h in range(7,13):
        v,q=comb(h,5),comb(h,2)
        if v>q*h:raise ValueError('The nonpositive small-h product center control failed')
        small.append(dict(h=h,v=v,q=q,product_center_deficit=2*(v*v-q*q*h*h)))
    # The common elementary inequality exp(z)>=1+z supplies a lower bound
    # from the M width-one calls alone. M/N=c(h)^2-1, c(h) is increasing.
    return dict(status='PASS ALL-H NAIVE TENSOR-CENTER SIDE EXCLUSION',saving=saving,cases=rows,
                small_h_nonpositive_center_controls=small,
                all_h_ge_13_proof=dict(first_nonzero_count=first_c,
                    log169_lower=logarithm[0],ln_m_greater_than_one=True,
                    normalized_numerator_margin_per_N_lower=sufficient_margin,
                    inequality='moment >= 1 + [b*M*ln(m)-2*N+2*q^2*m]/(W*m) > 1',
                    premises=['h>=13; m=h^2>=169',
                              'c(h)=C(h-5,5)+10*C(h-5,3)+5*(h-5)+1 is nondecreasing',
                              'M/N=c(h)^2-1>=657^2-1',
                              'Each edge helper has an obligatory width-one source-line entrance',
                              'The remaining helper geodesic moment is at least its rank at b0',
                              'The product center closes q^2 full→zero→full releases']),
                not_excluded=['Shared or factorized side helpers', 'A different joint signed exchange',
                              'A different center release or endpoint architecture',
                              'A changed transfer beyond this direct product frame word'],
                scope='Conditional all-h obstruction for the declared naive O(v^4) product-side stock. It does not exclude K tensor K fitting algebra or general multiplier improvements.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=(Path(__file__),Path(intervals.__file__))
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in sources}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=1,native_threads_each=1,
                  source_sha256={p.name:value for p,value in hashes.items()},seed=None,
                  allocation_preflight='Integer counts and exact interval arithmetic only; no product labels, edge graph, side helper banks or physical matrices allocated.')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    result=verify()
    if any(sha256(p.read_bytes()).hexdigest()!=value for p,value in hashes.items()):
        raise ValueError('Effective preflight source changed')
    (args.output/'certificate.json').write_text(json.dumps(intervals.serializable(result),indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(result['cases']),
                          all_h_ge_13_margin=str(result['all_h_ge_13_proof']['normalized_numerator_margin_per_N_lower']))))


if __name__=='__main__':main()
