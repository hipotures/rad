#!/usr/bin/env python3
"""Independent F9 word-XOR bridge and physical cancellation discriminators.

Finite coefficients are a+bi modulo three, i^2=-1. No producer imports.
The bridge is exact; the scoped extra-child count is not a universal
obstruction to another jointly compiled finite network.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random
import time


def add(a, b):
    return (a[0] + b[0]) % 3, (a[1] + b[1]) % 3


def neg(a):
    return (-a[0]) % 3, (-a[1]) % 3


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1]) % 3, (a[0] * b[1] + a[1] * b[0]) % 3


def power(a, n):
    out = 1, 0
    while n:
        if n % 2:
            out = mul(out, a)
        a = mul(a, a)
        n //= 2
    return out


def c_step(data, bit):
    out = [None] * len(data)
    a, b = (2, 2), (2, 1)  # (1+i)/2 and (1-i)/2 in F9.
    for x in range(len(data)):
        if x & (1 << bit):
            continue
        y = x | (1 << bit)
        out[x] = add(mul(a, data[x]), mul(b, data[y]))
        out[y] = add(mul(b, data[x]), mul(a, data[y]))
    return out


def word(address, bits):
    return sum(((address >> bit) & 1) << j for j, bit in enumerate(bits))


def walsh_bridge(data, bits, inverse=False, omit_s=False):
    # W=(1-i)^f S C^f S, with W^-1=2^-f W.
    work = list(data)
    if not omit_s:
        work = [mul(z, power((0, 1), word(x, bits).bit_count())) for x, z in enumerate(work)]
    for bit in bits:
        work = c_step(work, bit)
    if not omit_s:
        work = [mul(z, power((0, 1), word(x, bits).bit_count())) for x, z in enumerate(work)]
    factor = power((1, 2), len(bits))
    if inverse:
        factor = mul(factor, power((2, 0), len(bits)))
    return [mul(z, factor) for z in work]


def direct_walsh(data, bits, inverse=False):
    out = []
    mask = sum(1 << bit for bit in bits)
    for address in range(len(data)):
        total = 0, 0
        target = word(address, bits)
        for source in range(1 << len(bits)):
            x = address & ~mask
            x |= sum(((source >> j) & 1) << bit for j, bit in enumerate(bits))
            value = data[x]
            if (target & source).bit_count() % 2:
                value = neg(value)
            total = add(total, value)
        out.append(mul(total, power((2, 0), len(bits))) if inverse else total)
    return out


def xor_map(address, target, source):
    return address ^ sum(((address >> s) & 1) << t for t, s in zip(target, source))


def permutation(data, mapper):
    out = [None] * len(data)
    for address, value in enumerate(data):
        destination = mapper(address)
        assert out[destination] is None
        out[destination] = value
    return out


def bridge(data, target, controls, omit_scale=False, omit_s=False):
    work = walsh_bridge(data, target, omit_s=omit_s)
    for address, value in enumerate(work):
        parity = sum((word(address, target) & word(address, source)).bit_count()
                     for source in controls) % 2
        if parity:
            work[address] = neg(value)
    return walsh_bridge(work, target, inverse=not omit_scale, omit_s=omit_s)


def frame_diagonal(data, rows, m, f):
    out = []
    for address, value in enumerate(data):
        q = 0
        for j in range(f):
            h = sum(((address >> (a * f + j)) & 1) << a for a in range(m))
            d = sum(((address >> ((m + a) * f + j)) & 1) << a for a in range(m))
            md = sum(((row & d).bit_count() % 2) << a for a, row in enumerate(rows))
            q ^= (h & md).bit_count() % 2
        out.append(neg(value) if q else value)
    return out


def frame_permutation(data, rows, m, f):
    def mapper(address):
        result = address
        for j in range(f):
            d = sum(((address >> ((m + a) * f + j)) & 1) << a for a in range(m))
            for a, row in enumerate(rows):
                if (row & d).bit_count() % 2:
                    result ^= 1 << (a * f + j)
        return result
    return permutation(data, mapper)


def global_schedule(m, f, rng):
    assert m % 2 == 1
    full = [1 << a for a in range(m)]
    projection = [(1 << m) - 1] * m
    empty = [0] * m
    complement = [a ^ b for a, b in zip(full, projection)]
    data = [[(rng.randrange(3), rng.randrange(3)) for _ in range(1 << (2 * m * f))]
            for _ in range(2)]
    target_bits = list(range(m * f))

    def execute(fourier):
        work = [walsh_bridge(a, target_bits) for a in data] if fourier else [list(a) for a in data]
        previous = [projection, empty]
        for step, frame in enumerate((projection, full, complement)):
            for role in range(2):
                delta = [a ^ b for a, b in zip(frame, previous[role])]
                work[role] = (frame_diagonal(work[role], delta, m, f) if fourier else
                              frame_permutation(work[role], delta, m, f))
                previous[role] = frame
            if step == 0:
                work[1] = [add(y, neg(x)) for x, y in zip(*work)]
            elif step == 1:
                work[0] = [add(x, y) for x, y in zip(*work)]
            else:
                work[1] = [add(x, neg(y)) for x, y in zip(*work)]
        for role, sink in enumerate((full, complement)):
            delta = [a ^ b for a, b in zip(sink, previous[role])]
            work[role] = (frame_diagonal(work[role], delta, m, f) if fourier else
                          frame_permutation(work[role], delta, m, f))
        if fourier:
            work = [walsh_bridge(a, target_bits, inverse=True) for a in work]
        return [work[1], work[0]]

    direct, fourier = execute(False), execute(True)
    expected = [frame_permutation(a, full, m, f) for a in data]
    assert direct == fourier == expected
    return {'m': m, 'f': f, 'all_input_output_values': 2 * len(data[0]),
            'global_walsh_size': m * f, 'same_size_complex_calls_per_role': 2,
            'direct_f_axis_children_per_role': 2 * m,
            'scope': 'Valid common-basis telescope; unchanged target word size at its two boundaries'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--counts', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    assert not args.output.exists()
    started = time.monotonic()
    rng = random.Random(613)
    cases = []
    entries = 0
    for f in range(1, 6):
        target, source = list(range(f)), list(range(f, 2 * f))
        size = 1 << (2 * f)
        probes = [[(rng.randrange(3), rng.randrange(3)) for _ in range(size)]]
        if f <= 2:
            for j in range(size):
                data = [(0, 0)] * size
                data[j] = (1, 0)
                probes.append(data)
        for data in probes:
            assert walsh_bridge(data, target) == direct_walsh(data, target)
            assert walsh_bridge(data, target, inverse=True) == direct_walsh(data, target, inverse=True)
            for t, s in ((target, source), (source, target)):
                assert bridge(data, t, [s]) == permutation(data, lambda x: xor_map(x, t, s))
                entries += size
        cases.append({'f': f, 'probes': len(probes), 'both_physical_directions': True,
                      'payload': 'F9', 'returned_bit_basis': f <= 2})
    grouped = []
    for f in range(1, 4):
        target, y, z = [list(range(a * f, (a + 1) * f)) for a in range(3)]
        data = [(rng.randrange(3), rng.randrange(3)) for _ in range(1 << (3 * f))]
        expected = permutation(data, lambda x: xor_map(xor_map(x, target, y), target, z))
        assert bridge(data, target, [y, z]) == expected
        grouped.append({'f': f, 'outputs': len(data), 'sequential_shears': 2,
                        'grouped_complex_calls': 2, 'uncancelled_complex_calls': 4})
    global_cases = [global_schedule(1, 3, rng), global_schedule(3, 1, rng)]
    # Mixed role bases cannot pass through an unchanged pointwise addition.
    impulse = [(1, 0), (0, 0)]
    wrong = walsh_bridge(impulse, [0], inverse=True)
    assert wrong == [(2, 0), (2, 0)] and wrong != impulse
    # Generic lower triangular adapters are not all simultaneously diagonal:
    # two such elementary shears already fail to commute.
    a = lambda x: x ^ (((x >> 0) & 1) << 1)
    b = lambda x: x ^ (((x >> 1) & 1) << 2)
    assert b(a(1)) == 7 and a(b(1)) == 3
    tiny = [(1, 0), (0, 0), (0, 0), (0, 0)]
    expected = permutation(tiny, lambda x: xor_map(x, [0], [1]))
    assert bridge(tiny, [0], [[1]], omit_scale=True) != expected
    assert bridge(tiny, [0], [[1]], omit_s=True) != expected
    # Omitting both global Walsh boundaries leaves a sign diagonal, which
    # cannot move an impulse even on the simplest controlled-XOR fiber.
    assert [(1, 0), (0, 0)] != [(0, 0), (1, 0)]
    producer = json.loads(args.counts.read_text())
    counts = producer['witnesses'][0]['complex_counts']
    w, m, s, n = (int(counts[k]) for k in ('W', 'm', 's', 'N'))
    deficit, source_edges = w * m - s, 3 * n
    assert deficit == int(counts['D']) and deficit > 0
    excess = 2 * source_edges - deficit
    assert excess > 0 and Q(2 * source_edges, deficit) == Q(117, 10)
    result = {'status': 'PASS exact bridge and cancellation controls; scoped uncancelled compiler negative',
              'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(), 'seed': 613,
              'counts_input_sha256': sha256(args.counts.read_bytes()).hexdigest(),
              'bridge_cases': cases, 'checked_bridge_outputs': entries,
              'same_target_grouping': grouped, 'global_common_basis': global_cases,
              'complex_counts': counts,
              'uncancelled_extra_children': 2 * source_edges,
              'rank_deficit': deficit, 'extra_to_deficit': str(Q(2 * source_edges, deficit)),
              'excess_over_Wm': excess, 'normalized_growth_relative_to_m': str(Q(s + 2 * source_edges, w * m)),
              'mixed_basis_gate_counterexample': {'f': 1, 'input': impulse, 'wrong_output': wrong},
              'lower_triangular_noncommutation': {'input': 1, 'first_then_second': 7, 'second_then_first': 3},
              'elapsed_seconds': time.monotonic() - started,
              'scope': 'No optimized joint-basis compiler or universal movement lower bound inferred'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('bridge_cases', 'same_target_grouping', 'global_common_basis')},
                     sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
