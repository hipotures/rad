#!/usr/bin/env python3
"""Bounded exact dirty-echo and serial/parallel elimination checks.

The compiler is a prerequisite; binaries and graph tables are disposable.
This entrypoint does not repeat the 135-label width-four experiment. It
checks the retained source patch, exhaustive finite-factor controls, scalar
columns, exact small-domain optima, reconstructed paths and rejection guards.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import tempfile

import dirty_color_echo_dp as dp
import dirty_color_echo_full_dp as parallel
from frame_factor_guards import guard_graph

FULL_FIXTURE = Path(__file__).resolve().parents[2] / 'fixtures/synthesis/dirty-center-full-preflight.json'


def compile_kernels(work, cxx):
    serial = work / 'serial'
    command = [cxx, '-O3', '-std=c++17', str(dp.CPP), '-o', str(serial)]
    subprocess.run(command, check=True, text=True, capture_output=True)
    patched = work / 'parallel.cpp'
    subprocess.run(['patch', '-o', str(patched), str(dp.CPP), str(parallel.PATCH)],
                   check=True, text=True, capture_output=True)
    native = work / 'parallel'
    subprocess.run([cxx, '-O3', '-std=c++17', '-fopenmp', str(patched),
                    '-o', str(native)], check=True, text=True, capture_output=True)
    return serial, native, sha256(patched.read_bytes()).hexdigest()


def rejection_controls(binary, work):
    # The first exhaustive control's graph is valid and has three variables.
    values = list(map(int, (work / 'controls/control-0/graph.txt').read_text().split()))
    variants = {
        'truncated_input': values[:-1],
        'duplicate_elimination_variable': values[:-1] + [values[-2]],
        'predeclared_factor_storage': values[:3] + [0] + values[4:],
    }
    receipts = []
    for name, fields in variants.items():
        path = work / (name + '.txt')
        path.write_text(' '.join(map(str, fields)) + '\n')
        result = subprocess.run([str(binary), str(path)], text=True, capture_output=True)
        if result.returncode == 0:
            raise ValueError('Invalid exact graph input was accepted: ' + name)
        receipts.append(dict(name=name, rejection=result.stderr.strip()))
    return receipts


def verify(work, cxx):
    serial, native, generated_hash = compile_kernels(work, cxx)
    old_solve = dp.solve
    def guarded_serial(binary, directory, edges, unary, table, constant=0, order=None):
        guard_graph(edges, unary, table, constant, order)
        return old_solve(binary, directory, edges, unary, table, constant, order)
    try:
        dp.solve = guarded_serial
        control = dp.controls(serial, work / 'controls')
        rejects = rejection_controls(serial, work)
        cases = []
        for index, spec in enumerate([
                (2, 2, 'all-Lagrangian', 'center-first'),
                (3, 3, 'L_E', 'side-inside')]):
            result = dp.probe((*spec, serial, work / f'case-{index}'))
            if result['minimum_rank_charge'] != result['capacity']:
                raise ValueError('Retained exact bounded dirty-echo optimum changed')
            cases.append({key: value for key, value in result.items()
                          if key not in ('complete_frames', 'word')})
    finally:
        dp.solve = old_solve
    # Test the exact parallel patch independently on the same exhaustive
    # factor suite; each native receipt is replayed by Python in full_solve.
    old_threads = os.environ.get('OMP_NUM_THREADS')
    old_dynamic = os.environ.get('OMP_DYNAMIC')
    try:
        def guarded_parallel(binary, directory, edges, unary, table, constant=0, order=None):
            guard_graph(edges, unary, table, constant, order)
            return parallel.full_solve(binary, directory, edges, unary, table, constant, order)
        dp.solve = guarded_parallel
        os.environ['OMP_NUM_THREADS'] = '2'
        os.environ['OMP_DYNAMIC'] = 'FALSE'
        parallel_controls = dp.controls(native, work / 'parallel-controls')
        semantics = lambda receipt: (receipt['seed'], receipt['assignments_each'],
                                      [(case['case'], case['optimum']) for case in receipt['cases']])
        # Distinct storage caps are retained in their graph input headers,
        # so the input SHA must differ while the finite objective agrees.
        if semantics(parallel_controls) != semantics(control):
            raise ValueError('Serial/parallel exhaustive finite-factor controls differ')
    finally:
        dp.solve = old_solve
        for name, value in [('OMP_NUM_THREADS', old_threads), ('OMP_DYNAMIC', old_dynamic)]:
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
    # The full enumeration is small; validity/completeness are independent
    # of running the large variable-elimination instance.
    frames = dp.f.lagrangians(3)
    if len(frames) != 135 or len(set(frames)) != 135:
        raise ValueError('Complete three-bit frame domain changed')
    if any(len(F) != 3 or any(dp.f.pairing(a, b, 3) for a in F for b in F)
           for F in frames):
        raise ValueError('The complete frame domain contains an invalid Lagrangian')
    estimate = parallel.preflight()
    if estimate['candidate_cost_evaluations'] != 271374460110:
        raise ValueError('Full-case graph/order evaluation preflight changed')
    if estimate['peak_factor_and_decision_bytes'] != 5353959600:
        raise ValueError('Full-case exact payload preflight changed')
    fixture = json.loads(FULL_FIXTURE.read_text())
    if generated_hash != fixture['generated_parallel_source_sha256']:
        raise ValueError('Parallel source differs from the completed full-case source')
    n = m = 3
    word = dp.scalar_word(m, 'side-inside')
    zero = dp.f.le((), n)
    full = dp.f.le((1, 2, 4), n)
    starts = [dp.f.le((1 << j,), n) for j in range(m)] + [zero] * (m + 1)
    ends = [full] * m + [dp.f.le(dp.f.perpendicular((1 << j,), n), n)
                         for j in range(m)] + [full]
    table = [[dp.f.distance(a, b, n) for b in frames] for a in frames]
    ids = {F: j for j, F in enumerate(frames)}
    edges, boundaries, constant = dp.f.incidence_graph(word, 7, starts, ends)
    unary = [[sum(table[j][ids[F]] for F in boundary) for j in range(len(frames))]
             for boundary in boundaries]
    guard = guard_graph(edges, unary, table, constant, estimate['order'])
    if guard['global_nonnegative_charge_bound'] != fixture['global_nonnegative_cost_bound']:
        raise ValueError('Full-case guarded nonnegative charge bound changed')
    fields = [len(word), len(frames), constant, parallel.FACTOR_MAX_ENTRIES]
    fields += [x for row in table for x in row] + [x for row in unary for x in row]
    fields += [len(edges)] + [x for edge in edges for x in edge] + estimate['order']
    full_input_hash = sha256((' '.join(map(str, fields)) + '\n').encode()).hexdigest()
    if full_input_hash != fixture['graph_input_sha256']:
        raise ValueError('Full finite instance differs from the completed input')
    if dp.f.energy(fixture['assignment'], edges, unary, lambda a, b: table[a][b], constant) != fixture['minimum_rank_charge']:
        raise ValueError('Completed full-domain backtracking witness is corrupted')
    guard_negatives = []
    for name, costs, distances, offset, elimination in [
            ('negative_unary', [[-1, 0]], [[0, 1], [1, 0]], 0, [0]),
            ('oversized_distance', [[0, 0]], [[0, 65535], [1, 0]], 0, [0]),
            ('negative_constant', [[0, 0]], [[0, 1], [1, 0]], -1, [0]),
            ('overflow_total', [[32768, 32768], [32768, 32768]], [[0, 1], [1, 0]], 0, [0, 1]),
            ('invalid_order', [[0, 0]], [[0, 1], [1, 0]], 0, [1])]:
        try:
            guard_graph([], costs, distances, offset, elimination)
        except ValueError as error:
            guard_negatives.append(dict(name=name, rejection=str(error)))
        else:
            raise ValueError('Malformed finite factor was not rejected: ' + name)
    return dict(status='PASS BOUNDED EXACT ECHO ELIMINATION',
                recorded_utc=datetime.now(timezone.utc).isoformat(),
                compiler=subprocess.run([cxx, '--version'], check=True, text=True,
                                        capture_output=True).stdout.splitlines()[0],
                generated_parallel_source_sha256=generated_hash,
                exhaustive_factor_controls=control, parallel_factor_controls=parallel_controls,
                rejection_controls=rejects, cases=cases,
                factor_guard_controls=guard_negatives,
                full_case_input_sha256=full_input_hash,
                full_case_nonnegative_bound=guard,
                all_three_bit_frames=135,
                full_case_preflight=dict(candidate_cost_evaluations=estimate['candidate_cost_evaluations'],
                                        peak_factor_and_decision_bytes=estimate['peak_factor_and_decision_bytes']),
                scope='Exact bounded finite factors and specified dirty scalar/frame words; full 135-frame domain is validated but the large width-four minimum is not rerun here. Gaussian operator lifts, tape movement, precision and multiplier recurrence remain separate.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--cxx', default='c++')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='rad-echo-check-') as temporary:
        result = verify(Path(temporary), args.cxx)
    paths = [Path(__file__), Path(dp.__file__), Path(parallel.__file__), dp.CPP,
             parallel.PATCH, Path(__file__).with_name('frame_factor_guards.py'),
             FULL_FIXTURE, Path(dp.f.__file__),
             Path(dp.f.__file__).with_name('lagrangian_graph_completion.py'),
             Path(dp.f.__file__).with_name('trimmed_zeta_dirty_probe.py'), dp.f.SIDE_SOURCE]
    result['source_sha256'] = {path.name: sha256(path.read_bytes()).hexdigest() for path in paths}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], exact_cases=len(result['cases']),
                          exhaustive_assignments=16 * 64, parallel_control_cases=16)))


if __name__ == '__main__':
    main()
