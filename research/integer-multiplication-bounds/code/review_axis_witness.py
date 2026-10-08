#!/usr/bin/env python3
"""Thin independent verification of explicit rotated producer witnesses.

Reuse the frozen independent profile proof; reconstruct each supplied
moment/count and a stronger exact characteristic without producer imports.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import sys
import time

from review_parameter_audit import log_integer
from review_pivot_batching import stringify
from review_pivot_extension import line_projector


def universal_kernel_controls():
    checked=0
    for h, first, second in ((6,(0,1,2),(3,4,5)),(8,(3,6,7),(0,2,6))):
        Pa,Pb=[line_projector(h,t) for t in (first,second)]
        support=[i*h+j for i in first for j in second]
        B=[[Q(int(a==i and b==j))-Pa[a][i]*Pb[b][j]
            for i in range(h) for j in range(h)] for a in range(h) for b in range(h)]
        assert all(sum(row[j] for j in support)==0 for row in B)
        checked+=len(B)
    return dict(exact_prefix_kernel_rows=checked,
                kernel='F tensor t1 tensor t2 after global cycle',
                holes='i*h^2+h*min(t1)+min(t2)',
                consequence='all universal data increasing runs<=h^2-1',
                old_third_factor_kernel_not_reused=True)


def main():
    sys.set_int_max_str_digits(0)
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--axis-review',type=Path,required=True)
    ap.add_argument('--producer',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    started=time.monotonic()
    old=json.loads(args.axis_review.read_text());p=json.loads(args.producer.read_text())
    assert old['status']=='PASS independent global-axis batching construction'
    for name,digest in old['source_sha256'].items():
        assert sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    assert p['status'].startswith('PASS PROSPECTIVE GLOBAL-AXIS')
    assert p['finite_input']['sha256']==old['finite_review_sha256']
    assert p['source_sha256']==sha256(Path(__file__).with_name('downstream_rotated_batch_characteristic.py').read_bytes()).hexdigest()
    n=old['rows'][0]['counts'];h,m,R,v=[n[k] for k in ('h','m','side_roles','v')]
    moment_middle=Q(old['rows'][0]['middle_moment_lower'])
    moment_joined=Q(old['rows'][0]['joined_moment_lower'])
    exact_data=Q(old['rows'][2]['data_moment_lower'])
    r3=(h*h-1)*(h-1);d3=m-r3;t3=m-2*d3;g3=2*d3+1
    universal_data=2*n['N']*t3*(log_integer(t3,64)[0]-log_integer(g3,64)[1])
    lm=log_integer(m,64)[1]
    expected_hist=Counter()
    multiplier=2*v*(h-1)
    for a in range(h-2):
        for b in range(h-2):
            count=multiplier*comb(h-a-1,2)*comb(h-b-1,2)
            for r in (h*a+b,h*h-h*a-b-2,1):
                if r:expected_hist[r]+=count
    assert sum(r*count for r,count in expected_hist.items())==2*n['N']*r3
    rows=[]
    for supplied in p['witnesses']:
        for key,value in n.items():assert supplied['counts'][key]==value
        variant=supplied['variant']
        assert variant in ('two-family','universal-data','tensor-data')
        assert supplied['compiler_basis_order']==[3,1,2]
        assert supplied['middle_child_rank']==supplied['maximum_child_rank']==h*h
        assert supplied['joined_run_bound']==4*h+1 and supplied['joined_minimum_diagonal']==m-4*h
        assert supplied['joined_maximum_diagonal_run']==h*h-1
        assert supplied['middle_batch_calls']==(R+h)*v*v*(h-1)
        assert supplied['middle_old_rank']==old['rows'][0]['middle_old_rank']
        assert supplied['joined_old_rank']==old['rows'][0]['joined_old_rank']
        data_moment={'two-family':Q(0),'universal-data':universal_data,'tensor-data':exact_data}[variant]
        expected_data_rank=0 if variant=='two-family' else 2*n['N']*r3
        assert supplied['data_old_rank']==expected_data_rank
        assert supplied['middle_old_rank']+supplied['joined_old_rank']+expected_data_rank+supplied['other_unchanged_rank']==n['s']
        assert Q(supplied['middle_rank_log_sum_lower'])<=moment_middle
        assert Q(supplied['joined_rank_log_sum_lower'])<=moment_joined
        assert Q(supplied['data_rank_log_sum_lower'])<=data_moment
        if variant=='tensor-data':
            assert {int(k):value for k,value in supplied['data_batch_histogram'].items()}==dict(expected_hist)
        else:assert supplied['data_batch_histogram']=={}
        a=Q(supplied['saving']);first=n['s']*lm-moment_middle-moment_joined-data_moment
        assert 0<a*lm<1
        gap=n['D']-a*first-a*a*n['s']*lm*lm/(2*(1-a*lm))
        assert gap>0
        rows.append(dict(variant=variant,saving=a,strict_independent_characteristic_gap=gap,
                         reconstructed_middle_moment_lower=moment_middle,
                         reconstructed_joined_moment_lower=moment_joined,
                         reconstructed_data_moment_lower=data_moment,
                         exact_data_histogram_matches=variant=='tensor-data',
                         total_rank_conserved=True,global_maximum_run=h*h))
    names=('review_axis_witness.py','review_parameter_audit.py','review_pivot_extension.py','review_pivot_batching.py')
    result=dict(status='PASS independent explicit rotated primitive witnesses',
                generated_utc=datetime.now(timezone.utc).isoformat(),counts=n,rows=rows,
                source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
                input_sha256={str(path):sha256(path.read_bytes()).hexdigest() for path in (args.axis_review,args.producer)},
                replacement_universal_data_kernel=universal_kernel_controls(),
                scope='All-size source/table/tape transfer is the frozen global-axis review; this thin audit checks supplied explicit exponents and alternate kernel',
                wall_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(stringify(result),indent=2,sort_keys=True)+'\n')
    for row in rows:print('PASS explicit producer',row['variant'],row['saving'],flush=True)


if __name__=='__main__':main()
