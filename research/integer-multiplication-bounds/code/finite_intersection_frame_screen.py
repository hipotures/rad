#!/usr/bin/env python3
"""Discriminating frame-obstruction screen for monotone intersection sums.

A source span with a common triple point is positive for H=9I-J. Any source
span supported on fewer than nine coordinates is also positive. Remaining
source-core-zero nodes can use a nondegenerate descendant-target complement
provided those actual targets share a point. This screen checks the finite
combinatorial premises; it does not compile or claim a transferred bound.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

from finite_intersection_blocks import IntersectionCircuit
from finite_physical_target_kernels import physical_intersections


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h', type=int, nargs='+', default=[8, 12, 20, 50])
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(); assert not args.output.exists()
    start = time.monotonic(); rows = []
    result = dict(started_utc=datetime.now(timezone.utc).isoformat(), rows=rows,
        source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            [Path(__file__).name, 'finite_intersection_blocks.py', 'finite_complex_blocks.py', 'finite_physical_target_kernels.py']})
    for h in args.h:
        at = time.monotonic(); circuit = IntersectionCircuit(h); logical = circuit.verify()
        targets = physical_intersections(circuit)
        bad = [node for node in circuit.active if not circuit.core[node] and
               circuit.union[node].bit_count() >= 9 and not targets[node]]
        histogram = Counter((circuit.union[node].bit_count(), targets[node].bit_count())
                            for node in circuit.active if not circuit.core[node])
        # The chosen frame type is monotone along every original gate edge:
        # once core=0 and union>=9, every parent retains these properties.
        complement = {node for node in circuit.active if not circuit.core[node]
                      and circuit.union[node].bit_count() >= 9}
        forced = [(child,node) for node in circuit.active for child in circuit.args[node] or ()
                  if child in complement and node not in complement]
        assert not forced
        row = dict(h=h, original=logical, unresolved_nodes=len(bad), unresolved_first_ids=bad[:20],
            exact_complement_to_positive_edges=len(forced), complement_nodes=len(complement),
            source_core_zero_union_target_common_histogram={str(key):value for key,value in sorted(histogram.items())},
            premises_pass=not bad, elapsed_seconds=time.monotonic()-at,
            scope='Finite common/small-coordinate positivity and physically common target premises only; exact source-span labels, compiler and dirty/stage transfer remain unimplemented')
        rows.append(row); result['elapsed_seconds'] = time.monotonic()-start
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        print(json.dumps(dict(h=h, scalar_roles=logical['unframed_physical_roles'], unresolved=len(bad),
            complement_nodes=len(complement), seconds=row['elapsed_seconds'])), flush=True)
    result['status'] = 'Terminal finite premises PASS' if all(row['premises_pass'] for row in rows) else 'Terminal finite premises FAIL'
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
