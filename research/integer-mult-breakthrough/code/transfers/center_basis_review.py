#!/usr/bin/env python3
"""Independent dyadic center-basis inverse, scalar word and prefix audit.

No producer imports. Literal local gates are immutable input data. Native
source/target frame transitions, payload routing and an exponent are unpaid.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import random
import time


TOPIC = Path(__file__).resolve().parents[2]
CONTRACT = TOPIC/'fixtures/transfers/center-basis-word-contract.json'
LOCAL = TOPIC/'fixtures/complex/center-basis-local-words.json'
BASE = TOPIC/'fixtures/complex/mixed-center-h7-inverse.json'
REPLACED = {(0, 1), (0, 2)}


def identity(n):
    return [[Q(int(i == j)) for j in range(n)] for i in range(n)]


def product(a, b):
    columns = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, column) if x and y)
             for column in columns] for row in a]


def exact_integer_determinant(matrix):
    rows = [[int(x) for x in row] for row in matrix]
    previous, sign = 1, 1
    for k in range(len(rows)-1):
        if not rows[k][k]:
            pivot = next(i for i in range(k+1, len(rows)) if rows[i][k])
            rows[k], rows[pivot] = rows[pivot], rows[k]
            sign = -sign
        value = rows[k][k]
        for i in range(k+1, len(rows)):
            for j in range(k+1, len(rows)):
                numerator = value*rows[i][j]-rows[i][k]*rows[k][j]
                if numerator % previous:
                    raise ValueError('Exact determinant division is not integral')
                rows[i][j] = numerator//previous
            rows[i][k] = 0
        previous = value
    return sign*rows[-1][-1]


def feature(pair, source):
    incidence = int(set(pair) <= set(source))
    return 1-incidence if pair in REPLACED else incidence


def additions(j):
    return [tuple(sorted((set(range(5))-{i}) | {j})) for i in range(5)] + [
        (0, 1, 2, i, j) for i in range(5, j)]


def diagonal_inverse(j):
    return [[Q(1, 4)-int(i == k) if i < 5 and k < 5 else
             (Q(1, 4) if i < 3 else Q(-3, 4)) if i < 5 and k >= 5 else
             Q(int(i == k)) for k in range(j)] for i in range(j)]


def read_inputs():
    contract = json.loads(CONTRACT.read_text())
    for path, digest in contract['source_fixture_pins'].items():
        if sha256((TOPIC/path).read_bytes()).hexdigest() != digest:
            raise ValueError('Immutable producer fixture pin changed')
    return contract, json.loads(LOCAL.read_text()), json.loads(BASE.read_text())


def decode_word(raw):
    return [[op[0], *op[1:-1], Q(op[-1])] if op[0] in ('add', 'scale')
            else list(op) for op in raw]


def apply(word, values, backwards=False):
    values = list(values)
    for op in reversed(word) if backwards else word:
        if op[0] == 'add':
            _, i, j, c = op
            values[i] += (-c if backwards else c)*values[j]
        elif op[0] == 'scale':
            _, i, c = op
            values[i] *= (1/c if backwards else c)
        elif op[0] == 'swap':
            _, i, j = op
            values[i], values[j] = values[j], values[i]
        else:
            raise ValueError('Unknown scalar gate')
    return values


def local_prefix(word, n, backwards):
    rows = identity(n)
    maximum_denominator = 1
    maximum_row_sum = Q(1)
    for op in reversed(word) if backwards else word:
        if op[0] == 'add':
            _, i, j, c = op
            c = -c if backwards else c
            maximum_row_sum = max(maximum_row_sum, sum(abs(c*x) for x in rows[j]))
            maximum_denominator = max(maximum_denominator, max((c*x).denominator for x in rows[j]))
            rows[i] = [a+c*b for a, b in zip(rows[i], rows[j])]
        elif op[0] == 'scale':
            _, i, c = op
            c = 1/c if backwards else c
            rows[i] = [a*c for a in rows[i]]
        else:
            _, i, j = op
            rows[i], rows[j] = rows[j], rows[i]
        maximum_denominator = max(maximum_denominator,
            max(x.denominator for row in rows for x in row))
        maximum_row_sum = max(maximum_row_sum,
            max(sum(abs(x) for x in row) for row in rows))
    if maximum_denominator & (maximum_denominator-1):
        raise ValueError('Local word left the dyadic ring')
    return dict(fractional_bits=maximum_denominator.bit_length()-1,
                maximum_row_l1=str(maximum_row_sum))


def finite_coefficient_classes(base, local):
    pairs = [tuple(p) for p in base['features']]
    sources = [tuple(s) for s in base['sources']]
    matrix = [[feature(p, s) for s in sources] for p in pairs]
    inverse = [[Q(z, base['inverse_denominator']) for z in row]
               for row in base['inverse_numerators']]
    if product(matrix, inverse) != identity(21) or product(inverse, matrix) != identity(21):
        raise ValueError('Independent two-sided mixed-base inverse failed')
    if abs(exact_integer_determinant(matrix)) != 2**15:
        raise ValueError('Independent mixed-base determinant failed')
    if exact_integer_determinant([[int(i != j) for j in range(5)] for i in range(5)]) != 4:
        raise ValueError('Independent determinant-four border failed')
    if pairs != [tuple(p) for p in local['base']['row_pair_order']] or sources != [tuple(s) for s in local['base']['column_source_order']]:
        raise ValueError('Literal word base orders differ from the inverse fixture')
    first_five = additions(7)[:5]
    F = [[Q(feature(p, s)) for s in first_five] for p in pairs]
    v = [[Q(-1, 4)] for _ in range(3)] + [[Q(3, 4)], [Q(3, 4)]]
    wprime = product(F, v)
    f5 = [[Q(feature(p, (0, 1, 2, 5, 7)))] for p in pairs]
    f6 = [[Q(feature(p, (0, 1, 2, 6, 7)))] for p in pairs]
    w = [[Q(int(p == (1, 2)))] for p in pairs]
    top = product(product(inverse, F), diagonal_inverse(5))
    c5 = product(inverse, [[a[0]-b[0]] for a, b in zip(f5, wprime)])
    c6 = product(inverse, [[a[0]-b[0]] for a, b in zip(f6, wprime)])
    cnew = product(inverse, [[a[0]-2*b[0]] for a, b in zip(w, wprime)])
    classes = dict(base=inverse, first_five=[[-z for z in row] for row in top],
        old_extra_five=[[-z for z in row] for row in c5],
        old_extra_six=[[-z for z in row] for row in c6],
        later_extra=[[-z for z in row] for row in cnew])
    coefficients = [x for a in classes.values() for row in a for x in row]
    if any(not x for x in coefficients) or any((x*32).denominator != 1 for x in coefficients):
        raise ValueError('Finite nonzero/grid classes do not support the all-h formula')
    if max(abs(x) for x in coefficients+[Q(3, 4)]) != Q(7, 8):
        raise ValueError('Uniform absolute-entry bound changed')
    corrupted = [row[:] for row in inverse]
    corrupted[0][0] += Q(1, 32)
    if product(matrix, corrupted) == identity(21):
        raise ValueError('Corrupted inverse numerator was not detected')
    return pairs, sources, matrix, inverse, classes


def observe_scalar_prefix(word, initial, backwards):
    values = list(initial)
    input_denominator = max(x.denominator for x in values)
    maximum_denominator = input_denominator
    maximum_component = max(abs(x) for x in values)
    input_component = maximum_component
    for op in reversed(word) if backwards else word:
        changed = []
        if op[0] == 'add':
            _, i, j, c = op
            temporary = (-c if backwards else c)*values[j]
            changed.append(temporary)
            values[i] += temporary
            changed.append(values[i])
        elif op[0] == 'scale':
            _, i, c = op
            values[i] *= 1/c if backwards else c
            changed.append(values[i])
        else:
            _, i, j = op
            values[i], values[j] = values[j], values[i]
            changed += [values[i], values[j]]
        maximum_denominator = max(maximum_denominator, max(x.denominator for x in changed))
        maximum_component = max(maximum_component, max(abs(x) for x in changed))
    return dict(additional_fractional_bits=maximum_denominator.bit_length()-input_denominator.bit_length(),
        component_factor=str(maximum_component/input_component if input_component else Q(0)))


def construct(h, base, local):
    pairs, pivots, _, base_inverse, classes = finite_coefficient_classes(base, local)
    starts = {}
    offset = 21
    for j in range(7, h):
        starts[j] = offset
        offset += j
        pairs += [(i, j) for i in range(j)]
        pivots += additions(j)
    q = comb(h, 2)
    if len(pairs) != q or len(pivots) != q or len(set(pivots)) != q:
        raise ValueError('Pivot construction has missing or repeated coordinates')
    matrix = [[Q(feature(p, s)) for s in pivots] for p in pairs]
    inverse = [[Q(0) for _ in range(q)] for _ in range(q)]
    for i in range(21):
        inverse[i][:21] = base_inverse[i]
    for j in range(7, h):
        start = starts[j]
        block_inverse = diagonal_inverse(j)
        for i in range(j):
            inverse[start+i][start:start+j] = block_inverse[i]
        for ell in range(j+1, h):
            for i in range(5):
                inverse[start+i][starts[ell]+j] = Q(1, 4) if i < 3 else Q(-3, 4)
        for i in range(21):
            inverse[i][start:start+5] = classes['first_five'][i]
            inverse[i][start+5] = classes['old_extra_five'][i][0]
            inverse[i][start+6] = classes['old_extra_six'][i][0]
            for k in range(7, j):
                inverse[i][start+k] = classes['later_extra'][i][0]
    if product(matrix, inverse) != identity(q) or product(inverse, matrix) != identity(q):
        raise ValueError('Closed-form all-h pivot inverse failed')
    if sum(bool(x) for row in inverse for x in row) != (4*h-7)**2:
        raise ValueError('Exact inverse nonzero formula failed')
    if any((x*32).denominator != 1 for row in inverse for x in row):
        raise ValueError('Uniform 1/32 grid failed')
    if max(abs(x) for row in inverse for x in row) > 1:
        raise ValueError('Full pivot inverse exceeded the uniform entry bound one')
    return pairs, pivots, matrix, inverse


def compile_word(h, pairs, pivots, matrix, local):
    base_word = decode_word(local['base']['word'])
    border_word = decode_word(local['border']['word'])
    blocks = [(0, 21, base_word)]
    offset = 21
    for j in range(7, h):
        block = border_word + [['add', i, k, Q(1)] for k in range(5, j) for i in range(3)]
        blocks.append((offset, j, block))
        offset += j
    word = []
    for offset, length, block in blocks:
        for op in block:
            if op[0] == 'add':
                _, i, j, c = op
                word.append(['add', offset+i, offset+j, c])
            elif op[0] == 'scale':
                _, i, c = op
                word.append(['scale', offset+i, c])
            else:
                _, i, j = op
                word.append(['swap', offset+i, offset+j])
        for i in range(offset, offset+length):
            for j in range(offset+length, len(pairs)):
                if matrix[i][j]:
                    word.append(['add', i, j, matrix[i][j]])
    pivot_set = set(pivots)
    nonpivots = [s for s in combinations(range(h), 5) if s not in pivot_set]
    lookup = {p: i for i, p in enumerate(pairs)}
    for index, s in enumerate(nonpivots, len(pairs)):
        contained = set(combinations(s, 2))
        for p in sorted(contained-REPLACED):
            word.append(['add', lookup[p], index, Q(1)])
        for p in ((0, 1), (0, 2)):
            if p not in contained:
                word.append(['add', lookup[p], index, Q(1)])
    return pivots+nonpivots, word


def decoder_numerators(source, pairs):
    alpha = [64*int(set(p) <= set(source))-24*len(set(p)&set(source)) for p in pairs]
    gamma = 96+sum(alpha[i] for i, p in enumerate(pairs) if p in REPLACED)
    if gamma % 8:
        raise ValueError('Decoder left the stated 1/256 grid')
    return [(-a-gamma//8 if p in REPLACED else a+gamma//8) for p, a in zip(pairs, alpha)]


def audit_case(h):
    started = time.monotonic()
    contract, local, base = read_inputs()
    pairs, pivots, minor, inverse = construct(h, base, local)
    sources, word = compile_word(h, pairs, pivots, minor, local)
    q, volume = len(pairs), len(sources)
    counts = dict(Counter(op[0] for op in word))
    digest = sha256(json.dumps(word, separators=(',', ':'), default=str).encode()).hexdigest()
    for expected in contract['producer_receipts']:
        if expected['h'] == h and (counts != expected['operation_counts'] or digest != expected['word_sha256']):
            raise ValueError('Independent literal word differs from retained producer digest')
    basis_checks = central_entries = 0
    observed_prefixes = []
    negatives = ['corrupted base inverse numerator', 'different source frames cannot be renamed as a common-frame scalar basis']
    if h <= 10:
        bank = [[feature(p, s) for s in sources] for p in pairs]
        for j in range(volume):
            initial = [Q(int(i == j)) for i in range(volume)]
            output = apply(word, initial)
            expected = [Q(row[j]) for row in bank] + initial[q:]
            if output != expected or apply(word, output, True) != initial:
                raise ValueError('Complete arbitrary-dirty scalar word or inverse failed')
            basis_checks += 1
        rng = random.Random(20261009+h)
        fields = [[Q(rng.randrange(-100, 101), 1 << rng.randrange(6)) for _ in range(volume)] for _ in range(4)]
        for initial in fields:
            expected = [sum(Q(c)*x for c, x in zip(row, initial) if c) for row in bank]+initial[q:]
            output = apply(word, initial)
            if output != expected or apply(word, output, True) != initial:
                raise ValueError('Mixed dirty fields failed')
            for backwards in (False, True):
                observed = observe_scalar_prefix(word, initial, backwards)
                bound = Q(384)*(1+12*q)*volume if backwards else Q(260+2*volume)
                if observed['additional_fractional_bits'] > (7 if backwards else 0) or Q(observed['component_factor']) > bound:
                    raise ValueError('Literal scalar prefix exceeds the proposed analytic bound')
                observed_prefixes.append(dict(direction='inverse' if backwards else 'forward', **observed))
        if not any(apply(list(reversed(word)), x) != apply(word, x) for x in fields):
            raise ValueError('Wrong inverse chronology did not discriminate')
        negatives.append('reversing order without inverse scalar coefficients')
        for s in sources:
            r = decoder_numerators(s, pairs)
            for t_index, t in enumerate(sources):
                entry = sum(a*bank[i][t_index] for i, a in enumerate(r))
                overlap = len(set(s)&set(t))
                if entry != 32*(overlap-1)*(overlap-3):
                    raise ValueError('Independent central factorization K=R*G failed')
                central_entries += 1
        # Every retained nonpivot coordinate is indispensable for invertibility.
        if volume > q:
            null = [-sum(inverse[i][k]*Q(bank[k][q]) for k in range(q)) for i in range(q)] + [Q(1)] + [Q(0)]*(volume-q-1)
            if any(sum(Q(c)*x for c, x in zip(row, null)) for row in bank):
                raise ValueError('Null column of completed basis is not central-null')
            if apply(word, null) != [Q(0)]*q+[Q(1)]+[Q(0)]*(volume-q-1):
                raise ValueError('Nonpivot identity retention failed')
            negatives.append('dropping the nonpivot identity coordinates destroys invertibility')
    return dict(h=h, volume=volume, center_rank=q, null_dimension=volume-q,
        inverse_grid_denominator=32, inverse_nonzeros=(4*h-7)**2,
        maximum_nonidentity_pivot_inverse_entry_bound='7/8', maximum_pivot_inverse_entry_bound='1',
        observed_maximum_entry=str(max(abs(x) for row in inverse for x in row)),
        all_h_absolute_determinant=str(2**(2*h+1)),
        literal_word_sha256=digest, scalar_gate_counts=counts, extra_dirty_banks=0,
        complete_basis_columns=basis_checks, independently_factored_central_entries=central_entries,
        mixed_dyadic_fields=4 if h <= 10 else 0, negative_controls=negatives, observed_literal_prefixes=observed_prefixes,
        scalar_prefix_guard_contract=dict(forward_extra_fractional_bits=0, inverse_extra_fractional_bits_at_most=7,
            forward_component_factor=str(260+2*volume),
            inverse_component_factor=str(Q(384)*(1+12*q)*volume),
            premise='Atomic declared scalar gates at identical actual address operators, fixed global grid, arbitrary dirty fields. Physical frame adapters and scalar implementation scratch are separate.'),
        seconds=time.monotonic()-started,
        scope='Exact scalar component and independently derived all-h block formula. No native frame chronology or exponent.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    contract, local, base = read_inputs()
    paths = [Path(__file__).resolve(), CONTRACT, LOCAL, BASE]
    hashes = {str(p.relative_to(TOPIC)): sha256(p.read_bytes()).hexdigest() for p in paths}
    start_utc = datetime.now(timezone.utc)
    protocol = dict(created_utc=start_utc.isoformat(), workers=args.workers,
        native_threads_per_worker=1, source_and_input_sha256=hashes,
        producer_source_sha256=local['source_sha256'],
        cases=[8] if args.small else [7, 8, 10, 16], seeds='20261009+h',
        independence='No producer imports; literal local gates consumed as immutable data, all incidence matrices and full words independently reconstructed.')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    _, _, _, _, coefficient_classes = finite_coefficient_classes(base, local)
    prefix = {f'{name}_{direction}': local_prefix(decode_word(local[name]['word']), n, direction == 'inverse')
              for name, n in (('base', 21), ('border', 5)) for direction in ('forward', 'inverse')}
    if prefix != {'base_forward': {'fractional_bits': 0, 'maximum_row_l1': '260'},
        'base_inverse': {'fractional_bits': 5, 'maximum_row_l1': '384'},
        'border_forward': {'fractional_bits': 0, 'maximum_row_l1': '8'},
        'border_inverse': {'fractional_bits': 2, 'maximum_row_l1': '7'}}:
        raise ValueError('Declared local prefix constants changed')
    # Physical frame negative: C_1 versus C_7 on delta_0. A scalar shear
    # cannot declare their two distinct actual source operators identical.
    def line_entry(label, address):
        if address == 0:
            return Q(1, 2), Q(1, 2)
        if address == label:
            return Q(1, 2), Q(-1, 2)
        return Q(0), Q(0)
    expected_frame, actual_frame = line_entry(1, 1), line_entry(7, 1)
    if expected_frame == actual_frame:
        raise ValueError('Unadapted distinct-frame scalar shear did not discriminate')
    mismatch = dict(common_target_frame='C_1', other_actual_source_frame='C_7',
        other_virtual_input='delta_0', output_address=1,
        expected_if_common_frame=[str(x) for x in expected_frame], actual_after_unadapted_scalar_shear=[str(x) for x in actual_frame])
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        cases = list(pool.map(audit_case, protocol['cases']))
    if any(sha256((TOPIC/p).read_bytes()).hexdigest() != digest for p, digest in hashes.items()):
        raise ValueError('Effective source/input changed during attempt')
    result = dict(status='INDEPENDENT ALL-H DYADIC FORMULA AND SCALAR WORD REVIEW PASS',
        local_prefix_constants=prefix, same_frame_negative=mismatch, cases=cases,
        all_h_base_coefficient_classes={name:[[str(x) for x in row] for row in matrix] for name, matrix in coefficient_classes.items()},
        seconds=time.monotonic()-started,
        scope='Exact finite review plus constructive all-h scalar deductions, not formal verification, native phase chronology or kappa.')
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], cases=len(cases),
        complete_basis_columns=sum(c['complete_basis_columns'] for c in cases), seconds=result['seconds'], scope=result['scope'])))


if __name__ == '__main__':
    main()
