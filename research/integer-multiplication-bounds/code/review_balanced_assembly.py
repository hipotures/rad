#!/usr/bin/env python3
"""Independent exact balanced-layout counts, logarithms, margins and cutoffs.

Imports only previously independent reviewer routines. The actual Fourier
operator controls and the all-size tape/layout proof remain distinct inputs.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import subprocess
import time

from review_compact_generic import PIN, ceil_q, finite_counts, independent_saving


def audit_row(row, previous_kappa):
    n = finite_counts(row['bit_counts'])
    h, R = int(row['complex_counts']['h']), int(row['complex_counts']['R'])
    assert h >= 8 and h % 2 == 0 and R > 0
    v, m = comb(h, 3), h**3
    N = v**3
    W = 2*N+2*v*v*(R+h+1)
    L = 3*v*v*h*(h+1)
    D = 2*N-2*L
    s = W*m-D
    nc = dict(h=h, R=R, v=v, m=m, N=N, W=W, L=L, D=D,
              s=s, eta=Q(D, W*m))
    assert all(Q(row['complex_counts'][k]) == value for k, value in nc.items())
    actual_logs = {}
    for name, counts in (('bit', n), ('complex', nc)):
        lo, hi = independent_saving(counts['eta'], counts['m'])
        saved = row[name+'_saving_enclosure']
        assert Q(saved['saving_lower']) < lo < hi < Q(saved['saving_upper'])
        assert 0 < Q(saved['chosen_saving']) < lo
        actual_logs[name] = [str(lo), str(hi)]
    p = {k:Q(value) for k, value in row['parameters'].items()}
    a, b = p['a_bit'], p['a_complex']
    assert a == Q(row['bit_saving_enclosure']['chosen_saving'])
    assert b == Q(row['complex_saving_enclosure']['chosen_saving'])
    assert 0 < a < b < Q(1, 32) and b > 4*a
    assert row['mode'] in ('conservative', 'tight')
    backoff = a/16 if row['mode'] == 'conservative' else Q(1, 2**64)
    c = 1-backoff
    q = a*(1-2*backoff)
    x = (q/b)*(1+backoff)
    beta = 1-x
    tau, sigma = 1-a, 1-b
    lp, lam = 1-q, (tau+1-q)/2
    eps = (1-backoff)/(1+c)
    r, delta = (1-eps)/2, (1-eps)/16
    C1 = 1+4*x+backoff
    E = 64*(W+m+1)**3
    B = s+E
    C0 = 32*m*B*B*(1+1/backoff)
    recipe = dict(a_bit=a, a_complex=b, tau=tau, sigma=sigma, c=c,
        beta=beta, lambda_=lam, lambda_prime=lp, epsilon=eps,
        alpha_squared_power=r, delta=delta, zeta=backoff, C1=C1, C0=C0)
    assert all(p[k] == value for k, value in recipe.items())
    internal = tau+(1-beta)*max(sigma-tau, Q(0))
    leaf = sigma+beta*(1-sigma)
    reserve = max(1-c, Q(0))
    assert internal == tau
    assert all(Q(row['recurrence'][k]) == value for k, value in
               dict(internal=internal, leaf=leaf, reservations=reserve).items())
    assert s*(8+E) <= 9*B*B and 2 <= s < m**5
    assert 3*v*v*(4*R+4) < 6*W
    assert 12*W**3+4*s+4*W+4 < E
    assert 9*m*B*B*(1+1/backoff)+18 < C0
    margins = dict(g1=1-eps, g2=eps*a*c, g3=eps*q, g4=a*(1-eps),
        g5=min(1-eps-delta, r-delta), g6=1-eps-delta, g7=eps)
    assert all(Q(row['margins'][k]) == value for k, value in margins.items())
    G = min(margins.values())
    assert G == Q(row['minimum_margin']) == margins['g3']
    kappa = Q((G.numerator*10**40-1)//G.denominator, 10**40)
    assert kappa == p['kappa'] and kappa > previous_kappa
    geometry = 1-eps*(1+c)
    assert geometry == backoff == Q(row['old_prefix_margin'])
    slacks = dict(
        bit_primitive=Q(row['bit_saving_enclosure']['negative_log_deficit_lower'])
            -a*Q(row['bit_saving_enclosure']['log_m_upper']),
        complex_primitive=Q(row['complex_saving_enclosure']['negative_log_deficit_lower'])
            -b*Q(row['complex_saving_enclosure']['log_m_upper']),
        primitive_order=b-a, guard_headroom=b-4*a, c_positive=c,
        c_below_one=1-c, beta_positive=beta, beta_below_one=1-beta,
        epsilon_positive=eps, epsilon_below_one=1-eps,
        lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
        compact_internal=lam-internal, lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf, compact_reservations=lp-reserve,
        guard=1-eps*C1, K_smaller_than_ell=geometry,
        K_dominates_log_p=eps*c, record_suffix_superpolynomial=1-eps,
        phase_local_cost=1-eps-delta, phase_boundary_cost=r-delta,
        gamma_sublinear=1-eps-r, cell_larger_than_band=eps-(1-r)/2,
        prime_interval_packing=1-eps, alpha_power=r, delta_positive=delta,
        delta_below_one_eighth=Q(1, 8)-delta,
        prefix_vs_layer=margins['g1']-G, movement_vs_layer=margins['g2']-G,
        crt_vs_layer=margins['g4']-G, gaussian_vs_layer=margins['g5']-G,
        scalar_vs_layer=margins['g6']-G, dimension_vs_layer=margins['g7']-G,
        absorption=G-kappa, improvement_over_previous_compact=kappa-previous_kappa,
        old_prefix_proof_fails=kappa-geometry)
    assert set(slacks) == set(row['constraint_slacks'])
    assert all(value > 0 for value in slacks.values())
    assert all(Q(row['constraint_slacks'][k]) == value for k, value in slacks.items())
    assert Q(row['previous_compact_kappa']) == previous_kappa
    assert Q(row['strict_gain']) == kappa-previous_kappa
    assert Q(row['strict_improvement_ratio']) == kappa/previous_kappa
    upper = Q(row['bit_saving_enclosure']['saving_upper'])/2
    assert Q(row['scoped_model_upper']) == upper > kappa
    assert Q(row['achieved_fraction_of_scoped_upper']) == kappa/upper
    ka, km = ceil_q(1/r), ceil_q(1/(eps*c))
    cutoff_compact = 64*km*km+1
    assert cutoff_compact >= 2*km
    real_log_slack = 2**(cutoff_compact//km)-32*cutoff_compact-192
    assert real_log_slack > 0
    saved_real = row['strengthened_real_log_compact_cutoff']
    assert saved_real['L0'] == cutoff_compact and saved_real['k'] == km
    assert saved_real['exact_integer_slack'] == real_log_slack
    assert saved_real['denominator_constant'] == 192
    assert saved_real['denominator_slope'] == 32
    cuts = dict(gamma=ceil_q(7/(1-eps-r)),
        logarithmic_alpha=16*ka*ka+1,
        full_guard=ceil_q(Q((2*ceil_q(C0)).bit_length())/(1-eps*C1)),
        phase_cell=ceil_q(9/(eps-(1-r)/2)),
        compact_controls=cutoff_compact,
        balanced_geometry=ceil_q(3/geometry))
    cuts['common'] = max(cuts.values())
    assert row['cutoff_log2_b'] == cuts
    assert cuts['balanced_geometry']*geometry >= 3
    assert cuts['gamma']*(1-eps-r) >= 7
    assert cuts['phase_cell']*(eps-(1-r)/2) >= 9
    assert cuts['full_guard']*(1-eps*C1) >= (2*ceil_q(C0)).bit_length()
    assert ka*r >= 1
    return dict(mode=row['mode'], kappa=str(kappa),
        minimum_margin=str(G), bit_roles=int(row['bit_counts']['side_roles']),
        complex_ground=h, complex_roles=R,
        independent_logarithm_enclosures=actual_logs,
        exact_strict_slacks_checked=len(slacks), cutoffs=cuts,
        changed_layout_required_since_old_prefix_margin_below_kappa=True,
        scoped_upper=str(upper), strict_gain=str(kappa-previous_kappa))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for flag in ('certificate', 'previous', 'previous-review', 'layout',
                 'operator-review', 'reference', 'output'):
        ap.add_argument('--'+flag, type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    started = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat()
    paths = {flag:getattr(args, flag.replace('-', '_')) for flag in
        ('certificate', 'previous', 'previous-review', 'layout', 'operator-review')}
    packets = {flag:json.loads(path.read_text()) for flag, path in paths.items()}
    data, previous, reviewed, layout, operators = (packets[k] for k in paths)
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=args.reference,
                                   text=True).strip() == PIN
    assert data['compact_reference']['commit'] == PIN
    assert data['original_reference']['commit'] == 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    assert reviewed['status'].startswith('PASS independent generic compact')
    assert reviewed['input_sha256'] == sha256(args.previous.read_bytes()).hexdigest()
    assert reviewed['source_sha256'] == sha256(Path(__file__).with_name('review_compact_generic.py').read_bytes()).hexdigest()
    for path in (args.previous, args.layout):
        digest = sha256(path.read_bytes()).hexdigest()
        assert any(item['sha256'] == digest for item in data['input_files'].values())
    assert data['promoted_bit_audit'] == previous['promoted_bit_audit']
    assert data['promoted_complex_audit'] == previous['promoted_complex_audit']
    assert reviewed['promoted_metadata']['bit_roles'] == data['promoted_bit_audit']['roles']
    assert reviewed['promoted_metadata']['complex_ground'] == int(previous['witnesses'][0]['complex_counts']['h'])
    for name, digest in data['source_sha256'].items():
        assert sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() == digest
    for name, digest in layout['source_sha256'].items():
        assert data['source_sha256'][name] == digest
    assert layout['cases'] == 3800
    assert layout['exact_axis_round_chronology_checks'] == 2068936
    assert layout['one_bit_unequal_width_moves'] == 1718
    assert operators['status'].startswith('PASS exact independent balanced')
    assert operators['source_sha256'] == sha256(Path(__file__).with_name('review_balanced_transform.py').read_bytes()).hexdigest()
    assert operators['shape_count'] == 38 and operators['input_basis_columns'] == 454
    assert operators['exact_forward_matrix_entries'] == 114180
    assert all(row['normalized_opposite_composite_exact'] for row in operators['cases'])
    previous_tight = next(row for row in reviewed['rows'] if row['mode'] == 'tight')
    old_kappa = Q(previous_tight['kappa'])
    assert old_kappa == Q(next(row for row in previous['witnesses'] if row['mode'] == 'tight')['parameters']['kappa'])
    rows = [audit_row(row, old_kappa) for row in data['witnesses']]
    assert {row['mode'] for row in rows} == {'conservative', 'tight'}
    result = dict(status='PASS independent balanced-layout exact arithmetic',
        started_utc=started_utc, completed_utc=datetime.now(timezone.utc).isoformat(),
        input_files={flag:dict(sha256=sha256(path.read_bytes()).hexdigest(),
                              bytes=path.stat().st_size) for flag, path in paths.items()},
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        reviewer_dependency_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
          for name in ('review_compact_generic.py', 'review_asymmetric_motif.py', 'review_packed_unrolling.py')},
        reference_revision=PIN, promoted_metadata=reviewed['promoted_metadata'],
        actual_operator_controls=dict(shapes=38, basis_columns=454, polynomial_entries=114180),
        rows=rows, wall_seconds=time.monotonic()-started,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Independent counts and longer rational logarithms, all 37 saved strict slacks, changed prefix cost, guard and six cutoffs. Previous finite promotion and the explicit all-size balanced/compact/phase proofs remain dependencies. No formal fixed-tape multiplication-machine verification.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    for row in rows:
        print('PASS balanced', row['mode'], 'kappa', row['kappa'],
              'strict conditions', row['exact_strict_slacks_checked'],
              'cutoff', row['cutoffs']['common'])


if __name__ == '__main__':
    main()
