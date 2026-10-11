#!/usr/bin/env python3
"""Independently check the signed kernel of reachable one-core terminal frames.

Gamma_c is sum(x)=3*x_c. Each required terminal K_(c,a,b) additionally
imposes x_a+x_b=0. Bipartite components yield signed positive directions;
components with an odd cycle vanish. This concerns universal address spaces,
not a restriction of the payload arrays. Literal physical compilation remains
a separate obligation.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import random


def rational_rank(rows):
    rows = [[Fraction(x) for x in row] for row in rows]
    r = 0
    for j in range(len(rows[0])):
        k = next((i for i in range(r, len(rows)) if rows[i][j]), None)
        if k is None:
            continue
        rows[r], rows[k] = rows[k], rows[r]
        pivot = rows[r][j]
        rows[r] = [x / pivot for x in rows[r]]
        for i in range(r+1, len(rows)):
            if rows[i][j]:
                scale = rows[i][j]
                rows[i] = [x-scale*y for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def signed_columns(h, common, edges):
    adjacency = {i: set() for i in range(h) if i != common}
    for a, b in edges:
        assert a != b and a != common and b != common
        adjacency[a].add(b)
        adjacency[b].add(a)
    visited, columns, odd = set(), [], []
    for start in adjacency:
        if start in visited:
            continue
        colors, stack, compatible = {start: 1}, [start], True
        while stack:
            a = stack.pop()
            for b in adjacency[a]:
                if b in colors:
                    compatible &= colors[b] == -colors[a]
                else:
                    colors[b] = -colors[a]
                    stack.append(b)
        visited.update(colors)
        if compatible:
            row = [0] * h
            for i, sign in colors.items():
                row[i] = 2 * sign
            row[common] = sum(colors.values())
            columns.append(row)
        else:
            odd.append(sorted(colors))
    return columns, odd


def check(h, common, edges):
    cols, odd = signed_columns(h, common, edges)
    gamma = [1] * h
    gamma[common] = -2
    constraints = [gamma]
    for a, b in edges:
        row = [0] * h
        row[a] = row[b] = 1
        constraints.append(row)
    assert all(sum(x*y for x, y in zip(row, col)) == 0
               for row in constraints for col in cols)
    assert rational_rank(constraints) == h-len(cols)
    # Disjoint outside supports make the Gram diagonal positive. This is the
    # exact H0=I-J/9 Gram, after multiplying its entries by nine.
    for i, a in enumerate(cols):
        for j, b in enumerate(cols):
            gram9 = 9*sum(x*y for x, y in zip(a, b))-sum(a)*sum(b)
            assert gram9 == 9*sum(a[k]*b[k] for k in range(h) if k != common)
            assert (gram9 > 0) if i == j else (gram9 == 0)
    # A positive source triple containing c fits exactly when it avoids both
    # vertices of EVERY reachable target pair. No ridge-array premise enters.
    source_checks = 0
    for a, b in combinations((i for i in range(h) if i != common), 2):
        triple = {common, a, b}
        source = [int(i in triple) for i in range(h)]
        fits = all(sum(x*y for x, y in zip(row, source)) == 0 for row in constraints)
        expected = all(not ({a, b} & set(edge)) for edge in edges)
        assert fits == expected
        source_checks += 1
    return {"h": h, "common": common, "edges": [list(e) for e in edges],
            "rank": len(cols), "odd_components": odd,
            "source_lines_checked": source_checks}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--random-cases', type=int, default=64)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    rows = []
    possible = list(combinations(range(1, 5), 2))
    for bits in range(1 << len(possible)):
        rows.append(check(5, 0, [e for i, e in enumerate(possible) if bits >> i & 1]))
    rng = random.Random(args.seed)
    for h in (23, 25):
        pairs = list(combinations(range(1, h), 2))
        for i in range(args.random_cases):
            probability = (0.01, 0.04, 0.12, 0.3)[i % 4]
            rows.append(check(h, 0, [e for e in pairs if rng.random() < probability]))
    examples = [check(23, 0, edges) for edges in
                ([], [(1, 2)], [(1, 2), (1, 3)], [(1, 2), (1, 3), (2, 3)])]
    assert [x['rank'] for x in examples] == [22, 21, 20, 19]
    output = {
        'utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS EXACT REACHABLE-TERMINAL SIGNED POSITIVE KERNEL CONTROLS',
        'classification': 'EXACT FRAME LEMMA; no physical word or exponent accepted',
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'seed': args.seed, 'cases': len(rows),
        'source_lines_checked': sum(x['source_lines_checked'] for x in rows),
        'method': 'Exhaustive outside graph on four vertices plus disjoint seeded actual-dimension graphs. Independent Fraction Gaussian rank of the literal terminal constraint matrix, all integer-column inclusions, exact positive H0 Gram and every source line.',
        'theorem': 'Each connected bipartite outside component contributes one independent signed column, outside 2 sigma and core sum sigma. Odd-cycle components contribute none. Propagation along every graph edge proves completeness. On Gamma_c, x^T(I-J/9)x=sum_{i!=c}x_i^2; hence the resulting kernel is positive.',
        'monotonicity': 'A producer whose reachable terminal set contains that of a consumer has a contained kernel. This is only a necessary address-space inclusion; actual allocation, all XOR operands, chronology, source supports and dirty restoration remain physical compiler obligations.',
        'obstruction_scope': 'If the terminal-pair graph is complete on at least three excluded coordinates, its odd cycle kills those coordinates and gives no enlargement there. Sparse bipartite future graphs can retain extra signed directions. This is not a global impossibility result.',
        'examples': examples,
        'row_results_sha256': hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
        'limitations': 'No scalar DAG, retained use, physical transition, full DATA family, recurrence or kappa is inferred from this frame lemma alone.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps({k: output[k] for k in ('status', 'cases', 'source_lines_checked')}))


if __name__ == '__main__':
    main()
