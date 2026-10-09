#!/usr/bin/env python3
"""Complete finite controls for geometric-width nonunit endpoint guards.

The literal two-bank word has Z_e endpoints, positive and negative width
dependent scales and dyadic shears. All children strictly halve width.
It is a numerical/precision discriminator, not a faster Z supplier. Array
indexing is reference arithmetic; no native routing or activity codec is
asserted by it.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time


def clone(state):
    return [[tuple(z) for z in bank] for bank in state]


def flatten(state):
    return [component for bank in state for z in bank for component in z]


def squared_norm(state):
    return sum(component*component for component in flatten(state))


def difference(a, b):
    return [[tuple(x-y for x, y in zip(p, q)) for p, q in zip(u, v)]
            for u, v in zip(a, b)]


def digest(state):
    return sha256(json.dumps(state, separators=(',', ':')).encode()).hexdigest()


def round_divide(value, exponent):
    denominator = 1 << exponent
    quotient, remainder = divmod(abs(value), denominator)
    if 2*remainder > denominator or (2*remainder == denominator and quotient % 2):
        quotient += 1
    return quotient if value >= 0 else -quotient


def partitions(axes):
    q, r = divmod(len(axes), 3)
    sizes = [q+int(j < r) for j in range(3)]
    parts = []
    offset = 0
    for size in sizes:
        if size:
            parts.append(axes[offset:offset+size])
        offset += size
    if len(axes) > 1 and any(2*len(part) > len(axes) for part in parts):
        raise AssertionError('Every retained child must have at most half parent width')
    return parts


def word(axes, inverse=False):
    e = len(axes)
    if not e:
        return []
    if e == 1:
        return [('zeta', axes[0], -1 if inverse else 1)]
    gates = [('scale', 0, e), ('scale', 1, -e),
             ('shear', 0, 1, -e, 1), ('shear', 1, 0, 0, 1)]
    children = partitions(axes)
    if inverse:
        children = list(reversed(children))
    for child in children:
        gates.extend(word(child, inverse))
    gates.extend([('shear', 1, 0, 0, -1), ('shear', 0, 1, -e, -1),
                  ('scale', 1, e), ('scale', 0, -e)])
    return gates


def internal_nodes(axes):
    return 0 if len(axes) <= 1 else 1+sum(internal_nodes(p) for p in partitions(axes))


def apply_fixed(state, gates, rounded=False):
    state = clone(state)
    metrics = dict(max_numerator_bits=0, rounding_writes=0, nonzero_injections=0)
    for gate in gates:
        kind = gate[0]
        if kind == 'zeta':
            _, bit, sign = gate
            for bank in state:
                for target in range(len(bank)):
                    if target & (1 << bit):
                        bank[target] = tuple(x+sign*y for x, y in
                                             zip(bank[target], bank[target ^ (1 << bit)]))
        elif kind == 'scale':
            _, bank, exponent = gate
            for i, z in enumerate(state[bank]):
                values = []
                for value in z:
                    if exponent >= 0:
                        values.append(value << exponent)
                    else:
                        if not rounded and value % (1 << -exponent):
                            raise ValueError('The reserved exact common grid is insufficient')
                        result = round_divide(value, -exponent) if rounded else value >> -exponent
                        values.append(result)
                        if rounded:
                            metrics['rounding_writes'] += 1
                            metrics['nonzero_injections'] += int((result << -exponent) != value)
                state[bank][i] = tuple(values)
        elif kind == 'shear':
            _, target, source, exponent, sign = gate
            for i, z in enumerate(state[source]):
                values = []
                for a, b in zip(state[target][i], z):
                    if exponent >= 0:
                        term = b << exponent
                    else:
                        if not rounded and b % (1 << -exponent):
                            raise ValueError('The reserved exact common grid is insufficient')
                        term = round_divide(b, -exponent) if rounded else b >> -exponent
                        if rounded:
                            metrics['rounding_writes'] += 1
                            metrics['nonzero_injections'] += int((term << -exponent) != b)
                    values.append(a+sign*term)
                state[target][i] = tuple(values)
        else:
            raise AssertionError('Every literal gate kind must be known')
        metrics['max_numerator_bits'] = max(metrics['max_numerator_bits'],
                                            max(abs(x).bit_length() for x in flatten(state)))
    return state, metrics


def trailing_zeros(value):
    return (abs(value) & -abs(value)).bit_length()-1


def apply_reference(state, grid, gates):
    """Minimal-grid exact instrumentation; no physical regridding is claimed."""
    state = clone(state)
    initial_grid = grid
    max_minimal = grid
    max_unreduced = grid
    for gate in gates:
        if gate[0] == 'zeta':
            state, _ = apply_fixed(state, [gate])
        elif gate[0] == 'scale':
            _, bank, exponent = gate
            if exponent >= 0:
                state[bank] = [tuple(x << exponent for x in z) for z in state[bank]]
            else:
                amount = -exponent
                state[1-bank] = [tuple(x << amount for x in z) for z in state[1-bank]]
                grid += amount
        else:
            _, target, source, exponent, sign = gate
            if exponent >= 0:
                state[target] = [tuple(a+sign*(b << exponent) for a, b in zip(x, y))
                                 for x, y in zip(state[target], state[source])]
            else:
                amount = -exponent
                prior_source = state[source]
                state = [[tuple(x << amount for x in z) for z in bank] for bank in state]
                state[target] = [tuple(a+sign*b for a, b in zip(x, y))
                                 for x, y in zip(state[target], prior_source)]
                grid += amount
        max_unreduced = max(max_unreduced, grid)
        values = [x for x in flatten(state) if x]
        amount = min(grid, min(trailing_zeros(x) for x in values)) if values else grid
        if amount:
            state = [[tuple(x >> amount for x in z) for z in bank] for bank in state]
            grid -= amount
        max_minimal = max(max_minimal, grid)
    return state, grid, dict(max_minimal_grid_excess=max_minimal-initial_grid,
                             max_unreduced_temporary_excess=max_unreduced-initial_grid,
                             minimal_grid_reduction='Mathematical reference only; actual exact replay uses a fixed global grid')


def direct_zeta(state, e, inverse=False):
    gates = [('zeta', bit, -1 if inverse else 1) for bit in range(e)]
    return apply_fixed(state, gates)[0]


def ceil_log2(value):
    return (value-1).bit_length() if value > 0 else 0


def probe(task):
    e, target_precision, seed, magnitude_bits = task
    rng = Random(seed)
    D = 1 << e
    axes = tuple(range(e))
    forward, inverse = word(axes), word(axes, True)
    nodes = internal_nodes(axes)
    N = 8*D*nodes
    gamma_bits = 18*e
    q = target_precision+ceil_log2(N)+gamma_bits+e+4
    exact_grid = q+4*e
    signed_guard = exact_grid+magnitude_bits+ceil_log2(4*D)//2+gamma_bits+6
    fields = []
    for field in range(4):
        inputs = [[tuple(rng.randrange(-(1 << (q+magnitude_bits)),
                                       1 << (q+magnitude_bits)) | 1 for _ in range(2))
                   for _ in range(D)] for _ in range(2)]
        target = direct_zeta(inputs, e)
        ref, ref_grid, reference_metrics = apply_reference(inputs, q, forward)
        ref_aligned = [[tuple(x << (q-ref_grid) for x in z) for z in bank] for bank in ref]
        if ref_grid > q or ref_aligned != target:
            raise AssertionError('Every complete exact endpoint must be the declared Z_e on both dirty banks')
        if reference_metrics['max_unreduced_temporary_excess'] > 4*e:
            raise AssertionError('Every literal exact temporary grid must meet the geometric reserve')
        fixed_input = [[tuple(x << (exact_grid-q) for x in z) for z in bank] for bank in inputs]
        fixed, fixed_metrics = apply_fixed(fixed_input, forward)
        wanted_fixed = [[tuple(x << (exact_grid-q) for x in z) for z in bank] for bank in target]
        if fixed != wanted_fixed or apply_fixed(fixed, inverse)[0] != fixed_input:
            raise AssertionError('The actual fixed-grid exact word and its true inverse must preserve all fields')
        rounded, metrics = apply_fixed(inputs, forward, True)
        undo, undo_metrics = apply_fixed(rounded, inverse, True)
        if metrics['rounding_writes'] != N or undo_metrics['rounding_writes'] != N:
            raise AssertionError('Every real rounding injection must be charged')
        forward_bound = N << gamma_bits
        undo_bound = N*((1 << e)+1) << gamma_bits
        if squared_norm(difference(rounded, target)) > forward_bound*forward_bound:
            raise AssertionError('The complete forward error must meet the typed depth bound')
        if squared_norm(difference(undo, inputs)) > undo_bound*undo_bound:
            raise AssertionError('The completed inverse Z_e must amplify prior forward error explicitly')
        if undo_bound > (1 << (q-target_precision)):
            raise AssertionError('The actual selected numerical reserve must cover forward and undo')
        if max(metrics['max_numerator_bits'], undo_metrics['max_numerator_bits'],
               fixed_metrics['max_numerator_bits']) >= signed_guard:
            raise AssertionError('All stored numerator guards must be sufficient')
        if not metrics['nonzero_injections'] or not undo_metrics['nonzero_injections']:
            raise AssertionError('Admitted fractional dirty fields must exercise genuine rounding')
        fields.append(dict(field=field, input_sha256=digest(inputs), exact_endpoint_sha256=digest(target),
                           rounded_endpoint_sha256=digest(rounded), rounded_undo_sha256=digest(undo),
                           forward_error_squared=squared_norm(difference(rounded, target)),
                           undo_error_squared=squared_norm(difference(undo, inputs)),
                           reference=reference_metrics, fixed_grid=fixed_metrics,
                           rounding=metrics, inverse_rounding=undo_metrics))
    basis_columns = 0
    if e == 3:
        for bank in range(2):
            for address in range(D):
                basis = [[(0, 0) for _ in range(D)] for _ in range(2)]
                basis[bank][address] = (1 << (4*e), 0)
                if apply_fixed(basis, forward)[0] != direct_zeta(basis, e):
                    raise AssertionError('Every tiny physical bank column must bind the endpoint')
                basis_columns += 1
    ones = [[(1, 0) for _ in range(D)] for _ in range(2)]
    if squared_norm(direct_zeta(ones, e)) <= squared_norm(ones):
        raise AssertionError('Z_e must reject a false unitary endpoint premise')
    insufficient = [[(1 << (e-1), 0) for _ in range(D)] for _ in range(2)]
    try:
        apply_fixed(insufficient, forward)
    except ValueError:
        pass
    else:
        raise AssertionError('An omitted width-dependent exact grid reserve must fail')
    return dict(selected_width=e, target_precision=target_precision, seed=seed,
                address_records=D, internal_nodes=nodes, literal_gates=len(forward),
                rounding_writes_per_direction=N, gamma_bits=gamma_bits,
                numerical_grid=q, exact_fixed_grid=exact_grid, signed_guard=signed_guard,
                complete_gaussian_dirty_fields=4, complete_tiny_bank_columns=basis_columns,
                fields=fields, false_unitary_control_rejected=True,
                insufficient_grid_control_rejected=True,
                scope='Exact and rounded full-bank Z reference word with geometric children; '
                      'no activity compaction, native layout, time improvement or new exponent.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('At least one actual worker is required')
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh path for each immutable attempt')
    topic = Path(__file__).resolve().parents[2]
    cfg = topic/'configs/transfers/geometric-endpoint-guards.json'
    config = json.loads(cfg.read_text())
    tasks = [(case['selected_width'],case['target_precision'],config['seed']+i,config['magnitude_bits'])
             for i,case in enumerate(config['cases'])]
    if args.small:
        tasks = tasks[:1]
    started = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    if args.workers == 1:
        results = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(probe,tasks))
    data = dict(status='PASS',actual_start_utc=started,elapsed_seconds=time.monotonic()-start,
                workers=args.workers,cases=results,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                config_sha256=sha256(cfg.read_bytes()).hexdigest())
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(status=data['status'],actual_start_utc=started,
                         elapsed_seconds=data['elapsed_seconds'],workers=args.workers,cases=len(results))))


if __name__ == '__main__':
    main()
