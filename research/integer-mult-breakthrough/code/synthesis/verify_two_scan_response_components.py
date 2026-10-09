#!/usr/bin/env python3
"""Bounded response capacity, complete dirty word and separator controls."""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random

import two_scan_response_span_probe as P
import two_scan_response_four_entry_obstruction as F


def events(groups, n):
    return tuple((target, source, matrix, sign)
                 for unused, diagonal, B, A in groups
                 for target, source, matrix, sign in ((2*n, 0, A, 1),
                     (n, 2*n, B, 1), (2*n, 0, A, -1), (n, 2*n, B, -1)))


def complete_prefix_bill(word, n, invert=False):
    rows = [[Q(i == j) for j in range(3*n)] for i in range(3*n)]
    maximum, grid = Q(1), 0
    for target, source, matrix, sign in reversed(word) if invert else word:
        sign = -sign if invert else sign
        before = [row[:] for row in rows[source:source+n]]
        for i, coefficients in enumerate(matrix):
            rows[target+i] = [value+sign*sum(c*row[j] for c, row in zip(coefficients, before))
                              for j, value in enumerate(rows[target+i])]
        maximum = max(maximum, max(sum(abs(x) for x in row) for row in rows))
        for row in rows:
            for x in row:
                if x.denominator & (x.denominator-1):
                    raise AssertionError('A complete response endpoint prefix leaves the dyadic grid')
                grid = max(grid, x.denominator.bit_length()-1)
    return rows, {'maximum_complete_shear_endpoint_row_L1': [maximum.numerator, maximum.denominator],
                  'maximum_complete_shear_endpoint_fractional_bits': grid,
                  'native_intra_scan_prefixes_buffers_routing_and_metadata_not_included': True}


def probe():
    rows = [P.probe(f) for f in (2, 3, 4, 5)]
    if any(rows[i]['rational_status'] != 'EXACT COMPLETE RATIONAL RESPONSE SUM'
           or not rows[i]['dyadic_coefficients_in_this_witness'] for i in (0, 1)):
        raise AssertionError('A retained small dyadic response identity failed')
    if any(row['finite_capacity'][0]['target_in_field_span'] for row in rows[2:]):
        raise AssertionError('An excluded response capacity unexpectedly has a field solution')
    n = 8
    entries = P.generators(3)
    named, columns = zip(*entries)
    target = P.S.zeta(3)
    coefficients = P.rational_witness(columns, tuple(x for row in target for x in row))
    groups = P.response_groups(3, named, coefficients)
    word = events(groups, n)
    actual, guard = complete_prefix_bill(word, n)
    expected = [[Q(i == j) + (Q(target[i-n][j]) if n <= i < 2*n and j < n else 0)
                 for j in range(3*n)] for i in range(3*n)]
    if actual != expected:
        raise AssertionError('The full response word does not preserve every dirty/source/sink column')
    reverse, inverse_guard = complete_prefix_bill(word, n, True)
    expected_reverse = [[Q(i == j) - (Q(target[i-n][j]) if n <= i < 2*n and j < n else 0)
                         for j in range(3*n)] for i in range(3*n)]
    if reverse != expected_reverse:
        raise AssertionError('The inverse response word changes an endpoint column')
    bad, unused = complete_prefix_bill(word[:-1], n)
    if bad == expected:
        raise AssertionError('Omitting the final dirty-response debit passed the full column replay')
    rng = random.Random(202610091111)
    fields = 0
    for grid in (0, 3, 9):
        parts = [[Q(rng.randrange(-31, 32), 1 << grid) for unused in range(3*n)]
                 for unused in range(2)]
        for part in parts:
            x, y, dirty = tuple(part[:n]), tuple(part[n:2*n]), tuple(part[2*n:])
            result = P.literal_commutator(groups, x, y, dirty)
            expected_field = (x, tuple(a+b for a, b in zip(y, P.operator_times(target, x))), dirty)
            if result != expected_field or P.literal_commutator(groups, *result, invert=True) != (x, y, dirty):
                raise AssertionError('A complete Gaussian response field or inverse failed')
        fields += 1
    separator = [F.probe(f) for f in (4, 5)]
    small = F.small_width_escape()
    return {'status': 'PASS SINGULAR RESPONSE AND SEPARATOR BOUNDED CONTROLS',
            'exact_dyadic_widths': [2, 3], 'excluded_capacity_widths': [4, 5],
            'complete_dirty_source_sink_operator_columns': 3*n,
            'complete_Gaussian_fields': fields, 'field_seed': 202610091111,
            'small_positive_response_groups': len(groups), 'abstract_additive_scan_shears': len(word),
            'forward_shear_endpoint_bill': guard, 'inverse_shear_endpoint_bill': inverse_guard,
            'missing_final_dirty_debit_rejected': True,
            'exact_separator_generator_checks': sum(r['all_complete_generator_coefficients_checked'] for r in separator),
            'threshold_control': small, 'written_all_size_proof_not_formal': True,
            'no_native_or_multiplier_exponent_claim': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('A fresh optional output file is required')
    sources = [Path(module.__file__).resolve() for module in (P, F, P.S, P.S.R)]
    sources.append(Path(__file__).resolve())
    hashes = {str(path.relative_to(Path(__file__).resolve().parents[2])):
              sha256(path.read_bytes()).hexdigest() for path in sources}
    started = datetime.now(timezone.utc).isoformat()
    receipt = probe()
    if hashes != {str(path.relative_to(Path(__file__).resolve().parents[2])):
                  sha256(path.read_bytes()).hexdigest() for path in sources}:
        raise AssertionError('The effective source closure changed')
    receipt.update(started_utc=started, standard_library_only=True, source_closure=hashes)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({key: receipt[key] for key in ('status', 'small_positive_response_groups',
                                                   'abstract_additive_scan_shears')}, sort_keys=True))


if __name__ == '__main__':
    main()
