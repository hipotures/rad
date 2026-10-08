#!/usr/bin/env python3
"""Binary-address Bruhat algebra with fixed odd-prime payload symbols.

The scalar and address alphabets are deliberately distinct. These exact
controls do not make whole-word triangular XOR linear-time on tapes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import time

from downstream_binary_shear_interface import apply, inverse, multiply, projection
from downstream_complex_circuit import TripleSideCircuit
from downstream_gaussian import check_sources, require


def identity(n):
    return [1 << i for i in range(n)]


def column_add(rows, target, source):
    return [row ^ ((1 << target) if row >> source & 1 else 0) for row in rows]


def bruhat(rows):
    """Return E1,Pi,E2 over F2 with both E factors lower triangular."""
    n = len(rows)
    current, left, right = list(rows), identity(n), identity(n)
    active_rows, active_columns = list(range(n)), list(range(n))
    while active_rows:
        mask = sum(1 << j for j in active_columns)
        pivot_row = next((i for i in active_rows if current[i] & mask), None)
        if pivot_row is None:
            break
        pivot_column = max(j for j in active_columns if current[pivot_row] >> j & 1)
        for j in active_columns:
            if j < pivot_column and current[pivot_row] >> j & 1:
                current = column_add(current, j, pivot_column)
                right = column_add(right, j, pivot_column)
        for i in active_rows:
            if i > pivot_row and current[i] >> pivot_column & 1:
                current[i] ^= current[pivot_row]
                left[i] ^= left[pivot_row]
        active_rows.remove(pivot_row)
        active_columns.remove(pivot_column)
    e1, e2 = inverse(left, n), inverse(right, n)
    require(e1 is not None and e2 is not None, 'Binary triangular factor became singular')
    for factor in (e1, e2, left, right):
        require(all(factor[i] >> (i + 1) == 0 and factor[i] >> i & 1 for i in range(n)),
                'Bruhat factor is not invertible lower triangular')
    require(all(row.bit_count() <= 1 for row in current), 'Partial permutation has repeated row pivot')
    columns = [row.bit_length() - 1 for row in current if row]
    require(len(set(columns)) == len(columns), 'Partial permutation has repeated column pivot')
    require(multiply(multiply(e1, current), e2) == list(rows), 'Exact binary Bruhat product differs')
    return e1, current, e2


def transform_words(matrix, values):
    out = []
    for row in matrix:
        value = 0
        for j, word in enumerate(values):
            if row >> j & 1:
                value ^= word
        out.append(value)
    return out


def ideal_shear(rows, h, d):
    e1, pivots, e2 = bruhat(rows)
    hh = transform_words(inverse(e1, len(rows)), h)
    dd = transform_words(e2, d)
    calls = 0
    for i, row in enumerate(pivots):
        if not row:
            continue
        j = row.bit_length() - 1
        dd[j] ^= hh[i]
        hh[i], dd[j] = dd[j], hh[i]
        dd[j] ^= hh[i]
        calls += 1
    hh = transform_words(e1, hh)
    dd = transform_words(inverse(e2, len(rows)), dd)
    expected = [a ^ b for a, b in zip(h, transform_words(rows, d))]
    require(hh == expected and dd == list(d), 'Ideal binary word-shear pipeline differs')
    require(calls == len([row for row in pivots if row]), 'Ideal child count differs from binary rank')
    return calls


def matrix_controls():
    rng = random.Random(202610080328)
    checked = addresses = 0
    rank_histogram = {}
    samples = []
    for n in range(1, 9):
        matrices = (list(product(range(1 << n), repeat=n)) if n <= 3 else
                    [tuple(rng.randrange(1 << n) for _ in range(n)) for _ in range(32)])
        matrices += [tuple([0] * n), tuple(identity(n))]
        for rows in matrices:
            _, pivots, _ = bruhat(rows)
            rank = sum(bool(row) for row in pivots)
            rank_histogram[rank] = rank_histogram.get(rank, 0) + 1
            checked += 1
        if n <= 3:
            selected = matrices[:min(12, len(matrices))] + [tuple(identity(n))]
            for rows in selected:
                for width in (1, 2):
                    for address in range(1 << (2 * n * width)):
                        mask = (1 << width) - 1
                        words = [(address >> (i * width)) & mask for i in range(2 * n)]
                        calls = ideal_shear(rows, words[:n], words[n:])
                        addresses += 1
                    if len(samples) < 6:
                        samples.append(dict(dimension=n, column_width=width, rank=calls,
                                            address_cardinality=1 << (2 * n * width),
                                            address_alphabet='binary', payload_alphabet='not used in this matrix test'))
    return dict(exact_factorizations=checked, full_joint_binary_address_checks=addresses,
                rank_histogram=rank_histogram, samples=samples,
                scope='Ideal complete binary word-XOR updates; no linear tape-cost assertion')


def modular_mixer(values, code, prime, reverse=False):
    gates = reversed(code['gates']) if reverse else code['gates']
    for _, ins, outs in gates:
        if reverse:
            for target in outs[1:]:
                values[target] = (values[target] - values[ins[0]]) % prime
            for source in ins[1:]:
                values[ins[0]] = (values[ins[0]] - values[source]) % prime
        else:
            for source in ins[1:]:
                values[ins[0]] = (values[ins[0]] + values[source]) % prime
            for target in outs[1:]:
                values[target] = (values[target] + values[ins[0]]) % prime


def modular_invocation(circuit, code, x, y, scratch, center, prime):
    half = pow(2, -1, prime)

    def inject(sign):
        for i, triple in enumerate(circuit.inputs):
            delta = scratch[code['outputs']['D', triple]] - scratch[code['outputs']['E', triple]]
            y[i] = (y[i] + sign * half * delta) % prime

    def scatter(sign):
        for i, triple in enumerate(circuit.inputs):
            delta = sum(center[j] for j in triple) - center[-1]
            y[i] = (y[i] + sign * half * delta) % prime

    def copy(sign):
        for i, triple in enumerate(circuit.inputs):
            target = code['sources'][triple]
            scratch[target] = (scratch[target] + sign * x[i]) % prime

    def gather(sign):
        for i, triple in enumerate(circuit.inputs):
            for j in triple:
                center[j] = (center[j] + sign * x[i]) % prime
            center[-1] = (center[-1] + sign * x[i]) % prime

    modular_mixer(scratch, code, prime); inject(-1)
    modular_mixer(scratch, code, prime, True); scatter(-1)
    copy(1); gather(1); scatter(1)
    modular_mixer(scratch, code, prime); inject(1)
    modular_mixer(scratch, code, prime, True)
    gather(-1); copy(-1)


def payload_controls():
    circuit = TripleSideCircuit(8)
    code = circuit.compile()
    v, r, h = len(circuit.inputs), code['roles'], circuit.h
    size = 2 * v + r + h + 1
    rng = random.Random(202610080329)
    basis = random_checks = 0
    for prime in (3, 5):
        tests = [[rng.randrange(prime) for _ in range(size)] for _ in range(8)]
        if prime == 3:
            tests += [[int(i == j) for i in range(size)] for j in range(size)]
        for values in tests:
            x, y = values[:v], values[v:2 * v]
            scratch, center = values[2 * v:2 * v + r], values[2 * v + r:]
            old = [list(z) for z in (x, y, scratch, center)]
            modular_invocation(circuit, code, x, y, scratch, center, prime)
            require(x == old[0] and y == [(a + b) % prime for a, b in zip(old[1], old[0])]
                    and scratch == old[2] and center == old[3], 'Odd-prime payload scalar map/restoration differs')
            require(all(0 <= z < prime for part in (x, y, scratch, center) for z in part),
                    'Payload record escaped its fixed finite alphabet')
        basis += size if prime == 3 else 0
        random_checks += 8
    return dict(ground=8, full_dirty_basis_dimension=size, prime3_basis_probes=basis,
                arbitrary_prime3_prime5_word_probes=random_checks, intermediate_symbols='F3 or F5, reduced at every update',
                payload_width='one fixed finite-alphabet symbol; binary encoding has constant width',
                address_volume='not altered by scalar alphabet')


def add_symbols(a, b, prime, sign=1):
    result = dict(a)
    for key, value in b.items():
        result[key] = (result.get(key, 0) + sign * value) % prime
        if not result[key]:
            del result[key]
    return result


def phi(matrix, values, n):
    out = [None] * len(values)
    mask = (1 << n) - 1
    for address, value in enumerate(values):
        h, d = address & mask, address >> n
        target = (h ^ apply(matrix, d)) | (d << n)
        require(out[target] is None, 'Address shear is not a complete binary permutation')
        out[target] = value
    return out


def frame_controls():
    total = 0
    for n in (2, 3, 4, 5):
        line = (1 << min(n, 3)) - 1
        if line.bit_count() % 2 == 0:
            line = 1
        p, _ = projection([line], n)
        require(p is not None, 'Source line is degenerate')
        ident = identity(n)
        for prime in (3, 5):
            original = [[{(role, address): 1} for address in range(1 << (2 * n))] for role in range(2)]
            values = [list(original[0]), list(original[1])]
            previous = [p, [0] * n]
            gates = [p, ident, [a ^ b for a, b in zip(ident, p)]]
            for step, frame in enumerate(gates):
                values = [phi([a ^ b for a, b in zip(frame, old)], role, n)
                          for role, old in zip(values, previous)]
                previous = [frame, frame]
                if step == 0:
                    values[1] = [add_symbols(b, a, prime, -1) for a, b in zip(*values)]
                elif step == 1:
                    values[0] = [add_symbols(a, b, prime) for a, b in zip(*values)]
                else:
                    values[1] = [add_symbols(a, b, prime, -1) for a, b in zip(*values)]
            sinks = [ident, [a ^ b for a, b in zip(ident, p)]]
            values = [phi([a ^ b for a, b in zip(sink, old)], role, n)
                      for role, old, sink in zip(values, previous, sinks)]
            merged = [values[1], values[0]]
            expected = [phi(ident, role, n) for role in original]
            require(merged == expected, 'Binary frame/odd-payload endpoint permutation differs')
            total += 2 * len(values[0])
    return dict(exact_complete_operator_rows=total, dimensions=[2, 3, 4, 5],
                scalar_primes=[3, 5], complete_address_permutations=True,
                source_endpoint='P_U', routed_sink_endpoint='I+P_U', source_rank_exception=0,
                scope='Complete common-frame symbolic linear operators, independently of tape cost')


def xor_cost_negative():
    b, mask, modulus = 3, 2, 8
    permutation = [value ^ mask for value in range(modulus)]
    require(all(permutation != [(a * value + c) % modulus for value in range(modulus)]
                for a in range(1, modulus, 2) for c in range(modulus)),
            'Chosen binary XOR is unexpectedly an ordinary modular affine map')
    return dict(column_width=b, prefix_mask=mask, exact_binary_permutation=permutation,
                ordinary_integer_modulus=modulus, affine_unit_and_offset_pairs_excluded=modulus * modulus // 2,
                consequence='The retained controlled modular-affine scan lemma does not directly implement triangular word-XOR')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream', type=Path, required=True)
    ap.add_argument('--accepted-generic', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    started = time.monotonic()
    old = json.loads(args.accepted_generic.read_text())
    row = next(r for r in old['witnesses'] if r['mode'] == 'tight')
    counts = row['complex_counts']
    alpha = Q(counts['s'], counts['W'])
    require(alpha < counts['m'], 'Accepted complex count has no binary address rank deficit')
    source_dir = Path(__file__).parent
    names = ['downstream_binary_bruhat_payload.py', 'downstream_binary_shear_interface.py',
             'downstream_complex_circuit.py', 'downstream_gaussian.py']
    result = dict(status='PASS BINARY ADDRESS AND ODD-PRIME PAYLOAD ALGEBRA; TRIANGULAR WORD-XOR TAPE COST UNRESOLVED',
        campaign='20261007T222521Z', campaign_start='2026-10-07T22:25:21Z',
        campaign_original_deadline='2026-10-08T08:25:21Z', campaign_deadline='2026-10-08T10:00:00Z',
        generated_at=datetime.now(timezone.utc).isoformat(), reference=check_sources(args.upstream),
        input=dict(path=str(args.accepted_generic), bytes=args.accepted_generic.stat().st_size,
                   sha256=hashlib.sha256(args.accepted_generic.read_bytes()).hexdigest()),
        source_sha256={name:hashlib.sha256((source_dir / name).read_bytes()).hexdigest() for name in names},
        binary_bruhat=matrix_controls(), fixed_payload=payload_controls(),
        common_frame=frame_controls(), modular_affine_counterexample=xor_cost_negative(),
        unchanged_candidate_counts=counts, prospective_normalized_rank_children=str(alpha),
        unresolved_cost='F(e)<=(s_complex/W_complex)F(e/m)+O(e^tau_old*polylog(e)) using currently supported compact word-XOR; no stronger exponent follows from this bound',
        scope='Algebra and fixed finite payload compatibility only; no free binary triangular scan, changed primitive promotion, universal obstruction or novelty claim',
        elapsed_seconds=time.monotonic() - started)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS binary Bruhat factorizations', result['binary_bruhat']['exact_factorizations'],
          'binary addresses', result['binary_bruhat']['full_joint_binary_address_checks'],
          'F3 full dirty basis', result['fixed_payload']['prime3_basis_probes'],
          'tape XOR cost remains unresolved', flush=True)


if __name__ == '__main__':
    main()
