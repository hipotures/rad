#!/usr/bin/env python3
"""Exact conditional arithmetic for the proposed arbitrary-bit router.

The new routing contract is a hypothesis pending independent construction
and transfer review. Synthetic positional movement gains margin a, while
resampling exposure retains a(1-epsilon). A separate explicitly unproved
bulk-exposure branch records its larger conditional consequence. The
original uniform-K prefix is retained in the minimal-dependency row.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from downstream_compact_control_assembly import COMPACT_KAPPA, compose as old_compose
from downstream_gaussian import BASELINE_KAPPA, ceil_q, require
from downstream_generic_compact_composition import strengthened_real_log_cutoff
from downstream_parameter_optimum import as_strings, compact_lower, rational_decimal_lower, saving_enclosure
from downstream_promoted_complex_composition import parse_counts


def ceiling(a,b):
    require(0 < a < b < 1, 'Current routing family requires b>a')
    branches = dict(compact_and_guard=a*b/(4*a+b),leaf_and_guard=b/5)
    return min(branches.values()),branches


def witness(n,nc,mode,prefix,exposure,previous_kappa):
    eb,ec = saving_enclosure(n['eta'],n['m']),saving_enclosure(nc['eta'],nc['m'])
    a,b = eb['chosen_saving'],ec['chosen_saving']
    require(0 < a < b < Q(1,32), 'Routing witness requires decaying compact branch')
    require(mode in ('conservative','tight') and prefix in ('original','balanced'), 'Unknown routing row')
    require(exposure in ('retained','bulk_unproved'), 'Unknown resampling exposure branch')
    h = (a/16 if exposure == 'retained' else Q(1,2**20)) if mode == 'conservative' else Q(1,2**64)
    c = Q(1,8)
    q = a*(1-2*h)
    x = (q/b)*(1+h)
    beta = 1-x
    tau,sigma = 1-a,1-b
    lp = 1-q
    lam = (tau+lp)/2
    zeta = h
    C1 = 1+4*x+zeta
    eps = Q(1,2) if exposure == 'retained' else (1-h)/C1
    r = (1-eps)/2
    delta = r/8
    internal = tau+(1-beta)*max(sigma-tau,Q(0))
    leaf = sigma+beta*(1-sigma)
    reserve = max(1-c,Q(0))
    E = 64*(nc['W']+nc['m']+1)**3
    B = nc['s']+E
    C0 = 32*nc['m']*B*B*(1+1/zeta)
    require(2 <= nc['s'] < nc['m']**5 and nc['s']*(8+E) <= 9*B*B and
            9*nc['m']*B*B*(1+1/zeta)+18 < C0, 'Routing stopped guard premise failed')
    prefix_margin = 1-eps*(1+c) if prefix == 'original' else 1-eps
    crt_and_exposure_margin = a*(1-eps) if exposure == 'retained' else a
    margins = dict(g1=prefix_margin,g2=a,g3=eps*q,g4=crt_and_exposure_margin,
                   g5=min(1-eps-delta,r-delta),g6=1-eps-delta,g7=eps)
    G = min(margins.values())
    kappa = compact_lower(G,places=40)
    geometry = 1-eps*(1+c)
    slacks = dict(bit_primitive=eb['strict_primitive_gap'],complex_primitive=ec['strict_primitive_gap'],
                  primitive_order=b-a,c_positive=c,c_below_one=1-c,beta_positive=beta,beta_below_one=1-beta,
                  epsilon_positive=eps,epsilon_below_one=1-eps,lambda_above_tau=lam-tau,
                  lambda_above_sigma=lam-sigma,compact_internal=lam-internal,
                  lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-reserve,
                  guard=1-eps*C1,K_smaller_than_ell=geometry,K_dominates_log_p=eps*c,
                  record_suffix_superpolynomial=1-eps,phase_local_cost=1-eps-delta,
                  phase_boundary_cost=r-delta,gamma_sublinear=1-eps-r,
                  cell_larger_than_band=eps-(1-r)/2,prime_interval_packing=1-eps,alpha_power=r,
                  delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,
                  prefix_vs_layer=margins['g1']-G,movement_vs_layer=a-G,
                  crt_vs_layer=crt_and_exposure_margin-G,
                  gaussian_vs_layer=margins['g5']-G,scalar_vs_layer=margins['g6']-G,
                  dimension_vs_layer=eps-G,absorption=G-kappa,
                  improvement_over_accepted_compact=kappa-previous_kappa,
                  old_nonadjacent_layout_margin_fails=kappa-eps*a*c)
    if exposure == 'bulk_unproved':
        slacks['old_nonadjacent_crt_margin_fails'] = kappa-a*(1-eps)
    for name,value in slacks.items():
        require(value > 0, 'Nonpositive routing hypothesis slack '+name)
    require(G == margins['g3'] and internal == tau, 'Wrong routing hypothesis minimum/recurrence branch')
    lower,branches = ceiling(a,b)
    upper,upper_branches = ceiling(eb['saving_upper'],ec['saving_upper'])
    if exposure == 'retained':
        upper_branches['retained_resampling_exposure'] = eb['saving_upper']/2
        upper = min(upper_branches.values())
    require(lower == branches['compact_and_guard'] and kappa < upper, 'Routing scoped ceiling failed')
    ka,km = ceil_q(1/r),ceil_q(1/(eps*c))
    cutoffs = dict(gamma=ceil_q(Q(7)/(1-eps-r)),logarithmic_alpha=16*ka*ka+1,
                   full_guard=ceil_q(Q((2*ceil_q(C0)).bit_length())/(1-eps*C1)),
                   phase_cell=ceil_q(Q(9)/(eps-(1-r)/2)),compact_controls=64*km*km+1,
                   transform_geometry=ceil_q(Q(3)/geometry),routing_reservoirs=14)
    require(cutoffs['gamma']*(1-eps-r) >= 7 and Q(1,ka) <= r and
            cutoffs['full_guard']*(1-eps*C1) >= (2*ceil_q(C0)).bit_length() and
            cutoffs['phase_cell']*(eps-(1-r)/2) >= 9 and cutoffs['transform_geometry']*geometry >= 3,
            'Routing hypothesis numeric parameter cutoff failed')
    # For the outer integer assembly, n_address >=b/8=p/48 once b>=8
    # and d>=2. The retained sizes give log2 T>=b/2 and
    # ell<=log2(T)/d+1, hence log2(M)>=b/4-1>=b/8.
    # At real L=log2 b>=14, p=6b>=768(4L+22)>=768G,
    # so n_address>=16G. With router K_r=64G,
    # H=ceil(n_address/K_r)G<=n_address/64+G<=5n_address/64;
    # therefore9H<n_address. Monotonicity follows from log2>1/2.
    L0 = cutoffs['routing_reservoirs']
    require(6*2**L0 > 768*(4*L0+22) and L0 >= 2,
            'Declared router reservoir cutoff failed')
    row = dict(status='STRICT EXACT ARITHMETIC UNDER UNREVIEWED ROUTING HYPOTHESIS; NO PROMOTION',
               mode=mode,prefix=prefix,resampling_exposure=exposure,bit_counts=n,complex_counts=nc,
               bit_saving_enclosure=eb,complex_saving_enclosure=ec,
               parameters=dict(tau=tau,sigma=sigma,a_bit=a,a_complex=b,c=c,beta=beta,lambda_=lam,
                 lambda_prime=lp,epsilon=eps,alpha_squared_power=r,delta=delta,zeta=zeta,C0=C0,C1=C1,kappa=kappa),
               margins=margins,constraint_slacks=slacks,minimum_margin=G,
               recurrence=dict(internal=internal,leaf=leaf,reservations=reserve),
               proposed_positional_routing_cost='O(V*p^tau*polylog(p)); record suffix exceeds every fixed polynomial in p',
               original_prefix_retained=(prefix == 'original'),scoped_hypothesis_upper=upper,
               scoped_hypothesis_upper_branches=upper_branches,
               achieved_fraction_of_scoped_upper=kappa/upper,
               previous_accepted_compact_kappa=previous_kappa,strict_gain=kappa-previous_kappa,
               strict_improvement_ratio=kappa/previous_kappa,
               improvement_ratio_decimal_lower=rational_decimal_lower(kappa/previous_kappa,15),
               compact_upstream_ratio=kappa/COMPACT_KAPPA,
               compact_ratio_decimal_lower=rational_decimal_lower(kappa/COMPACT_KAPPA,15),
               original_baseline_ratio=kappa/BASELINE_KAPPA,
               cutoff_log2_b={**cutoffs,'common':max(cutoffs.values())},
               additional_eventual_cutoffs=['Generalized arbitrary-source packed gadget and exact exceptional repair',
                 'Three-reservoir matching partition, relocation and fixed-tape routing schedule',
                 'Superpolynomial spectator record construction for arrays whose coefficient records have O(p) bits',
                 'Retained initial size and descriptor/record domination thresholds',
                 'BHP prime interval and strict recurrence/logarithm absorption',
                 'Pinned complete conditional multiplication interfaces'],
               proof_obligations=['PROPOSED arbitrary bit-coordinate routing theorem independently reviewed',
                 'Retained arbitrary-gap chunk-swap with original bit exponent tau, no circular new multiplier',
                 'Sources unchanged between completed gadgets; reservoir completeness; exact bad-address inverse',
                 'Routing synthetic layout and CRT axis reversal without changing arithmetic or padding',
                 'Accepted promoted finite bit/complex, compact layer and phase inverse interfaces'])
    if exposure == 'bulk_unproved':
        row['proof_obligations'].insert(0,'UNPROVED bulk resampling-axis exposure/removal of the d separate routing calls')
        row['status'] = 'ARITHMETIC ONLY UNDER EXTRA UNPROVED BULK RESAMPLING EXPOSURE; NO IMPROVED HEADLINE'
    row['strengthened_real_log_compact_cutoff'] = strengthened_real_log_cutoff(row)
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--accepted-generic-compact',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    started = time.monotonic()
    accepted = json.loads(args.accepted_generic_compact.read_text())
    source_dir = Path(__file__).parent
    for name,expected in accepted['source_sha256'].items():
        require(hashlib.sha256((source_dir/name).read_bytes()).hexdigest() == expected,
                'Accepted compact source changed '+name)
    regressions = []
    for row in accepted['witnesses']:
        actual = old_compose(parse_counts(row['bit_counts']),parse_counts(row['complex_counts']),row['mode'],
                             Q(row['previous_accepted_kappa']))
        for group in ('parameters','margins','recurrence','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group]) == row[group], 'Accepted compact regression failed '+group)
        regressions.append(dict(mode=row['mode'],kappa=row['parameters']['kappa'],unchanged=True))
    selected = next(r for r in accepted['witnesses'] if r['mode'] == 'tight')
    n,nc = parse_counts(selected['bit_counts']),parse_counts(selected['complex_counts'])
    old = Q(selected['parameters']['kappa'])
    rows = [witness(n,nc,mode,prefix,exposure,old) for exposure in ('retained','bulk_unproved')
            for mode in ('conservative','tight') for prefix in ('original','balanced')]
    for exposure in ('retained','bulk_unproved'):
        for mode in ('conservative','tight'):
            pair = [r for r in rows if r['mode'] == mode and r['resampling_exposure'] == exposure]
            require(pair[0]['parameters']['kappa'] == pair[1]['parameters']['kappa'] and
                    pair[0]['minimum_margin'] == pair[1]['minimum_margin'],
                    'Routing witness unnecessarily depends on balanced prefix')
    source_hashes = dict(accepted['source_sha256'])
    source_hashes[Path(__file__).name] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result = dict(status='PASS EXACT HYPOTHESIS ARITHMETIC; ROUTING PROOF/TRANSFER UNREVIEWED; NOT A HEADLINE',
                  campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                  campaign_deadline='2026-10-08T08:25:21Z',generated_at=datetime.now(timezone.utc).isoformat(),
                  original_reference=accepted['original_reference'],compact_reference=accepted['compact_reference'],
                  input_file=dict(path=str(args.accepted_generic_compact),bytes=args.accepted_generic_compact.stat().st_size,
                    sha256=hashlib.sha256(args.accepted_generic_compact.read_bytes()).hexdigest()),
                  source_sha256=source_hashes,promoted_bit_audit=accepted['promoted_bit_audit'],
                  promoted_complex_audit=accepted['promoted_complex_audit'],accepted_compact_regressions=regressions,
                  witnesses=rows,elapsed_seconds=time.monotonic()-started,
                  scope='Conditional parameter consequence of a fresh routing hypothesis; original prefix row isolates that sole new construction; no established routing bound, promoted kappa, universal optimum or novelty claim')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:
        print('HYPOTHESIS ONLY',row['resampling_exposure'],row['mode'],row['prefix'],'kappa',row['parameters']['kappa'],
              'cutoff',row['cutoff_log2_b']['common'],flush=True)


if __name__ == '__main__':
    main()
