#!/usr/bin/env python3
"""Independent complete assembly for a reflected tensor basis.

The retained algebra comes from an independent assembly reviewer. The
changed native moment is independently reconstructed with64-term exact
logs and outward 320-bit dyadic bounds. No producer is imported.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path
import resource
import time

from review_asymmetric_motif import independent_saving
from review_parameter_audit import log_integer
from review_packed_unrolling import finite_counts
from review_semantic_bulk_assembly import ceil_q, complex_counts, power_certificate, require


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


@cache
def bounds(n):
    lo, hi = log_integer(n, 64)
    scale = 2**320
    lower = Q(lo.numerator*scale//lo.denominator, scale)
    upper = Q(-((-hi.numerator*scale)//hi.denominator), scale)
    require(lower <= lo <= hi <= upper, 'Independent dyadic rounding failed')
    return lower, upper


def audit_primitive(p):
    n=finite_counts(p['counts']);h,roles=p['h'],p['roles']
    require(h==51 and roles==500703 and p['variant']=='tensor-data','Unexpected reflected input')
    v,m=comb(h,3),h**3;copies=(roles+h)*v*v
    u_in,u_out=1-Q(6,h),-Q(6,h)
    v_out=Q(h-18,6*h);v_in=Q(1,2)+v_out
    require(all(x!=0 for x in (u_in,u_out,v_in,v_out)) and
            3*u_in*v_in+(h-3)*u_out*v_out==1 and
            u_in*v_in+2*u_in*v_out+2*u_out*v_in+(h-5)*u_out*v_out==0,
            'Reflected source normalization or intersection-one orthogonality failed')
    alpha=Q(2,h)
    require(-2*alpha+h*alpha*alpha==0,'Q involution coefficient differs')
    middle_histogram={h*h:copies,h*h*(h-2):copies}
    data_count=2*n['N']*(h-1);data_histogram={1:data_count,h*h-2:data_count}
    middle_rank=copies*h*h*(h-1);joined_rank=copies*(m-2*h);data_rank=data_count*(h*h-1)
    require(sum(r*c for r,c in middle_histogram.items())==middle_rank and
            sum(r*c for r,c in data_histogram.items())==data_rank,'Complete reflected rank lost')
    for name,histogram in [('middle',middle_histogram),('data',data_histogram)]:
        require({str(k):v for k,v in sorted(histogram.items())}==p[name+'_batch_histogram'],
                'Independent uniform reflected histogram differs '+name)
    middle=sum((r*c*bounds(r)[0] for r,c in middle_histogram.items()),Q(0))
    data=sum((r*c*bounds(r)[0] for r,c in data_histogram.items()),Q(0))
    joined=copies*(m-4*h)*(bounds(m-4*h)[0]-bounds(4*h+1)[1])
    require(p['compiler_basis']=='Cycle(3,1,2)*(Q tensor Q tensor Q), Q=I-2J/h' and
            p['ground_metric']=='H=I-J/9' and
            p['middle_old_rank']==middle_rank and p['joined_old_rank']==joined_rank and
            p['data_old_rank']==data_rank and
            p['other_unchanged_rank']==n['s']-middle_rank-joined_rank-data_rank>0 and
            p['joined_minimum_diagonal']==m-4*h and p['joined_run_bound']==4*h+1 and
            p['maximum_child_rank']==h*h*(h-2) and Q(p['child_ratio'])==Q(h-2,h),
            'New reflected native profile multiplicities or proper child bounds differ')
    line=p['reflected_line']
    require(all(Q(line[k])==x for k,x in [('u_in',u_in),('u_out',u_out),('v_in',v_in),('v_out',v_out)]),
            'Explicit ground source/dual coefficients differ')
    lm=bounds(m)[1];linear=n['W']*m*lm-middle-joined-data;quadratic=Q(n['s'],2)*lm*lm
    saved_linear,saved_quadratic=(Q(p[k]) for k in ('taylor_linear_coefficient','taylor_quadratic_coefficient'))
    a=Q(p['saving']);require(a==Q(13047622335460119,10**24),'Unexpected strict reflected saving')
    require(saved_linear>=linear>0 and saved_quadratic>=quadratic>0,'Independent moments do not support saved coefficients')
    gap=n['D']-a*saved_linear-a*a*saved_quadratic;independent_gap=n['D']-a*linear-a*a*quadratic
    require(gap==Q(p['strict_taylor_gap'])>0 and independent_gap>=gap,'Reflected strict characteristic failed')
    return dict(chosen_saving=str(a),exact_total_rank=n['s'],middle_rank=middle_rank,
                joined_rank=joined_rank,data_rank=data_rank,maximum_child_rank=h*h*(h-2),
                logarithm_terms=64,outward_dyadic_bits=320,independent_taylor_gap=str(independent_gap),
                saved_strict_gap=str(gap),new_reflected_table_and_fixed_prime_required=True)


def audit_row(row, old_tight, primitive):
    n=finite_counts(row['bit_counts']);nc=complex_counts(row['complex_counts'])
    p={k:Q(v) for k,v in row['parameters'].items()}
    a,b,tau,sigma,c,beta,eps,lam,lp,r,delta,kappa=(p[k] for k in
        ('a_bit','a_complex','tau','sigma','c','beta','epsilon','lambda_',
         'lambda_prime','alpha_squared_power','delta','kappa'))
    log_records={}
    primitive_gaps={}
    for name,counts,chosen in (('complex',nc,b),):
        lower,upper=independent_saving(counts['eta'],counts['m'])
        enc=row[name+'_saving_enclosure']
        require(Q(enc['saving_lower'])<lower<upper<Q(enc['saving_upper']),
                'Longer independent logarithm not inside saved enclosure')
        require(0<chosen<lower and chosen==Q(enc['chosen_saving']),
                'Primitive chosen saving exceeds independent bound')
        primitive_gaps[name+'_primitive']=(Q(enc['negative_log_deficit_lower'])-
                                           chosen*Q(enc['log_m_upper']))
        require(primitive_gaps[name+'_primitive']==Q(enc['strict_primitive_gap'])>0,
                'Saved logarithmic primitive strict slack differs')
        log_records[name]=dict(lower=str(lower),upper=str(upper),chosen_strict=True,
                                deficit_log_terms=20,radix_log_terms=48)
    require(a == Q(primitive['saving']), 'Explicit Taylor saving differs')
    eb = row['bit_saving_certificate']
    require(eb['certificate_kind'] == 'STRICT SECOND-ORDER BATCH CHARACTERISTIC, NOT UNIFORM SHRINK',
            'New primitive must not use a uniform rank-saving enclosure')
    require(Q(eb['chosen_saving']) == a and
            Q(eb['strict_primitive_gap']) == Q(primitive['strict_taylor_gap']) and
            Q(eb['taylor_linear_coefficient']) == Q(primitive['taylor_linear_coefficient']) and
            Q(eb['taylor_quadratic_coefficient']) == Q(primitive['taylor_quadratic_coefficient']),
            'Row primitive certificate differs from the reviewed Taylor input')
    primitive_gaps['bit_primitive'] = Q(primitive['strict_taylor_gap'])
    require(primitive_gaps['bit_primitive'] > 0, 'Explicit Taylor gap is not strict')
    require(tau==1-a and sigma==1-b and 0<a<b/2<Q(1,64),'Primitive order/half leaf branch invalid')
    require(beta==Q(1,2),'Semantic row must retain its half stopping threshold')
    h=Q(1,2**(20 if row['mode']=='conservative' else 64))
    require(row['mode'] in ('conservative','tight'),'Unknown fixed parameter mode')
    q=1-lp
    require(q==a*(1-2*h) and lam==(tau+lp)/2,'Strict layer/intermediate exponent differs')
    prefix=row['prefix']
    if prefix=='original':
        require(c==q*(1+h) and eps==(1-h)/(1+c+q),'Original prefix strict parameters differ')
        g1=1-eps*(1+c)
    else:
        require(prefix=='balanced','Unknown reviewed prefix interface')
        require(c==q+h/4 and eps==(1-h)/(1+q),'Balanced strict parameters differ')
        g1=1-eps
    G=eps*q
    require(r==(G+1-eps)/2 and delta==h/8,'Gaussian power/precision strict parameters differ')
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    reserve=max(1-c,Q(0))
    recurrence=dict(internal=internal,leaf=leaf,reservations=reserve)
    require(all(Q(row['recurrence'][k])==v for k,v in recurrence.items()),'Compact recurrence differs')
    E=64*(nc['W']+nc['m']+1)**3;B=nc['s']+E;C0=32*nc['m']*B*B
    require(p['C0']==C0 and p['C1']==1,'Linear semantic guard differs')
    require(12*nc['W']**3+4*nc['s']+4*nc['W']+4<E and C0>2*B+18,
            'Exact scalar charge or complete linear guard constant invalid')
    semantic=row['semantic_guard']
    require(all(Q(semantic[k])==v for k,v in dict(E=E,B=B,C0=C0,C1=1).items()),
            'Semantic proof input constants differ')
    require(Q(row['linear_guard_constant_slack'])==C0-(2*B+18), 'Saved linear constant slack differs')
    margins=dict(g1=g1,g2=a,g3=G,g4=a,g5=min(1-eps-delta,r-delta),
                 g6=1-eps-delta,g7=eps)
    require(all(Q(row['margins'][k])==v for k,v in margins.items()),'Complete seven-margin model differs')
    require(min(margins.values())==G==Q(row['minimum_margin']),'Layer is not the unique strict minimum')
    require(kappa==Q((G.numerator*10**40-1)//G.denominator,10**40),
            'Compact decimal witness is not the strict lower grid point')
    previous=Q(old_tight['parameters']['kappa'])
    require(Q(row['previous_accepted_kappa'])==previous,'Accepted generic previous witness differs')
    geometry=1-eps*(1+c)
    slacks=dict(**primitive_gaps,primitive_order=b-a,half_leaf_saving=b/2-q,
        c_positive=c,c_below_one=1-c,beta_positive=beta,beta_below_one=1-beta,
        epsilon_positive=eps,epsilon_below_one=1-eps,lambda_above_tau=lam-tau,
        lambda_above_sigma=lam-sigma,compact_internal=lam-internal,
        lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-reserve,
        linear_scalar_guard=1-eps,K_smaller_than_ell=geometry,K_dominates_log_p=eps*c,
        record_suffix_superpolynomial=1-eps,phase_local_cost=1-eps-delta,
        phase_boundary_cost=r-delta,gamma_sublinear=1-eps-r,
        cell_larger_than_band=eps-(1-r)/2,prime_interval_packing=1-eps,
        alpha_power=r,delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,
        prefix_vs_layer=g1-G,movement_vs_layer=a-G,exposure_vs_layer=a-G,
        gaussian_vs_layer=margins['g5']-G,scalar_vs_layer=margins['g6']-G,
        dimension_vs_layer=eps-G,absorption=G-kappa,improvement_over_accepted=kappa-previous,
        old_nonadjacent_synthetic_margin_fails=kappa-eps*a*c,
        old_separate_resampling_exposure_fails=kappa-a*(1-eps),
        small_field_exposure_vs_layer=1-eps-G,
        microbox_artificial_boundary_vs_layer=8-eps+r-delta-G)
    if prefix=='balanced':
        require(1-eps-G==h and 1-eps-r==h/2,'Balanced exact small scale gaps differ')
        if row['mode']=='tight':slacks['old_prefix_estimate_fails']=kappa-geometry
    else:require(g1-G==h,'Original exact prefix gap differs')
    require(set(slacks)==set(row['constraint_slacks']),'Declared complete constraint set differs')
    require(all(Q(row['constraint_slacks'][k])==v>0 for k,v in slacks.items()),
            'A complete strict assembly slack differs or is nonpositive')
    extra=dict(short_record_elementary_fallback=eps-a,
               gamma_constant_power_range=Q(1,4)-r,
               alpha_below_sqrt_p=1-r,lambda_prime_below_one=q,
               strict_recurrence_intermediate_gap=lp-lam)
    require(all(v>0 for v in extra.values()),'Additional router/Gaussian interface range failed')

    ka,km,kb=ceil_q(1/r),ceil_q(1/(eps*c)),ceil_q(1/(1-eps))
    cuts=dict(gamma=ceil_q(7/(1-eps-r)),logarithmic_alpha=16*ka*ka+1,
        full_guard=ceil_q(Q((2*C0).bit_length())/(1-eps)),
        phase_cell=ceil_q(9/(eps-(1-r)/2)),compact_controls=64*km*km+1,
        K_geometry=ceil_q(3/geometry),microbox_period=128*kb*kb+1,routing_reservoirs=14)
    cuts['common']=max(cuts.values())
    require(row['cutoff_log2_b']==cuts,'Independent exact numeric cutoffs differ')
    require(cuts['gamma']*(1-eps-r)>=7 and
            cuts['full_guard']*(1-eps)>=(2*C0).bit_length() and
            cuts['phase_cell']*(eps-(1-r)/2)>=9 and cuts['K_geometry']*geometry>=3,
            'Guard/gamma/cell/geometry cutoff inequalities fail')
    compact=row['strengthened_real_log_compact_cutoff']
    require(compact['k']==km and compact['L0']==cuts['compact_controls'] and
            compact['denominator_slope']==32 and compact['denominator_constant']==192,
            'Real-log compact-field proof parameters differ')
    require(cuts['compact_controls']>=2*km and cuts['microbox_period']>=2*kb,
            'Monotonic real-log derivative range not established')
    compact_proof=power_certificate(compact['strict_power_certificate'],
        cuts['compact_controls']//km,32*cuts['compact_controls']+192)
    period_proof=power_certificate(row['microbox_period_power_certificate'],
        cuts['microbox_period']//kb,16*cuts['microbox_period']+56)
    # An independent, stronger alpha certificate: p^r >8log2(b)+64.
    alpha_exp=cuts['logarithmic_alpha']//ka
    require(alpha_exp >= (8*cuts['logarithmic_alpha']+64).bit_length() and
            cuts['logarithmic_alpha']>=2*ka,'Linear-log alpha domination cutoff fails')
    # This ceiling applies only to the declared certified exponent a.
    # It is not an exclusion of stronger future finite/recurrence primitives.
    factor = 1 if prefix == 'balanced' else 2
    upper = a/(1+factor*a)
    require(Q(row['declared_exponent_parameter_upper']) == upper and kappa < upper,
            'Declared-exponent parameter cap differs')
    require(Q(row['achieved_fraction_of_parameter_upper']) == kappa/upper,
            'Declared cap attainment differs')
    padding = row['compact_row_padding']
    require(padding['status'].startswith('PASS') and padding['reciprocal_exponent_ceiling'] == kb and
            padding['real_log_lower'] == cuts['common'] and len(padding['checks']) == 6,
            'New recursive row-padding input differs')
    require(row['bit_counts']['W'] < 2**49 and cuts['common'] >= max(25, 2*kb),
            'New row divisor or real-log monotonicity range fails')
    row_checks = []
    for j, record in enumerate(padding['checks']):
        L = cuts['common']*2**j
        require(record['log2_b'] == L, 'Row-padding checkpoint differs')
        row_checks.append(power_certificate(record['strict_power_certificate'], L//kb, 10400*(L+8)))
    require(padding['fixed_eventual_setup'] ==
            'p>=max(2,C) for the retained layout constant C; finite native prime/table constants remain separate',
            'Unproved universal layout constant was introduced')
    require(padding['row_polynomial_degree'] == 2600 and
            padding['W_upper_binary_exponent'] == 49 and
            padding['maximum_child_rank'] == 51**2*49 and
            Q(padding['child_ratio']) == Q(49,51) and
            padding['depth'] == 'ceil(log_(51/49)e)<=26ceil(log2e)' and
            padding['inequality'] == 'b^(1-epsilon)>10400*(log2(b)+8)' and
            padding['row_divisor'] == 'W^depth<p^2600 for e<=C*p, p>=C and log2(p)>=25' and
            49*26*(2*25+1) < 2600*25,
            'New uncapped depth/row-reservoir contract differs')
    native=row['native_bit_primitive']
    require(native['certificate_kind']=='HOUSEHOLDER DENSE-LINE NEGATIVE-EXPONENTIAL TAYLOR' and
            Q(native['chosen_saving'])==a and Q(native['strict_taylor_gap'])==Q(primitive['strict_taylor_gap']) and
            native['compiler_basis']=='Cycle(3,1,2)*(Q tensor Q tensor Q), Q=I-2J/51' and
            native['simultaneous_frame_conjugation']=='Every source, gate, sink and incidence' and
            native['maximum_child_rank']==51**2*49 and Q(native['child_ratio'])==Q(49,51) and
            native['depth']=='ceil(log_(51/49)e)<=26ceil(log2e)' and
            native['row_divisor']=='W^depth<p^2600 after p>=C and log2p>=25',
            'Complete reflected native basis/child/depth contract differs')
    require(native['factor_table']=='New fixed rational Bruhat table for all reflected frames' and
            native['native_prime']=='A newly fixed admissible odd prime for the full reflected table; no numerical equality with the old prime is assumed' and
            native['complex_guard']=='Original h28 R97586 network and semantic C0/C1 unchanged',
            'New reflected table/odd prime and separate complex guard scope differs')
    require(Q(row['strict_gain'])==kappa-previous and
            Q(row['improvement_ratio'])==kappa/previous and
            Q(row['compact_upstream_ratio'])==kappa/Q(83,10**12),
            'Improvement/count comparison differs')
    return dict(mode=row['mode'],prefix=prefix,kappa=str(kappa),minimum_margin=str(G),
        complete_declared_strict_conditions=len(slacks),additional_interface_conditions=len(extra),
        bit_roles=row['bit_counts']['side_roles'],complex_ground=nc['h'],complex_roles=nc['R'],
        independent_log_enclosures=log_records,cutoffs=cuts,
        compact_power=compact_proof,microbox_period_power=period_proof,
        logarithmic_alpha_power=dict(exponent=alpha_exp,
            right_bit_length=(8*cuts['logarithmic_alpha']+64).bit_length(),strict=True),
        declared_exponent_parameter_upper=str(upper),
        row_padding_compressed_checks=row_checks,
        ratio_to_83_over_10_to_12=str(kappa/Q(83,10**12)),
        old_unproved_estimates_reject_this_witness=True,
        enormous_power_allocation_performed=False)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('certificate','previous','previous-review','primitive','reflection-review','output'):
        ap.add_argument('--'+name,type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh result path');start=time.monotonic()
    files=[args.certificate,args.previous,args.previous_review,args.primitive,args.reflection_review]
    hashes={str(p):digest(p) for p in files}
    data=json.loads(args.certificate.read_text());old=json.loads(args.previous.read_text())
    previous_review=json.loads(args.previous_review.read_text());primitive=json.loads(args.primitive.read_text())
    peer=json.loads(args.reflection_review.read_text())
    require(previous_review['status'].startswith('PASS') and
            previous_review['input_sha256'][str(args.previous)]==digest(args.previous),
            'Previous uncapped complete assembly lacks independent arithmetic')
    require(data['reflected_characteristic_certificate']==primitive and
            data['independent_reflection_review_sha256']==digest(args.reflection_review) and
            primitive['independent_reflected_review_sha256']==digest(args.reflection_review),
            'Reflected native primitive or complete all-size review differs')
    identity=data['odd_bit_finite_audit']
    require(identity==old['odd_bit_finite_audit']==previous_review['promoted_finite_identity'] and
            identity['roles']==500703 and peer['finite_candidate_id']==identity['candidate_id'] and
            peer['finite_compiled_sha256']==identity['compiled_sha256'],
            'Reflected construction changed accepted finite scalar graph identity')
    require(data['promoted_complex_audit']==old['promoted_complex_audit']==previous_review['unchanged_complex_audit'],
            'Accepted separate complex input differs')
    require(peer['status'].startswith('PASS') and peer['new_address_table'] and peer['no_runtime_basis_adapter'] and
            peer['separate_complex_scalar_guard_unchanged'] and peer['retained_uncapped_row_degree']==2600 and
            peer['whole_common_frame_controls']['exact_reflected_source_gate_sink_pipeline'] and
            peer['whole_common_frame_controls']['omitted_one_conjugation_discriminated']>0,
            'Full simultaneous reflected interface and negative control not independently accepted')
    for name,expected in data['source_sha256'].items():
        require(digest(Path(__file__).with_name(name))==expected,'Frozen producer source changed '+name)
    for path in (args.previous,args.primitive,args.reflection_review):
        require(any(record['sha256']==hashes[str(path)] for record in data['input_files'].values()),
                'Assembler input hash absent '+path.name)
    old_best=max(old['witnesses'],key=lambda row:Q(row['parameters']['kappa']))
    require(Q(data['previous_accepted_kappa'])==Q(old_best['parameters']['kappa']),'Prior accepted comparison differs')
    p=next(record for record in primitive['witnesses'] if record['variant']=='tensor-data')
    native=audit_primitive(p);rows=[]
    for row in data['witnesses']:
        require(row['bit_counts']==p['counts'] and row['complex_counts']==old_best['complex_counts'] and
                row['batch_variant']=='reflected-tensor-data','New reflected finite inputs differ')
        checked=audit_row(row,old_best,p);checked['batch_variant']=row['batch_variant'];rows.append(checked)
    require({(r['mode'],r['prefix']) for r in rows}==set(product(('conservative','tight'),('original','balanced'))),
            'Complete four reflected rows missing')
    names=('review_householder_assembly.py','review_uncapped_assembly.py','review_asymmetric_motif.py',
           'review_parameter_audit.py','review_packed_unrolling.py','review_semantic_bulk_assembly.py')
    result=dict(status='PASS independent complete reflected-basis conditional assembly',campaign='20261007T222521Z',
        generated_utc=datetime.now(timezone.utc).isoformat(),input_sha256=hashes,
        reviewer_source_sha256={name:digest(Path(__file__).with_name(name)) for name in names},
        exact_primitive_audit=native,rows=rows,unchanged_finite_identity=identity,
        unchanged_complex_audit=data['promoted_complex_audit'],wall_seconds=time.monotonic()-start,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limitations=['Conditional written reviewed all-size interfaces; not formal/unconditional theorem or novelty claim',
          'New fixed reflected rational table, eligible odd prime, layoutC and full setup/absorption thresholds remain separate',
          'Strict producer saving retained; sharper joined moments and new descendant graph are not included'])
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for row in rows:print('PASS',row['mode'],row['prefix'],row['kappa'],flush=True)


if __name__=='__main__':main()
