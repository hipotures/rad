#!/usr/bin/env python3
"""Exact full-width/zero-width wrapper endpoint controls on complete fields.

Same-width children remain opaque paid calls in the plan. This verifier uses
elementary reference arrays and supplies no recursive termination proof.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import native_frame_wrapper_plan as wrappers


WRAPPER_SHA = '3b2fa9fb3e992104ffdde75f5bbd407782691792c9189cf875324a509b1b069d'


def normal(n, kind):
    rank = 0 if kind == 'identity' else n
    inverse = kind == 'inverse-C'
    Q = dict(constant=(-n) % 4 if inverse else 0,
             linear=[2 if inverse else 0]*n, cross=[])
    R = dict(constant=0, linear=[2 if inverse else 0]*n, cross=[])
    return dict(n=n, selected_rank_per_column=rank, one_bulk_child_calls=int(rank > 0),
                input_columns=[1 << j for j in range(n)], output_columns=[1 << j for j in range(n)],
                output_affine_offset=0, input_quadratic=Q, output_quadratic=R,
                global_unit_exponent=Q['constant'])


def direct_C(values, width, inverse):
    kernels = []
    for differences in range(width+1):
        coefficient = (1, 0)
        for j in range(width):
            imaginary = (1 if inverse else -1) if j < differences else (-1 if inverse else 1)
            coefficient = wrappers.multiply(coefficient, (1, imaginary))
        kernels.append(coefficient)
    out = []
    for y in range(len(values)):
        row = [0, 0, 0, 0]
        for x, value in enumerate(values):
            coefficient = kernels[(x ^ y).bit_count()]
            for pair in (0, 2):
                a, b = wrappers.multiply(coefficient, value[pair:pair+2])
                row[pair] += a
                row[pair+1] += b
        out.append(tuple(row))
    return out


def check(task):
    n, f, kind = task
    descriptor = normal(n, kind)
    plan = wrappers.wrapper_plan(descriptor, f)
    rank = descriptor['selected_rank_per_column']
    if plan['recursive_axis_count'] != rank*f:
        raise AssertionError('bulk/profile rank was confused with selected-axis count')
    if plan['same_width_child'] != (rank == n):
        raise AssertionError('same-width endpoint call was concealed')
    if plan['gaussian_children'] != int(kind != 'identity'):
        raise AssertionError('endpoint child count changed')
    values = [wrappers.routes.payload(j) for j in range(1 << (n*f))]
    result, grid = wrappers.execute(plan, values)
    expected = values if kind == 'identity' else direct_C(values, n*f, kind == 'inverse-C')
    if result != expected or grid != rank*f:
        raise AssertionError('endpoint whole field operator differs from direct kernel')
    back, extra = wrappers.execute(plan, result, inverse=True)
    if back != [tuple(v << (grid+extra) for v in row) for row in values]:
        raise AssertionError('endpoint inverse did not restore all fields on fixed grid')
    return dict(n=n, columns=f, kind=kind, exact_records=len(values), exact_fields=4*len(values),
                forward_grid=grid, inverse_grid=extra,
                profile_rank=rank, selected_axis_count=rank*f, gaussian_children=plan['gaussian_children'],
                same_width_child=plan['same_width_child'],
                recursive_termination_supplied=False,
                global_phase_audit=plan['aggregate_global_phase_mod4'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive workers required')
    source = Path(__file__)
    before = {p.name: sha256(p.read_bytes()).hexdigest() for p in
              (source, Path(wrappers.__file__), Path(wrappers.routes.__file__))}
    if before[Path(wrappers.__file__).name] != WRAPPER_SHA or before[Path(wrappers.routes.__file__).name] != wrappers.ROUTES_SHA:
        raise AssertionError('pinned wrapper closure changed')
    utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [(3, 2, kind) for kind in ('identity', 'C', 'inverse-C')]
    if not args.bounded:
        tasks += [(n, f, kind) for n, f in ((3, 1), (4, 1), (4, 2))
                  for kind in ('identity', 'C', 'inverse-C')]
    if args.workers == 1:
        cases = [check(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(check, tasks))
    after = {p.name: sha256(p.read_bytes()).hexdigest() for p in
             (source, Path(wrappers.__file__), Path(wrappers.routes.__file__))}
    if before != after:
        raise AssertionError('effective source changed during endpoint checks')
    certificate = dict(status='PASS', started_utc=utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                       source_sha256=before, source_freeze_verified=True,
                       workers=args.workers, bounded=args.bounded, cases=cases,
                       seconds=time.monotonic()-started,
                       scope='Exact direct Gaussian endpoint and inverse controls on all four fields. Same-width C calls remain explicit; no native runtime, recursive termination or exponent certificate.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(certificate, indent=2)+'\n')
    print(json.dumps(dict(status='PASS', cases=len(cases),
                          fields=sum(c['exact_fields'] for c in cases),
                          seconds=certificate['seconds'], scope=certificate['scope'])), flush=True)


if __name__ == '__main__':
    main()
