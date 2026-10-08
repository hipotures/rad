#!/usr/bin/env python3
"""Rebuild an actual-frame profile from a freshly recovered DAG, labels and map.

Scalar DAG/frame/map generation belongs to the graph recovery driver. This gate
requires all three regenerated inputs to agree with the selected finite witness,
then compiles the projector code, profiles every physical transition, and runs
the separate literal graph compiler. It never substitutes original envelopes.
"""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

from run_positive_profiles import run


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dag', type=Path, required=True)
    parser.add_argument('--selected', type=Path, required=True)
    parser.add_argument('--expected', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-receipt', type=Path)
    parser.add_argument('--profiler-source', type=Path)
    parser.add_argument('--compiler', type=Path)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    assert not sys.flags.optimize
    args.work.mkdir(parents=True)
    expected = json.loads(args.expected.read_text())
    producer = expected['producer']
    labels = Path(str(args.dag)+'.positive')
    assert digest(args.dag) == producer['dag_sha256']
    assert digest(labels) == producer['positive_sha256']
    fresh = json.loads(args.selected.read_text())
    pinned = expected['selected_links']
    assert fresh['h'] == pinned['h'] == producer['h']
    assert fresh['n'] == pinned['n']
    assert sorted(map(tuple, fresh['links'])) == sorted(map(tuple, pinned['links']))
    assert len(fresh['links']) == producer['matched']
    assert len({x for x, _ in fresh['links']}) == len(fresh['links'])
    assert len({u for _, u in fresh['links']}) == len(fresh['links'])
    # Preserve the frozen witness's harmless ordering/metadata after checking the
    # freshly generated selected map; native physical execution is deterministic.
    selected = args.work/'selected-uses.json'
    selected.write_text(json.dumps(pinned)+'\n')
    input_path = args.work/'input.json'
    row = dict(producer, dag_path=str(args.dag), witness_path=str(selected),
               witness_sha256=digest(selected))
    input_path.write_text(json.dumps(dict(producer=row))+'\n')
    basis = expected['fixed_profile']['basis']
    filename = ('parameter_positive_profiles.cpp' if basis.startswith('beta:')
                else 'positive_transpose_profiles.cpp' if basis.endswith('-transpose')
                else 'positive_frame_profiles.cpp')
    source = args.profiler_source or Path(__file__).with_name(filename)
    assert digest(source) == expected['provenance']['authored_source_sha256']
    binary = args.work/'profiler'
    env = dict(os.environ)
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[key] = '1'
    build = [env.get('CXX', 'c++'), '-O3', '-std=c++17', str(source), '-o', str(binary)]
    subprocess.run(build, check=True, env=env)
    result_path = args.work/'recovered-profile.json'
    run(input_path, binary, basis, args.work/'profile', result_path, authored_source=source)
    result = json.loads(result_path.read_text())
    assert result['copied_blocks'] == expected['copied_blocks']
    for key in ('h', 'v', 'R', 'matched', 'loss', 'rank_sum', 'rank_histogram', 'blocks'):
        assert result['fixed_profile'][key] == expected['fixed_profile'][key], key
    compiler = args.compiler or Path(__file__).resolve().parents[2]/'graph/code/check_compiled_witness.py'
    assert compiler.exists()
    compiled = args.work/'literal-compiler.json'
    command = [sys.executable, str(compiler), '--witness', str(result_path), '--output', str(compiled)]
    subprocess.run(command, check=True, env=env)
    receipt = dict(status='PASS FRESH ACTUAL FRAME PROFILE AND LITERAL COMPILER RECOVERY',
                   utc=datetime.now(timezone.utc).isoformat(), h=producer['h'], basis=basis,
                   expected_sha256=digest(args.expected), regenerated_dag_sha256=digest(args.dag),
                   regenerated_labels_sha256=digest(labels), regenerated_selected_sha256=digest(args.selected),
                   pinned_selected_sha256=digest(selected), build_command=build, source_sha256=digest(source),
                   binary_sha256=digest(binary), profile=str(result_path), profile_sha256=digest(result_path),
                   compiler_command=command, compiler_receipt=str(compiled), compiler_sha256=digest(compiled),
                   copied_rank_mass=sum(i*n for i, n in enumerate(result['copied_blocks'])),
                   source_receipt=str(args.source_receipt) if args.source_receipt else None,
                   source_receipt_sha256=digest(args.source_receipt) if args.source_receipt else None,
                   scope='Graph source recovery is a prerequisite; this gate rebuilds all exact matrices and literal chronology. Full multiplication assembly is separate.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2)+'\n')
    print(receipt['status'], flush=True)


if __name__ == '__main__':
    main()
