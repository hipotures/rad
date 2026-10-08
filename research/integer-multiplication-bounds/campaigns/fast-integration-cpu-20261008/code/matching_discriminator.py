#!/usr/bin/env python3
"""Changed-component experiment: choose continuations by native moment cost.

Uses pinned icekylinx PR36 scalar/positive-label producers, Apache-2.0.
All output paths are fresh. No predecessor file or downloaded source is edited.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import importlib
import json
from pathlib import Path
import subprocess
import sys
import time


def run_case(case):
    source, program, work, h, mode, seed = case
    source, work = Path(source), Path(work)
    sys.path.insert(0, str(source / 'scripts'))
    from partial_swap.graph import graph, export
    from partial_swap.positive import run as positive_labels
    case_dir = work / f'h{h}-mode{mode}-seed{seed}'
    case_dir.mkdir(parents=True, exist_ok=False)
    begin = time.monotonic()
    circuit = graph(h)
    scalar = circuit.verify()
    dag = case_dir / 'graph.bin'
    export(circuit, dag)
    circuit.support_in.cache_clear()
    del circuit
    with (case_dir / 'envelope.log').open('w') as log:
        envelope = json.loads(subprocess.check_output([str(work / 'envelope'), str(dag), str(dag)+'.links'], stderr=log, text=True))
    labels = positive_labels(str(dag))
    with (case_dir / 'matching.log').open('w') as log:
        changed = json.loads(subprocess.check_output([program, str(dag), str(dag)+'.positive', str(mode), str(seed), '0.00003850919324'], stderr=log, text=True))
    assert changed['matched'] == envelope['matched']
    assert changed['loss'] == h*(h-1)
    hist = changed['histogram']
    assert sum(r*n for r,n in enumerate(hist)) == h*changed['R']+2*changed['loss']
    assert hist[h] >= h
    hist = list(hist)
    hist[1] += h
    hist[h] -= h
    assert sum(r*n for r,n in enumerate(hist)) == h*changed['R']+changed['loss']
    result = {'h':h, 'mode':mode, 'seed':seed, 'envelope':envelope,
              'changed':changed, 'copied_histogram':hist, 'scalar':scalar,
              'labels':labels, 'elapsed_seconds':time.monotonic()-begin,
              'scope':'Maximum cardinality and local rank identities; full finite tape and corner transfer remain separate.'}
    (case_dir / 'result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--modes', nargs='+', type=int, default=[0,1,2,4])
    parser.add_argument('--seeds', nargs='+', type=int, default=[20261008])
    parser.add_argument('--dimensions', nargs='+', type=int, default=[23,25])
    args = parser.parse_args()
    assert 1 <= args.workers <= 12
    source, work = args.source.resolve(), args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    code = Path(__file__).resolve().parent
    subprocess.run(['c++','-O3','-std=c++17',str(code/'moment_matching.cpp'),'-o',str(work/'weighted')], check=True)
    subprocess.run(['c++','-O3','-std=c++17',str(source/'scripts/partial_swap/match_exported_dag.cpp'),'-o',str(work/'envelope')], check=True)
    jobs = [(str(source), str(work/'weighted'), str(work), h, mode, seed)
            for h in args.dimensions for mode in args.modes for seed in args.seeds]
    results = []
    start = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed(pool.submit(run_case, job) for job in jobs):
            result = future.result()
            results.append(result)
            print(json.dumps({key:result[key] for key in ('h','mode','seed','elapsed_seconds')}), flush=True)
    out = {'input_commit':'11817ccacb564bb7f98789c20dc11d3fece207e3',
           'mechanism':'Native factor moment traversal under unchanged positive labels and maximal cardinality.',
           'workers':args.workers,'elapsed_seconds':time.monotonic()-start,
           'cases':sorted(results,key=lambda r:(r['h'],r['mode'],r['seed']))}
    args.output.write_text(json.dumps(out,indent=2)+'\n')


if __name__ == '__main__':
    main()
