#!/usr/bin/env python3
"""Exhaustive source-family discrimination of one actual changed basis/permutation.

Two modular fields and bounded Q controls are retained. This is discovery,
not a complete rational NE-rank or multiplication certificate.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import combinations
import json
import math
from pathlib import Path
import time
import cupy as cp
import numpy as np

SOURCE = Path(__file__).with_name('gpu_basis_parameter_vectorized.py')
spec = importlib.util.spec_from_file_location('full_family_helpers', SOURCE)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
base = helper.base
assert base.CUDA.count('if(!valid)break;') == 1
# Complete every row even in a rank-deficient field, so all NE flags are available.
CUDA = base.CUDA.replace('if(!valid)break;', 'if(q<0)continue;')


def stamp():
    return datetime.now(timezone.utc).isoformat()


def matrix_reference(permutation, pair, triples, prime=None):
    weights = [base.rational_weights(h, beta) for h, beta in zip((23, 25), pair)]
    vectors = [[1/weights[k][0 if i in triples[k] else 1] for i in range(h)]
               for k, h in enumerate((23, 25))]
    if prime:
        vectors = [[x.numerator*pow(x.denominator, -1, prime) % prime for x in v]
                   for v in vectors]
    rows = [(int(permutation[i % 25, i // 25]), i % 25) for i in range(47)]
    columns = [(int(permutation[(528+j) % 25, (528+j) // 25]), (528+j) % 25)
               for j in range(47)]
    matrix = [[vectors[0][r]*(r == c)+vectors[1][b]*(b == d)-1
               for c, d in columns] for r, b in rows]
    if prime:
        matrix = [[x % prime for x in row] for row in matrix]
    pivots = []
    for i in range(47):
        q = next((j for j in range(46, -1, -1) if matrix[i][j]), -1)
        pivots.append(q)
        if q < 0:
            continue
        inverse = pow(matrix[i][q], -1, prime) if prime else 1/matrix[i][q]
        for k in range(i+1, 47):
            factor = matrix[k][q]*inverse
            if prime:
                factor %= prime
            if factor:
                matrix[k] = [v-factor*w for v, w in zip(matrix[k], matrix[i])]
                if prime:
                    matrix[k] = [v % prime for v in matrix[k]]
    return pivots


def vector_table(h, beta, triples, prime):
    masks = np.zeros((len(triples), h), bool)
    masks[np.arange(len(triples))[:, None], triples] = True
    inverses = [w.denominator*pow(w.numerator, -1, prime) % prime
                for w in base.rational_weights(h, beta)]
    return cp.asarray(np.where(masks, inverses[0], inverses[1]).astype(np.int32))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--batch', type=int, default=8192)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--baseline-histogram', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.device in (0, 1) and not args.output.exists()
    args.output.mkdir(parents=True)
    cp.cuda.Device(args.device).use()
    cp.get_default_memory_pool().set_limit(size=8*1024**3)
    candidate = json.loads(args.candidate.read_text())
    permutation = np.asarray(candidate['permutations'], np.int32)
    assert permutation.shape == (25, 23)
    assert all(sorted(row.tolist()) == list(range(23)) for row in permutation)
    pair = (F(2, 39), F(1, 57))
    primes = (65521, 1000003)
    assert all(helper.prime(p) for p in primes)
    triples = [np.asarray(list(combinations(range(h), 3)), np.int32) for h in (23, 25)]
    N = len(triples[0])*len(triples[1])
    start, end = N*args.device//2, N*(args.device+1)//2
    assert N == 4073300
    tables = [[vector_table(h, beta, triple, p)
               for h, beta, triple in zip((23, 25), pair, triples)] for p in primes]
    kernel = cp.RawKernel(CUDA, 'search')
    parent_gpu = cp.asarray(permutation)
    outscore = [cp.empty(args.batch, cp.float64) for p in primes]
    outpiv = [cp.empty((args.batch, 47), cp.int32) for p in primes]
    outperm = cp.empty((args.batch, 25, 23), cp.int32)
    controls = []
    for actual in (start, end-1):
        left, right = divmod(actual, len(triples[1]))
        source = [triples[0][left].tolist(), triples[1][right].tolist()]
        q = matrix_reference(permutation, pair, source)
        fields = []
        for k, p in enumerate(primes):
            x, y = tables[k][0][left:left+1], tables[k][1][right:right+1]
            kernel((1,), (128,), (parent_gpu, x, y, np.int32(p), np.uint32(args.seed),
                                   np.uint32(0), np.int32(0), outscore[k], outpiv[k], outperm))
            cp.cuda.Stream.null.synchronize()
            reference = matrix_reference(permutation, pair, source, p)
            assert outpiv[k][0].get().tolist() == reference
            fields.append({'prime': p, 'pivots': reference, 'matches_Q': reference == q})
        controls.append({'pair_index': actual, 'triples': source, 'Q_pivots': q, 'fields': fields})
    baseline = json.loads(args.baseline_histogram.read_text())
    assert baseline['actual_pairs'] == N
    protocol = {'start_utc': stamp(), 'method_kind': 'full_source_family',
                'classification': 'DISCOVERY ONLY: full two-field discrimination; bounded Q controls, no complete rational NE-rank certificate.',
                'device': args.device, 'seed': args.seed, 'batch': args.batch, 'primes': primes,
                'parameter_pairs': 1, 'beta23': base.serial_fraction(pair[0]),
                'beta25': base.serial_fraction(pair[1]), 'source_family_size': N,
                'source_partition_start_inclusive': start, 'source_partition_end_exclusive': end,
                'source_enumeration': 'Lexicographic combinations(range(23),3) times combinations(range(25),3), S index varying fastest.',
                'mutations': 0, 'actual_permutation': permutation.tolist(),
                'candidate_path': str(args.candidate),
                'candidate_sha256': hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
                'baseline_histogram_path': str(args.baseline_histogram),
                'baseline_histogram_sha256': hashlib.sha256(args.baseline_histogram.read_bytes()).hexdigest(),
                'baseline_scope': 'Read existing exact histogram only; unchanged baseline is not replayed.',
                'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'helper_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                'inherited_helper_sha256': hashlib.sha256(helper.HELPER.read_bytes()).hexdigest(),
                'inherited_source_sha256': hashlib.sha256(base.ROOT_SOURCE.read_bytes()).hexdigest(),
                'cuda_sha256': hashlib.sha256(CUDA.encode()).hexdigest(),
                'cupy': cp.__version__, 'numpy': np.__version__, 'initial_controls': controls}
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    saved = [np.lib.format.open_memmap(args.output/f'pivots-prime{p}.npy', mode='w+',
                                     dtype=np.int8, shape=(end-start, 47)) for p in primes]
    flags = np.lib.format.open_memmap(args.output/'pair-status.npy', mode='w+',
                                    dtype=np.uint8, shape=(end-start,))
    profiles = Counter()
    disagreements = 0
    valid_counts = [0, 0]
    exceptions = []
    sampled_keys = set()
    processed = 0
    begun = time.monotonic()
    bit_weights = cp.asarray(np.uint64(1) << np.arange(46, dtype=np.uint64))
    with (args.output/'progress.jsonl').open('x') as progress:
        for first in range(start, end, args.batch):
            count = min(args.batch, end-first)
            ids = cp.arange(first, first+count, dtype=cp.int32)
            left, right = ids//len(triples[1]), ids % len(triples[1])
            for k, p in enumerate(primes):
                x, y = cp.take(tables[k][0], left, axis=0), cp.take(tables[k][1], right, axis=0)
                kernel((count,), (128,), (parent_gpu, x, y, np.int32(p), np.uint32(args.seed),
                                          np.uint32(first), np.int32(0), outscore[k], outpiv[k], outperm))
            cp.cuda.Stream.null.synchronize()
            piv = [v[:count].get().astype(np.int8) for v in outpiv]
            valid = [(v >= 0).all(axis=1) for v in piv]
            same = (piv[0] == piv[1]).all(axis=1)
            status = valid[0].astype(np.uint8)+2*valid[1].astype(np.uint8)+4*same.astype(np.uint8)
            for k in range(2):
                saved[k][processed:processed+count] = piv[k]
                valid_counts[k] += int(valid[k].sum())
            flags[processed:processed+count] = status
            agreement = cp.asarray(same & valid[0] & valid[1])
            masks = cp.sum((outpiv[0][:count, 1:] != outpiv[0][:count, :-1]+1).astype(cp.uint64)*bit_weights,
                           axis=1, dtype=cp.uint64)
            keys, frequencies = cp.unique(masks[agreement], return_counts=True)
            profiles.update({int(k): int(v) for k, v in zip(keys.get(), frequencies.get())})
            bad = np.flatnonzero(~same | ~valid[0] | ~valid[1])
            disagreements += int((~same).sum())
            for local in bad:
                phenotype = tuple(piv[0][local].tolist()), tuple(piv[1][local].tolist())
                if phenotype in sampled_keys or len(exceptions) >= 12:
                    continue
                sampled_keys.add(phenotype)
                index = first+int(local)
                a, b = divmod(index, len(triples[1]))
                source = [triples[0][a].tolist(), triples[1][b].tolist()]
                q = matrix_reference(permutation, pair, source)
                exceptions.append({'pair_index': index, 'triples': source, 'Q_pivots': q,
                                   'fields': [{'prime': p, 'pivots': pv[local].tolist(),
                                               'matches_Q': pv[local].tolist() == q}
                                              for p, pv in zip(primes, piv)]})
            processed += count
            progress.write(json.dumps({'utc': stamp(), 'attempts': processed,
                                       'source_pairs_completed': processed,
                                       'source_pairs_remaining': end-start-processed,
                                       'elapsed_seconds': time.monotonic()-begun,
                                       'field_profile_disagreements': disagreements,
                                       'field_full_rank_pairs': valid_counts,
                                       'bounded_Q_exception_controls': len(exceptions)})+'\n')
            progress.flush()
    for v in saved:
        v.flush()
    flags.flush()
    histogram = Counter()
    classes = []
    for mask, frequency in sorted(profiles.items()):
        cuts = [0]+[i+1 for i in range(46) if mask & (1 << i)]+[47]
        runs = [b-a for a, b in zip(cuts, cuts[1:])]
        for width in runs:
            histogram[width] += frequency
        histogram[481] += frequency
        classes.append({'cut_mask': mask, 'count': frequency, 'runs': runs})
    outputs = []
    for path in sorted(args.output.glob('*.npy')):
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024*1024), b''):
                digest.update(block)
        outputs.append({'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest.hexdigest(),
                        'recovery': 'Deterministically regenerate the recorded lexicographic partition with this script and pinned candidate.'})
    result = {**protocol, 'finish_utc': stamp(), 'attempts': processed,
              'elapsed_seconds': time.monotonic()-begun,
              'source_pairs_completed': processed, 'field_full_rank_pairs': valid_counts,
              'field_profile_disagreements': disagreements,
              'two_field_agree_full_rank_pairs': sum(profiles.values()),
              'profile_classes_agree_full_rank': classes,
              'one_front_histogram_agree_full_rank': dict(sorted(histogram.items())),
              'bounded_Q_exception_controls': exceptions, 'binary_artifacts': outputs,
              'limitations': ['Equal two-field profiles do not prove rational zero minors.',
                              'Unresolved field disagreements are excluded from this histogram; both complete field pivot arrays are retained.',
                              'Global characteristic comparison requires rational CRT and all basis/physical/bridge gates.']}
    (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('finish_utc', 'device', 'source_pairs_completed',
                                            'field_full_rank_pairs', 'field_profile_disagreements',
                                            'two_field_agree_full_rank_pairs', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
