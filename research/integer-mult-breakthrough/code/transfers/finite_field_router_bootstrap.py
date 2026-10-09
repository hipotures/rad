#!/usr/bin/env python3
"""F5 Clifford address router and a scoped coordinate-only bootstrap floor.

i maps to 2 and dyadic denominators remain invertible. Literal phase words
transport complete F5 payloads and Boolean bits exactly. No native supplier
ABI, Gaussian reconstruction or unpaid frame router is inferred. A separate
single-bank coordinate-C/unit-diagonal model exposes naive wrapper costs.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time


def require(condition, message):
    if not condition:
        raise ValueError(message)


def c_axis(rows, bit, inverse=False):
    output = [row[:] for row in rows]
    a, b = (2, 4) if inverse else (4, 2)
    for address in range(len(rows)):
        if address >> bit & 1:
            continue
        partner = address | (1 << bit)
        output[address] = [(a * x + b * y) % 5 for x, y in zip(rows[address], rows[partner])]
        output[partner] = [(b * x + a * y) % 5 for x, y in zip(rows[address], rows[partner])]
    return output


def c_target(rows, width, inverse=False):
    for bit in range(width):
        rows = c_axis(rows, bit, inverse)
    return rows


def mask(control, width):
    # A nonlinear immutable-control mask, with no target/guard reads.
    return (control ^ ((control & 1) * (control >> 1))) & ((1 << width) - 1)


def route(rows, width, reverse=False, omit=None):
    # Chronological Htilde^-1, D_G, Htilde; true inverse reverses and
    # inverts every literal scalar/C gate. D_G is its own inverse.
    events = [('S', True), ('C', True), ('S', True), ('D', False),
              ('S', False), ('C', False), ('S', False)]
    if reverse:
        events = [(kind, not inverse) for kind, inverse in reversed(events)]
    rows = [row[:] for row in rows]
    target_mask = (1 << width) - 1
    for index, (kind, inverse) in enumerate(events):
        if index == omit:
            continue
        if kind == 'C':
            rows = c_target(rows, width, inverse)
            continue
        output = []
        for address, values in enumerate(rows):
            target = address & target_mask
            if kind == 'S':
                exponent = target.bit_count()
                multiplier = pow(3 if inverse else 2, exponent, 5)
            else:
                control = address >> width & target_mask
                multiplier = 4 if (target & mask(control, width)).bit_count() & 1 else 1
            output.append([(multiplier * x) % 5 for x in values])
        rows = output
    return rows


def router_case(width):
    # Two complete immutable guard bits and a complete restored companion
    # bit are retained. This tests an algebraic router, not native placement.
    size = 1 << (2 * width + 3)
    target_mask = (1 << width) - 1
    dense = [[(address * (2 * field + 1) + field) % 5 for field in range(4)]
             for address in range(size)]
    bits = [[(address >> (field % (2 * width + 3))) & 1 for field in range(4)]
            for address in range(size)]
    fields_checked = 0
    for rows in (dense, bits):
        expected = []
        for address in range(size):
            control = address >> width & target_mask
            expected.append(rows[address ^ mask(control, width)])
        actual = route(rows, width)
        require(actual == expected, 'F5 route failed an arbitrary complete payload field')
        require(route(actual, width, reverse=True) == rows, 'True scalar/C inverse failed')
        if rows is bits:
            require(all(x in (0, 1) for row in actual for x in row),
                    'Boolean payload reduction did not return Boolean endpoints')
        fields_checked += 2 * size * 4
    require(route(dense, width, omit=0) != route(dense, width),
            'Missing input chirp was falsely accepted')
    # Complete target/control blocks: every physical input column, without
    # pretending the unmaterialized zero off-block entries were computed.
    columns = entries = 0
    block_size = 1 << (2 * width)
    for control in range(1 << width):
        for source in range(1 << width):
            rows = [[0] for unused in range(block_size)]
            rows[(control << width) | source][0] = 1
            actual = route(rows, width)
            expected_address = (control << width) | (source ^ mask(control, width))
            require(all(value[0] == int(address == expected_address)
                        for address, value in enumerate(actual)),
                    'Complete literal F5 router column differs from the intended monomial')
            columns += 1
            entries += block_size
    return {'kind': 'literal F5 controlled address XOR', 'selected_target_width': width,
            'all_complete_records': size, 'four_F5_fields_forward_and_inverse': fields_checked,
            'literal_target_control_basis_columns': columns, 'literal_block_entries': entries,
            'Boolean_and_arbitrary_F5_endpoints_exact': True,
            'guard_and_companion_coordinates_fixed': True,
            'two_C_width_f_calls': 2, 'input_output_chirps_and_inverse_units_paid': True,
            'missing_chirp_negative_rejected': True,
            'scope': 'Exact F5 coefficient/address algebra. Array routing and field encoding are not a native tape implementation.'}


def coordinate_floor(weight):
    size = 1 << weight
    entries = 0
    for source in range(size):
        rows = [[int(address == source)] for address in range(size)]
        # Each coordinate appears once. Every intervening diagonal is a
        # Gaussian unit reduced modulo5 and every path is unique.
        for bit in range(weight):
            rows = [[value[0] * pow(2, ((address * (2 * bit + 1)) ^
                    (address >> (bit % weight))) % 4, 5) % 5]
                    for address, value in enumerate(rows)]
            rows = c_axis(rows, bit)
        require(all(value[0] != 0 for value in rows),
                'One-pass coordinate word unexpectedly cancelled a unique nonzero path')
        # The actual mixed-line phase has only identity and all-bit-flip
        # entries. Both are nonzero after i->2 reduction.
        target = [4 * int(address == source) + 2 * int(address == (source ^ (size - 1)))
                  for address in range(size)]
        require(sum(value != 0 for value in target) == 2, 'Mixed-line phase support changed')
        require([value[0] for value in rows] != target, 'An unpaid mixed-line wrapper was accepted')
        entries += size
    return {'kind': 'single-bank coordinate-C/unit-diagonal floor', 'mixed_line_weight': weight,
            'one_pass_full_support': size, 'required_mixed_line_support': 2,
            'all_basis_columns': size, 'literal_entries': entries,
            'proved_minimum_sum_coordinate_child_ranks': weight + 1,
            'proof_requires_invertible_diagonals_and_no_noncoordinate_permutation': True,
            'helpers_bank_interference_and_general_native_routers_outside_scope': True}


def master_case(pair_count):
    h, v, q = 2 * pair_count, 32 * comb(pair_count, 5), 2 * pair_count * (pair_count - 1) + 1
    original_deficit = 2 * v - 3 * q * h
    # Replacing only the one-rank helper source-line adapter by coordinate
    # C children adds >=5 ranks per source/core under the stated model.
    changed_deficit = original_deficit - 15 * v
    require(changed_deficit < 0, 'Naive coordinate-only F5 bootstrap gained first-moment slack')
    return {'kind': 'conditional fixed-stock wrapper bootstrap ledger', 'pair_count': pair_count,
            'h': h, 'sources': v, 'all_dirty_roots_including_total': q,
            'old_center_deficit': original_deficit,
            'minimum_added_rank_from_line_adapters_only': 15 * v,
            'resulting_deficit_upper': changed_deficit,
            'proper_child_first_moment_cannot_contract': True,
            'scope': 'Same stock/three-core master, one scalar bank per adapter, coordinate C children and unit diagonals only. Other coupled architectures remain open.'}


def run(task):
    kind, value = task
    return router_case(value) if kind == 'router' else (
        coordinate_floor(value) if kind == 'floor' else master_case(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    require(args.workers > 0, 'At least one worker is required')
    source_path = Path(__file__).resolve()
    frozen = source_path.read_bytes()
    start, clock = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    tasks = [('router', 2), ('floor', 5), ('master', 12)] if args.bounded else (
        [('router', f) for f in (1, 2, 3, 4)] + [('floor', k) for k in (3, 5, 7)] + [('master', 12)])
    if args.workers == 1:
        rows = [run(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
            rows = list(pool.map(run, tasks))
    require(source_path.read_bytes() == frozen, 'Immutable source changed during the experiment')
    result = {'status': 'PASS exact F5 router and scoped coordinate-bootstrap discriminator',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - clock, 'workers': args.workers,
              'source_sha256': sha256(frozen).hexdigest(),
              'coefficient_homomorphism': {'Gaussian_i': 2, 'one_half': 3, 'prime': 5,
                  'C': [[4, 2], [2, 4]], 'C_inverse': [[2, 4], [4, 2]],
                  'nonfaithfulness_witness_2_minus_i_maps_to': 0,
                  'Gaussian_reconstruction_not_claimed': True},
              'cases': rows,
              'scope': 'Exact coefficient/address algebra and one restricted coupled-rank obstruction. No native supplier, arbitrary-width atom, Gaussian reconstruction or kappa.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds']}), flush=True)


if __name__ == '__main__':
    main()
