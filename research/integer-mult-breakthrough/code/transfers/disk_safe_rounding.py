#!/usr/bin/env python3
"""Exact finite controls for a conditional disk-valued numerical interface.

The target must already have modulus at most one, and a complete endpoint
error bound is a prerequisite. This is a final arithmetic scan, not a native
transform supplier, a physical fixed-tape execution, or an exponent claim.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time


def norm_squared(z):
    return z[0]*z[0]+z[1]*z[1]


def difference(a, b):
    return a[0]-b[0], a[1]-b[1]


def toward_zero(value):
    return value.numerator//value.denominator if value >= 0 else -((-value).numerator//value.denominator)


def grid_truncate(z, precision):
    scale = 1 << precision
    return tuple(toward_zero(component*scale) for component in z)


def safe_numerators(z, precision):
    """Truncate, then move the larger nonzero component one unit toward zero."""
    if precision < 1:
        raise ValueError('The stated sufficient proof uses p>=1')
    values = list(grid_truncate(z, precision))
    selected = 0 if abs(values[0]) >= abs(values[1]) else 1
    if values[selected]:
        values[selected] += -1 if values[selected] > 0 else 1
    return tuple(values)


def represented(values, precision):
    return tuple(Fraction(component, 1 << precision) for component in values)


def one_record(target, approximate, precision):
    h = Fraction(1, 1 << precision)
    eta = h/8
    if norm_squared(target) > 1:
        raise ValueError('The ideal target must belong to the closed unit disk')
    if norm_squared(difference(approximate, target)) > eta*eta:
        raise ValueError('The complete coefficient error must be at most 2^(-p-3)')
    output = safe_numerators(approximate, precision)
    value = represented(output, precision)
    if norm_squared(value) > 1:
        raise AssertionError('The final numerical interface must return a disk value')
    if norm_squared(difference(value, target)) >= 9*h*h:
        raise AssertionError('The sufficient absolute error must be less than 3*2^-p')
    return dict(ideal=[str(x) for x in target], approximate=[str(x) for x in approximate],
                output=list(output), output_norm_squared=str(norm_squared(value)),
                error_norm_squared=str(norm_squared(difference(value, target))))


def probe(task):
    precision, seed, records = task
    rng = Random(seed)
    h = Fraction(1, 1 << precision)
    q = precision+6
    scale = 1 << q
    fields = []
    for field in range(4):
        cases = []
        while len(cases) < records:
            z = (Fraction(rng.randrange(-scale, scale+1), scale),
                 Fraction(rng.randrange(-scale, scale+1), scale))
            if norm_squared(z) > 1:
                continue
            step = h/32
            error = (step*(-1 if (len(cases)+field) % 2 else 1),
                     step*(-1 if (2*len(cases)+field) % 3 else 1))
            cases.append(one_record(z, tuple(a+b for a, b in zip(z, error)), precision))
        for axis in (0, 1):
            for sign in (-1, 1):
                z = tuple(Fraction(sign if component == axis else 0) for component in (0, 1))
                approximate = tuple(a+(sign*h/8 if component == axis else 0)
                                    for component, a in enumerate(z))
                cases.append(one_record(z, approximate, precision))
        zero = one_record((Fraction(0), Fraction(0)), (h/32, -h/32), precision)
        if zero['output'] != [0, 0]:
            raise AssertionError('Small final padding residues must truncate to exact zero')
        cases.append(zero)
        fields.append(dict(field=field, complete_records=len(cases), records=cases))
    # This near-boundary target has a finer ideal grid. A generic disk-valued
    # target and admitted error do not guarantee that ordinary Q_p stays inside.
    if precision < 3:
        raise ValueError('The negative control requires p>=3')
    target = (1-h*h, h)
    approximate = (Fraction(1), h)
    if norm_squared(target) > 1 or h*h > h/8:
        raise AssertionError('The exact negative-control domain must be admitted')
    ordinary = represented(grid_truncate(approximate, precision), precision)
    if norm_squared(ordinary) <= 1:
        raise AssertionError('Omitting the safe decrement must fail this admitted disk target')
    witness = one_record(target, approximate, precision)
    if witness['output'] != [(1 << precision)-1, 1]:
        raise AssertionError('The displayed safe negative-control output must be literal')
    for target_bad, error_bad in (((Fraction(2), Fraction(0)), (Fraction(2), Fraction(0))),
                                  ((Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)))):
        try:
            one_record(target_bad, error_bad, precision)
        except ValueError:
            pass
        else:
            raise AssertionError('The target disk and absolute error premises must be enforced')
    return dict(precision=precision, seed=seed, fields=fields,
                ordinary_truncation_failure=dict(ideal=[str(x) for x in target],
                    approximate=[str(x) for x in approximate],
                    ordinary_output=list(grid_truncate(approximate, precision)),
                    ordinary_norm_squared=str(norm_squared(ordinary)), safe_result=witness),
                domain_and_error_premises_checked=True,
                scope='Exact scalar final-scan controls with admitted errors and a generic '
                      'disk-valued target; no native transform or time theorem.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('At least one actual worker is required')
    if args.output and args.output.exists():
        raise FileExistsError('Completed output evidence is immutable; use a fresh path')
    topic = Path(__file__).resolve().parents[2]
    config_path = topic/'configs/transfers/disk-safe-rounding.json'
    config = json.loads(config_path.read_text())
    tasks = [(p, config['seed']+i, config['records_per_field'])
             for i, p in enumerate(config['precisions'])]
    if args.small:
        tasks = tasks[:1]
    started = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    if args.workers == 1:
        results = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(probe, tasks))
    output = dict(status='PASS', actual_start_utc=started, workers=args.workers,
                  elapsed_seconds=time.monotonic()-start, cases=results,
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  config_sha256=sha256(config_path.read_bytes()).hexdigest(),
                  scope='Exact finite disk-recovery controls; the all-size comparison '
                        'and linear scan bill are separate analytical deductions.')
    text = json.dumps(output, indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(json.dumps(dict(status=output['status'], actual_start_utc=started,
                         workers=args.workers, cases=len(results),
                         elapsed_seconds=output['elapsed_seconds'],
                         complete_records=sum(sum(f['complete_records'] for f in c['fields'])
                                              for c in results)), sort_keys=True))


if __name__ == '__main__':
    main()
