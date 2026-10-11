#!/usr/bin/env python3
"""Finite actual-source discrimination of distinct single-swap DATA orders.

The catalogue deduplicates identical first/last endpoint signatures. Two
fields, full lexical source coverage and compact complete frequency tables
are discovery evidence; exact rational certification remains separate.
Raw per-pair pivot arrays are intentionally not retained and regenerate
from the immutable source, parameters and exact swap tuple.
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

HELPER = Path(__file__).with_name('gpu_basis_configured_full_family.py')
spec = importlib.util.spec_from_file_location('swap_family_helper', HELPER)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
base = family.base


def stamp():
    return datetime.now(timezone.utc).isoformat()


def signature(permutation):
    return tuple(int(permutation[i % 25, i // 25]) for i in range(47)) + tuple(
        int(permutation[(528+j) % 25, (528+j) // 25]) for j in range(47))


def catalogue(parent):
    original = signature(parent)
    seen = {original}
    result = []
    for row in range(25):
        forced = ({0} if row < 23 else set()) | ({22} if row >= 2 else set())
        for left, right in combinations([j for j in range(23) if j not in forced], 2):
            permutation = parent.copy()
            permutation[row, left], permutation[row, right] = permutation[row, right], permutation[row, left]
            key = signature(permutation)
            if key in seen:
                continue
            seen.add(key)
            result.append(((row, left, right), permutation, key))
    return result


def decode_histogram(counter):
    widths = Counter()
    classes = []
    for mask, frequency in sorted(counter.items()):
        cuts = [0] + [i+1 for i in range(46) if mask & (1 << i)] + [47]
        runs = [b-a for a, b in zip(cuts, cuts[1:])]
        widths.update({width: frequency*runs.count(width) for width in set(runs)})
        widths[481] += frequency
        classes.append({'cut_mask': mask, 'count': frequency, 'runs': runs})
    return classes, dict(sorted(widths.items()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--batch', type=int, default=32768)
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--end', type=int)
    parser.add_argument('--beta23', type=F, required=True)
    parser.add_argument('--beta25', type=F, required=True)
    parser.add_argument('--skip-order', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.device in (0, 1) and not args.output.exists()
    pair = args.beta23, args.beta25
    assert all(beta not in family.helper.excluded(h) for h, beta in zip((23, 25), pair))
    parent = base.upstream.baseline()
    entries = catalogue(parent)
    skip = None
    if args.skip_order:
        record = json.loads(args.skip_order.read_text())
        skip = signature(np.asarray(record['permutations'], np.int32))
    end = len(entries) if args.end is None else args.end
    assert 0 <= args.start < end <= len(entries)
    selected = [i for i in range(args.start, end) if entries[i][2] != skip]
    assert selected
    args.output.mkdir(parents=True)
    cp.cuda.Device(args.device).use()
    cp.get_default_memory_pool().set_limit(size=8*1024**3)
    primes = (65521, 1000003)
    assert all(family.helper.prime(p) for p in primes)
    triples = [np.asarray(list(combinations(range(h), 3)), np.int32) for h in (23, 25)]
    N = len(triples[0])*len(triples[1])
    assert N == 4073300
    tables = [[family.vector_table(h, beta, ts, p) for h, beta, ts in zip((23, 25), pair, triples)] for p in primes]
    kernel = cp.RawKernel(family.CUDA, 'search')
    outscore = [cp.empty(args.batch, cp.float64) for _ in primes]
    outpiv = [cp.empty((args.batch, 47), cp.int32) for _ in primes]
    outperm = cp.empty((args.batch, 25, 23), cp.int32)
    bit_weights = cp.asarray(np.uint64(1) << np.arange(46, dtype=np.uint64))
    protocol = {'start_utc': stamp(), 'method_kind': 'full_source_family_single_swap_catalogue',
                'classification': 'DISCOVERY ONLY; two fields do not prove rational zero minors or assembly costs.',
                'device': args.device, 'seed': args.seed, 'batch': args.batch, 'primes': primes,
                'beta23': base.serial_fraction(pair[0]), 'beta25': base.serial_fraction(pair[1]),
                'source_family_size': N, 'source_enumeration': 'Lexical T index times2300 plus lexical S index.',
                'catalogue_size': len(entries), 'catalogue_range': [args.start, end], 'selected_indices': selected,
                'catalogue_sha256': hashlib.sha256(json.dumps([entry[0] for entry in entries]).encode()).hexdigest(),
                'parent_permutation_sha256': hashlib.sha256(parent.astype('<i4').tobytes()).hexdigest(),
                'forced_boundary_constraints': 'Pi[row,0]=row for row<23; Pi[row,22]=row-2 for row>=2.',
                'deduplication': 'Actual first47 and last47 left-coordinate signatures; first lexical valid swap retained.',
                'skipped_order': str(args.skip_order) if args.skip_order else None,
                'skipped_order_sha256': hashlib.sha256(args.skip_order.read_bytes()).hexdigest() if args.skip_order else None,
                'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'helper_sha256': hashlib.sha256(HELPER.read_bytes()).hexdigest(),
                'cuda_sha256': hashlib.sha256(family.CUDA.encode()).hexdigest(),
                'binary_omission': 'No per-pair binary arrays retained. Complete field/agree frequency tables and bounded controls are preserved. Winning geometry requires a fresh retained-pivot CRT run.',
                'cupy': cp.__version__, 'numpy': np.__version__}
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    begun = time.monotonic()
    complete = []
    with (args.output/'progress.jsonl').open('x') as progress:
        for ordinal, index in enumerate(selected):
            swap, permutation, endpoint_signature = entries[index]
            assert all(permutation[i, 0] == i for i in range(23))
            assert all(permutation[i, 22] == i-2 for i in range(2, 25))
            parent_gpu = cp.asarray(permutation)
            controls = []
            for actual in (0, N-1):
                left, right = divmod(actual, 2300)
                source = [triples[0][left].tolist(), triples[1][right].tolist()]
                q = family.matrix_reference(permutation, pair, source)
                fields = []
                for k, p in enumerate(primes):
                    kernel((1,), (128,), (parent_gpu, tables[k][0][left:left+1], tables[k][1][right:right+1], np.int32(p), np.uint32(args.seed), np.uint32(index), np.int32(0), outscore[k], outpiv[k], outperm))
                    cp.cuda.Stream.null.synchronize()
                    reference = family.matrix_reference(permutation, pair, source, p)
                    actual_pivots = outpiv[k][0].get().tolist()
                    assert actual_pivots == reference
                    fields.append({'prime': p, 'pivots': reference, 'matches_Q': reference == q})
                controls.append({'pair_index': actual, 'triples': source, 'Q_pivots': q, 'fields': fields})
            counts = [Counter(), Counter(), Counter()]
            full_rank = [0, 0]
            disagreements = 0
            before = time.monotonic()
            for first in range(0, N, args.batch):
                n = min(args.batch, N-first)
                ids = cp.arange(first, first+n, dtype=cp.int32)
                left, right = ids//2300, ids % 2300
                for k, p in enumerate(primes):
                    x, y = cp.take(tables[k][0], left, axis=0), cp.take(tables[k][1], right, axis=0)
                    kernel((n,), (128,), (parent_gpu, x, y, np.int32(p), np.uint32(args.seed), np.uint32(first), np.int32(0), outscore[k], outpiv[k], outperm))
                valid = [(outpiv[k][:n] >= 0).all(axis=1) for k in range(2)]
                same = (outpiv[0][:n] == outpiv[1][:n]).all(axis=1)
                masks = [cp.sum((outpiv[k][:n,1:] != outpiv[k][:n,:-1]+1).astype(cp.uint64)*bit_weights, axis=1, dtype=cp.uint64) for k in range(2)]
                selectors = [valid[0], valid[1], valid[0] & valid[1] & same]
                for k, selector in enumerate(selectors):
                    keys, frequencies = cp.unique(masks[min(k,1) if k<2 else 0][selector], return_counts=True)
                    counts[k].update({int(key): int(frequency) for key, frequency in zip(keys.get(), frequencies.get())})
                full_rank = [full_rank[k]+int(valid[k].sum().get()) for k in range(2)]
                disagreements += int((~same).sum().get())
            receipt = {'finish_utc': stamp(), 'catalogue_index': index, 'swap': swap,
                       'endpoint_signature': endpoint_signature, 'actual_permutation': permutation.tolist(),
                       'source_pairs_completed': N, 'field_full_rank_pairs': full_rank,
                       'field_profile_disagreements': disagreements, 'two_field_agree_full_rank_pairs': sum(counts[2].values()),
                       'elapsed_seconds': time.monotonic()-before, 'initial_controls': controls,
                       'classification': protocol['classification'], 'source_sha256': protocol['source_sha256']}
            for k, name in enumerate(('prime65521', 'prime1000003', 'agree')):
                classes, histogram = decode_histogram(counts[k])
                receipt[name] = {'profile_classes': classes, 'one_front_histogram': histogram}
            path = args.output/f'swap-{index:04d}.json'
            path.write_text(json.dumps(receipt, indent=2)+'\n')
            assert path.stat().st_size <= 1024*1024
            complete.append({'index': index, 'swap': swap, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                             'field_profile_disagreements': disagreements})
            observation = {'utc': stamp(), 'completed_permutations': ordinal+1,
                           'permutations_required': len(selected), 'source_pairs_completed': (ordinal+1)*N,
                           'attempts': 2*(ordinal+1)*N, 'elapsed_seconds': time.monotonic()-begun,
                           'latest_catalogue_index': index, 'field_profile_disagreements': disagreements}
            progress.write(json.dumps(observation)+'\n'); progress.flush()
            print(json.dumps(observation), flush=True)
    summary = {**protocol, 'finish_utc': stamp(), 'status': 'COMPLETE FINITE SINGLE-SWAP FAMILY DISCOVERY',
               'completed_permutations': len(complete), 'source_pairs_completed': len(complete)*N,
               'attempts': 2*len(complete)*N, 'elapsed_seconds': time.monotonic()-begun,
               'completed_receipts': complete}
    (args.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')


if __name__ == '__main__':
    main()
