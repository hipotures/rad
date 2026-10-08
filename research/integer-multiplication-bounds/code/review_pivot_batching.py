#!/usr/bin/env python3
"""Independent lower/lower factors, segmented pivot batches and count bounds.

Exact arithmetic throughout. General rational factors are reconstructed,
not read from the producer. The producer's profile is only a comparison.
The rank-one terminal profile, middle-bank multiplicities and low-rank
joined bound provide separate, explicitly conditional saving certificates.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from math import comb, lcm
from pathlib import Path
import random
import resource
import sys
import time

from review_parameter_audit import log_integer
from review_asymmetric_motif import independent_saving


def identity(n):
    return [[Q(int(i == j)) for j in range(n)] for i in range(n)]


def multiply(A, B):
    return [[sum(a*b for a, b in zip(row, column)) for column in zip(*B)] for row in A]


def transpose(A):
    return [list(row) for row in zip(*A)]


def invert(A):
    n = len(A)
    work = [list(map(Q, row))+eye for row, eye in zip(A, identity(n))]
    for j in range(n):
        pivot = next(i for i in range(j, n) if work[i][j])
        work[j], work[pivot] = work[pivot], work[j]
        c = work[j][j]
        work[j] = [v/c for v in work[j]]
        for i in range(n):
            if i != j and work[i][j]:
                c = work[i][j]
                work[i] = [a-c*b for a, b in zip(work[i], work[j])]
    return [row[n:] for row in work]


def exact_factor(A):
    """Track L and R with LAR=Pi, clearing below and then left."""
    n = len(A)
    work = [list(map(Q, row)) for row in A]
    L, R = identity(n), identity(n)
    pivots = []
    for i in range(n):
        columns = [j for j in range(n) if work[i][j]]
        if not columns:
            continue
        j = max(columns)
        pivots.append((i, j))
        for k in range(i+1, n):
            if work[k][j]:
                c = work[k][j]/work[i][j]
                work[k] = [a-c*b for a, b in zip(work[k], work[i])]
                L[k] = [a-c*b for a, b in zip(L[k], L[i])]
        for k in range(j):
            if work[i][k]:
                c = work[i][k]/work[i][j]
                for row in range(n):
                    work[row][k] -= c*work[row][j]
                    R[row][k] -= c*R[row][j]
        c = work[i][j]
        work[i] = [v/c for v in work[i]]
        L[i] = [v/c for v in L[i]]
        assert work[i] == [Q(int(k == j)) for k in range(n)]
        assert all(work[k][j] == int(k == i) for k in range(n))
    Pi = [[Q(int((i, j) in pivots)) for j in range(n)] for i in range(n)]
    assert work == Pi == multiply(multiply(L, A), R)
    assert all(L[i][j] == R[i][j] == 0 for i in range(n) for j in range(i+1, n))
    assert all(L[i][i] and R[i][i] for i in range(n))
    return pivots, L, R


def sparse_profile(A):
    """Direct rational elimination on future rows only, no integer gcd code."""
    rows = [{j: Q(v) for j, v in enumerate(row) if v} for row in A]
    answer = []
    for i, row in enumerate(rows):
        if not row:
            continue
        j = max(row)
        answer.append((i, j))
        for k in range(i+1, len(rows)):
            if j not in rows[k]:
                continue
            c = rows[k][j]/row[j]
            values = dict(rows[k])
            for column, value in row.items():
                values[column] = values.get(column, Q(0))-c*value
                if not values[column]:
                    del values[column]
            rows[k] = values
    assert len({j for _, j in answer}) == len(answer)
    return answer


def diagonal_runs(pivots, cap):
    answer = []
    previous = None
    for i, j in pivots:
        if i != j:
            previous = None
            continue
        if previous is not None and previous+1 == i and answer[-1] < cap:
            answer[-1] += 1
        else:
            answer.append(1)
        previous = i
    return answer


def concentrate_rows(U):
    n, d = len(U), len(U[0])
    S, work = identity(n), [list(map(Q, row)) for row in U]
    pivots = []
    for i in range(n):
        for column, previous in pivots:
            if work[i][column]:
                c = work[i][column]
                work[i] = [a-c*b for a, b in zip(work[i], work[previous])]
                S[i] = [a-c*b for a, b in zip(S[i], S[previous])]
        nonzero = [j for j in range(d) if work[i][j]]
        if nonzero:
            column = min(nonzero)
            c = work[i][column]
            work[i] = [v/c for v in work[i]]
            S[i] = [v/c for v in S[i]]
            pivots.append((column, i))
    assert multiply(S, U) == work and len(pivots) <= d
    assert all(S[i][j] == 0 for i in range(n) for j in range(i+1, n))
    assert all(S[i][i] for i in range(n))
    return S, {i for i, row in enumerate(work) if any(row)}


def generic_controls(seed):
    from diagonal_bruhat_batches import profile as producer_profile
    rng = random.Random(seed)
    general = lowrank = 0
    for n in range(2, 8):
        matrices = [identity(n), [[Q(0)]*n for _ in range(n)]]
        matrices += [[[Q(rng.randrange(-3, 4)) for _ in range(n)] for _ in range(n)] for _ in range(4)]
        for A in matrices:
            pivots, L, R = exact_factor(A)
            assert pivots == sparse_profile(A)
            common = lcm(*(v.denominator for row in A for v in row))
            sparse = [{j: int(v*common) for j, v in enumerate(row) if v} for row in A]
            assert producer_profile(sparse)[0] == pivots
            general += 1
        for d in range(1, min(3, n-1)+1):
            for _ in range(3):
                U = [[Q(int(i == j)) for j in range(d)] for i in range(d)]
                U += [[Q(rng.randrange(-2, 3)) for _ in range(d)] for _ in range(n-d)]
                rng.shuffle(U)
                Vt = multiply(invert(multiply(transpose(U), U)), transpose(U))
                P = multiply(U, Vt)
                assert multiply(P, P) == P
                A = [[Q(int(i == j))-P[i][j] for j in range(n)] for i in range(n)]
                S, modified = concentrate_rows(U)
                B = multiply(S, A)
                first = sparse_profile(A)
                second = sparse_profile(B)
                assert first == second and len(first) == n-d
                stolen = {j for i, j in second if i in modified and j > i and j not in modified}
                assert len(stolen) <= len(modified) <= d
                pivot_map = dict(second)
                assert all(pivot_map[i] == i for i in range(n) if i not in modified | stolen)
                runs = diagonal_runs(second, n-1)
                assert sum(runs) >= n-2*d and len(runs) <= 2*d+1
                lowrank += 1
    # A rank-one complement does not in general have all nonzero pivots
    # diagonal; the missing diagonal must not be silently counted twice.
    n = 5
    A = [[Q(int(i == j))-Q(1, n) for j in range(n)] for i in range(n)]
    pivots = sparse_profile(A)
    assert len(pivots) == n-1 and sum(i == j for i, j in pivots) == n-2
    return dict(seed=seed, reconstructed_general_LAR_factors=general,
        generic_lowrank_projections=lowrank, lower_concentration_profile_invariant=True,
        every_unmodified_unstolen_row_diagonal=True, two_d_union_bound_verified=True,
        rejected_all_rank_pivots_diagonal=dict(dimension=n, rank=n-1, diagonal=n-2))


def terminal_profiles(h):
    frequencies = Counter(min(t) for t in combinations(range(h), 3))
    assert all(frequencies[a] == comb(h-a-1, 2) for a in range(h-2))
    checked = 0
    for a in range(h-2):
        triples = {(a, a+1, a+2), (a, a+1, h-1), (a, h-2, h-1)}
        for triple in triples:
            u = [Q(int(i in triple)) for i in range(h)]
            v = [Q(2 if i in triple else -1, 6) for i in range(h)]
            assert sum(x*y for x, y in zip(u, v)) == 1 and u[a] and v[-1]
            A = [[Q(int(i == j))-u[i]*v[j] for j in range(h)] for i in range(h)]
            actual = sparse_profile(A)
            expected = [(i, h-1 if i == a else i) for i in range(h-1)]
            assert actual == expected
            assert diagonal_runs(actual, h-1) == [r for r in (a, h-a-2) if r]
            checked += 1
    return frequencies, dict(ground=h, all_triples=sum(frequencies.values()),
        distinct_minimum_positions=len(frequencies), independently_eliminated_profiles=checked,
        rank_one_projector_complement_rank=h-1, exact_profile_and_run_formula=True)


def batched_add(H, D, runs, modulus):
    H, D = H[:], D[:]
    pairs = [(a+i, b+i) for a, b, width in runs for i in range(width)]
    assert len({a for a, _ in pairs}) == len({b for _, b in pairs}) == len(pairs)
    for a, b, width in runs:
        for i in range(width):
            D[b+i] = (D[b+i]+H[a+i]) % modulus
        H[a:a+width], D[b:b+width] = D[b:b+width], H[a:a+width]
        for i in range(width):
            D[b+i] = (H[a+i]-D[b+i]) % modulus
    return H, D


def operator_controls():
    cases = entries = 0
    for n, modulus, runs in ((3, 3, [(0, 0, 2), (2, 2, 1)]),
                             (3, 3, [(0, 1, 2)]), (2, 9, [(0, 0, 1), (1, 1, 1)])):
        for values in product(range(modulus), repeat=2*n):
            H, D = list(values[:n]), list(values[n:])
            expected = H[:]
            for a, b, width in runs:
                for i in range(width):
                    expected[a+i] = (expected[a+i]+D[b+i]) % modulus
            actual_H, actual_D = batched_add(H, D, runs, modulus)
            assert actual_H == expected and actual_D == D
            entries += 1
        cases += 1
    # The aggregate arithmetic must not carry from one b-digit field into
    # the next. It is not addition modulo q^(rb).
    q, H, D = 3, [2, 0], [1, 0]
    component = [(a+b) % q for a, b in zip(H, D)]
    aggregate = (H[0]+q*H[1]+D[0]+q*D[1]) % q**2
    decoded = [aggregate % q, aggregate//q]
    assert component == [0, 0] and decoded == [0, 1]
    # An arbitrary permutation of pivots cannot be batched without the
    # missing coordinate adapter.
    wrong, _ = batched_add([0, 0], [1, 2], [(0, 0, 2)], 3)
    assert wrong == [1, 2] and wrong != [2, 1]
    return dict(exhaustive_ring_shapes=cases, exact_ring_addresses=entries,
        disjoint_runs_preserve_other_words=True, wrong_aggregate_carry=decoded,
        required_component_result=component, rejected_noncontiguous_reverse_pivots=True)


def tail_controls():
    shapes = entries = 0
    for m, e, q in ((3, 3, 3), (3, 4, 3), (2, 5, 3)):
        b, t = divmod(e, m)
        Qb = q**b
        for values in product(range(q), repeat=2*e):
            H, D = list(values[:e]), list(values[e:])
            oldH, oldD = H[:], D[:]
            words = lambda v: [sum(v[j*b+i]*q**i for i in range(b)) for j in range(m)]
            Hw, Dw = words(H), words(D)
            # Full main swap is the original three-shear identity. The
            # middle identity partial permutation is split into strict runs.
            Dw = [(x-y) % Qb for x, y in zip(Dw, Hw)]
            Hw, Dw = batched_add(Hw, Dw, [(0, 0, m-1), (m-1, m-1, 1)], Qb)
            Dw = [(x-y) % Qb for x, y in zip(Hw, Dw)]
            H[:m*b] = [(Hw[j]//q**i) % q for j in range(m) for i in range(b)]
            D[:m*b] = [(Dw[j]//q**i) % q for j in range(m) for i in range(b)]
            for i in range(m*b, e):
                H[i], D[i] = D[i], H[i]
            assert H == oldD and D == oldH
            entries += 1
        assert t < m and all(r*b <= r*e//m and r*b < e for r in range(1, m))
        shapes += 1
    return dict(odd_radix_shapes=shapes, complete_main_tail_addresses=entries,
        exact_arbitrary_width_swap=True, main_and_tail_coordinate_order_preserved=True,
        added_address_records=0)


def weighted_bound(h, R, include_join, cap):
    v, m = comb(h, 3), h**3
    N = v**3
    W = 2*N+2*v*v*(R+h)
    L = 3*v*v*h*h
    D = N-2*L
    s = W*m-D
    assert D > 0
    per_triple = Counter()
    for a in range(h-2):
        frequency = comb(h-a-1, 2)
        per_triple[1] += frequency
        if a:
            per_triple[a] += frequency
        per_triple[h-a-2] += frequency
    multiplier = (R+h)*v*h*h
    middle = {r: count*multiplier for r, count in per_triple.items()}
    T = (R+h)*v*v*h*h*(h-1)
    assert sum(r*count for r, count in middle.items()) == T < s
    lm_low, lm_high = log_integer(m, 48)
    middle_moment = sum(count*r*log_integer(r, 48)[0] for r, count in middle.items())
    join_count = (R+h)*v*v
    join_rank = m-2*h
    t = m-4*h
    groups = (5*h+1 if cap else 4*h+1)
    join_moment = Q(0)
    if include_join:
        assert t >= groups and T+join_count*join_rank <= s
        logarithm = log_integer(t, 48)[0]-log_integer(groups, 48)[1]
        assert logarithm > 0
        join_moment = join_count*t*logarithm
    first_moment_upper = s*lm_high-middle_moment-join_moment
    assert first_moment_upper > 0
    candidate = (1-Q(1, 2**20))*D/first_moment_upper
    a = Q((candidate.numerator*10**15-1)//candidate.denominator, 10**15)
    assert 0 < a < Q(1, 64) and a*lm_high < 1
    # For 0<=x<1, exp(x)<=1+x+x^2/[2(1-x)]. All true
    # ln(m/r) are between0 and lm_high. Bound the global quadratic
    # remainder conservatively, while using the proven lower log moment.
    normalized_cost_upper = s+a*first_moment_upper+a*a*s*lm_high*lm_high/(2*(1-a*lm_high))
    gap = W*m-normalized_cost_upper
    assert gap > 0
    old_low, old_high = independent_saving(Q(D, W*m), m)
    assert a > old_high
    max_run = (h*h if cap else m-2*h) if include_join else h-2
    # Integer depth bound: ln(m/max_run)>= (m-max_run)/m,
    # ln(e)<=log2(e), so ceil[m/(m-max_run)*log2(e)] suffices.
    row_depth_multiplier = Q(m, m-max_run)
    row_bit_degree = (W-1).bit_length()*row_depth_multiplier
    return dict(h=h, side_roles=R, v=v, m=m, N=N, W=W, L=L, D=D, s=s,
        subset_middle_old_ranks=T, middle_batches=middle,
        joined_edges=join_count if include_join else 0,
        joined_rank_per_edge=join_rank, joined_guaranteed_diagonal_pivots=t,
        joined_run_bound=groups if include_join else 0,
        joined_length_cap=h*h if cap else None, maximum_run=max_run,
        row_depth_log2_multiplier=row_depth_multiplier, row_divisor_bit_degree=row_bit_degree,
        middle_log_moment_lower=middle_moment, joined_log_moment_lower=join_moment,
        first_moment_upper=first_moment_upper, chosen_bit_saving=a,
        old_unbatched_saving_lower=old_low, old_unbatched_saving_upper=old_high,
        strict_improvement_over_old_upper=a-old_high,
        quadratic_exponential_upper=normalized_cost_upper,
        strict_weighted_gap=gap,
        scope='Fixed finite batch subset and proven low-rank run bound; all unchanged scalar edges stay individual')


def stringify(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [stringify(item) for item in value]
    return value


def main():
    sys.set_int_max_str_digits(0)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--finite-review', type=Path, required=True)
    ap.add_argument('--seed', type=int, default=631)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    started = time.monotonic()
    saved = json.loads(args.finite_review.read_text())
    assert saved['status'] == 'PASS' and saved['full']['matches_immutable_producer_identity_and_compilation']
    h, R = saved['full']['h'], saved['full']['compiled_roles']
    print('Starting generic rational factor and pivot controls', flush=True)
    generic = generic_controls(args.seed)
    print('PASS generic lower/lower factors and low-rank union bound', flush=True)
    _, profiles = terminal_profiles(h)
    operators, tails = operator_controls(), tail_controls()
    print('PASS closed terminal profiles and segmented odd-radix operators', flush=True)
    rows = [weighted_bound(h, R, joined, capped) for joined, capped in
            ((False, False), (True, False), (True, True))]
    names = ('review_pivot_batching.py', 'review_parameter_audit.py',
             'review_asymmetric_motif.py', 'diagonal_bruhat_batches.py')
    result = dict(status='PASS independent pivot batching algebra/count/strict weighted-bound certificate',
        generated_at=datetime.now(timezone.utc).isoformat(), seed=args.seed,
        finite_review_sha256=sha256(args.finite_review.read_bytes()).hexdigest(),
        finite_candidate_id=saved['full']['candidate_id'],
        finite_compiled_sha256=saved['full']['compiled_sha256'],
        source_sha256={name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
        generic_controls=generic, terminal_profiles=profiles,
        segmented_operator_controls=operators, arbitrary_width_tail_controls=tails,
        rows=rows, wall_seconds=time.monotonic()-started,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limitations=['Complete original fixed-tape/row-reservation transfer is a separately stated mathematical argument',
            'No actual finite joined matrices or whole multiplication machine are materialized',
            'No integer-multiplication kappa is inferred without fresh downstream composition'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(stringify(result), indent=2, sort_keys=True)+'\n')
    for row in rows:
        print('PASS weighted bit saving', row['chosen_bit_saving'], 'joined', bool(row['joined_edges']),
              'cap', row['joined_length_cap'], flush=True)


if __name__ == '__main__':
    main()
