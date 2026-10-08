#!/usr/bin/env python3
"""Exact controls for a scoped zero-excess common-frame transport lemma.

This is an independently implemented binary geometry and scalar-flow model.
It does not prove a quantitative global excess or an integer multiplier.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random
import time


def basis(rows):
    pivots = {}
    for value in rows:
        for pivot in sorted(pivots, reverse=True):
            if value >> pivot & 1:
                value ^= pivots[pivot]
        if value:
            pivot = value.bit_length() - 1
            for old in tuple(pivots):
                if pivots[old] >> pivot & 1:
                    pivots[old] ^= value
            pivots[pivot] = value
    return tuple(pivots[j] for j in sorted(pivots, reverse=True))


def subset(a, b):
    return len(basis(a + b)) == len(b)


def perpendicular(e, n):
    # Independent bounded enumeration rather than a producer's elimination.
    return basis(v for v in range(1 << n)
                 if all(not ((v & a).bit_count() & 1) for a in e))


def le(e, n):
    return basis(perpendicular(e, n) + tuple(v | (v << n) for v in e))


def distance(a, b, n):
    return len(basis(a + b)) - n


def subspaces(n):
    known = {()}
    pending = [()]
    for e in pending:
        for v in range(1, 1 << n):
            f = basis(e + (v,))
            if f not in known:
                known.add(f)
                pending.append(f)
    return sorted(known)


def lagrangians(n):
    # Generate all isotropic subspaces by extension; no Clifford producer.
    level = {()}
    mask = (1 << n) - 1
    for _ in range(n):
        next_level = set()
        for old in level:
            for v in range(1, 1 << (2 * n)):
                if any((((v & mask) & (u >> n)).bit_count()
                        + ((v >> n) & (u & mask)).bit_count()) & 1
                       for u in old):
                    continue
                new = basis(old + (v,))
                if len(new) == len(old) + 1:
                    next_level.add(new)
        level = next_level
    expected = 1
    for j in range(1, n + 1):
        expected *= 2**j + 1
    if len(level) != expected:
        raise ValueError('Incomplete isotropic enumeration')
    return sorted(level)


def geometry(n, samples, seed):
    spaces = subspaces(n)
    lifts = {e: le(e, n) for e in spaces}
    lags = lagrangians(n)
    intervals = [(a, b) for a in spaces for b in spaces if subset(a, b)]
    exhaustive = n <= 3
    if not exhaustive:
        rng = random.Random(seed)
        intervals = rng.sample(intervals, min(samples, len(intervals)))
    checks = negatives = 0
    digest = sha256()
    for a, b in intervals:
        allowed = {lifts[e] for e in spaces if subset(a, e) and subset(e, b)}
        endpoint = distance(lifts[a], lifts[b], n)
        for lag in lags:
            actual = distance(lifts[a], lag, n) + distance(lag, lifts[b], n)
            if (actual == endpoint) != (lag in allowed):
                raise ValueError('Geodesic interval classification failed')
            checks += 1
            negatives += actual != endpoint
            digest.update(f'{a},{b},{lag}:{actual};'.encode())
    return dict(n=n, exhaustive_nested_intervals=exhaustive,
                intervals=len(intervals), lagrangians=len(lags), checks=checks,
                off_geodesic_controls=negatives, sha256=digest.hexdigest())


def flow(n, seed, attempts=512):
    rng = random.Random(seed)
    labels = [t for t in range(1 << n) if t.bit_count() & 1]
    v = len(labels)
    full = basis(1 << j for j in range(n))
    start = [(t,) for t in labels] + [()] * (v + 3)
    caps = [full] * v + [perpendicular((t,), n) for t in labels] + [full] * 3
    current = list(start)
    coefficients = [[Fraction(int(i == j)) for j in range(v)]
                    for i in range(2 * v + 3)]
    spaces = subspaces(n)
    moves = charge = 0
    for _ in range(attempts):
        a, b = rng.sample(range(len(current)), 2)
        allowed = [e for e in spaces if subset(current[a], e)
                   and subset(current[b], e) and subset(e, caps[a])
                   and subset(e, caps[b])]
        if not allowed:
            continue
        e = rng.choice(allowed)
        charge += 2 * len(e) - len(current[a]) - len(current[b])
        current[a] = current[b] = e
        scalar = rng.choice([Fraction(-1), Fraction(1), Fraction(1, 2)])
        coefficients[a] = [x + scalar * y for x, y in zip(coefficients[a], coefficients[b])]
        moves += 1
        for role, row in enumerate(coefficients):
            for t, c in zip(labels, row):
                if c and not subset((t,), current[role]):
                    raise ValueError('Source-label transport invariant failed')
    charge += sum(len(cap) - len(e) for cap, e in zip(caps, current))
    baseline = sum(len(cap) - len(e) for cap, e in zip(caps, start))
    if charge != baseline:
        raise ValueError('Monotone chronology did not telescope')
    forbidden = allowed_nonzero = 0
    for s, row in zip(labels, coefficients[v:2*v]):
        for t, c in zip(labels, row):
            if (s & t).bit_count() & 1:
                forbidden += 1
                if c:
                    raise ValueError('Forbidden nonorthogonal flow survived')
            elif c:
                allowed_nonzero += 1
    return dict(n=n, seed=seed, source_labels=labels, attempts=attempts,
                legal_common_frame_gates=moves, exact_rank_charge=charge,
                endpoint_baseline=baseline, forbidden_coefficients_checked=forbidden,
                allowed_nonzero_coefficients=allowed_nonzero,
                dirty_restoration_claimed=False)


def scope_controls(n):
    # A complete dirty echo uses one paid decrease to transmit an odd self label.
    t = 1
    full = basis(1 << j for j in range(n))
    line = (t,)
    kernel = perpendicular(line, n)
    starts = [line, (), ()]  # source, sink, helper
    ends = [full, kernel, full]
    word = [(1, 2, -1, ()), (2, 0, 1, line),
            (1, 2, 1, ()), (2, 0, -1, full)]
    current = list(starts)
    columns = [[Fraction(int(i == j)) for j in range(3)] for i in range(3)]
    charge = 0
    decreases = 0
    for a, b, scalar, frame in word:
        for role in (a, b):
            charge += distance(le(current[role], n), le(frame, n), n)
            decreases += not subset(current[role], frame)
            current[role] = frame
        columns[a] = [x + scalar * y for x, y in zip(columns[a], columns[b])]
    for e, cap in zip(current, ends):
        charge += distance(le(e, n), le(cap, n), n)
    if columns != [[1, 0, 0], [1, 1, 0], [0, 0, 1]]:
        raise ValueError('Complete dirty echo failed')
    if charge != 3*n or decreases != 1:
        raise ValueError('Paid backtracking control was omitted')
    baseline = sum(distance(le(e, n), le(cap, n), n) for e, cap in zip(starts, ends))
    if charge - baseline != 2:
        raise ValueError('Backtracking excess is not charged')
    # One orthogonal direct transfer can saturate the endpoint bound.
    orthogonal = None
    if n >= 2:
        s = 2
        end = perpendicular((s,), n)
        ranks = [distance(le((), n), le(line, n), n),
                 distance(le(line, n), le(full, n), n),
                 distance(le(line, n), le(end, n), n)]
        if sum(ranks) != 2*n-2:
            raise ValueError('Allowed zero-excess transfer failed')
        orthogonal = dict(source=t, sink=s, exact_rank=sum(ranks))
    return dict(n=n, odd_self_transfer_with_arbitrary_dirty_restoration=True,
                rank_charge=charge, baseline=baseline, paid_excess=charge-baseline,
                rank_decreasing_moves=decreases, orthogonal_zero_excess=orthogonal)


def case(args):
    n, samples, seed = args
    return dict(geometry=geometry(n, samples, seed),
                flows=[flow(n, seed+j) for j in range(4)],
                scope_controls=scope_controls(n))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError('Invalid worker count')
    cases = [(n, 32, 202610084000+n) for n in range(1, 4 if args.bounded else 5)]
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh output path')
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(case, cases))
    result = dict(status='PASS EXACT SCOPED GEODESIC TRANSPORT CONTROLS',
                  recorded_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  workers=args.workers, cases=results, seconds=time.perf_counter()-started,
                  scope='Zero-extra-rank common-frame scalar transport requires orthogonal source/sink labels under fixed geodesic anchors. No additive per-output penalty, arbitrary gauge lower bound, native motif or exponent is certified.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'workers', 'seconds', 'scope')}))


if __name__ == '__main__':
    main()
