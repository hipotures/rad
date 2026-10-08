#!/usr/bin/env python3
"""Independent alternating-frame algebra and actual spaced-bit tape controls.

No producer imports. Integer Fourier coefficients check every ambient
difference, including zero entries between complement cosets. A separate
operator pipeline uses Gaussian integers, selected-only row shears and
ordinary C children. Complete physical counters include chunk gaps and
spectator intervals and charge aligned tape-head motion.
"""

import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import time


def dot(a, b):
    return (a & b).bit_count() % 2


def embed(a, columns):
    out = 0
    for j, v in enumerate(columns):
        if (a >> j) & 1:
            out ^= v
    return out


def rank(columns):
    pivots = {}
    for v in columns:
        while v:
            k = v.bit_length() - 1
            if k not in pivots:
                pivots[k] = v
                break
            v ^= pivots[k]
    return len(pivots)


def solve(rows, rhs):
    n = len(rows)
    a = [rows[j] | (((rhs >> j) & 1) << n) for j in range(n)]
    for k in range(n):
        p = next(j for j in range(k, n) if (a[j] >> k) & 1)
        a[k], a[p] = a[p], a[k]
        for j in range(n):
            if j != k and (a[j] >> k) & 1:
                a[j] ^= a[k]
    assert all((v & ((1 << n) - 1)) == 1 << j for j, v in enumerate(a))
    return sum(((v >> n) & 1) << j for j, v in enumerate(a))


def project(z, basis):
    rows = [sum(dot(a, b) << j for j, b in enumerate(basis)) for a in basis]
    rhs = sum(dot(z, v) << j for j, v in enumerate(basis))
    return embed(solve(rows, rhs), basis) if basis else 0


def walsh(values):
    a = list(values)
    h = 1
    while h < len(a):
        for k in range(0, len(a), 2 * h):
            for j in range(k, k + h):
                a[j], a[j + h] = a[j] + a[j + h], a[j] - a[j + h]
        h *= 2
    return a


def quadratic(a, basis):
    wt = embed(a, basis).bit_count()
    assert wt % 2 == 0
    return (wt // 2) % 2


def space_case(n, basis):
    r = len(basis)
    assert r > 0 and r % 2 == 0 and rank(basis) == r
    assert all(dot(v, v) == 0 for v in basis)
    assert all(dot(u, v) == int(j == (k ^ 1))
               for k, u in enumerate(basis) for j, v in enumerate(basis))
    coordinates = {embed(a, basis): a for a in range(1 << r)}
    linear = [quadratic(1 << j, basis) for j in range(r)]
    arf = sum(linear[j] * linear[j + 1] for j in range(0, r, 2)) % 2
    for a in range(1 << r):
        polynomial = sum(linear[j] * ((a >> j) & 1) for j in range(r))
        polynomial += sum(((a >> j) & 1) * ((a >> (j + 1)) & 1)
                          for j in range(0, r, 2))
        assert quadratic(a, basis) == polynomial % 2
    phase = [1 - 2 * quadratic(coordinates[project(z, basis)], basis)
             for z in range(1 << n)]
    fourier = walsh(phase)
    digest = sha256()
    for difference, actual in enumerate(fourier):
        expected = 0
        if difference in coordinates:
            expected = (1 - 2 * (arf ^ quadratic(coordinates[difference], basis)))
            expected *= 1 << (n - r // 2)
        assert actual == expected
        digest.update(f'{difference}:{actual};'.encode())
    # The projector is symmetric, idempotent and alternating, including its
    # diagonal. These assertions use a general binary Gram-system solver.
    columns = [project(1 << j, basis) for j in range(n)]
    for j, v in enumerate(columns):
        assert ((v >> j) & 1) == 0 and project(v, basis) == v
        assert all(((v >> k) & 1) == ((columns[k] >> j) & 1) for k in range(n))
    assert sum(1 - 2 * quadratic(a, basis) for a in range(1 << r)) == (
        1 - 2 * arf) * (1 << (r // 2))
    return {'ambient': n, 'basis': basis, 'rank': r, 'arf': arf,
            'ambient_differences': len(fourier),
            'zero_outside_subspace': (1 << n) - (1 << r),
            'kernel_sha256': digest.hexdigest()}


def unit(z, k):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[k % 4]


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def scale(a, t):
    return a[0] * t, a[1] * t


def c_step(data, bit):
    out = [None] * len(data)
    for x in range(len(data)):
        if x & (1 << bit):
            continue
        y = x | (1 << bit)
        u, v = data[x], data[y]
        # Common numerator denominator doubles at this ordinary C step.
        out[x] = plus(plus(u, unit(u, 1)), plus(v, unit(v, -1)))
        out[y] = plus(plus(u, unit(u, -1)), plus(v, unit(v, 1)))
    return out


def selected(x, banks, f, k, rho):
    return [sum(((x >> (a * f * k + j * k + rho)) & 1) << j for j in range(f))
            for a in range(banks)]


def replace_selected(x, words, f, k, rho):
    for a, word in enumerate(words):
        for j in range(f):
            bit = a * f * k + j * k + rho
            x = (x & ~(1 << bit)) | (((word >> j) & 1) << bit)
    return x


def permutation(data, mapping):
    out = [None] * len(data)
    for x, value in enumerate(data):
        destination = mapping(x)
        assert out[destination] is None
        out[destination] = value
    assert all(v is not None for v in out)
    return out


def extension(basis, n):
    out = list(basis)
    for j in range(n):
        if rank(out + [1 << j]) > len(out):
            out.append(1 << j)
    assert len(out) == n
    return out


def pipeline_case(n, basis, f, k, rho, rng, exhaustive=False):
    r = len(basis)
    columns = extension(basis, n)
    inverse = {embed(a, columns): a for a in range(1 << n)}
    linear = [quadratic(1 << j, basis) for j in range(r)]
    arf = sum(linear[j] * linear[j + 1] for j in range(0, r, 2)) % 2
    nbits = n * f * k
    rows = 1 << nbits

    def basis_map(x, backward):
        words = selected(x, n, f, k, rho)
        out = [0] * n
        for j in range(f):
            v = sum(((words[a] >> j) & 1) << a for a in range(n))
            v = inverse[v] if backward else embed(v, columns)
            for a in range(n):
                out[a] |= ((v >> a) & 1) << j
        return replace_selected(x, out, f, k, rho)

    def shear(x, source, target):
        words = selected(x, n, f, k, rho)
        words[target] ^= words[source]
        return replace_selected(x, words, f, k, rho)

    def phase(x):
        words = selected(x, n, f, k, rho)
        q = sum(quadratic(sum(((words[a] >> j) & 1) << a for a in range(r)), basis)
                for j in range(f)) % 2
        wt = sum(words[a].bit_count() for a in range(r)) % 4
        return q, wt

    probes = []
    if exhaustive:
        for x in range(rows):
            data = [(0, 0)] * rows
            data[x] = (1, 0)
            probes.append(data)
    probes.append([(rng.randrange(-3, 4), rng.randrange(-3, 4)) for _ in range(rows)])
    digest = sha256()
    outputs = 0
    untouched_mask = ((1 << nbits) - 1) ^ sum(1 << (a * f * k + j * k + rho)
                                             for a in range(n) for j in range(f))
    for data in probes:
        work = permutation(data, lambda x: basis_map(x, True))
        work = [unit(z, 2 * phase(x)[0]) for x, z in enumerate(work)]
        for a in range(0, r, 2):
            # Exchange only selected words; the chunk gaps are spectators.
            for source, target in ((a, a + 1), (a + 1, a), (a, a + 1)):
                for x in range(rows):
                    assert (shear(x, source, target) & untouched_mask) == (x & untouched_mask)
                work = permutation(work, lambda x, s=source, t=target: shear(x, s, t))
        work = [unit(z, phase(x)[1]) for x, z in enumerate(work)]
        for a in range(r):
            for j in range(f):
                work = c_step(work, a * f * k + j * k + rho)
        work = [unit(z, phase(x)[1] + 2 * phase(x)[0] + 2 * f * arf - r * f // 2)
                for x, z in enumerate(work)]
        work = permutation(work, lambda x: basis_map(x, False))
        for x, value in enumerate(work):
            expected = (0, 0)
            for delta in range(1 << (r * f)):
                difference = 0
                q = f * arf
                for j in range(f):
                    a = (delta >> (j * r)) & ((1 << r) - 1)
                    v = embed(a, basis)
                    q += quadratic(a, basis)
                    for bank in range(n):
                        difference |= ((v >> bank) & 1) << (bank * f * k + j * k + rho)
                expected = plus(expected, scale(data[x ^ difference], 1 - 2 * (q % 2)))
            expected = scale(expected, 1 << (r * f // 2))
            assert value == expected
            digest.update(f'{value[0]},{value[1]};'.encode())
            outputs += 1
    return {'ambient_banks': n, 'basis': basis, 'f': f, 'K': k, 'rho': rho,
            'physical_address_bits': nbits, 'probes': len(probes), 'checked_outputs': outputs,
            'ordinary_f_axis_children': r, 'selected_word_shears': 3 * r // 2,
            'output_sha256': digest.hexdigest()}


def counter_case(banks, f, k, rho, active, linear, gaps):
    assert len(active) % 2 == 0 and len(set(active)) == len(active)
    assert len(gaps) == banks + 1 and 0 <= rho < k
    width = f * k
    offsets = []
    address_bits = gaps[0]
    for a in range(banks):
        offsets.append(address_bits)
        address_bits += width + gaps[a + 1]
    assert address_bits <= 19
    locations = {}
    for a, offset in enumerate(offsets):
        for j in range(width):
            locations[offset + j] = a, j
    mate = dict(pair for a, b in zip(active[::2], active[1::2])
                for pair in ((a, b), (b, a)))
    global_counter = [0] * address_bits
    bank_tapes = [[0] * width for _ in range(banks)]
    mask = [int(j % k == rho) for j in range(width)]
    heads = [0] * (banks + 1)  # Include the selected-position mask tape.
    global_head = 0
    q = wt = flips = bank_moves = global_moves = selected_flips = 0
    digest = sha256()

    def move_banks(j):
        nonlocal bank_moves
        for a in range(len(heads)):
            bank_moves += abs(heads[a] - j)
            heads[a] = j

    rows = 1 << address_bits
    for address in range(rows):
        words = [sum(((address >> (offsets[a] + j * k + rho)) & 1) << j
                     for j in range(f)) for a in range(banks)]
        expected_q = sum((words[a] & words[b]).bit_count()
                         for a, b in zip(active[::2], active[1::2]))
        expected_q += sum(linear[a] * words[a].bit_count() for a in active)
        expected_wt = sum(words[a].bit_count() for a in active) % 4
        assert (q, wt) == (expected_q % 2, expected_wt)
        assert sum(bit << j for j, bit in enumerate(global_counter)) == address
        digest.update(bytes((q, wt)))
        if address + 1 == rows:
            continue
        for bit in range(address_bits):
            global_moves += abs(global_head - bit)
            global_head = bit
            old = global_counter[bit]
            if bit in locations:
                a, j = locations[bit]
                move_banks(j)
                assert bank_tapes[a][heads[a]] == old
                if a in mate and mask[heads[-1]]:
                    q ^= linear[a] ^ bank_tapes[mate[a]][heads[mate[a]]]
                    wt = (wt + 1 - 2 * old) % 4
                    selected_flips += 1
                bank_tapes[a][heads[a]] ^= 1
            global_counter[bit] ^= 1
            flips += 1
            if old == 0:
                break
        global_moves += global_head
        global_head = 0
        move_banks(0)
    # Every increment with carry length l pays at most 2l global steps and
    # 2l steps on each aligned tape, including whole-bank resets.
    assert flips < 2 * rows
    assert global_moves <= 4 * rows
    assert bank_moves <= 4 * (banks + 1) * rows
    return {'banks': banks, 'f': f, 'K': k, 'rho': rho, 'active_banks': active,
            'spectator_gap_bits': gaps, 'complete_addresses': rows,
            'symbol_flips': flips, 'selected_phase_flips': selected_flips,
            'global_counter_head_moves': global_moves, 'aligned_bank_head_moves': bank_moves,
            'initialized_counter_symbols': address_bits + (banks + 1) * width,
            'phase_sha256': digest.hexdigest()}


def nesting_case(n, residual, other):
    whole = other + residual
    assert rank(whole) == len(whole)
    assert all(dot(a, b) == 0 for a in other for b in residual)
    for z in range(1 << n):
        p = project(z, other)
        pe = project(z, residual)
        v = project(z, whole)
        assert v == p ^ pe
        forward = (v.bit_count() - p.bit_count()) % 4
        reverse = (p.bit_count() - v.bit_count()) % 4
        assert forward == reverse == pe.bit_count() % 4
        complement = z ^ p
        assert (p.bit_count() + complement.bit_count()) % 4 == z.bit_count() % 4
    return {'ambient': n, 'other': other, 'residual': residual,
            'both_orientations': 1 << n, 'complement_endpoints': 1 << n}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert not args.output.exists(), 'Use a fresh run'
    started = time.monotonic()
    rng = random.Random(607)
    spaces, seen = [], set()
    for n in range(3, 8):
        even = [x for x in range(1, 1 << n) if x.bit_count() % 2 == 0]
        for a, b in product(even, repeat=2):
            key = n, tuple(sorted((a, b, a ^ b)))
            if dot(a, b) and key not in seen:
                seen.add(key)
                spaces.append(space_case(n, [a, b]))
    for n, basis in ((6, [3, 5, 24, 40]), (8, [3, 5, 24, 40]),
                     (9, [3, 5, 24, 40, 192, 320])):
        spaces.append(space_case(n, basis))
    pipeline = [pipeline_case(3, [3, 5], 1, 2, 1, rng, exhaustive=True),
                pipeline_case(4, [3, 5], 1, 2, 0, rng),
                pipeline_case(3, [3, 5], 2, 2, 0, rng)]
    configs = [(2, 1, 3, rho, [0, 1], [1, 1, 1]) for rho in range(3)]
    configs += [(2, 2, 3, rho, [0, 1], [0, 0, 0]) for rho in range(3)]
    configs += [(3, 2, 2, rho, [0, 2], [1, 1, 1, 1]) for rho in range(2)]
    configs += [(4, 1, 3, rho, [0, 1, 2, 3], [1, 0, 1, 0, 1]) for rho in range(3)]
    counters = [counter_case(m, f, k, rho, active,
                             [rng.randrange(2) for _ in range(m)], gaps)
                for m, f, k, rho, active, gaps in configs]
    nesting = [nesting_case(4, [3, 5], [8]), nesting_case(6, [3, 5], [24, 40]),
               nesting_case(7, [3, 5, 24, 40], [64])]
    # Wrongly treating the chunk gap as another selected column changes a
    # phase at address 1, whereas rho=1 makes all true selected bits zero.
    assert quadratic(1, [3, 5]) == 1
    negatives = {'missing_arf': {'basis': [3, 5], 'correct': '-1/2', 'wrong': '1/2'},
                 'unmasked_chunk_gap': {'K': 2, 'rho': 1, 'address': 1,
                                       'correct_q': 0, 'wrong_q': 1},
                 'whole_bank_swap_changes_spectator': {'K': 2, 'rho': 1,
                                                        'address': 1, 'correct': 1, 'wrong': 4}}
    result = {'status': 'PASS independent alternating algebra, spaced counters and selected-only pipeline',
              'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(), 'seed': 607,
              'plane_spaces': len(seen), 'space_cases': spaces, 'pipeline_cases': pipeline,
              'counter_cases': counters, 'nesting_cases': nesting, 'negative_controls': negatives,
              'ambient_differences': sum(x['ambient_differences'] for x in spaces),
              'zero_difference_entries': sum(x['zero_outside_subspace'] for x in spaces),
              'pipeline_output_values': sum(x['checked_outputs'] for x in pipeline),
              'counter_addresses': sum(x['complete_addresses'] for x in counters),
              'elapsed_seconds': time.monotonic() - started,
              'scope': 'Primitive transfer; no odd finite network or improved exponent claimed'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('space_cases', 'pipeline_cases', 'counter_cases', 'nesting_cases')},
                     sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
