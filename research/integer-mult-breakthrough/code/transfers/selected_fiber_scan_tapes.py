#!/usr/bin/env python3
"""Literal natural-order prefix/difference scan on interleaved selected bits.

Seven finite-alphabet tapes retain every address/header bit and four Gaussian
fields. A spectator accumulator table moves by fewer than three whole input
volumes. Ripple carries and backward countdowns include their head returns;
no numeric seek, array gathering or per-record full mask walk is used by the
consumer. Numeric indexing appears only in tape storage and reference/setup.
This is an ordinary blank-scratch Turing component, not a dirty circuit or a
native high-flux zigzag order or a faster complete transform supplier.
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


ZERO, ONE, START, END, ROW, HEADER, WORD, BLANK, SELECTED, SPECTATOR = range(10)


def require(value, message):
    if not value:
        raise AssertionError(message)


class Tape:
    """Only these methods access a cell or head index; statistics are monitors."""

    def __init__(self, name, cells=()):
        self.name = name
        self.cells = bytearray(cells) or bytearray([BLANK])
        self.head = 0
        self.reads = self.writes = self.moves = 0

    def read(self):
        self.reads += 1
        return self.cells[self.head]

    def write(self, symbol):
        require(symbol in range(10), "Finite alphabet required")
        self.cells[self.head] = symbol
        self.writes += 1

    def step(self, direction):
        require(direction in (-1, 1), "Only one-cell head moves are allowed")
        self.head += direction
        require(self.head >= 0, "A head escaped the marked left boundary")
        if self.head == len(self.cells):
            self.cells.append(BLANK)
        self.moves += 1

    def emit(self, symbol):
        self.write(symbol)
        self.step(1)

    def rewind(self, marker=START):
        while self.read() != marker:
            self.step(-1)

    def erase(self):
        self.rewind()
        self.step(1)
        while self.read() != END:
            self.write(BLANK)
            self.step(1)
        self.write(BLANK)
        self.rewind()
        self.write(BLANK)

    def stats(self):
        return {"reads": self.reads, "writes": self.writes, "unit_head_moves": self.moves,
                "total_steps": self.reads + self.writes + self.moves,
                "allocated_cells": len(self.cells), "final_head": self.head}


class Counter:
    """Ripple counter with a mask cursor, unary selected count and countdown."""

    def __init__(self, mask):
        self.mask = mask
        self.bits = Tape("binary-counter")
        self.ones = Tape("selected-one-count")
        self.back = Tape("backward-countdown")
        self.bits.emit(START)
        self.ones.emit(START)
        self.back.emit(START)
        self.back.write(END)
        require(mask.read() == START, "The immutable descriptor starts at its marker")
        mask.step(1)
        while mask.read() != END:
            symbol = mask.read()
            require(symbol in (SELECTED, SPECTATOR), "A mask describes every local bit")
            self.bits.emit(ZERO)
            if symbol == SELECTED:
                self.ones.emit(ONE)
            mask.step(1)
        self.bits.write(END)
        self.ones.write(END)
        self.bits.rewind()
        self.ones.rewind()
        mask.rewind()

    def selected_zero(self):
        return self.ones.read() == START

    def clear_back(self):
        # The end marker remains visible until the return to START finishes.
        self.back.rewind()
        self.back.step(1)
        while self.back.read() != END:
            self.back.write(BLANK)
            self.back.step(1)
        self.back.write(BLANK)
        self.back.rewind()
        self.back.step(1)
        self.back.write(END)

    def advance(self):
        """Return the carry type; append one countdown bit per lower spectator."""
        a, mask, back = self.bits, self.mask, self.back
        require(a.read() == START and mask.read() == START and back.read() == END,
                "Counter and empty countdown must have their declared starting heads")
        a.step(1)
        mask.step(1)
        while True:
            digit, kind = a.read(), mask.read()
            if digit == END:
                require(kind == END, "The counter and mask must have equal length")
                result = END
                break
            require(digit in (ZERO, ONE) and kind in (SELECTED, SPECTATOR),
                    "Only finite binary digits and fixed mask symbols are consumed")
            if digit == ZERO:
                a.write(ONE)
                if kind == SELECTED:
                    self.ones.step(1)
                result = kind
                break
            a.write(ZERO)
            if kind == SELECTED:
                self.ones.step(-1)
            else:
                back.write(ONE)
                back.step(1)
                back.write(END)
            a.step(1)
            mask.step(1)
        a.rewind()
        mask.rewind()
        return result

    def decrement_back(self):
        """One real binary decrement, including return; underflow ends the loop."""
        self.back.rewind()
        self.back.step(1)
        while True:
            digit = self.back.read()
            if digit == END:
                self.clear_back()
                return False
            require(digit in (ZERO, ONE), "A finite countdown digit is required")
            if digit == ONE:
                self.back.write(ZERO)
                self.back.rewind()
                self.back.step(1)
                return True
            self.back.write(ONE)
            self.back.step(1)

    def finish(self):
        require(self.selected_zero(), "A complete local cube must return the selected count to zero")
        self.bits.erase()
        self.ones.erase()
        self.back.erase()
        self.mask.rewind()


def copy_or_skip_record(source, destination=None, zero_fields=False):
    """Every header, component word and delimiter is traversed literally."""
    require(source.read() == ROW, "A complete record must begin at ROW")
    in_fields = False
    while True:
        value = source.read()
        require(value in (ZERO, ONE, ROW, HEADER, WORD), "Malformed complete record")
        if destination is not None:
            destination.emit(ZERO if zero_fields and in_fields and value in (ZERO, ONE) else value)
        source.step(1)
        if value == HEADER:
            in_fields = True
        if value == WORD:
            # A fixed finite control counts exactly eight Gaussian components.
            break
    # The first WORD just completed component zero; seven components remain.
    for _ in range(7):
        while True:
            value = source.read()
            require(value in (ZERO, ONE, WORD), "Every complete field word is binary")
            if destination is not None:
                destination.emit(ZERO if zero_fields and value in (ZERO, ONE) else value)
            source.step(1)
            if value == WORD:
                break
    require(source.read() == ROW, "A complete record ends at ROW")
    if destination is not None:
        destination.emit(ROW)
    source.step(1)


def initialize_accumulators(source, table, counter):
    """One complete input pass emits zero rows only at selected index zero."""
    require(source.read() == START, "The immutable input has a left marker")
    source.step(1)
    table.emit(START)
    overflow = True
    while source.read() != END:
        copy_or_skip_record(source, table if counter.selected_zero() else None, zero_fields=True)
        overflow = counter.advance() == END
        counter.clear_back()
    require(overflow, "Input must contain complete consecutive local address cubes")
    table.write(END)
    table.rewind()
    table.step(1)
    source.rewind()
    source.step(1)


def previous_row(table):
    require(table.read() == ROW, "Accumulator head must begin at a row boundary")
    table.step(-1)
    require(table.read() == ROW, "The previous complete row's closing marker is required")
    table.step(-1)
    while table.read() != ROW:
        table.step(-1)


def next_row(table):
    require(table.read() == ROW, "Accumulator head must begin at a row boundary")
    table.step(1)
    # Headers and all eight words lie between the two ROW markers.
    while table.read() != ROW:
        table.step(1)
    table.step(1)


def arithmetic_record(source, table, output, inverse):
    """Bit-serial signed addition/difference; no conversion to a Python number."""
    require(source.read() == ROW and table.read() == ROW, "Complete source and accumulator rows required")
    output.emit(ROW)
    source.step(1)
    table.step(1)
    while source.read() != HEADER:
        digit = source.read()
        require(digit in (ZERO, ONE) and table.read() in (ZERO, ONE), "Aligned complete headers required")
        output.emit(digit)
        source.step(1)
        table.step(1)
    require(table.read() == HEADER, "The entire header width must be retained")
    output.emit(HEADER)
    source.step(1)
    table.step(1)
    for _ in range(8):
        carry = int(inverse)
        first = True
        last_source = last_table = last_result = ZERO
        while source.read() != WORD:
            x, old = source.read(), table.read()
            require(x in (ZERO, ONE) and old in (ZERO, ONE), "A full signed word uses binary symbols")
            total = x + (ONE - old if inverse else old) + carry
            result, carry = total & ONE, total >> 1
            output.emit(result)
            table.write(x if inverse else result)
            source.step(1)
            table.step(1)
            last_source, last_table, last_result, first = x, old, result, False
        require(not first and table.read() == WORD, "All component words keep their complete width")
        overflow = ((last_source != last_table) if inverse else (last_source == last_table)) and last_result != last_source
        require(not overflow, "Signed arithmetic overflow: a full magnitude guard is required")
        output.emit(WORD)
        source.step(1)
        table.step(1)
    require(source.read() == ROW and table.read() == ROW, "All four Gaussian fields must be consumed")
    output.emit(ROW)
    source.step(1)
    table.rewind(ROW)
    # rewind would stop immediately at the closing ROW; cross it first.
    table.step(-1)
    while table.read() != ROW:
        table.step(-1)


def scan(input_cells, mask_cells, inverse=False):
    """Seven tapes; input/setup encoding and oracle decoding are outside this consumer."""
    source, mask = Tape("input", input_cells), Tape("immutable-mask", mask_cells)
    table, output = Tape("complete-accumulators"), Tape("output")
    counter = Counter(mask)
    initialize_accumulators(source, table, counter)
    output.emit(START)
    forward_rows = backward_rows = 0  # Monitor only, never determines execution.
    while source.read() != END:
        arithmetic_record(source, table, output, inverse)
        kind = counter.advance()
        more = source.read() != END
        if kind == SELECTED:
            while counter.decrement_back():
                previous_row(table)
                backward_rows += 1
        else:
            counter.clear_back()
            if more:
                next_row(table)
                forward_rows += 1
        if not more:
            require(kind == END, "The last physical record must close a complete address cube")
    output.write(END)
    source.rewind()
    table.erase()
    counter.finish()
    tapes = [source, mask, table, output, counter.bits, counter.ones, counter.back]
    stats = {tape.name: tape.stats() for tape in tapes}
    require(all(symbol == BLANK for tape in (table, counter.bits, counter.ones, counter.back)
                for symbol in tape.cells), "All ordinary scratch tapes are erased")
    require(source.cells == bytearray(input_cells), "The complete input remains immutable")
    return bytes(output.cells), {"tapes": stats, "forward_accumulator_rows": forward_rows,
                                 "backward_accumulator_rows": backward_rows,
                                 "fixed_tape_count": 7, "ordinary_scratch_erased": True}


def encode(rows, local_bits, header_bits, word_bits):
    """Input/setup oracle; this is not claimed as a native serializer theorem."""
    result = [START]
    for index, row in enumerate(rows):
        require(len(row) == 8, "Four complete Gaussian fields required")
        result.append(ROW)
        result.extend((index >> bit) & 1 for bit in range(header_bits))
        result.append(HEADER)
        for value in row:
            require(-(1 << (word_bits - 1)) <= value < 1 << (word_bits - 1), "Setup integer fits its signed word")
            raw = value % (1 << word_bits)
            result.extend((raw >> bit) & 1 for bit in range(word_bits))
            result.append(WORD)
        result.append(ROW)
    result.append(END)
    return bytes(result)


def decode(cells, header_bits, word_bits):
    """Independent output oracle; numeric addressing is not part of the consumer."""
    require(cells[0] == START and cells[-1] == END, "Full framing retained")
    position, rows = 1, []
    while cells[position] != END:
        require(cells[position] == ROW, "Exact record start retained")
        position += 1
        header = sum(cells[position + bit] << bit for bit in range(header_bits))
        require(header == len(rows), "Every original row/address bit stays unchanged")
        position += header_bits
        require(cells[position] == HEADER, "Exact header delimiter retained")
        position += 1
        row = []
        for _ in range(8):
            value = sum(cells[position + bit] << bit for bit in range(word_bits))
            if value >> (word_bits - 1):
                value -= 1 << word_bits
            row.append(value)
            position += word_bits
            require(cells[position] == WORD, "All eight exact component word boundaries retained")
            position += 1
        require(cells[position] == ROW, "Exact record end retained")
        position += 1
        rows.append(row)
    require(position == len(cells) - 1, "No hidden output payload is omitted")
    return rows


def compress(value, positions):
    return sum(((value >> position) & 1) << bit for bit, position in enumerate(positions))


def reference(rows, n, selected, inverse=False):
    guards = tuple(bit for bit in range(n) if bit not in selected)
    cube, stock = 1 << n, 1 << len(guards)
    table = {}
    output = []
    for index, row in enumerate(rows):
        key = (index // cube) * stock + compress(index % cube, guards)
        previous = table.get(key, [0] * 8)
        result = [x - y if inverse else x + y for x, y in zip(row, previous)]
        table[key] = row if inverse else result
        output.append(result)
    return output


def motion_controls():
    masks = 0
    for n in range(1, 9):
        for mask in range(1 << n):
            selected = tuple(bit for bit in range(n) if mask >> bit & 1)
            guards = tuple(bit for bit in range(n) if bit not in selected)
            sequence = [compress(value, guards) for value in range(1 << n)]
            backward = sum(max(0, a - b) for a, b in zip(sequence, sequence[1:]))
            exact = sum((1 << (n - bit - 1)) * ((1 << (bit - rank)) - 1)
                        for rank, bit in enumerate(selected))
            variation = sum(abs(a - b) for a, b in zip(sequence, sequence[1:]))
            require(backward == exact < 1 << n, "The exact selected-carry backward identity must hold")
            require(variation == (1 << len(guards)) - 1 + 2 * exact < 3 * (1 << n),
                    "The complete natural accumulator variation must be less than three volumes")
            masks += 1
    return {"all_masks_n1_through8": masks, "exact_jump_identity": True,
            "numeric_reference_only_not_tape_execution": True}


def probe(task):
    n, selected, old_rows, base_bits, grid_bits = task
    selected = tuple(selected)
    f, count = len(selected), old_rows << n
    header_bits = n + (old_rows - 1).bit_length()
    word_bits = base_bits + f + 2
    peak = (1 << (base_bits - 1)) - 1
    seed = 17431 + 101 * n + 17 * old_rows + sum(selected)
    rng = random.Random(seed)
    original = [[peak] + [rng.randrange(-peak, peak + 1) for _ in range(7)] for _ in range(count)]
    input_cells = encode(original, n, header_bits, word_bits)
    mask_cells = bytes([START] + [SELECTED if bit in selected else SPECTATOR for bit in range(n)] + [END])
    actual_cells, forward = scan(input_cells, mask_cells)
    actual = decode(actual_cells, header_bits, word_bits)
    expected = reference(original, n, selected)
    require(actual == expected, "All complete signed Gaussian fields must equal the independent prefix reference")
    restored_cells, reverse = scan(actual_cells, mask_cells, inverse=True)
    require(decode(restored_cells, header_bits, word_bits) == original and restored_cells == input_cells,
            "The actual bit-serial difference scan must restore every input/header symbol")
    stock = old_rows << (n - f)
    negative = old_rows * sum((1 << (n - bit - 1)) * ((1 << (bit - rank)) - 1)
                              for rank, bit in enumerate(selected))
    expected_forward = stock - 1 + negative
    volume = len(input_cells) - 2
    for name, run in (("forward", forward), ("inverse", reverse)):
        require(run['backward_accumulator_rows'] == negative and run['forward_accumulator_rows'] == expected_forward,
                "Literal seek row counts must bind to the independently derived carry law")
        metadata = sum(run['tapes'][key]['total_steps'] for key in
                       ('immutable-mask', 'binary-counter', 'selected-one-count', 'backward-countdown'))
        require(metadata <= 128 * (count + n + 1), "Every metadata carry, return and erase must satisfy the amortized linear ledger")
        require(run['tapes']['complete-accumulators']['unit_head_moves'] <= 12 * volume,
                "Complete accumulator payload moves must satisfy a linear input-volume ledger")
        run['counter_mask_total_steps'] = metadata
    require(max(row[0] for row in actual) == peak << f, "An unnormalized prefix consumes f magnitude bits")
    wrong_all_record_scan = []
    state = [0] * 8
    for row in original:
        state = [a + b for a, b in zip(state, row)]
        wrong_all_record_scan.append(state)
    guards_present = f < n or old_rows > 1
    if guards_present:
        require(wrong_all_record_scan != actual, "Ignoring complete spectator/old-row fibers must fail")
    short_guard_rejects = False
    if f:
        short = encode(original, n, header_bits, base_bits)
        try:
            scan(short, mask_cells)
        except AssertionError as exc:
            require('overflow' in str(exc), "The magnitude negative must fail for its stated reason")
            short_guard_rejects = True
        require(short_guard_rejects, "An input-only signed width is an insufficient prefix guard")
    return {"n": n, "selected_positions": list(selected), "old_rows": old_rows,
            "selected_width_f": f, "four_Gaussian_fields": 4, "complete_records": count,
            "signed_component_values": 8 * count, "fixed_grid_fractional_bits": grid_bits,
            "base_word_bits": base_bits, "reserved_word_bits": word_bits,
            "record_symbols": (volume // count), "input_volume_symbols": volume,
            "complete_accumulator_records": stock, "accumulator_fraction_of_input": f'1/{1 << f}',
            "seed": seed, "full_prefix_magnitude": peak << f,
            "input_only_magnitude_guard_rejected": short_guard_rejects,
            "spectator_ignorance_rejected": guards_present, "forward": forward, "inverse": reverse,
            "scope": "Exact seven-tape natural selected scan with ordinary blank scratch; no high-flux order or fast full supplier"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    require(args.workers > 0, "A positive worker count is required")
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
    own = Path(__file__).resolve()
    digest = sha256(own.read_bytes()).hexdigest()
    start = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    tasks = [(4, (0, 2), 2, 4, 3)] if args.bounded else [
        (6, (0, 3), 3, 4, 2), (8, (0, 2, 4, 6), 2, 5, 3),
        (9, (1, 4, 7), 1, 4, 2), (7, (0, 2, 5, 6), 3, 4, 3),
        (4, (), 2, 4, 2), (4, (0, 1, 2, 3), 1, 4, 3)]
    if args.workers == 1:
        cases = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, tasks))
    result = {"status": "PASS literal natural selected-fiber prefix/difference tapes",
              "started_utc": start, "completed_utc": datetime.now(timezone.utc).isoformat(),
              "seconds": time.monotonic() - tick, "workers": args.workers, "bounded": args.bounded,
              "source_sha256": digest, "motion_controls": motion_controls(), "cases": cases,
              "total_records": sum(case['complete_records'] for case in cases),
              "total_signed_component_values": sum(case['signed_component_values'] for case in cases),
              "scope": "Standalone ordinary-scratch natural selected scan; no high-flux zigzag, arbitrary-dirty scratch, routed whole supplier or new kappa"}
    require(sha256(own.read_bytes()).hexdigest() == digest, "Source must remain unchanged")
    if args.output:
        (args.output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key not in ('motion_controls', 'cases')}, sort_keys=True))


if __name__ == '__main__':
    main()
