#!/usr/bin/env python3
"""Independent unequal-motif phase parameter and grid-ranking audit."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from review_asymmetric_motif import counts, independent_saving
from review_parameter_audit import root_signs


def ceiling(x):
    return -(-x.numerator//x.denominator)


def audit(row):
    raw = row['counts']
    n = counts(raw['p'], raw['q'], raw['outer_side_roles'], raw['middle_side_roles'])
    assert all(Q(raw[key]) == value for key, value in n.items())
    assert 0 < n['D'] and 2 <= n['s'] < n['m']**5
    complex_ = row['retained_complex_counts']
    assert complex_['ground'] == 50 and complex_['m'] == 125000
    assert Q(complex_['eta']) == Q(complex_['W']*complex_['m']-complex_['s'],
                                   complex_['W']*complex_['m'])
    # These complex counts were independently derived in the frozen phase
    # and asymmetric reviews; verify their exact retained interface here.
    assert complex_['W'] == 369474390296480000
    assert complex_['s'] == 46184298777878576000000
    for name, eta, m in [('bit', n['eta'], n['m']),
                         ('complex', Q(complex_['eta']), complex_['m'])]:
        lo, hi = independent_saving(eta, m)
        enclosure = row[name+'_saving_enclosure']
        assert Q(enclosure['saving_lower']) < lo < hi < Q(enclosure['saving_upper'])
        assert 0 < Q(enclosure['chosen_saving']) < lo
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
    assert lamp == 1-a*c and lam == (lamp+threshold)/2
    B = complex_['s']+64*(complex_['W']+complex_['m']+1)**3
    if row['mode'] == 'conservative':
        assert (e, r, delta, zeta) == (Q(9, 10), Q(1, 20), Q(1, 1000), Q(1, 20))
        assert p['C1'] == Q(11, 10) and p['C0'] == 256*125000*B*B
        assert beta >= Q(999, 1000) and 9*21+18 < 256
    else:
        assert row['mode'] == 'optimized' and zeta == Q(1, 2**30)
        assert p['C1'] == 5-4*beta+zeta and e == (1-Q(1, 2**20))/p['C1']
        assert r == (1-e)/2 and delta == r/8
        assert p['C0'] == 32*125000*B*B*(1+1/zeta)
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
    margins = dict(g1=1-e*(1+c), g2=e*a*c, g3=e*(1-lamp), g4=a*(1-e),
                   g5=min(1-e-delta, r-delta), g6=1-delta-e, g7=e)
    assert all(Q(row['margins'][key]) == value for key, value in margins.items())
    minimum = min(margins.values())
    assert minimum == margins['g2'] == margins['g3'] == Q(row['minimum_margin'])
    assert 0 < p['kappa'] < minimum
    assert p['kappa'] == Q((minimum.numerator*10**30-1)//minimum.denominator, 10**30)
    assert p['kappa'] > Q(1, 2**57)
    assert row['strict_simple_11_over_2_to_60'] == (p['kappa'] > Q(11, 2**60))
    if row['mode'] == 'optimized':
        assert p['kappa'] > Q(11, 2**60)
    ua, ub = (Q(row[k+'_saving_enclosure']['saving_upper']) for k in ('bit', 'complex'))
    upper = Q(row['guard_family_model_upper'])
    ux = upper/(ub-4*upper)
    assert 0 < ux < 1 and ua*ub*ux*ux-(ub+ua*ua)*ux+ua*ua < 0
    assert p['kappa'] < upper
    k = ceiling(1/r)
    cutoffs = dict(gamma=ceiling(7/(1-e-r)), logarithmic_alpha=16*k*k+1,
                   full_guard=ceiling(Q((2*ceiling(p['C0'])).bit_length())/(1-e*p['C1'])),
                   phase_cell=ceiling(9/(e-(1-r)/2)))
    cutoffs['common'] = max(cutoffs.values())
    assert row['cutoff_log2_b'] == cutoffs
    return dict(p=n['p'], q=n['q'], mode=row['mode'], kappa=str(p['kappa']),
                independent_strict_conditions=len(slacks), independent_primitive_enclosures=True,
                strict_root_absorption_and_guard_verified=True,
                independently_recomputed_cutoffs=cutoffs)


def ranking(certificate):
    roles = {int(h): int(r) for h, r in certificate['verified_role_counts'].items()}
    best = certificate['best']
    selected = (best['counts']['p'], best['counts']['q'])
    kappa = Q(best['parameters']['kappa'])
    complex_ = best['retained_complex_counts']
    b = independent_saving(Q(complex_['eta']), complex_['m'])[1]
    upper_max, nearest = Q(0), None
    comparisons = 0
    for row in certificate['ranking']:
        p, q = row['p'], row['q']
        n = counts(p, q, roles[p], roles[q])
        if (p, q) == selected:
            continue
        a = independent_saving(n['eta'], n['m'])[1]
        # At the original balance root, bx=a²(1-x)/(1-ax).
        # Since 1-ax>=1-a, x<=a²/[b(1-a)+a²].
        # This conservative ceiling neglects the chosen positive guard,
        # recurrence and grid slacks, so it bounds every original-family
        # choice at these primitive upper enclosures.
        xupper = a*a/(b*(1-a)+a*a)
        ceiling_ = b*xupper/(1+4*xupper)
        assert ceiling_ < kappa, (p, q)
        comparisons += 1
        if ceiling_ > upper_max:
            upper_max, nearest = ceiling_, (p, q)
    assert comparisons+1 == len(roles)**2 == len(certificate['ranking'])
    ratio = kappa/upper_max-1
    ratio_lower = Q((ratio.numerator*10**12-1)//ratio.denominator, 10**12)
    assert 0 < ratio_lower < ratio
    return dict(independently_bounded_other_candidates=comparisons,
                selected_beats_every_other_guard_family_ceiling=True,
                closest_competitor=list(nearest),
                selected_over_closest_upper_minus_one_strict_lower=str(ratio_lower),
                method='Longer independent logarithm enclosures and conservative analytic balance-root upper; does not rely on producer sorting')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    start = time.monotonic()
    raw = args.certificate.read_bytes()
    data = json.loads(raw)
    assert data['provenance']['commit'] == 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    regressions = data['uniform_phase_regressions']
    assert len(regressions) == 8 and all(row['passed'] for row in regressions)
    result = dict(input_certificate_sha256=sha256(raw).hexdigest(),
                  code_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  best=audit(data['best']), conservative_selected=audit(data['conservative_selected']),
                  ranking=ranking(data), uniform_regressions_reported=8,
                  wall_seconds=time.monotonic()-start,
                  scope='Independent unequal counts, phase strict parameters/cutoffs and original guard-family finite-grid dominance; finite graphs and all-size analytic interfaces separately reviewed')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
