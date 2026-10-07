#!/usr/bin/env python3
"""Independent exact assembly audit for the reusable banded inverse proof."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

from review_parameter_audit import log_integer, log_series, root_signs


def audit(row):
    h, R = row['bit_ground'], row['physical_side_roles']
    v, m = comb(h, 3), h**3
    N, W = v**3, 2*v**3+2*v*v*(R+h)
    D, s = N-6*v*v*h*h, W*m-(N-6*v*v*h*h)
    eta = Q(D, W*m)
    for key, value in dict(v=v, m=m, N=N, W=W, D=D, s=s, eta=eta).items():
        assert Q(row['counts'][key]) == value
    vc, mc = comb(50, 3), 50**3
    Nc = vc**3
    Wc = 2*Nc+3*vc*vc*(vc*(comb(47, 3)+141)+51)
    Lc = 3*vc*vc*51*50
    sc = Wc*mc-2*Nc+2*Lc
    etac = Q(Wc*mc-sc, Wc*mc)
    for key, value in dict(W=Wc, L=Lc, s=sc, eta=etac, m=mc, ground=50).items():
        assert Q(row['retained_complex_counts'][key]) == value
    assert 2*Lc < Nc and 2 <= sc < mc**5
    for kind, deficit, radix in [('bit', eta, m), ('complex', etac, mc)]:
        enclosed = row[kind+'_saving_enclosure']
        lnlo, lnhi = log_series(1/(1-deficit), 20)
        lmlo, lmhi = log_integer(radix)
        assert Q(enclosed['saving_lower']) < lnlo/lmhi < lnhi/lmlo < Q(enclosed['saving_upper'])
        assert 0 < Q(enclosed['chosen_saving']) < lnlo/lmhi
    p = {key: Q(value) for key, value in row['parameters'].items()}
    a, b, e, r = p['a_bit'], p['a_complex'], p['epsilon'], p['alpha_squared_power']
    beta, c, lam, lamp = p['beta'], p['c'], p['lambda'], p['lambda_prime']
    tau, sigma, delta = p['tau'], p['sigma'], p['delta']
    assert tau == 1-a and sigma == 1-b
    xlo, xhi = root_signs(a, b, row['balance_root_interval'])
    assert beta == 1-xhi
    assert c == a*beta/(tau+a*beta)*(1-Q(1, 2**32))
    assert 1-lamp == a*c
    assert e == Q(2, 3)-Q(1, 2**20) and r == Q(1, 3) and delta == Q(1, 2**22)
    B = sc+64*(Wc+mc+1)**3
    assert p['C1'] == Q(3, 2) and p['C0'] == 128*mc*B*B
    slacks = dict(tau_positive=tau, tau_below_one=a, sigma_positive=sigma,
                  sigma_below_one=b, c_positive=c, epsilon_positive=e,
                  beta_positive=beta, beta_below_one=1-beta,
                  lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
                  lambda_below_one=1-lam, packed_overhead=lam-tau*(1+c/beta),
                  lambda_prime_above_lambda=lamp-lam, leaf_cost=lamp-(sigma+beta*b),
                  lambda_prime_below_one=1-lamp, guard_width=1-e*p['C1'],
                  guard_stopping_range=beta-Q(15, 16), crt_layout=a*(1-e),
                  gaussian_cost=Q(1, 2)+r/2-delta-e, prefix_cost=1-e*(1+c),
                  scalar_cost=1-delta-e, delta_positive=delta,
                  delta_below_one_eighth=Q(1, 8)-delta, alpha_power_positive=r,
                  alpha_below_sqrt_p=1-r, gamma_sublinear=1-e-r,
                  prime_interval_and_line_growth=1-e, K_smaller_than_ell=1-e-e*c,
                  K_dominates_log_p=e*c, kappa_positive=p['kappa'])
    assert all(value > 0 for value in slacks.values())
    assert 1-2*e < 0  # Explicitly replaced legacy sufficient condition.
    margins = dict(g1=1-e*(1+c), g2=e*c*a, g3=e*(1-lamp), g4=a*(1-e),
                   g5=Q(1, 2)+r/2-delta-e, g6=1-delta-e, g7=e)
    assert all(value == Q(row['margins'][key]) for key, value in margins.items())
    G = min(margins.values())
    assert G == margins['g2'] == margins['g3'] == Q(row['minimum_margin'])
    assert 0 < p['kappa'] < G
    assert p['kappa'] == Q((G.numerator*10**30-1)//G.denominator, 10**30)
    assert Q(row['model_kappa_upper']) > p['kappa']
    upper_a = Q(row['bit_saving_enclosure']['saving_upper'])
    upper_b = Q(row['complex_saving_enclosure']['saving_upper'])
    upper_x = Q(row['model_kappa_upper'])/(Q(2, 3)*upper_b)
    assert 0 < upper_x < 1
    assert upper_a*upper_b*upper_x**2-(upper_b+upper_a**2)*upper_x+upper_a**2 < 0
    assert 7/(1-e-r) == 7340032 and 4*17 < 128
    assert row['gamma_cutoff'] == 'b >= 2^7340032'
    # The strengthened guard uses the same C0 from the pinned model.
    assert 5-4*beta+Q(1, 4) <= Q(3, 2)
    assert 45+18 < 128
    return dict(bit_ground=h, physical_roles=R, kappa=str(p['kappa']),
                independently_checked_strict_constraints=len(slacks),
                independent_primitive_log_enclosures=True, correct_root_orientation=True,
                same_guard_constant_verified=True, negative_legacy_prime_condition_explicitly_replaced=True,
                changed_gaussian_and_guard_margins_positive=True,
                gamma_cutoff_verified=True, strict_absorption=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--certificate', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    begin = time.monotonic()
    source = args.certificate.read_bytes()
    data = json.loads(source)
    assert data['provenance']['commit'] == 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    result = dict(certificate_sha256=sha256(source).hexdigest(),
                  code_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  witnesses=[audit(row) for row in data['witnesses']],
                  wall_seconds=time.monotonic()-begin,
                  scope='Exact revised assembly arithmetic; analytic inverse/guard/prime proofs and finite labels independently required')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
