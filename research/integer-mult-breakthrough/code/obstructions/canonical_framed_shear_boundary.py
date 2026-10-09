#!/usr/bin/env python3
"""Exact canonical wrapper controls for the geodesic framed identity shear.

This named wrapper erases the apparent endpoint saving. It is not an
optimal-wrapper lower bound and does not exclude a changed bulk architecture.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import geodesic_side_capacity as geometry
from unitary_dyadic import Gaussian, ZERO, ONE, ALPHA

BETA = ALPHA.conjugate()


def line(values, label, h, columns, inverse=False):
    data = list(values)
    lo, hi = (BETA, ALPHA) if inverse else (ALPHA, BETA)
    for column in range(columns):
        mask = sum(((label >> j) & 1) << (j * columns + column) for j in range(h))
        for a in range(len(data)):
            b = a ^ mask
            if a < b:
                x, y = data[a], data[b]
                data[a], data[b] = lo * x + hi * y, hi * x + lo * y
    return data


def full(values, bits):
    data = list(values)
    for bit in range(bits):
        data = line(data, 1 << bit, bits, 1)
    return data


def framed(x, y, label, h, columns):
    virtual = line(x, label, h, columns, True)
    combined = [a + b for a, b in zip(y, virtual)]
    return full(virtual, h * columns), full(line(combined, label, h, columns, True), h * columns)


def canonical(x, y, label, h, columns, omission=None):
    source = x if omission == 'source_encoding' else line(x, label, h, columns)
    out_x, out_y = framed(source, y, label, h, columns)
    if omission != 'sink_return':
        out_y = line(out_y, label, h, columns)
    if omission != 'scalar_cleanup':
        out_y = [a - b for a, b in zip(out_y, out_x)]
    return out_x, out_y


def operator_controls(bounded):
    specs = [(3, 7, 2)] if bounded else [(h, label, 1) for h in range(1, 5)
                for label in range(1, 1 << h) if label.bit_count() % 2] + [(3, 7, 2)]
    columns_checked = 0
    negatives = set()
    for h, label, columns in specs:
        size = 1 << (h * columns)
        for initial_column in range(2 * size):
            x = [ONE if a == initial_column else ZERO for a in range(size)]
            y = [ONE if size + a == initial_column else ZERO for a in range(size)]
            expected = full(x, h * columns), full(y, h * columns)
            assert canonical(x, y, label, h, columns) == expected
            translation = sum(((label >> j) & 1) << (j * columns + c)
                              for j in range(h) for c in range(columns))
            assert line(line(x, label, h, columns), label, h, columns) == [
                x[a ^ translation] for a in range(size)]
            for omission in ('source_encoding', 'sink_return', 'scalar_cleanup'):
                if omission not in negatives and canonical(x, y, label, h, columns, omission) != expected:
                    negatives.add(omission)
            columns_checked += 1
    assert negatives == {'source_encoding', 'sink_return', 'scalar_cleanup'}
    return dict(complete_bank_address_columns=columns_checked, cases=specs,
                detected_omissions=sorted(negatives), scope='Literal exact operators for the named canonical repair; no optimal-wrapper or native-time lower bound.')


def capacity(h):
    row = geometry.case(h)
    p = row['profile']
    multiplicities = dict(p['child_multiplicities'])
    multiplicities[1] += 2 * row['source_banks']
    total = sum(width * count for width, count in multiplicities.items())
    q = row['center_features']
    assert total == p['W'] * h + 2 * q * h
    wrapped = dict(p, total_rank=total, deficit=-2 * q * h,
                   child_multiplicities=multiplicities)
    interval = geometry.arithmetic.moment_interval(wrapped, geometry.TARGET)
    assert interval[0] > 1
    return dict(h=h, framed_profile_root=row['conditional_root_bracket'],
                extra_width_one_calls=2 * row['source_banks'],
                canonical_profile=wrapped, canonical_target_moment_interval=interval,
                status='ABOVE ONE AFTER PAID CANONICAL WRAPPER')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh output directory')
    paths = [Path(__file__), Path(geometry.__file__), Path(geometry.arithmetic.__file__),
             Path(__file__).with_name('unitary_dyadic.py')]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    source_sha256={str(p): sha256(p.read_bytes()).hexdigest() for p in paths})
    controls = operator_controls(args.bounded)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(capacity, [9] if args.bounded else [9, 10, 12, 16]))
    result = dict(status='PASS NAMED CANONICAL WRAPPER BOUNDARY', controls=controls,
                  capacity=geometry.arithmetic.serializable(rows),
                  scope='The geodesic word is a complete framed shear under its physical interface premises. These separate canonical wrappers eliminate its saving; a different shared or bulk architecture remains open.')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], complete_operator_columns=controls['complete_bank_address_columns'], canonical_profiles_above_one=len(rows))))


if __name__ == '__main__':
    main()
