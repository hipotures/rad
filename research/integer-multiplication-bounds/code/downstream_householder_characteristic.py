#!/usr/bin/env python3
"""Strict characteristic for one fixed H-orthogonal ground reflection.

Q=I-2J/h is applied to every assigned rational frame before constructing
the fixed native table. It is not a physical array adapter. This source
retains the universal joined bound; stronger joined bounds are separate.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_gaussian import network_counts,require
from downstream_parameter_optimum import as_strings,rational_decimal_lower
from downstream_rotated_batch_characteristic import log_bounds
from downstream_uncapped_middle_characteristic import uncapped_middle


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def householder(h,roles,variant):
    require(h>18 and variant in ('two-family','tensor-data'),'Invalid reflection scope')
    n=network_counts(h,roles);v,m=n['v'],n['m'];copies=(roles+h)*v*v
    u_in,u_out=1-F(6,h),-F(6,h)
    v_out=F(h-18,6*h);v_in=F(1,2)+v_out
    require(all(x!=0 for x in (u_in,u_out,v_in,v_out)),
            'Reflected triple vector or dual has a zero coordinate')
    require(3*u_in*v_in+(h-3)*u_out*v_out==1,
            'Reflected projector normalization failed')
    require(u_in*v_in+2*u_in*v_out+2*u_out*v_in+(h-5)*u_out*v_out==0,
            'Reflected intersection-one orthogonality failed')
    middle_histogram={h*h:copies,h*h*(h-2):copies}
    middle_rank=copies*h*h*(h-1)
    require(sum(r*c for r,c in middle_histogram.items())==middle_rank,
            'Uniform reflected middle rank differs')
    middle_moment=sum((r*c*log_bounds(r)[0] for r,c in middle_histogram.items()),F(0))
    joined_rank=copies*(m-2*h);t=m-4*h;g=4*h+1
    joined_moment=copies*t*(log_bounds(t)[0]-log_bounds(g)[1])
    data_rank=data_moment=0;data_histogram={}
    if variant=='tensor-data':
        count=2*n['N']*(h-1)
        data_histogram={1:count,h*h-2:count}
        data_rank=count*(h*h-1)
        require(sum(r*c for r,c in data_histogram.items())==data_rank,
                'Uniform reflected tensor data rank differs')
        data_moment=count*(h*h-2)*log_bounds(h*h-2)[0]
    require(middle_rank+joined_rank+data_rank<n['s'],
            'Reflected grouped families are not disjoint')
    lm=log_bounds(m)[1]
    linear=n['W']*m*lm-middle_moment-joined_moment-data_moment
    quadratic=F(n['s'],2)*lm*lm
    require(linear>0 and quadratic>0,'Invalid reflected characteristic')
    gap=lambda a:n['D']-a*linear-a*a*quadratic
    lo,hi=F(0),F(1,10**7)
    require(gap(lo)>0>gap(hi),'Reflected root bracket failed')
    for _ in range(96):
        mid=(lo+hi)/2
        if gap(mid)>0:lo=mid
        else:hi=mid
    saving=F(lo.numerator*10**24//lo.denominator,10**24)
    require(gap(saving)>0,'Reflected Taylor certificate is not strict')
    return dict(certificate_kind='HOUSEHOLDER DENSE-LINE NEGATIVE-EXPONENTIAL TAYLOR',
                variant=variant,h=h,roles=roles,counts=n,
                compiler_basis='Cycle(3,1,2)*(Q tensor Q tensor Q), Q=I-2J/h',
                ground_metric='H=I-J/9',
                reflected_line=dict(u_in=u_in,u_out=u_out,v_in=v_in,v_out=v_out,
                                    every_coordinate_nonzero=True,
                                    normalized_dual_exact=True,intersection_one_orthogonality_exact=True),
                middle_old_rank=middle_rank,joined_old_rank=joined_rank,data_old_rank=data_rank,
                other_unchanged_rank=n['s']-middle_rank-joined_rank-data_rank,
                middle_batch_histogram={str(r):c for r,c in sorted(middle_histogram.items())},
                middle_rank_log_sum_lower=middle_moment,
                joined_rank_log_sum_lower=joined_moment,
                joined_minimum_diagonal=t,joined_run_bound=g,
                joined_bound='Retained universal Jensen moment only',
                data_batch_histogram={str(r):c for r,c in sorted(data_histogram.items())},
                data_rank_log_sum_lower=data_moment,
                maximum_child_rank=h*h*(h-2),child_ratio=F(h-2,h),
                row_depth='ceil(log_(h/(h-2))e)<=ceil((h/2)*ln(e))',
                taylor_linear_coefficient=linear,taylor_quadratic_coefficient=quadratic,
                saving=saving,saving_decimal_lower=rational_decimal_lower(saving,18),
                strict_taylor_gap=gap(saving),root_bracket=[lo,hi],
                exact_log_method='24-term integer logarithm intervals, outward common dyadic256-bit endpoints',
                above_two_power_minus_26=saving>F(1,2**26))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--uncapped-characteristic',type=Path,required=True)
    ap.add_argument('--reflected-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic();old=json.loads(args.uncapped_characteristic.read_text())
    source_dir=Path(__file__).parent
    for name,digest in old['source_sha256'].items():
        require(sha(source_dir/name)==digest,'Frozen uncapped source differs '+name)
    finite=old['odd_bit_finite_audit']
    require(finite['status']=='INDEPENDENT FINITE PROMOTION PASS' and
            finite['h']==51 and finite['roles']==500703,'Pinned finite clone differs')
    review=json.loads(args.reflected_review.read_text())
    require(review['status'].startswith('PASS') and
            review['finite_candidate_id']==finite['candidate_id'] and
            review['finite_compiled_sha256']==finite['compiled_sha256'],
            'Independent complete reflected finite identity differs')
    require(review['new_address_table'] and review['no_runtime_basis_adapter'] and
            review['separate_complex_scalar_guard_unchanged'] and
            review['retained_uncapped_row_degree']==2600 and
            review['whole_common_frame_controls']['exact_reflected_source_gate_sink_pipeline'],
            'Independent complete reflected frame/tape interface absent')
    regressions=[]
    for p in old['witnesses']:
        require(as_strings(uncapped_middle(p['h'],p['roles'],p['variant']))==p,
                'Historical uncapped characteristic regression differs')
        regressions.append(dict(variant=p['variant'],saving=p['saving'],unchanged=True))
    rows=[householder(finite['h'],finite['roles'],v) for v in ('two-family','tensor-data')]
    for p in rows:
        previous=next(r for r in old['witnesses'] if r['variant']==p['variant'])
        require(p['saving']>F(previous['saving']),'No strict Householder improvement')
        peer=next(r for r in review['rows'] if
                  (r['data_rank']>0)==(p['variant']=='tensor-data'))
        for key in ('h','m','N','W','L','D','s'):
            require(peer['counts'][key]==p['counts'][key],
                    'Independent reflected count differs '+key)
        require(F(peer['explicit_saving'])>=p['saving'] and
                F(peer['strict_characteristic_gap'])>0 and
                peer['maximum_middle_child']==p['maximum_child_rank'],
                'Independent stronger reflected characteristic absent')
    hashes=dict(old['source_sha256']);hashes[Path(__file__).name]=sha(Path(__file__))
    result=dict(status='PASS STRICT HOUSEHOLDER CHARACTERISTICS WITH INDEPENDENT FIXED-BASIS TRANSFER',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
                generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
                input_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in
                             (args.uncapped_characteristic,args.reflected_review)},
                odd_bit_finite_audit=finite,uncapped_regressions=regressions,witnesses=rows,
                independent_reflected_review_sha256=sha(args.reflected_review),
                elapsed_seconds=time.monotonic()-started,
                scope='One newly fixed H-orthogonal rational frame/table basis, full dense-line middle and exact tensor-data profiles. Role graph/ranks and complex numerical guard unchanged. New fixed table/prime/C are eventual setup obligations; no runtime Q adapter or sharper joined hypothesis is assumed.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for p in rows:print(result['status'],p['variant'],p['saving'],p['saving_decimal_lower'],flush=True)


if __name__=='__main__':main()
