#!/usr/bin/env python3
"""Exact source-frame relocation screen on the accepted closing counts.

This is a separate analytic candidate. A complete source/sink and common-
basis transfer audit must approve the new middle projector before assembly.
No new PR complex histogram or runtime interface is assumed.
"""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

from downstream_gaussian import network_counts,require
from downstream_parameter_optimum import as_strings
from downstream_rotated_batch_characteristic import log_bounds
from downstream_whole_complex_semantic_bulk import check_sources


def sha(path):return sha256(path.read_bytes()).hexdigest()


def normalized(counts,hist):
    m,s,D=counts['m'],counts['s'],counts['D'];lm=log_bounds(m)
    require(sum(r*c for r,c in hist.items())==s,'Complete normalized child rank sum differs')
    logs={r:log_bounds(r) for r in hist if r>1}
    M=sum(r*c*logs[r][0] for r,c in hist.items() if r>1)
    linear=s*lm[1]-M;quad=Q(s,2)*lm[1]**2
    gap=lambda a:D-a*linear-a*a*quad/(1-a*lm[1])
    lo,hi=Q(0),Q(1,10000)
    require(hi*lm[1]<1 and gap(lo)>0>gap(hi),'Normalized root bracket failed')
    for _ in range(100):
        mid=(lo+hi)/2
        if gap(mid)>0:lo=mid
        else:hi=mid
    a=Q(lo.numerator*10**24//lo.denominator,10**24)
    require(gap(a)>0,'Strict normalized saving failed')
    return dict(saving=a,strict_taylor_gap=gap(a),root_bracket=[lo,hi],
        taylor_linear_coefficient=linear,taylor_quadratic_coefficient=quad,
        rank_log_moment_lower=M,logarithm_intervals={'m':list(lm),**{str(r):list(pair) for r,pair in logs.items()}},
        child_histogram={str(r):c for r,c in sorted(hist.items())},
        inequality='D-a*(s*ln(m)_U-M_L)-a^2*s*ln(m)_U^2/[2*(1-a*ln(m)_U)]>0')


def bit_characteristic(h,R,protected):
    n=network_counts(h,R);v,m=n['v'],n['m'];J=(R+h)*v*v
    n['L']-=3*protected*v*v;n['D']+=6*protected*v*v;n['s']-=6*protected*v*v
    n['eta']=Q(n['D'],n['W']*m)
    kernels=dict(middle=h,joined=2*h,data=h*h+h-1)
    runs={k:m-2*d for k,d in kernels.items()};copies=dict(middle=J,joined=J,data=2*n['N'])
    hist={}
    for k,r in runs.items():hist[r]=hist.get(r,0)+copies[k]
    long_rank=sum(r*c for r,c in hist.items());individual=n['s']-long_rank
    require(individual>0,'New source-frame grouped union exceeds actual rank sum');hist[1]=individual
    p=normalized(n,hist);maximum=max(runs.values());depth=1
    while m**depth<=2*maximum**depth:depth+=1
    p.update(certificate_kind='SOURCE-FRAME MIDDLE RELOCATION, GENERIC METRIC FLAGS, NORMALIZED POSITIVE EXPONENTIAL',
        h=h,roles=R,protected_centers=protected,counts=n,kernel_dimensions=kernels,grouped_runs=runs,
        family_multiplicities=copies,family_ranks={k:copies[k]*(m-kernels[k]) for k in kernels},
        source_frame_relocation=dict(copies=J,old_entrance_rank=h*h-h,old_exit_rank=m-h*h,
            new_entrance_rank=0,new_exit_rank=m-h,rank_sum_unchanged=True),
        maximum_child_rank=maximum,depth_per_ceil_log2e=depth,W_binary_upper_exponent=n['W'].bit_length(),
        changed_native_table_prime_required=True,giant_basis_table_prime_materialized=False)
    return p


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--closing-assembly',type=Path,required=True)
    ap.add_argument('--source-frame-checkout',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path');t=time.monotonic()
    revision=subprocess.check_output(['git','-C',str(args.source_frame_checkout),'rev-parse','HEAD'],text=True).strip()
    require(revision=='3ef246fa4f69c87ebfed78376418afa9ffcad145','Pinned PR13 revision differs')
    old=json.loads(args.closing_assembly.read_text());check_sources(old,Path(__file__).parent)
    oldp=old['generic_characteristics'];h,R=oldp[0]['h'],oldp[0]['roles']
    bits=[bit_characteristic(h,R,k) for k in (0,1,2)]
    nc=old['complex_counts_unchanged'];phase_old=old['witnesses'][0]['complex_branching_certificate']
    phase=normalized(nc,{int(r):c for r,c in phase_old['child_histogram'].items()})
    coarse_linear=nc['s']*10-Q(99,10)*phase_old['total_grouped_rank'];coarse_quad=Q(nc['s'],2)*100
    coarse_gap=lambda b:nc['D']-b*coarse_linear-b*b*coarse_quad/(1-10*b)
    coarse_probes={str(b):coarse_gap(b) for b in (Q(1,10**6),Q(13,10**7),Q(14,10**7),Q(2,10**6))}
    checks=[]
    for p in bits:
        a,b=p['saving'],phase['saving'];beta=(1-a/b)/2 if a<b else Q(1,2**64)
        tau,sigma=1-a,1-b;internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
        require(0<beta<1,'New source-frame beta infeasible')
        checks.append(dict(protected_centers=p['protected_centers'],a=a,b=b,beta=beta,
            internal_saving=1-internal,leaf_saving=1-leaf,
            fixed_beta_saving_cap=min(1-internal,1-leaf),
            limiting_balanced_family_upper=min(a,b)/(1+min(a,b)),
            source_frame_interface_unreviewed=True))
    result=dict(status='PASS EXACT SOURCE-FRAME NUMERICAL CANDIDATE; NEW TRANSFER AND COMPLETE ASSEMBLY REQUIRED',
        generated_utc=datetime.now(timezone.utc).isoformat(),campaign_start='2026-10-07T22:25:21Z',
        historical_deadline='2026-10-08T08:25:21Z',active_deadline='2026-10-08T10:00:00Z',
        source_sha256={name:sha(Path(__file__).with_name(name)) for name in
            (Path(__file__).name,'downstream_rotated_batch_characteristic.py','downstream_gaussian.py')},
        input_sha256={str(args.closing_assembly):sha(args.closing_assembly)},
        source_frame_pr=dict(url='https://github.com/CrocSwap/integer-mult-bounds/pull/13',commit=revision,checkout=str(args.source_frame_checkout)),
        bit_characteristics=bits,complex_same_accepted_histogram=phase,
        complex_coarse_probes=coarse_probes,general_beta_probes=checks,
        old_complex_histogram_unchanged=True,new_pr_complex_classes_imported=False,
        scope='Exact changed middle moment on accepted actual closing counts, pending new source/sink and common-basis proof. The complex witness is recertified on precisely the accepted three-family histogram; no all-rank or PR-controlled complex transfer is imported. Different maximum bit child requires fresh depth, product-stock, guard and full assembly. These parameter caps are candidate arithmetic, not an accepted multiplication exponent.',
        elapsed_seconds=time.monotonic()-t)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],[(p['protected_centers'],p['saving'],p['depth_per_ceil_log2e']) for p in bits],phase['saving'],flush=True)


if __name__=='__main__':main()
