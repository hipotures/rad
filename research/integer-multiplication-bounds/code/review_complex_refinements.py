#!/usr/bin/env python3
"""Independent arithmetic for promoted bit roles and complex center refinements.

Retains the previously reviewed exact logarithm, recurrence and margin audit,
with explicit finite-role and central-channel inputs instead of one frozen
primitive. The original reviewer is untouched.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

from review_asymmetric_motif import independent_saving
from review_packed_unrolling import finite_counts


def ceiling(x):
    return -(-x.numerator//x.denominator)


def stopped_controls():
    # m=64, tau=1/2, sigma=1/3, beta=1/3, c=1/6.
    # The ratio 4/sqrt(64)=1/2 decays. d=64^(6k), K=64^k.
    checked = internal = small = 0
    wrong_growth = []
    for k in range(1, 11):
        threshold = 64**(2*k)
        for n in range(6*k+1):
            e = 64**n
            for branching in (3, 4):
                if e < threshold:
                    assert e <= 2**(20*k)
                    small += 1
                else:
                    depth = n-2*k+1
                    leaf = e//64**depth
                    assert threshold//64 <= leaf < threshold
                    direct = leaf
                    for j in reversed(range(depth)):
                        node = e//64**j
                        overhead = 2**(3*(k+n-j))
                        assert overhead*overhead == 64**k*node
                        direct = branching*direct+overhead+1
                    exact = branching**depth*leaf+sum(
                        branching**j*(2**(3*(k+n-j))+1) for j in range(depth))
                    assert direct == exact
                    main = sum(4**j*2**(3*(k+n-j)) for j in range(depth))
                    constant = sum(4**j for j in range(depth))
                    leaves = 4**depth*leaf
                    top = 2**(3*(k+n))
                    assert main == 2*top*(1-Q(1, 2**depth)) < 2*top
                    assert constant < top
                    assert leaves == 2**(2*n+8*k-4) <= Q(2**(20*k), 16)
                    assert direct < 3*2**(21*k)+Q(2**(20*k), 16)
                    internal += 1
                checked += 1
        # Applying the growing-ratio exponent would predict d^(17/36),
        # whereas the mandatory top node alone costs d^(7/12).
        ratio = Q(2**(21*k), 2**(17*k))
        assert ratio == 2**(4*k)
        wrong_growth.append(dict(k=k, top_over_wrong_power=str(ratio)))
    return dict(complete_stopped_recurrences=checked, internal=internal,
                individually_executed=small, fixed_branching_bounds=[3, 4],
                true_internal_exponent='7/12', leaf_exponent='5/9',
                wrong_growing_exponent='17/36', unbounded_wrong_branch_controls=wrong_growth)


def audit(row, expected_roles, central_channels):
    n = finite_counts(row['bit_counts'])
    assert row['bit_counts']['h'] == 50 and row['bit_counts']['side_roles'] == expected_roles
    assert central_channels in (50, 51)
    nc = row['complex_counts']
    h, v, m, R = 50, comb(50, 3), 125000, 629617
    N = v**3
    L = 3*v*v*central_channels*h
    multiplier = next(j for j in (2, 3) if 2*N+j*v*v*(R+central_channels) == nc['W'])
    W = 2*N+multiplier*v*v*(R+central_channels)
    D = 2*N-2*L
    s = W*m-D
    eta = Q(D, W*m)
    for key, value in dict(h=h, v=v, m=m, R=R, N=N, W=W, L=L, D=D, s=s, eta=eta).items():
        assert Q(nc[key]) == value
    assert 0 < D and 2 <= s < m**5
    assert 3*v*v*(4*R+4) < 6*W
    E = 64*(W+m+1)**3
    assert 12*W**3+4*s+4*W+4 < E
    for name, fraction, radix in [('bit', n['eta'], n['m']), ('complex', eta, m)]:
        lo, hi = independent_saving(fraction, radix)
        enclosure = row[name+'_saving_enclosure']
        assert Q(enclosure['saving_lower']) < lo < hi < Q(enclosure['saving_upper'])
        assert 0 < Q(enclosure['chosen_saving']) < lo
    p = {key: Q(value) for key, value in row['parameters'].items()}
    a, b = p['a_bit'], p['a_complex']
    tau, sigma = p['tau'], p['sigma']
    c, beta, lp, lam = (p[key] for key in ('c', 'beta', 'lambda_prime', 'lambda_'))
    eps, r, delta, zeta = (p[key] for key in ('epsilon', 'alpha_squared_power', 'delta', 'zeta'))
    assert tau == 1-a and sigma == 1-b and 0 < a < b < Q(1, 32)
    assert Q(row['bit_saving_enclosure']['saving_upper']) < Q(row['complex_saving_enclosure']['saving_lower'])
    backoff = Q(1, 2**64)
    q = 1-lp
    assert c == a and q == a*a*(1-backoff)
    assert 1-beta == (q/b)*(1+backoff)
    internal, leaf = tau*(1+c), sigma+beta*(1-sigma)
    assert Q(row['internal_exponent']) == internal
    assert Q(row['leaf_exponent']) == leaf
    assert lam == (lp+max(tau, sigma, internal))/2
    guard_backoff = Q(1, 2**20) if row['mode'] == 'conservative' else backoff
    assert row['mode'] in ('conservative', 'tight')
    assert zeta == (Q(1, 2**30) if row['mode'] == 'conservative' else backoff)
    assert p['C1'] == 5-4*beta+zeta
    assert eps == (1-guard_backoff)/max(p['C1'], 1+c+q)
    assert r == (1-eps)/2 and delta == r/8
    assert p['C0'] == 32*m*(s+E)**2*(1+1/zeta)
    assert Q(9, 10) <= beta < 1 and 0 < r <= Q(1, 3)
    margins = dict(g1=1-eps*(1+c), g2=eps*a*c, g3=eps*q,
                   g4=a*(1-eps), g5=min(1-eps-delta, r-delta),
                   g6=1-eps-delta, g7=eps)
    assert all(Q(row['margins'][key]) == value for key, value in margins.items())
    G = min(margins.values())
    assert G == margins['g3'] == Q(row['minimum_margin'])
    slacks = dict(tau=tau, sigma=sigma, decaying_order=tau-sigma,
                  c=c, beta=beta, beta_below_one=1-beta,
                  lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
                  true_internal=lam-internal, lambda_prime_above_lambda=lp-lam,
                  leaf=lp-leaf, lambda_prime_below_one=1-lp,
                  guard=1-eps*p['C1'], prefix=margins['g1'],
                  K_smaller_than_axis=1-eps-eps*c, K_dominates_log_p=eps*c,
                  local_inverse=1-eps-delta, boundary_inverse=r-delta,
                  gamma=1-eps-r, cell_separation=eps-(1-r)/2,
                  prime_and_line_growth=1-eps, alpha_power=r, alpha_below_sqrt_p=1-r,
                  delta=delta, delta_below_eighth=Q(1, 8)-delta,
                  movement_above_layer=margins['g2']-G,
                  prefix_above_layer=margins['g1']-G,
                  CRT_above_layer=margins['g4']-G,
                  kappa=p['kappa'], absorption=G-p['kappa'])
    assert all(value > 0 for value in slacks.values())
    assert p['kappa'] == Q((G.numerator*10**40-1)//G.denominator, 10**40)
    assert p['kappa'] > Q(row['old_accepted_phase_kappa']) == Q(9638040483941, 10**30)
    assert Q(row['strict_improvement_factor']) == p['kappa']/Q(row['old_accepted_phase_kappa'])
    au, bu = (Q(row[name+'_saving_enclosure']['saving_upper']) for name in ('bit', 'complex'))
    upper = min(au*au*bu/(bu+4*au*au), au*au/(1+au+au*au))
    assert Q(row['scoped_model_upper']) == upper > p['kappa']
    wrong = sigma+beta*(tau-sigma)+tau*c
    assert internal-wrong == (b-a)*(1-beta) > 0
    control = row['wrong_growing_branch_control']
    assert Q(control['invalid_internal_exponent']) == wrong
    assert Q(control['true_top_internal_exponent']) == internal
    assert Q(control['strict_underestimate']) == internal-wrong
    k = ceiling(1/r)
    cutoffs = dict(gamma=ceiling(7/(1-eps-r)), logarithmic_alpha=16*k*k+1,
                   full_guard=ceiling(Q((2*ceiling(p['C0'])).bit_length())/(1-eps*p['C1'])),
                   phase_cell=ceiling(9/(eps-(1-r)/2)))
    cutoffs['common'] = max(cutoffs.values())
    assert row['cutoff_log2_b'] == cutoffs
    assert any('absorption' in text for text in row['additional_eventual_cutoffs'])
    active = 'prefix' if 1+a+a*a >= 1+4*a*a/b else 'guard'
    return dict(mode=row['mode'], shared=multiplier == 2, kappa=str(p['kappa']),
                independent_strict_conditions=len(slacks), independent_log_enclosures=True,
                wrong_branch_falsified=True, exact_new_complex_counts_and_guard=True,
                active_limiting_family=active, cutoffs=cutoffs,
                recurrence_absorption_additional_threshold_explicit=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--bit-roles', type=int, required=True)
    ap.add_argument('--central-channels', type=int, choices=[50, 51], default=51)
    ap.add_argument('--promotion', type=Path)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    started = time.monotonic()
    raw = args.certificate.read_bytes()
    data = json.loads(raw)
    assert data['provenance']['commit'] == 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    promotion = None
    if args.promotion:
        promotion = json.loads(args.promotion.read_text())
        assert promotion['status'] == 'PASS' and promotion['full']['roles'] == args.bit_roles
        digest = sha256(args.promotion.read_bytes()).hexdigest()
        assert digest in [entry['sha256'] for entry in data['input_files'].values()]
        assert data['promoted_finite_audit']['roles'] == args.bit_roles
        assert data['promoted_finite_audit']['compiled_sha256'] == promotion['full']['compiled_sha256']
        assert data['promoted_finite_audit']['independently_counted_roles'] == args.bit_roles
    result = dict(input_sha256=sha256(raw).hexdigest(),
                  expected_bit_roles=args.bit_roles, central_channels=args.central_channels,
                  promotion_input_sha256=sha256(args.promotion.read_bytes()).hexdigest() if args.promotion else None,
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  stopped_recurrences=stopped_controls(),
                  rows=[audit(row, args.bit_roles, args.central_channels) for row in
                        (data['witnesses'] if 'witnesses' in data else data['compositions'])],
                  wall_seconds=time.monotonic()-started,
                  scope='Independent complete counts, exact log/parameter/cutoff arithmetic and decaying recurrence controls; finite binary and all-size phase transfer in companion report')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS', result['stopped_recurrences']['complete_stopped_recurrences'],
          'complete decaying recurrences and', len(result['rows']), 'exact composition rows')


if __name__ == '__main__':
    main()
