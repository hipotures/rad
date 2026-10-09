#!/usr/bin/env python3
"""Bind general actual frames, original graph ports, and complete dirty fields.

The original symmetric port operators remain unchanged. Generic median
representatives are connected by actual compiled words, including their
phases and routes. This is one finite local component, not a multiplier.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import lagrangian_frame_interfaces as general
import native_frame_wrapper_plan as wrappers


GENERAL_SHA = '1b9bce1af1b7ac39eafa9e765c5e58b362875ec0df1f81e91c80ada5d666b109'
WRAPPER_SHA = '3b2fa9fb3e992104ffdde75f5bbd407782691792c9189cf875324a509b1b069d'
WITNESS_SHA = '8ae3dd3489d18251dd540e2d7e5925c00e61f830bd67b6de9308df381894d96f'


def graph_word(A):
    n = len(A)
    q = general.exact.Quadratic(n)
    for j in range(n):
        q.linear[j] = A[j][j]
        for i in range(j):
            if A[i][j]:
                q.pair(i, j)
    # Htilde phases cancel between the two sides: this is the original
    # normalized Fourier conjugate of the canonical quadratic chirp.
    return ([('H', j, -1) for j in range(n)]
            + [('Q', general.exact.serialize_quadratic(q))]
            + [('H', j, 1) for j in range(n)])


def frame_covariance(n):
    frames = general.all_lagrangians(n)
    values_checked = path_zero_values = 0
    for L in frames:
        word = general.frame_word(L, n)['actual_word']
        X, Z = general.exact.tableau(word, n)
        zero, grid = general.literal_column(word, n, 0)
        for y in range(1 << n):
            if general.path_sum(word, n, y)[0] != zero[y]:
                raise AssertionError('actual global coefficient/path sum differs')
            path_zero_values += 1
        for x in range(1 << n):
            column, other_grid = general.literal_column(word, n, x)
            if other_grid != grid:
                raise AssertionError('literal matrix changed its fixed common grid')
            shift, character, phase = general.exact.pauli_combination(X, x)
            for y, value in enumerate(column):
                expected = general.exact.multiply_gaussian(zero[y ^ shift], general.exact.UNITS[
                    (phase+2*general.exact.dot(character, y ^ shift)) % 4])
                if value != expected:
                    raise AssertionError('full matrix column differs from actual phased Pauli image')
                values_checked += 1
    invalid = (1, 1 << n)+tuple(1 << j for j in range(1, n-1))
    try:
        general.frame_word(invalid, n)
    except ValueError:
        pass
    else:
        raise AssertionError('non-isotropic frame negative accepted')
    return dict(kind='complete-phased-frame-covariance', n=n, frames=len(frames),
                literal_entries_checked=values_checked, exact_zero_column_path_values=path_zero_values,
                nonisotropic_frame_negative_rejected=True)


def matrix(word, n):
    columns, grid = [], None
    for x in range(1 << n):
        values, bits = general.literal_column(word, n, x)
        if grid is not None and bits != grid:
            raise AssertionError('reference matrix has inconsistent grid')
        grid = bits
        columns.append(values)
    return [[columns[x][y] for x in range(1 << n)] for y in range(1 << n)], grid


def tensor_word(word, n, f, values):
    single, grid = matrix(word, n)
    out = []
    for y in range(len(values)):
        row = [0, 0, 0, 0]
        for x, fields in enumerate(values):
            coefficient = (1, 0)
            for j in range(f):
                coefficient = general.exact.multiply_gaussian(coefficient, single[
                    wrappers.column_vector(y, n, f, j)][wrappers.column_vector(x, n, f, j)])
                if coefficient == (0, 0):
                    break
            for pair in (0, 2):
                a, b = general.exact.multiply_gaussian(coefficient, fields[pair:pair+2])
                row[pair] += a
                row[pair+1] += b
        out.append(tuple(row))
    return out, grid*f


def component(f):
    fixture = Path(__file__).parents[2]/'fixtures'/'complex'/'noncommuting-four-incidence.json'
    if sha256(fixture.read_bytes()).hexdigest() != WITNESS_SHA:
        raise AssertionError('original port fixture changed')
    data = json.loads(fixture.read_text())
    n = data['n']
    ports = [graph_word(A) for A in data['incoming_symmetric_matrices']+data['outgoing_symmetric_matrices']]
    L = tuple((v >> n) | ((v & ((1 << n)-1)) << n) for v in data['common_lagrangian_basis'])
    common = general.frame_word(L, n)['actual_word']
    relative = [general.inverse_word(ports[0])+common, general.inverse_word(ports[1])+common,
                general.inverse_word(common)+ports[2], general.inverse_word(common)+ports[3]]
    normals = [general.compile_word(word, n, rank) for word, rank in zip(relative, data['charged_incidence_ranks'])]
    ranks = [normal['selected_rank_per_column'] for normal in normals]
    if ranks != [1, 1, 1, 2]:
        raise AssertionError('original actual graph ports lost the local intersection gain')
    # Complete coefficient binding for all four actual edges.
    edges_checked = 0
    for word, normal in zip(relative, normals):
        M, grid = matrix(word, n)
        r = normal['selected_rank_per_column']
        for y in range(1 << n):
            for x in range(1 << n):
                expected = general.exact.reconstructed_entry(normal, y, x)
                if M[y][x] != tuple(v << (grid-r) for v in expected):
                    raise AssertionError('generic anchor actual phase/route differs')
                edges_checked += 1
    plans = [wrappers.wrapper_plan(normal, f) for normal in normals]
    rawX = [wrappers.routes.payload(j) for j in range(1 << (n*f))]
    rawY = [wrappers.routes.unit(wrappers.routes.payload(j+len(rawX)), 1) for j in range(len(rawX))]
    X, gx = wrappers.execute(plans[0], rawX)
    Y, gy = wrappers.execute(plans[1], rawY)
    if gx != gy:
        raise AssertionError('common-frame payloads need explicit grid alignment')
    Y = [tuple(a+b for a, b in zip(x, y)) for x, y in zip(X, Y)]
    actualX, dx = wrappers.execute(plans[2], X)
    actualY, dy = wrappers.execute(plans[3], Y)
    gx, gy = gx+dx, gy+dy
    # Independent physical port reference: inverse original incoming K,
    # actual virtual shear, then original outgoing K. No generic anchor.
    VX, ix = tensor_word(general.inverse_word(ports[0]), n, f, rawX)
    VY, iy = tensor_word(general.inverse_word(ports[1]), n, f, rawY)
    if ix != iy:
        raise AssertionError('original-port reference grids differ')
    VY = [tuple(a+b for a, b in zip(x, y)) for x, y in zip(VX, VY)]
    expectX, ox = tensor_word(ports[2], n, f, VX)
    expectY, oy = tensor_word(ports[3], n, f, VY)
    for actual, grid, expected, reference_grid in ((actualX, gx, expectX, ix+ox), (actualY, gy, expectY, iy+oy)):
        if reference_grid < grid or expected != [tuple(v << (reference_grid-grid) for v in row) for row in actual]:
            raise AssertionError('whole actual two-bank operator differs from original port shear')
    if [wrappers.routes.unit(row, 1) for row in actualY] == actualY:
        raise AssertionError('global phase corruption negative did not discriminate')
    return dict(kind='original-graph-port-common-frame-shear', n=n, columns=f,
                selected_edge_ranks=ranks, total_rank=5, retained_all_graph_minimum=6,
                original_K_ports_preserved=True, exact_edge_entries=edges_checked,
                complete_two_bank_fields=8*len(rawX), compiled_output_grids=[gx, gy],
                reference_output_grids=[ix+ox, iy+oy],
                native_wrapper_plans=plans, extra_scalar_banks=0,
                phase_corruption_negative_rejects=True,
                scope='One finite two-role shear with all four original physical endpoints. No complete native primitive or exponent.')


def dispatch(task):
    kind, value = task
    return frame_covariance(value) if kind == 'frames' else component(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive workers required')
    files = [Path(__file__), Path(general.__file__), Path(general.exact.__file__),
             Path(general.exact.reference.__file__), Path(wrappers.__file__), Path(wrappers.routes.__file__)]
    before = {p.name:sha256(p.read_bytes()).hexdigest() for p in files}
    if before[Path(general.__file__).name] != GENERAL_SHA or before[Path(wrappers.__file__).name] != WRAPPER_SHA:
        raise AssertionError('pinned frame/wrapper source changed')
    utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [('frames', 2), ('component', 1)] if args.bounded else [('frames', 3), ('component', 1), ('component', 2)]
    if args.workers == 1:
        cases = [dispatch(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(dispatch, tasks))
    if before != {p.name:sha256(p.read_bytes()).hexdigest() for p in files}:
        raise AssertionError('effective source changed during run')
    certificate = dict(status='PASS', started_utc=utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                       effective_sources=before, workers=args.workers, bounded=args.bounded,
                       cases=cases, seconds=time.monotonic()-started,
                       scope='Full phased finite frames and original-port two-bank shear. Paid native wrapper and Gaussian child contracts remain conditional; no new whole chronology or exponent.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps(dict(status='PASS',cases=len(cases),seconds=certificate['seconds'],scope=certificate['scope'])),flush=True)


if __name__ == '__main__':
    main()
