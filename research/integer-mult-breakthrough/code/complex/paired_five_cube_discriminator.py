#!/usr/bin/env python3
"""Exact scalar-bank and center-span discriminator for paired odd-weight cubes.

This constructs a paid in-place dyadic word for each parity block. Address
frame lifts, the complete side chronology and its child histogram are not
supplied here. Role-bank scalar butterflies are not recursive address C calls.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb, expm1, factorial, log
from pathlib import Path
import time


def basis(rows):
    pivots = {}
    for value in rows:
        for pivot in sorted(pivots, reverse=True):
            if value & (1 << pivot):
                value ^= pivots[pivot]
        if value:
            pivot = value.bit_length() - 1
            for old in list(pivots):
                if pivots[old] & (1 << pivot):
                    pivots[old] ^= value
            pivots[pivot] = value
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def kernel(k, intersection):
    r = (k - 1) // 2
    value = Q(1)
    for j in range(r):
        value *= Q(intersection - 1, 2) - j
    return value / factorial(r)


def selector(u, k, parity):
    return u | (((u.bit_count() & 1) ^ parity) << (k - 1))


def cube_label(bits, k):
    return sum(1 << (2 * j + ((bits >> j) & 1)) for j in range(k))


def hadamard_word(n):
    word = []
    for coordinate in range(n):
        for a in range(1 << n):
            if a & (1 << coordinate):
                continue
            b = a | (1 << coordinate)
            # (a,b) becomes (a+b,a-b), including the nonunit scale.
            word.extend((('add', a, b, Q(1)), ('scale', b, b, Q(-2)),
                         ('add', b, a, Q(1))))
    return word


def parity_word(k):
    n, N, r = k - 1, 1 << (k - 1), (k - 1) // 2
    H = hadamard_word(n)
    return H + [('scale', a, a, Q(-1)) for a in range(N) if a.bit_count() <= r] + H + [
        ('scale', a, a, Q(1, N)) for a in range(N)]


def inverse_word(word):
    return [(kind, target, source, -coefficient if kind == 'add' else 1 / coefficient)
            for kind, target, source, coefficient in reversed(word)]


def apply(word, values):
    values = list(values)
    for kind, target, source, coefficient in word:
        temporary = coefficient * values[source]
        values[target] = values[target] + temporary if kind == 'add' else temporary
    return values


def literal_matrix_and_prefix(word, N):
    rows = [[Q(i == j) for j in range(N)] for i in range(N)]
    maximum_l1, fractional_bits = Q(1), 0

    def observe(row):
        nonlocal maximum_l1, fractional_bits
        maximum_l1 = max(maximum_l1, sum(abs(value) for value in row))
        for value in row:
            denominator = value.denominator
            if denominator & (denominator - 1):
                raise AssertionError('a scalar prefix introduced an odd denominator')
            fractional_bits = max(fractional_bits, denominator.bit_length() - 1)

    for kind, target, source, coefficient in word:
        temporary = [coefficient * value for value in rows[source]]
        observe(temporary)
        rows[target] = [a + b for a, b in zip(rows[target], temporary)] if kind == 'add' else temporary
        observe(rows[target])
    return rows, dict(row_l1=str(maximum_l1), fractional_bits=fractional_bits,
                      includes_all_multiplication_temporaries=True)


def scalar_word_case(k):
    n, N = k - 1, 1 << (k - 1)
    word = parity_word(k)
    observed, prefix = literal_matrix_and_prefix(word, N)
    inverse, inverse_prefix = literal_matrix_and_prefix(inverse_word(word), N)
    expected = [[-kernel(k, k - (selector(a, k, 1) ^ selector(b, k, 0)).bit_count())
                 for b in range(N)] for a in range(N)]
    if observed != expected or inverse != expected:
        raise AssertionError('literal original-bank parity mixer or inverse differs from the cube correction')
    for i in range(N):
        for j in range(N):
            if sum(observed[i][t] * observed[j][t] for t in range(N)) != (i == j):
                raise AssertionError('the parity block is not exactly orthogonal')
    # Four arbitrary dirty Gaussian fields are bound component by component.
    for field in range(4):
        for component in range(2):
            values = [Q(((i + 1) * (field + 3) * (component + 2)) % 31 - 15, 8) for i in range(N)]
            mixed = apply(word, values)
            if mixed != [sum(c * x for c, x in zip(row, values)) for row in expected]:
                raise AssertionError('a complete Gaussian payload field was not transformed')
            if apply(inverse_word(word), mixed) != values:
                raise AssertionError('the mutable original source field did not return exactly')
    even_labels = [cube_label(selector(a, k, 0), k) for a in range(N)]
    odd_labels = [cube_label(selector(a, k, 1), k) for a in range(N)]
    U = basis(even_labels)
    if len(U) != k or any((a & b).bit_count() & 1 for a in U for b in odd_labels):
        raise AssertionError('the original parity frame does not lie in opposite target caps')
    gram = basis(sum(((a & b).bit_count() & 1) << j for j, b in enumerate(U)) for a in U)
    if len(gram) != 1:
        raise AssertionError('the original parity span has the wrong radical')
    flat = len({abs(c) for row in observed for c in row if c}) == 1
    if k == 5 and flat:
        raise AssertionError('the five-cube unexpectedly passed a flat Clifford-column test')
    bad = [event for event in word if not (event[0] == 'scale' and event[3] == Q(1, N))]
    wrong, unused = literal_matrix_and_prefix(bad, N)
    if wrong == expected:
        raise AssertionError('omitted normalization negative failed to reject')
    return dict(k=k, banks_per_parity=N, gates_per_parity=len(word),
                forward_and_inverse_gates_per_source=str(Q(2 * len(word), N)),
                additions_per_parity=sum(event[0] == 'add' for event in word),
                scales_per_parity=sum(event[0] == 'scale' for event in word),
                prefix=prefix, inverse_prefix=inverse_prefix,
                row_l1=str(sum(abs(c) for c in observed[0])),
                nonzero_amplitudes=sorted({str(abs(c)) for row in observed for c in row if c}),
                flat_nonzero_columns=flat, exact_scalar_columns=2 * N * N,
                dirty_gaussian_components=8 * N, all_sources_return=True,
                common_parity_frame_rank=k, common_parity_radical=k - 1,
                omitted_normalization_rejected=True,
                schedule='Both parity blocks stay in their own identical actual source frame; their output rows are assigned to opposite target caps. Apply the inverse within original slots at the common full frame before source cleanup.',
                scope='Exact fixed scalar-bank word and parity geometry; no native frame/record execution or complete side word')


def labels(p, k):
    return [sum(1 << (2 * coordinate + ((bits >> j) & 1))
                for j, coordinate in enumerate(selected))
            for selected in combinations(range(p), k) for bits in range(1 << k)]


def center_case(task):
    p, complete_matrix = task
    h, k = 2 * p, 5
    sources = labels(p, k)
    ranks, radical = Counter(), Counter()
    all_centers = [(i, j) for i in range(h) for j in range(i + 1, h) if i // 2 != j // 2]
    sample = []
    for i, j in all_centers:
        star = basis(source for source in sources if source & (1 << i) and source & (1 << j))
        fixed = (1 << i) | (1 << j)
        outside = [c for c in range(h) if c not in (i, i ^ 1, j, j ^ 1)]
        expected = basis((1 << c) | fixed for c in outside)
        if star != expected or len(star) != h - 4:
            raise AssertionError('a nonpartner pair star has the wrong exact source span')
        gram = basis(sum(((a & b).bit_count() & 1) << t for t, b in enumerate(star)) for a in star)
        ranks[len(star)] += 1
        radical[len(star) - len(gram)] += 1
        if len(gram) != h - 4:
            raise AssertionError('paired five-subset center is unexpectedly degenerate')
        if len(sample) < 2:
            sample.append(dict(coordinates=[i, j], basis=list(star)))
    # Integer numerator over 160: 1/10, -9/160 or 3/80.
    targets = sources if complete_matrix else sources[:min(32, len(sources))]
    decoded = 0
    source_pairs = [[(i, j) for i, j in combinations([c for c in range(h) if S & (1 << c)], 2)]
                    for S in sources]
    for T in targets:
        for S, pairs in zip(sources, source_pairs):
            numerator = sum(16 if T & (1 << i) and T & (1 << j)
                            else -9 if bool(T & (1 << i)) != bool(T & (1 << j))
                            else 6 for i, j in pairs)
            if numerator != 20 * ((T & S).bit_count() - 1) * ((T & S).bit_count() - 3):
                raise AssertionError('the pair-only central decoder differs from f5')
            decoded += 1
    return dict(p=p, h=h, k=k, v=len(sources), centers=len(all_centers),
                center_rank_histogram=dict(ranks), center_radical_histogram=dict(radical),
                copied_center_loss=len(all_centers) * (h - 4),
                center_decoder_denominator=160, new_fixed_odd_divisor=5,
                exact_decoder_entries=decoded, complete_central_matrix=complete_matrix,
                representative_centers=sample,
                deficit_if_shared_ledger_holds=2 * len(sources) - 3 * len(all_centers) * (h - 4),
                source_geodesic_widths=[k - 1, h - k - 1, 1],
                scope='Exact pair-star spans and central scalar decoder. Copied-center, side and whole shared-core chronology remain hypotheses.')


def capacity_rows():
    result = []
    for p in (8, 9, 10, 11, 12, 14, 16):
        h, v, q = 2 * p, 32 * comb(p, 5), 2 * p * (p - 1)
        loss, m = q * (h - 4), 3 * h
        deficit = 2 * v - 3 * loss
        # NECESSARY ONLY: every child r<=h-1 would imply
        # Phi(1-b) >= rank/(mW) * (m/(h-1))**b.
        # This bound supplies no complete attainable distribution.
        for b in (0.0001, 0.001, 0.01):
            allowance = deficit / (m * v * (-expm1(-b * log(m / (h - 1))))) - 2
            result.append(dict(p=p, h=h, v=v, centers=q, loss=loss, deficit=deficit,
                               target_b=b, necessary_max_physical_R_over_v=allowance,
                               hypothesis='A completed three-orthogonal-block ledger with W=2v+R, loss=q(h-4), and maximum child<=h-1; scalar K words add fixed paid L/G work but no extra roles.',
                               scope='Floating sensitivity and necessary capacity ceiling only; not a child moment certificate or multiplier kappa'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    source = Path(__file__)
    original = source.read_bytes()
    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    words = [scalar_word_case(k) for k in (3, 5)]
    tasks = [(7, True)] if args.bounded else [(7, True), (8, False), (9, False), (12, False)]
    if args.workers == 1:
        centers = [center_case(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            centers = list(pool.map(center_case, tasks))
    if source.read_bytes() != original:
        raise AssertionError('source changed during execution')
    result = dict(status='PASS exact paired-five scalar-bank/center discriminator',
                  source_sha256=sha256(original).hexdigest(), started_utc=started_utc,
                  completed_utc=datetime.now(timezone.utc).isoformat(),
                  seconds=time.monotonic() - started, workers=args.workers,
                  bounded=args.bounded, scalar_words=words, center_cases=centers,
                  capacity_sensitivity=capacity_rows(),
                  scope='Finite scalar words and spans; capacity is explicitly hypothetical and necessary only. No whole side/native supplier, child profile or kappa claim.')
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], seconds=result['seconds'],
                          center_cases=len(centers), decoder_entries=sum(c['exact_decoder_entries'] for c in centers),
                          scalar_columns=sum(c['exact_scalar_columns'] for c in words))), flush=True)


if __name__ == '__main__':
    main()
