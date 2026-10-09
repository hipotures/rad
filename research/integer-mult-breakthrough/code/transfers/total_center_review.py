#!/usr/bin/env python3
"""Independent single-total center/null basis and uniform scalar guard review.

Literal local words are immutable input data. Only this track's previously
published rational arithmetic and scalar observation helpers are imported.
No producer modules or physical frame assumptions are imported.
"""

import argparse
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

from center_basis_review import (identity, product, exact_integer_determinant,
    additions, diagonal_inverse, decode_word, apply, local_prefix, observe_scalar_prefix)


TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/total-center-review.json'


def feature(pair, source):
    return 1 if pair == (0, 1) else int(set(pair) <= set(source))


def classes(local):
    pairs = [tuple(p) for p in local['pair_order']]
    sources = [tuple(s) for s in local['pivot_source_order']]
    matrix = [[Q(feature(p, s)) for s in sources] for p in pairs]
    inverse = [[Q(z) for z in row] for row in local['base_inverse']]
    if matrix != local['base_minor'] or product(matrix, inverse) != identity(21) or product(inverse, matrix) != identity(21):
        raise ValueError('Independent single-total base inverse failed')
    if abs(exact_integer_determinant(matrix)) != 2**12:
        raise ValueError('Single-total base determinant changed')
    first = additions(7)[:5]
    F = [[Q(feature(p, s)) for s in first] for p in pairs]
    v = [[Q(-1, 4)] for _ in range(3)]+[[Q(3, 4)], [Q(3, 4)]]
    correction = product(F, v)
    f5 = [[Q(feature(p, (0, 1, 2, 5, 7)))] for p in pairs]
    f6 = [[Q(feature(p, (0, 1, 2, 6, 7)))] for p in pairs]
    later = [[Q(int(p in [(0, 1), (0, 2), (1, 2)]))] for p in pairs]
    first_inverse = product(product(inverse, F), diagonal_inverse(5))
    c5 = product(inverse, [[a[0]-b[0]] for a, b in zip(f5, correction)])
    c6 = product(inverse, [[a[0]-b[0]] for a, b in zip(f6, correction)])
    cn = product(inverse, [[a[0]-2*b[0]] for a, b in zip(later, correction)])
    result = dict(base=inverse, first_five=[[-x for x in row] for row in first_inverse],
        old_extra_five=[[-x for x in row] for row in c5],
        old_extra_six=[[-x for x in row] for row in c6],
        later_extra=[[-x for x in row] for row in cn])
    values = [x for matrix in result.values() for row in matrix for x in row]
    if any((4*x).denominator != 1 for x in values) or max(abs(x) for x in values) != 6:
        raise ValueError('All-h 1/4 grid or maximum-six coefficient classes failed')
    bad = [row[:] for row in inverse]; bad[0][0] += Q(1, 4)
    if product(matrix, bad) == identity(21):
        raise ValueError('Corrupt inverse numerator was not rejected')
    return pairs, sources, matrix, inverse, result


def construct(h, local):
    pairs, pivots, _, base_inverse, coefficient_classes = classes(local)
    starts, offset = {}, 21
    for j in range(7, h):
        starts[j] = offset; offset += j
        pairs += [(i, j) for i in range(j)]
        pivots += additions(j)
    q = comb(h, 2)
    if len(pairs) != q or len(set(pivots)) != q:
        raise ValueError('Complete pivot stock failed')
    matrix = [[Q(feature(p, s)) for s in pivots] for p in pairs]
    inverse = [[Q(0) for _ in range(q)] for _ in range(q)]
    for i in range(21):
        inverse[i][:21] = base_inverse[i]
    for j in range(7, h):
        start = starts[j]
        for i, row in enumerate(diagonal_inverse(j)):
            inverse[start+i][start:start+j] = row
        for ell in range(j+1, h):
            for i in range(5):
                inverse[start+i][starts[ell]+j] = Q(1, 4) if i < 3 else Q(-3, 4)
        for i in range(21):
            inverse[i][start:start+5] = coefficient_classes['first_five'][i]
            inverse[i][start+5] = coefficient_classes['old_extra_five'][i][0]
            inverse[i][start+6] = coefficient_classes['old_extra_six'][i][0]
            for k in range(7, j):
                inverse[i][start+k] = coefficient_classes['later_extra'][i][0]
    if product(matrix, inverse) != identity(q) or product(inverse, matrix) != identity(q):
        raise ValueError('Independent closed-form total pivot inverse failed')
    if any((4*x).denominator != 1 for row in inverse for x in row):
        raise ValueError('Uniform all-h 1/4 inverse grid failed')
    if max(abs(x) for row in inverse for x in row) != Q(6):
        raise ValueError('Complete inverse maximum coefficient changed')
    return pairs, pivots, matrix, inverse, coefficient_classes


def compile_word(h, pairs, pivots, local):
    blocks = [(0, 21, decode_word(local['base_word']))]
    offset = 21
    for j in range(7, h):
        blocks.append((offset, j, decode_word(local['border_word'])+[
            ['add', i, k, Q(1)] for k in range(5, j) for i in range(3)]))
        offset += j
    word = []
    for offset, length, local_word in blocks:
        for op in local_word:
            if op[0] == 'add':
                word.append(['add', offset+op[1], offset+op[2], op[3]])
            elif op[0] == 'scale':
                word.append(['scale', offset+op[1], op[2]])
            else:
                word.append(['swap', offset+op[1], offset+op[2]])
        for i in range(offset, offset+length):
            for j in range(offset+length, len(pairs)):
                if feature(pairs[i], pivots[j]):
                    word.append(['add', i, j, Q(1)])
    chosen = set(pivots)
    nonpivots = [s for s in combinations(range(h), 5) if s not in chosen]
    sources = pivots+nonpivots
    index = {p: i for i, p in enumerate(pairs)}
    for j, source in enumerate(nonpivots, len(pairs)):
        word.append(['add', 0, j, Q(1)])
        for pair in combinations(source, 2):
            if pair != (0, 1):
                word.append(['add', index[pair], j, Q(1)])
    return sources, word


def decoder_control(h, pairs, sources):
    masks = [sum(1 << x for x in s) for s in sources]
    bank = [[feature(p, s) for p in pairs] for s in sources]
    maximum_l1, total_values = Q(0), set()
    for target, mask in zip(sources, masks):
        alpha = [Q(int(set(p) <= set(target)), 4)-Q(sum(x in target for x in p), 32)*3 for p in pairs]
        coefficients = [x-alpha[0] for x in alpha]
        coefficients[0] = Q(3, 8)+10*alpha[0]
        total_values.add(coefficients[0]); maximum_l1 = max(maximum_l1, sum(abs(x) for x in coefficients))
        for source_mask, column in zip(masks, bank):
            actual = sum(c*x for c, x in zip(coefficients, column) if c and x)
            t = (mask & source_mask).bit_count()
            if actual != Q((t-1)*(t-3), 8):
                raise ValueError('Independent full central decoder failed')
    if total_values != {Q(3, 8), Q(-9, 16), Q(1)}:
        raise ValueError('Exact total scatter coefficient classes changed')
    theoretical = max(Q(15*h-43, 32), Q(3*comb(h-5, 2)+68, 32),
                      Q(2*comb(h-5, 2)+25*(h-5)+32, 32))
    if maximum_l1 != theoretical:
        raise ValueError('Independent decoder L1 class formula failed')
    return dict(complete_entries=len(sources)**2, exact_decoder_grid_bits=5,
                total_values=sorted(str(x) for x in total_values), exact_maximum_row_L1=str(maximum_l1))


def case(task):
    h, local, config = task
    started = time.monotonic()
    pairs, pivots, matrix, inverse, coefficient_classes = construct(h, local)
    q, v = comb(h, 2), comb(h, 5)
    base_forward = local_prefix(decode_word(local['base_word']), 21, False)
    base_inverse = local_prefix(decode_word(local['base_word']), 21, True)
    border_forward = local_prefix(decode_word(local['border_word']), 5, False)
    border_inverse = local_prefix(decode_word(local['border_word']), 5, True)
    forward_constant = max(Q(base_forward['maximum_row_l1']), Q(border_forward['maximum_row_l1']))
    inverse_constant = max(Q(base_inverse['maximum_row_l1']), Q(border_inverse['maximum_row_l1']), Q(1))
    fraction_bound = base_inverse['fractional_bits']+border_inverse['fractional_bits']
    guard = dict(common_grid_assumption=True, forward_extra_fraction_bits=0,
        inverse_extra_fraction_bits=fraction_bound, inverse_endpoint_extra_fraction_bits=2,
        forward_component_factor=str(forward_constant+h+v),
        inverse_component_factor=str(inverse_constant*(1+6*q*q)*(1+v)),
        inverse_endpoint_component_factor=str(66*v),
        scope='Conditional literal scalar roles and coefficient-times-source temporaries; native multiplication/exchange scratch and physical frames are not included.')
    result = dict(h=h, pivot_rank=q, volume=v, null_dimension=v-q,
        all_h_absolute_determinant=str(2**(2*h-2)), complete_inverse_grid_bits=2,
        maximum_pivot_inverse_absolute=str(max(abs(x) for row in inverse for x in row)),
        inverse_nonzeros=sum(bool(x) for row in inverse for x in row),
        finite_coefficient_class_count=sum(len(row) for mat in coefficient_classes.values() for row in mat),
        local_scalar_prefixes=dict(base_forward=base_forward, base_inverse=base_inverse,
                                  border_forward=border_forward, border_inverse=border_inverse),
        proposed_uniform_scalar_guard=guard, exact_two_sided_inverse=True)
    if h <= config['literal_maximum_h']:
        sources, word = compile_word(h, pairs, pivots, local)
        bank = [[Q(feature(p, s)) for s in sources] for p in pairs]
        observations = []
        for j in range(v):
            values = [Q(int(i == j)) for i in range(v)]
            expected = [row[j] for row in bank]+values[q:]
            if apply(word, values) != expected or apply(word, expected, True) != values:
                raise ValueError('Complete scalar basis column/inverse failed')
        rng = random.Random(config['seed']+h)
        for _ in range(4):
            values = [Q(rng.randrange(-100, 101), 1 << rng.randrange(6)) for _ in range(v)]
            expected = [sum(c*x for c, x in zip(row, values) if c) for row in bank]+values[q:]
            if apply(word, values) != expected or apply(word, expected, True) != values:
                raise ValueError('Complete dirty data-bank word failed')
            for backwards in (False, True):
                observation = observe_scalar_prefix(word, values, backwards)
                bound = Q(guard['inverse_component_factor' if backwards else 'forward_component_factor'])
                allowed = fraction_bound if backwards else 0
                if observation['additional_fractional_bits'] > allowed or Q(observation['component_factor']) > bound:
                    raise ValueError('Observed temporary exceeds proposed uniform scalar bound')
                observations.append(dict(backwards=backwards, **observation))
        result.update(complete_basis_columns=v, arbitrary_dirty_fields=4, scalar_operations=len(word),
            complete_word_sha256=sha256(json.dumps(word, default=str, separators=(',', ':')).encode()).hexdigest(),
            observed_scalar_prefixes=observations, central_decoder=decoder_control(h, pairs, sources), extra_banks=0)
    result['seconds'] = time.monotonic()-started
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text()); fixture = TOPIC/config['producer_fixture']
    if sha256(fixture.read_bytes()).hexdigest() != config['producer_fixture_sha256']:
        raise ValueError('Pinned single-total literal fixture changed')
    local = json.loads(fixture.read_text())
    if local['source_sha256'] != config['producer_source_sha256']:
        raise ValueError('Fixture producer identity changed')
    paths = [Path(__file__).resolve(), Path(__file__).with_name('center_basis_review.py'), CONFIG, fixture]
    hashes = {str(p.relative_to(TOPIC)): sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
        effective_source_config_fixture_sha256=hashes, seed=config['seed'], scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started = time.monotonic()
    dimensions = [8] if args.small else config['ambient_dimensions']
    try:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows = list(pool.map(case,[(h,local,config) for h in dimensions]))
        if any(sha256((TOPIC/p).read_bytes()).hexdigest()!=value for p,value in hashes.items()):
            raise ValueError('Effective source/config/input changed during attempt')
        result = dict(status='INDEPENDENT EXACT SINGLE-TOTAL SCALAR REVIEW PASS',cases=rows,
            complete_basis_columns=sum(x.get('complete_basis_columns',0) for x in rows),
            complete_central_entries=sum(x.get('central_decoder',{}).get('complete_entries',0) for x in rows),
            seconds=time.monotonic()-started,scope=config['scope'])
        if args.output:
            (args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({key:result[key] for key in ['status','complete_basis_columns','complete_central_entries','seconds']}))
    except Exception as error:
        if args.output:
            (args.output/'failure.json').write_text(json.dumps(dict(error_type=type(error).__name__,error=str(error)),indent=2)+'\n')
        raise


if __name__ == '__main__':
    main()
