#!/usr/bin/env python3
"""Mixed partial/full output normalization for the joint mutable-source core.

The all-h profile is a conditional extension of the finite width-four word.
It is not a new circuit family or a general coupled-recurrence exclusion.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

import canonical_framed_shear_boundary as literal
from unitary_dyadic import ONE, ZERO

arithmetic = literal.geometry.arithmetic


def budget(h):
    if h < 3:
        raise ValueError('The proposed common frame has dimension two')
    children = Counter({1: 2, 2: 4})
    children[h - 2] += 6
    target_widths = [h - 1] * 2 + [h] * 4
    splits = [(1, h - 2)] * 2 + [(2, h - 2)] * 4
    if [sum(pair) for pair in splits] != target_widths:
        raise AssertionError('The partial/full row split is inconsistent')
    rank = sum(r * n for r, n in children.items())
    if rank != sum(target_widths) or rank != 6 * h - 2:
        raise AssertionError('Mixed target rank does not equal core charge')
    profile = dict(m=h, W=6, child_multiplicities=dict(children))
    rows = []
    for saving in (Q(20, 189981), Q(1, 1000)):
        child = arithmetic.moment_interval(profile, saving)
        lo, hi = arithmetic.log_interval(Q(h, h - 1))
        el, eu = arithmetic.exp_interval(saving * lo, saving * hi)
        denominator = (4 + Q(2 * (h - 1), h) * el,
                       4 + Q(2 * (h - 1), h) * eu)
        mixed = (6 * child[0] / denominator[1],
                 6 * child[1] / denominator[0])
        if child[1] >= 1 or mixed[0] <= 1:
            raise AssertionError('Wrong-baseline false gain or paid split did not discriminate')
        rows.append(dict(saving=saving, wrong_all_full_moment=child,
                         mixed_target_moment=mixed,
                         false_all_full_contraction_rejected=True))
    return dict(h=h, proposed_stock=6, core_rank=rank,
                actual_target_rank=sum(target_widths), target_widths=target_widths,
                per_target_child_splits=splits, child_histogram=dict(children),
                mixed_first_moment_exact=1, intervals=rows,
                scope='Conditional all-h extension of the rank ledger. Every row splits into two positive smaller widths; strict subadditivity excludes its uniform power ansatz. This does not exclude a different partial supplier, fusion or coupled assembly.')


def endpoints(case):
    h, columns = case
    size = 1 << (h * columns)
    digest = sha256()
    for label in (1, 7):
        for address in range(size):
            values = [ONE if a == address else ZERO for a in range(size)]
            partial = literal.full(literal.line(values, label, h, columns, True), h * columns)
            if sum(z != ZERO for z in partial) != 1 << ((h - 1) * columns):
                raise AssertionError('Actual partial output has the wrong support')
            restored = literal.line(partial, label, h, columns)
            if restored != literal.full(values, h * columns):
                raise AssertionError('The omitted source-line correction is not the exact missing operator')
            digest.update(str(partial).encode())
    return dict(h=h, columns=columns, labels=[1, 7],
                complete_partial_operator_columns=2 * size,
                exact_partial_coefficients=2 * size * size,
                selected_partial_rank=h - 1, missing_line_repair_verified=True,
                partial_operator_sha256=digest.hexdigest(),
                scope='Complete literal partial-output columns only; the joint dirty chronology is independently reviewed in its separate package.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or (args.output and args.output.exists()):
        raise ValueError('Positive workers and a fresh optional output are required')
    sources = [Path(__file__), Path(literal.__file__), Path(literal.geometry.__file__),
               Path(arithmetic.__file__), Path(__file__).with_name('unitary_dyadic.py')]
    hashes = {str(p.resolve()): sha256(p.read_bytes()).hexdigest() for p in sources}
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    bounded=args.bounded, seed=None, source_sha256=hashes,
                    scope='Mixed-output baseline discriminator, not a native supplier or multiplier theorem')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        budgets = list(pool.map(budget, [4] if args.bounded else [3, 4, 16, 64]))
        operators = list(pool.map(endpoints, [(4, 1)] if args.bounded else [(3, 1), (3, 2), (4, 1), (4, 2)]))
    if any(sha256(Path(p).read_bytes()).hexdigest() != digest for p, digest in hashes.items()):
        raise ValueError('An effective source changed during verification')
    summary = arithmetic.serializable(dict(status='PASS MIXED PARTIAL OUTPUT BASELINE',
                         budgets=budgets, actual_partial_operators=operators,
                         complete_native_supplier=False, new_multiplier_exponent=False))
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'], budgets=len(budgets),
                         complete_partial_columns=sum(r['complete_partial_operator_columns'] for r in operators))))


if __name__ == '__main__':
    main()
