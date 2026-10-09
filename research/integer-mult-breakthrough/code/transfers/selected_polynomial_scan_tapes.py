#!/usr/bin/env python3
"""Long-polynomial extension of the seven-tape natural selected-fiber scan.

The fixed finite control reads component words until the record marker, so
the number of Gaussian coefficients does not become a machine tape count.
The literal counter/countdown implementation is pinned and imported from
selected_fiber_scan_tapes.py. Setup/reference routines alone use numeric
coordinates. The consumer's arithmetic is finite-state signed bit addition.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import time

import selected_fiber_scan_tapes as base


BASE_SHA256 = '5565695705b0525861a136dd0ef74e6e0b28802916f080cdc3df015b2ee62e7a'
ZERO, ONE, START, END, ROW, HEADER, WORD = base.ZERO, base.ONE, base.START, base.END, base.ROW, base.HEADER, base.WORD
Tape, Counter, require = base.Tape, base.Counter, base.require


def copy_record(source, destination=None, zero_fields=False):
    require(source.read() == ROW, 'A complete polynomial record starts at ROW')
    if destination is not None:
        destination.emit(ROW)
    source.step(1)
    in_fields = False
    while source.read() != ROW:
        value = source.read()
        require(value in (ZERO, ONE, HEADER, WORD), 'Polynomial record uses the fixed finite alphabet')
        if destination is not None:
            destination.emit(ZERO if zero_fields and in_fields and value in (ZERO, ONE) else value)
        source.step(1)
        if value == HEADER:
            in_fields = True
    require(in_fields, 'Every polynomial record contains its full address header')
    if destination is not None:
        destination.emit(ROW)
    source.step(1)


def initialize(source, table, counter):
    require(source.read() == START, 'Immutable input starts at its marker')
    source.step(1)
    table.emit(START)
    overflow = True
    while source.read() != END:
        copy_record(source, table if counter.selected_zero() else None, zero_fields=True)
        overflow = counter.advance() == END
        counter.clear_back()
    require(overflow, 'Old rows contain complete consecutive local address cubes')
    table.write(END)
    table.rewind()
    table.step(1)
    source.rewind()
    source.step(1)


def arithmetic_record(source, table, output, inverse):
    require(source.read() == ROW and table.read() == ROW, 'Complete source and accumulator records required')
    output.emit(ROW)
    source.step(1)
    table.step(1)
    while source.read() != HEADER:
        digit = source.read()
        require(digit in (ZERO, ONE) and table.read() in (ZERO, ONE), 'All unchanged header bits must align')
        output.emit(digit)
        source.step(1)
        table.step(1)
    require(table.read() == HEADER, 'The full common header width must be retained')
    output.emit(HEADER)
    source.step(1)
    table.step(1)
    any_component = False
    while source.read() != ROW:
        carry = int(inverse)
        any_bit = False
        last_x = last_old = last_result = ZERO
        while source.read() != WORD:
            x, old = source.read(), table.read()
            require(x in (ZERO, ONE) and old in (ZERO, ONE), 'Complete signed component words use binary digits')
            total = x + (ONE - old if inverse else old) + carry
            result, carry = total & ONE, total >> 1
            output.emit(result)
            table.write(x if inverse else result)
            source.step(1)
            table.step(1)
            last_x, last_old, last_result, any_bit = x, old, result, True
        require(any_bit and table.read() == WORD, 'Every component retains its common word width')
        overflow = ((last_x != last_old) if inverse else (last_x == last_old)) and last_result != last_x
        require(not overflow, 'Signed arithmetic overflow: selected-width magnitude reserve is required')
        output.emit(WORD)
        source.step(1)
        table.step(1)
        any_component = True
    require(any_component and table.read() == ROW, 'Every polynomial coefficient and its boundary must be consumed')
    output.emit(ROW)
    source.step(1)
    table.step(-1)
    while table.read() != ROW:
        table.step(-1)


def scan(input_cells, mask_cells, inverse=False):
    """Same seven literal tapes; component count is read from framing."""
    source, mask = Tape('input', input_cells), Tape('immutable-mask', mask_cells)
    table, output = Tape('complete-accumulators'), Tape('output')
    counter = Counter(mask)
    initialize(source, table, counter)
    output.emit(START)
    forward_rows = backward_rows = 0  # Monitor only.
    while source.read() != END:
        arithmetic_record(source, table, output, inverse)
        kind = counter.advance()
        more = source.read() != END
        if kind == base.SELECTED:
            while counter.decrement_back():
                base.previous_row(table)
                backward_rows += 1
        else:
            counter.clear_back()
            if more:
                base.next_row(table)
                forward_rows += 1
        if not more:
            require(kind == END, 'The final record must close a complete address cube')
    output.write(END)
    source.rewind()
    table.erase()
    counter.finish()
    tapes = [source, mask, table, output, counter.bits, counter.ones, counter.back]
    require(all(symbol == base.BLANK for tape in (table, counter.bits, counter.ones, counter.back)
                for symbol in tape.cells), 'All ordinary scratch must be erased')
    require(source.cells == bytearray(input_cells), 'Full polynomial input is immutable')
    return bytes(output.cells), {'tapes': {tape.name: tape.stats() for tape in tapes},
                                'forward_accumulator_rows': forward_rows, 'backward_accumulator_rows': backward_rows,
                                'fixed_tape_count': 7, 'ordinary_scratch_erased': True}


def encode(rows, header_bits, word_bits):
    result = [START]
    for index, row in enumerate(rows):
        result.append(ROW)
        result.extend((index >> bit) & 1 for bit in range(header_bits))
        result.append(HEADER)
        for value in row:
            require(-(1 << (word_bits - 1)) <= value < 1 << (word_bits - 1), 'Setup numerator fits its full signed format')
            raw = value % (1 << word_bits)
            result.extend((raw >> bit) & 1 for bit in range(word_bits))
            result.append(WORD)
        result.append(ROW)
    result.append(END)
    return bytes(result)


def decode(cells, header_bits, word_bits, coefficients):
    require(cells[0] == START and cells[-1] == END, 'Full polynomial stream framing retained')
    position, rows = 1, []
    while cells[position] != END:
        require(cells[position] == ROW, 'Full record start retained')
        position += 1
        header = sum(cells[position + bit] << bit for bit in range(header_bits))
        require(header == len(rows), 'Every original row and address label remains unchanged')
        position += header_bits
        require(cells[position] == HEADER, 'Header boundary retained')
        position += 1
        row = []
        for _ in range(2 * coefficients):
            value = sum(cells[position + bit] << bit for bit in range(word_bits))
            if value >> (word_bits - 1):
                value -= 1 << word_bits
            row.append(value)
            position += word_bits
            require(cells[position] == WORD, 'Every complete Gaussian component retained')
            position += 1
        require(cells[position] == ROW, 'Complete polynomial record end retained')
        position += 1
        rows.append(row)
    require(position == len(cells) - 1, 'No record tail or hidden payload is omitted')
    return rows


def reference(rows, n, selected, inverse=False):
    guards = tuple(bit for bit in range(n) if bit not in selected)
    cube, stock = 1 << n, 1 << len(guards)
    table, output = {}, []
    for index, row in enumerate(rows):
        key = (index // cube) * stock + base.compress(index % cube, guards)
        previous = table.get(key, [0] * len(row))
        result = [x - y if inverse else x + y for x, y in zip(row, previous)]
        table[key] = row if inverse else result
        output.append(result)
    return output


def probe(task):
    n, selected, old_rows, coefficients, precision = task
    selected = tuple(selected)
    f, count = len(selected), old_rows << n
    header_bits = n + (old_rows - 1).bit_length()
    word_bits, baseline_word_bits = precision + f + 3, precision + 3
    peak = 1 << (precision - 2)
    rng = random.Random(31031 + 31 * coefficients + 17 * n)
    original = [[peak] + [rng.randrange(-peak, peak + 1) for _ in range(2 * coefficients - 1)]
                for _ in range(count)]
    input_cells = encode(original, header_bits, word_bits)
    mask_cells = bytes([START] + [base.SELECTED if bit in selected else base.SPECTATOR for bit in range(n)] + [END])
    actual_cells, forward = scan(input_cells, mask_cells)
    actual = decode(actual_cells, header_bits, word_bits, coefficients)
    require(actual == reference(original, n, selected), 'Every complete long-polynomial coefficient matches the independent reference')
    restored_cells, reverse = scan(actual_cells, mask_cells, inverse=True)
    require(restored_cells == input_cells and decode(restored_cells, header_bits, word_bits, coefficients) == original,
            'Actual bit-serial inverse restores every header and arbitrary Gaussian coefficient')
    volume = len(input_cells) - 2
    negative = old_rows * sum((1 << (n - bit - 1)) * ((1 << (bit - rank)) - 1)
                              for rank, bit in enumerate(selected))
    stock = old_rows << (n - f)
    for run in (forward, reverse):
        require(run['backward_accumulator_rows'] == negative and
                run['forward_accumulator_rows'] == stock - 1 + negative,
                'Long-record physical head paths match the exact carry law')
        metadata = sum(run['tapes'][name]['total_steps'] for name in
                       ('immutable-mask', 'binary-counter', 'selected-one-count', 'backward-countdown'))
        require(metadata <= 128 * (count + n + 1), 'Counter/mask work is linear independently of polynomial length')
        require(run['tapes']['complete-accumulators']['unit_head_moves'] <= 12 * volume,
                'Every long accumulator payload move remains linear in actual volume')
        run['counter_mask_total_steps'] = metadata
    require(max(row[0] for row in actual) == peak << f, 'The f-bit magnitude growth is real and must be paid')
    # Prefix along a binary total order is not the subset incidence transform.
    prefix_not_subset_zeta = False
    if f >= 2:
        delta = [int(i == 1) for i in range(1 << f)]
        prefix = [sum(delta[:i + 1]) for i in range(1 << f)]
        zeta = [sum(delta[j] for j in range(1 << f) if j & i == j) for i in range(1 << f)]
        require(prefix != zeta, 'A cheap total-order prefix cannot be renamed a subset-zeta supplier')
        prefix_not_subset_zeta = True
    return {'n': n, 'selected_positions': list(selected), 'selected_width_f': f, 'old_rows': old_rows,
            'complete_records': count, 'Gaussian_coefficients_per_record': coefficients,
            'signed_component_values': 2 * coefficients * count, 'precision_fractional_bits': precision,
            'baseline_component_width': baseline_word_bits, 'scan_component_width': word_bits,
            'magnitude_bits_added': f, 'width_ratio': f'{word_bits}/{baseline_word_bits}',
            'input_volume_symbols': volume, 'complete_accumulator_records': stock,
            'input_coefficients_in_unit_disk': True, 'output_magnitude_bound': f'2^{f}',
            'prefix_not_subset_zeta': prefix_not_subset_zeta,
            'forward': forward, 'inverse': reverse}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    require(args.workers > 0, 'A positive worker count is required')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
    own, helper = Path(__file__).resolve(), Path(base.__file__).resolve()
    digests = {str(path.name): sha256(path.read_bytes()).hexdigest() for path in (own, helper)}
    require(digests[helper.name] == BASE_SHA256, 'The literal seven-tape helper must match its immutable accepted source')
    start, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    tasks = [(4, (0, 2), 2, 3, 8)] if args.bounded else [
        (5, (0, 2), 3, 1, 16), (6, (1, 4), 2, 3, 32),
        (6, (0, 2, 4), 1, 16, 64), (7, (0, 3, 6), 1, 64, 24)]
    if args.workers == 1:
        cases = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, tasks))
    require(all(sha256(path.read_bytes()).hexdigest() == digests[path.name] for path in (own, helper)),
            'Every effective source must remain unchanged')
    result = {'status': 'PASS complete long-polynomial natural selected scans',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.monotonic() - tick, 'workers': args.workers, 'bounded': args.bounded,
              'source_sha256': digests, 'cases': cases,
              'total_records': sum(case['complete_records'] for case in cases),
              'total_signed_component_values': sum(case['signed_component_values'] for case in cases),
              'scope': 'Exact ordinary-scratch natural scan with paid p+f+3 component widths; no high-flux route, faster subset-zeta or new exponent'}
    if args.output:
        (args.output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'cases'}, sort_keys=True))


if __name__ == '__main__':
    main()
