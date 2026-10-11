#!/usr/bin/env python3
"""Exhaustive one-variable finite-field loci; two disjoint weight-class ranges.

Field profiles and reconstructed rational representatives are discovery only.
Conjugate beta roots are identified by exact field z_out, so none are repeated.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import time

import cupy as cp
import numpy as np

HELPER = Path(__file__).with_name('gpu_basis_parameter_full_family.py')
spec = importlib.util.spec_from_file_location('field_loci_helpers', HELPER)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
base = family.base


def stamp():
    return datetime.now(timezone.utc).isoformat()


def mod(value, p):
    return value.numerator * pow(value.denominator, -1, p) % p


def lift(value, p):
    candidates = set()
    for denominator in range(1, 257):
        numerator = value * denominator % p
        if numerator > p // 2:
            numerator -= p
        if abs(numerator) <= 2048:
            candidates.add(F(numerator, denominator))
    return min(candidates, key=lambda x: (max(abs(x.numerator), x.denominator),
                                         abs(x.numerator) + x.denominator, x))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--batch', type=int, default=8192)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.device in (0, 1) and not args.output.exists()
    args.output.mkdir(parents=True)
    p = 65521
    assert family.helper.prime(p)
    excluded = {mod(x, p) for x in family.helper.excluded(25)}
    representatives = {}
    for beta in range(p):
        if beta in excluded:
            continue
        z = -beta * (9 * beta - 1) * pow(2 * (1 - 25 * beta) % p, -1, p) % p
        inside = (1 - 22 * z) * pow(3, -1, p) % p
        assert inside and z
        representatives.setdefault(z, beta)
    classes = sorted(representatives.items())
    start, end = len(classes) * args.device // 2, len(classes) * (args.device + 1) // 2
    local = classes[start:end]
    left_betas = (F(2, 39), F(-1), F(1, 51))
    cp.cuda.Device(args.device).use()
    permutation = base.upstream.baseline()
    parent = cp.asarray(permutation)
    kernel = cp.RawKernel(family.CUDA, 'search')
    score = cp.empty(args.batch, cp.float64)
    pivots = cp.empty((args.batch, 47), cp.int32)
    outperm = cp.empty((args.batch, 25, 23), cp.int32)
    output = np.lib.format.open_memmap(args.output / 'all-field-pivots.npy', mode='w+',
                                       dtype=np.int8, shape=(3, 2, len(local), 47))
    protocol = {'start_utc': stamp(), 'method_kind': 'exhaustive_finite_field_loci',
                'classification': 'DISCOVERY ONLY, not rational full-source geometry.',
                'device': args.device, 'seed': args.seed, 'batch': args.batch,
                'parameter_pairs': 3 * len(local), 'prime': p,
                'basis_family': 'L_h=I-beta_h J',
                'fixed_beta23': [base.serial_fraction(x) for x in left_betas],
                'beta25_catalogue': 'Every admissible F65521 beta, deduplicated by field z_out conjugacy.',
                'field_classes_total': len(classes), 'class_partition': [start, end],
                'source_triples': base.SOURCES, 'actual_permutation': permutation.tolist(),
                'mutations': 0, 'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'helper_sha256': hashlib.sha256(HELPER.read_bytes()).hexdigest(),
                'cuda_sha256': hashlib.sha256(family.CUDA.encode()).hexdigest(),
                'cupy': cp.__version__, 'numpy': np.__version__}
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    started = time.monotonic()
    records = []
    with (args.output / 'progress.jsonl').open('x') as progress:
        for left_index, beta23 in enumerate(left_betas):
            for source_id, source in enumerate(base.SOURCES):
                baseline = family.matrix_reference(permutation, (beta23, F(1, 21)), source)
                baseline_field = family.matrix_reference(permutation, (beta23, F(1, 21)), source, p)
                profiles = Counter()
                for first in range(0, len(local), args.batch):
                    count = min(args.batch, len(local) - first)
                    chosen = local[first:first + count]
                    inside = [(1 - 22 * z) * pow(3, -1, p) % p for z, beta in chosen]
                    inside_inv = np.asarray([pow(value, -1, p) for value in inside], np.int32)
                    outside_inv = np.asarray([pow(z, -1, p) for z, beta in chosen], np.int32)
                    y = np.where(np.asarray([i in source[1] for i in range(25)])[None, :],
                                 inside_inv[:, None], outside_inv[:, None]).astype(np.int32)
                    x = np.tile(base.modular_inverse_weights(23, beta23, source[0], p), (count, 1)).astype(np.int32)
                    kernel((count,), (128,), (parent, cp.asarray(x), cp.asarray(y), np.int32(p),
                                              np.uint32(args.seed), np.uint32(first), np.int32(0),
                                              score, pivots, outperm))
                    cp.cuda.Stream.null.synchronize()
                    actual = pivots[:count].get().astype(np.int8)
                    if first == 0:
                        reference = family.matrix_reference(permutation, (beta23, F(chosen[0][1])), source, p)
                        assert actual[0].tolist() == reference, 'Independent first field-source control failed'
                    output[left_index, source_id, first:first + count] = actual
                    for row in actual:
                        profiles[tuple(int(x) for x in row)] += 1
                    progress.write(json.dumps({'utc': stamp(), 'attempts': (2 * left_index + source_id) * len(local) + first + count,
                                               'fixed_beta23_index': left_index, 'source_id': source_id,
                                               'classes_completed': first + count,
                                               'elapsed_seconds': time.monotonic() - started}) + '\n')
                    progress.flush()
                dominant = max(profiles, key=profiles.get)
                exceptions = []
                for index, row in enumerate(output[left_index, source_id]):
                    if tuple(row) == dominant:
                        continue
                    z, field_beta = local[index]
                    rational_beta = lift(field_beta, p)
                    q_pivots = None
                    if rational_beta not in family.helper.excluded(25):
                        q_pivots = family.matrix_reference(permutation, (beta23, rational_beta), source)
                    exceptions.append({'class_index': start + index, 'field_z_out25': z,
                                       'field_beta25': field_beta, 'rational_beta25': base.serial_fraction(rational_beta),
                                       'field_pivots': row.tolist(), 'Q_pivots': q_pivots,
                                       'field_matches_reconstructed_Q': q_pivots == row.tolist()})
                records.append({'beta23': base.serial_fraction(beta23), 'source_id': source_id,
                                'source_triples': source, 'baseline_Q_pivots': baseline,
                                'baseline_field_pivots': baseline_field,
                                'dominant_field_pivots': list(dominant),
                                'profile_classes': [{'pivots': list(key), 'count': count}
                                                    for key, count in profiles.items()],
                                'exceptional_field_classes': exceptions})
    output.flush()
    artifact = args.output / 'all-field-pivots.npy'
    summary = {**protocol, 'finish_utc': stamp(), 'status': 'COMPLETE EXHAUSTIVE FIELD LOCI DISCOVERY',
               'attempts': 6 * len(local), 'elapsed_seconds': time.monotonic() - started,
               'records': records,
               'binary_artifact': {'path': str(artifact), 'bytes': artifact.stat().st_size,
                                   'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
                                   'recovery': 'Deterministic fixed-prime class enumeration and GPU profile replay.'}}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'status': summary['status'], 'device': args.device,
                      'classes': len(local), 'attempts': summary['attempts'],
                      'exceptions_per_fixture': [len(x['exceptional_field_classes']) for x in records]}), flush=True)


if __name__ == '__main__':
    main()
