#!/usr/bin/env python3
"""Strict characteristic for the reviewed simultaneous rational metric basis.

The giant basis/table/prime are fixed finite setup, not instantiated here.
The source verifies the actual promoted boundary ranks and uses a direct
negative-exponential Taylor certificate independent of the peer formula.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_gaussian import network_counts,require
from downstream_parameter_optimum import as_strings,rational_decimal_lower
from downstream_rotated_batch_characteristic import log_bounds


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def generic(h,roles):
    require((h,roles)==(51,485680),'This certificate pins the promoted h51 descendant')
    n=network_counts(h,roles);m,v=n['m'],n['v'];J=(roles+h)*v*v
    deficits=dict(middle=h*h,joined=2*h,data=h*h+h-1)
    multiplicities=dict(middle=J,joined=J,data=2*n['N'])
    runs={name:m-2*d for name,d in deficits.items()}
    family_ranks={name:multiplicities[name]*(m-d) for name,d in deficits.items()}
    require(all(0<r<m for r in runs.values()) and sum(family_ranks.values())<n['s'],
            'Useful generic kernels or disjoint family ranks failed')
    hist={}
    for name,r in runs.items():hist[r]=hist.get(r,0)+multiplicities[name]
    long_rank=sum(r*c for r,c in hist.items());individual=n['s']-long_rank
    require(individual>0,'Remaining individual pivot count is nonpositive')
    moments={name:multiplicities[name]*r*log_bounds(r)[0] for name,r in runs.items()}
    lm=log_bounds(m)[1]
    linear=n['W']*m*lm-sum(moments.values())
    quadratic=Q(n['s'],2)*lm*lm
    gap=lambda a:n['D']-a*linear-a*a*quadratic
    lo,hi=Q(0),Q(1,10**5)
    require(linear>0 and gap(lo)>0>gap(hi),'Generic strict root bracket failed')
    for _ in range(100):
        mid=(lo+hi)/2
        if gap(mid)>0:lo=mid
        else:hi=mid
    saving=Q(lo.numerator*10**24//lo.denominator,10**24)
    require(gap(saving)>0,'Generic characteristic is not strict')
    maximum=max(runs.values())
    require(maximum==m-4*h and m**651>2*maximum**651,
            'Generic 651-level halving bound failed')
    require(n['W']<2**49 and Q(49*651)*(2+Q(1,25))<66000,
            'Generic complete row degree bound failed')
    return dict(certificate_kind='GENERIC METRIC FLAGS, DIRECT NEGATIVE-EXPONENTIAL TAYLOR',
                h=h,roles=roles,counts=n,kernel_dimensions=deficits,
                family_multiplicities=multiplicities,family_ranks=family_ranks,
                grouped_runs=runs,long_run_histogram={str(r):c for r,c in sorted(hist.items())},
                long_grouped_rank=long_rank,individual_pivot_count=individual,
                rank_log_moment_lower=moments,
                taylor_linear_coefficient=linear,taylor_quadratic_coefficient=quadratic,
                saving=saving,saving_decimal_lower=rational_decimal_lower(saving,18),
                strict_taylor_gap=gap(saving),root_bracket=[lo,hi],
                maximum_child_rank=maximum,child_ratio=Q(maximum,m),
                depth_per_ceil_log2e=651,sufficient_row_degree=66000,
                sufficient_reservoir_coefficient=264000,
                row_degree_rational_slack=66000-Q(49*651)*(2+Q(1,25)),
                native_basis='One constructively defined rational ambient metric isometry making both flags full for every useful kernel',
                fixed_table_changed=True,runtime_basis_adapter=False,
                full_h51_basis_instantiated=False,
                setup='Finite deterministic reflection search, new rational factor table and one shared admissible odd prime; constants separately eventual',
                exact_log_method='Outward24-term exact intervals on common dyadic2^256 grid')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--descendant-characteristic',type=Path,required=True)
    ap.add_argument('--generic-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic();source_dir=Path(__file__).parent
    old=json.loads(args.descendant_characteristic.read_text())
    review=json.loads(args.generic_review.read_text())
    for document in (old,review):
        for name,digest in document['source_sha256'].items():
            require(sha(source_dir/name)==digest,'Executed generic/descendant source differs '+name)
    finite=old['odd_bit_finite_audit']
    require(review['status']=='PASS independent finite-family rational reflections and complementary flags' and
            review['finite_candidate_id']==finite['candidate_id'] and
            review['finite_compiled_sha256']==finite['compiled_sha256'] and
            review['fixed_table_changed'] and not review['new_runtime_adapter'] and
            not review['all_h51_ambient_basis_instantiated'],
            'Complete generic fixed-table construction/finite identity absent')
    require(review['dirty_common_frame_control']['full_source_gate_sink_conjugation'] and
            review['dirty_common_frame_control']['omitted_one_conjugation_discriminated'],
            'Independent complete common-frame dirty endpoint control absent')
    require(old['actual_boundary_histogram_audit']['all_categories_reconstruct_actual_histogram'] and
            old['actual_boundary_histogram_audit']['no_identity_padding'],
            'Actual promoted boundary histogram absent')
    p=generic(finite['h'],finite['roles']);peer=review['row']
    for key in ('h','side_roles','v','m','N','W','L','D','s'):
        require(peer['counts'][key]==p['counts'][key],
                'Independent generic count differs '+key)
    require(peer['kernel_dimensions']==p['kernel_dimensions'] and
            peer['family_ranks']==p['family_ranks'] and
            peer['grouped_middle']==p['grouped_runs']['middle'] and
            peer['grouped_joined']==p['grouped_runs']['joined'] and
            peer['grouped_data']==p['grouped_runs']['data'],
            'Independent complementary profile/rank families differ')
    require(peer['maximum_child']==p['maximum_child_rank'] and
            peer['depth_bound_per_ceil_log2e']==651 and
            peer['sufficient_row_degree']==66000 and
            peer['sufficient_reservoir_linear_coefficient']==264000,
            'Independent deeper row/table transfer differs')
    require(Q(peer['explicit_saving'])>=p['saving'] and
            Q(peer['strict_characteristic_gap'])>0 and
            p['saving']>Q(old['witness']['saving']),
            'Independent stronger generic strict saving absent')
    for name,oldkey in (('middle','middle_old_rank'),('joined','joined_old_rank'),('data','data_old_rank')):
        require(p['family_ranks'][name]==old['witness'][oldkey],
                'Generic family rank differs from actual promoted boundary '+name)
    hashes=dict(old['source_sha256']);hashes[Path(__file__).name]=sha(Path(__file__))
    result=dict(status='PASS STRICT GENERIC METRIC CHARACTERISTIC WITH INDEPENDENT CONSTRUCTIVE TRANSFER',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
                generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
                input_files={str(q):dict(bytes=q.stat().st_size,sha256=sha(q)) for q in
                             (args.descendant_characteristic,args.generic_review)},
                odd_bit_finite_audit=finite,
                actual_boundary_histogram_audit=old['actual_boundary_histogram_audit'],
                actual_bit_literal_guard=old['actual_bit_literal_guard'],
                independent_generic_review_sha256=sha(args.generic_review),
                independent_generic_source_sha256=review['source_sha256'],
                witness=p,elapsed_seconds=time.monotonic()-started,
                scope='New constructively defined fixed rational metric basis/table for the promoted actual descendant frames. No giant h51 basis/table/prime is instantiated or runtime adapter executed. Direct strict characteristic and independent stronger positive-exp witness agree; general-beta final assembly and p^66000 reservoir remain required.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],p['saving'],p['saving_decimal_lower'],flush=True)


if __name__=='__main__':main()
