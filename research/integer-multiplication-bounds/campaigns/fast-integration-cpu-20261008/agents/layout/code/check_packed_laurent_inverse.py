#!/usr/bin/env python3
"""Actual signed Kronecker Laurent inverse against the GLOBAL cyclic N solve.

The full packed two-dimensional input is generated and multiplied. A rank-two
input permits an independent global reference with four one-dimensional solves;
this reference shortcut does not replace the tensor packed multiplication.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from pathlib import Path
from random import Random
from time import perf_counter

import gmpy2
import mpmath as mp


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def encode(point, base):
    answer = 0
    for coordinate in point:
        answer = answer * base + coordinate
    return answer


def pack(rows, slot_bytes, degree):
    buffer = bytearray((degree + 1) * slot_bytes)
    for index, value in rows:
        buffer[index * slot_bytes:(index + 1) * slot_bytes] = value.to_bytes(slot_bytes, 'little')
    return gmpy2.mpz(int.from_bytes(buffer, 'little'))


def truncate_signed(value, bits):
    return (abs(value) >> bits) * (-1 if value < 0 else 1)


def run(config, cyclic, laurent):
    started = perf_counter()
    shape = tuple(config['source'])
    target, side, radius = config['target'], config['side'], config['radius']
    alpha, bits = config['alpha'], config['bits']
    d = len(shape)
    assert d == 2 and side % 2 == 0
    origins = tuple(config.get('origins', [(2*s + target-s)//(2*(target-s)) for s in shape]))
    low = -side // 2 - radius
    length = side + 2 * radius
    high = low + length - 1
    with mp.workprec(bits + 512):
        theta = [mp.mpf(target - s) / s for s in shape]
        reserve = sum(mp.pi * alpha**2 * th * max(low*low, high*high) / mp.log(2)
                      for th in theta)
        reserve_bits = int(mp.ceil(reserve))
    work_bits = bits + reserve_bits + 96
    rng = Random(config['seed'])
    components = [[[rng.randrange(-8, 9) for _ in range(s)] for s in shape] for _ in range(2)]
    global_solutions = []
    global_receipts = []
    kernels = []
    with mp.workprec(work_bits):
        for i, (s, origin) in enumerate(zip(shape, origins)):
            assert 0 <= origin + low <= origin + high < s, 'unwrapped retained cell touches a source-period cut'
            for a in range(low, high + 1):
                assert cyclic.selector(origin + a, s, target) == cyclic.selector(origin, s, target) + a
            reference = cyclic.CyclicGaussianReference(s, target, alpha, bits + 48)
            axis_solutions = []
            for component in components:
                rhs = [mp.mpf(value) / 64 for value in component[i]]
                solution = reference.solve(rhs)
                certificate = reference.residual_certificate(rhs, solution)
                assert certificate['solution_error_upper'] < certificate['target']
                axis_solutions.append(solution)
                global_receipts.append(certificate)
            global_solutions.append(axis_solutions)
            kernels.append(laurent.regular_inverse_kernel(s, target, alpha**2, origin, radius,
                           target_bits=bits, reserve_bits=reserve_bits))
        scale = 1 << work_bits
        input_rows = [[], []]
        for a in itertools.product(range(length), repeat=d):
            local = tuple(x + low for x in a)
            point = tuple(origin + x for origin, x in zip(origins, local))
            value = sum(math.prod(component[i][j] for i, j in enumerate(point))
                        for component in components)
            diagonal = mp.exp(-sum(mp.pi * alpha**2 * th * x*x for th, x in zip(theta, local)))
            diagonal_word = int(mp.nint(diagonal * scale))
            input_word = abs(value) * scale // (64**d)
            rounded = truncate_signed(diagonal_word * input_word, work_bits)
            input_rows[value < 0].append((encode(a, length + 2*radius), rounded))
        base = length + 2*radius
        kernel_rows = [[], []]
        for hp in itertools.product(range(2*radius + 1), repeat=d):
            # Kernel API b_h acts from i+h. A polynomial product uses b_-h.
            value = mp.mpf(1)
            rounded_prefix = scale
            for i, x in enumerate(hp):
                coefficient = kernels[i]['coefficients'][radius - x]
                value *= coefficient
                rounded_prefix = int(mp.nint(mp.mpf(rounded_prefix) * coefficient))
            kernel_rows[rounded_prefix < 0].append((encode(hp, base), abs(rounded_prefix)))
        input_degree = encode((length-1,) * d, base)
        kernel_degree = encode((2*radius,) * d, base)
        assert input_degree + kernel_degree < base**d
        slot_bits = 8 * math.ceil((2*work_bits + math.ceil(math.log2(length**d)) + 8)/8)
        slot_bytes = slot_bits//8
        ip, im = [pack(rows, slot_bytes, input_degree) for rows in input_rows]
        kp, km = [pack(rows, slot_bytes, kernel_degree) for rows in kernel_rows]
        products = [int(ip*kp), int(im*km), int(ip*km), int(im*kp)]
        mask = (1 << slot_bits) - 1
        maximum_error = mp.mpf(0)
        maximum_wrong_chirp_error = mp.mpf(0)
        checked = 0
        for output in itertools.product(range(-side//2, side//2), repeat=d):
            index = encode(tuple(x-low+radius for x in output), base)
            parts = [(value >> (slot_bits*index)) & mask for value in products]
            numerator = parts[0] + parts[1] - parts[2] - parts[3]
            unchirped = mp.mpf(numerator)/(scale*scale)
            output_diagonal = mp.exp(sum(mp.pi*alpha**2*th*x*x for th,x in zip(theta,output)))
            output_diagonal_word = int(mp.nint(output_diagonal * scale))
            output_word = truncate_signed(numerator * output_diagonal_word, 2*work_bits)
            computed = mp.mpf(output_word) / scale
            reference = sum(math.prod(global_solutions[i][c][origins[i]+x]
                            for i,x in enumerate(output)) for c in range(2))
            maximum_error = max(maximum_error,abs(computed-reference))
            maximum_wrong_chirp_error = max(maximum_wrong_chirp_error,abs(unchirped-reference))
            checked += 1
        amplification = mp.mpf(2)**reserve_bits
        # Telescoping a tensor product also charges the other inverse factors'
        # row norms. The bare Laurent inverse is slightly larger than one.
        tensor_norm_factor = math.prod(1/(1-kernel['unweighted_perturbation_row_bound']) +
                                      kernel['analytic_kernel_row_error'] for kernel in kernels)
        analytic_tail = (amplification * tensor_norm_factor *
                         sum(kernel['analytic_kernel_row_error'] for kernel in kernels))
        numerical_pass = maximum_error < mp.mpf(2)**(-bits)
        analytic_tail_pass = analytic_tail < mp.mpf(2)**(-bits)
        if config.get('expected_radius_failure'):
            assert not numerical_pass, 'the radius-negative fixture unexpectedly passed'
        else:
            assert analytic_tail_pass, analytic_tail
            assert numerical_pass, maximum_error
        assert maximum_wrong_chirp_error > mp.mpf('1e-8')

        def scalar(value):
            return mp.nstr(value, math.ceil(work_bits*math.log10(2))+8) if hasattr(value,'_mpf_') else value

        status = ('insufficient inverse radius fails requested numerical precision'
                  if config.get('expected_radius_failure') else
                  'genuine packed Laurent inverse agrees with global cyclic N inverse')
        return {'config':config,'status':status,
            'origins':origins,'retained_input_distances':[low,high],
            'target_bits':bits,'reserve_bits':reserve_bits,'work_bits':work_bits,
            'maximum_error':scalar(maximum_error),'analytic_local_kernel_tail_after_reserve':scalar(analytic_tail),
            'tensor_operator_norm_factor':scalar(tensor_norm_factor),
            'numerical_precision_pass':numerical_pass,'analytic_local_tail_pass':analytic_tail_pass,
            'negative_omitted_output_chirp_error':scalar(maximum_wrong_chirp_error),
            'input_records':length**d,'output_records_checked':checked,'kernel_records':(2*radius+1)**d,
            'kronecker_base':base,'slot_bits':slot_bits,'signed_integer_products':4,
            'maximum_integer_operand_bits':max(x.bit_length() for x in [ip,im,kp,km]),
            'online_outer_factor_policy':'integer dyadic products of frozen P-bit input/output diagonal words',
            'global_reference_receipts':[{k:scalar(v) for k,v in receipt.items()} for receipt in global_receipts],
            'kernel_receipts':[{k:scalar(v) for k,v in kernel.items() if k!='coefficients'} for kernel in kernels],
            'seconds':perf_counter()-started,
            'limitations':['global reference coefficients are high precision plus analytic alias tail, not directed interval proof',
                'one regular cell with paid explicit halo; joint all-size gathering/exception repair is a separate theorem',
                'analytic local kernel tail excludes global phase-boundary replacement, which this numerical global oracle checks',
                'rank-two reference inputs; actual packed input and products execute every tensor record']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cyclic-api',required=True)
    parser.add_argument('--laurent-api',required=True)
    parser.add_argument('--config',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    assert gmpy2.__version__=='2.3.0'
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    cyclic=module('cyclic_gaussian_reference',args.cyclic_api)
    sys.modules['cyclic_gaussian_reference']=cyclic
    laurent=module('frozen_laurent_kernel',args.laurent_api)
    rows=[]
    for i,config in enumerate(json.loads(Path(args.config).read_text())):
        row=run(config,cyclic,laurent);rows.append(row)
        (out/f'row-{i}.json').write_text(json.dumps(row,indent=2)+'\n')
    result={'status':'packed localized inverse numerical controls passed','rows':rows,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cyclic_api_sha256':hashlib.sha256(Path(args.cyclic_api).read_bytes()).hexdigest(),
        'laurent_api_sha256':hashlib.sha256(Path(args.laurent_api).read_bytes()).hexdigest()}
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'seconds':[r['seconds'] for r in rows]}))


if __name__=='__main__':main()
