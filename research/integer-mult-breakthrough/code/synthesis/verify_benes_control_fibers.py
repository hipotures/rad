#!/usr/bin/env python3
"""Bounded literal-slot and Gaussian-kernel checks for the declared component.

The retained contract is read-only. This does not regenerate discovery sweeps,
measure native tape time, supply a shorter row word or verify an exponent.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import time

TOPIC = Path(__file__).resolve().parents[2]
CONTRACT = TOPIC / 'fixtures/synthesis/benes-control-fiber-contract.json'
CONTRACT_SHA = '42eb6f2e6033fcecf458c9201f94248da15ac82c7e0981797b5059c39a6b0655'
if sha256(CONTRACT.read_bytes()).hexdigest() != CONTRACT_SHA:
    raise ValueError('The retained control-fiber contract changed')
contract = json.loads(CONTRACT.read_text())
for name, digest in contract['source_sha256'].items():
    if sha256((TOPIC / name).read_bytes()).hexdigest() != digest:
        raise ValueError('An effective component source changed: ' + name)

SPEC = importlib.util.spec_from_file_location('finite_gaussian_fiber_verifier', TOPIC / 'code/synthesis/benes_gaussian_fiber_operator.py')
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)
v, w, b = g.v, g.w, g.b


def expect_rejection(action, message):
    try:
        action()
    except (ValueError, AssertionError):
        return
    raise AssertionError(message)


def verify_endpoint():
    rng = random.Random(20261009131)
    checked = 0
    for f, K in ((4, 1), (4, 2), (8, 6), (16, 6)):
        n = (3 * f + 12) * K
        for pattern in ((0, 0), (0, 1), (1, 0), (1, 1)):
            for unused in range(16):
                original = w.canonical_embed(tuple(rng.getrandbits(f) for unused in range(3)),
                                             f, K, rng.getrandbits(n - 3 * f))
                actual = v.compact_address(original, f, K, pattern=pattern)
                if actual != v.reference_compact(original, f, K, pattern):
                    raise AssertionError('Bounded literal canonical endpoint failed')
                if v.compact_address(actual, f, K, pattern=pattern, inverse=True) != original:
                    raise AssertionError('A dirty companion, guard or spectator did not restore')
                checked += 1
    negatives = contract['literal_negative_controls']
    for name, option in (('omitted_decoding', dict(literal=False, wrong_decode=True)),
                         ('omitted_exceptional_correction', dict(omit_repair=True))):
        witness = negatives[name]
        actual = v.compact_address(witness['original'], 4, 1,
                                   pattern=tuple(witness['pattern']), **option)
        if actual != witness['wrong'] or actual == witness['expected']:
            raise AssertionError('A retained literal corruption witness was not reproduced: ' + name)
    witness = negatives['omitted_canonical_control_label_reconstruction']
    actual = w.compact_address(witness['original'], 4, 1,
                              pattern=tuple(witness['pattern']), literal=False)
    if actual != witness['wrong'] or actual == witness['expected']:
        raise AssertionError('The immutable version-two matching negative disappeared')
    for f in (4, 8, 16, 32, 128, 1024):
        swaps, unused_orders = w.stock_layout(f)
        if len(swaps) > 60:
            raise AssertionError('The bounded stock placement escaped its all-size bound')
    expect_rejection(lambda: w.stock_layout(6), 'Unpaid non-power-of-two wire padding was accepted')
    expect_rejection(lambda: w.validate_shape(4, 0), 'An empty complete guard chunk was accepted')
    expect_rejection(lambda: w.packed_xor(1 << 7, 0, 0, 8, 2),
                     'A terminal selected guard was illegally targeted')
    return dict(literal_complete_address_samples=checked, retained_corruptions_reproduced=3,
                arbitrary_companions_and_all_guard_planes_restored=True)


def verify_operator():
    f, checked, fields, gauge_controls = 4, 0, 0, 0
    for item in contract['gaussian_fixtures']:
        K = item['K']
        c = tuple(Q(numerator, denominator) for numerator, denominator in item['coefficient'])
        cp = g.powers(c, f)
        for fixture in item['fixtures']:
            y, z = fixture['y'], fixture['z']
            pattern = tuple(fixture['pattern'])
            active, a, route = g.physical_fiber_route(f, K, y, z, pattern,
                                                     fixture['complete_spectator_plane'])
            if (active, a, route) != (fixture['active'], fixture['a'], fixture['action_permutation']):
                raise AssertionError('A retained canonical complete-K child fixture changed')
            low = (1 << a) - 1
            for source in range(1 << f):
                for target in range(1 << f):
                    j, k = route[source], route[target]
                    actual = cp[(k & low).bit_count() - (j & low).bit_count()] if j >> a == k >> a and not (j & low) & ~(k & low) else g.ZERO
                    expected = cp[(target & active).bit_count() - (source & active).bit_count()] if source & ~active == target & ~active and not (source & active) & ~(target & active) else g.ZERO
                    if actual != expected:
                        raise AssertionError('A bounded actual Gaussian kernel entry failed')
                    checked += 1
            values = [(Q(3 * i - 7, 16), Q(5 * i + 3, 8)) for i in range(1 << f)]
            actual, unused_grid = g.apply_fiber(values, route, a, c)
            expected = g.direct_gate(values, f, active, c)
            if actual != expected or g.apply_fiber(actual, route, a, g.neg(c))[0] != values:
                raise AssertionError('A bounded arbitrary dirty Gaussian field or inverse failed')
            if c != g.ONE and a and g.apply_fiber(values, route, a, c, omit_input_gauge=True)[0] != expected:
                gauge_controls += 1
            fields += len(values)
    if gauge_controls < 3:
        raise AssertionError('Nonunit/phase gauge corruption controls were not exercised')
    expect_rejection(lambda: g.inverse(g.ZERO), 'A zero Gaussian child gauge was accepted')
    return dict(within_control_kernel_entries=checked, complete_dirty_gaussian_field_values=fields,
                nonunit_and_phase_gauge_negatives=gauge_controls,
                preserved_inactive_patterns=3, recursive_child_is_exact_oracle=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component', choices=('all', 'endpoint', 'operator'), default='all')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise ValueError('Optional outputs must be fresh')
    started, clock = time.monotonic(), datetime.now(timezone.utc).isoformat()
    source = Path(__file__).resolve()
    closure = dict(contract['source_sha256'])
    closure[str(CONTRACT.relative_to(TOPIC))] = CONTRACT_SHA
    closure[str(source.relative_to(TOPIC))] = sha256(source.read_bytes()).hexdigest()
    results = {}
    if args.component in ('all', 'endpoint'):
        results['endpoint'] = verify_endpoint()
    if args.component in ('all', 'operator'):
        results['operator'] = verify_operator()
    for name, digest in closure.items():
        if sha256((TOPIC / name).read_bytes()).hexdigest() != digest:
            raise AssertionError('An effective immutable input changed during verification')
    summary = dict(status='PASS BENES CANONICAL CONTROL FIBERS', component=args.component,
                   checks=results, seconds=time.monotonic() - started,
                   measured_native_runtime=False, faster_zeta_supplier=False, new_kappa=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(dict(started_utc=clock, source_sha256=closure,
                                                                  component=args.component, stdlib_only=True), indent=2) + '\n')
        (args.output / 'certificate.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
