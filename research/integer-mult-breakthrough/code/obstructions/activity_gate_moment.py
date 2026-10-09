#!/usr/bin/env python3
"""Exact activity-volume and optimistic scalar-gate moment discriminator.

The binomial law assumes complete prefix cylinders with all K-bit chunks.
The moment is an assumed normalized cost model, not a native supplier.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb, isqrt
from pathlib import Path
import time


def activity_rows(h, f):
    if h < 2 or f < 1:
        raise ValueError('Positive block count and base width at least two required')
    D = 1 << h
    return [(w, Q(comb(f, w) * 2**w * (D-2)**(f-w), D**f))
            for w in range(f+1)]


def validate_rows(h, f, rows):
    D = 1 << h
    if [w for w, _ in rows] != list(range(f+1)):
        raise AssertionError('Every activity width must be present once')
    if any(weight < 0 for _, weight in rows) or sum(q for _, q in rows) != 1:
        raise AssertionError('Complete nonnegative physical volume must sum to one')
    mean = sum(w*q for w, q in rows)
    variance = sum((Q(w)-mean)**2*q for w, q in rows)
    if mean != Q(2*f, D) or variance != f*Q(2, D)*(1-Q(2, D)):
        raise AssertionError('The claimed pair-activity law has incorrect moments')


def sqrt_interval(value, bits=80):
    scale = 1 << bits
    floor = isqrt((value.numerator << (2*bits)) // value.denominator)
    low = Q(floor, scale)
    high = low if low*low == value else Q(floor+1, scale)
    if not low*low <= value <= high*high:
        raise AssertionError('Integer square-root enclosure failed')
    return low, high


def jensen_contract(h, gates, numerator, denominator):
    """Certify gates*(2/(h*2**h))**p < 1 by positive integer powers."""
    if h < 2 or gates < 1 or not 0 < numerator <= denominator:
        raise ValueError('Positive gate count and exponent in (0,1] required')
    base = h*(1 << h)//2
    left, right = gates**denominator, base**numerator
    return dict(base_width=h, scalar_gates=gates,
                exponent=f'{numerator}/{denominator}',
                comparison_left=str(left), comparison_right=str(right),
                strict_jensen_contraction=left < right,
                hypothetical_word_only=True)


def probe(task):
    h, f, K = task
    D = 1 << h
    rows = activity_rows(h, f)
    validate_rows(h, f, rows)
    baseline = h*D//2
    first = baseline*sum(Q(w, h*f)*q for w, q in rows)
    if first != 1:
        raise AssertionError('The ordinary gate count must have first moment one')
    # Full K-bit spectators alter the physical volume, not the width law.
    total_addresses = 1 << (h*f*K)
    physical = []
    for w, weight in rows:
        volume = weight*total_addresses
        if volume.denominator != 1:
            raise AssertionError('A complete activity class must have integral volume')
        child_addresses = 1 << (w*K)
        if volume.numerator % child_addresses:
            raise AssertionError('Whole active K-bit cylinders must fit without padding')
        physical.append(dict(width=w, cylinders=volume.numerator//child_addresses,
                             addresses_per_child=child_addresses))
    if sum(r['cylinders']*r['addresses_per_child'] for r in physical) != total_addresses:
        raise AssertionError('A physical address was lost or duplicated')
    low = high = Q(0)
    for w, probability in rows:
        a, b = sqrt_interval(Q(w, h*f))
        low += baseline*probability*a
        high += baseline*probability*b
    if not low > first:
        raise AssertionError('Ordinary gates must fail the half-power moment')
    jlow, jhigh = sqrt_interval(Q(2, h*D))
    if low > baseline*jhigh:
        raise AssertionError('The exact finite lower bound exceeds Jensen upper bound')
    broken = [(w, q) for w, q in rows if w != f]
    try:
        validate_rows(h, f, broken)
    except AssertionError:
        pass
    else:
        raise AssertionError('Deleting the rare all-active class was accepted')
    if Q(2*baseline, h*D) < 1:
        raise AssertionError('Ordinary gates were mislabeled a strict improvement')
    return dict(base_width=h, blocks=f, chunk_width=K, selected_width=h*f,
                complete_classes=len(rows), baseline_gates=baseline,
                first_moment=str(first), half_moment_interval=[str(low), str(high)],
                jensen_half_upper=str(baseline*jhigh),
                maximum_child_width=f, total_address_bits=h*f*K,
                full_chunk_cylinder_ledger_sha256=sha256(json.dumps(physical).encode()).hexdigest(),
                complete_volume=True, omitted_rare_class_rejected=True,
                native_layout_cost_proved=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    source = Path(__file__).resolve()
    source_hash = sha256(source.read_bytes()).hexdigest()
    tasks = [(2, 1, 1), (3, 4, 2)] if args.bounded else [
        (2, 1, 1), (2, 16, 3), (3, 1, 2), (3, 4, 2),
        (3, 64, 1), (4, 16, 2), (4, 256, 1), (6, 32, 2)]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                    source_sha256=source_hash, workers=args.workers, cases=tasks,
                    randomness='None; every activity class is retained',
                    scope='Exact activity volume and assumed moment model; no short circuit or multiplier')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    start = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        cases = list(pool.map(probe, tasks))
    hypothetical = jensen_contract(3, 11, 97, 100)
    baseline = jensen_contract(3, 12, 97, 100)
    if not hypothetical['strict_jensen_contraction'] or baseline['strict_jensen_contraction']:
        raise AssertionError('The exact optimistic gate-count comparison failed')
    if sha256(source.read_bytes()).hexdigest() != source_hash:
        raise AssertionError('Source changed during the experiment')
    result = dict(status='PASS EXACT ACTIVITY VOLUME AND CONDITIONAL MOMENT SCREEN',
                  cases=cases, hypothetical_eleven_gate_word=hypothetical,
                  ordinary_twelve_gate_word=baseline, seconds=time.monotonic()-start,
                  complete_scalar_word_provided=False, native_bill_proved=False,
                  new_exponent=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], cases=len(cases),
                          complete_classes=sum(c['complete_classes'] for c in cases),
                          seconds=result['seconds'], new_exponent=False)))


if __name__ == '__main__':
    main()
