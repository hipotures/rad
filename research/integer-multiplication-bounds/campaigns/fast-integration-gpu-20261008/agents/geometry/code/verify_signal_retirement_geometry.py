#!/usr/bin/env python3
"""Independent exact Gamma/K/source geometry for proposed signal retirement.

This is finite geometry evidence. It does not implement a physical retirement
gate or infer its cost from a projector rank difference.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import json
from math import lcm
from pathlib import Path
import time

from review_positive_physical_profiles import mm, projector
from decompose_common_context_profiles import pivot_run_histogram


def conjugate(P, beta):
    h = len(P)
    assert 1 - h * beta
    rows = [sum(row) for row in P]
    cols = [sum(P[i][j] for i in range(h)) for j in range(h)]
    total = sum(rows)
    eta = beta / (1 - h * beta)
    return [[P[i][j] - beta * cols[j] + eta * rows[i] - beta * eta * total
             for j in range(h)] for i in range(h)]


def pivots(P):
    h = len(P)
    M = [row[:] for row in P]
    result = []
    for i in range(h):
        nonzero = [j for j in range(h) if M[i][j]]
        if not nonzero:
            continue
        j = nonzero[-1]
        result.append([i, j])
        for k in range(i + 1, h):
            scale = M[k][j] / M[i][j]
            if scale:
                for column in range(j + 1):
                    M[k][column] -= scale * M[i][column]
    return result


def apply(P, vector):
    return [sum(x * y for x, y in zip(row, vector)) for row in P]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    started = time.monotonic()
    receipts = []
    for h in (23, 25):
        betas = (F(1, 15), F(-1, 12)) if h == 23 else (F(7, 207), F(1, 2))
        for c, a, b in ((0, 1, 2), (h - 1, 0, h - 2), (h - 3, 1, h - 2)):
            forced = 1 << c
            triple_mask = sum(1 << i for i in (c, a, b))
            gamma_symbols = [1 if i == c else i + 2 for i in range(h)]
            E_symbols = [0 if i in (a, b) else label for i, label in enumerate(gamma_symbols)]
            K_symbols = E_symbols[:]
            K_symbols[a], K_symbols[b] = h + 2, -(h + 2)
            source_symbols = [int(triple_mask >> i & 1) for i in range(h)]
            G = projector(h, forced, gamma_symbols, 'beta:0:1')
            K = projector(h, forced, K_symbols, 'beta:0:1')
            E = projector(h, forced, E_symbols, 'beta:0:1')
            S = projector(h, triple_mask, source_symbols, 'beta:0:1')
            identity = [[F(i == j) for j in range(h)] for i in range(h)]
            C = [[identity[i][j] - G[i][j] for j in range(h)] for i in range(h)]
            assert [[G[i][j] - K[i][j] for j in range(h)] for i in range(h)] == S
            assert mm(G, K) == K and mm(K, G) == K
            assert mm(K, E) == E and mm(E, K) == E
            assert mm(S, C) == [[F(0) for j in range(h)] for i in range(h)]
            assert [sum(P[i][i] for i in range(h)) for P in (G, K, E, S, C)] == [h-1,h-2,h-3,1,1]
            for beta in betas:
                mapped = {name: conjugate(P, beta) for name, P in
                          (('Gamma', G), ('K', K), ('E', E), ('source', S), ('center', C))}
                assert [[mapped['Gamma'][i][j] - mapped['K'][i][j]
                         for j in range(h)] for i in range(h)] == mapped['source']
                checked = 0
                for triple in combinations(range(h), 3):
                    coefficient = int(c in triple) - int(c in triple and a in triple) \
                        - int(c in triple and b in triple) + int(set(triple) == {c,a,b})
                    expected = int(c in triple and a not in triple and b not in triple)
                    assert coefficient == expected
                    if coefficient:
                        vector = [F(i in triple) - 3 * beta for i in range(h)]
                        assert apply(mapped['E'], vector) == vector
                        assert apply(mapped['K'], vector) == vector
                        assert apply(mapped['source'], vector) == [F(0)] * h
                        checked += 1
                source_pivots = pivots(mapped['source'])
                K_pivots = pivots(mapped['K'])
                assert len(source_pivots) == 1 and len(K_pivots) == h - 2
                den = lcm(*(x.denominator for row in mapped['source'] for x in row))
                entry = max(abs(x * den) for row in mapped['source'] for x in row)
                assert entry.denominator == 1
                receipts.append(dict(h=h, common=c, omitted=[a,b],
                    beta_numerator=beta.numerator, beta_denominator=beta.denominator,
                    original_signal_rank=h-3, retained_kernel_rank=h-2,
                    global_frame_rank=h-1, discarded_projector_rank=1,
                    scalar_coefficients_all_triples=True,
                    source_lines_checked=checked, source_annihilation=True,
                    exact_Gamma_minus_K_equals_source=True,
                    discarded_NE_pivots=source_pivots,
                    discarded_child_histogram=dict(pivot_run_histogram(source_pivots)),
                    paid_full_projection_NE_pivots=K_pivots,
                    paid_full_projection_child_histogram=dict(pivot_run_histogram(K_pivots)),
                    cleared_discarded_denominator=str(den),
                    exact_discarded_entry_bound=str(entry.numerator)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = dict(status='PASS INDEPENDENT EXACT SIGNAL-RETIREMENT GEOMETRY',
        rows=receipts, elapsed_seconds=time.monotonic()-started,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        gram_source_sha256=sha256(Path(__file__).with_name(
            'review_positive_physical_profiles.py').read_bytes()).hexdigest(),
        proof_scope='Explicit B/H0 Gram projectors and scalar source identities. '
                   'All-beta identities follow by invertible L conjugation. '
                   'Rank-one Gamma-minus-K is NOT an implementation or price '
                   'certificate for physical retirement. Arbitrary discarded '
                   'dirty components must remain preserved until uncomputation. '
                   'A new paid copy into K would use the full rank h-2 projector; '
                   'a cheaper primitive needs an explicit reversible construction '
                   'and complete resource, transition and dirty-state proof.')
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'],checks=len(receipts),
                          seconds=result['elapsed_seconds'])), flush=True)


if __name__ == '__main__':
    main()
