#!/usr/bin/env python3
"""Complete paired-grid Gaussian forward stage with real packed products.

No halo payloads are replicated. One source-core packet per grid feeds one
mixed-radix packed tensor convolution. Valid interiors are combined, and every
remaining output is explicitly repaired by the independent periodic band
reference. Array layouts model the bounded packet schedule and retain a
movement ledger; known-bit gathers remain an inherited physical interface.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from random import Random
from time import perf_counter

import mpmath as mp


def coords(shape):
    return itertools.product(*(range(x) for x in shape))


def encode(key, shape):
    out = 0
    for j, length in zip(key, shape):
        out = out * length + j
    return out


def tz(value, bits):
    return value >> bits if value >= 0 else -((-value) >> bits)


def product_grid(factors, bits, target_bits):
    value = 1 << bits
    for factor in factors:
        value = tz(value * factor, bits)
    return tz(value, bits - target_bits)


def pack_signed(rows, slots, slot_bytes):
    positive, negative = bytearray(slots * slot_bytes), bytearray(slots * slot_bytes)
    for position, value in rows:
        selected = positive if value >= 0 else negative
        selected[position * slot_bytes:(position + 1) * slot_bytes] = abs(value).to_bytes(slot_bytes, 'little')
    return int.from_bytes(positive, 'little') - int.from_bytes(negative, 'little')


def decode_centered(value, slots, slot_bytes, wanted):
    width = 8 * slot_bytes
    base = 1 << width
    raw = (value % (1 << (width * slots))).to_bytes(slots * slot_bytes, 'little')
    carry, result = 0, {}
    for position in range(slots):
        number = int.from_bytes(raw[position * slot_bytes:(position + 1) * slot_bytes], 'little') + carry
        carry = int(number >= base // 2)
        number -= carry * base
        if position in wanted:
            result[position] = number
    assert carry == int(value < 0)
    return result


def periodic_band_reference(data, source, target, alpha, q, p, ledger):
    current = tuple(source)
    for axis, (s, t) in enumerate(zip(source, target)):
        radius = int(mp.ceil(alpha * mp.sqrt((p + 48) * mp.log(2) / mp.pi))) + 2
        rows = []
        for k in range(t):
            center = mp.mpf(s) * k / t
            weights = {}
            for j in range(int(mp.floor(center)) - radius, int(mp.floor(center)) + radius + 1):
                original = j % s
                weight = int(mp.exp(-mp.pi * (mp.mpf(j) - center) ** 2 / (alpha * alpha)) * (1 << p) / (2 * alpha))
                if weight:
                    weights[original] = weights.get(original, 0) + weight
            rows.append(tuple(weights.items()))
        stride = math.prod(current[axis + 1:])
        outer = math.prod(current[:axis])
        out = [(0, 0)] * (outer * t * stride)
        for parent in range(outer):
            for post in range(stride):
                for k, row in enumerate(rows):
                    rr = ii = 0
                    for j, weight in row:
                        x = data[(parent * s + j) * stride + post]
                        rr += weight * x[0]
                        ii += weight * x[1]
                    out[(parent * t + k) * stride + post] = tz(rr, p), tz(ii, p)
                    ledger['reference_payload_reads'] += len(row)
        ledger['reference_axis_passes'] += 1
        ledger['reference_payload_writes'] += len(out)
        current = current[:axis] + (t,) + current[axis + 1:]
        data = out
    return data


def packed_forward(data, source, target, alpha, q, side, radius, ledger):
    dimension = len(source)
    sigmas = [mp.mpf(s) / t for s, t in zip(source, target)]
    reserve = int(mp.ceil(sum(mp.pi * sigma * (1 - sigma) * (side - 1) ** 2 / (alpha * alpha * mp.log(2))
                             for sigma in sigmas)))
    local_q, p = q + reserve + 64, q + reserve + 128
    assert mp.mp.prec > p + 64
    base = side + 2 * radius
    packing_shape = (base,) * dimension
    width_bytes = (2 * local_q + (side ** dimension).bit_length() + 23) // 8 + 1
    input_degree = encode((side - 1,) * dimension, packing_shape)
    kernel_degree = encode((2 * radius,) * dimension, packing_shape)
    slots = input_degree + kernel_degree + 1
    assert slots <= base ** dimension
    result = [None] * math.prod(target)
    overlap_max = 0
    for shift in (0, side // 2):
        for cell in coords(tuple(t // side for t in target)):
            origins = tuple(c * side + shift for c in cell)
            if any(k + side > t for k, t in zip(origins, target)):
                ledger['period_cut_cells_excluded'] += 1
                continue
            starts = tuple(s * k // t for s, t, k in zip(source, target, origins))
            ends = tuple(s * (k + side) // t for s, t, k in zip(source, target, origins))
            lengths = tuple(hi - lo for hi, lo in zip(ends, starts))
            y = [mp.mpf(j) - sigma * k for j, sigma, k in zip(starts, sigmas, origins)]
            input_axes, output_axes, kernel_axes = [], [], []
            for sigma, offset in zip(sigmas, y):
                input_axes.append([int(mp.exp(-mp.pi * (1 - sigma) * (a + offset) ** 2 / (alpha * alpha)) * (1 << p))
                                   for a in range(side)])
                output_axes.append([int(mp.exp(mp.pi * sigma * (1 - sigma) * b * b / (alpha * alpha)) * (1 << p))
                                    for b in range(side)])
                kernel_axes.append([int(mp.exp(-mp.pi * sigma * (-h + offset) ** 2 / (alpha * alpha)) * (1 << p))
                                    for h in range(-radius, radius + 1)])
            real_rows, imag_rows = [], []
            for key in coords(lengths):
                diagonal = product_grid((input_axes[i][key[i]] for i in range(dimension)), p, local_q)
                original = tuple(a + lo for a, lo in zip(key, starts))
                x = data[encode(original, source)]
                position = encode(key, packing_shape)
                real_rows.append((position, tz((x[0] << (local_q - q)) * diagonal, local_q)))
                imag_rows.append((position, tz((x[1] << (local_q - q)) * diagonal, local_q)))
            kernel_rows = [(encode(key, packing_shape), product_grid((kernel_axes[i][key[i]] for i in range(dimension)), p, local_q))
                           for key in coords((2 * radius + 1,) * dimension)]
            kernel = pack_signed(kernel_rows, kernel_degree + 1, width_bytes)
            real = pack_signed(real_rows, input_degree + 1, width_bytes) * kernel
            imag = pack_signed(imag_rows, input_degree + 1, width_bytes) * kernel
            good_shape = tuple(max(0, min(side - radius - 2, length - radius - 2) - radius - 2) for length in lengths)
            wanted = {}
            for fine in coords(good_shape):
                b = tuple(j + radius + 2 for j in fine)
                wanted[encode(tuple(j + radius for j in b), packing_shape)] = b
            real_coefficients = decode_centered(real, slots, width_bytes, wanted)
            imag_coefficients = decode_centered(imag, slots, width_bytes, wanted)
            denominator = (1 << (2 * local_q + p - q)) * (2 * alpha) ** dimension
            for position, b in wanted.items():
                diagonal = product_grid((output_axes[i][b[i]] for i in range(dimension)), p, p)
                values = (real_coefficients[position] * diagonal, imag_coefficients[position] * diagonal)
                value = tuple(v // denominator if v >= 0 else -((-v) // denominator) for v in values)
                target_index = encode(tuple(k + j for k, j in zip(origins, b)), target)
                if result[target_index] is None:
                    result[target_index] = value
                else:
                    overlap_max = max(overlap_max, *(abs(a - b) for a, b in zip(result[target_index], value)))
            ledger['source_packet_payload_reads'] += math.prod(lengths)
            ledger['zero_padded_packet_writes'] += side ** dimension
            ledger['packed_tensor_cells'] += 1
            ledger['signed_integer_multiplications'] += 2
            ledger['packed_polynomial_slots'] += slots
            ledger['maximum_operand_bits'] = max(ledger['maximum_operand_bits'], input_degree * 8 * width_bytes + local_q)
    return result, {'local_fractional_bits': local_q, 'coefficient_fractional_bits': p,
                    'full_tensor_reserve_bits': reserve, 'mixed_radix_base': base,
                    'binary_slot_bytes': width_bytes, 'overlap_maximum_grid_difference': overlap_max}


def run_case(config):
    started = perf_counter()
    source, target = tuple(config['source']), tuple(config['target'])
    q, alpha = config['q'], config['alpha']
    mp.mp.dps = config['digits']
    rng = Random(config['seed'])
    data = [(rng.randrange(-8, 9) << (q - 6), rng.randrange(-8, 9) << (q - 6)) for _ in range(math.prod(source))]
    ledger = {name: 0 for name in ('reference_payload_reads', 'reference_payload_writes', 'reference_axis_passes',
                                  'period_cut_cells_excluded', 'source_packet_payload_reads', 'zero_padded_packet_writes',
                                  'packed_tensor_cells', 'signed_integer_multiplications', 'packed_polynomial_slots', 'maximum_operand_bits')}
    approximate, reserve = packed_forward(data, source, target, alpha, q, config['side'], config['radius'], ledger)
    reference = periodic_band_reference(data, source, target, alpha, q, q + 64, ledger)
    regular = [j for j, x in enumerate(approximate) if x is not None]
    assert regular, 'all cells are exceptional; not a useful packed-stage control'
    error = max(abs(a - b) for j in regular for a, b in zip(approximate[j], reference[j]))
    assert error <= 16, (config, error)
    # Every unselected coefficient is explicitly repaired; reference work is
    # retained rather than being attributed to the fast packed cells.
    repair = 0
    for j, value in enumerate(approximate):
        if value is None:
            approximate[j] = reference[j]
            repair += 1
    maximum = max(abs(a - b) for arow, brow in zip(approximate, reference) for a, b in zip(arow, brow))
    result = {'status': 'complete joint packed forward stage and explicit repairs passed', 'config': config,
              'regular_coefficients': len(regular), 'repair_coefficients': repair, 'target_volume': math.prod(target),
              'maximum_integer_grid_error': maximum, 'maximum_absolute_error': str(mp.mpf(maximum) / (1 << q)),
              'reserve': reserve, 'movement_ledger': ledger, 'seconds': perf_counter() - started,
              'limitations': ['bounded named-bit gather is modeled and charged, not implemented as a native tape router',
                              'repair reference performs separately charged classical axis passes',
                              'finite side and radius choices do not certify all-size exceptional density']}
    Path(config['row_output']).write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error('one to four allocated one-thread workers')
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[key] = '1'
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    configs = json.loads(Path(args.config).read_text())
    for j, config in enumerate(configs):
        config['row_output'] = str(output / f'row-{j}.json')
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        rows = list(executor.map(run_case, configs))
    result = {'status': 'joint packed forward-stage controls passed', 'rows': rows,
              'dependency': {'mpmath': mp.__version__}, 'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'rows': [(r['regular_coefficients'], r['repair_coefficients'], r['maximum_integer_grid_error']) for r in rows]}))


if __name__ == '__main__':
    main()
