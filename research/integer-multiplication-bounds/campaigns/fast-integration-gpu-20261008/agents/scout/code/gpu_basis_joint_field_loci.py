#!/usr/bin/env python3
"""Exhaustive joint finite-field source-weight classes at pinned PR54 order.

Field cuts are discovery. Only bounded rational reconstructions with matching
exact Q pivots are retained as rational samples; no full-family claim follows.
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

HELPER = Path(__file__).with_name('gpu_basis_field_loci.py')
spec = importlib.util.spec_from_file_location('joint_field_helpers', HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
family, base = helper.family, helper.base


def reconstruct(a, p, bound=180):
    r0, r1, t0, t1 = p, a, 0, 1
    while abs(r1) > bound:
        q = r0 // r1
        r0, r1, t0, t1 = r1, r0 - q * r1, t1, t0 - q * t1
    if t1 < 0:
        r1, t1 = -r1, -t1
    if not 0 < t1 <= bound or math.gcd(r1, t1) != 1 or (r1 - a * t1) % p:
        return None
    return F(r1, t1)


def catalogue(h, p, k):
    excluded = {helper.mod(x, p) for x in family.helper.excluded(h)}
    representatives = {}
    for beta in range(p):
        if beta in excluded:
            continue
        z = -beta * (9 * beta - 1) * pow(2 * (1 - h * beta) % p, -1, p) % p
        inside = (1 - (h - 3) * z) * pow(3, -1, p) % p
        assert inside and z
        representatives.setdefault(z, beta)
    classes = sorted(representatives.items())
    lifted = []
    for z, beta in classes:
        value = reconstruct(z, p)
        choices = []
        if value is not None:
            discriminant = (1 + 2 * h * value) ** 2 - 72 * value
            if discriminant >= 0:
                n, d = math.isqrt(discriminant.numerator), math.isqrt(discriminant.denominator)
                if n * n == discriminant.numerator and d * d == discriminant.denominator:
                    root = F(n, d)
                    choices = [x for x in ((1 + 2 * h * value + root) / 18,
                                          (1 + 2 * h * value - root) / 18)
                               if x not in family.helper.excluded(h)]
                    choices.sort(key=lambda x: (max(abs(x.numerator), x.denominator), x))
        lifted.append(choices[0] if choices else None)
    values = [[pow((1 - (h - 3) * z) * pow(3, -1, p) % p, -1, p),
               pow(z, -1, p)] for z, beta in classes]
    vectors = np.asarray([[[(inside if i in source[k] else outside) for i in range(h)]
                            for source in base.SOURCES]
                           for inside, outside in values], dtype=np.int32)
    return classes, lifted, vectors.reshape(-1, h)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--batch', type=int, default=8192)
    parser.add_argument('--pr54-snapshot', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.device in (0, 1) and args.batch % 2 == 0 and not args.output.exists()
    args.output.mkdir(parents=True)
    p = 65521
    assert family.helper.prime(p)
    cp.cuda.Device(args.device).use()
    cp.get_default_memory_pool().set_limit(size=8 * 1024 ** 3)
    classes, lifts, tables = [], [], []
    for k, h in enumerate((23, 25)):
        catalogue_classes, lifted, vector = catalogue(h, p, k)
        classes.append(catalogue_classes)
        lifts.append(lifted)
        tables.append(cp.asarray(vector))
    sizes = [len(x) for x in classes]
    total = sizes[0] * sizes[1]
    start, end = total * args.device // 2, total * (args.device + 1) // 2
    permutation = base.upstream.baseline()
    rows = [int(permutation[i % 25, i // 25]) for i in range(47)]
    columns = [int(permutation[(528 + j) % 25, (528 + j) // 25]) for j in range(47)]
    assert rows == list(range(23)) + [22] + list(range(23))
    assert columns == list(range(23)) + [0] + list(range(23))
    pr54_source = args.pr54_snapshot / 'research/copied-fixed/data_recovery.py'
    assert pr54_source.is_file() and args.pr54_snapshot.name.endswith('84eb0b067741dc2690da837743fda06d133da865')
    parent = cp.asarray(permutation)
    kernel = cp.RawKernel(family.CUDA, 'search')
    score = cp.empty(args.batch, cp.float64)
    pivots = cp.empty((args.batch, 47), cp.int32)
    outperm = cp.empty((args.batch, 25, 23), cp.int32)
    liftable = [cp.asarray(np.asarray([x is not None for x in values])) for values in lifts]
    generic_entropy = 21 * math.log(21) + 17 * math.log(17)
    protocol = {'start_utc': helper.stamp(), 'method_kind': 'exhaustive_joint_finite_field_loci',
                'classification': 'DISCOVERY ONLY; field loci and exact rational samples do not certify full-source geometry.',
                'device': args.device, 'seed': args.seed, 'batch': args.batch, 'prime': p,
                'parameter_pairs': end - start, 'joint_classes_total': total,
                'axis_class_counts': sizes, 'joint_class_partition': [start, end],
                'source_weight_catalogue': 'Every admissible beta in F65521, canonical field z_out representatives on both axes.',
                'source_triples': base.SOURCES, 'mutations': 0, 'actual_permutation': permutation.tolist(),
                'pr54_snapshot': str(args.pr54_snapshot), 'pr54_data_source_sha256': hashlib.sha256(pr54_source.read_bytes()).hexdigest(),
                'field_class_catalogue_sha256': [hashlib.sha256(np.asarray(axis, dtype='<i4').tobytes()).hexdigest() for axis in classes],
                'rational_weight_reconstruction': 'Unique numerator/denominator absolute bounds180, 2*180^2<65521, then exact-square quadratic roots and seven coordinate gates.',
                'liftable_axis_classes': [sum(x is not None for x in axis) for axis in lifts],
                'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'helper_sha256': hashlib.sha256(HELPER.read_bytes()).hexdigest(),
                'cuda_sha256': hashlib.sha256(family.CUDA.encode()).hexdigest(),
                'cupy': cp.__version__, 'numpy': np.__version__}
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    counts = [Counter(), Counter()]
    candidates, seen = [], set()
    started = time.monotonic()
    with (args.output / 'progress.jsonl').open('x') as progress:
        for first in range(2 * start, 2 * end, args.batch):
            count = min(args.batch, 2 * end - first)
            ids = cp.arange(first, first + count, dtype=cp.int64)
            pairs, sid = ids // 2, ids % 2
            left, right = pairs // sizes[1], pairs % sizes[1]
            x = cp.take(tables[0], 2 * left + sid, axis=0)
            y = cp.take(tables[1], 2 * right + sid, axis=0)
            kernel((count,), (128,), (parent, x, y, np.int32(p), np.uint32(args.seed),
                                      np.uint32(first % (2 ** 32)), np.int32(0), score, pivots, outperm))
            actual = pivots[:count]
            mask = cp.sum((actual[:, 1:] != actual[:, :-1] + 1).astype(cp.uint64)
                          * (cp.uint64(1) << cp.arange(46, dtype=cp.uint64)), axis=1)
            mask = cp.where(score[:count] >= 0, mask, cp.uint64(2 ** 63))
            for source_id in range(2):
                keys, frequencies = cp.unique(mask[source_id::2], return_counts=True)
                counts[source_id].update({int(key): int(frequency) for key, frequency in zip(keys.get(), frequencies.get())})
            selected = cp.flatnonzero((score[:count] > generic_entropy + 1e-9)
                                      & liftable[0][left] & liftable[1][right]).get()
            for index in selected:
                joint = (first + int(index)) // 2
                source_id = (first + int(index)) % 2
                li, ri = divmod(joint, sizes[1])
                key = (li, ri, source_id)
                if key in seen:
                    continue
                seen.add(key)
                pair = (lifts[0][li], lifts[1][ri])
                field = actual[int(index)].get().tolist()
                q = family.matrix_reference(permutation, pair, base.SOURCES[source_id])
                record = {'joint_class_index': joint, 'source_id': source_id,
                          'beta23': base.serial_fraction(pair[0]), 'beta25': base.serial_fraction(pair[1]),
                          'z_out_field': [classes[0][li][0], classes[1][ri][0]],
                          'field_pivots': field, 'Q_pivots': q,
                          'Q_matches_field': q == field,
                          'Q_runs': base.upstream.widths(q) if min(q) >= 0 else None,
                          'classification': 'EXACT Q SAMPLE ONLY' if q == field else 'FIELD-ONLY LOCUS, RATIONAL LIFT REJECTED'}
                candidates.append(record)
            completed = (first + count) // 2 - start
            progress.write(json.dumps({'utc': helper.stamp(), 'attempts': first + count - 2 * start,
                                       'unique_joint_classes_completed': completed,
                                       'remaining_joint_classes': end - start - completed,
                                       'rational_sample_controls': len(candidates),
                                       'elapsed_seconds': time.monotonic() - started}) + '\n')
            progress.flush()
            if first == 2 * start:
                li, ri = divmod(start, sizes[1])
                reference = family.matrix_reference(permutation, (F(classes[0][li][1]), F(classes[1][ri][1])), base.SOURCES[0], p)
                assert actual[0].get().tolist() == reference
    result = {**protocol, 'finish_utc': helper.stamp(), 'status': 'COMPLETE JOINT FINITE FIELD LOCI DISCOVERY',
              'attempts': 2 * (end - start), 'unique_joint_classes_completed': end - start,
              'elapsed_seconds': time.monotonic() - started,
              'profile_cut_histograms_by_fixture': [dict(sorted(axis.items())) for axis in counts],
              'rational_sample_controls': candidates,
              'limitations': ['Complete finite-field cut classification, not a rational or full-source-family proof.',
                              'Conjugate beta roots are deduplicated by field weight classes; local transpose flags remain separate.']}
    assert all(sum(axis.values()) == end - start for axis in counts)
    (args.output / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'unique_joint_classes': end - start,
                      'rational_sample_controls': len(candidates)}), flush=True)


if __name__ == '__main__':
    main()
