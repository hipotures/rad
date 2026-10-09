#!/usr/bin/env python3
"""New complete-field replay of the immutable seven-tape scan consumer.

Only the consumer and its elementary encoding are imported. The expected
endpoint is reconstructed by explicit same-spectator Boolean comparisons,
without the producer's reference, probe or numeric motion verifier. This is
a finite independent replay plus scope-limited controls, not formal proof.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import time

TOPIC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOPIC / "code/transfers"))
import selected_polynomial_scan_tapes as P


PINS = {"selected_polynomial_scan_tapes.py": "0dcd1ada09c55f74b5001d14d4ffcf89a8ef0589363535f37758cd071fb385c6",
        "selected_fiber_scan_tapes.py": "5565695705b0525861a136dd0ef74e6e0b28802916f080cdc3df015b2ee62e7a"}


def parse(cells, precision, fields):
    if cells[0] != P.START or cells[-1] != P.END:
        raise AssertionError("Complete output framing was lost")
    index, rows = 1, []
    while cells[index] != P.END:
        if cells[index:index + 2] != bytes((P.ROW, P.HEADER)):
            raise AssertionError("The replay expects implicit address records")
        index += 2
        row = []
        for _ in range(2 * fields):
            digits = cells[index:index + precision]
            if len(digits) != precision or any(x not in (0, 1) for x in digits):
                raise AssertionError("A complete signed component is missing")
            value = sum(x << b for b, x in enumerate(digits))
            if digits[-1]:
                value -= 1 << precision
            row.append(value)
            index += precision
            if cells[index] != P.WORD:
                raise AssertionError("The fixed component boundary is missing")
            index += 1
        if cells[index] != P.ROW:
            raise AssertionError("The complete polynomial boundary is missing")
        index += 1
        rows.append(row)
    if index != len(cells) - 1:
        raise AssertionError("Trailing field bytes were omitted")
    return rows


def case(task):
    n, selected, old_rows, fields, fractional_bits = task
    f = len(selected)
    block = 1 << n
    count = old_rows * block
    peak = 1 << (fractional_bits - 3)
    seed = 202610091107 + n * 1009 + fields * 37 + old_rows * 13
    rng = random.Random(seed)
    original = [[peak] + [rng.randrange(-peak, peak + 1) for _ in range(2 * fields - 1)]
                for _ in range(count)]
    width = fractional_bits + f + 3
    cells = P.encode(original, 0, width)
    selected_mask = sum(1 << b for b in selected)
    spectator_mask = (block - 1) ^ selected_mask
    mask = bytes([P.START] + [P.base.SELECTED if selected_mask >> b & 1 else P.base.SPECTATOR
                             for b in range(n)] + [P.END])
    # At a fixed spectator label, numeric selected submasks have the same
    # order as their compressed selected index. This reference does not
    # maintain the producer's spectator accumulator table or carry paths.
    expected = []
    for old in range(old_rows):
        for address in range(block):
            predecessors = [old * block + y for y in range(block)
                            if (y & spectator_mask) == (address & spectator_mask)
                            and (y & selected_mask) <= (address & selected_mask)]
            expected.append([sum(original[y][c] for y in predecessors)
                             for c in range(2 * fields)])
    actual_cells, forward = P.scan(cells, mask)
    if parse(actual_cells, width, fields) != expected:
        raise AssertionError("The independent complete Boolean endpoint disagreed")
    reverse_cells, reverse = P.scan(actual_cells, mask, inverse=True)
    if reverse_cells != cells or parse(reverse_cells, width, fields) != original:
        raise AssertionError("The true inverse lost complete original fields")
    volume = len(cells) - 2
    for run in (forward, reverse):
        if run["fixed_tape_count"] != 7 or not run["ordinary_scratch_erased"]:
            raise AssertionError("The fixed-tape/ordinary scratch endpoint changed")
        if run["tapes"]["complete-accumulators"]["unit_head_moves"] > 12 * volume:
            raise AssertionError("The actual full-record head bill exceeded its bound")
        metadata = sum(run["tapes"][label]["total_steps"] for label in
                       ("immutable-mask", "binary-counter", "selected-one-count", "backward-countdown"))
        if metadata > 128 * (count + n + 1):
            raise AssertionError("The literal counter/mask bill exceeded its bound")
    wrong = []
    running = [0] * (2 * fields)
    for row in original:
        running = [a + b for a, b in zip(running, row)]
        wrong.append(running[:])
    if (old_rows > 1 or f < n) and wrong == expected:
        raise AssertionError("The omitted spectator/old-row negative did not discriminate")
    overflow_rejected = None
    if f >= 3:
        narrow = P.encode(original, 0, fractional_bits)
        try:
            P.scan(narrow, mask)
        except AssertionError as error:
            if "overflow" not in str(error):
                raise
            overflow_rejected = True
        else:
            raise AssertionError("The omitted magnitude reserve was not rejected")
    return {"n": n, "selected": list(selected), "old_rows": old_rows,
            "Gaussian_coefficients": fields, "fractional_bits": fractional_bits,
            "signed_component_width": width, "seed": seed, "records": count,
            "signed_component_values": 2 * fields * count,
            "source_input_output_sha256": sha256(cells).hexdigest(),
            "complete_forward_sha256": sha256(actual_cells).hexdigest(),
            "literal_forward": forward, "literal_inverse": reverse,
            "omitted_reserve_overflow_rejected": overflow_rejected,
            "original_integer_fields": original, "expected_integer_fields": expected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--bounded", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError("Positive workers required")
    paths = [Path(__file__).resolve(), Path(P.__file__).resolve(), Path(P.base.__file__).resolve()]
    before = {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}
    if any(before[name] != digest for name, digest in PINS.items()):
        raise AssertionError("The pinned literal consumer source changed")
    tasks = [(5, (0, 2, 4), 3, 7, 8)] if args.bounded else [
        (5, (0, 2, 4), 3, 7, 8), (7, (2, 5), 5, 33, 12),
        (4, (0, 1, 2, 3), 1, 4, 4), (6, (), 2, 11, 9)]
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / "protocol.json").write_text(json.dumps({"started_utc": datetime.now(timezone.utc).isoformat(),
            "source_sha256": before, "workers": args.workers, "tasks": tasks,
            "independent_reference": "Explicit same-spectator predecessor sums; no producer probe/reference"}, indent=2) + "\n")
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(case, tasks))
    if before != {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}:
        raise AssertionError("The full immutable source closure changed")
    result = {"status": "PASS INDEPENDENT COMPLETE SELECTED SCAN REPLAY", "rows": rows,
              "seconds": time.monotonic() - started, "source_sha256": before,
              "records": sum(r["records"] for r in rows),
              "signed_component_values": sum(r["signed_component_values"] for r in rows),
              "native_surrounding_supplier_and_exponent_not_certified": True}
    if args.output:
        (args.output / "certificate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, sort_keys=True))


if __name__ == "__main__":
    main()
