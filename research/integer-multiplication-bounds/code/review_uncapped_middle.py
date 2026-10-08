#!/usr/bin/env python3
"""Independent uncapped rotated middle profiles, row depth and witnesses.

Use only frozen independent rational and logarithm helpers. Reconstruct
the actual middle histogram and its first moment before comparing the
producer; no producer characteristic or root-bracketing function is used.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import sys
import time

from review_axis_batching import increasing_runs
from review_parameter_audit import log_integer
from review_pivot_batching import sparse_profile, stringify
from review_pivot_extension import independent_counts, line_projector


def small_profiles():
    results = []
    for h, triple in ((6, (0, 1, 2)), (6, (1, 3, 5)), (6, (3, 4, 5)),
                      (8, (0, 1, 2)), (8, (3, 6, 7)), (8, (5, 6, 7))):
        s = h*h
        projector = line_projector(h, triple)
        base = [[Q(int(i == j))-projector[i][j] for j in range(h)]
                for i in range(h)]
        matrix = [[Q(0)]*(h*s) for _ in range(h*s)]
        for i in range(h):
            for j in range(h):
                if base[i][j]:
                    for k in range(s):
                        matrix[i*s+k][j*s+k] = base[i][j]
        profile = sparse_profile(matrix)
        groups = increasing_runs(profile, h**3)
        a = min(triple)
        expected = sorted(r*s for r in (a, h-a-2, 1) if r)
        assert sorted(r for _, _, r in groups) == expected
        assert sum(expected) == (h-1)*s
        assert any(i != j and r == s for i, j, r in groups)
        assert max(expected) <= (h-2)*s < h**3
        assert a != 0 or (h-2)*s == max(expected)
        capped = increasing_runs(profile, s)
        assert len(capped) == h-1 and all(r == s for _, _, r in capped)
        results.append(dict(h=h, triple=triple, groups=groups,
                            full_canonical_profile_sha256=sha256(json.dumps(profile).encode()).hexdigest(),
                            actual_uncapped_lengths=sorted(expected),
                            exact_rank=(h-1)*s, old_cap_discriminated=len(groups)<len(capped)))
    assert any(row['old_cap_discriminated'] for row in results)
    return results


def moments(h, roles, variant):
    n = independent_counts(h, roles)
    v, m = n['v'], n['m']
    grid = 2**256
    cache = {}
    def lower(r):
        if r not in cache:
            lo = log_integer(r, 64)[0]
            cache[r] = Q(lo.numerator*grid//lo.denominator, grid)
        return cache[r]
    middle_hist = Counter()
    base_moment = Q(0)
    for a in range(h-2):
        count = (roles+h)*v*comb(h-a-1, 2)
        for r in (a, h-a-2, 1):
            if r:
                middle_hist[r*h*h] += count
                base_moment += count*h*h*r*lower(r)
    middle_rank = (roles+h)*v*v*h*h*(h-1)
    assert sum(r*c for r,c in middle_hist.items()) == middle_rank
    assert max(middle_hist) == (h-2)*h*h < m
    middle = middle_rank*lower(h*h)+base_moment
    joined_rank = (roles+h)*v*v*(m-2*h)
    t, g = m-4*h, 4*h+1
    joined = (roles+h)*v*v*t*(lower(t)-log_integer(g, 64)[1])
    data_hist = Counter()
    data = Q(0)
    data_rank = 0
    if variant == 'tensor-data':
        for a in range(h-2):
            for b in range(h-2):
                frequency = 2*v*(h-1)*comb(h-a-1, 2)*comb(h-b-1, 2)
                k = h*a+b
                for r in (k, h*h-k-2, 1):
                    if r:
                        data_hist[r] += frequency
                        data += frequency*r*lower(r)
        data_rank = 2*n['N']*(h-1)*(h*h-1)
        assert sum(r*c for r,c in data_hist.items()) == data_rank
    else:
        assert variant == 'two-family'
    unchanged = n['s']-middle_rank-joined_rank-data_rank
    assert unchanged >= 0
    lm = log_integer(m, 64)[1]
    first = n['s']*lm-middle-joined-data
    assert first > 0
    def gap(a):
        assert 0 <= a*lm < 1
        return n['D']-a*first-a*a*n['s']*lm*lm/(2*(1-a*lm))
    lo, hi = Q(0), Q(1, 10**7)
    assert gap(lo)>0>gap(hi)
    for _ in range(96):
        mid = (lo+hi)/2
        if gap(mid)>0:
            lo = mid
        else:
            hi = mid
    saving = Q(lo.numerator*10**24//lo.denominator, 10**24)
    assert gap(saving)>0
    return dict(counts=n, variant=variant, middle_histogram=dict(middle_hist),
                data_histogram=dict(data_hist), middle_moment=middle,
                additional_middle_moment=base_moment, joined_moment=joined,
                data_moment=data, middle_rank=middle_rank,
                joined_rank=joined_rank, data_rank=data_rank,
                unchanged_rank=unchanged, first_moment_upper=first,
                maximum_child=(h-2)*h*h, independent_saving=saving,
                independent_strict_gap=gap(saving)), gap


def main():
    sys.set_int_max_str_digits(0)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--producer', type=Path, required=True)
    ap.add_argument('--clone-review', type=Path, required=True)
    ap.add_argument('--clone-proof', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    start = time.monotonic()
    p = json.loads(args.producer.read_text())
    f = json.loads(args.clone_review.read_text())
    c = json.loads(args.clone_proof.read_text())
    assert p['status'].startswith('PASS STRICT UNCAPPED')
    assert f['status'] == 'PASS independent explicit clone finite witness'
    assert c['status'].startswith('PASS independent clone premises')
    for name, digest in p['source_sha256'].items():
        assert sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() == digest
    full = f['full']
    assert f['candidate_id'] == c['candidate_id'] == p['odd_bit_finite_audit']['candidate_id']
    assert p['odd_bit_finite_audit']['sha256'] == sha256(args.clone_review.read_bytes()).hexdigest()
    assert full['h'] == c['counts']['h'] == 51
    assert full['roles'] == c['changed_roles'] == 500703
    assert full['controller_plan']['selected_links'] == c['selected_links'] == 36312
    assert full['logical']['additions'] == c['changed_additions'] == 474540
    assert full['every_mapped_frame_has_exact_canonical_core_and_support']
    assert full['logical']['all_global_coefficients_exact']
    assert full['physical']['every_gate_output_exact'] and full['physical']['every_physical_target_exact']
    assert all(full['rational_frames'][key] for key in
               ('all_input_frames_original_lines', 'all_output_frames_exact',
                'every_designated_target_orthogonal', 'forward_and_reverse_complement_nesting'))
    for key, value in full['exact_counts'].items():
        assert c['counts'][key] == value
    for key in ('G', 'E', 'depth'):
        assert full['literal_scalar_guard'][key] == c['scalar_guard'][key]
    dirty = f['small_control']['complete_invocation_dirty_basis']
    assert len(dirty) == 2 and {row['inverse'] for row in dirty} == {False, True}
    assert all(row['exact_linear_map'] and row['input_basis_vectors']==4239 for row in dirty)
    rows = []
    for group in ('old_uncapped_comparison', 'witnesses'):
        for supplied in p[group]:
            h, roles, variant = supplied['h'], supplied['roles'], supplied['variant']
            independent, gap = moments(h, roles, variant)
            n = independent['counts']
            for key, value in n.items():
                assert supplied['counts'][key] == value
            assert Q(supplied['counts']['eta']) == Q(n['D'], n['W']*n['m'])
            assert supplied['compiler_basis_order'] == [3, 1, 2]
            hist = {int(r):count for r,count in supplied['middle_batch_histogram'].items()}
            assert hist == independent['middle_histogram']
            assert supplied['middle_batch_calls'] == sum(hist.values())
            assert supplied['middle_old_rank'] == independent['middle_rank']
            assert supplied['joined_old_rank'] == independent['joined_rank']
            assert supplied['data_old_rank'] == independent['data_rank']
            assert supplied['other_unchanged_rank'] == independent['unchanged_rank']
            assert supplied['maximum_child_rank'] == independent['maximum_child']
            assert Q(supplied['child_ratio']) == Q(h-2, h)
            a = Q(supplied['saving'])
            assert a > Q(supplied['capped_predecessor_saving'])
            assert gap(a)>0
            independent.update(supplied_saving=a, supplied_strict_gap=gap(a),
                               finite_group=group, h=h, side_roles=roles)
            rows.append(independent)
    h, W = 51, full['exact_counts']['W']
    assert W < 2**49
    assert 49*26*(2*25+1) < 2600*25
    names = ('review_uncapped_middle.py', 'review_axis_batching.py',
             'review_parameter_audit.py', 'review_pivot_batching.py', 'review_pivot_extension.py')
    result = dict(status='PASS independent uncapped middle construction and explicit witnesses',
                  generated_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
                  input_sha256={str(path):sha256(path.read_bytes()).hexdigest() for path in
                                (args.producer,args.clone_review,args.clone_proof)},
                  actual_uncapped_middle_profiles=small_profiles(), rows=rows,
                  clone_acceptance=dict(candidate_id=f['candidate_id'], roles=500703,
                      compiled_sha256=full['compiled_sha256'], changed_coefficients=70471800,
                      physical_frame_transitions=2899566, full_small_dirty_basis=4239,
                      full_finite_promotion_plus_separate_all_size_proof=True),
                  row_padding=dict(maximum_child=127449, child_ratio=Q(49,51),
                      depth_bound='26 ceil(log2 e)', fixed_width_premise='e<=C*p, p>=C',
                      W_bits=49, sufficient_polynomial_degree=2600,
                      polynomial_condition='log2(p)>=25',
                      sufficient_reservoir_condition='p^(1-epsilon)>5200 log2(p)',
                      sufficient_b_condition='b^(1-epsilon)>10400(log2(b)+8)',
                      eventual_constant_and_fixed_prime_thresholds_separate=True),
                  scope='Fresh uncapped profiles/depth/characteristics; frozen global-axis scalar/frame/tape proof and new full clone finite promotion supply their separate interfaces',
                  wall_seconds=time.monotonic()-start,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(stringify(result), indent=2, sort_keys=True)+'\n')
    for row in rows:
        print('PASS', row['finite_group'], row['variant'], row['supplied_saving'], flush=True)


if __name__ == '__main__':
    main()
