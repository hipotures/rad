#!/usr/bin/env python3
"""Exact fixed-network s<m^nu guard refinement and scoped active-margin check.

This computes a changed guard estimate only. It does not change an accepted
parameter witness or claim that an inactive guard improves kappa.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import resource
import time

from review_compact_generic import ceil_q
from review_parameter_audit import log_integer


def recursive_controls():
    checked = 0
    examples = []
    for m, s, nu in ((4, 3, Q(1)), (4, 7, Q(3, 2)),
                     (4, 13, Q(2)), (8, 31, Q(2)),
                     (8, 127, Q(5, 2))):
        assert s**nu.denominator < m**nu.numerator
        E, beta = 17, Q(1, 3)
        for k in range(1, 9):
            d, threshold = m**(6*k), m**(2*k)
            exponent = (beta+nu*(1-beta))*6*k
            assert exponent.denominator == 1
            bound = s*(8+E)*m**exponent.numerator
            for j in range(6*k+1):
                e = m**j
                if e < threshold:
                    actual = 8*e
                    depth = 0
                else:
                    depth = j-2*k+1
                    leaf = e//m**depth
                    assert threshold//m <= leaf < threshold
                    actual = 8*leaf
                    for _ in range(depth):
                        actual = s*actual+E
                    independent = 8*leaf*s**depth+E*sum(s**a for a in range(depth))
                    assert actual == independent
                assert actual <= bound
                checked += 1
                if j == 6*k and k == 8:
                    examples.append(dict(m=m, s=s, nu=str(nu), depth=depth,
                        exact_coefficient_depth=str(actual), one_piece_bound=str(bound)))
    return dict(actual_stopped_coefficient_recurrences=checked, beta='1/3',
                s_power_cases=['1', '3/2', '2', '5/2'], examples=examples)


def audit_row(row):
    nc = {key:Q(value) for key, value in row['complex_counts'].items()}
    m, s, W = (int(nc[key]) for key in ('m', 's', 'W'))
    sl, su = log_integer(s, 64)
    ml, mu = log_integer(m, 64)
    lower, upper = sl/mu, su/ml
    assert 1 < lower < upper < 5
    nu = Q(ceil_q(1000*upper), 1000)
    assert nu > upper
    assert s**nu.denominator < m**nu.numerator
    assert s < m**4
    p = {key:Q(value) for key, value in row['parameters'].items()}
    beta, eps, zeta = p['beta'], p['epsilon'], p['zeta']
    x = 1-beta
    old_C1 = 1+4*x+zeta
    integer_C1 = 1+3*x+zeta
    sharper_C1 = 1+(nu-1)*x+zeta
    assert p['C1'] == old_C1
    assert 1 < sharper_C1 < integer_C1 < old_C1
    E = 64*(W+m+1)**3
    B = s+E
    C0 = 32*m*B*B*(1+1/zeta)
    assert p['C0'] == C0
    bits = (2*ceil_q(C0)).bit_length()
    old_cut = ceil_q(Q(bits)/(1-eps*old_C1))
    integer_cut = ceil_q(Q(bits)/(1-eps*integer_C1))
    sharper_cut = ceil_q(Q(bits)/(1-eps*sharper_C1))
    assert old_cut == row['cutoff_log2_b']['full_guard']
    assert 0 < sharper_cut <= integer_cut < old_cut
    old_cuts = row['cutoff_log2_b']
    new_common = max(value for key, value in old_cuts.items()
                     if key not in ('common', 'full_guard'))
    new_common = max(new_common, sharper_cut)
    a, b = p['a_bit'], p['a_complex']
    assert b > 4*a > (nu-1)*a
    assert eps*old_C1 < 1 and 1-eps*old_C1 > p['kappa']
    return dict(mode=row['mode'], h=int(nc['h']), m=m, s=s,
        actual_log_m_s_interval=[str(lower), str(upper)],
        strict_rational_nu=str(nu), exact_s_power_below_m_power=True,
        simpler_integer_nu='4', C1_old=str(old_C1),
        C1_integer_nu=str(integer_C1), C1_sharper=str(sharper_C1),
        guard_cutoffs=dict(old=old_cut, integer_nu=integer_cut, sharper=sharper_cut),
        old_common=old_cuts['common'], sharper_common=new_common,
        original_witness_kappa=str(p['kappa']),
        kappa_unchanged_since_guard_inactive=True,
        balanced_guard_headroom_threshold=str((nu-1)*a))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificates', type=Path, nargs='+', required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    started = time.monotonic()
    rows = []
    for path in args.certificates:
        data = json.loads(path.read_text())
        rows.append(dict(input_sha256=sha256(path.read_bytes()).hexdigest(),
                         witnesses=[audit_row(row) for row in data['witnesses']]))
    controls = recursive_controls()
    result = dict(status='PASS exact actual-network stopped guard refinement',
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        dependency_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                           for name in ('review_compact_generic.py', 'review_parameter_audit.py')},
        one_piece_exponent='beta+nu*(1-beta)',
        layer_exponent='1+(nu-1)*(1-beta)+zeta',
        controls=controls, inputs=rows, wall_seconds=time.monotonic()-started,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Sharper guard/cutoff with unchanged fixed finite network and constants. It is inactive for current exponent witnesses; no kappa promotion or universal network claim.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS', controls['actual_stopped_coefficient_recurrences'],
          'actual coefficient-depth controls; witness guards',
          [(row['mode'],row['strict_rational_nu'],row['guard_cutoffs'])
           for packet in rows for row in packet['witnesses']])


if __name__ == '__main__':
    main()
