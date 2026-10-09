#!/usr/bin/env python3
"""Bounded physical controls for separately scoped component words.

These checks preserve arbitrary dirty endpoints and actual common operators.
They never infer a multiplier exponent from a component rank histogram.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys


def outer_interfaces():
    p = importlib.import_module('outer_axis_frame_splice')
    cases = []
    h = 3
    n = h * h
    for s, t in ((1, 1), (1, 7), (7, 1), (7, 7)):
        full = tuple(1 << j for j in range(n))
        es = tuple(p.tensor_direction(s, 1 << j, h) for j in range(h))
        et = tuple(p.tensor_direction(1 << i, t, h) for i in range(h))
        u = p.tensor_direction(s, t, h)
        phi = p.convolution_frame(n, et, True, p.convolution_frame(n, full))
        source = p.convolution_frame(n, es, True, p.apply_line(phi, u))
        sink = p.apply_line(p.convolution_frame(n, es, True, phi), u)
        if source != sink:
            raise AssertionError('Broad source/sink operators differ')
        normal = p.normal_form(source, p.perp(es + et, n), n, False)
        background = p.normal_form(phi, p.perp(et, n), n, False)
        if normal['child_width'] != 4 or background['child_width'] != 6:
            raise AssertionError('Two-axis child or background rank changed')
        for form in (normal, background):
            for key in ('output_columns', 'input_columns'):
                routed = {p.image(form[key], a) for a in range(1 << n)}
                if routed != set(range(1 << n)):
                    raise AssertionError('A complete spectator router is not a permutation')
        if p.convolution_frame(n, es, True, phi) == source:
            raise AssertionError('Omitted line correction was not detected')
        cases.append(dict(labels=[s, t], broad=normal, background=background,
                          complete_convolution_coefficients=1 << n,
                          complete_router_images=4 * (1 << n),
                          omitted_line_correction_detected=True))
    return dict(cases=cases, scope='Complete small convolution kernels, all active child coefficients and all spectator router images. Full physical matrix entries follow from convolution and the exact routing identities; this bounded check does not serialize all matrix entries or compose a full master word.')


def check(kind):
    if kind == 'two-axis':
        return outer_interfaces()
    if kind == 'native-exchanges':
        p = importlib.import_module('literal_bank_exchange_control')
        rows = [p.probe((3, 3, basis, exchange)) for basis in ('sum', 'side')
                for exchange in ('literal', 'signed-shears')]
        if any(row['exact_zero_full_rank_optimum'] != 18 for row in rows):
            raise AssertionError('The fixed exchange control changed its exact minimum')
        return dict(cases=rows, scope='Complete finite physical operators and the zero/full metric optimum for these four fixed no-helper words; no general circuit lower bound.')
    if kind == 'closed-side':
        p = importlib.import_module('closed_center_side_splice')
        row = p.probe(('orthogonal-color', 3, 1, 'all-columns'))
        if row['full_materialization_ledger']['deficit'] >= 0:
            raise AssertionError('Closed side materialization unexpectedly has rank saving')
        return dict(cases=[row], scope=row['limitation'])
    if kind == 'geodesic-side':
        p = importlib.import_module('geodesic_edge_side_splice')
        row = p.probe(('physical', 3, 1, 1))
        return dict(cases=[row], scope='Complete orthogonal-color physical columns and dirty cleanup. This coordinate case alone does not validate generic nonconvolution representatives or a canonical primitive.')
    if kind == 'canonical-geodesic':
        p = importlib.import_module('canonical_geodesic_side_review')
        row = p.probe((4, 1, False, True))
        if row['explicit_initial_columns'] != 384 or not row['per_gate_covariance_shortcut_rejected']:
            raise AssertionError('Generic actual-frame coverage or corruption control changed')
        return dict(cases=[row], scope=row['scope'])
    if kind == 'tensor-preflight':
        p = importlib.import_module('tensor_center_side_preflight')
        return p.verify()
    if kind == 'geodesic-moment':
        p = importlib.import_module('certify_geodesic_edge_moment')
        path = Path(__file__).resolve().parents[2] / 'runs/20261009T014025Z-synthesis-geodesic-edge-side/results/certificate.json'
        data = json.loads(path.read_text())
        rows = [p.certify(case['rank_ledger']) for case in data['cases'] if case['kind'] == 'rank']
        if sorted(row['h'] for row in rows) != [9, 12, 16]:
            raise AssertionError('Pinned abstract profile coverage changed')
        return dict(input_path=str(path.relative_to(path.parents[3])),
                    input_sha256=sha256(path.read_bytes()).hexdigest(),
                    cases=p.intervals.serializable(rows),
                    scope='Exact conditional moments for the three retained abstract side ledgers; no canonical primitive or multiplier exponent.')
    if kind == 'source-cycle':
        p = importlib.import_module('source_cycle_echo_search')
        path = Path(__file__).resolve().parents[2] / 'runs/20261009T005332Z-synthesis-source-cycle-echo/results/summary.json'
        data = json.loads(path.read_text())
        rows = []
        n = m = 3
        f = p.dp.f
        zero, full = f.le((), n), f.le((1, 2, 4), n)
        starts = [f.le((1 << j,), n) for j in range(m)] + [zero] * m
        ends = [full] * m + [f.le(f.perpendicular((1 << j,), n), n) for j in range(m)]
        for case in data['cases']:
            word = p.operations(case['topology'])
            scalar = p.scalar_columns(word, m)
            p.scalar_columns(word, m, True)
            shears = [(e[1], e[2], e[3]) for e in word if e[0] == 'add']
            frames = f.lagrangians(n) if case['frame_kind'] == 'all-Lagrangian' else [f.le(e, n) for e in f.subspaces(n)]
            frames = sorted(frames)
            assignment = case['exact_min_sum']['assignment']
            if len(assignment) != len(shears):
                raise AssertionError('Frozen source-cycle assignment length changed')
            current = list(starts)
            histogram = Counter()
            for (a, b, _), frame_id in zip(shears, assignment):
                frame = frames[frame_id]
                for role in (a, b):
                    distance = f.distance(current[role], frame, n)
                    if distance:
                        histogram[distance] += 1
                    current[role] = frame
            for before, after in zip(current, ends):
                distance = f.distance(before, after, n)
                if distance:
                    histogram[distance] += 1
            if sum(width * count for width, count in histogram.items()) != 18:
                raise AssertionError('Frozen source-cycle witness charge changed')
            if dict(histogram) != {int(k): v for k, v in case['chronological_histogram'].items()}:
                raise AssertionError('Frozen complete source-cycle histogram changed')
            rows.append(dict(topology=case['topology'], frame_kind=case['frame_kind'],
                             scalar_columns=scalar, witness_histogram=dict(histogram),
                             witness_charge=18))
        if len(rows) != 4:
            raise AssertionError('Frozen source-cycle coverage changed')
        return dict(input_sha256=sha256(path.read_bytes()).hexdigest(), cases=rows,
                    scope='Complete scalar source/sink identity and retained assignment replay in four domains. The expensive finite minimum is not recomputed by this bounded check.')
    raise ValueError('Unknown component check')


def loaded_sources():
    root = Path(__file__).resolve().parents[1]
    paths = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.suffix == '.py' and path.is_relative_to(root):
                paths.add(path)
        # The trimmed side generator uses importlib without a sys.modules
        # registration; its actual source is a separate runtime dependency.
        dynamic = getattr(module, 'SIDE_SOURCE', None)
        if isinstance(dynamic, Path) and dynamic.resolve().is_relative_to(root):
            paths.add(dynamic.resolve())
    return sorted(paths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True, choices=('two-axis', 'native-exchanges',
                        'closed-side', 'geodesic-side', 'canonical-geodesic', 'tensor-preflight',
                        'geodesic-moment', 'source-cycle'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    modules = {'two-axis': 'outer_axis_frame_splice',
               'native-exchanges': 'literal_bank_exchange_control',
               'closed-side': 'closed_center_side_splice',
               'geodesic-side': 'geodesic_edge_side_splice',
               'canonical-geodesic': 'canonical_geodesic_side_review',
               'tensor-preflight': 'tensor_center_side_preflight',
               'geodesic-moment': 'certify_geodesic_edge_moment',
               'source-cycle': 'source_cycle_echo_search'}
    importlib.import_module(modules[args.case])
    root = Path(__file__).resolve().parents[1]
    hashes = {str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
              for path in loaded_sources()}
    result = check(args.case)
    if any(sha256((root / name).read_bytes()).hexdigest() != digest
           for name, digest in hashes.items()):
        raise ValueError('An effective source changed during component replay')
    receipt = dict(status='PASS BOUNDED COMPONENT WORD', case=args.case,
                   started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(),
                   source_sha256=hashes, result=result,
                   multiplier_exponent_established=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(receipt, indent=2, default=str) + '\n')
    print(json.dumps(dict(status=receipt['status'], case=args.case,
                          loaded_source_files=len(hashes), multiplier_exponent_established=False)))


if __name__ == '__main__':
    main()
