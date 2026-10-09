#!/usr/bin/env python3
"""Independent complete-chunk guard geometry and positive-power majorant.

No producer is imported. Geometry alone does not supply the missing whole
Gaussian network, contracting moment, native tape algorithm or exponent.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

TOPIC = Path(__file__).resolve().parents[2]
PINS = {'code/transfers/guarded_slot_layout.py': '5c5e9b8fdfbc9685582bd75ce6654fa0c78482e8cbe698a7c943811035eba99e',
        'configs/transfers/guarded-slot-layout.json': 'f3800fa4209260a223a88e58ab8de4f51def2ae1b07360f461d5d0381d44ca2e'}


def geometry(h):
    count, swaps, decreases = 0, 0, 0
    for e in range(2 * h, 12 * h + 1):
        f, remainder = e // h - 1, e % h
        guards = {slot * (f + 1) + f for slot in range(h)}
        if h + remainder >= 2 * h or f < 1:
            raise AssertionError('The paid guard count or active width changed')
        for t in range(1, h + 1):
            active = {slot * (f + 1) + column
                      for slot in range(t) for column in range(f)}
            child = t * f
            prefix = set(range(child))
            holes, donors = prefix - active, active - prefix
            if holes != prefix & guards or len(holes) != len(donors) or len(holes) > t:
                raise AssertionError('Complete-chunk holes are not paid guards')
            exchanges = list(zip(sorted(holes, reverse=True), sorted(donors)))
            names = list(range(e))
            for a, b in exchanges:
                names[a], names[b] = names[b], names[a]
            if set(names[:child]) != active or set(names[:child]) & guards:
                raise AssertionError('A transformed guard entered the active child')
            for a, b in reversed(exchanges):
                names[a], names[b] = names[b], names[a]
            if names != list(range(e)):
                raise AssertionError('The complete address chunks did not return')
            if not Fraction(child, e) <= Fraction(t, h) or not child < e:
                raise AssertionError('The majorant or selected-width decrease failed')
            if t == h and not child <= e - h:
                raise AssertionError('A nominal full-width child failed to decrease')
            count += 1
            swaps += len(exchanges)
            decreases += t == h
    return dict(h=h, geometry_cases=count, actual_enter_exchanges=swaps,
                full_rank_strict_decrease_cases=decreases,
                complete_chunks_restored=True, positive_power_majorant=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or (args.output and args.output.exists()):
        raise ValueError('Positive workers and a fresh optional output are required')
    pins = {**PINS, str(Path(__file__).resolve().relative_to(TOPIC)):
            sha256(Path(__file__).read_bytes()).hexdigest()}
    for name, digest in pins.items():
        if sha256((TOPIC / name).read_bytes()).hexdigest() != digest:
            raise ValueError('A reviewed source or config changed: ' + name)
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    workers=args.workers, source_and_data_pins=pins,
                    producer_imports=False, seed=None)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(geometry, [4] if args.bounded else [4, 5, 6, 8]))
    for name, digest in pins.items():
        if sha256((TOPIC / name).read_bytes()).hexdigest() != digest:
            raise ValueError('A source changed during the independent review')
    summary = dict(status='PASS INDEPENDENT GUARD GEOMETRY', cases=rows,
                   scope='Independent label-set compaction and exact child majorant; all-size Gaussian block and native suppliers remain conditional',
                   complete_native_network=False, new_multiplier_exponent=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'],
                         geometry_cases=sum(r['geometry_cases'] for r in rows))))


if __name__ == '__main__':
    main()
