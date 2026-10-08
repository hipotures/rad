#!/usr/bin/env python3
"""Exact prospective composition of linear semantic guard and bulk resampling.

All rows explicitly require the fresh router and the complete microbox
fixed-tape transfer. Passing arithmetic is not a promoted multiplication
claim. The accepted finite inputs and old assembly are regressed unchanged.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from downstream_compact_control_assembly import COMPACT_KAPPA,compose as old_compose
from downstream_gaussian import BASELINE_KAPPA,ceil_q,require
from downstream_parameter_optimum import as_strings,compact_lower,rational_decimal_lower,saving_enclosure
from downstream_promoted_complex_composition import parse_counts


def compressed_power_certificate(exponent,right):
    """Prove 2^exponent>right without allocating an exponential integer."""
    require(exponent>=right.bit_length(),'Compressed strict power comparison failed')
    return dict(exponent=exponent,right=right,right_bit_length=right.bit_length(),
                strict=True,proof='2^exponent>=2^bit_length(right)>right')


def compact_cutoff(row):
    eps,c=Q(row['parameters']['epsilon']),Q(row['parameters']['c'])
    k=ceil_q(1/(eps*c));L0=row['cutoff_log2_b']['compact_controls']
    require(L0==64*k*k+1 and L0>=2*k,'Compact cutoff changed')
    certificate=compressed_power_certificate(L0//k,32*L0+192)
    return dict(status='PASS exact compressed real-L compact-field comparison',L0=L0,k=k,
        denominator_slope=32,denominator_constant=192,strict_power_certificate=certificate,
        K_lower_bound='8*log2(b_input)+48',required_bound='8*ceil(log2(p))+16',
        real_log_ceiling='ceil(log2(p))<=log2(b_input)+4,p=6*b_input')


def witness(n,nc,mode,prefix,previous):
    eb,ec=saving_enclosure(n['eta'],n['m']),saving_enclosure(nc['eta'],nc['m'])
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
    saving_upper=eb['saving_upper']
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
    row=dict(status='EXACT PROSPECTIVE ARITHMETIC; ROUTER/MICROBOX/SEMANTIC TRANSFER REVIEW REQUIRED',
      mode=mode,prefix=prefix,bit_counts=n,complex_counts=nc,
      bit_saving_enclosure=eb,complex_saving_enclosure=ec,
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
      scoped_hypothesis_upper=upper,achieved_fraction_of_scoped_upper=kappa/upper,
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
    ap.add_argument('--accepted-generic-compact',type=Path,required=True)
    ap.add_argument('--semantic-controls',type=Path,required=True)
    ap.add_argument('--microbox-controls',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic();source_dir=Path(__file__).parent
    old=json.loads(args.accepted_generic_compact.read_text())
    for name,sha in old['source_sha256'].items():
        require(hashlib.sha256((source_dir/name).read_bytes()).hexdigest()==sha,'Accepted source changed '+name)
    semantic=json.loads(args.semantic_controls.read_text());micro=json.loads(args.microbox_controls.read_text())
    for name,data in [('downstream_semantic_guard.py',semantic),('downstream_microbox_locality.py',micro)]:
        require(hashlib.sha256((source_dir/name).read_bytes()).hexdigest()==data['source_sha256'],
            'New proof control source changed '+name)
    require(semantic['interfaces']['exact_tensor_entries']==5460 and semantic['recurrences']['exact_stopped_cases']==240,
            'Semantic control protocol differs')
    require(micro['locality']['windows']==48 and micro['phase']['windows']==6 and micro['fractional']['cores']==13188,
            'Microbox finite control protocol differs')
    regressions=[]
    for row in old['witnesses']:
        actual=old_compose(parse_counts(row['bit_counts']),parse_counts(row['complex_counts']),row['mode'],
                           Q(row['previous_accepted_kappa']))
        for group in ('parameters','margins','recurrence','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group])==row[group],'Accepted unchanged regression failed '+group)
        regressions.append(dict(mode=row['mode'],kappa=row['parameters']['kappa'],unchanged=True))
    tight=next(r for r in old['witnesses'] if r['mode']=='tight')
    n,nc=parse_counts(tight['bit_counts']),parse_counts(tight['complex_counts']);previous=Q(tight['parameters']['kappa'])
    rows=[witness(n,nc,mode,prefix,previous) for mode in ('conservative','tight') for prefix in ('original','balanced')]
    hashes=dict(old['source_sha256'])
    for name in ['downstream_semantic_bulk_assembly.py','downstream_semantic_guard.py','downstream_microbox_locality.py']:
        hashes[name]=hashlib.sha256((source_dir/name).read_bytes()).hexdigest()
    result=dict(status='PASS PROSPECTIVE EXACT ARITHMETIC; NO PROMOTED HEADLINE UNTIL FULL TRANSFER REVIEW',
        campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',campaign_deadline='2026-10-08T08:25:21Z',
        generated_at=datetime.now(timezone.utc).isoformat(),original_reference=old['original_reference'],
        compact_reference=old['compact_reference'],promoted_bit_audit=old['promoted_bit_audit'],
        promoted_complex_audit=old['promoted_complex_audit'],source_sha256=hashes,
        input_files={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                     for p in (args.accepted_generic_compact,args.semantic_controls,args.microbox_controls)},
        old_assembly_regressions=regressions,witnesses=rows,elapsed_seconds=time.monotonic()-started,
        scope='Exact consequence of three fresh constructions/estimates with explicit remaining independent review; not a universal optimum or novelty claim')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:
        print('PROSPECTIVE ONLY',row['mode'],row['prefix'],'kappa',row['parameters']['kappa'],
            'common cutoff',row['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
