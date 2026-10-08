#!/usr/bin/env python3
"""Exact compact-control composition with independently promoted finite data.

The old quadratic assembly is preserved. This fresh proof family uses the
new upstream compact-control recurrence, our accepted phase inverse and the
reviewed shared complex primitive. Arithmetic does not establish the new
compact movement/layout/repair proof, whose review is a separate dependency.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import subprocess
import time

from downstream_gaussian import BASELINE_KAPPA, ceil_q, check_sources, require
from downstream_parameter_optimum import as_strings, compact_lower, rational_decimal_lower, saving_enclosure
from downstream_promoted_complex_composition import parse_counts, promoted

COMPACT_REVISION = '6e564879f51ae16f23d392e9e196c605f36d90df'
COMPACT_KAPPA = Q(83,10**12)


def model_ceiling(a,b):
    """An upper bound from the actual seven margins and guard/leaf family."""
    require(0 < a < 1 and 0 < b < 1, 'Invalid primitive savings')
    values = dict(prefix_and_movement=a/(2+a),
                  movement_and_guard=a*b/(4*a+b),
                  leaf_and_guard=b/5)
    return min(values.values()), values


def upstream_regression(certificate):
    p = {k:Q(v) for k,v in certificate['main']['parameters'].items()}
    e,c,t,s,b,d = [p[k] for k in ('epsilon','c','tau','sigma','beta','delta')]
    actual = dict(g1=1-e*(1+c),g2=e*c*(1-t),g3=e*(1-p['lamp']),
                  g4=(1-t)*(1-e),g5=Q(1,4)-d-Q(5,4)*e,
                  g6=1-d-e,g7=e)
    require(as_strings(actual) == certificate['main']['margins'], 'New upstream seven-margin regression failed')
    exponents = dict(internal=t+(1-b)*max(s-t,Q(0)),leaf=s+b*(1-s),
                     preprocessing=max(1-c,Q(0)))
    exponents['layer'] = max(exponents.values())
    require(as_strings(exponents) == certificate['main']['recurrence'], 'New upstream compact recurrence regression failed')
    require(min(actual.values()) == Q(certificate['main']['minimum_margin']) > p['kappa'] == COMPACT_KAPPA,
            'New upstream advertised strict margin changed')
    return dict(status='PASS exact compact upstream recurrence and seven-margin regression',
                parameters=p,minimum_margin=min(actual.values()),advertised_kappa=p['kappa'])


def compose(n,nc,mode,old_kappa):
    eb,ec = saving_enclosure(n['eta'],n['m']),saving_enclosure(nc['eta'],nc['m'])
    a,b = eb['chosen_saving'],ec['chosen_saving']
    require(0 < a < b < Q(1,32), 'Current compact witness uses decaying complex branching')
    require(eb['saving_upper'] < ec['saving_lower'], 'Exact primitive ordering not separated')
    h = Q(1,2**64)
    c = 1-h
    q = a*(1-2*h)
    x = (q/b)*(1+h)
    beta = 1-x
    tau,sigma = 1-a,1-b
    internal = tau+(1-beta)*max(sigma-tau,Q(0))
    leaf = sigma+beta*(1-sigma)
    reserve = max(1-c,Q(0))
    lp = 1-q
    lam = (max(tau,sigma,internal)+lp)/2
    require(mode in ('conservative','tight'), 'Unknown slack mode')
    backoff = Q(1,2**20) if mode == 'conservative' else h
    zeta = Q(1,2**30) if mode == 'conservative' else h
    C1 = 5-4*beta+zeta
    prefix_cap = 1+c+q
    eps = (1-backoff)/max(C1,prefix_cap)
    r = (1-eps)/2
    delta = r/8
    E = 64*(nc['W']+nc['m']+1)**3
    B = nc['s']+E
    # This is the already reviewed coefficient-depth estimate. Compact
    # permutations introduce no scalar arithmetic; general beta is covered
    # by the newly supplied stopped-depth proof, not the older beta>=.9 API.
    C0 = 32*nc['m']*B*B*(1+1/zeta)
    require(9*nc['m']*B*B*(1+1/zeta)+18 < C0,
            'General stopped whole-layer guard constant failed')
    require(nc['s']*(8+E) <= 9*B*B and 2 <= nc['s'] < nc['m']**5,
            'General stopped guard premise failed')
    margins = dict(g1=1-eps*(1+c),g2=eps*a*c,g3=eps*q,
                   g4=a*(1-eps),g5=min(1-eps-delta,r-delta),
                   g6=1-eps-delta,g7=eps)
    G = min(margins.values());kappa = compact_lower(G,places=40)
    slacks = dict(bit_primitive=eb['strict_primitive_gap'],complex_primitive=ec['strict_primitive_gap'],
                  primitive_order=b-a,c_positive=c,c_below_one=1-c,
                  beta_positive=beta,beta_below_one=1-beta,
                  epsilon_positive=eps,epsilon_below_one=1-eps,
                  lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
                  compact_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
                  compact_leaf=lp-leaf,compact_reservations=lp-reserve,
                  guard=1-eps*C1,K_smaller_than_ell=1-eps*(1+c),
                  K_dominates_log_p=eps*c,record_suffix_superpolynomial=1-eps,
                  phase_local_cost=1-eps-delta,phase_boundary_cost=r-delta,
                  gamma_sublinear=1-eps-r,cell_larger_than_band=eps-(1-r)/2,
                  prime_interval_packing=1-eps,alpha_power=r,
                  delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,
                  prefix_vs_layer=margins['g1']-G,movement_vs_layer=margins['g2']-G,
                  crt_vs_layer=margins['g4']-G,gaussian_vs_layer=margins['g5']-G,
                  scalar_vs_layer=margins['g6']-G,dimension_vs_layer=margins['g7']-G,
                  absorption=G-kappa,improvement_over_compact_upstream=kappa-COMPACT_KAPPA,
                  improvement_over_old_accepted=kappa-old_kappa)
    for name,value in slacks.items():require(value > 0, 'Nonpositive compact composition slack '+name)
    require(G == margins['g3'] and internal == tau, 'Wrong current compact bottleneck/branch')
    require(0 < beta < 1 and 0 < r < Q(1,3), 'Current phase/compact parameter domain failed')
    lower_ceiling,lower_branches = model_ceiling(a,b)
    require(lower_ceiling == lower_branches['prefix_and_movement'], 'Current witness is not prefix-limited')
    require(b > 4*a/(1+a) and C1 < prefix_cap, 'Current exact guard headroom failed')
    upper,upper_branches = model_ceiling(eb['saving_upper'],ec['saving_upper'])
    require(kappa < upper, 'Compact scoped ceiling is not above witness')
    ka = ceil_q(1/r)
    km = ceil_q(1/(eps*c))
    compact_cutoff = 64*km*km+1
    # For log2 b=L at and above this cutoff: epsilon*c>=1/km;
    # 2^(L/km)/(32L+160) increases when L>=2km, using log2>=1/2.
    # d>=b^epsilon/2, floor(d^c)>=d^c/2 and 0<c<1 give
    # K>=b^(epsilon*c)/4 >=8L+40 >=G+4ceil(log2 p)+10, p=6b.
    require(compact_cutoff >= 2*km and 2**(compact_cutoff//km) >= 32*compact_cutoff+160,
            'Compact control logarithmic cutoff failed')
    cutoffs = dict(gamma=ceil_q(Q(7)/(1-eps-r)),logarithmic_alpha=16*ka*ka+1,
                   full_guard=ceil_q(Q((2*ceil_q(C0)).bit_length())/(1-eps*C1)),
                   phase_cell=ceil_q(Q(9)/(eps-(1-r)/2)),compact_controls=compact_cutoff)
    require(cutoffs['gamma']*(1-eps-r) >= 7 and Q(1,ka) <= r,
            'Gamma/logarithmic alpha cutoff failed')
    require(cutoffs['full_guard']*(1-eps*C1) >= (2*ceil_q(C0)).bit_length(),
            'Full guard cutoff failed')
    require(cutoffs['phase_cell']*(eps-(1-r)/2) >= 9, 'Phase cell cutoff failed')
    return dict(status='Strict exact compact arithmetic; independent new movement/layout/repair review required',
                mode=mode,bit_counts=n,complex_counts=nc,
                bit_saving_enclosure=eb,complex_saving_enclosure=ec,
                parameters=dict(tau=tau,sigma=sigma,a_bit=a,a_complex=b,beta=beta,c=c,
                                lambda_=lam,lambda_prime=lp,epsilon=eps,alpha_squared_power=r,
                                delta=delta,zeta=zeta,C0=C0,C1=C1,kappa=kappa),
                recurrence=dict(internal=internal,leaf=leaf,reservations=reserve,
                                compact_movement_spacing_power=0),
                prefix_and_guard_denominators=dict(prefix=prefix_cap,guard=C1),
                margins=margins,constraint_slacks=slacks,minimum_margin=G,
                scoped_model_upper=upper,scoped_model_upper_branches=upper_branches,
                achieved_fraction_of_scoped_upper=kappa/upper,
                kappa_ratio_to_compact_upstream=kappa/COMPACT_KAPPA,
                compact_ratio_decimal_lower=rational_decimal_lower(kappa/COMPACT_KAPPA,15),
                kappa_ratio_to_baseline=kappa/BASELINE_KAPPA,
                baseline_ratio_decimal_lower=rational_decimal_lower(kappa/BASELINE_KAPPA,15),
                previous_accepted_kappa=old_kappa,
                cutoff_log2_b={**cutoffs,'common':max(cutoffs.values())},
                additional_eventual_cutoffs=['BHP prime threshold and interval packing',
                                            'Strict compact recurrence, descriptor/record and logarithm absorption',
                                            'Retained original fixed-tape multiplication and rounding interfaces'],
                proof_obligations=['Independently promoted rational bit circuit',
                                   'Accepted shared complex scalar/binary-frame/guard/rank proof',
                                   'Accepted phase-cell/GS/Schur Gaussian inverse and BHP transfer',
                                   'New compact movement, complete-field layout, dirty repair and generalized guard review',
                                   'Pinned complete conditional multiplication theorem'])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--original-upstream',type=Path,required=True)
    ap.add_argument('--compact-upstream',type=Path,required=True)
    ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--promotion-review',type=Path,required=True)
    ap.add_argument('--complex-certificate',type=Path,required=True)
    ap.add_argument('--old-accepted-assembly',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args();require(not args.output.exists(),'Use a fresh result path')
    start = time.monotonic();original = check_sources(args.original_upstream)
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=args.compact_upstream,text=True).strip()
    require(revision == COMPACT_REVISION, 'Wrong separately pinned compact-control input')
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=args.compact_upstream,text=True),
            'Compact input checkout was modified')
    candidate_bytes = args.candidate.read_bytes();candidate = json.loads(candidate_bytes)
    promotion = json.loads(args.promotion_review.read_text())
    n,finite = promoted(candidate,promotion,original['commit'],candidate_bytes)
    cx = json.loads(args.complex_certificate.read_text())
    require(cx['provenance']['commit'] == original['commit'],'Complex input changed reference')
    row = next(r for r in cx['cases'] if r['h'] == 50)
    require(row['terminal']['every_terminal_complement_nondegenerate_nonalternating'] and
            row['matching']['involution'] and row['guard']['stopped_depth_branching_premise'],
            'Accepted complex finite prerequisites absent')
    nc = parse_counts(row['shared_complex_counts'])
    old = json.loads(args.old_accepted_assembly.read_text())
    old_kappa = max(Q(r['parameters']['kappa']) for r in old['witnesses'])
    compact_certificate = args.compact_upstream/'certificates/compact-control-layer.json'
    regression = upstream_regression(json.loads(compact_certificate.read_text()))
    witnesses = [compose(n,nc,mode,old_kappa) for mode in ('conservative','tight')]
    source = Path(__file__)
    names = ['downstream_compact_control_assembly.py','downstream_promoted_complex_composition.py',
             'downstream_complex_assembly.py','downstream_gaussian.py','downstream_parameter_optimum.py']
    files = ['notes/compact-control-movement.tex','notes/compact-control-layout.tex',
             'notes/compact-control-guard.tex','notes/independent-complex.tex',
             'scripts/compact_control_layer.py','scripts/prepare_layers.py','scripts/certify.py']
    result = dict(status='PASS exact candidate compact composition; new compact proof review pending',
                  campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                  campaign_deadline='2026-10-08T08:25:21Z',generated_at=datetime.now(timezone.utc).isoformat(),
                  original_reference=original,compact_reference=dict(commit=revision,
                    upstream_url='https://github.com/CrocSwap/integer-mult-bounds',
                    path=str(args.compact_upstream),pristine=True,
                    source_sha256={name:hashlib.sha256((args.compact_upstream/name).read_bytes()).hexdigest() for name in files}),
                  input_files={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in
                               [args.candidate,args.promotion_review,args.complex_certificate,args.old_accepted_assembly,compact_certificate]},
                  source_sha256={name:hashlib.sha256((source.parent/name).read_bytes()).hexdigest() for name in names},
                  promoted_finite_audit=finite,upstream_compact_arithmetic_regression=regression,
                  witnesses=witnesses,elapsed_seconds=time.monotonic()-start,
                  scope='New separately pinned compact-control estimate plus accepted finite/phase branches; not a formal machine verification, universal optimum or novelty claim')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in witnesses:
        print('PASS compact',row['mode'],'roles',finite['roles'],'kappa',row['parameters']['kappa'],
              'ratio to83e-12 >=',row['compact_ratio_decimal_lower'],'cutoff',row['cutoff_log2_b']['common'],flush=True)


if __name__ == '__main__':main()
