#!/usr/bin/env python3
"""Exact finite-field lookup components and a paid sequential-access boundary.

Alman's arXiv:2211.04643v1 motivates full-domain block tables. The streaming
lookup here charges every abstract tape read/write/head move, without assuming
RAM lookup. It is a particular three-tape scan, not an optimality theorem or
a formal finite-control machine. OpenAI Codex assisted this implementation.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import time


def transform(vector: tuple[int, ...], prime: int) -> tuple[int, ...]:
    values = list(vector)
    stride = 1
    while stride < len(values):
        for base in range(0, len(values), 2 * stride):
            for offset in range(stride):
                a, b = values[base + offset], values[base + offset + stride]
                values[base + offset] = (a + b) % prime
                values[base + offset + stride] = (a - b) % prime
        stride *= 2
    return tuple(values)


def direct(vector: tuple[int, ...], prime: int) -> tuple[int, ...]:
    return tuple(sum((-1) ** ((i & j).bit_count() % 2) * value
                     for j, value in enumerate(vector)) % prime
                 for i in range(len(vector)))


def encode(vector: tuple[int, ...], prime: int) -> str:
    width = (prime - 1).bit_length()
    assert all(0 <= x < prime for x in vector)
    return "".join(format(value, f"0{width}b") for value in vector)


def decode(bits: str, prime: int) -> tuple[int, ...]:
    width = (prime - 1).bit_length()
    assert len(bits) % width == 0 and set(bits) <= {"0", "1"}
    values = tuple(int(bits[j:j + width], 2) for j in range(0, len(bits), width))
    assert all(value < prime for value in values), "Invalid field-symbol code"
    return values


class Tape:
    def __init__(self, content: str):
        assert content.startswith("^")
        self.content = content
        self.head = 1
        self.reads = 0
        self.moves = 0

    def read(self) -> str:
        assert 0 <= self.head < len(self.content), "Unexpected end of tape"
        self.reads += 1
        return self.content[self.head]

    def move(self, direction: int) -> None:
        assert direction in (-1, 1)
        self.head += direction
        self.moves += 1

    def next(self) -> str:
        value = self.read()
        self.move(1)
        return value

    def rewind_query(self) -> None:
        while self.read() != "^":
            self.move(-1)
        self.move(1)


def scan(table: str, query: tuple[int, ...], prime: int) -> dict:
    data = Tape(table)
    key = Tape("^" + encode(query, prime) + "|")
    output = []
    records = 0
    while True:
        matched = True
        while True:
            symbol = data.next()
            if symbol == "|":
                assert key.read() == "|", "Mismatched key width"
                break
            assert symbol in "01", "Invalid table-key framing"
            matched &= key.next() == symbol
        key.rewind_query()
        while True:
            symbol = data.next()
            if symbol == "\n":
                break
            assert symbol in "01", "Invalid table-value framing"
            if matched:
                output.append(symbol)
        records += 1
        if matched:
            result = decode("".join(output), prime)
            assert len(result) == len(query)
            return {"output": result, "records_scanned": records,
                    "table_reads": data.reads, "table_head_moves": data.moves,
                    "query_reads": key.reads, "query_head_moves": key.moves,
                    # Fresh sequential output writes plus its head movement.
                    "output_writes": len(output), "output_head_moves": len(output),
                    "query_and_table_unchanged": True}


def capacity(log2_global_width: int, prime: int, budget_numerator: int = 1,
             budget_denominator: int = 2) -> dict:
    """Largest power-of-two full-domain block satisfying q^K <= N^delta."""
    assert log2_global_width > 0 and prime >= 2
    budget_bits = log2_global_width * budget_numerator // budget_denominator
    block = 1
    while prime ** (2 * block) <= 2**budget_bits:
        block *= 2
    assert prime**block <= 2**budget_bits, "Budget cannot hold one symbol"
    assert prime**(2 * block) > 2**budget_bits
    return {"log2_global_width": log2_global_width, "prime": prime,
            "setup_budget_bits": budget_bits, "maximum_full_domain_block": block,
            "maximum_grouped_address_bits": block.bit_length() - 1,
            "complete_domain_size_bits": (prime**block - 1).bit_length(),
            "next_doubled_block_rejected": True}


def probe(case: tuple[int, int]) -> dict:
    prime, block = case
    assert prime in (3, 5, 7) and block > 0 and block & (block - 1) == 0
    start = time.perf_counter()
    rows = []
    checked_values = 0
    for vector in product(range(prime), repeat=block):
        value = transform(vector, prime)
        assert value == direct(vector, prime)
        rows.append(encode(vector, prime) + "|" + encode(value, prime) + "\n")
        checked_values += block
    table = "^" + "".join(rows)
    rng = random.Random(20261009 + 100 * prime + block)
    queries = [(0,) * block, (prime - 1,) * block]
    queries += [tuple(rng.randrange(prime) for _ in range(block)) for _ in range(12)]
    measurements = []
    for query in queries:
        receipt = scan(table, query, prime)
        assert receipt.pop("output") == direct(query, prime)
        receipt["query"] = list(query)
        receipt["charged_access_steps"] = sum(receipt[name] for name in (
            "table_reads", "table_head_moves", "query_reads", "query_head_moves",
            "output_writes", "output_head_moves"))
        measurements.append(receipt)
    assert measurements[0]["records_scanned"] == 1
    assert measurements[1]["records_scanned"] == prime**block
    return {"prime": prime, "block": block, "status": "PASS",
            "complete_table_records": prime**block, "table_bytes": len(table),
            "table_sha256": hashlib.sha256(table.encode()).hexdigest(),
            "checked_output_values": checked_values, "lookups": measurements,
            "elapsed_seconds": time.perf_counter() - start,
            "scope": "Exact complete finite field table and paid sequential scan; no optimal native access claim"}


def bounded() -> dict:
    result = probe((3, 2))
    try:
        decode("11", 3)
    except AssertionError:
        invalid_code_rejected = True
    else:
        raise AssertionError("Unused field code was admitted")
    try:
        scan("^00|00!\n", (0,), 3)
    except AssertionError:
        invalid_framing_rejected = True
    else:
        raise AssertionError("Invalid table framing was admitted")
    budgets = [capacity(d, 3) for d in (16, 64, 256)]
    return {"status": "PASS", "case": result, "capacity": budgets,
            "invalid_code_rejected": invalid_code_rejected,
            "invalid_framing_rejected": invalid_framing_rejected,
            "scope": "Exact finite tables and scoped full-domain setup/access boundary; no exponent certificate"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--bounded", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.bounded:
        result = bounded()
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, ((3, 2), (3, 4), (3, 8), (5, 4))))
        result = {"status": "PASS", "workers": args.workers, "cases": cases,
                  "capacity": [capacity(d, 3) for d in (64, 256, 1024, 4096, 16384, 65536)],
                  "scope": "Complete-domain table lemma and specific scan; no fixed-tape optimality theorem"}
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        if args.output.exists():
            raise SystemExit("Refusing to replace an existing result")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
