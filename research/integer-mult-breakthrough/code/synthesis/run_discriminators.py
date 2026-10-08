#!/usr/bin/env python3
"""Four-worker initial exact discriminators; every claim has separate scope."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb, factorial
from pathlib import Path
import time

from global_incidence import (dirty_word, identity, multiply, projector, rank,
                              replay_dirty_word, side_rows, source_line, subtract)


def scalar_probe():
    rows = []
    for h in [6, 7, 8, 9, 10, 23, 25]:
        inputs, sides, summed = side_rows(h)
        rows.append(dict(h=h, inputs=len(inputs), ordinary_sides=len(sides),
                         exact_target_rows=len(summed),
                         identity='A_exactly_one = I + Incidence_1^T Incidence_1 over GF(2)',
                         global_total_signals=h, shared_pair_signals=comb(h, 2)))
    return dict(status='EXACT BINARY SCALAR IDENTITY PASS', rows=rows,
                scope='Abstract binary source/sink maps; no physical address frames or transfer theorem.')


def reversible_probe():
    rows = []
    for h in [6, 7, 23, 25]:
        for separate in [False, True]:
            word = dirty_word(h, separate)
            receipt = replay_dirty_word(word)
            v = comb(h, 3)
            if receipt['paid_cnots'] != (33 if separate else 13) * v:
                raise ValueError('Unpaid word operation')
            # Targeted negatives: omit the last dirty echo and alter source index.
            bad = dict(word)
            bad['cnot_word'] = word['cnot_word'][:-v - 1] + word['cnot_word'][-v:]
            try:
                replay_dirty_word(bad)
            except ValueError:
                pass
            else:
                raise ValueError('Missing dirty echo was not rejected')
            bad = dict(word)
            bad['cnot_word'] = list(word['cnot_word'])
            a, b = bad['cnot_word'][-1]
            bad['cnot_word'][-1] = (a, (b + 1) % v)
            try:
                replay_dirty_word(bad)
            except ValueError:
                pass
            else:
                raise ValueError('Corrupted source map was not rejected')
            rows.append(dict(h=h, separate_sides=separate, **receipt,
                             missing_echo_negative_rejected=True,
                             corrupted_source_negative_rejected=True))
    return dict(status='EXACT ABSTRACT REVERSIBLE WORD PASS', rows=rows,
                scope='Literal paid CNOT word with full independent source, output and dirty columns. Capacity is allocated as counted roles; physical frames and address residuals are not implemented.')


def geometry_probe():
    rows = []
    for h in [6, 7, 8, 10, 23, 25]:
        candidates = list(combinations(range(h), 3)) if h <= 8 else [(0, 1, 2), (0, h // 2, h - 1)]
        for t in candidates:
            p = projector(h, sum(1 << c for c in t), sum(1 << c for c in t))
            f = subtract(identity(h), p)
            if rank(f) != h - 1 or multiply(f, f) != f:
                raise ValueError('Wrong whole-output hyperplane')
            # The desired exactly-one supports span this hyperplane, except
            # at h=6 where only nine lines may create extra dependencies.
            lines = [source_line(h, u) for u in combinations(range(h), 3)
                     if len(set(t) & set(u)) == 1]
            support_rank = rank(lines)
            if support_rank != h - 1:
                raise ValueError('Summed support is not the claimed hyperplane')
            for c in t:
                high = projector(h, 1 << c, (1 << h) - 1)
                delta = subtract(high, f)
                if rank(high) != h - 1 or rank(delta) != 2:
                    raise ValueError('Global high/output transition ranks changed')
                if high == f:
                    raise ValueError('Unpaid frame replacement should be rejected')
                j = next(j for j in range(h) if any(delta[i][j] for i in range(h)))
                rows.append(dict(h=h, target=list(t), common=c,
                                 total_frame_rank=h - 1, whole_output_rank=h - 1,
                                 support_span_rank=support_rank,
                                 difference_rank=2, minimal_nesting_rank_drop=1,
                                 omitted_transition_basis_column=j,
                                 payload_difference=[str(delta[i][j]) for i in range(h)]))
    a, b = 23, 25
    n = comb(a, 3) * comb(b, 3)
    loss = comb(b, 3) * a * (a - 1) + comb(a, 3) * b * (b - 1)
    # Conditional reuse of the old controller: one rank drop per whole-output
    # carrier on each axis already gives 4N additional rank mass.
    return dict(status='EXACT GLOBAL HYPERPLANE FRAME OBSTRUCTION PASS', cases=rows,
                frozen_ledger=dict(N=n, loss=loss, old_deficit=n - loss,
                                   one_drop_per_global_output_extra_mass=4 * n,
                                   mass_excess_above_mW=3 * n + loss),
                scope='Exact rational geometry and a conditional obstruction to reusing the old boundary/controller ledger with nonnested global-output carriers. A new boundary decoder or recurrence may change that ledger; no global circuit lower bound is claimed.')


def log_interval(x):
    x = Q(x)
    k = 0
    while x > 2:
        x /= 2
        k += 1
    def series(y):
        z = (y - 1) / (y + 1)
        lo = 2 * sum((z ** (2 * j + 1) / Q(2 * j + 1) for j in range(40)), Q())
        return lo, lo + 2 * z ** 81 / (81 * (1 - z * z))
    lo, hi = series(x)
    l2, u2 = series(Q(2))
    scale = 10 ** 40
    low, high = (lo + k * l2) * scale, (hi + k * u2) * scale
    return Q(low.numerator // low.denominator, scale), Q(-(-high.numerator // high.denominator), scale)


def optimistic_controller(a, b, r_a, r_b):
    m, n = a * b, comb(a, 3) * comb(b, 3)
    w = 2 * n + comb(b, 3) * r_a + comb(a, 3) * r_b
    rows = Counter({1:19 * n, 21:2 * n, 17:2 * n, 481:2 * n})
    loss = 0
    for h, r, copies in [(a, r_a, comb(b, 3)), (b, r_b, comb(a, 3))]:
        rows[h] += 2 * r * copies
        rows[m - 2 * h] += r * copies
        rows[1] += copies * h * (h - 1) + 2 * n
        rows[h - 2] += 2 * n
        loss += copies * h * (h - 1)
    if sum(t * count for t, count in rows.items()) != m * w - n + loss:
        raise ValueError('Sensitivity mass identity failed')
    return m, w, rows


def exact_moment(m, w, rows, saving):
    low, high = Q(), Q()
    for t, count in rows.items():
        lo, hi = log_interval(Q(m, t))
        x, y = saving * lo, saving * hi
        weight = Q(t * count, m * w)
        low += weight * (1 + x + x * x / 2 + x ** 3 / 6)
        high += weight * (1 + y + y * y / (2 * (1 - y / 3)))
    return low, high


def sensitivity_probe():
    rows = []
    candidates = [('accepted_old_role_counts', 30645, 40330),
                  ('ordinary_sides_abstract_roles', 4 * comb(23, 3) + 23 + comb(23, 2), 4 * comb(25, 3) + 25 + comb(25, 2)),
                  ('global_summed_abstract_roles', 2 * comb(23, 3) + 23, 2 * comb(25, 3) + 25),
                  ('hypothetical_input_only_roles', comb(23, 3), comb(25, 3))]
    for label, ra, rb in candidates:
        m, w, children = optimistic_controller(23, 25, ra, rb)
        values = []
        for saving in [Q(1, 9999), Q(1, 999)]:
            lo, hi = exact_moment(m, w, children, saving)
            values.append(dict(binary_saving=str(saving), moment_lower=str(lo),
                               moment_upper=str(hi), target_strict_pass=hi < 1,
                               target_strictly_excluded=lo > 1))
        rows.append(dict(label=label, roles23=ra, roles25=rb, W=w, target_checks=values))
    return dict(status='EXACT HYPOTHETICAL CONTROLLER SENSITIVITY PASS', rows=rows,
                optimistic_assumption='Each internal role pays exactly one child of rank h plus loss singletons; source/sink/boundary and exterior terms are held frozen. This is a hypothetical favorable histogram, not an implemented network.',
                scope='Exact consequences of a stated hypothetical child ledger. A global-output circuit changes the boundary semantics and cannot inherit this ledger merely from its abstract role count. Frozen complex saving separately caps final kappa below 1e-4.')


PROBES = dict(scalar=scalar_probe, reversible=reversible_probe,
              geometry=geometry_probe, sensitivity=sensitivity_probe)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--probe', choices=list(PROBES) + ['all'], default='all')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), Path(__file__).with_name('global_incidence.py')]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    random_seeds='None; deterministic exact probes',
                    source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources},
                    selected=list(PROBES) if args.probe == 'all' else [args.probe],
                    native_threads_per_worker=1)
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    start = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(PROBES[name]):name for name in protocol['selected']}
        for future in as_completed(pending):
            name = pending[future]
            receipt = future.result()
            receipt['recorded_utc'] = datetime.now(timezone.utc).isoformat()
            receipt['elapsed_from_launch_seconds'] = time.monotonic() - start
            (args.output / f'{name}.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print(json.dumps(dict(probe=name, status=receipt['status'], seconds=time.monotonic()-start)), flush=True)


if __name__ == '__main__':
    main()
