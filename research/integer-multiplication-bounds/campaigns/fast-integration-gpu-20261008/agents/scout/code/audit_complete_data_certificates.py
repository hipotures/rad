#!/usr/bin/env python3
"""Independently bind full data-family CRT receipts to immutable input bytes.

This audit rederives rational weights, integer minor bounds, field primality,
lexicographic input tables and every attained lower profile. It does not replay
GPU upper-rank computations or claim a local-frame/compiler certificate.
"""
import argparse
import ast
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path

import numpy as np


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def record(path):
    return {'path': str(path), 'bytes': path.stat().st_size,
            'sha256': digest(path)}


def read(path):
    return json.loads(path.read_text())


def constant(path, name):
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == name
                for target in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(f'No literal {name} in {path}')


def weights(h, beta):
    gamma = (9 * beta - 1) / (3 * (1 - h * beta))
    inside = (1 - 3 * beta) * (1 + gamma) / 2
    outside = -3 * beta * gamma / 2
    assert inside and outside and 3 * inside + (h - 3) * outside == 1
    return inside, outside


def prime(p):
    return p >= 2 and all(p % d for d in range(2, math.isqrt(p) + 1))


def serial(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def run_audit(work, output):
    own = Path(__file__).resolve().parent
    campaign = own.parents[2]
    root_cuda_path = campaign / 'code/gpu_changed_basis_repair.py'
    cuda = constant(root_cuda_path, 'CUDA')
    cuda = cuda.replace('(r==c?xx[r]:0)+(be==de?yy[be]:0)',
                        '(r==c?xx[id*a+r]:0)+(be==de?yy[id*b+be]:0)')
    full_cuda = cuda.replace('if(!valid)break;', 'if(q<0)continue;')
    wide_cuda = full_cuda.replace(
        'int v=(r==c?xx[id*a+r]:0)+(be==de?yy[id*b+be]:0)-1;',
        'long long v=(long long)(r==c?xx[id*a+r]:0)+(be==de?yy[id*b+be]:0)-1;')
    wide_cuda = wide_cuda.replace('mat[z]=(v%p+p)%p;',
                                 'int residue=v%p;mat[z]=residue<0?residue+p:residue;')
    wide_hash = hashlib.sha256(wide_cuda.encode()).hexdigest()
    assert 'mat[z]=(v%p+p)%p;' not in wide_cuda
    assert 'int v=mat[k*d+j]-mul(factors[k],mat[i*d+j],p);' in wide_cuda
    assert '__device__ int mul(int x,int y,int p) { return (long long)x*y%p; }' in wide_cuda
    triples = [np.asarray(list(combinations(range(h), 3)), dtype='<i4')
               for h in (23, 25)]
    assert [len(table) for table in triples] == [1771, 2300]
    N = len(triples[0]) * len(triples[1])
    specs = [
        ('hybrid-half', 'gpu_basis_family_crt_wide.py',
         ['gpu-basis-full-crt-wide-20261008T1629-device0',
          'gpu-basis-full-crt-wide-20261008T1629-device1']),
        ('both-half', 'gpu_basis_family_crt_other.py',
         ['gpu-basis-other-crt-20261008T1638-device0']),
        ('five-thirds-half', 'gpu_basis_family_crt_other.py',
         ['gpu-basis-other-crt-20261008T1638-device1'])]
    results = []
    for label, filename, runs in specs:
        summaries = [read(work / 'derived/scout' / run / 'summary.json') for run in runs]
        first = summaries[0]
        beta = [Fraction(first[f'beta{h}']['numerator'],
                         first[f'beta{h}']['denominator']) for h in (23, 25)]
        source_path = own / filename
        assert digest(source_path) == first['source_sha256']
        assert digest(own / 'gpu_basis_parameter_full_family.py') == first['helper_sha256']
        assert digest(own / 'gpu_basis_parameter_vectorized.py') == first['inherited_helper_sha256']
        assert hashlib.sha256(full_cuda.encode()).hexdigest() == first['inherited_cuda_sha256']
        assert wide_hash == first['wide_cuda_sha256']
        check_hash = hashlib.sha256(constant(source_path, 'CHECK').encode()).hexdigest()
        assert check_hash == first['checker_cuda_sha256']
        actual_weights = [weights(h, value) for h, value in zip((23, 25), beta)]
        inverses = [[1 / value for value in axis] for axis in actual_weights]
        scale = math.lcm(*(value.denominator for axis in inverses for value in axis))
        entries = [scale * (dx * x + dy * y - 1)
                   for dx in (0, 1) for dy in (0, 1)
                   for x in inverses[0] for y in inverses[1]]
        assert all(value.denominator == 1 for value in entries)
        Z = max(abs(int(value)) for value in entries)
        bound = 47 ** 24 * Z ** 47
        assert (scale, Z, str(bound)) == (first['integer_matrix_scale'],
                first['integer_entry_absolute_bound'], first['all_minor_absolute_bound'])
        primes = first['primes']
        assert len(primes) == len(set(primes)) and all(prime(p) for p in primes)
        product = math.prod(primes)
        assert product == int(first['prime_product']) and product > bound
        assert all(0 < p < 2 ** 31 and scale % p for p in primes)
        permutation = np.asarray(first['actual_permutation'], dtype='<i4')
        expected = np.asarray(first['expected_pivots'], dtype=np.int8)
        assert permutation.shape == (25, 23)
        assert all(sorted(row.tolist()) == list(range(23)) for row in permutation)
        assert sorted(expected.tolist()) == list(range(47))
        initial_path = Path(first['initial_run_path']) / 'summary.json'
        assert digest(initial_path) == first['initial_summary_sha256']
        initial = read(initial_path)
        assert initial['source_pairs_completed'] == initial['source_family_size'] == N
        assert initial['source_partition_start_inclusive'] == 0
        assert initial['source_partition_end_exclusive'] == N
        assert initial['actual_permutation'] == permutation.tolist()
        assert all(initial[f'beta{h}'] == serial(value) for h, value in zip((23, 25), beta))
        arrays, input_records = [], []
        for artifact in first['initial_pivot_artifact_hashes']:
            path = Path(artifact['path'])
            actual = record(path)
            assert (actual['bytes'], actual['sha256']) == (artifact['bytes'], artifact['sha256'])
            assert artifact in initial['binary_artifacts']
            array = np.load(path, mmap_mode='r')
            assert array.dtype == np.int8 and array.shape == (N, 47)
            arrays.append(array)
            input_records.append(actual)
        assert len(arrays) == 2
        nonexpected, neither = [0, 0], 0
        for start in range(0, N, 65536):
            end = min(start + 65536, N)
            matches = [(array[start:end] == expected).all(axis=1) for array in arrays]
            for k in range(2):
                nonexpected[k] += int((~matches[k]).sum())
            neither += int((~matches[0] & ~matches[1]).sum())
        assert neither == 0
        part_records, end_previous = [], 0
        for name, summary in zip(runs, summaries):
            part_path = work / 'derived/scout' / name
            protocol = read(part_path / 'protocol.json')
            assert all(summary[key] == value for key, value in protocol.items())
            for key in ('source_sha256', 'helper_sha256', 'inherited_helper_sha256',
                        'wide_cuda_sha256', 'checker_cuda_sha256', 'primes',
                        'integer_matrix_scale', 'integer_entry_absolute_bound',
                        'all_minor_absolute_bound', 'expected_pivots', 'actual_permutation'):
                assert summary[key] == first[key]
            start, end = (summary['source_partition_start_inclusive'],
                          summary['source_partition_end_exclusive'])
            assert start == end_previous and start < end <= N
            end_previous = end
            assert summary['status'] == 'PASS EXACT RATIONAL COMPLETE NE RANK PROFILE'
            assert summary['source_pairs_completed'] == end - start
            assert summary['attained_lower_rank_pairs_in_partition'] == end - start
            assert summary['prime_replays_completed'] == len(primes)
            assert summary['attempts'] == len(primes) * (end - start)
            assert summary['upper_rank_violations'] == 0
            assert [item['prime'] for item in summary['prime_receipts']] == primes
            assert all(item['source_pairs_checked'] == end - start and
                       item['upper_rank_violations'] == 0 for item in summary['prime_receipts'])
            assert [item['prime'] for item in summary['field_CPU_controls']] == primes
            part_records.append({**record(part_path / 'summary.json'),
                                 'partition': [start, end]})
        assert end_previous == N
        regenerated = []
        for p in primes:
            tables = []
            for h, triple, axis in zip((23, 25), triples, inverses):
                mask = np.zeros((len(triple), h), bool)
                mask[np.arange(len(triple))[:, None], triple] = True
                values = [value.numerator * pow(value.denominator, -1, p) % p
                          for value in axis]
                table = np.where(mask, values[0], values[1]).astype('<i4')
                tables.append({'axis': h, 'shape': list(table.shape), 'dtype': '<i4',
                               'sha256_raw_C_order': hashlib.sha256(table.tobytes()).hexdigest()})
            regenerated.append({'prime': p, 'tables': tables})
        results.append({'family': label, 'status': 'PASS INPUT AND RECEIPT BINDING',
                        'beta23': serial(beta[0]), 'beta25': serial(beta[1]),
                        'source_pairs': N, 'integer_matrix_scale': scale,
                        'integer_entry_absolute_bound': Z,
                        'all_minor_absolute_bound': str(bound), 'minor_bound_bits': bound.bit_length(),
                        'prime_product': str(product), 'prime_product_bits': product.bit_length(),
                        'strict_prime_product_exceeds_bound': product > bound,
                        'all_primes_exact_trial_division_proven': True,
                        'primes': primes, 'lower_nonexpected_counts_in_artifact_order': nonexpected,
                        'lower_neither_expected': neither, 'lower_input_bytes': input_records,
                        'initial_summary': record(initial_path), 'CRT_parts': part_records,
                        'source': record(source_path), 'actual_permutation': permutation.tolist(),
                        'expected_pivots': expected.tolist(), 'expected_runs': first['expected_runs'],
                        'one_data_front_histogram': {'1': 9 * N, '17': N, '21': N, '481': N},
                        'regenerated_field_input_tables': regenerated})
    receipt = {'updated_utc': datetime.now(timezone.utc).isoformat(),
               'status': 'PASS THREE EXACT DATA FAMILIES INPUT BINDING',
               'audit_source': record(Path(__file__)), 'numpy': np.__version__,
               'source_enumeration': 'Lexicographic triples23 x triples25; right index varies fastest.',
               'triples': [{'h': h, 'shape': list(table.shape), 'dtype': '<i4',
                            'sha256_raw_C_order': hashlib.sha256(table.tobytes()).hexdigest()}
                           for h, table in zip((23, 25), triples)],
               'dependency_sources': [record(own / name) for name in
                   ('gpu_basis_parameter_full_family.py', 'gpu_basis_parameter_vectorized.py',
                    'gpu_basis_parameter_discovery.py')] + [record(root_cuda_path)],
               'wide_cuda_sha256': wide_hash, 'families': results,
               'limitations': [
                   'Regenerated field-table hashes bind the deterministic source formula; they are not GPU readbacks.',
                   'Upper-rank computations are checked through preserved complete receipts, not replayed here.',
                   'This audit supplies no new local-frame, endpoint/compiler, bridge or multiplication-cost proof.']}
    output.parent.mkdir(parents=True, exist_ok=True)
    assert not output.exists()
    output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': receipt['status'], 'output': str(output),
                      'families': [item['family'] for item in results]}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run_audit(args.work_root, args.output)
