#!/usr/bin/env python3
"""Falsify modular aliases by exact witness-minor quadratic reconstruction."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
from functools import reduce
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

from gpu_signed_corner_loci import read_binary, base_matrix, actual_matrix, cpu_pivots

GEOMETRY = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
sys.path.insert(0, str(GEOMETRY))
from review_positive_physical_profiles import projector


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def determinant(matrix):
    rows = [row[:] for row in matrix]
    n, value = len(rows), F(1)
    for i in range(n):
        pivot = next((j for j in range(i, n) if rows[j][i]), None)
        if pivot is None:
            return F(0)
        if pivot != i:
            rows[i], rows[pivot] = rows[pivot], rows[i]
            value = -value
        d = rows[i][i]
        value *= d
        for k in range(i + 1, n):
            scale = rows[k][i] / d
            if scale:
                for j in range(i + 1, n):
                    rows[k][j] -= scale * rows[i][j]
                rows[k][i] = F(0)
    return value


def similarity(matrix, beta):
    h = len(matrix)
    eta = beta / (1 - h * beta)
    rs = list(map(sum, matrix))
    cs = [sum(matrix[i][j] for i in range(h)) for j in range(h)]
    total = sum(rs)
    return [[matrix[i][j] - beta * cs[j] + eta * rs[i] - beta * eta * total
             for j in range(h)] for i in range(h)]


def corner_rank(matrix, rows, first_col):
    sub = [r[first_col:] for r in matrix[:rows]]
    rank = 0
    if not sub or not sub[0]:
        return 0
    for col in range(len(sub[0])):
        pivot = next((i for i in range(rank, len(sub)) if sub[i][col]), None)
        if pivot is None:
            continue
        sub[rank], sub[pivot] = sub[pivot], sub[rank]
        d = sub[rank][col]
        for k in range(rank + 1, len(sub)):
            scale = sub[k][col] / d
            if scale:
                for j in range(col, len(sub[0])):
                    sub[k][j] -= scale * sub[rank][j]
        rank += 1
        if rank == len(sub):
            break
    return rank


def roots(coefficients):
    a, b, c = coefficients
    den = math.lcm(*(x.denominator for x in coefficients))
    ints = [int(x * den) for x in coefficients]
    g = reduce(math.gcd, map(abs, ints))
    assert g
    ints = [x // g for x in ints]
    if next(x for x in reversed(ints) if x) < 0:
        ints = [-x for x in ints]
    ai, bi, ci = ints
    if ci:
        discriminant = bi * bi - 4 * ai * ci
        if discriminant < 0 or math.isqrt(discriminant) ** 2 != discriminant:
            return ints, discriminant, []
        root = math.isqrt(discriminant)
        return ints, discriminant, sorted({F(-bi + root, 2 * ci), F(-bi - root, 2 * ci)})
    if bi:
        return ints, None, [F(-ai, bi)]
    return ints, None, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--graph-receipt', type=Path, required=True)
    ap.add_argument('--reference-beta', type=F, required=True)
    ap.add_argument('--fields', type=int, default=8)
    ap.add_argument('--minors', type=int, default=2)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    protocol = json.loads((args.run / 'protocol.json').read_text())
    summary = json.loads((args.run / 'summary.json').read_text())
    graph = json.loads(args.graph_receipt.read_text())
    binary = Path(graph['profile_transition_path'])
    assert digest(binary) == graph['profile_transition_sha256'] == protocol['transition_sha256']
    assert graph['word_sha256'] == protocol['word_sha256']
    h, v, roles, singles, mass, loss, frames, transitions = read_binary(binary)
    selected = [tuple(x) for x in protocol['selected_transitions']]
    assert all(row in set(transitions) for row in selected)
    p = protocol['prime']
    beta_values = np.load(args.run / 'field-beta-values.npy')
    scores = np.load(args.run / 'sample-moments.npy')
    baseline = summary['control_sample_moment']
    hits = [int(i) for i in np.argsort(scores) if scores[i] < baseline - 1e-8][:args.fields]
    excluded = {F(0), F(1, h), F(1, 3), F(1, 9), F(2, 3 * (h - 3)),
                F(h - 7, 3 * (h - 3)), F(2, 3 * (h - 1))}
    modular_cache, exact_cache, reference_cache = {}, {}, {}

    def modular(fid):
        if fid not in modular_cache:
            modular_cache[fid] = base_matrix(frames[fid], h, p)
        return modular_cache[fid]

    def exact(fid):
        if fid not in exact_cache:
            if fid < 2:
                exact_cache[fid] = [[F(i == j and fid == 1) for j in range(h)] for i in range(h)]
            else:
                rank, forced, symbols = frames[fid]
                exact_cache[fid] = projector(h, forced, symbols, 'beta:0:1')
        return exact_cache[fid]

    observations = []
    started = time.monotonic()
    for hit in hits:
        field_beta = int(beta_values[hit])
        count = 0
        for ordinal, (a, b, frequency) in enumerate(selected):
            modular_difference = (modular(b) - modular(a)) % p
            if ordinal not in reference_cache:
                reference_cache[ordinal] = cpu_pivots(actual_matrix(modular_difference, args.reference_beta, h, p), p)
            ref = reference_cache[ordinal]
            new = cpu_pivots(actual_matrix(modular_difference, F(field_beta), h, p), p)
            if ref == new:
                continue
            reference_corner = np.cumsum(np.asarray(ref)[:, None] >= np.arange(h)[None, :], axis=0)
            observed_corner = np.cumsum(np.asarray(new)[:, None] >= np.arange(h)[None, :], axis=0)
            choices = np.argwhere((observed_corner < reference_corner) & (reference_corner >= 2))
            if not len(choices):
                continue
            last_row, first_col = map(int, choices[0])
            witness = [(i, j) for i, j in enumerate(ref) if i <= last_row and j >= first_col]
            rows, cols = zip(*witness)
            dimension = len(witness)
            E, G = exact(a), exact(b)
            Q = [[y - x for x, y in zip(u, w)] for u, w in zip(E, G)]

            def value(beta):
                M = similarity(Q, beta)
                return (1 - h * beta) * determinant([[M[i][j] for j in cols] for i in rows])

            f0, f1, fm1 = value(F(0)), value(F(1)), value(F(-1))
            coefficients = [f0, (f1 - fm1) / 2, (f1 + fm1 - 2 * f0) / 2]
            assert value(F(2)) == coefficients[0] + 2 * coefficients[1] + 4 * coefficients[2]
            assert value(args.reference_beta) != 0
            assert all(x.denominator % p for x in coefficients)
            evaluated = sum((x.numerator * pow(x.denominator % p, -1, p) % p)
                            * pow(field_beta, k, p) for k, x in enumerate(coefficients)) % p
            assert evaluated == 0
            integer_coefficients, discriminant, candidates = roots(coefficients)
            matched = []
            for beta in candidates:
                if beta in excluded or not beta.denominator % p:
                    continue
                if beta.numerator * pow(beta.denominator % p, -1, p) % p != field_beta:
                    continue
                rank = corner_rank(similarity(Q, beta), last_row + 1, first_col)
                matched.append({'beta': str(beta), 'exact_corner_rank': rank,
                                'reference_corner_rank': dimension,
                                'actual_rational_rank_drop': rank < dimension})
            observation = {'field_beta': field_beta, 'field_sample_gain': baseline - float(scores[hit]),
                           'selected_transition_ordinal': ordinal, 'a': a, 'b': b, 'count': frequency,
                           'corner_rows': last_row + 1, 'corner_first_column': first_col,
                           'witness_rows': list(rows), 'witness_columns': list(cols),
                           'minor_size': dimension, 'primitive_integer_coefficients_constant_linear_quadratic': integer_coefficients,
                           'discriminant': discriminant, 'all_exact_rational_roots': list(map(str, candidates)),
                           'matching_admissible_roots': matched,
                           'interpolation_beta0_1_minus1_and_independent_beta2': 'PASS',
                           'field_root_checked_against_exact_coefficients': True,
                           'classification': 'EXACT LOCAL RANK-DROP CANDIDATE' if any(r['actual_rational_rank_drop'] for r in matched)
                                             else 'REJECTED MODULAR ALIAS FOR THIS WITNESS'}
            observations.append(observation)
            count += 1
            print(json.dumps(observation), flush=True)
            if count == args.minors:
                break
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'h': h,
              'status': 'COMPLETE INDEPENDENT RATIONAL CORNER WITNESS QUADRATIC EXTRACTION',
              'source_sha256': digest(__file__), 'gram_source_sha256': digest(GEOMETRY / 'review_positive_physical_profiles.py'),
              'graph_receipt_sha256': digest(args.graph_receipt), 'word_sha256': graph['word_sha256'],
              'transition_sha256': digest(binary), 'run_protocol_sha256': digest(args.run / 'protocol.json'),
              'run_summary_sha256': digest(args.run / 'summary.json'),
              'field_scores_sha256': digest(args.run / 'sample-moments.npy'),
              'field_values_sha256': digest(args.run / 'field-beta-values.npy'),
              'reference_beta': str(args.reference_beta), 'fields_inspected': len(hits),
              'observations': observations, 'elapsed_seconds': time.monotonic() - started,
              'scope': 'Exact sampled witness minors and matching rational corner drops only. A root of one minor need not drop the whole corner; that rank is checked separately. Complete local native CRT, all-source DATA, actual word interfaces and strict recurrence assembly remain required. Field congruence representatives are not accepted as rational roots.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
