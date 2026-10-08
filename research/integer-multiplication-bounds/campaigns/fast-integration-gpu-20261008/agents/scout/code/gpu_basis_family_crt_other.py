#!/usr/bin/env python3
"""Exact NE-rank certificates for two new inherited-order source weight families.

One attained modular profile per pair gives all lower ranks. Every larger
minor vanishes in enough proven primes to exceed a uniform integer bound.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import time
import cupy as cp
import numpy as np

HELPER = Path(__file__).with_name('gpu_basis_parameter_full_family.py')
spec = importlib.util.spec_from_file_location('exact_family_gpu_helpers', HELPER)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
base = family.base
assert family.CUDA.count('int v=(r==c?xx[id*a+r]:0)+(be==de?yy[id*b+be]:0)-1;') == 1
assert family.CUDA.count('mat[z]=(v%p+p)%p;') == 1
CUDA = family.CUDA.replace('int v=(r==c?xx[id*a+r]:0)+(be==de?yy[id*b+be]:0)-1;',
                          'long long v=(long long)(r==c?xx[id*a+r]:0)+(be==de?yy[id*b+be]:0)-1;')
CUDA = CUDA.replace('mat[z]=(v%p+p)%p;',
                    'int residue=v%p;mat[z]=residue<0?residue+p:residue;')

CHECK = r'''
extern "C" __global__ void check_flags(const int *piv,const int *expected,int *flags) {
 int id=blockIdx.x,j=threadIdx.x;
 if(j>=47)return;
 int rank=0;
 for(int i=0;i<47;i++) {
  rank+=(piv[id*47+i]>=j);
  if(rank>expected[i*47+j])atomicCAS(flags+id,0,1+i*47+j);
 }
}
'''


def stamp():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            result.update(block)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--batch', type=int, default=8192)
    parser.add_argument('--initial-run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.device in (0, 1) and not args.output.exists()
    args.output.mkdir(parents=True)
    initial_path = args.initial_run/'summary.json'
    initial = json.loads(initial_path.read_text())
    assert initial['counterfactual_mode'] in ('half_both_inherited_permutation','five_thirds_left_half_right_inherited_permutation')
    assert initial['source_pairs_completed'] == initial['source_family_size'] == 4073300
    permutation = np.asarray(initial['actual_permutation'], np.int32)
    assert np.array_equal(permutation, base.upstream.baseline())
    pair = (F(1,51),F(1,57)) if initial['counterfactual_mode']=='half_both_inherited_permutation' else (F(5,3),F(1,57))
    assert initial['beta23'] == base.serial_fraction(pair[0])
    assert initial['beta25'] == base.serial_fraction(pair[1])
    expected = np.asarray(initial['initial_controls'][0]['Q_pivots'], np.int32)
    assert sorted(expected.tolist()) == list(range(47))
    N = initial['source_family_size']
    start, end = 0, N
    arrays = [np.load(args.initial_run/f'pivots-prime{p}.npy', mmap_mode='r')
              for p in initial['primes']]
    assert all(x.shape == (N, 47) and x.dtype == np.int8 for x in arrays)
    covered = 0
    nonexpected = [0, 0]
    for first in range(start, end, 65536):
        count = min(65536, end-first)
        matches = [(v[first:first+count] == expected).all(axis=1) for v in arrays]
        for k in range(2):
            nonexpected[k] += int((~matches[k]).sum())
        covered += int((matches[0] | matches[1]).sum())
    assert covered == end-start, 'Missing attained modular lower ranks'
    integer_scale = 1
    inverses = [[1/w for w in base.rational_weights(h, beta)]
                for h, beta in zip((23, 25), pair)]
    from math import lcm
    for vector in inverses:
        for value in vector:integer_scale=lcm(integer_scale,value.denominator)
    possible_entries = [integer_scale*(dx*x+dy*y-1)
                        for dx in (0, 1) for dy in (0, 1)
                        for x in inverses[0] for y in inverses[1]]
    assert all(x.denominator == 1 for x in possible_entries)
    Z = max(abs(int(x)) for x in possible_entries)
    assert Z > 0
    bound = 47**24*Z**47
    primes = []
    product = 1
    p = 2147483647
    while product <= bound:
        if family.helper.prime(p):
            assert integer_scale % p
            primes.append(p)
            product *= p
        p -= 2
    assert len(set(primes)) == len(primes) and product > bound
    cp.cuda.Device(args.device).use()
    cp.get_default_memory_pool().set_limit(size=8*1024**3)
    kernel = cp.RawKernel(CUDA, 'search')
    checker = cp.RawKernel(CHECK, 'check_flags')
    parent_gpu = cp.asarray(permutation)
    rank_table = np.cumsum(expected[:, None] >= np.arange(47)[None, :], axis=0).astype(np.int32)
    expected_gpu = cp.asarray(rank_table)
    triples = [np.asarray(list(combinations(range(h), 3)), np.int32) for h in (23, 25)]
    score = cp.empty(args.batch, cp.float64)
    pivots = cp.empty((args.batch, 47), cp.int32)
    outperm = cp.empty((args.batch, 25, 23), cp.int32)
    protocol = {'start_utc': stamp(), 'method_kind': 'full_source_family_crt',
                'classification': 'Exact rational NE ranks only after all prime-product upper checks pass.',
                'device': args.device, 'seed': args.seed, 'batch': args.batch,
                'parameter_pairs': 1, 'counterfactual_mode':initial['counterfactual_mode'], 'beta23': base.serial_fraction(pair[0]),
                'beta25': base.serial_fraction(pair[1]), 'source_family_size': N,
                'source_partition_start_inclusive': start, 'source_partition_end_exclusive': end,
                'expected_pivots': expected.tolist(),
                'expected_runs': base.upstream.widths(expected.tolist()),
                'actual_permutation': permutation.tolist(),
                'initial_run_path': str(args.initial_run),
                'initial_summary_sha256': digest(initial_path),
                'initial_pivot_artifact_hashes': [x for x in initial['binary_artifacts']
                                                if 'pivots-prime' in x['path']],
                'attained_lower_rank_pairs_in_partition': covered,
                'nonexpected_lower_field_profiles': nonexpected,
                'integer_matrix_scale': integer_scale, 'integer_entry_absolute_bound': Z,
                'all_minor_absolute_bound': str(bound), 'minor_bound_bits': bound.bit_length(),
                'primes': primes, 'primality_method': 'Exact trial division through integer square root.',
                'prime_product': str(product), 'prime_product_bits': product.bit_length(),
                'CRT_argument': 'Every corner rank is at most its expected rank in every proven field; every larger integer minor is divisible by the prime product exceeding its Hadamard bound, hence zero over Z. Prior attained field profile supplies every expected lower rank.',
                'source_sha256': digest(Path(__file__)), 'helper_sha256': digest(HELPER),
                'inherited_helper_sha256': digest(family.SOURCE),
                'inherited_cuda_sha256': hashlib.sha256(family.CUDA.encode()).hexdigest(),
                'wide_cuda_sha256': hashlib.sha256(CUDA.encode()).hexdigest(),
                'signed_arithmetic_scope': '64-bit initialization sum and branch normalization; field residues lie in [0,p), subtraction in (-p,p), products below p squared fit signed64 for proven31bit primes.',
                'checker_cuda_sha256': hashlib.sha256(CHECK.encode()).hexdigest(),
                'cupy': cp.__version__, 'numpy': np.__version__}
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    controls = []
    receipts = []
    with (args.output/'progress.jsonl').open('x') as progress:
        for pi, prime in enumerate(primes):
            tables = [family.vector_table(h, beta, triple, prime)
                      for h, beta, triple in zip((23, 25), pair, triples)]
            first_source = [triples[0][start//2300].tolist(), triples[1][start % 2300].tolist()]
            field_reference = family.matrix_reference(permutation, pair, first_source, prime)
            kernel((1,), (128,), (parent_gpu, tables[0][start//2300:start//2300+1],
                                  tables[1][start % 2300:start % 2300+1], np.int32(prime),
                                  np.uint32(args.seed), np.uint32(0), np.int32(0), score, pivots, outperm))
            cp.cuda.Stream.null.synchronize()
            assert pivots[0].get().tolist() == field_reference
            controls.append({'prime': prime, 'pair_index': start, 'pivots': field_reference})
            prime_started = time.monotonic()
            checked = 0
            for first in range(start, end, args.batch):
                count = min(args.batch, end-first)
                ids = cp.arange(first, first+count, dtype=cp.int32)
                x = cp.take(tables[0], ids//2300, axis=0)
                y = cp.take(tables[1], ids % 2300, axis=0)
                flags = cp.zeros(count, cp.int32)
                kernel((count,), (128,), (parent_gpu, x, y, np.int32(prime), np.uint32(args.seed),
                                          np.uint32(first), np.int32(0), score, pivots, outperm))
                checker((count,), (128,), (pivots, expected_gpu, flags))
                cp.cuda.Stream.null.synchronize()
                violations = int(cp.count_nonzero(flags))
                if violations:
                    local = int(cp.flatnonzero(flags)[0])
                    index = first+local
                    source = [triples[0][index//2300].tolist(), triples[1][index % 2300].tolist()]
                    failure = {'status': 'FAIL EXPECTED UPPER RANK', 'utc': stamp(),
                               'prime': prime, 'pair_index': index, 'triples': source,
                               'corner_code': int(flags[local]), 'field_pivots': pivots[local].get().tolist(),
                               'Q_pivots': family.matrix_reference(permutation, pair, source),
                               'violations_in_batch': violations}
                    (args.output/'failure.json').write_text(json.dumps(failure, indent=2)+'\n')
                    print(json.dumps(failure), flush=True)
                    return
                checked += count
                progress.write(json.dumps({'utc': stamp(), 'attempts': pi*(end-start)+checked,
                                           'prime_index': pi, 'prime': prime,
                                           'source_pairs_completed_current_prime': checked,
                                           'source_pairs_remaining_current_prime': end-start-checked,
                                           'elapsed_seconds': time.monotonic()-started,
                                           'upper_rank_violations': 0})+'\n')
                progress.flush()
            receipts.append({'prime': prime, 'source_pairs_checked': checked,
                             'upper_rank_violations': 0, 'seconds': time.monotonic()-prime_started})
            print(json.dumps({'utc': stamp(), 'device': args.device, 'prime_index': pi+1,
                              'primes_required': len(primes), 'source_pairs_checked': checked}), flush=True)
    result = {**protocol, 'status': 'PASS EXACT RATIONAL COMPLETE NE RANK PROFILE',
              'finish_utc': stamp(), 'attempts': len(primes)*(end-start),
              'source_pairs_completed': end-start, 'prime_replays_completed': len(primes),
              'elapsed_seconds': time.monotonic()-started, 'upper_rank_violations': 0,
              'field_CPU_controls': controls, 'prime_receipts': receipts,
              'limitations': ['Only this actual source data family, basis pair and inherited permutation are certified.',
                              'Local signed frames, copied centers, bridges and assembled multiplication cost remain separate obligations.']}
    (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'finish_utc', 'device',
                                          'source_pairs_completed', 'prime_replays_completed', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
