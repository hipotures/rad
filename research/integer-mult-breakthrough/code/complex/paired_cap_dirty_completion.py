#!/usr/bin/env python3
"""Paid in-place dyadic completions of two cap-compatible five-cube blocks.

The three retained actual rows are complemented by every missing Fourier
kernel row. Every original bank is retained, transformed and restored. The
reported bank counts and frame-entry bills are scoped to independent block
materialization; they are not a complete side chronology or native supplier.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def product(a, b):
    return [[sum(x * b[k][j] for k, x in enumerate(row))
             for j in range(len(b[0]))] for row in a]


def determinant(a):
    a = [list(row) for row in a]
    result = Q(1)
    for col in range(len(a)):
        row = next((i for i in range(col, len(a)) if a[i][col]), None)
        if row is None:
            return Q(0)
        if row != col:
            a[row], a[col] = a[col], a[row]
            result = -result
        pivot = a[col][col]
        result *= pivot
        for i in range(col + 1, len(a)):
            c = a[i][col] / pivot
            a[i] = [x - c * y for x, y in zip(a[i], a[col])]
    return result


def is_power_two(value):
    return value > 0 and value & (value - 1) == 0


def dyadic(value):
    return is_power_two(value.denominator)


def unit(value):
    return value and is_power_two(abs(value.numerator)) and dyadic(value)


def apply_gate(a, gate):
    kind, target, source, c = gate
    if kind == 'add':
        a[target] = [x + c * y for x, y in zip(a[target], a[source])]
    elif kind == 'scale':
        a[target] = [c * x for x in a[target]]
    else:
        raise AssertionError('Unknown elementary gate')


def invert_word(word):
    return [(kind, target, source, -c if kind == 'add' else 1 / c)
            for kind, target, source, c in reversed(word)]


def compile_word(matrix):
    """Use integer Euclidean shears and only power-two unit row scales.

    This is deterministic source generation, not a shortest-word claim.
    Rational determinants and decoding are independently checked below.
    """
    a = [list(row) for row in matrix]
    reducing = []

    def emit(kind, target, source, c):
        c = Q(c)
        if kind == 'add' and not c:
            return
        if not dyadic(c) or kind == 'scale' and not unit(c):
            raise AssertionError('Compiler attempted an odd-denominator inverse')
        gate = (kind, target, source, c)
        apply_gate(a, gate)
        reducing.append(gate)

    def swap(x, y):
        # Literal scalar exchanges, with the final sign correction paid.
        if x == y:
            return
        emit('add', x, y, 1)
        emit('add', y, x, -1)
        emit('add', x, y, 1)
        emit('scale', y, y, -1)

    for col in range(len(a)):
        first = next((i for i in range(col, len(a)) if a[i][col]), None)
        if first is None:
            raise AssertionError('Completion is singular')
        swap(col, first)
        denominator = max(v[col].denominator for v in a[col:])
        for i in range(col + 1, len(a)):
            while a[i][col]:
                x, y = a[col][col] * denominator, a[i][col] * denominator
                if x.denominator != 1 or y.denominator != 1:
                    raise AssertionError('Column grid changed under integer Euclidean shears')
                quotient = int(x) // int(y)
                emit('add', col, i, -quotient)
                swap(col, i)
        pivot = a[col][col]
        if not unit(pivot):
            raise AssertionError('Dyadic-unit determinant did not yield a unit pivot')
        if pivot != 1:
            emit('scale', col, col, 1 / pivot)
        for i in range(len(a)):
            if i != col and a[i][col]:
                emit('add', i, col, -a[i][col])
    if a != identity(len(a)):
        raise AssertionError('Elementary inverse did not reduce to the identity')
    return invert_word(reducing)


def word_matrix(n, word):
    a = identity(n)
    for gate in word:
        apply_gate(a, gate)
    return a


def prefix_bill(n, word):
    a = identity(n)
    max_l1, max_temporary, fractional = Q(1), Q(0), 0

    def charge(row, temporary=False):
        nonlocal max_l1, max_temporary, fractional
        norm = sum(abs(v) for v in row)
        max_l1 = max(max_l1, norm)
        if temporary:
            max_temporary = max(max_temporary, norm)
        for value in row:
            if not dyadic(value):
                raise AssertionError('Literal scalar prefix left the dyadic coefficient ring')
            fractional = max(fractional, value.denominator.bit_length() - 1)

    for kind, target, source, c in word:
        charge([c * x for x in a[source if kind == 'add' else target]], True)
        apply_gate(a, (kind, target, source, c))
        charge(a[target])
    return {'maximum_row_L1_including_products': str(max_l1),
            'maximum_multiplication_temporary_L1': str(max_temporary),
            'maximum_extra_fractional_bits': fractional}


def binary_basis(values):
    pivots = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return tuple(pivots[i] for i in sorted(pivots, reverse=True))


def parity_selector(j, parity, value):
    return value | ((parity ^ (value.bit_count() & 1)) << (j - 1))


def source_label(k, selector):
    return sum(1 << (2 * i + ((selector >> i) & 1)) for i in range(k))


def target_label(k, j, selector, outside):
    return (sum(1 << (2 * i + ((selector >> i) & 1)) for i in range(j))
            + sum(1 << (2 * k + 2 * i + ((outside >> i) & 1))
                  for i in range(k - j)))


def central(overlap):
    return Q((overlap - 1) * (overlap - 3), 8)


def solve_decoder(rows, target):
    # In this fixed family the first three independent actual rows suffice.
    # Generic exact row elimination binds their provenance independently of
    # the explicit antipodal/constant-kernel formulas.
    basis = []
    for i, original in enumerate(rows):
        value, provenance = list(original), [Q(i == a) for a in range(len(rows))]
        for pivot, row, coefficients in basis:
            c = value[pivot]
            value = [x - c * y for x, y in zip(value, row)]
            provenance = [x - c * y for x, y in zip(provenance, coefficients)]
        pivot = next((a for a, value in enumerate(value) if value), None)
        if pivot is None:
            raise AssertionError('Selected actual rows are dependent')
        c = value[pivot]
        basis.append((pivot, [x / c for x in value], [x / c for x in provenance]))
    remaining, decoder = list(target), [Q(0)] * len(rows)
    for pivot, row, provenance in basis:
        c = remaining[pivot]
        remaining = [x - c * y for x, y in zip(remaining, row)]
        decoder = [x + c * y for x, y in zip(decoder, provenance)]
    if any(remaining):
        raise AssertionError('A target row is outside the retained actual rows')
    return decoder


def literal_fields(matrix, word):
    n = len(matrix)
    # Four complete Gaussian fields, represented by all eight exact rational
    # components, with no imaginary or unused-field crop.
    original = [[Q((-1) ** (i + a) * (3 * i + 5 * a + 1), 1 << ((i + a) % 4))
                 for a in range(8)] for i in range(n)]
    expected = product(matrix, original)
    actual = [list(row) for row in original]
    for gate in word:
        apply_gate(actual, gate)
    if actual != expected:
        raise AssertionError('Literal four-field forward word differs from the complete matrix')
    inverse = invert_word(word)
    for gate in inverse:
        apply_gate(actual, gate)
    if actual != original:
        raise AssertionError('Complete arbitrary-dirty bank contents were not restored')
    cropped = [list(row) for row in expected]
    cropped[3] = [Q(0)] * 8
    for gate in inverse:
        apply_gate(cropped, gate)
    if cropped == original:
        raise AssertionError('Unpaid retirement of a parked kernel bank was accepted')
    missing = [list(row) for row in expected]
    for gate in inverse[:-1]:
        apply_gate(missing, gate)
    if missing == original:
        raise AssertionError('Missing inverse mutation was accepted')
    return {'Gaussian_fields_per_bank': 4, 'complete_components_checked': 16 * n,
            'omitted_kernel_bank_rejected': True, 'omitted_inverse_gate_rejected': True}


def serialized_word(word):
    return [{'kind': kind, 'target': target, 'source': source, 'coefficient': str(c)}
            for kind, target, source, c in word]


def probe(task):
    j, parity = task
    k, n, source_parity = 5, 1 << (j - 1), parity ^ (j & 1)
    targets = [parity_selector(j, parity, t) for t in range(n)]
    sources = [parity_selector(j, source_parity, u) for u in range(n)]
    a = [[-central(j - (s ^ t).bit_count()) for s in sources] for t in targets]
    spectrum = [sum(value * (-1) ** ((u & char).bit_count())
                    for u, value in enumerate(a[0])) for char in range(n)]
    active_masks = [i for i, value in enumerate(spectrum) if value]
    kernel_masks = [i for i, value in enumerate(spectrum) if not value]
    if len(active_masks) != 3 or len(kernel_masks) != n - 3:
        raise AssertionError('The exact parity-block rank/nullity changed')
    selected = [0, 1, 2]
    matrix = [a[i] for i in selected] + [[Q((-1) ** ((u & char).bit_count()))
                                         for u in range(n)] for char in kernel_masks]
    det = determinant(matrix)
    if not unit(det):
        raise AssertionError('Completion requires an odd-denominator inverse')
    word = compile_word(matrix)
    inverse_word = invert_word(word)
    if word_matrix(n, word) != matrix or product(word_matrix(n, inverse_word), matrix) != identity(n):
        raise AssertionError('Literal dyadic elementary word is not the declared invertible completion')
    decoders = [solve_decoder(a[:3], row) for row in a]
    if any(c.denominator != 1 for row in decoders for c in row):
        raise AssertionError('A selected-row decoder introduced an unexpected denominator')
    if product(decoders, matrix[:3]) != a:
        raise AssertionError('Full target decoder failed')
    corrupt = [list(row) for row in decoders]
    corrupt[-1][0] += 1
    if product(corrupt, matrix[:3]) == a:
        raise AssertionError('Corrupt active-channel scatter was accepted')

    buckets = [[source_label(k, s | (outside << j))
                for outside in range(1 << (k - j))] for s in sources]
    cap = binary_basis(label for bucket in buckets for label in bucket)
    if len(cap) != k:
        raise AssertionError('Literal source support is not the promised five-dimensional cap')
    bucket_ranks = [len(binary_basis(bucket)) for bucket in buckets]
    if bucket_ranks != [k - j + 1] * n:
        raise AssertionError('Aggregated input source-frame dimensions changed')
    all_targets = [[target_label(k, j, t, outside)
                    for outside in range(1 << (k - j))] for t in targets]
    if any((s & t).bit_count() & 1 for bucket in buckets for s in bucket
           for labels in all_targets for t in labels):
        raise AssertionError('Same-parity common cap is outside a literal output target cap')
    wrong = target_label(k, j, targets[0] ^ 1, 0)
    if not any((s & wrong).bit_count() & 1 for bucket in buckets for s in bucket):
        raise AssertionError('Opposite cap corruption was accepted')
    actual_root_spans = []
    actual_target_counts = []
    for root in range(3):
        fanout = [label for t, row in enumerate(decoders) if row[root]
                  for label in all_targets[t]]
        actual_root_spans.append(len(binary_basis(fanout)))
        actual_target_counts.append(len(fanout))
    fourier_target_span = len(binary_basis(label for row in all_targets for label in row))
    if actual_root_spans != [4, 4, 4] or fourier_target_span != 5:
        raise AssertionError('The charged actual-row versus Fourier fanout geometry changed')
    if any(sum(value * (-1) ** ((u & char).bit_count())
               for u, value in enumerate(row)) for row in a for char in kernel_masks):
        raise AssertionError('A parked character is not in the complete parity kernel')
    # This charges both directions, keeping the same actual common F_cap at
    # every scalar gate and read, before restoring the original input frames.
    closed_entry_rank = 2 * sum(k - r for r in bucket_ranks)
    return {'j': j, 'target_parity': parity, 'source_parity': source_parity,
            'selected_actual_target_selector_order': targets,
            'source_selector_order': sources,
            'original_complete_banks_retained': n, 'decoder_live_banks': 3,
            'parked_kernel_banks_retained': n - 3, 'active_Fourier_masks': active_masks,
            'parked_Fourier_masks': kernel_masks, 'completion_determinant': str(det),
            'complete_side_matrix': [[str(v) for v in row] for row in a],
            'completion_matrix': [[str(v) for v in row] for row in matrix],
            'full_target_decoder': [[str(v) for v in row] for row in decoders],
            'forward_word': serialized_word(word), 'inverse_word': serialized_word(inverse_word),
            'forward_gate_count': len(word), 'inverse_gate_count': len(inverse_word),
            'forward_prefix_bill': prefix_bill(n, word),
            'inverse_prefix_bill': prefix_bill(n, inverse_word),
            'literal_dirty_fields': literal_fields(matrix, word),
            'common_actual_cap_frame_rank': k,
            'paid_aggregated_input_frame_ranks': bucket_ranks,
            'closed_common_cap_entry_and_return_rank': closed_entry_rank,
            'raw_single_pattern_target_span': k - j + 1,
            'retained_actual_row_fanout_target_spans': actual_root_spans,
            'retained_actual_row_fanout_target_counts': actual_target_counts,
            'Fourier_channel_fanout_target_span': fourier_target_span,
            'all_source_and_target_cap_entries_checked': n * (1 << (k - j)) ** 2 * n,
            'opposite_parity_cap_rejected': True, 'corrupt_decoder_rejected': True,
            'aggregation_and_global_birth_or_phase_chronology_supplied': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker required')
    path = Path(__file__).resolve()
    source_bytes = path.read_bytes()
    started_utc, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    tasks = [(j, p) for j in (3, 4) for p in range(1 if args.bounded else 2)]
    if args.workers == 1:
        rows = list(map(probe, tasks))
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
            rows = list(pool.map(probe, tasks))
    if path.read_bytes() != source_bytes:
        raise AssertionError('Effective source changed during execution')
    result = {'status': 'PASS exact in-place dyadic cap-block completion and scoped stock boundary',
              'started_utc': started_utc, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'workers': args.workers,
              'bounded': args.bounded, 'source_sha256': sha256(source_bytes).hexdigest(),
              'cases': rows,
              'formal_all_proper_J_census': {'minimum_pair_count_for_all_J': 10,
                  'raw_independent_block_slots': 211, 'decoder_live_channels': 141,
                  'retained_parked_slots': 70,
                  'j3_weighted_parking': comb(5, 3) * (8 - 6),
                  'j4_weighted_parking': comb(5, 4) * (16 - 6),
                  'closed_entry_and_return_rank_for_j3_j4_blocks': 800},
              'scope': 'Four/eight complete arbitrary-dirty scalar banks at an identical actual common cap; scalar word, inverse, literal supports and closed entry/return ranks. Aggregation, global chronology, reusable parking, native cost, precision supplier and any exponent remain open.'}
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(encoded)
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'gate_counts': [row['forward_gate_count'] for row in rows],
                      'case_count': len(rows)}), flush=True)


if __name__ == '__main__':
    main()
