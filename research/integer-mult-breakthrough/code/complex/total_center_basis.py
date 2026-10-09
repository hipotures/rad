#!/usr/bin/env python3
"""Single-total dyadic center/null basis and complete reversible scalar word.

The first center is the literal total, replacing pair (0,1). No scalar
division by an odd integer is needed. Actual common address operators and
paid native source/sink chronology remain independent obligations.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import random
from time import perf_counter

from center_null_basis import identity, multiply, dyadic
from center_basis_scalar_word import apply
from structured_center_basis import (new_columns, border_inverse, determinant,
                                     inverse_square)
from total_center_capacity import feature, local_contract, counts
from characteristic import serializable


def orders(h):
    if h < 7:
        raise ValueError('The exact base uses seven labels')
    pairs = [(i, j) for j in range(1, h) for i in range(j)]
    pivots = list(combinations(range(7), 5))
    for point in range(7, h):
        pivots += new_columns(point)
    assert len(set(pivots)) == len(pairs) == comb(h, 2)
    return pairs, pivots


def build(h):
    pairs, columns = orders(7)
    minor = [[feature(pair, source) for source in columns] for pair in pairs]
    assert abs(determinant(minor)) == 2**12
    inverse = inverse_square(minor)
    assert all(4*x == int(4*x) for row in inverse for x in row)
    for point in range(7, h):
        old = len(pairs)
        additions = new_columns(point)
        row_additions = [(i, point) for i in range(point)]
        upper = [[feature(pair, source) for source in additions] for pair in pairs]
        assert not any(feature(pair, source) for pair in row_additions for source in columns)
        border = [[feature(pair, source) for source in additions] for pair in row_additions]
        binv = border_inverse(point)
        assert determinant(border) == 4
        assert multiply(border, binv) == multiply(binv, border) == identity(point)
        correction = multiply(multiply(inverse, upper), binv)
        inverse = [row+[-x for x in correction[i]] for i, row in enumerate(inverse)] + [
            [Q(0)]*old+row for row in binv]
        minor = [row+upper[i] for i, row in enumerate(minor)] + [
            [0]*old+row for row in border]
        pairs += row_additions
        columns += additions
    assert (pairs, columns) == orders(h)
    assert minor == [[feature(pair, source) for source in columns] for pair in pairs]
    assert multiply(minor, inverse) == identity(len(pairs))
    assert multiply(inverse, minor) == identity(len(pairs))
    assert all(dyadic(x) for row in inverse for x in row)
    return pairs, columns, minor, inverse


def pivot_word(h):
    pairs, pivots = orders(h)
    contract = local_contract()
    blocks = [(0, 21, contract['base_word'])]
    offset = 21
    for point in range(7, h):
        word = contract['border_word'] + [['add', i, j, Q(1)]
            for j in range(5, point) for i in range(3)]
        blocks.append((offset, point, word))
        offset += point
    assert offset == len(pairs)
    word = []
    for offset, length, local in blocks:
        for kind, *args in local:
            if kind == 'add':
                i, j, c = args; word.append([kind, offset+i, offset+j, c])
            elif kind == 'scale':
                i, c = args; word.append([kind, offset+i, c])
            else:
                word.append([kind, offset+args[0], offset+args[1]])
        for i in range(offset, offset+length):
            for j in range(offset+length, len(pairs)):
                c = feature(pairs[i], pivots[j])
                if c:
                    word.append(['add', i, j, Q(c)])
    return pairs, pivots, word


def complete_word(h):
    pairs, pivots, word = pivot_word(h)
    chosen = set(pivots)
    nonpivots = [source for source in combinations(range(h), 5) if source not in chosen]
    sources = pivots+nonpivots
    indices = {pair: j for j, pair in enumerate(pairs)}
    for j, source in enumerate(nonpivots, len(pairs)):
        word.append(['add', indices[(0, 1)], j, Q(1)])
        for pair in combinations(source, 2):
            if pair != (0, 1):
                word.append(['add', indices[pair], j, Q(1)])
    return dict(pair_order=pairs, source_order=sources, word=word,
                center_rank=len(pairs), total_feature_index=indices[(0, 1)])


def decoder_numerators(pair_order, target):
    target = set(target)
    alpha = [8*int(set(pair) <= target)-3*sum(x in target for x in pair)
             for pair in pair_order]
    r = pair_order.index((0, 1))
    result = [x-alpha[r] for x in alpha]
    result[r] = 12+10*alpha[r]
    return result


def central_control(h):
    pairs, _ = orders(h)
    sources = list(combinations(range(h), 5))
    bank = [[feature(pair, source) for source in sources] for pair in pairs]
    checked = 0
    maximum_decoder_l1 = 0
    for target in sources:
        coefficients = decoder_numerators(pairs, target)
        maximum_decoder_l1 = max(maximum_decoder_l1, sum(abs(x) for x in coefficients))
        for j, source in enumerate(sources):
            actual = sum(c*row[j] for c, row in zip(coefficients, bank) if c)
            t = len(set(source) & set(target))
            expected = 4*(t-1)*(t-3)
            assert actual == expected
            if source == target:
                assert actual == 32
            elif t & 1:
                assert actual == 0
            checked += 1
    assert all(x in (12, -18, 32) for target in sources
               for x in [decoder_numerators(pairs, target)[0]])
    return dict(complete_ordered_entries=checked, denominator_bits=5,
                total_numerators=[12, -18, 32],
                maximum_decoder_row_l1=Q(maximum_decoder_l1, 32),
                exact_central_polynomial='(intersection-1)*(intersection-3)/8')


def run(h, literal, seed):
    started = perf_counter()
    pairs, pivots, minor, inverse = build(h)
    q, volume = len(pairs), comb(h, 5)
    data = lambda matrix: json.dumps(matrix, separators=(',', ':'), default=str).encode()
    result = dict(status='EXACT SINGLE-TOTAL SCALAR BASIS', h=h, volume=volume,
        center_rank=q, null_dimension=volume-q, absolute_determinant=str(2**(2*h-2)),
        pivot_nonzeros=sum(bool(x) for row in minor for x in row),
        inverse_nonzeros=sum(bool(x) for row in inverse for x in row),
        inverse_denominator_counts=dict(Counter(str(x.denominator) for row in inverse for x in row)),
        maximum_pivot_inverse_absolute=max(abs(x) for row in inverse for x in row),
        exact_count_formula=counts(h),
        matrix_sha256=dict(minor=sha256(data(minor)).hexdigest(), inverse=sha256(data(inverse)).hexdigest()),
        source_order_pivots=pivots, pair_order=pairs,
        checked=dict(left_and_right_inverse=True, exact_new_borders=True,
                     all_h_basis_formula='[[M,G_nonpivot],[0,I]]',
                     all_h_inverse_formula='[[M^-1,-M^-1 G_nonpivot],[0,I]]'),
        scope='Exact scalar component and all-h dyadic existence. Equal actual address operators, native transitions, full dirty physical continuation and exponent remain unpaid.')
    if literal:
        if h > 10:
            raise ValueError('Complete scalar columns are bounded to h<=10')
        compiled = complete_word(h)
        word, sources = compiled['word'], compiled['source_order']
        operations = Counter(gate[0] for gate in word)
        for name in ('add', 'swap', 'scale'):
            expected = result['exact_count_formula'][{'add': 'additions', 'swap': 'swaps', 'scale': 'scales'}[name]]
            assert operations[name] == expected
        assert sum(abs(gate[3]) for gate in word if gate[0] == 'add') == result['exact_count_formula']['expanded_unit_additions']
        bank = [[feature(pair, source) for source in sources] for pair in pairs]
        for j in range(volume):
            original = [Q(int(i == j)) for i in range(volume)]
            forward = apply(word, original)
            assert forward == [row[j] for row in bank]+original[q:]
            assert apply(word, forward, True) == original
        rng = random.Random(seed)
        for _ in range(4):
            dirty = [Q(rng.randrange(-100, 101), 1 << rng.randrange(6)) for _ in range(volume)]
            forward = apply(word, dirty)
            assert forward == [sum(c*x for c, x in zip(row, dirty) if c) for row in bank]+dirty[q:]
            assert apply(word, forward, True) == dirty
        result['literal_checks'] = dict(complete_columns=volume, forward_inverse_values=2*volume**2,
                                        arbitrary_dirty_fields=4, extra_banks=0)
        result['word_sha256'] = sha256(data(word)).hexdigest()
        result['central_checks'] = central_control(h)
    result['elapsed_seconds'] = perf_counter()-started
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, choices=(7, 8, 10, 20, 30), required=True)
    parser.add_argument('--literal', action='store_true')
    parser.add_argument('--seed', type=int, default=20261009)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a fresh attempt path')
    result = run(args.h, args.literal, args.seed)
    result['source_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(serializable(result), indent=2)+'\n')
    print(json.dumps({k: serializable(v) for k, v in result.items() if k not in
                     ('pair_order', 'source_order_pivots', 'exact_count_formula')}), flush=True)


if __name__ == '__main__':
    main()
