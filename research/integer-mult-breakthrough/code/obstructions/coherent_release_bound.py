#!/usr/bin/env python3
"""Exact controls for a coherent scalar-word release/minrank lower bound.

The model requires constant scalar coefficients in fixed virtual bank bases
and exactly common actual frames at scalar gates. Address-dependent residual
gauges and operator-valued scalar mixtures are outside the claim.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random
import time

from geodesic_transport import basis, distance, lagrangians, le, perpendicular, subset


def field_basis(rows):
    pivots = {}
    for raw in rows:
        row = [Q(x) for x in raw]
        for j in sorted(pivots):
            factor = row[j]
            if factor:
                row = [x-factor*y for x, y in zip(row, pivots[j])]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            scale = row[pivot]
            pivots[pivot] = [x/scale for x in row]
    return [pivots[j] for j in sorted(pivots)]


def in_field_span(row, rows):
    return len(field_basis(rows+[row])) == len(field_basis(rows))


def diagonal_intersection(lag, n):
    return basis(t for t in range(1 << n) if subset((t | (t << n),), lag))


def intersection_dimension(a, b):
    return len(a)+len(b)-len(basis(a+b))


def compatible_units(e, labels):
    return [[Q(int(i == j)) for j in range(len(labels))]
            for i, t in enumerate(labels) if subset((t,), e)]


def central_part(row, z_rows, forbidden):
    """Recover a Z row matching every forbidden coordinate, without guessing."""
    pivots = {}
    for original in z_rows:
        projected = [original[j] if j in forbidden else Q(0) for j in range(len(row))]
        full = list(original)
        for j in sorted(pivots):
            factor = projected[j]
            if factor:
                a, b = pivots[j]
                projected = [x-factor*y for x, y in zip(projected, a)]
                full = [x-factor*y for x, y in zip(full, b)]
        pivot = next((j for j, x in enumerate(projected) if x), None)
        if pivot is not None:
            scale = projected[pivot]
            pivots[pivot] = ([x/scale for x in projected], [x/scale for x in full])
    residual = [row[j] if j in forbidden else Q(0) for j in range(len(row))]
    part = [Q(0)]*len(row)
    for j in sorted(pivots):
        factor = residual[j]
        a, b = pivots[j]
        residual = [x-factor*y for x, y in zip(residual, a)]
        part = [x+factor*y for x, y in zip(part, b)]
    if any(residual) or any(part[j] != row[j] for j in forbidden):
        raise AssertionError('A forbidden endpoint coefficient escaped shared Z')
    if not in_field_span(part, z_rows):
        raise AssertionError('Recovered central row left Z')
    return part


def geometry(n, samples, seed):
    lags = lagrangians(n)
    e = {lag: diagonal_intersection(lag, n) for lag in lags}
    rng = random.Random(seed)
    pairs = [(a, b) for a in lags for b in lags] if n <= 3 else [
        (rng.choice(lags), rng.choice(lags)) for _ in range(samples)]
    strict = 0
    digest = sha256()
    for a, b in pairs:
        shared = intersection_dimension(e[a], e[b])
        bound = len(e[a])+len(e[b])-2*shared
        paid = distance(a, b, n)
        if paid < bound:
            raise AssertionError('Diagonal-intersection metric bound failed')
        strict += paid > bound
        digest.update(f'{a},{b}:{paid},{bound};'.encode())
    return lags, e, dict(n=n, all_lagrangians=len(lags), pairs=len(pairs),
                         exhaustive_pairs=(n <= 3), strict_slack_pairs=strict,
                         sha256=digest.hexdigest())


def flow(n, lags, diagonal, seed, attempts):
    rng = random.Random(seed)
    labels = [t for t in range(1 << n) if t.bit_count() & 1]
    v = len(labels)
    full = basis(1 << j for j in range(n))
    starts = [le((t,), n) for t in labels]+[le((), n)]*(v+2)
    ends = [le(full, n)]*v+[le(perpendicular((s,), n), n) for s in labels]+[le(full, n)]*2
    frames = list(starts)
    rows = [[Q(int(i == j)) for j in range(v)] for i in range(2*v+2)]
    z = []
    charge = loss_mass = loss_events = transitions = 0
    def reframe(role, target):
        nonlocal charge, loss_mass, loss_events, transitions, z
        old = frames[role]
        a, b = diagonal[old], diagonal[target]
        loss = len(a)-intersection_dimension(a, b)
        charge += distance(old, target, n)
        loss_mass += loss
        loss_events += bool(loss)
        transitions += old != target
        if loss:
            z = field_basis(z+[rows[role]])
        frames[role] = target
        if not in_field_span(rows[role], z+compatible_units(b, labels)):
            raise AssertionError('Reframing broke the shared-defect invariant')
    for _ in range(attempts):
        a, b = rng.sample(range(len(frames)), 2)
        target = rng.choice(lags)
        reframe(a, target)
        reframe(b, target)
        scalar = rng.choice([Q(-1), Q(1), Q(1, 2), Q(-1, 2)])
        rows[a] = [x+scalar*y for x, y in zip(rows[a], rows[b])]
        if frames[a] != frames[b] or not in_field_span(rows[a], z+compatible_units(diagonal[target], labels)):
            raise AssertionError('An exactly common-frame scalar gate broke the invariant')
        if len(z) > loss_events or loss_events > loss_mass:
            raise AssertionError('A defect rank or loss event was undercharged')
    for role, target in enumerate(ends):
        reframe(role, target)
    baseline = sum(len(diagonal[end])-len(diagonal[start]) for start, end in zip(starts, ends))
    if baseline != (2*v+2)*n-2*v or charge < baseline+2*loss_mass:
        raise AssertionError('The whole chronological rank bound failed')
    central = []
    for s, row in zip(labels, rows[v:2*v]):
        forbidden = {j for j, t in enumerate(labels) if (s & t).bit_count() & 1}
        central.append(central_part(row, z, forbidden))
    rank = len(field_basis(central))
    if rank > len(z) or charge < baseline+2*rank:
        raise AssertionError('The endpoint fitting-rank bound failed')
    return dict(seed=seed, scalar_gates=attempts, frame_transitions=transitions,
                complete_rank_charge=charge, endpoint_dimension_baseline=baseline,
                shared_defect_rank=len(z), loss_events=loss_events,
                lost_direction_mass=loss_mass, endpoint_completion_rank=rank,
                extra_rank=charge-baseline,
                arbitrary_dirty_restoration_claimed=False,
                final_identity_map_claimed=False)


def controls():
    # Isotropy is necessary for the stronger metric inequality.
    a, b = basis((5, 11)), basis((10, 11))
    ea, eb = diagonal_intersection(a, 2), diagonal_intersection(b, 2)
    if distance(a, b, 2) >= len(ea)+len(eb)-2*intersection_dimension(ea, eb):
        raise AssertionError('Non-isotropic counterexample disappeared')
    # An uncharged copy from an odd line into its perpendicular violates Z=0.
    labels = [1]
    sink_e = perpendicular((1,), 2)
    if in_field_span([Q(1)], compatible_units(sink_e, labels)):
        raise AssertionError('Omitted unequal-frame transition was accepted')
    # Complete dirty echo saturates the rank-one bound, including restoration.
    rows = [[Q(int(i == j)) for j in range(3)] for i in range(3)]
    frames = [(1,), (), ()]
    ends = [(1, 2), (2,), (1, 2)]
    word = [(1, 2, -1, ()), (2, 0, 1, (1,)),
            (1, 2, 1, ()), (2, 0, -1, (1, 2))]
    charge = 0
    for a, b, scalar, frame in word:
        for role in (a, b):
            charge += distance(le(frames[role], 2), le(frame, 2), 2)
            frames[role] = frame
        rows[a] = [x+scalar*y for x, y in zip(rows[a], rows[b])]
    charge += sum(distance(le(e, 2), le(f, 2), 2) for e, f in zip(frames, ends))
    if rows != [[1, 0, 0], [1, 1, 0], [0, 0, 1]] or charge != 6:
        raise AssertionError('Exact arbitrary-dirty rank-one saturation failed')
    return dict(non_isotropic_metric_counterexample=True,
                uncharged_unequal_frame_copy_rejected=True,
                whole_dirty_echo=dict(rank=6, baseline=4, central_fitting_rank=1),
                residual_gauge_model_excluded=True)


def case(args):
    n, samples, seed, attempts = args
    lags, diagonal, checked = geometry(n, samples, seed)
    return dict(geometry=checked,
                flows=[flow(n, lags, diagonal, seed+j, attempts) for j in range(4)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError('Invalid workers')
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh output path')
    cases = [(n, 4096, 202610090100+n, 32 if args.bounded else 96)
             for n in range(1, 3 if args.bounded else 5)]
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        outcomes = list(pool.map(case, cases))
    sources = [Path(__file__), Path(__file__).with_name('geodesic_transport.py')]
    result = dict(status='PASS EXACT COHERENT RELEASE CONTROLS',
                  recorded_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                  source_sha256={str(p): sha256(p.read_bytes()).hexdigest() for p in sources},
                  cases=outcomes, controls=controls(), seconds=time.perf_counter()-started,
                  scope='Coherent constant-scalar words at common actual frames have extra rank at least twice central fitting minrank. Exact small geometry and random cancellation invariants; random words are not claimed to implement the final identity or restore dirty payloads. No arbitrary-gauge or multiplier bound.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as f:
            f.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'workers', 'seconds', 'scope')}))


if __name__ == '__main__':
    main()
