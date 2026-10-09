#!/usr/bin/env python3
"""Exact F5 mixed-line phase and a paid smaller-parameter routing ledger.

The two complete C calls are literal endpoint oracles in this finite replay,
evaluated by coordinate factors. No fast/native C5 supplier is implemented.
The recurrence includes their selected widths and all fixed-stock rank fees.

Status at the 2026-10-09 stop request: authored exploratory source, never
executed. All finite runtime controls in this file remain pending. The
separate finite_field_router_bootstrap.py component was executed earlier.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

from finite_field_router_bootstrap import c_axis, require


def literal_word(rows, weight, columns, inverse=False, omit=None):
    # Chronological Htilde^-1, i^sum(parity_U), Htilde. Inverting the word
    # reverses every actual phase/C event. All address spectators stay fixed.
    events = [('S', True), ('C', True), ('S', True), ('D', False),
              ('S', False), ('C', False), ('S', False)]
    if inverse:
        events = [(kind, not flag) for kind, flag in reversed(events)]
    rows = [row[:] for row in rows]
    active_bits = weight * columns
    for index, (kind, flag) in enumerate(events):
        if index == omit:
            continue
        if kind == 'C':
            for bit in range(active_bits):
                rows = c_axis(rows, bit, inverse=flag)
        else:
            updated = []
            for address, values in enumerate(rows):
                if kind == 'S':
                    exponent = (address & ((1 << active_bits) - 1)).bit_count()
                else:
                    exponent = sum((sum((address >> (bit * columns + column)) & 1
                                        for bit in range(weight)) & 1)
                                   for column in range(columns))
                multiplier = pow(3 if flag else 2, exponent, 5)
                updated.append([(multiplier * value) % 5 for value in values])
            rows = updated
    return rows


def expected_line(rows, weight, columns, inverse=False):
    a, b = (2, 4) if inverse else (4, 2)
    for column in range(columns):
        direction = sum(1 << (bit * columns + column) for bit in range(weight))
        rows = [[(a * value + b * partner) % 5
                 for value, partner in zip(rows[address], rows[address ^ direction])]
                for address in range(len(rows))]
    return rows


def phase_case(task):
    weight, columns = task
    active = weight * columns
    size = 1 << (active + 2)
    fields = [[(address * (2 * field + 1) + field * field) % 5
               for field in range(4)] for address in range(size)]
    actual = literal_word(fields, weight, columns)
    expected = expected_line(fields, weight, columns)
    require(actual == expected, 'Two paid Fourier calls failed the actual mixed-line phase')
    require(literal_word(actual, weight, columns, inverse=True) == fields,
            'True inverse failed an arbitrary F5 dirty field or spectator')
    require(expected_line(actual, weight, columns, inverse=True) == fields,
            'Mixed-line endpoint inverse disagreed with literal gates')
    require(literal_word(fields, weight, columns, omit=0) != expected,
            'An omitted chirp was accepted')
    active_size = 1 << active
    sources = range(active_size) if columns == 1 else (0, 1, active_size // 3, active_size - 1)
    checked = 0
    for source in sources:
        rows = [[int(address == source)] for address in range(active_size)]
        require(literal_word(rows, weight, columns) == expected_line(rows, weight, columns),
                'Literal mixed-line input column failed')
        checked += 1
    return {'kind': 'literal modular mixed-line phase', 'line_weight': weight,
            'columns': columns, 'native_selected_width_each_call': weight * columns,
            'two_complete_C5_calls': 2, 'complete_dirty_records': size,
            'forward_inverse_four_F5_field_values': 2 * 4 * size,
            'physical_active_basis_columns_checked': checked,
            'all_active_columns_checked': columns == 1,
            'two_complete_spectator_bits_fixed': True, 'missing_chirp_negative_rejected': True,
            'scope': 'Exact complete finite endpoint; coordinate-factor oracle evaluation is not a faster or native supplier'}


def ledger(pair_count):
    h = 2 * pair_count
    v, q = 32 * comb(pair_count, 5), 2 * pair_count * (pair_count - 1) + 1
    original = 2 * v - 3 * q * h
    floor_delta = original - 3 * v * (6 - 1)
    fourier_delta = original - 3 * v * (2 * 5 - 1)
    # Explicit GL line routing uses four transvections each way. Every
    # transvection is two C5_f calls, plus the original one-rank C5_f child.
    explicit_transvections = 3 * v * 8
    gl_delta = original - 2 * explicit_transvections
    require(max(floor_delta, fourier_delta, gl_delta) < 0,
            'A separately rebuilt line adapter obtained free first-moment slack')
    return {'kind': 'fixed-stock smaller-parameter route ledger', 'pair_count': pair_count,
            'h': h, 'v': v, 'roots_including_independent_total': q, 'master_m': 3 * h,
            'original_copied_center_deficit': original,
            'two_C5_f_calls_per_GL_transvection': 2,
            'GL_child_parameter_ratio': f'1/{3 * h}',
            'necessary_total_transvection_condition': '2*g < original_deficit',
            'coordinate_only_rank_floor_resulting_deficit_upper': floor_delta,
            'explicit_two_C5_5f_phase_resulting_deficit': fourier_delta,
            'explicit_GL_line_transvections_all_three_cores': explicit_transvections,
            'explicit_GL_line_resulting_deficit': gl_delta,
            'Gaussian_reconstruction_not_claimed': True,
            'scope': 'Only separately rebuilt source-helper line adapters at unchanged stock/master. Joint words, new address families and changed suppliers remain open.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    require(args.workers > 0, 'At least one worker is required')
    source = Path(__file__).resolve()
    helper = source.with_name('finite_field_router_bootstrap.py')
    frozen = {path: path.read_bytes() for path in (source, helper)}
    tasks = [(3, 1), (5, 2)] if args.bounded else [(3, 1), (5, 1), (3, 2), (5, 2)]
    start, clock = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    if args.workers == 1:
        rows = [phase_case(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
            rows = list(pool.map(phase_case, tasks))
    ledger_rows = [ledger(p) for p in ((12,) if args.bounded else (9, 12))]
    require(all(path.read_bytes() == payload for path, payload in frozen.items()),
            'Source closure changed during the run')
    result = {'status': 'PASS literal F5 mixed-line phase and scoped paid routing recurrence',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - clock, 'workers': args.workers,
              'source_sha256': {path.name: sha256(payload).hexdigest() for path, payload in frozen.items()},
              'phase_cases': rows, 'ledger_cases': ledger_rows,
              'conditional_native_ABI': {'lane_field': 'F5 residues, 3 bits per lane',
                  'all_payload_lanes_arbitrary': True, 'global_record_bits_R_at_least_address_bits_A': True,
                  'volume': 'V=M*R', 'scalar_and_metadata_passes': 'O(V+M*A)=O(V) under R>=A',
                  'root_mf_and_child_f': 'Every GL child f has ratio1/m; each complete record is moved and charged',
                  'native_lane_setup_copy_rowstocks_and_child_supplier': 'Unprovided separate interfaces'},
              'scope': 'Exact modular component and analytical typed recurrence only. No native supplier, ordinary exponent, Gaussian reconstruction or kappa'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds']}), flush=True)


if __name__ == '__main__':
    main()
