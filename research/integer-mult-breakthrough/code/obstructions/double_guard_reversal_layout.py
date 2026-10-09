#!/usr/bin/env python3
"""Independent two-terminal-guard geometry without extra address volume.

Labels represent complete K-bit ranges. This is a compaction and moment
majorant certificate, not the missing active Gaussian block or native runtime.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


def probe(case):
    h, maximum_g = case
    count = 0
    for g in range(1, maximum_g + 1):
        slot = 2 * (g + 1)
        for remainder in range(2 * h):
            e = h * slot + remainder
            guards = {row * slot + j for row in range(h) for j in (g, 2 * g + 1)}
            leftovers = set(range(h * slot, e))
            if len(guards | leftovers) >= 4 * h:
                raise AssertionError('The fixed guard/remainder bill grew')
            for width in range(1, h + 1):
                active = {row * slot + j for row in range(width)
                          for j in range(slot) if j not in (g, 2 * g + 1)}
                child = 2 * g * width
                prefix = set(range(child))
                holes, donors = prefix - active, active - prefix
                if holes != prefix & guards or len(holes) != len(donors) or len(holes) > 2 * width:
                    raise AssertionError('Two guarded bands failed full-chunk compaction')
                pairs = list(zip(sorted(holes), sorted(donors, reverse=True)))
                names = list(range(e))
                for a, b in pairs:
                    names[a], names[b] = names[b], names[a]
                if set(names[:child]) != active or set(names[:child]) & (guards | leftovers):
                    raise AssertionError('A guard or remainder entered the full active child')
                for a, b in reversed(pairs):
                    names[a], names[b] = names[b], names[a]
                if names != list(range(e)):
                    raise AssertionError('A spectator address range was not restored')
                if not Fraction(child, e) <= Fraction(width, h) or not child < e:
                    raise AssertionError('The unchanged positive-power majorant failed')
                if width == h and e - child != 2 * h + remainder:
                    raise AssertionError('The nominal full child failed to strictly decrease')
                count += 1
    return dict(h=h, maximum_g=maximum_g, complete_geometry_cases=count,
                extra_address_ranges=0, local_guard_and_remainder_kernels_less_than=4 * h,
                enter_whole_chunk_exchanges_at_most='2*child_rank',
                child_selected_width='2*g*child_rank', moment_majorant='child_rank/h',
                full_child_strict_decrease=True, independent_subcalls_required=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or args.output and args.output.exists():
        raise ValueError('Positive workers and a fresh optional output are required')
    source = Path(__file__).resolve()
    digest = sha256(source.read_bytes()).hexdigest()
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    source_sha256=digest, seed=None, input='Complete generated K-range labels',
                    scope='Same-volume double-guard compaction; active Gaussian network is a separate assumption')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, [(2, 4)] if args.bounded else [(h, 32) for h in (2, 3, 4, 6)]))
    if sha256(source.read_bytes()).hexdigest() != digest:
        raise ValueError('Source changed during exact geometry verification')
    summary = dict(status='PASS TWO-GUARD SAME-VOLUME GEOMETRY', cases=rows,
                   complete_gaussian_network=False, new_multiplier_exponent=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'], geometry_cases=sum(r['complete_geometry_cases'] for r in rows))))


if __name__ == '__main__':
    main()
