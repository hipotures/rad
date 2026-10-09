#!/usr/bin/env python3
"""Exact scan cut-rank certificates and independent order-flux controls.

The all-size argument is recorded separately. These finite controls certify
complete integer submatrices, integral rank factorizations and unit minors.
They do not certify a native scan, conditional route or multiplier exponent.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import random


def matrix(order, kind):
    n = len(order)
    positions = {value: index for index, value in enumerate(order)}
    if len(positions) != n or set(positions) != set(range(n)):
        raise ValueError("A complete address order is required")
    if kind == "prefix":
        return [[int(positions[y] <= positions[x]) for y in range(n)] for x in range(n)]
    if kind == "difference":
        return [[int(x == y) - int(positions[x] == positions[y] + 1)
                 for y in range(n)] for x in range(n)]
    raise ValueError("Unknown scan kind")


def cut(a, bit):
    return [[a[x][y] for y in range(len(a)) if not (y >> bit) & 1]
            for x in range(len(a)) if (x >> bit) & 1]


def rank_mod(a, prime):
    """Independent elimination, used only for small finite field controls."""
    if not a or not a[0]:
        return 0
    a = [[x % prime for x in row] for row in a]
    pivot = 0
    for col in range(len(a[0])):
        found = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        inverse = pow(a[pivot][col], -1, prime)
        a[pivot] = [x * inverse % prime for x in a[pivot]]
        for i in range(pivot + 1, len(a)):
            multiplier = a[i][col]
            if multiplier:
                a[i] = [(x - multiplier * y) % prime
                        for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def transition_indices(order, bit):
    return [j for j in range(1, len(order))
            if not (order[j - 1] >> bit) & 1 and (order[j] >> bit) & 1]


def certify_order(task):
    f, name, order, axes = task
    n = 1 << f
    positions = {value: j for j, value in enumerate(order)}
    prefix = matrix(order, "prefix")
    difference = matrix(order, "difference")
    ranks = []
    for bit in range(f):
        transitions = transition_indices(order, bit)
        count = len(transitions)
        ranks.append(count)
        row_labels = [x for x in range(n) if (x >> bit) & 1]
        col_labels = [y for y in range(n) if not (y >> bit) & 1]
        # For every 1-run after a transition, E selects its last transition.
        # F assigns each 0-run to its first following transition. Initial
        # 1-runs and final 0-runs have zero cross rows/columns respectively.
        row_groups = {x: next((a for a in range(count - 1, -1, -1)
                              if transitions[a] <= positions[x]), None)
                      for x in row_labels}
        col_groups = {y: next((b for b in range(count)
                              if positions[y] < transitions[b]), None)
                      for y in col_labels}
        for x in row_labels:
            for y in col_labels:
                a, b = row_groups[x], col_groups[y]
                expected = int(a is not None and b is not None and b <= a)
                if prefix[x][y] != expected:
                    raise AssertionError("Complete integral E L F factorization failed")
                edge = int(positions[x] == positions[y] + 1)
                if difference[x][y] != -edge:
                    raise AssertionError("Complete difference cut support failed")
        for kind, full in (("prefix", prefix), ("difference", difference)):
            minor = [[full[order[j]][order[k - 1]] for k in transitions]
                     for j in transitions]
            expected = [[int(b <= a) if kind == "prefix" else -int(a == b)
                         for b in range(count)] for a in range(count)]
            if minor != expected:
                raise AssertionError("The exact unit minor failed")
            if f <= 4:
                for prime in (2, 3, 5):
                    if rank_mod(cut(full, bit), prime) != count:
                        raise AssertionError("Independent field elimination disagreed")
                    gauged = [[full[x][y] * pow(2 if prime != 2 else 1, x % 3, prime)
                               * (-1 if y.bit_count() % 2 else 1)
                               for y in range(n)] for x in range(n)]
                    if rank_mod(cut(gauged, bit), prime) != count:
                        raise AssertionError("Nonzero diagonal gauges changed the rank")
        target = [[int((y & x) == y) for y in col_labels] for x in row_labels]
        if any(target[i][i] != 1 or any(target[i][j] for j in range(i + 1, n // 2))
               for i in range(n // 2)):
            raise AssertionError("The full Boolean-zeta cut is not unit lower triangular")
        if axes is not None:
            position = axes.index(bit) + 1
            if count != 1 << (position - 1):
                raise AssertionError("Axis-lexicographic cut-rank formula failed")
    total_distance = sum((x ^ y).bit_count() for x, y in zip(order, order[1:]))
    endpoint_change = order[-1].bit_count() - order[0].bit_count()
    if 2 * sum(ranks) != total_distance + endpoint_change:
        raise AssertionError("The exact positive-flux identity failed")
    return {"f": f, "name": name, "axes_most_significant_first": axes,
            "address_order": order, "exact_cut_ranks_both_kinds": ranks,
            "positive_flux": sum(ranks), "hamming_path_length": total_distance,
            "endpoint_weight_change": endpoint_change,
            "required_zeta_total_cut_rank": f * n // 2,
            "unit_minors_and_complete_factorizations": True}


def orders(max_f):
    rng = random.Random(202610091033)
    tasks = []
    for f in range(1, max_f + 1):
        n = 1 << f
        for axes in permutations(range(f)):
            order = tuple(sum(((j >> (f - 1 - t)) & 1) << b
                              for t, b in enumerate(axes)) for j in range(n))
            tasks.append((f, "axis-lexicographic", order, axes))
        shuffled = list(range(n))
        rng.shuffle(shuffled)
        for name, order in [("gray", tuple(j ^ (j >> 1) for j in range(n))),
                            ("complement-shear", tuple(j ^ ((j & 1) * (n - 2))
                                                       for j in range(n))),
                            ("seeded-arbitrary", tuple(shuffled))]:
            tasks.append((f, name, order, None))
    return tasks


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def product_controls():
    rng = random.Random(202610091034)
    cases = 0
    for f in (1, 2, 3, 4):
        n = 1 << f
        for kinds in product(("prefix", "difference"), repeat=2):
            a_order, b_order = list(range(n)), list(range(n))
            rng.shuffle(a_order)
            rng.shuffle(b_order)
            a, b = matrix(a_order, kinds[0]), matrix(b_order, kinds[1])
            a = [[x * rng.choice((-1, 1)) for x in row] for row in a]
            # The product theorem applies to all matrices; these additional
            # independent coefficient signs need not be diagonal gauges.
            ab = multiply(a, b)
            for bit in range(f):
                for prime in (2, 3, 5):
                    if rank_mod(cut(ab, bit), prime) > (rank_mod(cut(a, bit), prime)
                                                       + rank_mod(cut(b, bit), prime)):
                        raise AssertionError("Product cut subadditivity failed")
                    cases += 1
    # An omitted coordinate forces a wrong Z cut, and zero gauges are not
    # allowed: these controls reject two deliberately broadened claims.
    f = 3
    z = [[int((y & x) == y) for y in range(1 << f)] for x in range(1 << f)]
    bad = [[int((y & x) == y) * int(not (x >> 1) & 1) for y in range(1 << f)]
           for x in range(1 << f)]
    if rank_mod(cut(bad, 1), 3) == rank_mod(cut(z, 1), 3):
        raise AssertionError("The zero-gauge negative did not discriminate")
    shear = tuple(j ^ ((j & 1) * 6) for j in range(8))
    if sum(len(transition_indices(shear, b)) for b in range(3)) <= 7:
        raise AssertionError("The nonlexicographic escape negative did not discriminate")
    return {"field_product_cut_checks": cases, "zero_gauge_rejected": True,
            "universal_lex_budget_rejected_by_high_flux_order": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--bounded", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError("Positive workers are required")
    source = Path(__file__).resolve()
    original_hash = sha256(source.read_bytes()).hexdigest()
    tasks = orders(3 if args.bounded else 6)
    protocol = {"started_utc": datetime.now(timezone.utc).isoformat(),
                "source_sha256": original_hash, "workers": args.workers,
                "orders": len(tasks), "max_f": 3 if args.bounded else 6,
                "seeds": [202610091033, 202610091034], "standard_library_only": True}
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(certify_order, tasks))
    controls = product_controls()
    if sha256(source.read_bytes()).hexdigest() != original_hash:
        raise AssertionError("The source changed during execution")
    receipt = {"status": "PASS EXACT SCAN CUT-RANK CONTROLS", "orders": len(rows),
               "cut_kind_certificates": 2 * sum(r["f"] for r in rows),
               "all_size_proof_separate_from_finite_controls": True,
               "no_native_or_multiplier_exponent_claim": True, "controls": controls,
               "rows": rows}
    if args.output:
        (args.output / "certificate.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "rows"}, sort_keys=True))


if __name__ == "__main__":
    main()
