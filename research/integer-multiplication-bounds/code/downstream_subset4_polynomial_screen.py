#!/usr/bin/env python3
"""Exact fitting-matrix/central-rank screen for a distinct k4 bit motif.

The roots are intersections0/2; the scalar identity is I+E0+E2=J+A1A1T
over F2. All rational intersection-invariant fitting values are screened
by affine eigenvalue strata. No finite side graph or k5 test is replayed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import reduce
import hashlib
from itertools import combinations
import json
from math import comb, gcd
from pathlib import Path
import time

from downstream_gaussian import require
from downstream_parameter_optimum import as_strings


def choose(n, r):
    return comb(n, r) if 0 <= r <= n else 0


def spectrum_lines(n, k, coefficients):
    result = []
    for j in range(min(k, n-k) + 1):
        line = [0, 0, 0]
        for r in range(j, k+1):
            value = choose(k-j, r-j) * choose(n-r-j, k-r)
            for i in range(3):
                line[i] += value * coefficients[r][i]
        result.append((tuple(line), choose(n, j)-choose(n, j-1)))
    require(sum(m for _, m in result) == choose(n, k), 'Incidence multiplicities do not sum to volume')
    return result


GLOBAL = [(0,0,0), (1,0,0), (-2,0,0), (3,1,0), (-4,-4,1)]
STAR = [(1,0,0), (-1,0,0), (1,1,0), (-1,-3,1)]


def canonical(line):
    a, b, c = line
    if not a and not b:
        return None
    divisor = reduce(gcd, (abs(x) for x in line))
    out = tuple(x // divisor for x in line)
    return tuple(-x for x in out) if (out[0] or out[1]) < 0 else out


def evaluate(line, point):
    return line[0] * point[0] + line[1] * point[1] + line[2]


def strata(lines):
    lines = sorted({canonical(line) for line in lines if canonical(line) is not None})
    points = set()
    for first, second in combinations(lines, 2):
        a, b, c = first;d, e, f = second
        determinant = a*e-b*d
        if determinant:
            points.add((Q(b*f-c*e, determinant), Q(c*d-a*f, determinant)))
    for line in lines:
        a, b, c = line
        for t in range(len(lines)+2):
            point = (Q(-b*t-c, a), Q(t)) if a else (Q(t), Q(-c, b))
            if all(other == line or evaluate(other, point) for other in lines):
                points.add(point);break
        else:
            raise AssertionError('No open-line representative')
    for t in range(2*len(lines)+2):
        point = Q(t), Q(t*t)
        if all(evaluate(line, point) for line in lines):
            points.add(point);break
    else:
        raise AssertionError('No generic-plane representative')
    return lines, sorted(points)


def fitting_rank(lines, point):
    return sum(m for line, m in lines if evaluate(line, point))


def screen(h):
    global_lines = spectrum_lines(h, 4, GLOBAL)
    star_lines = spectrum_lines(h-2, 3, STAR)
    arrangement, points = strata([line for line, _ in global_lines+star_lines])
    v = comb(h, 4);rows = []
    for point in points:
        r = fitting_rank(global_lines, point)
        q = fitting_rank(star_lines, point)
        require(r > 0 and q > 0, 'Unit diagonal fitting matrix has zero rank')
        # One constant center, and h-1 incidence centers after eliminating
        # point0 using the even four-membership increment relation. Each
        # such scatter contains a fixed-point star omitting point0.
        loss = r + (h-1)*q
        deficit = v - 6*loss
        value = dict(A=point[0], B=point[1], ambient_rank=r,
                     omitted_point_star_rank=q, minimum_local_center_loss=loss,
                     optimistic_deficit_per_v_squared=deficit)
        if deficit > 0:
            m = r**3
            require(m >= 8, 'Positive rank stratum has invalid small native arity')
            eta = Q(deficit, 2*v*m)
            log_lower = 2*(r.bit_length()-1)
            require(log_lower > 0 and 0 < eta < 1, 'Invalid optimistic recurrence interval')
            value['optimistic_primitive_upper'] = eta / ((1-eta)*log_lower)
        else:
            value['optimistic_primitive_upper'] = Q(0)
        rows.append(value)
    return dict(h=h, v=v, unique_eigenvalue_lines=len(arrangement), exact_rank_strata=len(rows),
                maximum_optimistic_primitive_upper=max(x['optimistic_primitive_upper'] for x in rows),
                positive_deficit_strata=sum(x['optimistic_deficit_per_v_squared'] > 0 for x in rows),
                strata=rows)


def scalar_and_incidence_controls():
    entries = eigen_entries = 0
    for h in range(5, 10):
        sets = list(combinations(range(h), 4))
        for S in sets:
            for T in sets:
                overlap = len(set(S) & set(T))
                require((int(S == T) ^ int(overlap in (0,2))) == (1 ^ (overlap & 1)),
                        'New k4 F2 central-minus-side identity differs')
                entries += 1
        # The standard harmonic j-subset difference has lift to k-sets
        # product_i(1_(a_i in S)-1_(b_i in S)). Count its eigen action
        # directly against every inclusion Gram at k=4 and k=3.
        for n, k in ((h,4), (h-2,3)):
            family = list(combinations(range(n), k))
            maxj = min(k, n-k)
            for j in range(maxj+1):
                weights = []
                for S in family:
                    value = 1
                    for i in range(j):
                        value *= int(2*i in S)-int(2*i+1 in S)
                    weights.append(value)
                require(any(weights), 'Harmonic incidence control is zero')
                for r in range(k+1):
                    eigen = choose(k-j, r-j)*choose(n-r-j, k-r) if j <= r else 0
                    for i, S in enumerate(family):
                        actual = sum(choose(len(set(S)&set(T)), r)*w for T, w in zip(family,weights))
                        require(actual == eigen*weights[i], 'Exact incidence eigenvalue control differs')
                        eigen_entries += 1
    return dict(complete_scalar_entries=entries, exact_harmonic_incidence_entries=eigen_entries,
                scalar_relation='I+E0+E2=J+A1*A1^T over F2', no_E1_or_k5_replay=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--accepted-semantic-bulk', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    require(not a.output.exists(), 'Use a fresh output path')
    started = time.monotonic();old = json.loads(a.accepted_semantic_bulk.read_text())
    accepted_a = Q(next(row for row in old['witnesses'] if row['mode']=='tight' and row['prefix']=='balanced')['parameters']['a_bit'])
    require(accepted_a > Q(3,10**9), 'Accepted comparison saving differs')
    rows = [screen(h) for h in range(5,23)]
    finite_upper = max(row['maximum_optimistic_primitive_upper'] for row in rows)
    rmin = comb(23,2)-23
    infinite_upper = Q(1, (2*rmin**3-1)*2*(rmin.bit_length()-1))
    require(finite_upper < accepted_a and infinite_upper < Q(3,10**9) < accepted_a,
            'Scoped k4 polynomial family is not excluded by exact optimistic ceilings')
    result = dict(status='PASS VALID K4 ROOT0/2 SCALAR FAMILY; SCOPED OPTIMISTIC CEILING BELOW ACCEPTED BIT',
        campaign='20261007T222521Z', campaign_start='2026-10-07T22:25:21Z',
        campaign_original_deadline='2026-10-08T08:25:21Z', campaign_deadline='2026-10-08T10:00:00Z',
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        input=dict(path=str(a.accepted_semantic_bulk),sha256=hashlib.sha256(a.accepted_semantic_bulk.read_bytes()).hexdigest()),
        accepted_bit_saving=accepted_a, minimum_degree_polynomial='i*(i-2)',
        all_fitting_values='P(0)=P(2)=0,P(4)=1,A=P(1),B=P(3) arbitrary rational',
        finite_grounds=rows, finite_optimistic_upper=finite_upper,
        infinite_tail=dict(first_ground=23, ambient_rank_lower='C(h,2)-h',
                           minimum_rank=rmin, primitive_upper=infinite_upper,
                           proof='At least one Johnson eigenvalue of degree2/3/4 is nonzero; its multiplicity>=C(h,2)-h for h>=9'),
        controls=scalar_and_incidence_controls(),
        scope='All rational intersection-invariant fitting matrices with zeros0/2 in the retained three-stage incidence-center/monotone-target family; free side roles. Other root sets, noninvariant labels and changed chronology require separate proofs.',
        elapsed_seconds=time.monotonic()-started)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],'finite upper',finite_upper,'tail upper',infinite_upper,flush=True)


if __name__=='__main__':
    main()
