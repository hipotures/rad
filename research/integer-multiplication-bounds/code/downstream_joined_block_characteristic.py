#!/usr/bin/env python3
"""Sharper moment of the already grouped reflected joined runs.

The scalar graph, fixed reflected table and maximum child are unchanged.
The proposed interior-block lemma, not a new physical gather, supplies
the extra logarithmic moment. Independent all-size review is required.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_gaussian import require
from downstream_householder_characteristic import householder
from downstream_parameter_optimum import as_strings,rational_decimal_lower
from downstream_rotated_batch_characteristic import log_bounds


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def joined_block(h,roles,variant):
    p=householder(h,roles,variant);n=p['counts'];m=n['m'];v=n['v']
    inner=h*h;isolated_count=h-2;isolated_length=inner-2
    isolated_mass=isolated_count*isolated_length
    remainder_mass=m-4*h-isolated_mass;remainder_runs=3*h+3
    require(remainder_mass>remainder_runs>0,'Joined remainder monotonicity failed')
    moment_per_join=(isolated_mass*log_bounds(isolated_length)[0]+
                    remainder_mass*(log_bounds(remainder_mass)[0]-log_bounds(remainder_runs)[1]))
    copies=(roles+h)*v*v;moment=copies*moment_per_join
    require(moment>p['joined_rank_log_sum_lower'],'No strict joined moment improvement')
    lm=log_bounds(m)[1]
    linear=n['W']*m*lm-p['middle_rank_log_sum_lower']-moment-p['data_rank_log_sum_lower']
    quadratic=Q(n['s'],2)*lm*lm
    gap=lambda a:n['D']-a*linear-a*a*quadratic
    lo,hi=Q(0),Q(1,10**7)
    require(linear>0 and gap(lo)>0>gap(hi),'Joined root bracket failed')
    for _ in range(96):
        mid=(lo+hi)/2
        if gap(mid)>0:lo=mid
        else:hi=mid
    saving=Q(lo.numerator*10**24//lo.denominator,10**24)
    require(gap(saving)>0 and saving>p['saving'],'No strict joined saving improvement')
    out=dict(p)
    out.update(certificate_kind='REFLECTED JOINED INTERIOR-BLOCK MOMENT',
               isolated_joined_runs=isolated_count,isolated_joined_run_length=isolated_length,
               isolated_joined_rank=isolated_mass,
               remaining_joined_diagonal_lower=remainder_mass,
               remaining_joined_run_upper=remainder_runs,
               joined_rank_log_sum_lower=moment,
               previous_universal_joined_moment=p['joined_rank_log_sum_lower'],
               added_joined_rank_log_sum_lower=moment-p['joined_rank_log_sum_lower'],
               joined_bound='h-2 isolated exact local runs h^2-2 plus Jensen remainder',
               taylor_linear_coefficient=linear,taylor_quadratic_coefficient=quadratic,
               saving=saving,saving_decimal_lower=rational_decimal_lower(saving,18),
               strict_taylor_gap=gap(saving),root_bracket=[lo,hi],
               universal_joined_predecessor_saving=p['saving'],
               above_two_power_minus_26=saving>Q(1,2**26))
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--householder-characteristic',type=Path,required=True)
    ap.add_argument('--block-controls',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic();old=json.loads(args.householder_characteristic.read_text())
    controls=json.loads(args.block_controls.read_text());source_dir=Path(__file__).parent
    for name,digest in old['source_sha256'].items():
        require(sha(source_dir/name)==digest,'Frozen reflected source differs '+name)
    require(controls['status'].startswith('PASS') and
            controls['spike_inside_interior_discriminated'] and
            controls['dense_first_coordinate_prerequisite_discriminated'],
            'Small joined controls or negative qualifications failed')
    require(sha(source_dir/'downstream_joined_block_profile.py')==controls['source_sha256'],
            'Executed exact joined profile source changed')
    require(all(r['lower_concentration_profile_invariant'] and
                r['interior_local_profiles_exact'] and len(r['forced_maximal_diagonal_runs'])==r['h']-2
                for r in controls['cases']),
            'Complete exact joined profiles failed')
    regressions=[];rows=[]
    for p in old['witnesses']:
        require(as_strings(householder(p['h'],p['roles'],p['variant']))==p,
                'Historical universal joined characteristic differs')
        regressions.append(dict(variant=p['variant'],saving=p['saving'],unchanged=True))
        rows.append(joined_block(p['h'],p['roles'],p['variant']))
    hashes=dict(old['source_sha256']);hashes[Path(__file__).name]=sha(Path(__file__))
    hashes['downstream_joined_block_profile.py']=controls['source_sha256']
    result=dict(status='PASS STRICT JOINED BLOCK CHARACTERISTICS; INDEPENDENT ALL-SIZE REVIEW REQUIRED',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
                generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
                input_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in
                             (args.householder_characteristic,args.block_controls)},
                odd_bit_finite_audit=old['odd_bit_finite_audit'],
                universal_joined_regressions=regressions,witnesses=rows,
                elapsed_seconds=time.monotonic()-started,
                scope='Sharper logarithmic moment estimate for already grouped joins in the accepted fixed reflected program. No graph, role, factor-table, runtime transform, child maximum or row-depth change. Independent all-size block proof and complete assembly remain required.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for p in rows:print(result['status'],p['variant'],p['saving'],p['saving_decimal_lower'],flush=True)


if __name__=='__main__':main()
