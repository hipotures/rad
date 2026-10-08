#!/usr/bin/env python3
"""Complete general-beta compact assembly for the generic native metric basis.

The stopping exponent and lambda follow the actual retained inequalities.
No beta=1/2 primitive-order premise or old p^2600 stock is imported.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

from downstream_batched_semantic_bulk_assembly import batch_witness
from downstream_compact_control_assembly import COMPACT_KAPPA
from downstream_gaussian import BASELINE_KAPPA,ceil_q,require
from downstream_generic_metric_characteristic import generic
from downstream_parameter_optimum import as_strings,compact_lower,rational_decimal_lower,saving_enclosure
from downstream_promoted_complex_composition import parse_counts
from downstream_semantic_bulk_assembly import compact_cutoff,compressed_power_certificate


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def complex_counts(h,roles):
    require(h==28 and roles in (97586,92309),'Only independently accepted complex inputs are allowed')
    v=comb(h,3);m=h**3;N=v**3
    W=2*N+2*v*v*(roles+h+1);L=3*v*v*h*(h+1);D=2*N-2*L;s=W*m-D
    require(D>0,'Complex deficit is nonpositive')
    return dict(h=h,v=v,m=m,N=N,R=roles,W=W,L=L,D=D,s=s,eta=Q(D,W*m))


def general_row_padding(row,primitive):
    gap=1-Q(row['parameters']['epsilon']);k=ceil_q(1/gap)
    L0=row['cutoff_log2_b']['common'];n=row['bit_counts']
    require(L0>=25 and L0>=2*k and n['W']<2**49,
            'Generic real-log row stock premises failed')
    m=n['m'];maximum=primitive['maximum_child_rank']
    require(maximum==m-4*n['h'] and m**651>2*maximum**651,
            'Generic native halving depth failed')
    depth_slack=66000-Q(49*651)*(2+Q(1,25))
    require(depth_slack>0,'Generic row degree arithmetic failed')
    checks=[]
    for j in range(6):
        L=L0*2**j
        checks.append(dict(log2_b=L,strict_power_certificate=
                           compressed_power_certificate(L//k,264000*(L+8))))
    return dict(status='PASS exact generic p^66000 row reservoir',
                checks=checks,real_log_lower=L0,reciprocal_exponent_ceiling=k,
                maximum_child=maximum,depth_per_ceil_log2e=651,
                inequality='b^(1-epsilon)>264000*(log2(b)+8)',
                implication='ell>=b^(1-epsilon)/2>66000*log2(p), p=6b',
                row_divisor='W^depth<p^66000 after e<=C*p,p>=C,log2(p)>=25',
                row_degree_rational_slack=depth_slack,
                monotonicity='2^(L/k)/(L+8) increases for real L>=2k using ln2>1/2',
                old_p2600_not_asserted=True,
                fixed_eventual_setup='New basis/table/alphabet/layout constant C; p>=max(C,2^25), no e<=2p assertion')


def general_witness(n,nc,mode,prefix,previous,primitive,scalar_gates,beta_override=None,native_stock=True):
    a=Q(primitive['saving']);ec=saving_enclosure(nc['eta'],nc['m']);b=ec['chosen_saving']
    require(0<a<Q(1,32) and 0<b<Q(1,32) and Q(primitive['strict_taylor_gap'])>0,
            'Declared generic bit or complex strict primitive failed')
    require(mode in ('conservative','tight'),'Unknown fixed-slack mode')
    h=Q(1,2**20) if mode=='conservative' else Q(1,2**64)
    # Any positive fixed beta is permitted by the exact semantic guard.
    # A fast bit primitive needs beta small because the complex leaf is
    # now the limiting cost. Keep the stopping test rational and exact.
    beta=(Q(beta_override) if beta_override is not None else
          ((1-a/b)/2 if a<b else h))
    require(0<beta<1,'General stopping beta domain failed')
    tau,sigma=1-a,1-b
    internal=tau+(1-beta)*max(sigma-tau,Q(0))
    leaf=sigma+beta*(1-sigma)
    internal_saving,leaf_saving=1-internal,1-leaf
    q=min(internal_saving,leaf_saving)*(1-2*h);lp=1-q
    # Pinned compact-control-layout.tex112 retains ALL three lower bounds.
    lam=(max(tau,sigma,internal)+lp)/2
    if prefix=='original':
        c=q*(1+h);eps=(1-h)/(1+c+q)
    else:
        require(prefix=='balanced','Unknown prefix model')
        c=q+h/4;eps=(1-h)/(1+q)
    layer=eps*q;r=(layer+1-eps)/2;delta=h/8
    E=64*(nc['W']+nc['m']+1)**3;B=nc['s']+E;C0=32*nc['m']*B*B;C1=Q(1)
    literal_depth=2*scalar_gates*nc['W']*nc['W']+4*nc['s']+4*nc['W']+4
    require(scalar_gates>0 and E>literal_depth and B>=8 and C0>2*B+18,
            'Actual complex grouped-gate or semantic guard failed')
    reserve=max(1-c,Q(0))
    margins=dict(g1=1-eps*(1+c) if prefix=='original' else 1-eps,
                 g2=a,g3=layer,g4=a,g5=min(1-eps-delta,r-delta),
                 g6=1-eps-delta,g7=eps)
    require(min(margins.values())==layer,'General-beta layer is not the exact bottleneck')
    kappa=compact_lower(layer,places=40);geometry=1-eps*(1+c)
    slacks=dict(bit_primitive=Q(primitive['strict_taylor_gap']),
                complex_primitive=ec['strict_primitive_gap'],
                complex_literal_gate_guard=E-literal_depth,
                beta_positive=beta,beta_below_one=1-beta,
                q_below_internal_saving=internal_saving-q,q_below_leaf_saving=leaf_saving-q,
                q_below_reservation_c=c-q,c_positive=c,c_below_one=1-c,
                epsilon_positive=eps,epsilon_below_one=1-eps,
                lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
                compact_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
                compact_leaf=lp-leaf,compact_reservations=lp-reserve,
                linear_scalar_guard=1-eps*C1,K_smaller_than_ell=geometry,
                K_dominates_log_p=eps*c,record_suffix_superpolynomial=1-eps,
                phase_local_cost=1-eps-delta,phase_boundary_cost=r-delta,
                gamma_sublinear=1-eps-r,cell_larger_than_band=eps-(1-r)/2,
                prime_interval_packing=1-eps,alpha_power=r,
                delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,
                prefix_vs_layer=margins['g1']-layer,movement_vs_layer=a-layer,
                exposure_vs_layer=a-layer,gaussian_vs_layer=margins['g5']-layer,
                scalar_vs_layer=margins['g6']-layer,dimension_vs_layer=eps-layer,
                absorption=layer-kappa,improvement_over_accepted=kappa-previous,
                old_nonadjacent_synthetic_margin_fails=kappa-eps*a*c,
                old_separate_resampling_exposure_fails=kappa-a*(1-eps),
                small_field_exposure_vs_layer=1-eps-layer,
                microbox_artificial_boundary_vs_layer=8-eps+r-delta-layer)
    if a>b and beta_override is None:
        slacks['wrong_fixed_half_leaf_failure']=q-b/2
        slacks['wrong_tau_midpoint_below_sigma']=sigma-(tau+lp)/2
    for key,value in slacks.items():require(value>0,'General-beta nonpositive slack '+key)
    if prefix=='balanced':
        require(1-eps-layer==h and 1-eps-r==h/2,'Balanced general scale slack differs')
        if mode=='tight':
            slacks['old_prefix_estimate_fails']=kappa-geometry
            require(slacks['old_prefix_estimate_fails']>0,'Tight old-prefix negative missing')
    else:require(margins['g1']-layer==h,'Original general prefix slack differs')
    theta=min(a,b);factor=1 if prefix=='balanced' else 2
    upper=theta/(1+factor*theta)
    beta_cap=min(internal_saving,leaf_saving)
    fixed_beta_upper=beta_cap/(1+factor*beta_cap)
    require(kappa<fixed_beta_upper<=upper,'General-beta declared family cap failed')
    ka=ceil_q(1/r);km=ceil_q(1/(eps*c));kb=ceil_q(1/(1-eps))
    kstop=ceil_q(1/(eps*beta));minimum=max(n['m'],nc['m'])
    # d=floor(b^epsilon)>=b^epsilon/2. Since beta<1, it suffices
    # that b^(epsilon*beta)>4m to obtain d^beta>2m.
    stop=kstop*(4*minimum).bit_length()
    cutoffs=dict(gamma=ceil_q(Q(7)/(1-eps-r)),logarithmic_alpha=16*ka*ka+1,
                 full_guard=ceil_q(Q((2*int(C0)).bit_length())/(1-eps)),
                 phase_cell=ceil_q(Q(9)/(eps-(1-r)/2)),compact_controls=64*km*km+1,
                 K_geometry=ceil_q(Q(3)/geometry),microbox_period=128*kb*kb+1,
                 routing_reservoirs=14,stopped_leaf=stop)
    require(cutoffs['gamma']*(1-eps-r)>=7 and Q(1,ka)<=r and
            cutoffs['full_guard']*(1-eps)>=(2*int(C0)).bit_length() and
            cutoffs['phase_cell']*(eps-(1-r)/2)>=9 and
            cutoffs['K_geometry']*geometry>=3 and eps*max(cutoffs.values())>=1,
            'General-beta explicit parameter cutoff failed')
    period=cutoffs['microbox_period'];require(period>=2*kb,'Polynomial period monotonicity failed')
    period_certificate=compressed_power_certificate(period//kb,16*period+56)
    common=max(cutoffs.values());stop_checks=[]
    for j in range(6):
        L=common*2**j
        stop_checks.append(dict(log2_b=L,strict_power_certificate=
                               compressed_power_certificate(L//kstop,4*minimum)))
    row=dict(status='PASS STRICT CONDITIONAL GENERAL-BETA ASSEMBLY; INDEPENDENT FULL REVIEW REQUIRED',
             mode=mode,prefix=prefix,bit_counts=n,complex_counts=nc,
             bit_saving_certificate=dict(certificate_kind=primitive['certificate_kind'],
                 chosen_saving=a,strict_primitive_gap=Q(primitive['strict_taylor_gap']),
                 taylor_linear_coefficient=Q(primitive['taylor_linear_coefficient']),
                 taylor_quadratic_coefficient=Q(primitive['taylor_quadratic_coefficient'])),
             complex_saving_enclosure=ec,
             parameters=dict(a_bit=a,a_complex=b,tau=tau,sigma=sigma,beta=beta,c=c,
                 lambda_=lam,lambda_prime=lp,epsilon=eps,alpha_squared_power=r,delta=delta,
                 C0=C0,C1=C1,kappa=kappa),
             recurrence=dict(internal=internal,leaf=leaf,reservations=reserve),
             recurrence_savings=dict(internal=internal_saving,leaf=leaf_saving,reservations=c,q=q),
             exponent_order='tau<sigma: growing stopped sum' if a>b else 'sigma<=tau: root dominated',
             margins=margins,constraint_slacks=slacks,minimum_margin=layer,
             declared_exponent_parameter_upper=upper,fixed_beta_parameter_upper=fixed_beta_upper,
             achieved_fraction_of_parameter_upper=kappa/upper,
             semantic_guard=dict(E=E,B=B,C0=C0,C1=C1,
                 scalar_gates=scalar_gates,literal_depth=literal_depth,
                 literal_guard_slack=E-literal_depth,old_six_W_shortcut_not_used=True,
                 internal='A(e)<=A(e/m)+s*e/m+E',complete='A_layer<=(2B+18)d<C0d',
                 stopping_beta_independent=True,representation='Same fine-grid integers; no child truncation'),
             linear_guard_constant_slack=C0-(2*B+18),
             cutoff_log2_b={**cutoffs,'common':common},
             stopped_leaf_certificate=dict(status='PASS exact d^beta>2m after floors',
                 sufficient='b^(epsilon*beta)>4max(m_bit,m_complex)',
                 implication='d=floor(b^epsilon)>=b^epsilon/2 and beta<1 imply d^beta>2max(m_bit,m_complex)',
                 minimum=minimum,reciprocal_exponent_ceiling=kstop,checks=stop_checks,
                 integer_stopping_test='e^v<d^u for fixed beta=u/v; fixed rational exponents need no real-power comparison'),
             microbox_period_power_certificate=period_certificate,
             microbox=dict(side='2^ceil(8log2p)',halo='4096p^3',Neumann_terms='512p^2',
                 source_padding='Q*L=t_i and T/S<2',target_halo_volume='T(1+2A/L)^d<2T',
                 local_inverse='Same global rounded H; principal complement gap and original seams retained',
                 cost='O(T*p^(1+delta)*(d+w^2+d*w^2/L))',
                 exposure_cost='One global O(Tp*p^tau*polylogp) router and O(Tp*d*polylogp) small fields'),
             previous_accepted_kappa=previous,strict_gain=kappa-previous,
             improvement_ratio=kappa/previous,
             compact_upstream_ratio=kappa/COMPACT_KAPPA,
             compact_ratio_decimal_lower=rational_decimal_lower(kappa/COMPACT_KAPPA,15),
             original_baseline_ratio=kappa/BASELINE_KAPPA,
             proof_obligations=['Constructive simultaneous rational metric flags for every useful nondegenerate kernel',
                 'Complete generic source/gate/sink frame conjugation, native table and one shared admissible prime',
                 'Exact stopped growing/root-dominated compact recurrence at the selected rational beta',
                 'Retained max(tau,sigma,chi)<lambda<lambda_prime and leaf/reservation inequalities',
                 'Beta-independent exact semantic child guard with unchanged final-only truncation',
                 'Reviewed arbitrary routing and fixed-tape bulk principal-window/halo/page/crop transfer',
                 'Complete native p^66000 row reservoir and actual complex scalar-G/E guard',
                 'Retained conditional multiplication-machine interfaces'],
             additional_eventual_cutoffs=['Generic giant isometry/table/shared prime not instantiated; deterministic fixed setup constant',
                 'New native alphabet and layout C: e<=C*p, after p>=C; no e<=2p claim',
                 'Fixed rational stopping-test and descriptor constants at beta=u/v',
                 'BHP prime existence and interval packing',
                 'Initial padded sizes and at least three untouched spectator fields',
                 'Polynomial catalogue/setup amortized across full paid microboxes/spectators',
                 'Strict recurrence/polylog absorption constants, including the tiny lambda and leaf gaps',
                 'Complete original conditional theorem thresholds'])
    row['strengthened_real_log_compact_cutoff']=compact_cutoff(row)
    if native_stock:row['compact_row_padding']=general_row_padding(row,primitive)
    return row


if __name__=='__main__':
    raise SystemExit('Import general_witness from the forthcoming pinned composition adapter; this module is a proof/arithmetic component.')
