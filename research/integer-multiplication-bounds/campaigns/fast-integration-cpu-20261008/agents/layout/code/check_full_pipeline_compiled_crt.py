#!/usr/bin/env python3
"""Run complete actual guarded CRT at the input of a Gaussian integer pipeline.

Imports the inverse agent's pinned physical-program API read-only. The complete
arithmetic producer remains independently checked, and all API ledgers are
retained. No precomputed leaf-address lookup replaces its actual F_u events.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys
from pathlib import Path
from time import perf_counter


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--producer', required=True)
    parser.add_argument('--crt-api', required=True)
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--final-inverse', action='store_true')
    args = parser.parse_args()
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[key] = '1'
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(Path(args.crt_api).parent))
    api = import_file('physical_crt_payload_api', args.crt_api)
    producer = import_file('frozen_gaussian_pipeline', args.producer)
    api_hash_at_import = hashlib.sha256(Path(args.crt_api).read_bytes()).hexdigest()
    dependency_hashes = {name: hashlib.sha256((Path(args.crt_api).parent / name).read_bytes()).hexdigest()
                         for name in ('compiled_crt_pipeline_bankleaf.py', 'crt_guard_controls.py')}
    config = json.loads(Path(args.config).read_text())
    config['row_output'] = str(output / 'arithmetic-row.json')
    api_rows = []
    conversion_rows = []
    input_digits = []
    recovered_words = []
    original_reference = producer.crt_checked_source
    original_transform = producer.source_transform

    def capture_transform(*positional, **keywords):
        result = original_transform(*positional, **keywords)
        if keywords.get('opposite'):
            recovered_words[:] = result
        return result

    def actual_crt(digits, primes, q, digit_bits):
        coefficients = list(digits) + [0] * (math.prod(primes) - len(digits))
        input_digits.append(list(digits))
        receipt = api.transform_payload(primes, coefficients, reverse_check=not args.final_inverse, emit_stdout=False)
        binary = receipt.pop('output')
        caps = tuple(1 << (s - 1).bit_length() for s in primes)
        result = []
        for key in producer.addresses(primes):
            index, stride = 0, 1
            for coordinate, capacity in zip(key, caps):
                index += coordinate * stride
                stride *= capacity
            result.append((binary[index] << (q - digit_bits - 2), 0))
        # Independent triangular CRT reference is retained only as an oracle.
        assert result == original_reference(digits, primes, q, digit_bits)
        conversion_rows.append({'source_records': len(binary), 'destination_records': len(result),
                                'physical_operation': 'paid named axis-field reversal, then one zero-padding filter',
                                'payload_reads': len(binary), 'payload_writes': len(result)})
        api_rows.append(receipt)
        (output / f'crt-input-{len(api_rows)}.json').write_text(json.dumps(receipt, indent=2) + '\n')
        return result

    producer.crt_checked_source = actual_crt
    producer.source_transform = capture_transform
    started = perf_counter()
    arithmetic = producer.run_case(config)
    inverse_receipt = None
    if args.final_inverse:
        primes, q = config['source'], config['q']
        volume = math.prod(primes)
        caps = tuple(1 << (s - 1).bit_length() for s in primes)
        binary_leaf = [0] * math.prod(caps)
        scale = volume * volume * (1 << (2 * config['digit_bits'] + 4))
        for key, value in zip(producer.addresses(primes), recovered_words):
            index, stride = 0, 1
            for coordinate, capacity in zip(key, caps):
                index += coordinate * stride
                stride *= capacity
            binary_leaf[index] = producer.nearest_signed_integer(value[0] * scale, 1 << q)
        inverse_receipt = api.inverse_payload(primes, binary_leaf, emit_stdout=False)
        scalar = inverse_receipt.pop('coefficients')
        padded_scalar = inverse_receipt.pop('output')
        oracle = producer.direct_integer_convolution(*input_digits, volume)
        assert scalar == oracle and padded_scalar[:volume] == oracle and not any(padded_scalar[volume:])
        inverse_receipt['recovered_coefficient_sha256'] = hashlib.sha256(json.dumps(scalar).encode()).hexdigest()
        conversion_rows.append({'source_records': volume, 'destination_records': len(binary_leaf),
                                'physical_operation': 'paid named axis-field reversal and joint zero-padding embedding before actual reverse CRT',
                                'payload_reads': volume, 'payload_writes': len(binary_leaf)})
        (output / 'crt-final-inverse.json').write_text(json.dumps(inverse_receipt, indent=2) + '\n')
    result = {'status': ('complete Gaussian integer pipeline with actual compiled CRT forward and inverse programs passed'
                         if args.final_inverse else 'complete Gaussian integer pipeline with actual compiled CRT input programs passed'),
              'arithmetic': arithmetic, 'actual_crt_input_programs': api_rows,
              'paid_binary_to_source_conversions': conversion_rows,
              'actual_final_crt_inverse': inverse_receipt,
              'producer_sha256': producer.SOURCE_SHA256_AT_IMPORT,
              'crt_api_sha256': api_hash_at_import, 'crt_dependency_hashes': dependency_hashes,
              'wrapper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'seconds': perf_counter() - started,
              'limitations': ['dense Gaussian reference stages remain explicitly charged',
                              'reverse program compilation on positive labels is separately charged when used for final coefficients',
                              'finite physical program does not benchmark asymptotic fixed-tape complexity']}
    (output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'coefficient_error': arithmetic['coefficient_real_error'],
                      'compiled_batches': [len(row['compiled_batches']) for row in api_rows]}))


if __name__ == '__main__':
    main()
