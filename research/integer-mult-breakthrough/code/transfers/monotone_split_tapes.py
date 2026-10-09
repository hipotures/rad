#!/usr/bin/env python3
"""Literal head-motion model for a short-record monotone CRT split scan.

The consumer uses two independent finite-symbol counter/template scanners.
Every head step, cell read/write, full payload copy, zero fill and cleanup is
counted. Integer division exists only in immutable input/oracle generation.
No guarded rotation or complete CRT algorithm is claimed by this component.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import time


BIT0, BIT1, DELIM, START, END, BLANK, FULL = 0, 1, 2, 3, 4, 5, 8


class Tape:
    """Finite alphabet and single-cell head steps; position is a monitor."""

    def __init__(self, cells, name, initialized=False, head=0):
        self.cells = bytearray(cells)
        self.name, self.head = name, head
        self.moves = 0
        self.reads = 0
        self.writes = 0
        if initialized:
            # Metadata/template setup writes its complete finite word and
            # returns to its start; scalar descriptor generation is separate.
            self.writes += len(self.cells)
            self.moves += 2 * (len(self.cells) - 1)

    def read(self):
        self.reads += 1
        return self.cells[self.head]

    def write(self, value):
        self.writes += 1
        self.cells[self.head] = value

    def step(self, direction):
        if direction not in (-1, 1):
            raise ValueError("head movement must be an actual single-cell step")
        self.head += direction
        self.moves += 1
        if self.head < 0 or self.head >= len(self.cells):
            raise AssertionError("a head escaped its declared finite workspace")

    def rewind(self):
        while self.read() & ~FULL != START:
            self.step(-1)

    def erase_workspace(self):
        self.rewind()
        self.step(1)
        while self.read() != END:
            self.write(BLANK)
            self.step(1)
        self.write(BLANK)
        # Retain the start marker until the return head has reached it.
        while self.read() & ~FULL != START:
            self.step(-1)
        self.write(BLANK)

    def stats(self):
        return {"head_moves": self.moves, "cell_reads": self.reads,
                "cell_writes": self.writes,
                "total_counted_steps": self.moves + self.reads + self.writes,
                "final_head": self.head, "cells": len(self.cells)}


class BoxScanner:
    """No numeric coordinate values: bit comparisons and ripple carry only."""

    def __init__(self, bounds, capacities, name):
        if len(bounds) != len(capacities) or not bounds:
            raise ValueError("a scanner needs nonempty aligned fields")
        counter, template = [], []
        for j, (s, t) in enumerate(reversed(list(zip(bounds, capacities)))):
            if not 0 < s <= t or t & (t - 1):
                raise ValueError("positive interval inside a complete binary field required")
            marker = START if j == 0 else DELIM
            width = t.bit_length() - 1
            if width == 0:
                raise ValueError("the finite controls require at least one bit per field")
            counter.append(marker)
            template.append(marker | (FULL if s == t else 0))
            counter.extend([0] * width)
            template.extend([(s >> i) & 1 for i in range(width)])
        counter.append(END)
        template.append(END)
        self.counter = Tape(counter, name + "-counter", initialized=True)
        self.template = Tape(template, name + "-bound-template", initialized=True)
        self.finished = False
        self.records_advanced = 0
        self.validity_scans = 0

    def valid(self):
        if self.finished:
            raise ValueError("completed box has no current record")
        a, b = self.counter, self.template
        if a.read() != START or b.read() & ~FULL != START:
            raise AssertionError("metadata heads must begin each scan at the start")
        full, comparison, all_valid = bool(b.read() & FULL), 0, True
        a.step(1)
        b.step(1)
        while True:
            x, bound = a.read(), b.read()
            if x in (DELIM, END):
                all_valid = all_valid and (full or comparison < 0)
                if x == END:
                    break
                if bound & ~FULL != DELIM:
                    raise AssertionError("immutable field delimiters lost alignment")
                comparison = 0
                full = bool(bound & FULL)
            else:
                if x not in (0, 1) or bound not in (0, 1):
                    raise AssertionError("invalid finite digit symbol")
                # Later encountered differing bits are more significant.
                if x != bound:
                    comparison = -1 if x < bound else 1
            a.step(1)
            b.step(1)
        while a.read() != START:
            a.step(-1)
            b.step(-1)
        self.validity_scans += 1
        return all_valid

    def advance(self):
        if self.finished:
            raise ValueError("cannot advance a completed binary box")
        a = self.counter
        if a.read() != START:
            raise AssertionError("counter head failed to return before increment")
        a.step(1)
        while True:
            value = a.read()
            if value == END:
                self.finished = True
                break
            if value == DELIM:
                a.step(1)
            elif value == 1:
                a.write(0)
                a.step(1)
            elif value == 0:
                a.write(1)
                break
            else:
                raise AssertionError("invalid symbol in a ripple increment")
        a.rewind()
        self.records_advanced += 1


def read_record(source, destination=None, require_zero=False):
    nonzero = False
    while True:
        value = source.read()
        if value == DELIM:
            if destination is not None:
                destination.write(DELIM)
                destination.step(1)
            source.step(1)
            break
        if value not in (0, 1):
            raise AssertionError("payload record or delimiter was lost")
        nonzero = nonzero or bool(value)
        if destination is not None:
            destination.write(value)
            destination.step(1)
        source.step(1)
    if require_zero and nonzero:
        raise ValueError("nonzero invalid input cannot be silently deleted")


def write_zero_record(destination, zeros):
    if zeros.read() == START:
        zeros.step(1)
    while zeros.read() != END:
        if zeros.read() != 0:
            raise AssertionError("zero template was corrupted")
        destination.write(0)
        destination.step(1)
        zeros.step(1)
    destination.write(DELIM)
    destination.step(1)
    zeros.rewind()


def split_stream(source, old, new, payload_width):
    """Sequential monotone scan; complete records are consumed exactly once."""
    destination = Tape([START] + [BLANK] * (len(source.cells) - 1), "output-payload")
    zeros = Tape([START] + [0] * payload_width + [END], "zero-template", initialized=True)
    if source.read() != START:
        raise ValueError("input stream must begin at its marker")
    source.step(1)
    destination.step(1)
    copied, padded, removed = 0, 0, 0
    while not new.finished:
        if new.valid():
            while not old.finished and not old.valid():
                read_record(source, require_zero=True)
                old.advance()
                removed += 1
            if old.finished:
                raise ValueError("new valid box has more records than the old box")
            read_record(source, destination)
            old.advance()
            copied += 1
        else:
            write_zero_record(destination, zeros)
            padded += 1
        new.advance()
    while not old.finished:
        if old.valid():
            raise ValueError("old valid box has more records than the new box")
        read_record(source, require_zero=True)
        old.advance()
        removed += 1
    if source.read() != END:
        raise AssertionError("input payload was not completely consumed")
    destination.write(END)
    source.rewind()
    destination.rewind()
    zeros.erase_workspace()
    for box in (old, new):
        box.counter.erase_workspace()
        box.template.erase_workspace()
    return destination, zeros, {"copied_complete_records": copied,
                               "zero_padded_complete_records": padded,
                               "deleted_known_zero_records": removed}


def coordinates(address, capacities):
    values = []
    for capacity in reversed(capacities):
        values.append(address % capacity)
        address //= capacity
    return list(reversed(values))


def address_of(values, capacities):
    address = 0
    for value, capacity in zip(values, capacities):
        address = address * capacity + value
    return address


def generate_fixture(groups, payload_width, seed):
    # Acquisition and independent oracle only. Consumer split_stream never
    # calls these numeric coordinate/division helpers.
    old_bounds = [sl * sr for sl, tl, sr, tr in groups]
    old_caps = [tl * tr for sl, tl, sr, tr in groups]
    new_bounds = [s for sl, tl, sr, tr in groups for s in (sr, sl)]
    new_caps = [t for sl, tl, sr, tr in groups for t in (tr, tl)]
    size = 1
    for t in old_caps:
        size *= t
    rng = random.Random(seed)
    original = bytearray([START])
    reference = bytearray([START] + [0] * (size * (payload_width + 1)) + [END])
    for a in range(size):
        coord = coordinates(a, old_caps)
        good = all(value < bound for value, bound in zip(coord, old_bounds))
        value = rng.getrandbits(payload_width) if good else 0
        bits = [(value >> i) & 1 for i in range(payload_width)]
        original.extend(bits)
        original.append(DELIM)
        reference[1 + a * (payload_width + 1) + payload_width] = DELIM
        if good:
            image = []
            for node, (sl, tl, sr, tr) in zip(coord, groups):
                image.extend((node // sl, node % sl))
            target = address_of(image, new_caps)
            start = 1 + target * (payload_width + 1)
            reference[start:start + payload_width] = bytes(bits)
    original.append(END)
    return original, reference, old_bounds, old_caps, new_bounds, new_caps


def case(spec):
    groups, width, seed, label = spec
    started = time.monotonic()
    fixture = generate_fixture(groups, width, seed)
    original, reference, old_bounds, old_caps, new_bounds, new_caps = fixture
    source = Tape(original, "input-payload")
    old = BoxScanner(old_bounds, old_caps, "old")
    new = BoxScanner(new_bounds, new_caps, "new")
    result, zeros, flow = split_stream(source, old, new, width)
    if result.cells != reference or source.cells != original:
        raise AssertionError("complete payload, padding mask or source preservation failed")
    if old.records_advanced != new.records_advanced:
        raise AssertionError("complete box capacities differ")
    tapes = (source, result, zeros, old.counter, old.template, new.counter, new.template)
    stats = {t.name: t.stats() for t in tapes}
    metadata = (old.counter, old.template, new.counter, new.template)
    b = sum(t.bit_length() - 1 for t in old_caps)
    records = old.records_advanced
    volume = records * width
    total = sum(t.moves + t.reads + t.writes for t in tapes)
    if width < b:
        raise AssertionError("this short-record contract requires Q>=B")
    # A deliberately loose complete bound covers field delimiters, the
    # full comparisons/returns, ripple carries, bit payload and cleanup.
    if total > 100 * (volume + records * b + b * b + width):
        raise AssertionError("literal complete tape trajectory exceeds its bound")
    return {"label": label, "groups": groups, "seed": seed,
            "address_bits": b, "payload_bits": width, "complete_binary_records": records,
            "complete_payload_bits": volume, "consumer_numeric_coordinate_operations": 0,
            "all_payload_and_padding_bits_compared": len(reference),
            "output_sha256": hashlib.sha256(reference).hexdigest(), "flow": flow,
            "tapes": stats, "metadata_head_moves": sum(t.moves for t in metadata),
            "payload_and_zero_head_moves": source.moves + result.moves + zeros.moves,
            "total_counted_steps": total,
            "steps_per_complete_payload_bit": total / volume,
            "strict_Q_equals_address_bits": width == b,
            "exception_repairs_in_this_monotone_scan": 0,
            "scope": "No guarded rotation occurs in this exact monotone split; upstream repair must complete before invalid-zero deletion",
            "seconds": time.monotonic() - started}


def negative_controls():
    groups = [(3, 4, 3, 4)]
    fixture = generate_fixture(groups, 8, 20261008799)
    original, reference, old_s, old_t, new_s, new_t = fixture
    first_invalid = old_s[0]
    original[1 + first_invalid * 9] = 1
    try:
        split_stream(Tape(original, "corrupted-input"), BoxScanner(old_s, old_t, "old"),
                     BoxScanner(new_s, new_t, "new"), 8)
    except ValueError as error:
        if "nonzero invalid" not in str(error):
            raise
    else:
        raise AssertionError("deletion of nonzero invalid payload was accepted")
    box = BoxScanner([3], [4], "endpoint")
    valid = []
    while not box.finished:
        valid.append(box.valid())
        box.advance()
    if valid != [True, True, True, False]:
        raise AssertionError("comparison accepted the interval's excluded endpoint")
    full = BoxScanner([4], [4], "full-interval")
    all_valid = []
    while not full.finished:
        all_valid.append(full.valid())
        full.advance()
    if all_valid != [True] * 4:
        raise AssertionError("power-of-two full interval lost its explicit flag")
    return {"nonzero_invalid_payload_deletion_rejected": True,
            "excluded_interval_endpoint_rejected": True,
            "full_binary_interval_flag_required_and_checked": True,
            "free_numeric_countdown_not_used": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--small", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.output and args.output.exists():
        raise FileExistsError("use a fresh attempt output")
    specs = [([(31, 32, 29, 32), (7, 8, 5, 8)], 16, 20261008701, "two balanced nodes, Q=B"),
             ([(15, 16, 3, 4), (7, 8, 1, 2), (15, 16, 1, 2)], 16, 20261008702, "three unequal nodes"),
             ([(16, 16, 31, 32), (1, 2, 15, 16)], 16, 20261008703, "full intervals and unit bounds"),
             ([(127, 128, 61, 64), (3, 4, 7, 8)], 20, 20261008704, "longer sparse-padding nodes")]
    if args.small:
        specs = [([(7, 8, 5, 8), (3, 4, 3, 4)], 12, 20261008711, "two small split nodes"),
                 ([(4, 4, 3, 4), (1, 2, 3, 4)], 8, 20261008712, "small full and unit intervals")]
    started, utc_started = time.monotonic(), datetime.now(timezone.utc).isoformat()
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if args.workers == 1:
        cases = [case(spec) for spec in specs]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(case, specs))
    controls = negative_controls()
    if source_hash != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
        raise ValueError("effective source changed during the attempt")
    result = {"status": "PASS", "scope": "Exact sequential complete-payload monotone split and literal counted head trajectories; no full guarded CRT or multiplication exponent",
              "source_sha256": source_hash, "workers": args.workers, "small": args.small,
              "utc_started_at": utc_started, "utc_completed_at": datetime.now(timezone.utc).isoformat(),
              "cases": cases, "negative_controls": controls,
              "complete_records": sum(c["complete_binary_records"] for c in cases),
              "seconds": time.monotonic() - started}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "scope", "workers", "small", "complete_records", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
