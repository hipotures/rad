#!/usr/bin/env python3
"""Complete integer recovery with actual joint packed Gaussian forward cells.

The compression remains a charged matrix reference. Joint forward cells use
two global grids, actual signed integer products and explicit repairs. The
unchanged complete arithmetic oracle still checks every integer coefficient.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
from time import perf_counter


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--producer', required=True)
    parser.add_argument('--forward-stage', required=True)
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[key] = '1'
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    producer = import_file('frozen_complete_pipeline', args.producer)
    stage = import_file('frozen_joint_forward', args.forward_stage)
    config = json.loads(Path(args.config).read_text())
    config['row_output'] = str(output / 'arithmetic-row.json')
    stage_rows = []

    def source_transform(data, source_shape, target_shape, matrices, q, chirps, suffix_phases, ledger, opposite=False):
        stage.mp.mp.dps = max(stage.mp.mp.dps, config.get('packed_digits', config['digits']))
        if opposite:
            data = [producer.conjugate(x) for x in data]
        forward_ledger = {name: 0 for name in ('reference_payload_reads', 'reference_payload_writes', 'reference_axis_passes',
                                             'period_cut_cells_excluded', 'source_packet_payload_reads', 'zero_padded_packet_writes',
                                             'packed_tensor_cells', 'signed_integer_multiplications', 'packed_polynomial_slots', 'maximum_operand_bits')}
        partial, reserve = stage.packed_forward(data, source_shape, target_shape, config['alpha'], q,
                                                config['side'], config['radius'], forward_ledger)
        reference = stage.periodic_band_reference(data, source_shape, target_shape, config['alpha'], q, q + 64, forward_ledger)
        regular = [j for j, value in enumerate(partial) if value is not None]
        assert regular, 'no regular packed cell in complete pipeline'
        discrepancy = max(abs(a - b) for j in regular for a, b in zip(partial[j], reference[j]))
        assert discrepancy <= 16, ('joint forward vs periodic reference', discrepancy)
        data = [reference[j] if value is None else value for j, value in enumerate(partial)]
        current = target_shape
        chirped = [producer.cmul(producer.conjugate(a), x, q) for a, x in zip(chirps, data)]
        transformed = producer.scalar_cyclic_convolution(chirps, chirped, target_shape, q, suffix_phases, ledger)
        data = [producer.cmul(producer.conjugate(a), x, q) for a, x in zip(chirps, transformed)]
        for axis in reversed(range(len(source_shape))):
            data, current = producer.real_axis_pass(data, current, axis, matrices[axis][1], q + 64, ledger)
        assert current == source_shape
        gamma = sum(2 * axis[2]['alpha'] ** 2 for axis in matrices)
        data = [(a << gamma, b << gamma) for a, b in data]
        if opposite:
            data = [producer.conjugate(x) for x in data]
        ledger['gaussian_source_transforms'] += 1
        row = {'regular_coefficients': len(regular), 'repair_coefficients': math.prod(target_shape) - len(regular),
               'maximum_grid_discrepancy': discrepancy, 'reserve': reserve, 'movement_ledger': forward_ledger}
        stage_rows.append(row)
        (output / f'forward-stage-{len(stage_rows)}.json').write_text(json.dumps(row, indent=2) + '\n')
        return data

    producer.source_transform = source_transform
    started = perf_counter()
    arithmetic = producer.run_case(config)
    result = {'status': 'complete integer recovery with actual joint packed forward stages passed',
              'arithmetic': arithmetic, 'joint_forward_stages': stage_rows, 'seconds': perf_counter() - started,
              'producer_sha256': producer.SOURCE_SHA256_AT_IMPORT,
              'forward_stage_sha256': hashlib.sha256(Path(args.forward_stage).read_bytes()).hexdigest(),
              'wrapper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limitations': ['compression/inverse Gaussian stages remain explicitly charged matrix references',
                              'named-bit gather is modeled and charged rather than implemented as a native tape router',
                              'repair reference computes all classical outputs and charges them; this finite checker does not benchmark the sparse repair algorithm',
                              'no all-size complexity is inferred from finite complete arithmetic success']}
    (output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'coefficient_error': arithmetic['coefficient_real_error'],
                      'stage_regular_coefficients': [row['regular_coefficients'] for row in stage_rows]}))


if __name__ == '__main__':
    main()
