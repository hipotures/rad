#!/usr/bin/env python3
"""Exact pair-star scalar/frame and central-rank discriminator.

This small algebraic control does not compile a promoted movement motif.
The negative concerns the declared three-stage central/monotone-target
family; altered data-label chronology remains outside its scope.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from pathlib import Path
import random
import time

from downstream_binary_shear_interface import independent, multiply
from downstream_gaussian import require


def rank(rows):
    return len(independent(rows))


def identity(n):
    return [1 << j for j in range(n)]


def xor_matrix(a, b):
    return [x ^ y for x, y in zip(a, b)]


def line_projector(vector, n):
    require(vector.bit_count() & 1, 'Pair direction is not norm one')
    return [vector if vector >> j & 1 else 0 for j in range(n)]


def pair_vectors(h):
    pairs = list(combinations(range(h), 2))
    if h & 1:
        n = h
        vectors = [(1 << n) - 1 ^ (1 << a) ^ (1 << b) for a, b in pairs]
        encoding = 'Orthonormal z_j=e0+sum_(k!=j)e_k in the nondegenerate pair span'
    else:
        n = h - 1
        vectors = [(1 << (b - 1)) if a == 0 else
                   ((1 << n) - 1 ^ (1 << (a - 1)) ^ (1 << (b - 1)))
                   for a, b in pairs]
        encoding = 'Quotient by the ground-all-ones radical, in the orthonormal star0 basis'
    return pairs, vectors, n, encoding


def scalar_control(h, rng):
    pairs = list(combinations(range(h), 2))
    v = len(pairs)
    E = [[int(len(set(a) & set(b)) == 1) for b in pairs] for a in pairs]
    entries = 0
    for i, a in enumerate(pairs):
        for j, b in enumerate(pairs):
            require(Q(len(set(a) & set(b)), 2) - Q(E[i][j], 2) == int(i == j),
                    'Pair central-minus-E1 identity differs')
            entries += 1
    size = 3 * v + h
    probes = [[Q(int(k == j)) for k in range(size)] for j in range(size)]
    probes += [[Q(rng.randrange(-4, 5)) for _ in range(size)] for _ in range(8)]
    for data in probes:
        x, y, z, c = (list(data[:v]), list(data[v:2*v]),
                      list(data[2*v:3*v]), list(data[3*v:]))
        before = [list(x), list(y), list(z), list(c)]

        def scatter(sign):
            for k, (a, b) in enumerate(pairs):
                y[k] += sign * Q(c[a] + c[b], 2)

        def inject(sign):
            for k in range(v):
                y[k] -= sign * z[k] / 2

        def gather(sign):
            for k, (a, b) in enumerate(pairs):
                c[a] += sign * x[k]
                c[b] += sign * x[k]

        def copy(sign):
            for i in range(v):
                z[i] += sign * sum(E[i][j] * x[j] for j in range(v))

        inject(-1); scatter(-1); copy(1); gather(1)
        scatter(1); inject(1); gather(-1); copy(-1)
        require(x == before[0] and y == [a + b for a, b in zip(before[1], before[0])]
                and z == before[2] and c == before[3], 'Pair dirty scalar invocation/restoration differs')
    return dict(ground=h, pairs=v, scalar_identity_entries=entries,
                complete_dirty_basis_probes=size, additional_signed_probes=8,
                side_copy_scope='Reference E1 matrix; no finite positive circuit is claimed by this test')


def label_control(h):
    pairs, vectors, n, encoding = pair_vectors(h)
    original = [1 | (1 << (a + 1)) | (1 << (b + 1)) for a, b in pairs]
    basis = independent(original)
    gram = [sum(((a & b).bit_count() & 1) << j for j, b in enumerate(basis)) for a in basis]
    require(len(basis) == h and rank(gram) == (h if h & 1 else h - 1),
            'Augmented pair span/radical dimensions differ')
    require(rank(vectors) == n, 'Pair quotient/span does not fill its declared ambient space')
    orthogonalities = helper_containments = center_edges = 0
    center_rank_sum = 0
    full = identity(n)
    kernels = [xor_matrix(full, line_projector(vector, n)) for vector in vectors]
    for i, pair in enumerate(pairs):
        require(vectors[i].bit_count() & 1, 'Pair line is degenerate')
        for j, other in enumerate(pairs):
            expected = (1 + len(set(pair) & set(other))) & 1
            require(((vectors[i] & vectors[j]).bit_count() & 1) == expected,
                    'Pair intersection Gram formula differs')
            orthogonalities += 1
    for center in range(h):
        incident = [i for i, pair in enumerate(pairs) if center in pair]
        require(len(incident) == h - 1 and rank([vectors[i] for i in incident]) == h - 1,
                'Star is not an independent orthonormal family')
        states = [full] + [kernels[i] for i in incident] + [full]
        images = []
        local_rank = 0
        delta_sum = [0] * n
        for old, new in zip(states, states[1:]):
            delta = xor_matrix(old, new)
            require(all((delta[i] >> j & 1) == (delta[j] >> i & 1)
                        for i in range(n) for j in range(n)), 'Center difference lost symmetry')
            local_rank += rank(delta)
            images.extend(delta)
            delta_sum = xor_matrix(delta_sum, delta)
            center_edges += 1
        require(not any(delta_sum), 'Center phase path is not closed')
        require(local_rank == 2 * (h - 1) and rank(images) == h - 1,
                'Joint pair scatter does not attain the central closed-path bound')
        center_rank_sum += local_rank
    for i, (a, b) in enumerate(pairs):
        for center in (a, b):
            neighbors = [j for j, pair in enumerate(pairs) if center in pair and pair != (a, b)]
            partial = [0] * n
            for j in neighbors:
                partial = xor_matrix(partial, line_projector(vectors[j], n))
            require(rank(partial) == h - 2 and multiply(kernels[i], partial) == partial,
                    'Star-minus-self helper is not in the target kernel')
            require(rank(xor_matrix(partial, kernels[i])) == n - h + 1,
                    'Final helper-to-target residual has wrong rank')
            helper_containments += 1
    return dict(ground=h, pairs=len(pairs), ambient_dimension=n, augmented_span_dimension=h,
                augmented_gram_rank=rank(gram), encoding=encoding,
                intersection_gram_entries=orthogonalities, target_helper_containments=helper_containments,
                explicit_center_edges=center_edges, total_local_center_rank=center_rank_sum,
                exact_effective_local_center_loss=center_rank_sum // 2,
                center_lower_bound=h * (h - 1), minimum_attained=True)


def closed_symmetric_control(rng):
    cases = 0
    for n in range(1, 9):
        for _ in range(24):
            matrices = []
            for _ in range(rng.randrange(2, 7)):
                rows = [0] * n
                for i in range(n):
                    for j in range(i, n):
                        if rng.randrange(2):
                            rows[i] |= 1 << j
                            rows[j] |= 1 << i
                matrices.append(rows)
            tail = [0] * n
            for rows in matrices:
                tail = xor_matrix(tail, rows)
            matrices.append(tail)
            total_rank = sum(rank(rows) for rows in matrices)
            joint_dimension = rank([row for rows in matrices for row in rows])
            require(total_rank >= 2 * joint_dimension, 'Closed symmetric rank lemma control failed')
            cases += 1
    return dict(exact_closed_symmetric_paths=cases,
                statement='sum rank(Delta_i) >= 2 dim span(image Delta_i), when symmetric Delta_i sum to zero',
                proof='Factor Delta_i=U_i G_i U_i^T; concatenated U has totally isotropic row space in nondegenerate block-diagonal G')


def count_control():
    rows = []
    for h in range(3, 65):
        v = h * (h - 1) // 2
        local_loss = h * (h - 1)
        N, L = v ** 3, 3 * v * v * local_loss
        D = 2 * N - 2 * L
        require(D == -5 * v * v * h * (h - 1) and D < 0,
                'Favorable pair central deficit is unexpectedly positive')
        rows.append(dict(ground=h, v=v, ambient_dimension=h if h & 1 else h - 1,
                         N=N, minimum_local_center_loss=local_loss, L=L, D=D))
    return dict(exact_ground_controls=rows,
                declared_family='Three tensor stages, h incidence centers per invocation, targets remain inside their final pair-line kernels during scatter',
                result='Even the minimum attainable central path charge exceeds the full 2N endpoint saving',
                scope='Changed target chronology, altered central scalar representation and other motifs are not ruled out')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    require(not a.output.exists(), 'Use a fresh output path')
    started = time.monotonic()
    rng = random.Random(202610080405)
    result = dict(status='PASS PAIR SCALAR/FRAME CONTROLS; DECLARED CENTRAL FAMILY HAS NEGATIVE DEFICIT',
                  campaign='20261007T222521Z', campaign_start='2026-10-07T22:25:21Z',
                  campaign_original_deadline='2026-10-08T08:25:21Z', campaign_deadline='2026-10-08T10:00:00Z',
                  generated_at=datetime.now(timezone.utc).isoformat(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  dependency_sha256={name:hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                                     for name in ('downstream_binary_shear_interface.py', 'downstream_gaussian.py')},
                  scalar=[scalar_control(h, rng) for h in range(3, 9)],
                  labels=[label_control(h) for h in range(3, 15)],
                  closed_symmetric_rank=closed_symmetric_control(rng), count_discriminator=count_control(),
                  scope='Small exact hypothesis discriminator only; no promoted finite circuit, movement primitive or kappa',
                  elapsed_seconds=time.monotonic() - started)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], 'dirty basis', sum(x['complete_dirty_basis_probes'] for x in result['scalar']),
          'label grounds', len(result['labels']), 'closed paths', result['closed_symmetric_rank']['exact_closed_symmetric_paths'], flush=True)


if __name__ == '__main__':
    main()
