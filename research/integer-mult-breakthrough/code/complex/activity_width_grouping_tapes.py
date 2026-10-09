#!/usr/bin/env python3
"""Paid stable width grouping on seven symbol tapes.

The input is ALREADY in the prefix layout of prefix_activity_shape.py.
This word groups its complete records by activity width and undoes the
grouping after arbitrary payload changes. It does not implement the
initial prefix-layout permutation or provide a fast zeta primitive.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time

import prefix_activity_shape as prefix


SEED = 202610090702
BLANK = ord('_')
ORIGIN = ord('^')
DELIMITER = ord('|')
ZERO = ord('0')
ONE = ord('1')
STAGE_SEPARATOR = ord('#')
STAGE_END = ord('$')
TOKEN = ord('a')
MARKER = ord('x')
UNMARKED = ord('.')
NAMES = ('current', 'bucket0', 'bucket1', 'next', 'journal', 'count', 'header')


class Tape:
    """One current cell, unit moves, and a fixed finite alphabet.

    Direct buffer inspection is used only by the outer verifier. The
    consumer reads or writes exclusively at the current tape head.
    Each read, write and unit move contributes one measured step.
    """

    def __init__(self, name):
        self.name = name
        self.cells = bytearray([ORIGIN])
        self.head = 0
        self.reads = 0
        self.writes = 0
        self.moves = 0
        self.max_head = 0

    def read(self):
        self.reads += 1
        return self.cells[self.head] if self.head < len(self.cells) else BLANK

    def write(self, value):
        self.writes += 1
        if self.head == 0:
            raise AssertionError('the origin marker is immutable')
        if self.head < len(self.cells):
            self.cells[self.head] = value
        elif self.head == len(self.cells):
            self.cells.append(value)
        else:
            raise AssertionError('a consumer attempted a nonunit tape jump')

    def move(self, direction):
        if direction not in (-1, 1) or self.head + direction < 0:
            raise AssertionError('only legal unit tape moves are permitted')
        self.moves += 1
        self.head += direction
        self.max_head = max(self.max_head, self.head)

    def append(self, value):
        self.write(value)
        self.move(1)

    def rewind(self):
        while self.read() != ORIGIN:
            self.move(-1)

    def first(self):
        self.rewind()
        self.move(1)

    def clear(self):
        self.first()
        while self.read() != BLANK:
            self.write(BLANK)
            self.move(1)
        self.rewind()

    def verifier_bytes(self):
        value = bytes(self.cells[1:])
        end = value.find(bytes([BLANK]))
        if end >= 0:
            if any(c != BLANK for c in value[end:]):
                raise AssertionError('a tape contains data after a blank gap')
            value = value[:end]
        return value

    def counters(self):
        return dict(reads=self.reads, writes=self.writes, unit_moves=self.moves,
                    steps=self.reads + self.writes + self.moves,
                    maximum_visited_cell=self.max_head,
                    physical_buffer_extent=len(self.cells))


def copy_record(source, destination):
    if source.read() in (BLANK, ORIGIN):
        raise AssertionError('a complete record was unavailable')
    while True:
        value = source.read()
        if value not in (ZERO, ONE, DELIMITER):
            raise AssertionError('malformed or cropped record stream')
        destination.append(value)
        source.move(1)
        if value == DELIMITER:
            return


def copy_bucket(source, destination, journal=None):
    source.first()
    while source.read() != BLANK:
        value = source.read()
        if value not in (ZERO, ONE, DELIMITER):
            raise AssertionError('invalid complete-record bucket')
        destination.append(value)
        source.move(1)
        if value == DELIMITER and journal is not None:
            journal.append(TOKEN)


def read_key_and_return(current, header):
    """Scan the entire key header and undo all input-head moves.

    A single x marker selects the key bit of this radix stage. No
    numeric coordinate or payload arithmetic is used by this consumer.
    """
    key = None
    header.first()
    while header.read() != STAGE_END:
        value = current.read()
        if value not in (ZERO, ONE):
            raise AssertionError('the complete width header is absent')
        if header.read() == MARKER:
            key = value
        current.move(1)
        header.move(1)
    header.move(-1)
    while header.read() != ORIGIN:
        current.move(-1)
        header.move(-1)
    if key is None:
        raise AssertionError('the header has no selected radix position')
    return key


class GroupingWord:
    """Stable radix grouping and journal-based reverse on fixed tapes."""

    def __init__(self, records, key_bits):
        self.tapes = {name: Tape(name) for name in NAMES}
        self.current = self.tapes['current']
        self.other = self.tapes['next']
        self.key_bits = key_bits
        self.stages = 0
        self.initialization_steps = 0
        # Input loading and template initialization are measured too.
        self.current.move(1)
        for record in records:
            for bit in record:
                self.current.append(bit)
            self.current.append(DELIMITER)
        header = self.tapes['header']
        header.move(1)
        header.append(MARKER)
        for _ in range(key_bits - 1):
            header.append(UNMARKED)
        header.append(STAGE_END)
        header.rewind()
        self.tapes['journal'].move(1)
        self.initialization_steps = self.steps()

    def steps(self):
        return sum(t.reads + t.writes + t.moves for t in self.tapes.values())

    def forward(self):
        b0, b1 = self.tapes['bucket0'], self.tapes['bucket1']
        journal, header = self.tapes['journal'], self.tapes['header']
        while True:
            self.current.first()
            b0.first()
            b1.first()
            self.other.first()
            while self.current.read() != BLANK:
                key = read_key_and_return(self.current, header)
                copy_record(self.current, b0 if key == ZERO else b1)
                journal.append(key)
            journal.append(STAGE_SEPARATOR)
            copy_bucket(b0, self.other, journal=journal)
            copy_bucket(b1, self.other)
            journal.append(STAGE_END)
            self.current.clear()
            b0.clear()
            b1.clear()
            self.current, self.other = self.other, self.current
            self.stages += 1
            # Advance the marker by one measured move, not an index jump.
            header.first()
            while header.read() != MARKER:
                header.move(1)
            header.write(UNMARKED)
            header.move(1)
            if header.read() == STAGE_END:
                break
            header.write(MARKER)
        header.clear()
        journal.move(-1)
        if journal.read() != STAGE_END:
            raise AssertionError('the reverse journal is incomplete')

    def inverse(self):
        b0, b1 = self.tapes['bucket0'], self.tapes['bucket1']
        journal, count = self.tapes['journal'], self.tapes['count']
        while journal.read() != ORIGIN:
            if journal.read() != STAGE_END:
                raise AssertionError('reverse dispatch did not start at a stage boundary')
            count.first()
            journal.move(-1)
            while journal.read() == TOKEN:
                count.append(TOKEN)
                journal.move(-1)
            if journal.read() != STAGE_SEPARATOR:
                raise AssertionError('the saved split count was corrupted')
            journal.move(-1)
            while journal.read() in (ZERO, ONE):
                journal.move(-1)
            if journal.read() not in (ORIGIN, STAGE_END):
                raise AssertionError('partition-pattern boundary was corrupted')
            journal.move(1)
            self.current.first()
            b0.first()
            b1.first()
            count.first()
            # The unary threshold consumes one token per whole record.
            while self.current.read() != BLANK:
                if count.read() == TOKEN:
                    copy_record(self.current, b0)
                    count.move(1)
                else:
                    copy_record(self.current, b1)
            if count.read() != BLANK:
                raise AssertionError('split count exceeded the complete population')
            b0.first()
            b1.first()
            self.other.first()
            while journal.read() in (ZERO, ONE):
                key = journal.read()
                copy_record(b0 if key == ZERO else b1, self.other)
                journal.move(1)
            if journal.read() != STAGE_SEPARATOR or b0.read() != BLANK or b1.read() != BLANK:
                raise AssertionError('partition journal lost or duplicated a whole record')
            self.current.clear()
            b0.clear()
            b1.clear()
            count.clear()
            self.current, self.other = self.other, self.current
            # Erase only the completed journal stage, preserving the
            # previous end marker. Every erased cell and return is paid.
            journal.move(1)
            while journal.read() != BLANK:
                journal.move(1)
            journal.move(-1)
            if journal.read() != STAGE_END:
                raise AssertionError('erasure missed the saved stage end')
            journal.write(BLANK)
            journal.move(-1)
            while journal.read() not in (ORIGIN, STAGE_END):
                journal.write(BLANK)
                journal.move(-1)
        if any(t.verifier_bytes() for name, t in self.tapes.items() if t is not self.current):
            raise AssertionError('temporary tapes or routing metadata were not erased')

    def records_for_verifier(self):
        raw = self.current.verifier_bytes()
        if raw and raw[-1] != DELIMITER:
            raise AssertionError('the final whole record is cropped')
        return raw.split(bytes([DELIMITER]))[:-1]

    def replace_payload_for_verifier(self, changed):
        """Outside child oracle: overwrite only actual payload cells.

        Its computation is explicitly excluded from routing timing. The
        subsequent inverse must move its newly changed fields, rather
        than replay an original-data snapshot. No keys or tags change.
        """
        before = self.records_for_verifier()
        if len(before) != len(changed) or any(len(a) != len(b) for a, b in zip(before, changed)):
            raise AssertionError('outside child changed complete record framing')
        flat = bytes([DELIMITER]).join(changed) + bytes([DELIMITER])
        if len(flat) != len(self.current.verifier_bytes()):
            raise AssertionError('outside child changed stream volume')
        self.current.cells[1:1 + len(flat)] = flat


def bits(value, width):
    return bytes(ONE if value & (1 << j) else ZERO for j in range(width))


def unsigned(raw):
    if any(v not in (ZERO, ONE) for v in raw):
        raise AssertionError('invalid bit header')
    return sum((v == ONE) << j for j, v in enumerate(raw))


def fixture(task):
    h, f, K, component_bits = task
    address_bits = h * f * K
    M = 1 << address_bits
    ell = f.bit_length()
    rng = Random(SEED + 100000 * h + 1000 * f + 100 * K + component_bits)
    records = []
    groups = {}
    for encoded in range(M):
        _, width = prefix.decode(encoded, h, f, K)
        tag = bits(encoded, address_bits)
        # Four complete signed Gaussian fields, eight raw component
        # bitstrings. Their signs/grid meaning is immaterial to routing.
        fields = b''.join(bits(rng.getrandbits(component_bits), component_bits) for _ in range(8))
        records.append(bits(width, ell) + tag + fields)
        groups.setdefault((width, encoded >> (width * K)), []).append(encoded)
    return records, groups, ell, address_bits


def probe(task):
    h, f, K, component_bits = task
    records, groups, ell, address_bits = fixture(task)
    M = len(records)
    Q = len(records[0]) + 1  # record delimiter is included in movement.
    word = GroupingWord(records, ell)
    started = word.steps()
    word.forward()
    forward_steps = word.steps() - started
    grouped = word.records_for_verifier()
    reference = sorted(records, key=lambda r: unsigned(r[:ell]))
    if grouped != reference:
        raise AssertionError('stable width grouping differs on complete payload records')
    tags = [unsigned(record[ell:ell + address_bits]) for record in grouped]
    positions = {tag: index for index, tag in enumerate(tags)}
    populations = [0] * (f + 1)
    for record in grouped:
        populations[unsigned(record[:ell])] += 1
    for (width, p), original in groups.items():
        expected = list(range(p << (width * K), (p + 1) << (width * K)))
        if original != expected:
            raise AssertionError('input prefix fiber was not the whole complete-K cube')
        first = positions[original[0]]
        if tags[first:first + len(original)] != original:
            raise AssertionError('stable width grouping split or reversed a complete child fiber')
    journal_bytes = len(word.tapes['journal'].verifier_bytes())
    if journal_bytes > ell * (2 * M + 2):
        raise AssertionError('partition journal exceeds its linear metadata bound')
    # Change every real/imaginary raw field at its first and last bit.
    # Keep complete key/tag framing, as actual block children must do.
    changed = []
    header_size = ell + address_bits
    for record in grouped:
        value = bytearray(record)
        for field in range(8):
            for offset in (0, component_bits - 1):
                index = header_size + field * component_bits + offset
                value[index] = ONE if value[index] == ZERO else ZERO
        changed.append(bytes(value))
    word.replace_payload_for_verifier(changed)
    expected_changed = {unsigned(r[ell:ell + address_bits]): r for r in changed}
    started = word.steps()
    word.inverse()
    reverse_steps = word.steps() - started
    restored = word.records_for_verifier()
    if restored != [expected_changed[tag] for tag in range(M)]:
        raise AssertionError('routing inverse lost the newly changed arbitrary dirty payload')
    counters = {name: tape.counters() for name, tape in word.tapes.items()}
    # This conservative bound covers full copying/erasure/rewinds, every
    # header scan, the unary counter and both metadata directions.
    conservative = 160 * ell * (M * (Q + ell + 2) + 1)
    measured = forward_steps + reverse_steps
    if measured > conservative:
        raise AssertionError('literal routing exceeded the stated linear-pass bound')
    return dict(h=h, columns=f, chunk_bits=K, address_bits=address_bits,
                complete_records=M, record_symbols_including_delimiter=Q,
                width_key_bits=ell, activity_populations=populations,
                original_complete_K_fibers=len(groups), all_fibers_preserved=True,
                arbitrary_Gaussian_fields=4 * M, raw_component_bits=component_bits,
                all_changed_component_fields_restored=8 * M,
                physical_tape_count=7, alphabet_symbols=10,
                forward_steps=forward_steps, reverse_steps=reverse_steps,
                initialization_steps=word.initialization_steps,
                measured_routing_steps=measured, conservative_step_bound=conservative,
                steps_per_complete_symbol_per_radix_stage=measured / (M * Q * ell),
                saved_partition_journal_symbols=journal_bytes,
                per_tape_counters=counters, metadata_and_scratch_erased=True,
                initial_prefix_permutation_executed=False,
                child_payload_changes_are_outside_timing=True,
                scope='Literal fixed-tape width batching on an already prefix-ordered complete stream, including changed arbitrary fields and reversible journal. No initial prefix route or fast Z supplier.')


def negative_controls():
    records, _, ell, _ = fixture((3, 1, 1, 4))
    word = GroupingWord(records, ell)
    word.forward()
    journal = word.tapes['journal']
    journal.cells[1] = STAGE_SEPARATOR
    rejected = False
    try:
        word.inverse()
    except AssertionError:
        rejected = True
    if not rejected:
        raise AssertionError('corrupted partition journal negative did not reject')
    bad = GroupingWord(records, ell)
    bad.forward()
    values = bad.records_for_verifier()
    try:
        bad.replace_payload_for_verifier([r[:-1] for r in values])
    except AssertionError:
        cropped = True
    else:
        raise AssertionError('cropped complete payload negative did not reject')
    return dict(corrupted_partition_journal_rejected=rejected,
                cropped_complete_payload_rejected=cropped)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    sources = [Path(__file__), Path(prefix.__file__)]
    hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in sources}
    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [(3, 1, 1, 8), (3, 2, 1, 16)] if args.bounded else [
        (3, 1, 1, 8), (3, 2, 1, 16), (3, 1, 2, 32), (3, 2, 2, 64)]
    if args.workers == 1:
        cases = list(map(probe, tasks))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, tasks))
    negatives = negative_controls()
    if any(sha256(p.read_bytes()).hexdigest() != hashes[p.name] for p in sources):
        raise AssertionError('grouping source closure changed during execution')
    result = dict(status='PASS PAID STABLE ACTIVITY WIDTH TAPE GROUPING',
                  started_utc=started_utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=hashes[Path(__file__).name], source_closure=hashes,
                  workers=args.workers, bounded=args.bounded, cases=cases,
                  negative_controls=negatives, seconds=time.monotonic() - started,
                  scope='Exact fixed-tape width grouping and reverse after arbitrary payload changes. Initial prefix permutation, native zeta contract, precision transfer and kappa remain open.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], cases=len(cases),
                          complete_records=sum(c['complete_records'] for c in cases),
                          literal_tape_steps=sum(c['measured_routing_steps'] for c in cases),
                          seconds=result['seconds'])), flush=True)


if __name__ == '__main__':
    main()
