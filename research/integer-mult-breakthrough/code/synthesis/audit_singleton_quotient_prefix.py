#!/usr/bin/env python3
"""Exact scalar prefix/stock audit for the singleton quotient component.

The matrices are virtual common-frame scalar coefficients. They do not
measure tape head travel or an unsupplied child implementation's prefix.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import singleton_quotient_copies as producer

PRODUCER_SHA256 = 'b1e3d9688d59a8c1cb78f31063520a3cff226242c8d7bba10d490d595c6e05b9'


def audit(k):
    spec = producer.schedule(k)
    count = spec['roles']
    identity = [[int(i == j) for j in range(count)] for i in range(count)]
    wanted = [row[:] for row in identity]
    for i, bucket in enumerate(spec['buckets']):
        for source in bucket[2]:
            wanted[spec['A'] + i][source] += 1
    maxima = {}
    for reverse in (False, True):
        rows = [row[:] for row in identity]
        peak = 1
        for event in reversed(spec['events']) if reverse else spec['events']:
            if event['kind'] in ('add', 'copy-read'):
                i, j = event['target'], event.get('source', event.get('root'))
                sign = event['sign'] * (-1 if reverse else 1)
                rows[i] = [a + sign * b for a, b in zip(rows[i], rows[j])]
            elif event['kind'] == 'negate':
                rows[event['role']] = [-a for a in rows[event['role']]]
            peak = max(peak, *(sum(abs(a) for a in row) for row in rows))
        expected = [[2 * identity[i][j] - wanted[i][j] for j in range(count)]
                    for i in range(count)] if reverse else wanted
        if rows != expected or peak != 2 * spec['n'] + 1:
            raise AssertionError('The complete endpoint or virtual scalar prefix changed')
        maxima['inverse' if reverse else 'forward'] = peak
    copied = [event for event in spec['events'] if event['kind'] == 'copy-read']
    if len(copied) != 4 * k or any(not event['complete_owned_copy'] for event in copied):
        raise AssertionError('An early/late complete read copy was omitted')
    if sum(event['late'] for event in copied) != 2 * k:
        raise AssertionError('The rank-one late copy stock is wrong')
    return {
        'k': k, 'h': spec['h'], 'sources': spec['n'],
        'persistent_roles': count, 'extra_persistent_quotient_roots': spec['q'],
        'complete_source_helpers': spec['n'], 'aggregate_roots': 2 * k,
        'forward_inverse_scalar_prefix_row_L1': maxima,
        'scalar_endpoint_matrix_entries_per_direction': count * count,
        'endpoint_scalar_grid_bits': 0,
        'complete_owned_reads': len(copied), 'late_rank_one_child_reads': 2 * k,
        'maximum_concurrent_owned_copy_buffers': 1,
        'paid_rank_above_actual_endpoint_baseline': 2 * k,
        'all_prefixes_are_integer_scalar_rows': True,
        'physical_unitary_wrapper_norm_argument_is_analytical': True,
        'native_copy_erase_and_child_internal_precision_remain_conditional': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise ValueError('Use a fresh output file')
    path = Path(producer.__file__)
    if sha256(path.read_bytes()).hexdigest() != PRODUCER_SHA256:
        raise AssertionError('The accepted quotient producer changed')
    started = datetime.now(timezone.utc).isoformat()
    result = {'status': 'PASS exact singleton quotient scalar-prefix and copy-stock audit',
              'started_utc': started, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'producer_sha256': PRODUCER_SHA256, 'cases': [audit(k) for k in (1, 3, 5)],
              'scope': 'Both full independent scalar matrices and every integer prefix; actual native motion, scratch erasure and child internal implementations remain conditional.'}
    result['completed_utc'] = datetime.now(timezone.utc).isoformat()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'cases'}, sort_keys=True))


if __name__ == '__main__':
    main()
