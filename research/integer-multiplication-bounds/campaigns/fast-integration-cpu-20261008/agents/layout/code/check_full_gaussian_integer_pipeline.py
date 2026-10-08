#!/usr/bin/env python3
"""Bounded end-to-end dyadic Gaussian/CRT/tensor-ring integer recovery.

The finite Gaussian producers here use charged dense axis reference passes.
They are not an implementation or timing certificate of the all-size fast tape
producer. Every online complex value is an exact integer pair on one dyadic
work grid. mpmath is used only for setup, independently checked source DFTs and
reported error conversion. Polynomial products are actual signed Kronecker
integer products, with exact centered decoding and negacyclic reduction.
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

SOURCE_SHA256_AT_IMPORT = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def tz(value, bits):
    """Division by 2**bits toward zero, including signed integers."""
    if bits < 0:
        return value << -bits
    return value >> bits if value >= 0 else -((-value) >> bits)


def cadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def csub(a, b):
    return a[0] - b[0], a[1] - b[1]


def cmul(a, b, q):
    return tz(a[0] * b[0] - a[1] * b[1], q), tz(a[0] * b[1] + a[1] * b[0], q)


def conjugate(a):
    return a[0], -a[1]


def to_dyadic(value, q):
    return int(mp.re(value) * (1 << q)), int(mp.im(value) * (1 << q))


def addresses(shape):
    return itertools.product(*(range(n) for n in shape))


def encode(key, shape):
    result = 0
    for k, n in zip(key, shape):
        result = result * n + k
    return result


def decode(value, shape):
    key = [0] * len(shape)
    for j in reversed(range(len(shape))):
        value, key[j] = divmod(value, shape[j])
    assert value == 0
    return tuple(key)


def crt_forward(k, primes):
    if len(primes) == 1:
        return (k,)
    split = len(primes) // 2
    left, right = primes[:split], primes[split:]
    sl, sr = math.prod(left), math.prod(right)
    a, b = k % sl, k // sl
    changed = (b + pow(sl, -1, sr) * a) % sr
    return crt_forward(a, left) + crt_forward(changed, right)


def crt_inverse(key, primes):
    if len(primes) == 1:
        return key[0]
    split = len(primes) // 2
    left, right = primes[:split], primes[split:]
    sl, sr = math.prod(left), math.prod(right)
    a = crt_inverse(key[:split], left)
    changed = crt_inverse(key[split:], right)
    b = (changed - pow(sl, -1, sr) * a) % sr
    return a + sl * b


def crt_checked_source(digits, primes, q, digit_bits):
    volume = math.prod(primes)
    cofactors = []
    for leaf in range(len(primes)):
        lo, hi, factor = 0, len(primes), 1
        while hi - lo > 1:
            split = lo + (hi - lo) // 2
            if leaf >= split:
                factor *= math.prod(primes[lo:split])
                lo = split
            else:
                hi = split
        cofactors.append(factor)
    output = [(0, 0)] * volume
    for k in range(volume):
        key = crt_forward(k, primes)
        # Right-ancestor normalization is an additive CRT isomorphism. It need
        # not equal conventional full-cofactor normalization on left leaves.
        oracle = tuple(pow(factor, -1, p) * k % p for factor, p in zip(cofactors, primes))
        assert key == oracle
        assert crt_inverse(key, primes) == k
        if k < len(digits):
            output[encode(key, primes)] = (digits[k] << (q - digit_bits - 2), 0)
    return output


def setup_axis(s, t, alpha, q):
    precision = q + 64
    u = alpha * alpha
    rho = mp.mpf(t) / s
    radius = int(mp.ceil(alpha * mp.sqrt((mp.mp.dps + 20) * mp.log(10) / mp.pi) / s)) + 2
    images = range(-radius, radius + 1)
    selector = [int(mp.floor(rho * j + mp.mpf('0.5'))) for j in range(s)]
    assert len(set(selector)) == s and max(selector) < t
    diagonal = [mp.exp(mp.pi * u * (rho * j - selector[j]) ** 2) for j in range(s)]
    a = mp.matrix(t, s)
    tg = mp.matrix(t, s)
    for k in range(t):
        for j in range(s):
            a[k, j] = sum(mp.exp(-mp.pi * (j + period * s - mp.mpf(s) * k / t) ** 2 / u)
                          for period in images) / (2 * alpha)
            tg[k, j] = sum(mp.exp(-mp.pi * u * (rho * j + period * t - k) ** 2)
                           for period in images)
    n = mp.matrix(s, s)
    for j in range(s):
        for h in range(s):
            n[j, h] = tg[selector[j], h] * diagonal[h]
    inv = n ** -1
    b = mp.matrix(s, t)
    for j in range(s):
        for h in range(s):
            b[j, selector[h]] = diagonal[j] * inv[j, h] / mp.mpf(2) ** (2 * u - 1)
    aa = [[int(a[k, j] * (1 << precision)) for j in range(s)] for k in range(t)]
    bb = [[int(b[k, j] * (1 << precision)) for j in range(t)] for k in range(s)]
    receipt = {'s': s, 't': t, 'alpha': alpha, 'coefficient_fractional_bits': precision,
               'period_images': radius, 'selector': selector,
               'inverse_residual': str(max(abs(v) for v in inv * n - mp.eye(s)))}
    return aa, bb, receipt


def real_axis_pass(data, shape, axis, coefficients, p, ledger):
    n, m = shape[axis], len(coefficients)
    stride = math.prod(shape[axis + 1:])
    outer = math.prod(shape[:axis])
    result = [(0, 0)] * (outer * m * stride)
    for parent in range(outer):
        for post in range(stride):
            for k in range(m):
                rr = ii = 0
                for j in range(n):
                    coeff = coefficients[k][j]
                    x = data[(parent * n + j) * stride + post]
                    rr += coeff * x[0]
                    ii += coeff * x[1]
                result[(parent * m + k) * stride + post] = tz(rr, p), tz(ii, p)
    changed = shape[:axis] + (m,) + shape[axis + 1:]
    ledger['dense_gaussian_axis_passes'] += 1
    ledger['dense_gaussian_coefficient_products'] += 2 * outer * stride * n * m
    ledger['dense_gaussian_payload_reads'] += outer * stride * n * m
    ledger['dense_gaussian_payload_writes'] += len(result)
    return result, changed


def monomial(poly, power):
    r = len(poly)
    result = [(0, 0)] * r
    for k, value in enumerate(poly):
        wraps, j = divmod(k + power, r)
        result[j] = (-value[0], -value[1]) if wraps % 2 else value
    return result


def half_sum(a, b, subtract=False):
    op = csub if subtract else cadd
    return [(tz(v[0], 1), tz(v[1], 1)) for v in (op(x, y) for x, y in zip(a, b))]


def ring_forward(line, r):
    n = len(line)
    if n == 1:
        return line
    first = [half_sum(line[k], line[k + n // 2]) for k in range(n // 2)]
    second = [monomial(half_sum(line[k], line[k + n // 2], True), -(2 * r // n) * k)
              for k in range(n // 2)]
    return ring_forward(first, r) + ring_forward(second, r)


def ring_backward(line, r):
    n = len(line)
    if n == 1:
        return line
    first = ring_backward(line[:n // 2], r)
    second = ring_backward(line[n // 2:], r)
    twiddled = [monomial(second[k], (2 * r // n) * k) for k in range(n // 2)]
    return [half_sum(x, y) for x, y in zip(first, twiddled)] + [half_sum(x, y, True) for x, y in zip(first, twiddled)]


def ring_axis_pass(records, main, axis, r, inverse, ledger):
    stride = math.prod(main[axis + 1:])
    outer = math.prod(main[:axis])
    n = main[axis]
    result = list(records)
    for parent in range(outer):
        for post in range(stride):
            ids = [(parent * n + j) * stride + post for j in range(n)]
            transformed = (ring_backward if inverse else ring_forward)([records[k] for k in ids], r)
            for k, poly in zip(ids, transformed):
                result[k] = poly
    ledger['synthetic_fft_axis_passes'] += 1
    ledger['synthetic_fft_butterflies'] += outer * stride * (n // 2) * int(math.log2(n)) * r
    ledger['synthetic_fft_payload_reads'] += math.prod(main) * r * int(math.log2(n))
    return result


def signed_kronecker(a, b, q, ledger):
    r = len(a)
    width = 2 * q + (r - 1).bit_length() + 4
    base = 1 << width
    av = bv = 0
    for value in reversed(a):
        av = av * base + value
    for value in reversed(b):
        bv = bv * base + value
    value = av * bv
    result = []
    for _ in range(2 * r - 1):
        digit = (value + base // 2) % base - base // 2
        result.append(digit)
        value = (value - digit) // base
    assert value == 0, 'Kronecker width insufficient for exact signed decoding'
    ledger['signed_integer_multiplications'] += 1
    ledger['maximum_integer_operand_bits'] = max(ledger['maximum_integer_operand_bits'], abs(av).bit_length(), abs(bv).bit_length())
    return result


def ring_product(a, b, q, ledger):
    ar, ai = [x[0] for x in a], [x[1] for x in a]
    br, bi = [x[0] for x in b], [x[1] for x in b]
    rr = signed_kronecker(ar, br, q, ledger)
    ii = signed_kronecker(ai, bi, q, ledger)
    ri = signed_kronecker(ar, bi, q, ledger)
    ir = signed_kronecker(ai, br, q, ledger)
    r = len(a)
    full = [(x - y, z + w) for x, y, z, w in zip(rr, ii, ri, ir)]
    result = []
    for k in range(r):
        value = full[k]
        if k + r < len(full):
            value = csub(value, full[k + r])
        result.append((tz(value[0], q + int(math.log2(r))), tz(value[1], q + int(math.log2(r)))))
    return result


def scalar_cyclic_convolution(f, g, shape, q, phases, ledger):
    main, r = shape[:-1], shape[-1]
    total_main = math.prod(main)
    twisted_f = [[cmul(f[j * r + k], phases[k], q) for k in range(r)] for j in range(total_main)]
    twisted_g = [[cmul(g[j * r + k], phases[k], q) for k in range(r)] for j in range(total_main)]
    # Complete main-axis transforms keep suffix polynomials as record payloads.
    for axis in range(len(main)):
        twisted_f = ring_axis_pass(twisted_f, main, axis, r, False, ledger)
        twisted_g = ring_axis_pass(twisted_g, main, axis, r, False, ledger)
    product = [ring_product(a, b, q, ledger) for a, b in zip(twisted_f, twisted_g)]
    for axis in reversed(range(len(main))):
        product = ring_axis_pass(product, main, axis, r, True, ledger)
    result = []
    for poly in product:
        for k, value in enumerate(poly):
            untwisted = cmul(value, conjugate(phases[k]), q)
            result.append((untwisted[0] * total_main, untwisted[1] * total_main))
    ledger['coefficient_twists'] += 3 * math.prod(shape)
    return result


def source_transform(data, source_shape, target_shape, matrices, q, chirps, suffix_phases, ledger, opposite=False):
    if opposite:
        data = [conjugate(x) for x in data]
    current = source_shape
    for axis in range(len(source_shape)):
        data, current = real_axis_pass(data, current, axis, matrices[axis][0], q + 64, ledger)
    assert current == target_shape
    chirped = [cmul(conjugate(a), x, q) for a, x in zip(chirps, data)]
    transformed = scalar_cyclic_convolution(chirps, chirped, target_shape, q, suffix_phases, ledger)
    data = [cmul(conjugate(a), x, q) for a, x in zip(chirps, transformed)]
    for axis in reversed(range(len(source_shape))):
        data, current = real_axis_pass(data, current, axis, matrices[axis][1], q + 64, ledger)
    assert current == source_shape
    gamma = sum(2 * axis[2]['alpha'] ** 2 for axis in matrices)
    data = [(a << gamma, b << gamma) for a, b in data]
    if opposite:
        data = [conjugate(x) for x in data]
    ledger['gaussian_source_transforms'] += 1
    return data


def direct_source_dft(data, source_shape, target_shape, q, indices):
    result = []
    volume = math.prod(source_shape)
    occupied = [(decode(j, source_shape), value) for j, value in enumerate(data) if value != (0, 0)]
    for index in indices:
        frequency = decode(index, source_shape)
        total = mp.mpc(0)
        for key, value in occupied:
            phase = -2j * mp.pi * sum(mp.mpf(t * j * k) / s for s, t, j, k in zip(source_shape, target_shape, key, frequency))
            total += mp.mpc(value[0], value[1]) / (1 << q) * mp.exp(phase)
        result.append(total / volume)
    return result


def direct_integer_convolution(a, b, volume):
    result = [0] * volume
    for j, x in enumerate(a):
        if not x:
            continue
        for k, y in enumerate(b):
            if y:
                result[(j + k) % volume] += x * y
    return result


def nearest_signed_integer(value, denominator):
    if value < 0:
        return -((-value + denominator // 2) // denominator)
    return (value + denominator // 2) // denominator


def run_case(config):
    started = perf_counter()
    q, digit_bits = config['q'], config['digit_bits']
    mp.mp.dps = config['digits']
    assert mp.mp.prec >= q + 128
    source_shape, target_shape = tuple(config['source']), tuple(config['target'])
    assert len(source_shape) == len(target_shape) in (2, 3)
    assert all(t == target_shape[0] for t in target_shape[:-1])
    assert all(t <= target_shape[-1] and 2 * target_shape[-1] % t == 0 for t in target_shape[:-1])
    volume = math.prod(source_shape)
    rng = Random(config['seed'])
    count = config['input_digits']
    assert 2 * count - 1 <= volume
    a = [rng.randrange(1 << digit_bits) for _ in range(count)]
    b = [rng.randrange(1 << digit_bits) for _ in range(count)]
    a[-1] = b[-1] = (1 << digit_bits) - 1
    if config.get('input_mode') == 'cyclic-cut':
        a, b = [0] * volume, [0, (1 << digit_bits) - 1]
        a[-1] = (1 << digit_bits) - 2
    u = crt_checked_source(a, source_shape, q, digit_bits)
    v = crt_checked_source(b, source_shape, q, digit_bits)
    matrices = [setup_axis(s, t, config['alpha'], q) for s, t in zip(source_shape, target_shape)]
    chirps = [to_dyadic(mp.exp(-1j * mp.pi * sum(mp.mpf(s * j * j) / t for s, t, j in zip(source_shape, target_shape, key))), q)
              for key in addresses(target_shape)]
    suffix_phases = [to_dyadic(mp.exp(1j * mp.pi * k / target_shape[-1]), q) for k in range(target_shape[-1])]
    ledger = {key: 0 for key in ('dense_gaussian_axis_passes', 'dense_gaussian_coefficient_products',
                               'dense_gaussian_payload_reads', 'dense_gaussian_payload_writes',
                               'synthetic_fft_axis_passes', 'synthetic_fft_butterflies',
                               'synthetic_fft_payload_reads', 'signed_integer_multiplications',
                               'maximum_integer_operand_bits', 'coefficient_twists', 'gaussian_source_transforms')}
    transformed_u = source_transform(u, source_shape, target_shape, matrices, q, chirps, suffix_phases, ledger)
    direct_count = min(volume, config.get('direct_frequency_limit', volume))
    direct_indices = list(range(volume)) if direct_count == volume else sorted(set([0, volume - 1] + rng.sample(range(1, volume - 1), direct_count - 2)))
    direct_u = direct_source_dft(u, source_shape, target_shape, q, direct_indices)
    transform_error = max(abs(mp.mpc(transformed_u[j][0], transformed_u[j][1]) / (1 << q) - y) for j, y in zip(direct_indices, direct_u))
    transformed_v = source_transform(v, source_shape, target_shape, matrices, q, chirps, suffix_phases, ledger)
    pointwise = [cmul(x, y, q) for x, y in zip(transformed_u, transformed_v)]
    recovered = source_transform(pointwise, source_shape, target_shape, matrices, q, chirps, suffix_phases, ledger, opposite=True)
    integer_scale = volume * volume * (1 << (2 * digit_bits + 4))
    oracle = direct_integer_convolution(a, b, volume)
    actual = [0] * volume
    maximum_real_error = mp.mpf(0)
    maximum_imaginary_error = mp.mpf(0)
    missing_source_scale_wrong = 0
    for key, value in zip(addresses(source_shape), recovered):
        k = crt_inverse(key, source_shape)
        actual[k] = nearest_signed_integer(value[0] * integer_scale, 1 << q)
        maximum_real_error = max(maximum_real_error, abs(mp.mpf(value[0] * integer_scale) / (1 << q) - oracle[k]))
        maximum_imaginary_error = max(maximum_imaginary_error, abs(mp.mpf(value[1] * integer_scale) / (1 << q)))
        missing_source_scale_wrong += nearest_signed_integer(value[0] * (integer_scale // volume), 1 << q) != oracle[k]
    assert actual == oracle, (config, maximum_real_error, actual, oracle)
    assert maximum_real_error < mp.mpf('0.25') and maximum_imaginary_error < mp.mpf('0.25')
    assert missing_source_scale_wrong > 0
    radix = 1 << digit_bits
    input_a = sum(value * radix ** k for k, value in enumerate(a) if value)
    input_b = sum(value * radix ** k for k, value in enumerate(b) if value)
    recovered_integer = sum(value * radix ** k for k, value in enumerate(actual) if value)
    if config.get('input_mode') == 'cyclic-cut':
        assert recovered_integer == input_a * input_b % (radix ** volume - 1)
        assert recovered_integer != input_a * input_b
    else:
        assert recovered_integer == input_a * input_b
    # Independent explicit cyclic cut exercises the CRT homomorphism.
    cut_left, cut_right = crt_forward(volume - 1, source_shape), crt_forward(1, source_shape)
    assert tuple((a + b) % s for a, b, s in zip(cut_left, cut_right, source_shape)) == crt_forward(0, source_shape)
    cut_f = [(0, 0)] * math.prod(target_shape)
    cut_g = [(0, 0)] * math.prod(target_shape)
    cut_f[target_shape[-1] - 1] = (1 << (q - 2), 0)
    cut_g[1] = (1 << (q - 3), 0)
    correct_cut = scalar_cyclic_convolution(cut_f, cut_g, target_shape, q, suffix_phases, ledger)[0]
    wrong_cut = scalar_cyclic_convolution(cut_f, cut_g, target_shape, q, [(1 << q, 0)] * target_shape[-1], ledger)[0]
    expected_cut = mp.mpf(1) / (32 * math.prod(target_shape))
    assert abs(mp.mpf(correct_cut[0]) / (1 << q) - expected_cut) < mp.mpf(2) ** (-q + 32)
    assert abs(mp.mpf(wrong_cut[0]) / (1 << q) + expected_cut) < mp.mpf(2) ** (-q + 32)
    receipt = {'config': config, 'status': 'full dyadic Gaussian CRT synthetic-ring multiplication recovery passed',
               'source_volume': volume, 'target_volume': math.prod(target_shape), 'crt_addresses_checked': 2 * volume,
               'direct_source_frequency_indices': direct_indices,
               'source_transform_error': str(transform_error), 'coefficient_real_error': str(maximum_real_error),
               'coefficient_imaginary_error': str(maximum_imaginary_error), 'recovered_coefficients': volume,
               'input_digit_arrays': [a, b] if volume <= 8192 else None,
               'input_integer_product_hex_sha256': hashlib.sha256(hex(input_a * input_b).encode()).hexdigest(),
               'input_integer_product_bits': (input_a * input_b).bit_length(),
               'input_integer_product': str(input_a * input_b) if (input_a * input_b).bit_length() < 10000 else None,
               'negative_missing_source_scale_wrong_coefficients': missing_source_scale_wrong,
               'negative_missing_suffix_twist': {'correct_cyclic_cut': [str(mp.mpf(x) / (1 << q)) for x in correct_cut],
                                               'incorrect_untwisted_cut': [str(mp.mpf(x) / (1 << q)) for x in wrong_cut],
                                               'expected_coefficient': str(expected_cut)},
               'axis_setup': [x[2] for x in matrices], 'movement_ledger': ledger, 'seconds': perf_counter() - started,
               'limitations': ['finite dense Gaussian reference passes are charged and do not instantiate the fast tensor-cell producer',
                               'bounded CRT tree permutation is checked exactly; tiny cases use explicit reference routes, without an all-size rowbank stock claim',
                               'no asymptotic complexity or campaign cutoff is inferred from finite success']}
    if config.get('row_output'):
        Path(config['row_output']).write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error('one to four allocated single-thread CPU workers')
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[key] = '1'
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    configs = json.loads(Path(args.config).read_text())
    for j, config in enumerate(configs):
        config['row_output'] = str(output / f'row-{j}.json')
    started = perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        rows = list(executor.map(run_case, configs))
    result = {'status': 'bounded full dyadic Gaussian CRT multiplication pipeline passed', 'workers': args.workers,
              'dependency': {'mpmath': mp.__version__}, 'source_sha256': SOURCE_SHA256_AT_IMPORT,
              'rows': rows, 'seconds': perf_counter() - started}
    (output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'coefficient_errors': [row['coefficient_real_error'] for row in rows]}))


if __name__ == '__main__':
    main()
