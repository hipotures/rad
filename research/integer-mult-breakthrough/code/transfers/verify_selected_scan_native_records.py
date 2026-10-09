#!/usr/bin/env python3
"""Bounded complete-polynomial replay with implicit physical address labels.

This checks that the literal consumer needs no per-record address headers.
Delimiters encode the fixed component boundaries; translating to/from an
unframed binary record is the explicitly charged ordinary linear scan.
No high-flux order, polynomial-time native multiplier or new exponent follows.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import selected_polynomial_scan_tapes as poly


PINS = {'selected_polynomial_scan_tapes.py': '0dcd1ada09c55f74b5001d14d4ffcf89a8ef0589363535f37758cd071fb385c6',
        'selected_fiber_scan_tapes.py': '5565695705b0525861a136dd0ef74e6e0b28802916f080cdc3df015b2ee62e7a'}


def decode(cells, word_bits, coefficients):
    """Reference-only full sequential output parse with implicit labels."""
    poly.require(cells[0] == poly.START and cells[-1] == poly.END, 'Full native record framing retained')
    position, rows = 1, []
    while cells[position] != poly.END:
        poly.require(cells[position] == poly.ROW and cells[position + 1] == poly.HEADER,
                     'No numeric address header is present or needed')
        position += 2
        row = []
        for _ in range(2 * coefficients):
            word = cells[position:position + word_bits]
            poly.require(all(bit in (0, 1) for bit in word), 'Every complete signed component is retained')
            value = sum(bit << index for index, bit in enumerate(word))
            if word[-1]:
                value -= 1 << word_bits
            row.append(value)
            position += word_bits
            poly.require(cells[position] == poly.WORD, 'Each coefficient keeps its exact full width')
            position += 1
        poly.require(cells[position] == poly.ROW, 'Full polynomial boundary retained')
        position += 1
        rows.append(row)
    poly.require(position == len(cells) - 1, 'All physical record bytes are parsed')
    return rows


def probe(task):
    n, selected, old_rows, coefficients, precision = task
    selected = tuple(selected)
    f, count, peak = len(selected), old_rows << n, 1 << (precision - 2)
    # Input coefficients lie in the unit disk on the 2^-p Gaussian grid.
    original = [[peak] + [((index * 11 + component * 7) % (2 * peak + 1)) - peak
                         for component in range(1, 2 * coefficients)] for index in range(count)]
    word_bits = precision + f + 3
    cells = poly.encode(original, 0, word_bits)
    mask = bytes([poly.START] + [poly.base.SELECTED if bit in selected else poly.base.SPECTATOR
                                for bit in range(n)] + [poly.END])
    actual_cells, forward = poly.scan(cells, mask)
    actual = decode(actual_cells, word_bits, coefficients)
    poly.require(actual == poly.reference(original, n, selected), 'Every implicit-address fiber and full coefficient agrees')
    reverse_cells, reverse = poly.scan(actual_cells, mask, inverse=True)
    poly.require(reverse_cells == cells and decode(reverse_cells, word_bits, coefficients) == original,
                 'True bit-serial inverse restores all implicit native record positions')
    volume = len(cells) - 2
    for run in (forward, reverse):
        metadata = sum(run['tapes'][name]['total_steps'] for name in
                       ('immutable-mask', 'binary-counter', 'selected-one-count', 'backward-countdown'))
        poly.require(metadata <= 128 * (count + n + 1), 'Implicit-address counter still has linear amortized metadata')
        poly.require(run['tapes']['complete-accumulators']['unit_head_moves'] <= 12 * volume,
                     'All implicit complete accumulator record moves are charged')
    return {'n': n, 'selected_positions': list(selected), 'old_rows': old_rows,
            'records': count, 'Gaussian_coefficients_per_record': coefficients,
            'signed_component_values': 2 * coefficients * count, 'precision_p': precision,
            'selected_width_f': f, 'component_width': word_bits, 'per_record_address_header_bits': 0,
            'volume_symbols': volume, 'forward_total_steps': sum(t['total_steps'] for t in forward['tapes'].values()),
            'inverse_total_steps': sum(t['total_steps'] for t in reverse['tapes'].values()),
            'ordinary_scratch_erased': forward['ordinary_scratch_erased'] and reverse['ordinary_scratch_erased']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    poly.require(args.workers > 0, 'Positive workers required')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
    own = Path(__file__).resolve()
    paths = [own, Path(poly.__file__).resolve(), Path(poly.base.__file__).resolve()]
    before = {path.name: sha256(path.read_bytes()).hexdigest() for path in paths}
    poly.require(all(before[name] == digest for name, digest in PINS.items()), 'Accepted literal source closure must be pinned')
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    tasks = [(4, (0, 2), 2, 5, 7)] if args.bounded else [
        (4, (0, 2), 2, 5, 7), (6, (1, 4), 3, 17, 16),
        (7, (0, 3, 6), 1, 65, 24), (5, (), 2, 9, 8)]
    if args.workers == 1:
        rows = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows = list(pool.map(probe, tasks))
    poly.require(all(sha256(path.read_bytes()).hexdigest() == before[path.name] for path in paths), 'All source bytes stay unchanged')
    result = {'status': 'PASS headerless complete native-format selected scan controls',
              'started_utc': started, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.monotonic() - tick, 'workers': args.workers, 'bounded': args.bounded,
              'source_sha256': before, 'cases': rows,
              'scope': 'Literal natural scan with implicit record positions and paid p+f+3 signed widths; delimiter setup analytic, no high-flux or faster full supplier'}
    if args.output:
        (args.output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'cases'}, sort_keys=True))


if __name__ == '__main__':
    main()
