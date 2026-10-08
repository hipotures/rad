#!/usr/bin/env python3
"""Independent complete generic-basis assembly at a general stopping threshold.

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


def audit_primitive(p, root):
    n=finite_counts(p['counts']);h,roles=p['h'],p['roles'];v,m=n['v'],n['m']
    require((h,roles)==(51,485680),'Unexpected promoted generic graph')
    deficits=dict(middle=h*h,joined=2*h,data=h*h+h-1)
    multiplicities=dict(middle=(roles+h)*v*v,joined=(roles+h)*v*v,data=2*n['N'])
    runs={k:m-2*d for k,d in deficits.items()}
    ranks={k:multiplicities[k]*(m-d) for k,d in deficits.items()}
    require(p['kernel_dimensions']==deficits and p['family_multiplicities']==multiplicities and
        p['grouped_runs']==runs and p['family_ranks']==ranks and sum(ranks.values())<n['s'],
        'Independent disjoint generic boundary counts differ')
    moments={k:multiplicities[k]*r*bounds(r)[0] for k,r in runs.items()}
    hist=Counter()
    for k,r in runs.items():hist[r]+=multiplicities[k]
    long_rank=sum(r*c for r,c in hist.items())
    require({str(k):v for k,v in sorted(hist.items())}==p['long_run_histogram'] and
        p['long_grouped_rank']==long_rank and p['individual_pivot_count']==n['s']-long_rank>0,
        'Generic characteristic used stale or overlapping pivot mass')
    lm=bounds(m)[1];linear=n['W']*m*lm-sum(moments.values());quadratic=Q(n['s'],2)*lm*lm
    saved_linear,saved_quadratic=(Q(p[k]) for k in ('taylor_linear_coefficient','taylor_quadratic_coefficient'))
    a=Q(p['saving']);require(a==Q(143492085004836477,10**24),'Unknown strict generic saving')
    require(saved_linear>=linear>0 and saved_quadratic>=quadratic>0,
        'Independent moments do not support producer Taylor coefficients')
    gap=n['D']-a*saved_linear-a*a*saved_quadratic
    require(gap==Q(p['strict_taylor_gap'])>0 and
        n['D']-a*linear-a*a*quadratic>=gap,'Strict generic negative-exponential characteristic failed')
    r=root['independent_characteristic']
    require(r['kernels']==deficits and r['run_lengths']==runs and r['family_ranks']==ranks and
        r['roles']==roles and Q(r['chosen_saving'])>=a and Q(r['strict_characteristic_gap'])>0 and
        r['row_degree']==66000 and r['reservoir_slope']==264000,
        'Independent constructive all-size theorem and positive-exponential audit differ')
    require(p['maximum_child_rank']==m-4*h and Q(p['child_ratio'])==Q(m-4*h,m) and
        m**651>2*(m-4*h)**651 and n['W']<2**49 and
        Q(49*651)*(2+Q(1,25))<66000,
        'New maximum child/deeper row proof failed')
    return dict(chosen_saving=str(a),strict_taylor_gap=str(gap),
        independently_rebuilt_runs=runs,family_ranks=ranks,individual_pivots=n['s']-long_rank,
        maximum_child=m-4*h,row_degree=66000,logarithm_terms=64,outward_dyadic_bits=320,
        full_h51_basis_table_prime_materialized=False,constructive_theorem_separately_reviewed=True)


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
    require(eb['certificate_kind'] == 'GENERIC METRIC FLAGS, DIRECT NEGATIVE-EXPONENTIAL TAYLOR',
            'New primitive must not use a uniform rank-saving enclosure')
    require(Q(eb['chosen_saving']) == a and
            Q(eb['strict_primitive_gap']) == Q(primitive['strict_taylor_gap']) and
            Q(eb['taylor_linear_coefficient']) == Q(primitive['taylor_linear_coefficient']) and
            Q(eb['taylor_quadratic_coefficient']) == Q(primitive['taylor_quadratic_coefficient']),
            'Row primitive certificate differs from the reviewed Taylor input')
    primitive_gaps['bit_primitive'] = Q(primitive['strict_taylor_gap'])
    require(primitive_gaps['bit_primitive'] > 0, 'Explicit Taylor gap is not strict')
    require(tau==1-a and sigma==1-b and 0<b<a<Q(1,32),'New fast-bit exponent branch invalid')
    h=Q(1,2**(20 if row['mode']=='conservative' else 64))
    require(row['mode'] in ('conservative','tight'),'Unknown fixed parameter mode')
    require(beta==h,'Chosen general stopping threshold differs')
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    internal_saving,leaf_saving=1-internal,1-leaf
    q=1-lp
    require(q==min(internal_saving,leaf_saving)*(1-2*h) and
        lam==(max(tau,sigma,internal)+lp)/2,
        'All three original intermediate exponent bounds were not retained')
    require(row['exponent_order']=='tau<sigma: growing stopped sum' and
        all(Q(row['recurrence_savings'][k])==v for k,v in
            dict(internal=internal_saving,leaf=leaf_saving,reservations=c,q=q).items()),
        'General stopped savings differ')
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
    semantic=row['semantic_guard'];Gscalar=semantic['scalar_gates']
    literal_depth=2*Gscalar*nc['W']**2+4*nc['s']+4*nc['W']+4
    require(Gscalar>0 and E>literal_depth and C0>2*B+18,
        'Exact actual scalar charge or complete linear guard constant invalid')
    require(semantic['literal_depth']==literal_depth and
        semantic['literal_guard_slack']==E-literal_depth and semantic['old_six_W_shortcut_not_used'] and
        semantic['stopping_beta_independent'] and
        semantic['internal']=='A(e)<=A(e/m)+s*e/m+E' and
        semantic['complete']=='A_layer<=(2B+18)d<C0d' and
        semantic['representation']=='Same fine-grid integers; no child truncation',
        'Semantic general-beta/completed-child interface differs')
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
    slacks=dict(**primitive_gaps,complex_literal_gate_guard=E-literal_depth,
        q_below_internal_saving=internal_saving-q,q_below_leaf_saving=leaf_saving-q,
        q_below_reservation_c=c-q,
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
    slacks['wrong_fixed_half_leaf_failure']=q-b/2
    slacks['wrong_tau_midpoint_below_sigma']=sigma-(tau+lp)/2
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
    kstop=ceil_q(1/(eps*beta));minimum=max(n['m'],nc['m'])
    cuts['stopped_leaf']=kstop*(4*minimum).bit_length()
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
    upper = min(a,b)/(1+factor*min(a,b))
    beta_cap=min(internal_saving,leaf_saving)
    fixed_beta_upper=beta_cap/(1+factor*beta_cap)
    require(Q(row['fixed_beta_parameter_upper'])==fixed_beta_upper and
        kappa<fixed_beta_upper<=upper,'General stopping fixed-beta cap differs')
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
        row_checks.append(power_certificate(record['strict_power_certificate'], L//kb, 264000*(L+8)))
    require(padding['fixed_eventual_setup']=='New basis/table/alphabet/layout constant C; p>=max(C,2^25), no e<=2p assertion' and
        padding['maximum_child']==51**3-4*51 and padding['depth_per_ceil_log2e']==651 and
        Q(padding['row_degree_rational_slack'])==66000-Q(49*651)*(2+Q(1,25))>0 and
        padding['inequality']=='b^(1-epsilon)>264000*(log2(b)+8)' and
        padding['row_divisor']=='W^depth<p^66000 after e<=C*p,p>=C,log2(p)>=25' and
        padding['old_p2600_not_asserted'],
        'New 66000-degree native row reservoir differs')
    stopping=row['stopped_leaf_certificate']
    require(stopping['status'].startswith('PASS') and stopping['minimum']==minimum and
        stopping['reciprocal_exponent_ceiling']==kstop and len(stopping['checks'])==6 and
        stopping['sufficient']=='b^(epsilon*beta)>4max(m_bit,m_complex)' and
        stopping['implication']=='d=floor(b^epsilon)>=b^epsilon/2 and beta<1 imply d^beta>2max(m_bit,m_complex)' and
        stopping['integer_stopping_test']=='e^v<d^u for fixed beta=u/v; fixed rational exponents need no real-power comparison',
        'Exact fixed-rational stopping comparison or floor qualification differs')
    stop_checks=[]
    for j,record in enumerate(stopping['checks']):
        L=cuts['common']*2**j
        require(record['log2_b']==L,'Stopped leaf checkpoint differs')
        stop_checks.append(power_certificate(record['strict_power_certificate'],L//kstop,4*minimum))
    require(cuts['stopped_leaf']*eps*beta>=(4*minimum).bit_length(),
        'Stopping exponent cutoff failed')
    native=row['native_bit_primitive']
    require(native['certificate_kind']==primitive['certificate_kind'] and
        Q(native['chosen_saving'])==a and Q(native['strict_taylor_gap'])==Q(primitive['strict_taylor_gap']) and
        native['maximum_child']==51**3-4*51 and native['depth_per_ceil_log2e']==651 and
        native['row_degree']==66000 and native['reservoir_coefficient']==264000 and
        not native['runtime_basis_adapter'] and not native['full_h51_basis_table_prime_instantiated'] and
        native['factor_table']=='New fixed table for every actual conjugated source/gate/sink frame' and
        native['native_prime']=='One newly fixed admissible odd prime for the complete finite table; separate eventual setup',
        'Constructive native table/prime/depth/contract scope differs')
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
        row_padding_compressed_checks=row_checks,stopped_leaf_compressed_checks=stop_checks,
        scalar_gate_count=Gscalar,literal_scalar_depth=literal_depth,
        ratio_to_83_over_10_to_12=str(kappa/Q(83,10**12)),
        old_unproved_estimates_reject_this_witness=True,
        enormous_power_allocation_performed=False)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('certificate','previous','previous-review','primitive','generic-inputs','complex-review','output'):
        ap.add_argument('--'+name,type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh result path');start=time.monotonic()
    files=[args.certificate,args.previous,args.previous_review,args.primitive,args.generic_inputs,args.complex_review]
    hashes={str(p):digest(p) for p in files}
    data=json.loads(args.certificate.read_text());old=json.loads(args.previous.read_text())
    previous_review=json.loads(args.previous_review.read_text());primitive=json.loads(args.primitive.read_text())
    root=json.loads(args.generic_inputs.read_text());complex_review=json.loads(args.complex_review.read_text())
    require(previous_review['status'].startswith('PASS') and
        previous_review['input_sha256'][str(args.previous)]==digest(args.previous) and
        data['previous_complete_review_sha256']==digest(args.previous_review),
        'Accepted preceding complete changed-frame assembly missing')
    require(root['status']=='PASS root independent generic-basis inputs and written theorem review' and
        root['written_all_size_proof_reviewed'] and not root['runtime_basis_adapter'] and
        not root['all_h51_ambient_basis_instantiated'] and
        data['root_generic_inputs_sha256']==digest(args.generic_inputs) and
        data['generic_characteristic_certificate']==primitive,
        'Constructive all-size generic theorem lacks independent root review')
    identity=data['odd_bit_finite_audit']
    require(identity==old['odd_bit_finite_audit']==previous_review['unchanged_finite_identity'] and
        identity['roles']==485680 and root['finite_candidate_id']==identity['candidate_id'] and
        root['finite_compiled_sha256']==identity['compiled_sha256'],
        'New generic frame construction changed accepted scalar graph identity')
    require(data['original_complex_audit']==old['promoted_complex_audit']==previous_review['unchanged_complex_audit'],
        'Original separate complex input differs')
    require(complex_review['status']=='Terminal independent complex controller finite/transfer PASS',
        'Stronger separate complex input has no independent finite/all-size promotion')
    for name,expected in complex_review['independent_source_sha256'].items():
        require(digest(Path(__file__).with_name(name))==expected,'Independent complex source changed '+name)
    small=next(r for r in complex_review['rows'] if r['h']==8)
    require(small['complete_dirty_basis']['complete_basis_dimension']==951 and
        small['complete_dirty_basis']['forward_identity_shear_and_inverse_exact'] and
        small['complete_shared_exchange']['all_dirty_banks_restored_exactly'] and
        small['complete_shared_exchange']['all_data_outputs_exact'],
        'Stronger complex arbitrary dirty full boundary control missing')
    controller=next(r for r in complex_review['rows'] if r['h']==28)
    counts=complex_counts(controller['counts']);guard=controller['guard'];macro=guard['actual_grouped_scalar_gates']
    c=controller['logical']['logical_frames']-counts['v']
    require(c+2*counts['v']==97586 and
        macro==3*counts['v']**2*(4*(c+counts['v'])+4*counts['v']+4) and
        not guard['old_six_W_condition'] and guard['exact_grouped_gate_bound_used'],
        'Literal complex macro-gates replaced by false physical-role shortcut')
    audit=data['controller_complex_audit']
    require(audit['roles']==92309 and audit['compiled_sha256']==controller['physical']['compiled_sha256'] and
        audit['actual_grouped_scalar_gates']==macro and
        audit['exact_literal_depth']==guard['exact_saved_input_operation_depth_bound'] and
        audit['exact_guard_slack']==guard['operation_depth_slack'],
        'Promoted stronger complex count/guard identity differs')
    for name,expected in data['source_sha256'].items():
        require(digest(Path(__file__).with_name(name))==expected,'Frozen producer source changed '+name)
    require(digest(Path(__file__).with_name('review_generic_composition_inputs.py'))==root['source_sha256'],
        'Independent constructive theorem source changed')
    for path in files[1:]:
        require(any(record['sha256']==hashes[str(path)] for record in data['input_files'].values()),
            'Assembler pinned input hash absent '+path.name)
    old_best=max(old['witnesses'],key=lambda row:Q(row['parameters']['kappa']))
    require(Q(data['previous_accepted_kappa'])==Q(old_best['parameters']['kappa']),
        'Prior accepted comparison differs')
    p=primitive['witness'];native=audit_primitive(p,root);rows=[]
    for row in data['witnesses']:
        require(row['bit_counts']==p['counts'] and row['semantic_guard']['scalar_gates']==macro,
            'General-beta bit input or actual scalar gate count differs')
        label=row['complex_input'];require(label in ('controller92309','original97586'),'Unknown complex comparison input')
        expected=controller['counts'] if label=='controller92309' else old_best['complex_counts']
        require(row['complex_counts']==expected,'Selected accepted complex count differs')
        checked=audit_row(row,old_best,p);checked['complex_input']=label;rows.append(checked)
    require({(r['complex_input'],r['mode'],r['prefix']) for r in rows}==
        set(product(('controller92309','original97586'),('conservative','tight'),('original','balanced'))),
        'Eight complete independent general stopping rows missing')
    result=dict(status='PASS independent complete generic-basis general-beta conditional assembly',
        campaign='20261007T222521Z',generated_utc=datetime.now(timezone.utc).isoformat(),input_sha256=hashes,
        reviewer_source_sha256={name:digest(Path(__file__).with_name(name)) for name in
            ('review_general_beta_assembly.py','review_generic_composition_inputs.py','review_householder_assembly.py',
            'review_asymmetric_motif.py','review_parameter_audit.py','review_packed_unrolling.py','review_semantic_bulk_assembly.py')},
        exact_primitive_audit=native,rows=rows,unchanged_finite_identity=identity,
        original_complex_audit=data['original_complex_audit'],controller_complex_audit=audit,
        fixed_general_stopping_and_deeper_row_interfaces_reviewed=True,
        wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limitations=['Conditional written all-size interfaces, constructive fixed giant basis; not formal/unconditional theorem or novelty',
            'The full h51 T/table/eligible odd prime is finite deterministic setup and not instantiated',
            'Numeric cutoffs do not replace separate native layout/table/prime/record/absorption/machine thresholds',
            'New delayed complex frontiers and whole-rank complex calls are not included'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for row in rows:print('PASS',row['complex_input'],row['mode'],row['prefix'],row['kappa'],flush=True)


if __name__=='__main__':main()
