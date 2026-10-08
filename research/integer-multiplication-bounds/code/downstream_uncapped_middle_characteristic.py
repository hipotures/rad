#!/usr/bin/env python3
"""Exact grouped characteristic keeping the full rotated middle runs.

The fixed rational basis/table is the accepted (3,1,2) choice. Longer
middle children change the rank characteristic and row depth, not roles.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

from downstream_gaussian import ceil_q, require
from downstream_parameter_optimum import as_strings, rational_decimal_lower
from downstream_rotated_batch_characteristic import log_bounds, rotated


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def uncapped_middle(h, roles, variant):
    require(variant in ('two-family', 'tensor-data'), 'Unknown uncapped variant')
    p = rotated(h, roles, variant)
    n, v, m = p['counts'], p['counts']['v'], p['counts']['m']
    histogram = {}
    old_moment = Q(0)
    for a in range(h-2):
        copies = (roles+h)*v*comb(h-a-1, 2)
        for base in (a, h-a-2, 1):
            if base:
                width = base*h*h
                histogram[width] = histogram.get(width, 0)+copies
                old_moment += copies*h*h*base*log_bounds(base)[0]
    require(sum(r*c for r,c in histogram.items()) == p['middle_old_rank'],
            'Uncapped middle rank does not conserve every pivot')
    maximum = max(histogram)
    require(maximum == h*h*(h-2) < m, 'Uncapped child is not strictly smaller')
    middle_moment = p['middle_rank_log_sum_lower']+old_moment
    total_moment = middle_moment+p['joined_rank_log_sum_lower']+p['data_rank_log_sum_lower']
    lm = log_bounds(m)[1]
    linear = n['W']*m*lm-total_moment
    quadratic = Q(n['s'],2)*lm*lm
    require(linear>0 and old_moment>0, 'Invalid uncapped characteristic')
    gap = lambda a: n['D']-a*linear-a*a*quadratic
    lo,hi = Q(0),Q(1,10**7)
    require(gap(lo)>0>gap(hi), 'Characteristic root bracket failed')
    for _ in range(96):
        mid = (lo+hi)/2
        if gap(mid)>0: lo=mid
        else: hi=mid
    saving = Q(lo.numerator*10**24//lo.denominator,10**24)
    require(gap(saving)>0 and saving>Q(p['saving']), 'No strict uncapping improvement')
    result = dict(p)
    result.update(certificate_kind='UNCAPPED ROTATED MIDDLE + JOINED/TENSOR DATA',
                  middle_batch_histogram={str(r):c for r,c in sorted(histogram.items())},
                  middle_rank_log_sum_lower=middle_moment,
                  additional_middle_rank_log_sum_lower=old_moment,
                  middle_batch_calls=sum(histogram.values()),
                  middle_child_rank='Positive a*h^2, (h-a-2)*h^2, h^2 runs',
                  maximum_child_rank=maximum,child_ratio=Q(h-2,h),
                  child_width_relation='r*floor(e/m)<=(1-2/h)*e',
                  row_depth='ceil(log_(h/(h-2)) e)<=ceil((h/2)*ln(e))',
                  depth_multiplier_log2=ceil_q(Q(h,2)),
                  taylor_linear_coefficient=linear,taylor_quadratic_coefficient=quadratic,
                  saving=saving,saving_decimal_lower=rational_decimal_lower(saving,18),
                  strict_taylor_gap=gap(saving),root_bracket=[lo,hi],
                  capped_predecessor_saving=Q(p['saving']),
                  above_two_power_minus_27=saving>Q(1,2**27))
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--capped-characteristic',type=Path,required=True)
    ap.add_argument('--finite-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic()
    old=json.loads(args.capped_characteristic.read_text())
    review=json.loads(args.finite_review.read_text())
    require(review['status'].startswith('PASS'),'New finite review is not terminal PASS')
    full=review['full']; h=full['h']; roles=full.get('roles',full.get('compiled_roles'))
    require(h==51 and roles==500703,'This promotion interface pins h51 R500703')
    require(full['every_mapped_frame_has_exact_canonical_core_and_support'],
            'Promoted clone lacks the complete frame map control')
    rows=[uncapped_middle(h,roles,v) for v in ('two-family','tensor-data')]
    for key in ('v','m','N','W','L','D','s'):
        require(full['exact_counts'][key]==rows[0]['counts'][key],
                'Promoted clone count differs '+key)
    require(full['logical']['all_global_coefficients_exact'] and
            full['logical']['all_additions_disjoint'] and
            full['logical']['all_source_spans_have_common_point'] and
            full['stage_matching']['explicit_inverse_and_bijection'] and
            full['stage_matching']['intersection_one'] and
            full['stage_matching']['rational_form_nondegenerate'],
            'Promoted scalar, frame or matching control failed')
    require(full['physical']['every_gate_output_exact'] and
            full['physical']['every_physical_target_exact'] and
            full['rational_frames']['forward_and_reverse_complement_nesting'] and
            full['rational_frames']['every_designated_target_orthogonal'] and
            full['controller_plan']['independently_counted_roles']==roles and
            full['literal_scalar_guard']['slack']>0,
            'Promoted physical timeline or literal guard failed')
    require(all(r['exact_linear_map'] and r['input_basis_vectors']==4239
                for r in review['small_control']['complete_invocation_dirty_basis']) and
            len(review['small_control']['complete_invocation_dirty_basis'])==2,
            'Promoted complete dirty invocation controls absent')
    regressions=[];comparison=[]
    for p in old['witnesses']:
        require(as_strings(rotated(p['h'],p['roles'],p['variant']))==p,
                'Frozen capped characteristic differs')
        regressions.append(dict(variant=p['variant'],saving=p['saving'],unchanged=True))
        if p['variant'] in ('two-family','tensor-data'):
            comparison.append(uncapped_middle(p['h'],p['roles'],p['variant']))
    source_dir=Path(__file__).parent
    paths=(Path(__file__),source_dir/'downstream_rotated_batch_characteristic.py',
           source_dir/'downstream_gaussian.py')
    result=dict(status='PASS STRICT UNCAPPED MIDDLE CHARACTERISTICS; TRANSFER REVIEW REQUIRED',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
                generated_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256={p.name:sha(p) for p in paths},
                input_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p))
                             for p in (args.capped_characteristic,args.finite_review)},
                odd_bit_finite_audit=dict(status='INDEPENDENT FINITE PROMOTION PASS',
                    path=str(args.finite_review),sha256=sha(args.finite_review),
                    candidate_id=review['candidate_id'],compiled_sha256=full['compiled_sha256'],
                    h=h,roles=roles,counts=rows[0]['counts'],
                    reference_commit=review['reference_commit']),
                capped_regressions=regressions,old_uncapped_comparison=comparison,
                witnesses=rows,elapsed_seconds=time.monotonic()-started,
                scope='Full contiguous middle runs in the accepted fixed global basis, with strictly smaller variable-width children and deeper logarithmic row padding. Joined/exact-data profiles and complex guard unchanged. New promoted clone finite input is pinned; all-size uncapped transfer and complete assembly require independent review.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for group in ('old_uncapped_comparison','witnesses'):
        for row in result[group]:
            print(group,row['h'],row['roles'],row['variant'],row['saving'],
                  row['saving_decimal_lower'],'max',row['maximum_child_rank'],flush=True)


if __name__=='__main__':main()
