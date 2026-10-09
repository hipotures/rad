#!/usr/bin/env python3
"""Complete canonical signed exchange through one reused arbitrary-dirty helper.

The named architecture performs all scalar updates at one actual common
Clifford frame. Every source/sink interface and the helper's final F*z are
paid. This is a capacity control, not a universal one-helper obstruction.
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


def echo_word():
    result = []
    for target, source, coefficient in ((0, 1, 1), (1, 0, -1), (0, 1, 1)):
        result += [(target, 2, -coefficient), (2, source, 1),
                   (target, 2, coefficient), (2, source, -1)]
    return tuple(result)


def scalar_matrix(word):
    M = [[int(i == j) for j in range(3)] for i in range(3)]
    largest = 1
    prefixes = []
    for target, source, coefficient in word:
        M[target] = [a+coefficient*b for a, b in zip(M[target], M[source])]
        largest = max(largest, *(sum(abs(v) for v in row) for row in M))
        prefixes.append([row[:] for row in M])
    return M, largest, prefixes


def distance(A, B, n):
    return len(general.exact.basis(tuple(A)+tuple(B)))-n


def ports(U, n):
    F = [('C', 1 << j, 1) for j in range(n)]
    line = [('C', U, 1)]
    kernel = [('C', U, -1)]+F
    return [line, [], []], [F, kernel, F]


def median_label(n):
    if n != 3:
        raise ValueError('the retained four-incidence median has dimension three')
    fixture = Path(__file__).parents[2]/'fixtures'/'complex'/'noncommuting-four-incidence.json'
    data = json.loads(fixture.read_text())
    return general.exact.basis((v >> n) | ((v & ((1 << n)-1)) << n)
                               for v in data['common_lagrangian_basis'])


def price(U, n):
    source, sink = ports(U, n)
    S = [general.inverse_Z_labels(word, n) for word in source]
    T = [general.inverse_Z_labels(word, n) for word in sink]
    capacities = []
    for L in general.all_lagrangians(n):
        capacities.append((sum(distance(A, L, n) for A in S)
                           +sum(distance(L, B, n) for B in T), L))
    minimum = min(c for c, _ in capacities)
    med = median_label(n)
    if distance(S[0], T[1], n) != n or distance(S[1], T[0], n) != n or distance(S[2], T[2], n) != n:
        raise AssertionError('canonical crossed endpoint proof premises failed')
    if minimum != 3*n or any(c < 3*n for c, _ in capacities):
        raise AssertionError('one-common-frame endpoint triangle control failed')
    selected = next(c for c, L in capacities if L == med)
    return dict(all_lagrangians=len(capacities), exact_minimum_rank=minimum,
                minimizing_frames=sum(c == minimum for c, _ in capacities),
                complete_stock=3, capacity=3*n,
                median_total_rank=selected,
                median_helper_path=[distance(S[2], med, n), distance(med, T[2], n)],
                costs_sha256=sha256(json.dumps([(c,list(L)) for c,L in capacities]).encode()).hexdigest(),
                proof='Pair X-source with Y-sink, Y-source with X-sink, helper source with helper sink; each distance is n and both routes pass through the common frame.')


def regrid(values, old, new):
    if new < old:
        raise ValueError('reference never truncates a dyadic grid')
    return [tuple(v << (new-old) for v in row) for row in values]


def compare(A, gridA, B, gridB):
    grid = max(gridA, gridB)
    if regrid(A, gridA, grid) != regrid(B, gridB, grid):
        raise AssertionError('complete canonical physical payload endpoint differs')


def execute_scalar(word, banks):
    banks = [[row for row in bank] for bank in banks]
    for target, source, coefficient in word:
        banks[target] = [tuple(a+coefficient*b for a,b in zip(x,y))
                         for x,y in zip(banks[target], banks[source])]
    return banks


def C_reference(word, values, n):
    columns, grid = [], None
    for x in range(1 << n):
        values_column, bits = general.literal_column(word, n, x)
        grid = bits if grid is None else grid
        if bits != grid:
            raise AssertionError('reference has inconsistent fixed grid')
        columns.append(values_column)
    out = []
    for y in range(1 << n):
        fields = [0,0,0,0]
        for x, row in enumerate(values):
            coefficient = columns[wrappers.column_vector(x,n,1,0)][wrappers.column_vector(y,n,1,0)]
            for pair in (0,2):
                a,b = general.exact.multiply_gaussian(coefficient, row[pair:pair+2])
                fields[pair] += a
                fields[pair+1] += b
        out.append(tuple(fields))
    return out, grid


def compiled_component(raw, incoming, outgoing, word):
    transformed, grids = [], []
    for bank, plan in zip(raw, incoming):
        result, grid = wrappers.execute(plan, bank)
        transformed.append(result)
        grids.append(grid)
    common_grid = max(grids)
    transformed = [regrid(bank, grid, common_grid) for bank,grid in zip(transformed,grids)]
    transformed = execute_scalar(word, transformed)
    output, output_grids = [], []
    for bank, plan in zip(transformed,outgoing):
        result, grid = wrappers.execute(plan, bank)
        output.append(result)
        output_grids.append(common_grid+grid)
    return output, output_grids


def inverse_component(output, grids, incoming, outgoing, word):
    common_grid = max(grids)
    banks = [regrid(bank, grid, common_grid) for bank,grid in zip(output,grids)]
    old_grids, transformed = [], []
    for bank, plan in zip(banks,outgoing):
        result, grid = wrappers.execute(plan, bank, inverse=True)
        transformed.append(result)
        old_grids.append(common_grid+grid)
    common_grid = max(old_grids)
    transformed = [regrid(bank, grid, common_grid) for bank,grid in zip(transformed,old_grids)]
    transformed = execute_scalar(tuple((a,b,-c) for a,b,c in reversed(word)), transformed)
    output, grids = [], []
    for bank, plan in zip(transformed,incoming):
        result, grid = wrappers.execute(plan, bank, inverse=True)
        output.append(result)
        grids.append(common_grid+grid)
    return output, grids


def probe(task):
    U, choice = task
    n = 3
    word = echo_word()
    scalar, largest, prefixes = scalar_matrix(word)
    if scalar != [[0,1,0],[-1,0,0],[0,0,1]]:
        raise AssertionError('one shared arbitrary-dirty helper does not realize signed exchange')
    if scalar_matrix(word[:-1])[0] == scalar:
        raise AssertionError('omitted helper cleanup negative did not reject')
    source, sink = ports(U,n)
    L = general.inverse_Z_labels([],n) if choice == 'identity' else median_label(n)
    common = general.frame_word(L,n)['actual_word']
    words = [general.inverse_word(port)+common for port in source]+[general.inverse_word(common)+port for port in sink]
    normals = [general.compile_word(actual,n) for actual in words]
    plans = [wrappers.wrapper_plan(normal,1) for normal in normals]
    widths = [normal['selected_rank_per_column'] for normal in normals]
    total = sum(widths)
    metrics = price(U,n)
    if total != (3*n if choice == 'identity' else metrics['median_total_rank']):
        raise AssertionError('actual paid interface widths differ from endpoint prices')
    expected_entries = 0
    for actual, normal in zip(words,normals):
        r = normal['selected_rank_per_column']
        for x in range(1 << n):
            values, grid = general.literal_column(actual,n,x)
            for y in range(1 << n):
                expected = general.exact.reconstructed_entry(normal,y,x)
                if values[y] != tuple(v << (grid-r) for v in expected):
                    raise AssertionError('source/sink interface actual phase or route differs')
                expected_entries += 1
    origin_cases = []
    for role in range(3):
        for address in range(1 << n):
            raw = [[(0,0,0,0)]*(1 << n) for _ in range(3)]
            raw[role][address] = (1,2,-3,5)
            origin_cases.append(raw)
    origin_cases.append([[wrappers.routes.payload(24*role+j) for j in range(1 << n)] for role in range(3)])
    checked = inverses = 0
    F = sink[0]
    missing_return_rejected = False
    for raw in origin_cases:
        output, grids = compiled_component(raw,plans[:3],plans[3:],word)
        expectedX, gx = C_reference(F,raw[1],n)
        shifted = wrappers.routes.scatter(raw[0],lambda a:wrappers.replace_column(
            a,wrappers.column_vector(a,n,1,0)^U,n,1,0))
        expectedY, gy = C_reference(F,shifted,n)
        expectedY = [tuple(-v for v in row) for row in expectedY]
        expectedZ, gz = C_reference(F,raw[2],n)
        for A,ga,B,gb in zip(output,grids,(expectedX,expectedY,expectedZ),(gx,gy,gz)):
            compare(A,ga,B,gb)
            checked += 4*(1 << n)
        back, returned_grids = inverse_component(output,grids,plans[:3],plans[3:],word)
        for actual, grid, original in zip(back,returned_grids,raw):
            compare(actual,grid,original,0)
            inverses += 4*(1 << n)
        # A helper left at the common actual frame instead of F is a
        # meaningful wrong physical endpoint on arbitrary dirty inputs.
        if raw[2] != [(0,0,0,0)]*(1 << n):
            wrong, wg = C_reference(common,raw[2],n)
            if regrid(wrong,wg,max(wg,gz)) != regrid(expectedZ,gz,max(wg,gz)):
                missing_return_rejected = True
    if not missing_return_rejected:
        raise AssertionError('omitted final helper F return negative did not discriminate')
    return dict(U=U, common_frame=choice, f=1, n=n, physical_roles=['X','Y','dirty-Z'],
                scalar_word=[list(g) for g in word], scalar_matrix=scalar,
                scalar_prefix_max_row_L1=largest, scalar_prefixes=prefixes,
                actual_source_words=source, actual_sink_words=sink,
                actual_common_word=common, selected_interface_ranks=widths,
                total_paid_rank=total, capacity=3*n, deficit=3*n-total,
                profile_counts={str(r):widths.count(r) for r in sorted(set(widths)) if r},
                exact_source_sink_matrix_entries=expected_entries,
                full_physical_origin_cases=len(origin_cases), forward_fields=checked, inverse_fields=inverses,
                exact_helper_endpoint='C_full * arbitrary initial dirty-Z',
                missing_cleanup_negative=True, missing_helper_return_negative=True,
                helper_path=[widths[2],widths[5]], exact_endpoint_prices=metrics,
                numerical_note='Reference grids are aligned only by zero extension, never truncation. A native execution still requires fixed guarded buffers and active-child precision contracts.',
                scope='One common actual-frame twelve-shear dirty echo. All stock and canonical endpoints paid; no universal multi-frame/helper lower bound.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive worker count required')
    files = [Path(__file__),Path(general.__file__),Path(general.exact.__file__),
             Path(general.exact.reference.__file__),Path(wrappers.__file__),Path(wrappers.routes.__file__)]
    before = {p.name:sha256(p.read_bytes()).hexdigest() for p in files}
    if before[Path(general.__file__).name] != GENERAL_SHA or before[Path(wrappers.__file__).name] != WRAPPER_SHA:
        raise AssertionError('pinned actual-frame/wrapper source changed')
    utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [(1,'identity')] if args.bounded else [(U,choice) for U in (1,7) for choice in ('identity','retained-median')]
    if args.workers == 1:
        cases = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe,tasks))
    if before != {p.name:sha256(p.read_bytes()).hexdigest() for p in files}:
        raise AssertionError('effective source changed during run')
    certificate = dict(status='PASS SCOPED CAPACITY NEGATIVE',started_utc=utc,
                       completed_utc=datetime.now(timezone.utc).isoformat(),effective_sources=before,
                       workers=args.workers,bounded=args.bounded,cases=cases,
                       seconds=time.monotonic()-started,
                       scope='Exact canonical source/sink signed exchange using one genuinely reused dirty helper. One-common-frame architecture has minimum rank3h and cannot yield a positive characteristic saving. Other chronology/nonunit mechanisms remain open.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps(dict(status=certificate['status'],cases=len(cases),
                          ranks=[c['total_paid_rank'] for c in cases],
                          fields=sum(c['forward_fields']+c['inverse_fields'] for c in cases),
                          seconds=certificate['seconds'],scope=certificate['scope'])),flush=True)


if __name__ == '__main__':
    main()
