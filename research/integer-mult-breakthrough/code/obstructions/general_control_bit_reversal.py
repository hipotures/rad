#!/usr/bin/env python3
"""Paid frozen-control masks and three-shear selected-bit reversal controls.

The finite routing oracle is not a measured fixed-tape implementation.
Masks are computed from a control chunk fixed during each eight-rotation word.
Each complete native subslot includes a terminal K-bit guard range.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import time

TOPIC = Path(__file__).resolve().parents[2]
HELPER = TOPIC / 'code/transfers/native_gl_review.py'
HELPER_SHA = '1ae606d030f1f71ebe2d2497399601f1cdc6e59aa4e3209527533ecf57432d19'
if sha256(HELPER.read_bytes()).hexdigest() != HELPER_SHA:
    raise ValueError('The retained literal routing helper changed')
SPEC = importlib.util.spec_from_file_location('frozen_control_literal_helper', HELPER)
r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r)


def reflect(value, k, active, rho=0):
    return sum(((value >> (rho + j * k)) & 1) << (rho + (active - 1 - j) * k)
               for j in range(active))


def primitive(control, target, companion, k, active, rho=0):
    mask = reflect(control, k, active, rho)
    _, target, companion = r.rotations(mask, target, companion, k, active + 1, rho)
    _, target, companion = r.repair(mask, target, companion, k, active + 1, rho)
    return control, target, companion


def native_case(selected_control):
    started = time.monotonic()
    k, active, rho = 6, 2, 0
    control = sum(((selected_control >> j) & 1) << (j * k) for j in range(active))
    mask = reflect(control, k, active)
    wrong, witness = 0, None
    for target in range(128):
        for companion in range(128):
            actual = r.rotations(mask, target, companion, k, active + 1, rho)
            if r.rotations(*actual, k, active + 1, rho, True) != (mask, target, companion):
                raise AssertionError('Frozen-mask chronological inverse failed')
            ideal = (mask, target ^ mask, companion)
            if actual != ideal:
                wrong += 1
                witness = witness or [control, target, companion, list(actual), list(ideal)]
            if primitive(control, target, companion, k, active) != (control, target ^ mask, companion):
                raise AssertionError('Complete generalized-mask correction failed')
    rng = random.Random(202610090440 + selected_control)
    modulus = 1 << ((active + 1) * k)
    safe = 0
    for index in range(256):
        control, target, companion = [rng.randrange(modulus) for _ in range(3)]
        if index % 2 == 0:
            for position in (0, k):
                guard = 31 << (position + 1)
                target = (target & ~guard) | (rng.randrange(10, 22) << (position + 1))
                companion = (companion & ~guard) | (rng.randrange(10, 22) << (position + 1))
        mask = reflect(control, k, active)
        actual = r.rotations(mask, target, companion, k, active + 1, rho)
        if r.bad(actual[1], actual[2], k, active + 1, rho) != r.bad(target, companion, k, active + 1, rho):
            raise AssertionError('Generalized-mask exceptional set changed')
        if not r.bad(target, companion, k, active + 1, rho):
            safe += 1
            if actual != (mask, target ^ mask, companion):
                raise AssertionError('Complete carry-free mask lift failed')
        if primitive(control, target, companion, k, active) != (control, target ^ mask, companion):
            raise AssertionError('A spectator, terminal guard or dirty companion changed')
    if not safe:
        raise AssertionError('No complete carry-free address was tested')
    return dict(kind='arbitrary-frozen-control-mask', selected_control=selected_control,
                quotient_pairs=128 * 128, complete_address_samples=256,
                safe_complete_samples=safe, unrepaired_wrong=wrong,
                omitted_repair_witness=witness, terminal_guard_chunks=1,
                seconds=time.monotonic() - started)


def selected_word(x, y, companion, k, active):
    _, x, companion = primitive(y, x, companion, k, active)
    _, y, companion = primitive(x, y, companion, k, active)
    _, x, companion = primitive(y, x, companion, k, active)
    return x, y, companion


def selected_goal(x, y, companion, k, active):
    mask = sum(1 << (j * k) for j in range(active))
    return ((x & ~mask) | reflect(y, k, active),
            (y & ~mask) | reflect(x, k, active), companion)


def payload_case(unused):
    started = time.monotonic()
    k, active, width = 1, 2, 3
    count = 2 * (1 << (3 * width)) * 2
    original = [r.payload(index) for index in range(count)]

    def decode(index):
        tail, index = index % 2, index // 2
        chunks = [0] * 3
        for j in range(2, -1, -1):
            chunks[j], index = index % 8, index // 8
        return index, chunks, tail

    def encode(head, chunks, tail):
        for value in chunks:
            head = head * 8 + value
        return head * 2 + tail

    def shear(values, source, target):
        for changed, sign, parity in r.ROTATIONS:
            def rotation(index):
                head, chunks, tail = decode(index)
                slot, other = (target, 2) if changed == 0 else (2, target)
                control = reflect(chunks[source], k, active)
                offset = sum(1 << p for p in range(active)
                             if control >> p & 1 and (chunks[other] >> p & 1) == parity)
                chunks[slot] = (chunks[slot] + sign * offset) % 8
                return encode(head, chunks, tail)
            values = r.route(values, rotation)

        def correction(index):
            head, chunks, tail = decode(index)
            control = reflect(chunks[source], k, active)
            _, chunks[target], chunks[2] = r.repair(control, chunks[target], chunks[2], k, active + 1, 0)
            return encode(head, chunks, tail)
        return r.route(values, correction)

    values = list(original)
    for source, target in ((1, 0), (0, 1), (1, 0)):
        values = shear(values, source, target)

    def goal(index):
        head, chunks, tail = decode(index)
        chunks = list(selected_goal(*chunks, k, active))
        return encode(head, chunks, tail)
    expected = r.route(original, goal)
    if values != expected:
        raise AssertionError('Complete literal three-shear payload word failed')
    for source, target in ((1, 0), (0, 1), (1, 0)):
        values = shear(values, source, target)
    if values != original:
        raise AssertionError('The inverse bit reversal failed on dirty records')
    rng = random.Random(440903)
    for unused in range(512):
        inputs = tuple(rng.randrange(1 << 24) for unused in range(3))
        if selected_word(*inputs, 6, 3) != selected_goal(*inputs, 6, 3):
            raise AssertionError('The six-bit full-slot reversal lift failed')
    # An arbitrary nonlinear involution is a valid primitive control but need
    # not satisfy the distributive identity used by the three-shear exchange.
    nonlinear = lambda x: x ^ (((x & 1) & ((x >> 1) & 1)) << 2)
    witness = None
    for x in range(8):
        for y in range(8):
            a, b = x ^ nonlinear(y), y
            b ^= nonlinear(a)
            a ^= nonlinear(b)
            if (a, b) != (nonlinear(y), nonlinear(x)):
                witness = witness or [x, y, a, b, nonlinear(y), nonlinear(x)]
    if witness is None:
        raise AssertionError('The nonlinear-exchange scope control disappeared')
    return dict(kind='complete-three-shear-selected-reversal', complete_records=count,
                payload_fields=4, literal_rotations=24, correction_stages=3,
                complete_six_bit_address_samples=512, all_companion_spectators_and_guards_restored=True,
                inverse_pass=True, nonlinear_exchange_rejected=witness,
                expected_full_payload_sha256=sha256(str(expected).encode()).hexdigest(),
                seconds=time.monotonic() - started)


def dispatch(task):
    kind, value = task
    return native_case(value) if kind == 'mask' else payload_case(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or args.output and args.output.exists():
        raise ValueError('Positive workers and a fresh optional output are required')
    source = Path(__file__).resolve()
    before = {str(source.relative_to(TOPIC)): sha256(source.read_bytes()).hexdigest(),
              str(HELPER.relative_to(TOPIC)): HELPER_SHA}
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    workers=args.workers, source_and_helper_sha256=before,
                    input='Exhaustive selected control masks and low quotients; complete toy records; seeded full address samples',
                    conditional_control_rule='G depends only on chunks fixed throughout each complete eight-rotation word',
                    guard_geometry='Every equal subslot has g active K-chunks and one existing terminal K-chunk; two such subslots per old slot',
                    scope='Exact finite oracle and conditional native extension; no complete Gaussian network or exponent')
    tasks = [('mask', value) for value in range(4)] + [('payload', 0)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(dispatch, tasks))
    if any(sha256((TOPIC / name).read_bytes()).hexdigest() != digest
           for name, digest in before.items()):
        raise ValueError('An effective source changed during verification')
    if not any(row.get('unrepaired_wrong', 0) for row in rows):
        raise AssertionError('Omitting exceptional repair did not fail')
    summary = dict(status='PASS FROZEN CONTROL AND SELECTED REVERSAL', cases=rows,
                   fixed_packed_words=3, literal_rotations=24,
                   native_time_conditional=True, measured_native_tape_time=False,
                   complete_gaussian_network=False, new_multiplier_exponent=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'], cases=len(rows),
                         quotient_pairs=sum(row.get('quotient_pairs', 0) for row in rows),
                         complete_records=rows[-1]['complete_records'])))


if __name__ == '__main__':
    main()
