#!/usr/bin/env python3
"""Fresh exact two-family batched primitive with reviewed semantic/bulk costs.

The witness algebra is copied unchanged from the frozen semantic/bulk
producer except for its explicit Taylor bit certificate and declared-
exponent parameter cap. No uniform log(s/W) saving is substituted.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from downstream_compact_control_assembly import COMPACT_KAPPA
from downstream_gaussian import BASELINE_KAPPA,ceil_q,require
from downstream_parameter_optimum import as_strings,compact_lower,rational_decimal_lower,saving_enclosure
from downstream_promoted_complex_composition import parse_counts
from downstream_semantic_bulk_assembly import compact_cutoff,compressed_power_certificate,witness as uniform_witness
from downstream_diagonal_batch_join_bound import joint


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_padding_certificate(row):
    """A stronger real-log field inequality, without huge power allocation.

    p=6b and ell>=b^(1-epsilon)/2. The fixed layout constant C in
    e<=C*p is separate: after p>=C, W^depth<p^100 at these cutoffs.
    """
    gap=1-Q(row['parameters']['epsilon']);k=ceil_q(1/gap)
    L0=row['cutoff_log2_b']['common']
    require(L0>=25 and L0>=2*k,'Row-padding monotonicity cutoff failed')
    checks=[]
    for j in range(6):
        L=L0*2**j
        checks.append(dict(log2_b=L,strict_power_certificate=
                           compressed_power_certificate(L//k,400*(L+8))))
    require(row['bit_counts']['W']<2**49,'Declared row divisor bit bound failed')
    return dict(status='PASS exact logarithmic row-field domination',
        checks=checks,real_log_lower=L0,reciprocal_exponent_ceiling=k,
        inequality='b^(1-epsilon)>400*(log2(b)+8)',
        implication='ell>=b^(1-epsilon)/2>100*log2(p), p=6b',
        monotonicity='2^(L/k)/(L+8) increases for real L>=2k using log(2)>1/2',
        row_divisor='W^ceil(log_h(e))<p^100 for e<=C*p, p>=C and log2(p)>=25',
        fixed_eventual_setup='p>=max(2,C) for the retained layout constant C; no e<=2p assertion')


def batch_witness(n,nc,mode,prefix,previous,primitive):
    eb=dict(certificate_kind='STRICT SECOND-ORDER BATCH CHARACTERISTIC, NOT UNIFORM SHRINK',
            chosen_saving=Q(primitive['saving']),strict_primitive_gap=Q(primitive['strict_taylor_gap']),
            taylor_linear_coefficient=Q(primitive['taylor_linear_coefficient']),
            taylor_quadratic_coefficient=Q(primitive['taylor_quadratic_coefficient']))
    ec=saving_enclosure(nc['eta'],nc['m'])
    a,b=eb['chosen_saving'],ec['chosen_saving']
    require(0<a<b/2 and b<Q(1,32),'Semantic bulk row requires a<b/2')
    h=Q(1,2**20) if mode=='conservative' else Q(1,2**64)
    q=a*(1-2*h);tau=1-a;sigma=1-b
    beta=Q(1,2);lp=1-q;lam=(tau+lp)/2
    if prefix=='original':
        c=q*(1+h);eps=(1-h)/(1+c+q)
    else:
        require(prefix=='balanced','Unknown semantic prefix')
        c=q+h/4;eps=(1-h)/(1+q)
    G=eps*q;r=(G+1-eps)/2;delta=h/8
    E=64*(nc['W']+nc['m']+1)**3;B=nc['s']+E
    C0=32*nc['m']*B*B;C1=Q(1)
    require(2<=nc['s'] and B>=8 and C0>2*B+18,'Semantic linear constant failed')
    internal=tau+(1-beta)*max(sigma-tau,Q(0))
    leaf=sigma+beta*(1-sigma);reserve=max(1-c,Q(0))
    prefix_margin=1-eps*(1+c) if prefix=='original' else 1-eps
    margins=dict(g1=prefix_margin,g2=a,g3=G,g4=a,
                 g5=min(1-eps-delta,r-delta),g6=1-eps-delta,g7=eps)
    require(min(margins.values())==G,'Semantic bulk minimum is not the layer margin')
    kappa=compact_lower(G,places=40)
    geometry=1-eps*(1+c)
    slacks=dict(bit_primitive=eb['strict_primitive_gap'],complex_primitive=ec['strict_primitive_gap'],
      primitive_order=b-a,half_leaf_saving=b/2-q,c_positive=c,c_below_one=1-c,
      beta_positive=beta,beta_below_one=1-beta,epsilon_positive=eps,epsilon_below_one=1-eps,
      lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,compact_internal=lam-internal,
      lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-reserve,
      linear_scalar_guard=1-eps*C1,K_smaller_than_ell=geometry,K_dominates_log_p=eps*c,
      record_suffix_superpolynomial=1-eps,phase_local_cost=1-eps-delta,
      phase_boundary_cost=r-delta,gamma_sublinear=1-eps-r,
      cell_larger_than_band=eps-(1-r)/2,prime_interval_packing=1-eps,alpha_power=r,
      delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,
      prefix_vs_layer=margins['g1']-G,movement_vs_layer=a-G,exposure_vs_layer=a-G,
      gaussian_vs_layer=margins['g5']-G,scalar_vs_layer=margins['g6']-G,
      dimension_vs_layer=eps-G,absorption=G-kappa,improvement_over_accepted= kappa-previous,
      old_nonadjacent_synthetic_margin_fails=kappa-eps*a*c,
      old_separate_resampling_exposure_fails=kappa-a*(1-eps),
      small_field_exposure_vs_layer=1-eps-G,
      microbox_artificial_boundary_vs_layer=8-eps+r-delta-G)
    for name,value in slacks.items():require(value>0,'Semantic bulk nonpositive strict slack '+name)
    if prefix=='balanced':
        require(1-eps-G==h and 1-eps-r==h/2,'Balanced semantic scale slack differs')
        slacks['old_prefix_estimate_fails']=kappa-geometry
        if mode=='tight':require(slacks['old_prefix_estimate_fails']>0,'Tight old-prefix negative missing')
        else:slacks.pop('old_prefix_estimate_fails')
    else:
        require(margins['g1']-G==h,'Original semantic prefix slack differs')
    # This is the parameter cap for the DECLARED certified exponent a,
    # not an upper bound on every possible improved primitive.
    saving_upper=a
    upper=saving_upper/(1+(1 if prefix=='balanced' else 2)*saving_upper)
    require(kappa<upper,'Semantic bulk scoped upper failed')
    ka=ceil_q(1/r);km=ceil_q(1/(eps*c));kb=ceil_q(1/(1-eps))
    cutoffs=dict(gamma=ceil_q(Q(7)/(1-eps-r)),logarithmic_alpha=16*ka*ka+1,
       full_guard=ceil_q(Q((2*int(C0)).bit_length())/(1-eps)),
       phase_cell=ceil_q(Q(9)/(eps-(1-r)/2)),compact_controls=64*km*km+1,
       K_geometry=ceil_q(Q(3)/geometry),microbox_period=128*kb*kb+1,routing_reservoirs=14)
    require(cutoffs['gamma']*(1-eps-r)>=7 and Q(1,ka)<=r and
       cutoffs['full_guard']*(1-eps)>=(2*int(C0)).bit_length() and
       cutoffs['phase_cell']*(eps-(1-r)/2)>=9 and cutoffs['K_geometry']*geometry>=3,
       'Semantic bulk parameter cutoff failed')
    period=cutoffs['microbox_period']
    require(period>=2*kb,'Polynomial period monotonicity cutoff failed')
    period_certificate=compressed_power_certificate(period//kb,16*period+56)
    # At real L_input>=period: ell>=b^(1-eps)/2; log2 s>=ell-1.
    # Tile side L_tile<2p^8 and p=6b imply log2(4L_tile)<=8L_input+27.
    # The exact comparison makes s>2(L_tile+2A+2w); monotonicity uses
    # log(2)>1/2 and L_input>=2kb. All remaining halo inequalities hold p>100.
    row=dict(status='PASS STRICT CONDITIONAL BATCHED ASSEMBLY; INDEPENDENT ASSEMBLY REVIEW REQUIRED',
      mode=mode,prefix=prefix,bit_counts=n,complex_counts=nc,
      bit_saving_certificate=eb,complex_saving_enclosure=ec,
      parameters=dict(a_bit=a,a_complex=b,tau=tau,sigma=sigma,beta=beta,c=c,lambda_=lam,
        lambda_prime=lp,epsilon=eps,alpha_squared_power=r,delta=delta,C0=C0,C1=C1,kappa=kappa),
      recurrence=dict(internal=internal,leaf=leaf,reservations=reserve),margins=margins,
      constraint_slacks=slacks,minimum_margin=G,linear_guard_constant_slack=C0-(2*B+18),
      semantic_guard=dict(E=E,B=B,C0=C0,C1=C1,internal='A(e)<=A(e/m)+s*e/m+E',
        complete='A_layer<=(2B+18)d<C0d'),
      microbox=dict(side='2^ceil(8log2p)',halo='4096p^3',Neumann_terms='512p^2',
        source_padding='Q*L=t_i and T/S<2',target_halo_volume='T(1+2A/L)^d<2T',
        local_inverse='same global rounded H principal; original seams retained as boundaries',
        cost='O(T*p^(1+delta)*(d+w^2+d*w^2/L))',
        exposure_cost='one global O(Tp*p^tau*polylogp) router plus O(Tp*d*polylogp) small fields'),
      declared_exponent_parameter_upper=upper,achieved_fraction_of_parameter_upper=kappa/upper,
      previous_accepted_kappa=previous,strict_gain=kappa-previous,
      improvement_ratio=kappa/previous,improvement_ratio_decimal_lower=rational_decimal_lower(kappa/previous,15),
      compact_upstream_ratio=kappa/COMPACT_KAPPA,
      compact_ratio_decimal_lower=rational_decimal_lower(kappa/COMPACT_KAPPA,15),
      original_baseline_ratio=kappa/BASELINE_KAPPA,
      cutoff_log2_b={**cutoffs,'common':max(cutoffs.values())},
      microbox_period_power_certificate=period_certificate,
      proof_obligations=['Complete independently reviewed arbitrary-source masked router and record-paid spectators',
        'Same-global-H principal locality including sufficient complement and retained period cuts',
        'Ordered fractional halo split/pad/crop and small-field inverse transposes on fixed tapes',
        'Sequential factor-bank pages reused across spectator prefixes and complete inner microboxes',
        'Linear semantic forward/inverse completed child guard with no intermediate truncation',
        'Accepted finite primitives, compact recurrence, phase inverse and complete multiplication interfaces'],
      additional_eventual_cutoffs=['BHP prime existence and interval packing',
        'Retained initial padded sizes and at least three spectator fields',
        'Polynomial catalogue/setup dominated by complete microbox and spectator records',
        'Strict recurrence/polylogarithm absorption and complete conditional theorem thresholds'])
    row['strengthened_real_log_compact_cutoff']=compact_cutoff(row)
    return row


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--uniform-semantic-bulk',type=Path,required=True)
    ap.add_argument('--primitive-certificate',type=Path,required=True)
    ap.add_argument('--primitive-review',type=Path,required=True)
    ap.add_argument('--kernel-review',type=Path,required=True)
    ap.add_argument('--root-kernel-controls',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic();source_dir=Path(__file__).parent
    old=json.loads(args.uniform_semantic_bulk.read_text())
    primitive=json.loads(args.primitive_certificate.read_text())
    review=json.loads(args.primitive_review.read_text());kernel=json.loads(args.kernel_review.read_text())
    root_kernel=json.loads(args.root_kernel_controls.read_text())
    for name,expected in old['source_sha256'].items():
        require(sha(source_dir/name)==expected,'Frozen source changed '+name)
    for name,expected in primitive['source_sha256'].items():
        require(sha(source_dir/name)==expected,'Taylor source changed '+name)
    p=primitive['witness'];n=parse_counts(p['counts'])
    require(as_strings(joint(n['h'],n['side_roles']))==p,'Taylor certificate exact regeneration failed')
    require(Q(p['saving'])==Q(1058685652786963,2*10**23),'Unexpected declared two-family saving')
    require(n['h']==51 and n['side_roles']==502265,'Unexpected finite primitive')
    require(review['status'].startswith('PASS') and kernel['status'].startswith('PASS') and
            root_kernel['status'].startswith('PASS'),'Independent batching controls not terminal')
    finite=old['odd_bit_finite_audit']
    require(finite['status']=='INDEPENDENT FINITE PROMOTION PASS' and
            review['finite_candidate_id']==finite['candidate_id'] and
            review['finite_compiled_sha256']==finite['compiled_sha256'],
            'Independent primitive finite identity differs')
    require(kernel['batch_review_sha256']==sha(args.primitive_review),
            'Kernel review is not tied to primitive review')
    require(kernel['strengthened_maximum_run']==n['h']**2-1 and
            kernel['unchanged_moment_run_bound']==4*n['h']+1,
            'Joined kernel-hole contract differs')
    require(review['generic_controls']['two_d_union_bound_verified'] and
            review['generic_controls']['lower_concentration_profile_invariant'] and
            review['segmented_operator_controls']['disjoint_runs_preserve_other_words'] and
            review['arbitrary_width_tail_controls']['exact_arbitrary_width_swap'],
            'Independent primitive algebra/tape controls absent')
    regressions=[]
    for row in old['witnesses']:
        require(parse_counts(row['bit_counts'])==n,'Uniform h51 finite counts differ')
        actual=uniform_witness(n,parse_counts(row['complex_counts']),row['mode'],row['prefix'],
                               Q(row['previous_accepted_kappa']))
        for group in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group])==row[group],'Uniform predecessor regression differs '+group)
        regressions.append(dict(mode=row['mode'],prefix=row['prefix'],kappa=row['parameters']['kappa'],unchanged=True))
    previous=max(Q(row['parameters']['kappa']) for row in old['witnesses'])
    nc=parse_counts(old['witnesses'][0]['complex_counts'])
    require(nc['h']==28 and nc['R']==97586,'Original accepted complex input differs')
    rows=[batch_witness(n,nc,mode,prefix,previous,p) for mode in ('conservative','tight')
          for prefix in ('original','balanced')]
    for row in rows:
        row['native_bit_primitive']=dict(certificate_kind='BATCHED CHARACTERISTIC',
            exponent='tau=1-a',chosen_saving=Q(p['saving']),
            characteristic='W*m^(1-a)>sum(n_r*r^(1-a))',
            strict_taylor_gap=Q(p['strict_taylor_gap']),
            bit_guard_scope='Exact original rational address shear table; complex numerical guard unchanged',
            maximum_run=n['h']**2-1,child_shrink='r*floor(e/m)<e/h',
            row_depth='ceil(log_h e)<=3ceil(log_(h^3) e)',
            native_alphabet='Original fixed odd prime and original canonical factors retained')
        row['compact_row_padding']=row_padding_certificate(row)
        row['additional_eventual_cutoffs'] += ['Fixed batched primitive base case and original odd-prime rational table',
            'Fixed layout constant C: maximum batched invocation e<=C*p, after p>=C',
            'Finite descriptor/setup constants absorbed under the retained strict inequalities']
        row['proof_obligations'].insert(0,'Independently reviewed joined/middle pivot profile, kernel holes, component carry reset, arbitrary-width tails and h-fold recursive transfer')
    inputs=[args.uniform_semantic_bulk,args.primitive_certificate,args.primitive_review,args.kernel_review,args.root_kernel_controls]
    hashes=dict(old['source_sha256']);hashes.update(primitive['source_sha256'])
    hashes[Path(__file__).name]=sha(Path(__file__))
    result=dict(status='PASS STRICT CONDITIONAL BATCHED ASSEMBLY; INDEPENDENT ASSEMBLY REVIEW REQUIRED',
        campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
        campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
        generated_at=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
        original_reference=old['original_reference'],compact_reference=old['compact_reference'],
        input_files={str(path):dict(bytes=path.stat().st_size,sha256=sha(path)) for path in inputs},
        odd_bit_finite_audit=finite,promoted_complex_audit=old['promoted_complex_audit'],
        bit_primitive_certificate=primitive,independent_primitive_interface=dict(
            algebra_review_sha256=sha(args.primitive_review),kernel_review_sha256=sha(args.kernel_review),
            root_kernel_control_sha256=sha(args.root_kernel_controls),
            certified_saving_from_Taylor=Q(p['saving']),independent_coarse_saving=Q(kernel['promoted_uncapped_primitive_saving']),
            independent_final_assembly_pending=True),
        uniform_h51_regressions=regressions,previous_accepted_kappa=previous,witnesses=rows,
        copied_witness_algebra=dict(source='downstream_semantic_bulk_assembly.py',
            sha256=sha(source_dir/'downstream_semantic_bulk_assembly.py'),
            changes='Explicit Taylor primitive in place of uniform log enclosure; parameter cap uses declared certified a'),
        elapsed_seconds=time.monotonic()-started,
        scope='Complete retained multiplication estimates composed with a new two-family native bit primitive; conditional on full independently written batching transfer and its additional eventual row/setup thresholds; no graph replay or uniform-log substitution')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:
        print(result['status'],row['mode'],row['prefix'],row['parameters']['kappa'],
              row['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
