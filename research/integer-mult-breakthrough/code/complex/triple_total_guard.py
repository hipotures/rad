#!/usr/bin/env python3
"""Complete scalar coefficient-prefix guards for the integral triple basis.

Every shear multiplication temporary is included. This checks the actual
scalar word at selected h; it does not price phase children or tape buffers.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter

from triple_total_centers import word, feature, counts


def prefix(gates, volume, inverse=False):
    rows = [{j: 1} for j in range(volume)]
    norms = [1]*volume
    maximum = 1
    maximum_entry = 1
    index = None
    order = reversed(gates) if inverse else gates
    for position, gate in enumerate(order):
        kind, target, *args = gate
        if kind == 'scale':
            coefficient = args[0]
            assert coefficient == -1
            rows[target] = {j: -value for j, value in rows[target].items()}
        else:
            assert kind == 'add'
            source, c = args
            coefficient = int(-c if inverse else c)
            assert abs(coefficient) == 1
            # A separately materialized c*source has the same row norm,
            # but it still participates explicitly in the maximum.
            if norms[source] > maximum:
                maximum = norms[source]; index = (position, 'temporary', source)
            row = rows[target]
            for j, value in rows[source].items():
                old = row.get(j, 0)
                new = old+coefficient*value
                norms[target] += abs(new)-abs(old)
                if new:
                    row[j] = new
                    maximum_entry = max(maximum_entry, abs(new))
                elif j in row:
                    del row[j]
        if norms[target] > maximum:
            maximum = norms[target]; index = (position, 'bank', target)
    assert norms == [sum(abs(x) for x in row.values()) for row in rows]
    return dict(maximum_row_l1=maximum, maximum_coefficient=maximum_entry,
                maximum_witness=index, endpoint_row_l1=max(norms)), rows


def probe(h):
    started = perf_counter()
    compiled = word(h)
    sources, gates = compiled['source_order'], compiled['gates']
    v = len(sources)
    forward, rows = prefix(gates, v)
    for center in range(h):
        assert rows[center] == {j: feature(center, source) for j, source in enumerate(sources)
                                if feature(center, source)}
    assert rows[h:] == [{j: 1} for j in range(h, v)]
    assert forward['maximum_row_l1'] == v and forward['maximum_coefficient'] == 1
    backward, inverse_rows = prefix(gates, v, True)
    # Complete basis composition of B^-1 B, exploiting sparse rows.
    for i, row in enumerate(inverse_rows):
        composed = {}
        for j, c in row.items():
            for k, value in rows[j].items():
                composed[k] = composed.get(k, 0)+c*value
        assert {k: value for k, value in composed.items() if value} == {i: 1}
    # Endpoint coefficients are at most two, but a future-point withdrawal
    # can transiently put coefficient three on a nonpivot triple{4,5,6}.
    assert backward['maximum_coefficient'] <= 3
    assert max(abs(c) for row in inverse_rows for c in row.values()) <= 2
    return dict(h=h, volume=v, status='PASS COMPLETE SCALAR PREFIX',
        forward=forward, inverse=backward, added_fractional_bits=0,
        operation_counts=counts(h), elapsed_seconds=perf_counter()-started,
        scope='Exact finite coefficient bounds and all scalar multiplication temporaries; native phase children, routing, complete fixed-tape buffers and exponent remain open.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a fresh attempt path')
    cases = (4, 8) if args.small else (16, 32, 48, 64)
    started = perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        result = list(pool.map(probe, cases))
    encoded = json.dumps(dict(status='PASS', worker_processes=args.workers, cases=result,
        elapsed_seconds=perf_counter()-started,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()), indent=2, default=str)+'\n'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
