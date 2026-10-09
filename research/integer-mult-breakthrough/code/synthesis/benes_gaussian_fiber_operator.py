#!/usr/bin/env python3
"""Exact Gaussian G(c)^tensor-f binding to selected-only Benes fibers.

All inactive letters remain in complete fibers. The finite array oracle calls
the zeta child exactly and records its coefficient gauges; it does not supply
a faster native implementation of that recursive child or a shorter base word.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import time

TOPIC = Path(__file__).resolve().parents[2]
WORD = TOPIC / 'code/synthesis/benes_guarded_control_word_v3.py'
WORD_SHA = '33274fe5b21f67f06a9a4b198923c25a3f243bf6b8c459ddf4136cc02be9fe56'
if sha256(WORD.read_bytes()).hexdigest() != WORD_SHA:
    raise ValueError('The canonical literal word changed')
SPEC = importlib.util.spec_from_file_location('canonical_benes_v3', WORD)
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)
w = v.w
b = v.b
ZERO, ONE = (Q(0), Q(0)), (Q(1), Q(0))


def add(a, c):
    return a[0] + c[0], a[1] + c[1]


def neg(a):
    return -a[0], -a[1]


def mul(a, c):
    return a[0] * c[0] - a[1] * c[1], a[0] * c[1] + a[1] * c[0]


def inverse(a):
    norm = a[0] * a[0] + a[1] * a[1]
    if norm == 0:
        raise ValueError('A zero Gaussian gauge is not invertible')
    return a[0] / norm, -a[1] / norm


def powers(a, maximum):
    values = [ONE]
    for unused in range(maximum):
        values.append(mul(values[-1], a))
    return values


def serialize(a):
    return [[component.numerator, component.denominator] for component in a]


def guarded_coefficient_grid(values):
    exponent = 0
    maximum = Q(0)
    for value in values:
        maximum = max(maximum, abs(value[0]) + abs(value[1]))
        for component in value:
            denominator = component.denominator
            if denominator & (denominator - 1):
                raise AssertionError('An exact coefficient escaped the common dyadic grid')
            exponent = max(exponent, denominator.bit_length() - 1)
    return dict(common_denominator_bits=exponent,
                maximum_component_l1=[maximum.numerator, maximum.denominator])


def subset_zeta(values, a):
    result = list(values)
    for axis in range(a):
        bit = 1 << axis
        for source in range(len(result)):
            if not source & bit:
                result[source | bit] = add(result[source | bit], result[source])
    return result


def weighted_child(values, a, c, omit_input_gauge=False):
    """Actual diagonal(c^weight) Z_a diagonal(c^-weight), high axes fixed."""
    positive = powers(c, a)
    negative = powers(inverse(c), a)
    low = (1 << a) - 1
    pre = [mul(value, ONE if omit_input_gauge else negative[(index & low).bit_count()])
           for index, value in enumerate(values)]
    child = subset_zeta(pre, a)
    result = [mul(value, positive[(index & low).bit_count()]) for index, value in enumerate(child)]
    return result, dict(input_gauge=guarded_coefficient_grid(pre),
                        exact_zeta_child=guarded_coefficient_grid(child),
                        output_gauge=guarded_coefficient_grid(result))


def physical_fiber_route(f, K, y, z, pattern, spectator):
    forward = []
    for x in range(1 << f):
        original = w.canonical_embed((x, y, z), f, K, spectator)
        after = v.compact_address(original, f, K, pattern=pattern, literal=False)
        if after != v.reference_compact(original, f, K, pattern):
            raise AssertionError('The canonical physical compaction binding failed')
        forward.append(w.selected_canonical(after, f, K, 0))
        if v.compact_address(after, f, K, inverse=True, pattern=pattern, literal=False) != original:
            raise AssertionError('The physical fiber inverse changed a complete record address')
    if sorted(forward) != list(range(1 << f)):
        raise AssertionError('A complete action fiber was lost or duplicated')
    full = (1 << f) - 1
    active = (~((y ^ (full if pattern[0] else 0)) | (z ^ (full if pattern[1] else 0)))) & full
    a = active.bit_count()
    if b.permute_bits(active, b.stable_compaction(active, f)) != (1 << a) - 1:
        raise AssertionError('The child selected axes are not the canonical first a complete chunks')
    return active, a, forward


def apply_fiber(values, route, a, c, omit_input_gauge=False):
    placed = [None] * len(values)
    for source, target in enumerate(route):
        placed[target] = values[source]
    child, grids = weighted_child(placed, a, c, omit_input_gauge)
    # Pulling back by the same forward route is the literal inverse permutation.
    return [child[route[source]] for source in range(len(values))], grids


def direct_gate(values, f, active, c):
    result = list(values)
    for axis in range(f):
        bit = 1 << axis
        if active & bit:
            for source in range(1 << f):
                if not source & bit:
                    result[source | bit] = add(result[source | bit], mul(c, result[source]))
    return result


def coefficient_probe(task):
    f, K, coefficient_data, seed = task
    started = time.monotonic()
    c = tuple(Q(numerator, denominator) for numerator, denominator in coefficient_data)
    inverse(c)
    rng = random.Random(seed)
    c_power = powers(c, f)
    n = (3 * f + 12) * K
    cases, checked_entries, field_values, gauge_witness = 0, 0, 0, None
    histogram = {}
    gauges = dict(common_denominator_bits=0, maximum_component_l1=[0, 1])
    fixtures = []
    for pattern in ((0, 0), (0, 1), (1, 0), (1, 1)):
        for y in range(1 << f):
            for z in range(1 << f):
                plane = rng.getrandbits(n - 3 * f)
                active, a, route = physical_fiber_route(f, K, y, z, pattern, plane)
                histogram[a] = histogram.get(a, 0) + 1
                low = (1 << a) - 1
                for source in range(1 << f):
                    child_source = route[source]
                    for target in range(1 << f):
                        child_target = route[target]
                        allowed = ((child_source >> a) == (child_target >> a)
                                   and not ((child_source & low) & ~(child_target & low)))
                        actual = c_power[(child_target & low).bit_count() - (child_source & low).bit_count()] if allowed else ZERO
                        expected_allowed = ((source & ~active) == (target & ~active)
                                            and not ((source & active) & ~(target & active)))
                        expected = c_power[(target & active).bit_count() - (source & active).bit_count()] if expected_allowed else ZERO
                        if actual != expected:
                            raise AssertionError('An actual composed Gaussian fiber coefficient failed')
                        checked_entries += 1
                fields = [[(Q(3 * index - 7, 8), Q(5 * index + y - z, 4)) for index in range(1 << f)],
                          [(Q(rng.randrange(-16, 17), 16), Q(rng.randrange(-16, 17), 8)) for unused in range(1 << f)]]
                for values in fields:
                    actual, current_grid = apply_fiber(values, route, a, c)
                    expected = direct_gate(values, f, active, c)
                    if actual != expected or apply_fiber(actual, route, a, neg(c))[0] != values:
                        raise AssertionError('An arbitrary dirty Gaussian field or true inverse failed')
                    for state in current_grid.values():
                        gauges['common_denominator_bits'] = max(gauges['common_denominator_bits'], state['common_denominator_bits'])
                        if Q(*state['maximum_component_l1']) > Q(*gauges['maximum_component_l1']):
                            gauges['maximum_component_l1'] = state['maximum_component_l1']
                    if c != ONE and gauge_witness is None:
                        wrong = apply_fiber(values, route, a, c, omit_input_gauge=True)[0]
                        if wrong != expected:
                            gauge_witness = dict(pattern=pattern, y=y, z=z, a=a,
                                                 first_difference=next(i for i in range(len(wrong)) if wrong[i] != expected[i]))
                    field_values += len(values)
                if pattern == (0, 0) and (y, z) in ((0, 0), (1, 2), (3, 4), ((1 << f) - 1, 0)):
                    fixtures.append(dict(pattern=pattern, y=y, z=z, complete_spectator_plane=plane,
                                         a=a, active=active, action_permutation=route))
                cases += 1
    expected_histogram = {a: 4 * __import__('math').comb(f, a) * 3 ** (f - a) for a in range(f + 1)}
    if histogram != expected_histogram:
        raise AssertionError('The complete inactive alphabet or exact activity volume was changed')
    if c != ONE and gauge_witness is None:
        raise AssertionError('Omitting a required nonunit/unit phase gauge did not fail')
    return dict(status='PASS EXACT GAUSSIAN BENES FIBERS', f=f, K=K,
                coefficient=serialize(c), seed=seed, complete_control_fibers=cases,
                within_control_matrix_entries=checked_entries,
                arbitrary_dirty_gaussian_values_forward_and_inverse=field_values,
                selected_source_columns_each_pattern=1 << (3 * f),
                complete_K_planes='One seeded full spectator/guard plane per complete control fiber; unchanged planes are also proved by the literal endpoint identity',
                child_shape='Canonical first a complete K chunks; selected bit K-1; every other bit remains a spectator',
                exact_activity_control_histogram=histogram, recorded_prefix_grid=gauges,
                omitted_input_gauge_rejected=gauge_witness, fixtures=fixtures,
                faster_child_supplied=False, shorter_scalar_word=False, new_multiplier_exponent=False,
                seconds=time.monotonic() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('A positive worker count is required')
    args.output.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).resolve()
    closure = {str(source.relative_to(TOPIC)): sha256(source.read_bytes()).hexdigest(),
               str(WORD.relative_to(TOPIC)): WORD_SHA,
               str(v.WORD.relative_to(TOPIC)): v.WORD_SHA,
               str(w.BASE.relative_to(TOPIC)): w.BASE_SHA}
    tasks = [(4, 1, ((1, 1), (0, 1)), 20261009121),
             (4, 2, ((-1, 1), (0, 1)), 20261009122),
             (4, 6, ((0, 1), (1, 1)), 20261009123),
             (4, 2, ((1, 2), (1, 2)), 20261009124)]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_sha256=closure,
                    tasks=tasks, workers=args.workers, native_threads_each=1, stdlib_only=True,
                    resource_preflight=dict(aggregate_memory_bytes_upper=1 << 30),
                    exact_child_oracle='Integral subset zeta plus explicit Gaussian-dyadic weight gauges',
                    scope='Complete selected operator kernels/fields with full-K endpoint-plane binding, no native runtime or recursion contraction claim')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = []
        for row in pool.map(coefficient_probe, tasks):
            rows.append(row)
            print(json.dumps({key: row[key] for key in ('status', 'K', 'coefficient', 'within_control_matrix_entries', 'seconds')}), flush=True)
    for name, digest in closure.items():
        if sha256((TOPIC / name).read_bytes()).hexdigest() != digest:
            raise AssertionError('An effective Gaussian fiber source changed during execution')
    (args.output / 'certificate.json').write_text(json.dumps(dict(cases=rows), indent=2) + '\n')


if __name__ == '__main__':
    main()
