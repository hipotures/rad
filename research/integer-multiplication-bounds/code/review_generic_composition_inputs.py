#!/usr/bin/env python3
"""Independent controls and arithmetic for a common rational kernel basis.

The giant fixed basis is covered by the written finite-grid proof. This
review implements separate exact matrix arithmetic and an actual small
data-complement family, and never imports the generic-basis producer.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path
import random
import resource
import time


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def tr(a):
    return [list(x) for x in zip(*a)]


def mm(a, b):
    return [[sum((x*y for x, y in zip(row, col)), F(0))
             for col in zip(*b)] for row in a]


def elimination(a):
    b = [list(map(F, row)) for row in a]
    pivot_columns = []
    row = 0
    for col in range(len(b[0])):
        candidate = next((i for i in range(row, len(b)) if b[i][col]), None)
        if candidate is None:
            continue
        b[row], b[candidate] = b[candidate], b[row]
        scale = b[row][col]
        b[row] = [x/scale for x in b[row]]
        for i in range(len(b)):
            if i != row and b[i][col]:
                scale = b[i][col]
                b[i] = [x-scale*y for x, y in zip(b[i], b[row])]
        pivot_columns.append(col)
        row += 1
        if row == len(b):
            break
    return b, pivot_columns


def rank(a):
    return len(elimination(a)[1])


def inverse(a):
    n = len(a)
    b, pivots = elimination([row+e for row, e in zip(a, eye(n))])
    require(pivots[:n] == list(range(n)), 'Singular exact square matrix')
    return [row[n:] for row in b]


def dual(g, u):
    gu = mm(g, u)
    return mm(inverse(mm(tr(u), gu)), tr(gu))


def flags(u, v):
    n, d = len(u), len(v)
    return [rank(u[:d]), rank([row[n-d:] for row in v])]


def canonical_profile(a):
    """Row-only rightmost elimination; no imported profile implementation."""
    b = [list(map(F, row)) for row in a]
    out = []
    for i in range(len(b)):
        j = next((j for j in reversed(range(len(b[0]))) if b[i][j]), None)
        if j is None:
            continue
        out.append((i, j))
        scale = b[i][j]
        b[i] = [x/scale for x in b[i]]
        for k in range(i+1, len(b)):
            scale = b[k][j]
            if scale:
                b[k] = [x-scale*y for x, y in zip(b[k], b[i])]
    return out


def projector_profile(u, v):
    n, d = len(u), len(v)
    require(mm(v, u) == eye(d), 'Missing exact projector relation')
    require(2*d < n and flags(u, v) == [d, d], 'Complement flags absent')
    p = mm(u, v)
    a = [[F(i == j)-p[i][j] for j in range(n)] for i in range(n)]
    profile = canonical_profile(a)
    require(len(profile) == n-d, 'Full complementary rank differs')
    require([i for i, _ in profile[:d]] == list(range(d)) and
            {j for _, j in profile[:d]} == set(range(n-d, n)),
            'Top pivots do not fill the entire last block')
    require(profile[d:] == [(i, i) for i in range(d, n-d)],
            'Schur interior is not one complete diagonal run')
    return dict(kernel_dimension=d, rank=len(profile),
                individual_top_pivots=profile[:d], diagonal_run=[d, n-2*d],
                profile_sha256=sha256(json.dumps(profile).encode()).hexdigest())


def reflected_family(g, originals, seed):
    """Reject directions by exact changed ranks, separately from the proof.

    The proof's nonzero-polynomial tensor grid guarantees existence. These
    bounded small controls use reproducible trial directions and check the
    claimed rank increases directly, rather than reusing its null factors.
    """
    rng = random.Random(seed)
    n = len(g)
    pairs = [(u, dual(g, u)) for u in originals]
    initial = [flags(u, v) for u, v in pairs]
    transform = eye(n)
    records = []
    while any(any(k < len(v) for k in flags(u, v)) for u, v in pairs):
        old = [flags(u, v) for u, v in pairs]
        for attempt in range(1, 513):
            w = [F(rng.randint(-4, 4)) for _ in range(n)]
            wg = [sum((w[i]*g[i][j] for i in range(n)), F(0)) for j in range(n)]
            norm = sum((x*y for x, y in zip(w, wg)), F(0))
            if not norm:
                continue
            reflection = [[F(i == j)-2*w[i]*wg[j]/norm
                           for j in range(n)] for i in range(n)]
            changed = [(mm(reflection, u), mm(v, reflection)) for u, v in pairs]
            new = [flags(u, v) for u, v in changed]
            if all(new[k][j] == min(old[k][j]+1, len(pairs[k][1]))
                   for k in range(len(pairs)) for j in range(2)):
                break
        else:
            raise AssertionError('Bounded independent control did not find a direction')
        require(mm(reflection, reflection) == eye(n) and
                mm(mm(tr(reflection), g), reflection) == g,
                'Reflection failed exact involution/isometry')
        transform = mm(reflection, transform)
        pairs = changed
        records.append(dict(integer_direction=list(map(int, w)), norm=str(norm),
                            attempts=attempt, old_flags=old, new_flags=new))
        require(len(records) <= max(len(v) for _, v in pairs), 'Too many reflection rounds')
    transform_inverse = inverse(transform)
    require(mm(mm(tr(transform), g), transform) == g, 'Full common metric not preserved')
    for (u, v), original in zip(pairs, originals):
        require(u == mm(transform, original) and
                v == mm(dual(g, original), transform_inverse) and v == dual(g, u),
                'Full primal/dual simultaneous conjugation failed')
    return dict(dimension=n, initial_flags=initial, rounds=records,
                profiles=[projector_profile(u, v) for u, v in pairs],
                full_metric_identity=True, all_primal_dual_conjugations=True)


def small_controls():
    out = []
    for n, signs in ((5, [1]*5), (7, [1, -1, 2, -2, 3, -3, 4])):
        g = [[F(signs[i] if i == j else 0) for j in range(n)] for i in range(n)]
        spaces = [(1, 2), (n-2, n-1), (2,)]
        originals = [[[F(i == j) for j in space] for i in range(n)] for space in spaces]
        out.append(reflected_family(g, originals, 916+n))

    # The actual tensor data complement is absent from the earlier pilot.
    # h3 is a control of this algebraic family, not a h3 finite scalar DAG.
    h = 3
    addresses = list(product(range(h), repeat=3))
    ground = [[F(i == j)-F(1, 9) for j in range(h)] for i in range(h)]
    g = [[ground[a][i]*ground[b][j]*ground[c][k]
          for i, j, k in addresses] for a, b, c in addresses]
    line = [F(1)]*h
    line_dual = [F(1, h)]*h
    perpendicular = [[F(1), F(0)], [F(0), F(1)], [F(-1), F(-1)]]
    perpendicular_dual = dual(ground, perpendicular)
    u_mid = [[line[a]*F(b*h+c == j) for j in range(h*h)] for a, b, c in addresses]
    u_data = [row+[perpendicular[a][j]*line[b]*line[c] for j in range(h-1)]
              for row, (a, b, c) in zip(u_mid, addresses)]
    v_data = [[line_dual[a]*F(b*h+c == j) for a, b, c in addresses]
              for j in range(h*h)]
    v_data += [[perpendicular_dual[j][a]*line_dual[b]*line_dual[c]
                for a, b, c in addresses] for j in range(h-1)]
    require(v_data == dual(g, u_data) and mm(v_data, u_data) == eye(h*h+h-1),
            'Actual data orthogonal kernel sum failed')
    p = mm(u_data, v_data)
    pc = [[line[i]*line_dual[j] for j in range(h)] for i in range(h)]
    data_residual = [[(F(a == i)-pc[a][i])*
                     (F(b == j and c == k)-pc[b][j]*pc[c][k])
                     for i, j, k in addresses] for a, b, c in addresses]
    require(data_residual == [[F(i == j)-p[i][j] for j in range(h**3)]
                             for i in range(h**3)],
            'Actual Pi3 tensor Pi12 complement identity differs')
    record = reflected_family(g, [u_mid, u_data], 929)
    record.update(actual_tensor_data_complement=True, control_ground=h,
                  original_data_rank=(h-1)*(h*h-1), control_is_not_a_scalar_network=True)
    out.append(record)
    return out


def logarithm(n, terms=80):
    """Independent exact atanh series, with an explicit positive tail."""
    require(n >= 1, 'Positive logarithm argument needed')
    k = n.bit_length()-1
    def series(x):
        z = (x-1)/(x+1)
        power = z
        value = F(0)
        for j in range(terms):
            value += 2*power/(2*j+1)
            power *= z*z
        remainder = 2*power/((2*terms+1)*(1-z*z))
        return value, value+remainder
    a, b = series(F(n, 2**k))
    l2, u2 = series(F(2))
    lo, hi = a+k*l2, b+k*u2
    grid = 2**320
    return F(lo.numerator*grid//lo.denominator, grid), F(-(-hi.numerator*grid//hi.denominator), grid)


def characteristic(peer, finite):
    h, roles = 51, 485680
    v, m = comb(h, 3), h**3
    n = v**3
    w = 2*n+2*v*v*(roles+h)
    loss = 3*v*v*h*h
    deficit = n-2*loss
    total = w*m-deficit
    counts = dict(v=v, m=m, N=n, W=w, L=loss, D=deficit, s=total)
    require(all(finite['full']['exact_counts'][k] == value == peer['row']['counts'][k]
                for k, value in counts.items()), 'Independent counts differ from the promoted graph')
    kernels = dict(middle=h*h, joined=2*h, data=h*h+h-1)
    multiplicities = dict(middle=(roles+h)*v*v, joined=(roles+h)*v*v, data=2*n)
    runs = {key: m-2*d for key, d in kernels.items()}
    ranks = {key: multiplicities[key]*(m-d) for key, d in kernels.items()}
    require(sum(ranks.values()) < total and all(2*d < m for d in kernels.values()),
            'Boundary families overlap or the two flags meet')
    moments = {key: multiplicities[key]*r*logarithm(r)[0] for key, r in runs.items()}
    log_upper = logarithm(m)[1]
    a = F(peer['row']['explicit_saving'])
    require(a == F(143492327855947419, 10**24) and 0 < a*log_upper < 1,
            'Unreviewed saving or exponential remainder range')
    first = total*log_upper-sum(moments.values())
    quadratic_remainder = a*a*total*log_upper*log_upper/(2*(1-a*log_upper))
    gap = deficit-a*first-quadratic_remainder
    require(first > 0 and gap > 0, 'Normalized exact characteristic is not strict')
    maximum = max(runs.values())
    require(maximum == m-4*h and m**651 > 2*maximum**651 and
            w < 2**49 and F(49*651)*(2+F(1, 25)) < 66000,
            'New proper-child/depth/row stock proof failed')
    for key in kernels:
        require(peer['row']['kernel_dimensions'][key] == kernels[key] and
                peer['row']['family_ranks'][key] == ranks[key] and
                F(peer['row'][key+'_moment_lower']) <= moments[key],
                'Peer claimed family moment is unsupported '+key)
    require(peer['row']['maximum_child'] == maximum and
            peer['row']['depth_bound_per_ceil_log2e'] == 651 and
            peer['row']['sufficient_row_degree'] == 66000 and
            peer['row']['sufficient_reservoir_linear_coefficient'] == 264000,
            'Peer new recursion contract differs')
    dimensions = [2, m-1, m, m+1]+[m*k+t for k in range(1, 17) for t in (0, 1, m-1)]
    for e in dimensions:
        for r in runs.values():
            require(r*(e//m) < e and F(r*(e//m), e) <= F(r, m),
                    'Main/tail child did not strictly decrease')
    return dict(counts=counts, roles=roles, kernels=kernels, run_lengths=runs,
                family_ranks=ranks, moment_lower={k: str(x) for k, x in moments.items()},
                chosen_saving=str(a), first_moment_upper=str(first),
                strict_characteristic_gap=str(gap), logarithm_terms=80,
                outward_dyadic_bits=320, maximum_child=maximum,
                exact_depth_binary_power_verified=True, row_degree=66000,
                reservoir_slope=264000, old_2600_claim_rejected=True,
                main_tail_dimension_controls=len(dimensions)*len(runs))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('generic-review', 'finite-review', 'assembly-review', 'proof-report', 'output'):
        ap.add_argument('--'+name, type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    started = time.monotonic()
    paths = [args.generic_review, args.finite_review, args.assembly_review, args.proof_report]
    hashes = {str(p): digest(p) for p in paths}
    peer = json.loads(args.generic_review.read_text())
    finite = json.loads(args.finite_review.read_text())
    accepted = json.loads(args.assembly_review.read_text())
    require(peer['status'].startswith('PASS') and finite['status'].startswith('PASS') and
            accepted['status'].startswith('PASS'), 'Independent input promotion absent')
    require(peer['input_sha256'][str(args.finite_review)] == digest(args.finite_review) and
            peer['finite_candidate_id'] == finite['candidate_id'] ==
            accepted['unchanged_finite_identity']['candidate_id'] and
            peer['finite_compiled_sha256'] == finite['full']['compiled_sha256'],
            'Full accepted scalar graph identity differs')
    require(accepted['actual_changed_boundary_audit']['whole_histogram_reconstructed'] and
            accepted['actual_changed_boundary_audit']['internal_old_frequencies_not_assumed'],
            'Actual changed boundary family accounting absent')
    require(peer['rational_finite_setup_existence'] and peer['fixed_table_changed'] and
            not peer['new_runtime_adapter'] and not peer['all_h51_ambient_basis_instantiated'],
            'Constructive fixed setup was confused with a materialized large certificate')
    endpoint = peer['dirty_common_frame_control']
    require(endpoint['full_source_gate_sink_conjugation'] and
            endpoint['omitted_one_conjugation_discriminated'] and
            endpoint['arbitrary_dirty_arrays'] == 2 and endpoint['spectator_prefixes'] == 2,
            'Complete common-frame endpoint control absent')
    for name, expected in peer['source_sha256'].items():
        require(digest(Path(__file__).with_name(name)) == expected, 'Frozen peer source changed '+name)
    row = characteristic(peer, finite)
    print('Independent normalized characteristic PASS', row['chosen_saving'], flush=True)
    controls = small_controls()
    print('Independent exact small metric/data families PASS', flush=True)
    result = dict(status='PASS root independent generic-basis inputs and written theorem review',
                  campaign='20261007T222521Z', generated_utc=datetime.now(timezone.utc).isoformat(),
                  input_sha256=hashes, source_sha256=digest(Path(__file__)),
                  finite_candidate_id=finite['candidate_id'],
                  finite_compiled_sha256=finite['full']['compiled_sha256'],
                  independent_characteristic=row, independent_small_controls=controls,
                  written_all_size_proof_reviewed=True,
                  full_family_finite_grid_degree='at most2+4F',
                  full_family_reflection_rounds='at most max kernel dimension',
                  all_h51_ambient_basis_instantiated=False, runtime_basis_adapter=False,
                  wall_seconds=time.monotonic()-started,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitations=['Constructive rational all-size proof and exact small controls; no giant T/table/prime instantiated',
                               'Complete general-beta assembly and all new depth/precision costs still required',
                               'Conditional upstream computational interfaces; not formal/unconditional theorem or novelty'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
