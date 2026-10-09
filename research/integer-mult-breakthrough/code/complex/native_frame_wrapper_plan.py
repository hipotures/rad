#!/usr/bin/env python3
"""Bind compact Gaussian normal forms to explicitly paid native wrapper plans.

Reference arrays verify whole dyadic operators. Actual fixed-tape wrapper
costs remain conditional on native_gl_routes.py's complete-stream contract;
no Python array scatter is called a native routing implementation.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import native_gl_routes as routes


ROUTES_SHA = 'fc1b0bcc04fbc5bcaeb43b1db3e7fc16acd9d03d2d8a9fe87f7329b71eb79f54'
FIXTURES = {
    'scalable-subspace-normal-forms.json': '77fb258dcf779ae58e07a3839564114dd846694d0f49353dc3ec4439bc27cd42',
    'right-reflected-frame-interfaces.json': 'd59ea7611f919da38c6a1cb7ee49d22c79155171c9f6de8ec7f9fdb8e0c12d31',
}


def inverse_columns(columns):
    word = routes.gl_word(columns)
    return tuple(routes.apply_word(tuple(reversed(word)), 1 << j) for j in range(len(columns)))


def quadratic(q, x):
    return (q['constant'] + sum(c*(x >> j & 1) for j, c in enumerate(q['linear']))
            + sum(c*(x >> i & 1)*(x >> j & 1) for i, j, c in q['cross'])) % 4


def leaves(normal):
    if 'stages' in normal:
        return [leaf for stage in normal['stages'] for leaf in leaves(stage)]
    return [normal]


def wrapper_plan(normal, columns):
    n, r = normal['n'], normal['selected_rank_per_column']
    if columns < 1 or not 0 <= r <= n:
        raise ValueError('invalid bulk width')
    if 'stages' in normal:
        plans = [wrapper_plan(stage, columns) for stage in normal['stages']]
        child_count = sum(p['gaussian_children'] for p in plans)
        total_rank = sum(p['selected_rank_per_column'] for p in plans)
        if child_count > 1 or total_rank != r:
            raise AssertionError('composite fixture does not have the promised one-child rank')
        return dict(n=n, selected_rank_per_column=r, columns=columns,
                    recursive_axis_count=r*columns, gaussian_children=child_count,
                    same_width_child=any(p['same_width_child'] for p in plans),
                    temporal_stages=[stage for p in plans for stage in p['temporal_stages']],
                    transvection_calls=sum(p['transvection_calls'] for p in plans),
                    packed_translation_calls=sum(p['packed_translation_calls'] for p in plans),
                    unit_chirp_full_stream_passes=sum(p['unit_chirp_full_stream_passes'] for p in plans),
                    separate_global_phase_calls=0,
                    aggregate_global_phase_mod4=sum(p['aggregate_global_phase_mod4'] for p in plans) % 4,
                    monomial_normal_form_stages=len(plans), extra_scalar_roles=0,
                    cost_scope='All monomial stages paid; Gaussian child and whole recursive stock remain separate.')
    Qin, Qout = normal['input_quadratic'], normal['output_quadratic']
    if (Qin['constant'] + Qout['constant']) % 4 != normal['global_unit_exponent']:
        raise AssertionError('global audit metadata differs from implemented Q constants')
    before = routes.gl_word(inverse_columns(normal['input_columns']))
    after = routes.gl_word(normal['output_columns'])
    return dict(n=n, selected_rank_per_column=r, columns=columns,
                recursive_axis_count=r*columns, gaussian_children=int(r > 0),
                same_width_child=(r == n and r > 0),
                temporal_stages=[
                    dict(kind='GL', transvections=[list(g) for g in before]),
                    dict(kind='unit-chirp', quadratic=Qin),
                    dict(kind='C-child', selected_slots=list(range(r)), columns=columns),
                    dict(kind='unit-chirp', quadratic=Qout),
                    dict(kind='GL', transvections=[list(g) for g in after]),
                    dict(kind='affine-NOT', slots=[j for j in range(n) if normal['output_affine_offset'] >> j & 1]),
                ],
                transvection_calls=len(before)+len(after),
                packed_translation_calls=normal['output_affine_offset'].bit_count(),
                unit_chirp_full_stream_passes=2,
                separate_global_phase_calls=0,
                aggregate_global_phase_mod4=(columns*normal['global_unit_exponent']) % 4,
                address_companion='existing third complete fK-bit slot in the same role stream',
                extra_scalar_roles=0,
                cost_scope='Conditional complete-stream wrapper bill; C child, recursive termination and whole physical stock are separate.')


def column_vector(address, n, f, column):
    return sum((address >> ((n-j-1)*f+column) & 1) << j for j in range(n))


def replace_column(address, x, n, f, column):
    for j in range(n):
        bit = (n-j-1)*f+column
        address = (address & ~(1 << bit)) | ((x >> j & 1) << bit)
    return address


def C_factor(values, address_bit, inverse=False):
    stride = 1 << address_bit
    out = [None]*len(values)
    sign = -1 if inverse else 1
    for u in range(len(values)):
        if u & stride:
            continue
        v = u ^ stride
        A, B, C, D = values[u]
        a, b, c, d = values[v]
        out[u] = (A+a-sign*(B-b), B+b+sign*(A-a),
                  C+c-sign*(D-d), D+d+sign*(C-c))
        out[v] = (A+a+sign*(B-b), B+b-sign*(A-a),
                  C+c+sign*(D-d), D+d-sign*(C-c))
    return out


def execute(plan, values, inverse=False):
    n, f = plan['n'], plan['columns']
    denominator = 0
    stages = reversed(plan['temporal_stages']) if inverse else plan['temporal_stages']
    for stage in stages:
        kind = stage['kind']
        if kind == 'GL':
            word = tuple(tuple(g) for g in stage['transvections'])
            if inverse:
                word = tuple(reversed(word))
            def destination(address):
                for column in range(f):
                    x = column_vector(address, n, f, column)
                    address = replace_column(address, routes.apply_word(word, x), n, f, column)
                return address
            values = routes.scatter(values, destination)
        elif kind == 'unit-chirp':
            values = [routes.unit(value, (-1 if inverse else 1)*sum(
                quadratic(stage['quadratic'], column_vector(address, n, f, j)) for j in range(f)))
                for address, value in enumerate(values)]
        elif kind == 'C-child':
            factors = [(n-slot-1)*f+j for slot in stage['selected_slots'] for j in range(f)]
            for bit in (reversed(factors) if inverse else factors):
                values = C_factor(values, bit, inverse)
                denominator += 1
        elif kind == 'affine-NOT':
            mask = sum(1 << ((n-slot-1)*f+j) for slot in stage['slots'] for j in range(f))
            values = routes.scatter(values, lambda address: address ^ mask)
        else:
            raise ValueError('unsupported native wrapper stage')
    return values, denominator


def multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def reference_matrix(normal):
    n, r = normal['n'], normal['selected_rank_per_column']
    if 'stages' in normal:
        matrices = [reference_matrix(stage) for stage in normal['stages']]
        product = matrices[0]
        for matrix in matrices[1:]:
            rows = []
            for i in range(1 << n):
                row = []
                for j in range(1 << n):
                    a, b = 0, 0
                    for k in range(1 << n):
                        x, y = multiply(matrix[i][k], product[k][j])
                        a, b = a+x, b+y
                    row.append((a, b))
                rows.append(row)
            product = rows
        return product
    Pin = inverse_columns(normal['input_columns'])
    Pout = inverse_columns(normal['output_columns'])
    alpha = (1, 0)
    for _ in range(r):
        alpha = multiply(alpha, (1, 1))
    matrix = []
    for y in range(1 << n):
        a = routes.matrix_apply(Pout, y ^ normal['output_affine_offset'])
        row = []
        for x in range(1 << n):
            b = routes.matrix_apply(Pin, x)
            if a >> r != b >> r:
                row.append((0, 0))
            else:
                exponent = (quadratic(normal['output_quadratic'], a)
                            + quadratic(normal['input_quadratic'], b)
                            - ((a ^ b) & ((1 << r)-1)).bit_count()) % 4
                row.append(multiply(alpha, UNITS[exponent]))
        matrix.append(row)
    return matrix


def probe(task):
    label, normal, f, full = task
    plan = wrapper_plan(normal, f)
    n, r = plan['n'], plan['selected_rank_per_column']
    for leaf in leaves(normal):
        for cols in (leaf['input_columns'], leaf['output_columns']):
            word = routes.gl_word(cols)
            for j in range(n):
                if routes.apply_word(word, 1 << j) != cols[j]:
                    raise AssertionError('descriptor route does not implement physical columns')
    result = dict(fixture_case=label, n=n, columns=f, plan=plan,
                  GL_basis_images=2*n*len(leaves(normal)), full_payload_reference=full)
    if not full:
        return result
    original = [routes.payload(rank) for rank in range(1 << (n*f))]
    values, grid = execute(plan, original)
    if grid != r*f:
        raise AssertionError('C tensor denominator ledger differs from selected width')
    single = reference_matrix(normal)
    expected = []
    for y in range(len(original)):
        row = [0, 0, 0, 0]
        for x, field in enumerate(original):
            coefficient = (1, 0)
            for j in range(f):
                entry = single[column_vector(y, n, f, j)][column_vector(x, n, f, j)]
                coefficient = multiply(coefficient, entry)
                if coefficient == (0, 0):
                    break
            for pair in (0, 2):
                a, b = multiply(coefficient, field[pair:pair+2])
                row[pair] += a
                row[pair+1] += b
        expected.append(tuple(row))
    if values != expected:
        raise AssertionError('whole wrapper word differs from exact tensor normal form')
    restored, extra_grid = execute(plan, values, inverse=True)
    scaled = [tuple(value << (grid+extra_grid) for value in field) for field in original]
    if restored != scaled:
        raise AssertionError('arbitrary dirty four-field wrapper inverse failed')
    # The inverse returns exact trailing zeros on the common fixed grid;
    # no free format change or numerical truncation is performed.
    c = plan['aggregate_global_phase_mod4']
    if c and [routes.unit(field, c) for field in values] == expected:
        raise AssertionError('double-counted global audit phase negative did not reject')
    mutated = json.loads(json.dumps(normal))
    first = leaves(mutated)[0]
    first['global_unit_exponent'] = (first['global_unit_exponent']+1) % 4
    try:
        wrapper_plan(mutated, f)
    except AssertionError:
        pass
    else:
        raise AssertionError('corrupt global metadata accepted')
    result.update(complete_records=len(original), fields=4,
                  forward_reference_fields=4*len(original), inverse_fields=4*len(original),
                  grid_increment=grid, inverse_grid_increment=extra_grid,
                  double_global_phase_negative_discriminates=bool(c))
    return result


def fixture_cases(root):
    cases = []
    hashes = {}
    for name, expected in FIXTURES.items():
        path = root/name
        actual = sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise AssertionError('immutable normal-form fixture hash changed')
        hashes[name] = actual
        data = json.loads(path.read_text())
        for j, case in enumerate(data['cases']):
            normal = case.get('normal_form')
            if normal is not None:
                cases.append((f'{name}:{j}', normal))
            else:
                for k, stage in enumerate(case.get('stages', [])):
                    cases.append((f'{name}:{j}:stage{k}', stage))
    return cases, hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive worker count required')
    source = Path(__file__)
    before = sha256(source.read_bytes()).hexdigest()
    if sha256(Path(routes.__file__).read_bytes()).hexdigest() != ROUTES_SHA:
        raise AssertionError('paid routing reference source changed')
    started = time.monotonic()
    utc = datetime.now(timezone.utc).isoformat()
    fixture_root = source.parents[2]/'fixtures'/'complex'
    normals, fixture_hashes = fixture_cases(fixture_root)
    if args.bounded:
        normals = [normals[0]]
    jobs = [(label, normal, f, normal['n'] <= 4)
            for label, normal in normals for f in ((2,) if args.bounded else (1, 2))]
    if args.workers == 1:
        cases = [probe(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, jobs))
    if not any(c.get('double_global_phase_negative_discriminates') for c in cases):
        raise AssertionError('global double-charge negative not exercised')
    if sha256(source.read_bytes()).hexdigest() != before or sha256(Path(routes.__file__).read_bytes()).hexdigest() != ROUTES_SHA:
        raise AssertionError('effective source changed during execution')
    for name, expected in fixture_hashes.items():
        if sha256((fixture_root/name).read_bytes()).hexdigest() != expected:
            raise AssertionError('fixture changed during execution')
    result = dict(status='PASS', started_utc=utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=before, routing_source_sha256=ROUTES_SHA,
                  fixture_sha256=fixture_hashes, workers=args.workers, bounded=args.bounded,
                  seconds=time.monotonic()-started, cases=cases,
                  scope='Exact whole dyadic wrapper reference plus explicit paid route plan. Native wrapper time is conditional; the Gaussian child, complete recursive stock and termination are not implemented or certified.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status='PASS', cases=len(cases),
                          forward_reference_fields=sum(c.get('forward_reference_fields',0) for c in cases),
                          inverse_fields=sum(c.get('inverse_fields',0) for c in cases),
                          seconds=result['seconds'], scope=result['scope'])), flush=True)


if __name__ == '__main__':
    main()
