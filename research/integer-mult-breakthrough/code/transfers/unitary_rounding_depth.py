#!/usr/bin/env python3
"""Literal fixed-grid rounding under decreasing unitary-endpoint recursion.

The recursive words are numerical discriminators, not proposed fast bulk
suppliers. Exact dyadic reference reduction is mathematical instrumentation,
not a free physical normalization. All scalar rounding and discarded padded
bank residue are counted. Both original dirty banks have exact unitary
endpoints; nonlinear examples define a different explicit unitary family.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time

TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC / 'configs/transfers/unitary-rounding-depth.json'


def plus(a, b):
    return a[0]+b[0], a[1]+b[1]


def times(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def invert_word(word):
    result = []
    for gate in reversed(word):
        if gate[0] == 'shear':
            result.append(('shear', gate[1], gate[2], -gate[3]))
        elif gate[0] == 'C':
            result.append(('C', gate[1], not gate[2]))
        else:
            result.append(gate)
    return result


def word(width, family):
    if not width:
        return []
    child = word(width-1, family)
    # The two fixed dyadic bank shears commute with every complete
    # address operator applied identically to both banks.
    result = [('shear', 0, 1, 1), ('shear', 1, 0, 1)] + child
    if family == 'nonlinear_conjugate':
        if width == 2:
            result += [('route', (0,), 1)]
        elif width >= 3:
            result += [('route', (width-3, width-2), width-1)]
        result += invert_word(child)
    result += [('C', width-1, False), ('shear', 1, 0, -1),
               ('shear', 0, 1, -1)]
    return result


def rounded_half(n):
    quotient, remainder = divmod(n, 2)
    return quotient + int(bool(remainder) and bool(quotient & 1))


def trailing_zeros(n):
    n = abs(n)
    return (n & -n).bit_length()-1


def reduced_reference(values, grid):
    nonzero = [part for bank in values for pair in bank for part in pair if part]
    if not nonzero:
        return values, 0
    count = min(grid, min(map(trailing_zeros, nonzero)))
    if count:
        values = [[(a >> count, b >> count) for a, b in bank]
                  for bank in values]
    return values, grid-count


def apply(values, grid, gates, fixed=False, early_projection=False):
    values = [list(bank) for bank in values]
    maximum_grid = grid
    maximum_signed_numerator = max(
        [abs(part).bit_length()+1 for bank in values for pair in bank for part in pair]+[1])
    injections = 0
    size = len(values[0])
    for index, gate in enumerate(gates):
        if gate[0] == 'shear':
            _, target, source, sign = gate
            if fixed:
                values[target] = [tuple(rounded_half(2*a+sign*b)
                                        for a, b in zip(left, right))
                                  for left, right in zip(values[target], values[source])]
                injections += 2*size
            else:
                updated = [tuple(2*a+sign*b for a, b in zip(left, right))
                           for left, right in zip(values[target], values[source])]
                values = [[(2*a, 2*b) for a, b in bank] for bank in values]
                values[target] = updated
                grid += 1
        elif gate[0] == 'route':
            _, controls, target = gate
            control_mask = sum(1 << bit for bit in controls)
            permutation = [x ^ ((1 << target) if x & control_mask == control_mask else 0)
                           for x in range(size)]
            if len(set(permutation)) != size:
                raise AssertionError('Controlled route is not a complete permutation')
            values = [[bank[x] for x in permutation] for bank in values]
        else:
            _, bit, inverse = gate
            step = 1 << bit
            alpha = (1, -1) if inverse else (1, 1)
            beta = (1, 1) if inverse else (1, -1)
            result = [list(bank) for bank in values]
            for bank in range(2):
                for low in range(size):
                    if low & step:
                        continue
                    high = low | step
                    a, b = values[bank][low], values[bank][high]
                    lower = plus(times(alpha, a), times(beta, b))
                    upper = plus(times(beta, a), times(alpha, b))
                    if fixed:
                        lower = tuple(map(rounded_half, lower))
                        upper = tuple(map(rounded_half, upper))
                    result[bank][low], result[bank][high] = lower, upper
            values = result
            if fixed:
                injections += 4*size
            else:
                grid += 1
        if early_projection and index == 1:
            values[0] = [(0, 0)]*size
        if not fixed:
            values, grid = reduced_reference(values, grid)
        maximum_grid = max(maximum_grid, grid)
        maximum_signed_numerator = max(
            maximum_signed_numerator,
            max([abs(part).bit_length()+1 for bank in values for pair in bank for part in pair]+[1]))
    return values, grid, dict(injections=injections,
                             maximum_reference_common_grid=maximum_grid,
                             maximum_signed_numerator_bits=maximum_signed_numerator)


def aligned(values, grid, common):
    return [[(a << (common-grid), b << (common-grid)) for a, b in bank]
            for bank in values]


def exact_equal(left, g, right, h):
    common = max(g, h)
    return aligned(left, g, common) == aligned(right, h, common)


def squared_error(left, g, right, h):
    common = max(g, h)
    left, right = aligned(left, g, common), aligned(right, h, common)
    differences = [a-b for L, R in zip(left, right)
                   for x, y in zip(L, R) for a, b in zip(x, y)]
    return sum(x*x for x in differences), common, max(map(abs, differences), default=0)


def canonical(values, grid, width):
    size = 1 << width
    alpha = (1, 0)
    for _ in range(width):
        alpha = times(alpha, (1, 1))
    phases = ((1, 0), (0, -1), (-1, 0), (0, 1))
    matrix = [[times(alpha, phases[(x ^ y).bit_count() % 4])
               for y in range(size)] for x in range(size)]
    result = [[tuple(sum(times(coefficient, value)[part]
                         for coefficient, value in zip(row, bank)) for part in (0, 1))
               for row in matrix] for bank in values]
    return reduced_reference(result, grid+width)


def matrix_certificate(gates, width, family):
    size = 1 << width
    columns = []
    zero = [(0, 0)]*size
    bare = [gate for gate in gates if gate[0] != 'shear']
    maximum_grid = 0
    for bank in range(2):
        for origin in range(size):
            data = [list(zero), list(zero)]
            data[bank][origin] = (1, 0)
            actual, grid, audit = apply(data, 0, gates)
            reference, other_grid, _ = apply(data, 0, bare)
            if not exact_equal(actual, grid, reference, other_grid):
                raise AssertionError('Bank shears do not cancel on a complete physical column')
            if any(a or b for a, b in actual[1-bank]):
                raise AssertionError('Completed endpoint leaves a correlated dirty response')
            if family == 'canonical':
                wanted, wanted_grid = canonical(data, 0, width)
                if not exact_equal(actual, grid, wanted, wanted_grid):
                    raise AssertionError('Canonical endpoint differs from direct C tensor')
            if bank == 0:
                columns.append((actual[0], grid))
            else:
                previous, old_grid = columns[origin]
                if not exact_equal([actual[1]], grid, [previous], old_grid):
                    raise AssertionError('Different dirty banks have different endpoint operators')
            maximum_grid = max(maximum_grid, audit['maximum_reference_common_grid'])
    common = max(grid for column, grid in columns)
    columns = [[(a << (common-grid), b << (common-grid)) for a, b in column]
               for column, grid in columns]
    for i in range(size):
        for j in range(size):
            scalar = (0, 0)
            for a, b in zip(columns[i], columns[j]):
                scalar = plus(scalar, times((a[0], -a[1]), b))
            if scalar != ((1 << (2*common), 0) if i == j else (0, 0)):
                raise AssertionError('Completed nonlinear endpoint is not exactly unitary')
    return dict(all_physical_bank_columns=2*size,
                all_Gaussian_Gram_entries=size*size,
                completed_endpoint_unitary=True,
                matrix_common_grid=common,
                largest_exact_reference_prefix_grid=maximum_grid,
                direct_C_target_verified=family == 'canonical')


def probe(task):
    width, family, target_precision, magnitude_bits = task
    started = time.monotonic()
    size = 1 << width
    gates = word(width, family)
    nodes = width if family == 'canonical' else (1 << width)-1
    injections = 12*size*nodes
    tail_factor = 1 << (4*width)
    bound = 2*injections*tail_factor
    # Target is absolute l2 precision. Input fields occupy this full grid,
    # so the controls exercise nonzero rounding even at large q.
    q = target_precision+(2*injections-1).bit_length()+4*width+4
    guard = q+magnitude_bits+(width+3)//2+4*width+4
    seed = 202610090614+width+target_precision+int(family == 'canonical')
    randoms = Random(seed)
    limit = 1 << (q+magnitude_bits-1)
    certificate = matrix_certificate(gates, width, family)
    rows = []
    for field in range(4):
        data = [[(randoms.randrange(-limit, limit), randoms.randrange(-limit, limit))
                 for _ in range(size)] for bank in range(2)]
        if field in (0, 2):
            data[0] = [(0, 0)]*size
        exact, grid, exact_audit = apply(data, q, gates)
        approximate, approximate_grid, fixed_audit = apply(data, q, gates, fixed=True)
        if approximate_grid != q or fixed_audit['injections'] != injections:
            raise AssertionError('Fixed grid or complete rounding count differs from the word')
        sq, common, maximum = squared_error(approximate, q, exact, grid)
        if sq > bound*bound*(1 << (2*(common-q))):
            raise AssertionError('Complete forward rounding error exceeds the prefix/tail bound')
        back, _, back_audit = apply(approximate, q, invert_word(gates), fixed=True)
        undo_sq, undo_grid, _ = squared_error(back, q, data, q)
        if undo_grid != q or undo_sq > bound*bound:
            raise AssertionError('Forward/undo rounded word exceeds the complete bound')
        if fixed_audit['maximum_signed_numerator_bits'] > guard or back_audit['maximum_signed_numerator_bits'] > guard:
            raise AssertionError('A fixed-grid numerator exceeds the paid magnitude guard')
        projection_sq = None
        if field in (0, 2):
            if any(a or b for a, b in exact[0]):
                raise AssertionError('Exact complete endpoint failed to return a padded bank to zero')
            projection_sq = sum(a*a+b*b for a, b in approximate[0])
            if projection_sq > bound*bound:
                raise AssertionError('Discarded padded-bank residue was not covered')
            projected = [list(approximate[0]), list(approximate[1])]
            projected[0] = [(0, 0)]*size
            projected_back, _, _ = apply(projected, q, invert_word(gates), fixed=True)
            projected_sq, _, _ = squared_error(projected_back, q, data, q)
            if projected_sq > bound*bound:
                raise AssertionError('Charged padded projection and undo exceed their error bound')
        rows.append(dict(field=field,first_bank_initial_zero=field in (0, 2),
                         exact_final_reference_grid=grid,
                         largest_exact_prefix_reference_grid=exact_audit['maximum_reference_common_grid'],
                         exact_grid_excess_above_fixed_q=exact_audit['maximum_reference_common_grid']-q,
                         l2_squared_error_numerator=str(sq),error_common_grid=common,
                         maximum_component_error_numerator=str(maximum),
                         undo_squared_error_grid_q_numerator=str(undo_sq),
                         discarded_zero_bank_squared_norm_grid_q_numerator=None if projection_sq is None else str(projection_sq),
                         fixed_grid_signed_numerator_bits=fixed_audit['maximum_signed_numerator_bits'],
                         actual_rounding_injections=injections,
                         field_input_exact_approximate_sha256=sha256(json.dumps([data, exact, grid, approximate]).encode()).hexdigest()))
    # Premature erasure occurs while the zero bank carries a real correlated
    # source response, before the complete endpoint has returned it to zero.
    data = [[(0, 0)]*size, [(int(x == 0), 0) for x in range(size)]]
    wanted, wanted_grid, _ = apply(data, 0, gates)
    broken, broken_grid, _ = apply(data, 0, gates, early_projection=True)
    if exact_equal([wanted[1]], wanted_grid, [broken[1]], broken_grid):
        raise AssertionError('Premature projection did not corrupt the retained dirty bank')
    return dict(status='PASS LITERAL UNITARY RECURSION ROUNDING DEPTH',width=width,
                family=family,coefficient_addresses=size,dirty_banks=2,Gaussian_fields=4,
                selected_target_precision=target_precision,fixed_fractional_grid=q,
                safe_complete_signed_numerator_bits=guard,input_magnitude_bits=magnitude_bits,
                scalar_injections_each_complete_forward=injections,
                inverse_injections_also_paid=injections,uniform_local_scalar_norm_upper=2,
                unresolved_scalar_gates_per_depth_upper=4,prefix_tail_norm_upper=str(tail_factor),
                forward_and_undo_l2_error_upper_units_of_grid_q=str(bound),
                premature_zero_bank_projection='REJECTED ON RETAINED BANK',matrix_certificate=certificate,
                seed=seed,fields=rows,seconds=time.monotonic()-started,
                no_native_time_or_orbit_layout=True,no_faster_supplier=True,new_exponent=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or (args.output and args.output.exists()):
        raise ValueError('Positive workers and fresh output required')
    config = json.loads(CONFIG.read_text())
    paths = (Path(__file__).resolve(), CONFIG)
    pins = {str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
                    source_config_sha256=pins,scope=config['scope'],stdlib_only=True)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    cases = config['cases'][:1] if args.small else config['cases']
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, cases))
    if any(sha256((TOPIC/p).read_bytes()).hexdigest() != value for p, value in pins.items()):
        raise AssertionError('Source/configuration changed during numerical controls')
    result = dict(status='PASS FIXED-GRID UNITARY ENDPOINT NUMERICAL CONTRACT',cases=rows,
                  seconds=time.monotonic()-started,scope=config['scope'],
                  approximate_numerical_contract_only=True,exact_outer_integer_recovery=False,
                  new_exponent=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','seconds','scope')}))


if __name__ == '__main__':
    main()
