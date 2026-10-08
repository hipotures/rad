#!/usr/bin/env python3
"""Independent exact arithmetic audit of the phase-cell parameter family."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

from review_parameter_audit import log_series, log_integer, root_signs


def ceiling(x):
    return -(-x.numerator//x.denominator)


def audit(row):
    h, roles = row['bit_ground'], row['physical_side_roles']
    v, m = comb(h, 3), h**3
    n = v**3
    w = 2*n+2*v*v*(roles+h)
    loss = 3*v*v*h*h
    deficit, s = n-2*loss, w*m-n+2*loss
    eta = Q(deficit, w*m)
    for key, value in dict(v=v, m=m, N=n, W=w, L=loss, D=deficit, s=s, eta=eta).items():
        assert Q(row['counts'][key]) == value
    vc, mc = comb(50, 3), 50**3
    nc = vc**3
    wc = 2*nc+3*vc*vc*(vc*(comb(47, 3)+141)+51)
    lc = 3*vc*vc*51*50
    sc = wc*mc-2*nc+2*lc
    etac = Q(wc*mc-sc, wc*mc)
    for key, value in dict(ground=50, m=mc, W=wc, L=lc, s=sc).items():
        assert Q(row['retained_complex_counts'][key]) == value
    for name, fraction, radix in [('bit', eta, m), ('complex', etac, mc)]:
        alo, ahi = log_series(1/(1-fraction), 20)
        blo, bhi = log_integer(radix, 48)
        enclosure = row[name+'_saving_enclosure']
        assert Q(enclosure['saving_lower']) < alo/bhi < ahi/blo < Q(enclosure['saving_upper'])
        assert 0 < Q(enclosure['chosen_saving']) < alo/bhi
    p = {key: Q(value) for key, value in row['parameters'].items()}
    a, b, beta, c = (p[key] for key in ('a_bit', 'a_complex', 'beta', 'c'))
    e, r, delta, zeta = (p[key] for key in
                         ('epsilon', 'alpha_squared_power', 'delta', 'guard_piece_allowance'))
    tau, sigma, lam, lamp = (p[key] for key in ('tau', 'sigma', 'lambda', 'lambda_prime'))
    assert tau == 1-a and sigma == 1-b
    _, xhi = root_signs(a, b, row['balance_root_interval'])
    assert beta == 1-xhi
    assert c == a*beta/(tau+a*beta)*(1-Q(1, 2**32))
    threshold = tau*(1+c/beta)
    assert 1-lamp == a*c and lam == (threshold+lamp)/2
    B = sc+64*(wc+mc+1)**3
    if row['mode'] == 'conservative':
        assert e == Q(9, 10) and r == Q(1, 20) and delta == Q(1, 1000)
        assert zeta == Q(1, 20) and p['C1'] == Q(11, 10)
        assert beta >= Q(999, 1000)
        assert p['C0'] == 256*mc*B*B
        assert 9*(1+1/zeta)+18 == 207 < 256
    else:
        assert row['mode'] == 'optimized'
        assert zeta == Q(1, 2**30)
        assert p['C1'] == 5-4*beta+zeta
        assert e == (1-Q(1, 2**20))/p['C1']
        assert r == (1-e)/2 and delta == r/8
        assert p['C0'] == 32*mc*B*B*(1+1/zeta)
        assert 9*(1+1/zeta)+18 < 32*(1+1/zeta)
    assert p['C1'] >= 5-4*beta+zeta
    slacks = dict(tau_positive=tau, bit_saving_positive=a,
                  sigma_positive=sigma, complex_saving_positive=b,
                  c_positive=c, epsilon_positive=e, epsilon_below_one=1-e,
                  beta_positive=beta, beta_below_one=1-beta,
                  lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
                  lambda_below_one=1-lam, packed_recurrence=lam-threshold,
                  lambda_prime_above_lambda=lamp-lam, leaf_cost=lamp-sigma-beta*b,
                  lambda_prime_below_one=1-lamp, guard_width=1-e*p['C1'],
                  crt_layout=a*(1-e), prefix_cost=1-e*(1+c), scalar_cost=1-delta-e,
                  local_convolution_cost=1-e-delta, boundary_solve_cost=r-delta,
                  alpha_power_positive=r, alpha_below_sqrt_p=1-r,
                  gamma_sublinear=1-e-r, cell_band_separation=e-(1-r)/2,
                  prime_interval_growth=1-e, delta_positive=delta,
                  delta_below_one_eighth=Q(1, 8)-delta,
                  K_smaller_than_ell=1-e-e*c, K_dominates_log_p=e*c,
                  kappa_positive=p['kappa'])
    assert all(value > 0 for value in slacks.values())
    margins = dict(g1=1-e*(1+c), g2=e*a*c, g3=e*(1-lamp),
                   g4=a*(1-e), g5=min(1-e-delta, r-delta), g6=1-delta-e, g7=e)
    assert all(value == Q(row['margins'][key]) for key, value in margins.items())
    minimum = min(margins.values())
    assert minimum == margins['g2'] == margins['g3'] == Q(row['minimum_margin'])
    assert 0 < p['kappa'] < minimum
    assert p['kappa'] == Q((minimum.numerator*10**30-1)//minimum.denominator, 10**30)
    assert p['kappa'] > Q(1, 2**57) and row['strictly_supports_2^-57']
    ua = Q(row['bit_saving_enclosure']['saving_upper'])
    ub = Q(row['complex_saving_enclosure']['saving_upper'])
    model_upper = Q(row['guard_family_model_upper'])
    assert 0 < model_upper < ub/4
    ux = model_upper/(ub-4*model_upper)
    assert 0 < ux < 1 and ua*ub*ux*ux-(ub+ua*ua)*ux+ua*ua < 0
    assert p['kappa'] < model_upper
    gamma_cutoff = ceiling(7/(1-e-r))
    k = ceiling(1/r)
    alpha_cutoff = 16*k*k+1
    guard_cutoff = ceiling(Q((2*ceiling(p['C0'])).bit_length())/(1-e*p['C1']))
    cell_cutoff = ceiling(9/(e-(1-r)/2))
    for name, value in [('gamma_log2_b_cutoff', gamma_cutoff),
                        ('logarithmic_alpha_log2_b_cutoff', alpha_cutoff),
                        ('full_guard_log2_b_cutoff', guard_cutoff),
                        ('full_phase_cell_log2_b_cutoff', cell_cutoff)]:
        assert row[name] == value
    assert row['common_log2_b_cutoff'] == max(gamma_cutoff, alpha_cutoff, guard_cutoff, cell_cutoff)
    assert gamma_cutoff*(1-e-r) >= 7
    assert guard_cutoff*(1-e*p['C1']) >= (2*ceiling(p['C0'])).bit_length()
    assert cell_cutoff*(e-(1-r)/2) >= 9
    # w<10*b^((1-r)/2)+3, while d-2>=b^epsilon-3.
    assert 2**9 > 40+15
    return dict(roles=roles, mode=row['mode'], kappa=str(p['kappa']),
                independent_strict_constraints=len(slacks),
                independent_log_enclosures=True, root_signs_and_floor_grid=True,
                complete_guard_constant_verified=True,
                gamma_alpha_guard_cell_cutoffs_verified=True,
                common_log2_b_cutoff=row['common_log2_b_cutoff'],
                strict_support_for_2_to_minus_57=True,
                scoped_guard_family_upper_verified=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    started = time.monotonic()
    raw = args.certificate.read_bytes()
    data = json.loads(raw)
    assert data['provenance']['commit'] == 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    result = dict(input_certificate_sha256=sha256(raw).hexdigest(),
                  code_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  rows=[audit(row) for row in data['witnesses']],
                  wall_seconds=time.monotonic()-started,
                  scope='Independent exact phase-family arithmetic; analytic inverse, fixed-tape costs and finite graphs separately required')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
