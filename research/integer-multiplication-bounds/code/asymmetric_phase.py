#!/usr/bin/env python3
"""Exact unequal-motif composition with the reviewed phase-cell inverse.

Input circuit/count certificates and the independent all-size analytic
review are separate proof dependencies. This file checks their composed
strict parameters and explicit eventual cutoffs, not the main theorem.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from asymmetric_motif import counts, complex_counts
from downstream_gaussian import BASELINE_KAPPA, ceil_q, check_sources
from downstream_parameter_optimum import (as_strings, compact_lower,
                                          rational_decimal_lower, root_enclosure,
                                          saving_enclosure)


def compose(n, mode='optimized'):
    assert n['D'] > 0 and 2 <= n['s'] < n['m']**5
    nc = complex_counts()
    assert 2*nc['L'] < nc['N'] and 2 <= nc['s'] < nc['m']**5
    eb = saving_enclosure(n['eta'], n['m'])
    ec = saving_enclosure(nc['eta'], nc['m'])
    a, b = eb['chosen_saving'], ec['chosen_saving']
    xlo, xhi = root_enclosure(a, b)
    beta = 1-xhi
    tau, sigma = 1-a, 1-b
    c = a*beta/(tau+a*beta)*(1-Q(1, 2**32))
    q = a*c
    lp = 1-q
    threshold = tau*(1+c/beta)
    lam = (lp+threshold)/2
    guard_b = nc['s']+64*(nc['W']+nc['m']+1)**3
    if mode == 'conservative':
        eps, r, delta, c1 = Q(9, 10), Q(1, 20), Q(1, 1000), Q(11, 10)
        c0 = 256*nc['m']*guard_b**2
        zeta = Q(1, 20)
        assert beta >= Q(999, 1000)
    else:
        assert mode == 'optimized'
        zeta = Q(1, 2**30)
        c1 = 5-4*beta+zeta
        eps = (1-Q(1, 2**20))/c1
        r = (1-eps)/2
        delta = r/8
        c0 = 32*nc['m']*guard_b**2*(1+1/zeta)
    local, border = 1-eps-delta, r-delta
    margins = dict(g1=1-eps*(1+c), g2=eps*a*c, g3=eps*q,
                   g4=a*(1-eps), g5=min(local, border),
                   g6=1-delta-eps, g7=eps)
    minimum = min(margins.values())
    kappa = compact_lower(minimum)
    slacks = dict(bit_primitive=eb['strict_primitive_gap'],
                  complex_primitive=ec['strict_primitive_gap'],
                  lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
                  packed_recurrence=lam-threshold,
                  lambda_prime_above_lambda=lp-lam,
                  leaf_cost=lp-(sigma+beta*(1-sigma)),
                  guard=1-eps*c1, local_convolution_cost=local,
                  boundary_solve_cost=border, gamma_sublinear=1-eps-r,
                  cell_larger_than_band=eps-(1-r)/2,
                  prime_interval_and_line_growth=1-eps, alpha_power=r,
                  prefix_cost=1-eps*(1+c), scalar_cost=1-delta-eps,
                  K_smaller_than_ell=1-eps-eps*c,
                  absorption=minimum-kappa)
    assert all(v > 0 for v in slacks.values())
    guard_domination = c1-(5-4*beta+zeta)
    assert guard_domination >= 0 and Q(9, 10) <= beta < 1 and 0 < r <= Q(1, 3)
    assert minimum == margins['g2'] == margins['g3']
    _, ux = root_enclosure(eb['saving_upper'], ec['saving_upper'])
    model_upper = ec['saving_upper']*ux/(1+4*ux)
    assert kappa < model_upper
    gamma = ceil_q(7/(1-eps-r))
    k = ceil_q(1/r)
    alpha = 16*k*k+1
    guard = ceil_q(Q((2*ceil_q(c0)).bit_length())/(1-eps*c1))
    cell = ceil_q(Q(9)/(eps-(1-r)/2))
    assert gamma*(1-eps-r) >= 7
    assert Q(1, k) <= r
    assert guard*(1-eps*c1) >= (2*ceil_q(c0)).bit_length()
    assert cell*(eps-(1-r)/2) >= 9
    return dict(status='Conditional strict phase-cell composition; separate finite and analytic proofs retained',
                mode=mode, counts=n, retained_complex_counts=nc,
                bit_saving_enclosure=eb, complex_saving_enclosure=ec,
                balance_root_interval=[xlo, xhi],
                parameters={'tau':tau, 'sigma':sigma, 'a_bit':a, 'a_complex':b,
                            'beta':beta, 'c':c, 'lambda':lam, 'lambda_prime':lp,
                            'epsilon':eps, 'alpha_squared_power':r, 'delta':delta,
                            'guard_piece_allowance':zeta, 'C1':c1, 'C0':c0, 'kappa':kappa},
                constraint_slacks=slacks, nonstrict_guard_domination=guard_domination,
                margins=margins, minimum_margin=minimum,
                kappa_decimal_lower=rational_decimal_lower(kappa, 30),
                kappa_ratio_to_baseline=kappa/BASELINE_KAPPA,
                kappa_ratio_decimal_lower=rational_decimal_lower(kappa/BASELINE_KAPPA, 12),
                strict_dyadic_2_to_minus_57=kappa > Q(1, 2**57),
                strict_simple_11_over_2_to_60=kappa > Q(11, 2**60),
                guard_family_model_upper=model_upper,
                achieved_fraction_of_upper=kappa/model_upper,
                cutoff_log2_b={'gamma':gamma, 'logarithmic_alpha':alpha,
                               'full_guard':guard, 'phase_cell':cell,
                               'common':max(gamma, alpha, guard, cell)},
                additional_eventual_cutoffs=['BHP Theorem 1 and prime interval separation',
                                            'Retained original multiplication interfaces'],
                proof_inputs={'finite':'Exact source graphs, support-envelope compiler, arbitrary scratch restoration, rational tensor joining and ranks',
                              'analytic':'Reviewed phase cells, short Toeplitz convolutions, circular Schur solver, residual precision, fixed tapes and amortized setup',
                              'main':'Pinned complete conditional multiplication theorem remains assumed'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, required=True)
    parser.add_argument('--motif-certificate', type=Path, required=True)
    parser.add_argument('--phase-certificate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    provenance = check_sources(args.upstream)
    motif = json.loads(args.motif_certificate.read_text())
    phase = json.loads(args.phase_certificate.read_text())
    assert motif['provenance']['commit'] == provenance['commit']
    assert phase['provenance']['commit'] == provenance['commit']
    # Exact regression against all independently reviewed uniform phase rows.
    regressions = []
    for row in phase['witnesses']:
        h, roles, mode = row['bit_ground'], row['physical_side_roles'], row['mode']
        composed = compose(counts(h, h, roles, roles), mode)
        for name, value in composed['parameters'].items():
            assert Q(value) == Q(row['parameters'][name]), (name, h, roles, mode)
        assert str(composed['minimum_margin']) == row['minimum_margin']
        assert composed['cutoff_log2_b']['common'] == row['common_log2_b_cutoff']
        regressions.append(dict(ground=h, roles=roles, mode=mode, passed=True))
    roles = {int(h):int(r) for h,r in motif['verified_role_counts'].items()}
    candidates = []
    for p, rp in sorted(roles.items()):
        for q, rq in sorted(roles.items()):
            n = counts(p, q, rp, rq)
            if n['D'] > 0:
                candidates.append(compose(n))
    candidates.sort(key=lambda row:row['parameters']['kappa'], reverse=True)
    best = candidates[0]
    assert (best['counts']['p'], best['counts']['q']) == (52, 48)
    conservative = compose(best['counts'], 'conservative')
    result = dict(campaign_id='20261007T222521Z', generated_at=datetime.now(timezone.utc).isoformat(),
                  provenance=provenance,
                  inputs={str(p):{'bytes':p.stat().st_size,'sha256':sha256(p.read_bytes()).hexdigest()} for p in
                          (args.motif_certificate, args.phase_certificate)},
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in
                          (Path(__file__), Path(__file__).with_name('asymmetric_motif.py'))},
                  best=best, conservative_selected=conservative,
                  uniform_phase_regressions=regressions,
                  verified_role_counts=roles,
                  ranking=[dict(p=row['counts']['p'], q=row['counts']['q'],
                                kappa=row['parameters']['kappa'],
                                baseline_ratio_lower=row['kappa_ratio_decimal_lower']) for row in candidates],
                  elapsed_seconds=time.monotonic()-start,
                  scope='Original packed recurrence and stated refined guard family; reviewed phase inverse; supplied unequal bit circuits; retained complex h50; no general optimum or unconditional theorem claim')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    assert not args.output.exists(), 'Use a fresh output path'
    args.output.write_text(json.dumps(as_strings(result), indent=2)+'\n')
    print(json.dumps(as_strings(dict(kappa=best['parameters']['kappa'],
                                    ratio_lower=best['kappa_ratio_decimal_lower'],
                                    log2_b_cutoff=best['cutoff_log2_b']['common'],
                                    modes_checked=len(regressions), elapsed_seconds=result['elapsed_seconds']))), flush=True)


if __name__ == '__main__':
    main()
