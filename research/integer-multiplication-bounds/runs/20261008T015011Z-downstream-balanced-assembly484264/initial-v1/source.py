#!/usr/bin/env python3
"""Exact seven-margin assembly for the balanced synthetic-transform layout.

The previous compact-control arithmetic and finite promotions are immutable
inputs. This fresh family charges O(d) prefix work, retains strict K=o(ell)
as geometry, and makes every other analytic/cost obligation explicit.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from downstream_compact_control_assembly import COMPACT_KAPPA, compose as compact_compose
from downstream_gaussian import BASELINE_KAPPA, ceil_q, require
from downstream_generic_compact_composition import strengthened_real_log_cutoff
from downstream_parameter_optimum import as_strings, compact_lower, rational_decimal_lower, saving_enclosure
from downstream_promoted_complex_composition import parse_counts


def compose(n,nc,mode,previous_compact_kappa):
    eb,ec = saving_enclosure(n['eta'],n['m']),saving_enclosure(nc['eta'],nc['m'])
    a,b = eb['chosen_saving'],ec['chosen_saving']
    require(0 < a < b < Q(1,32) and b > 4*a, 'Balanced prefix witness requires b>4a')
    require(mode in ('conservative','tight'), 'Unknown balanced witness mode')
    h = a/16 if mode == 'conservative' else Q(1,2**64)
    c = 1-h
    q = a*(1-2*h)
    x = (q/b)*(1+h)
    beta = 1-x
    tau,sigma = 1-a,1-b
    lp = 1-q
    lam = (tau+lp)/2
    zeta = h
    C1 = 1+4*x+zeta
    # The new prefix has O(d) cost. K=o(ell) is a separate strict
    # geometric condition; it is not required to dominate kappa.
    eps = (1-h)/(1+c)
    geometry = 1-eps*(1+c)
    require(geometry == h > 0, 'Balanced geometric backoff differs')
    r = (1-eps)/2
    delta = r/8
    internal = tau+(1-beta)*max(sigma-tau,Q(0))
    leaf = sigma+beta*(1-sigma)
    reserve = max(1-c,Q(0))
    E = 64*(nc['W']+nc['m']+1)**3
    B = nc['s']+E
    C0 = 32*nc['m']*B*B*(1+1/zeta)
    require(nc['s']*(8+E) <= 9*B*B and 2 <= nc['s'] < nc['m']**5 and
            9*nc['m']*B*B*(1+1/zeta)+18 < C0, 'Balanced stopped guard failed')
    margins = dict(g1=1-eps,g2=eps*a*c,g3=eps*q,g4=a*(1-eps),
                   g5=min(1-eps-delta,r-delta),g6=1-eps-delta,g7=eps)
    G = min(margins.values())
    kappa = compact_lower(G,places=40)
    slacks = dict(bit_primitive=eb['strict_primitive_gap'],complex_primitive=ec['strict_primitive_gap'],
                  primitive_order=b-a,guard_headroom=b-4*a,c_positive=c,c_below_one=1-c,
                  beta_positive=beta,beta_below_one=1-beta,epsilon_positive=eps,epsilon_below_one=1-eps,
                  lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,compact_internal=lam-internal,
                  lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-reserve,
                  guard=1-eps*C1,K_smaller_than_ell=geometry,K_dominates_log_p=eps*c,
                  record_suffix_superpolynomial=1-eps,phase_local_cost=1-eps-delta,
                  phase_boundary_cost=r-delta,gamma_sublinear=1-eps-r,
                  cell_larger_than_band=eps-(1-r)/2,prime_interval_packing=1-eps,alpha_power=r,
                  delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,
                  prefix_vs_layer=margins['g1']-G,movement_vs_layer=margins['g2']-G,
                  crt_vs_layer=margins['g4']-G,gaussian_vs_layer=margins['g5']-G,
                  scalar_vs_layer=margins['g6']-G,dimension_vs_layer=margins['g7']-G,
                  absorption=G-kappa,improvement_over_previous_compact=kappa-previous_compact_kappa,
                  old_prefix_proof_fails=kappa-geometry)
    for name,value in slacks.items():
        require(value > 0, 'Nonpositive balanced assembly slack '+name)
    require(G == margins['g3'] and internal == tau, 'Balanced compact branch/bottleneck differs')
    upper = eb['saving_upper']/2
    require(kappa < upper and kappa > previous_compact_kappa,
            'Balanced strict witness/ceiling comparison failed')
    ka = ceil_q(1/r)
    km = ceil_q(1/(eps*c))
    cutoffs = dict(gamma=ceil_q(Q(7)/(1-eps-r)),logarithmic_alpha=16*ka*ka+1,
                   full_guard=ceil_q(Q((2*ceil_q(C0)).bit_length())/(1-eps*C1)),
                   phase_cell=ceil_q(Q(9)/(eps-(1-r)/2)),compact_controls=64*km*km+1,
                   balanced_geometry=ceil_q(Q(3)/geometry))
    require(cutoffs['gamma']*(1-eps-r) >= 7 and Q(1,ka) <= r,
            'Balanced gamma/log alpha cutoff failed')
    require(cutoffs['full_guard']*(1-eps*C1) >= (2*ceil_q(C0)).bit_length(),
            'Balanced full guard cutoff failed')
    require(cutoffs['phase_cell']*(eps-(1-r)/2) >= 9,
            'Balanced phase cell cutoff failed')
    require(cutoffs['balanced_geometry']*geometry >= 3,
            'Balanced ell/K cutoff failed')
    # Retained size bounds give ell>=b/(2d), d<=b^epsilon, K<=d^c.
    # At log2 b>=3/geometry: ell/K>=b^geometry/2>=4. Consequently
    # K<=ell-1, every balanced group fits, and polynomial suffixes remain.
    row = dict(status='PASS strict exact balanced-layout arithmetic; independent changed-layout transfer review pending',
               mode=mode,bit_counts=n,complex_counts=nc,bit_saving_enclosure=eb,complex_saving_enclosure=ec,
               parameters=dict(tau=tau,sigma=sigma,a_bit=a,a_complex=b,c=c,beta=beta,lambda_=lam,
                 lambda_prime=lp,epsilon=eps,alpha_squared_power=r,delta=delta,zeta=zeta,C0=C0,C1=C1,kappa=kappa),
               recurrence=dict(internal=internal,leaf=leaf,reservations=reserve),
               margins=margins,constraint_slacks=slacks,minimum_margin=G,
               old_prefix_margin=geometry,scoped_model_upper=upper,
               achieved_fraction_of_scoped_upper=kappa/upper,
               previous_compact_kappa=previous_compact_kappa,
               strict_improvement_ratio=kappa/previous_compact_kappa,
               strict_gain=kappa-previous_compact_kappa,
               compact_upstream_ratio=kappa/COMPACT_KAPPA,
               compact_ratio_decimal_lower=rational_decimal_lower(kappa/COMPACT_KAPPA,15),
               original_baseline_ratio=kappa/BASELINE_KAPPA,
               cutoff_log2_b={**cutoffs,'common':max(cutoffs.values())},
               additional_eventual_cutoffs=['Retained initial padded-box size inequalities',
                 'BHP prime threshold and interval packing','Uniform variable-width compact layer extension',
                 'Strict recurrence, descriptor/record and logarithm absorption',
                 'Pinned complete conditional multiplication interfaces'],
               proof_obligations=['Independent all-size balanced positional layout and unequal-width swaps',
                 'Uniform layer width band floor(d^c)<=K_j<2floor(d^c)',
                 'Named frequency/twiddle chronology, disk/error/precision and fixed tape transfer',
                 'Accepted independently promoted finite bit/complex inputs and compact movement/layout/guard',
                 'Accepted phase inverse and retained complete multiplication theorem'])
    row['strengthened_real_log_compact_cutoff'] = strengthened_real_log_cutoff(row)
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--generic-compact',type=Path,required=True)
    ap.add_argument('--balanced-layout',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    started = time.monotonic()
    previous = json.loads(args.generic_compact.read_text())
    layout = json.loads(args.balanced_layout.read_text())
    source_dir = Path(__file__).parent
    for name,expected in previous['source_sha256'].items():
        require(hashlib.sha256((source_dir/name).read_bytes()).hexdigest() == expected,
                'Executed generic compact dependency changed '+name)
    for name,expected in layout['source_sha256'].items():
        require(hashlib.sha256((source_dir/name).read_bytes()).hexdigest() == expected,
                'Executed balanced positional source changed '+name)
    require(layout['cases'] == 3800 and layout['exact_axis_round_chronology_checks'] == 2068936 and
            layout['one_bit_unequal_width_moves'] == 1718, 'Balanced finite protocol differs')
    require(layout['provenance']['commit'] == previous['original_reference']['commit'],
            'Balanced/compact original references differ')
    regressions = []
    for row in previous['witnesses']:
        actual = compact_compose(parse_counts(row['bit_counts']),parse_counts(row['complex_counts']),row['mode'],
                                 Q(row['previous_accepted_kappa']))
        for group in ('parameters','margins','recurrence','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group]) == row[group], 'Historical generic compact regression failed '+group)
        require(as_strings(strengthened_real_log_cutoff(row)) == row['strengthened_real_log_compact_cutoff'],
                'Historical strengthened compact cutoff differs')
        regressions.append(dict(mode=row['mode'],kappa=row['parameters']['kappa'],unchanged=True))
    tight = next(r for r in previous['witnesses'] if r['mode'] == 'tight')
    old = Q(tight['parameters']['kappa'])
    n,nc = parse_counts(tight['bit_counts']),parse_counts(tight['complex_counts'])
    rows = [compose(n,nc,mode,old) for mode in ('conservative','tight')]
    names = ['downstream_balanced_transform_assembly.py','downstream_balanced_transform_layout.py']
    source_hashes = dict(previous['source_sha256'])
    source_hashes.update({name:hashlib.sha256((source_dir/name).read_bytes()).hexdigest() for name in names})
    result = dict(status='PASS exact changed balanced-layout composition; independent transfer/arithmetic review required',
                  campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                  campaign_deadline='2026-10-08T08:25:21Z',generated_at=datetime.now(timezone.utc).isoformat(),
                  original_reference=previous['original_reference'],compact_reference=previous['compact_reference'],
                  promoted_bit_audit=previous['promoted_bit_audit'],promoted_complex_audit=previous['promoted_complex_audit'],
                  source_sha256=source_hashes,
                  input_files={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                               for p in [args.generic_compact,args.balanced_layout]},
                  previous_compact_regressions=regressions,balanced_layout_controls=dict(
                    cases=layout['cases'],axis_round_checks=layout['exact_axis_round_chronology_checks'],
                    unequal_width_decompositions=layout['one_bit_unequal_width_moves']),
                  witnesses=rows,elapsed_seconds=time.monotonic()-started,
                  scope='Changed O(d) prefix layout with strict K geometry and retained remaining margins; tiny scoped improvement, conditional fixed model, no universal optimum or novelty claim')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:
        print('PASS balanced',row['mode'],'bit roles',n['R'],'complex h',nc['h'],
              'kappa',row['parameters']['kappa'],'common cutoff',row['cutoff_log2_b']['common'],flush=True)


if __name__ == '__main__':
    main()
