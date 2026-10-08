#!/usr/bin/env python3
"""Prospective disjoint stage3 data-edge extension of two-family batching.

Projection and kernel-hole premises are recorded, not silently promoted.
The safe capped and optional kernel-hole rows preserve earlier sources.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_diagonal_batch_capped_bound import capped
from downstream_diagonal_batch_join_bound import joint
from downstream_gaussian import log_integer_bounds
from downstream_parameter_optimum import as_strings, rational_decimal_lower


def data_extension(h, roles, variant):
    old = capped(h, roles) if variant == 'capped' else joint(h, roles)
    n = old['counts'];m=n['m']
    rank = (h * h - 1) * (h - 1)
    defect = m - rank
    assert defect == h * h + h - 1
    count = 2 * n['N']
    diagonal = m - 2 * defect
    pieces = 2 * defect + 1
    if variant == 'capped':
        pieces += (rank + h * h - 1) // (h * h)
        maximum_child_rank = h * h
    else:
        assert variant == 'kernel-holes'
        # Existing join holes are h^2 apart; these data residuals have a
        # kernel line in every h-column block, so their runs are <=h-1.
        maximum_child_rank = h * h - 1
    assert diagonal > pieces and count * rank <= old['other_unchanged_rank']
    dl, _ = log_integer_bounds(diagonal)
    _, gh = log_integer_bounds(pieces)
    data_log_sum_lower = count * diagonal * (dl - gh)
    linear = old['taylor_linear_coefficient'] - data_log_sum_lower
    quadratic = old['taylor_quadratic_coefficient']
    assert linear > 0 and quadratic > 0
    gap = lambda a: n['D'] - a * linear - a * a * quadratic
    lo, hi = Q(0), Q(1, 100000000)
    assert gap(lo) > 0 and gap(hi) < 0
    for _ in range(80):
        mid = (lo + hi) / 2
        if gap(mid) > 0:
            lo = mid
        else:
            hi = mid
    saving = Q(lo.numerator * 10 ** 24 // lo.denominator, 10 ** 24)
    assert gap(saving) > 0 and saving > old['saving']
    return dict(variant=variant,h=h,roles=roles,counts=n,data_edge_count=count,
                data_edge_rank=rank,data_rank_defect=defect,
                data_minimum_diagonal_pivots=diagonal,data_maximum_run_pieces=pieces,
                data_rank_log_sum_lower=data_log_sum_lower,
                previous_join_and_middle_rank=old['joined_old_rank']+old['middle_old_rank'],
                data_old_rank=count*rank,other_unchanged_rank=old['other_unchanged_rank']-count*rank,
                maximum_child_rank=maximum_child_rank,child_ratio_bound=Q(1,h),
                taylor_linear_coefficient=linear,taylor_quadratic_coefficient=quadratic,
                saving=saving,saving_decimal_lower=rational_decimal_lower(saving,18),
                strict_taylor_gap=gap(saving),root_bracket=[lo,hi],
                previous_two_family_saving=old['saving'],strict_gain=saving-old['saving'],
                kernel_premises=(['Joined A annihilates F tensor t_A tensor t_B; one leading kernel column per h^2 block',
                                  'Stage3 data residual B tensor t_Y^perp annihilates F tensor F tensor t_Y; one leading kernel column per h block']
                                 if variant=='kernel-holes' else []))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h',type=int,required=True)
    ap.add_argument('--roles',type=int,required=True)
    ap.add_argument('--finite-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists(),'Use a fresh output path'
    review=json.loads(a.finite_review.read_text())
    assert review['status']=='PASS' and review['full']['h']==a.h
    assert review['full'].get('compiled_roles',review['full'].get('roles'))==a.roles
    started=time.monotonic();rows=[data_extension(a.h,a.roles,v) for v in ('capped','kernel-holes')]
    names=('downstream_diagonal_batch_data_bound.py','downstream_diagonal_batch_capped_bound.py',
           'downstream_diagonal_batch_join_bound.py','downstream_diagonal_batch_subset.py')
    result=dict(status='PASS PROSPECTIVE THREE-FAMILY DIAGONAL-BATCH SCREEN',
                generated_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256={n:sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in names},
                finite_input=dict(path=str(a.finite_review),sha256=sha256(a.finite_review.read_bytes()).hexdigest()),
                witnesses=rows,elapsed_seconds=time.monotonic()-started,
                scope='Disjoint two stage3 data families supplement earlier middle and join bounds. Safe capped and kernel-hole variants are separate; full physical projection/axis order, tape, row reservation and recursive transfer remain independent obligations.')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:print(result['status'],row['variant'],row['saving'],row['saving_decimal_lower'],flush=True)


if __name__=='__main__':main()
