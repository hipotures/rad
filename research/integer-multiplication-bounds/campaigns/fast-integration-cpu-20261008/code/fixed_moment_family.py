#!/usr/bin/env python3
"""Exact full-controller searches on explicitly matched fixed I+J profiles.

One worker profiles independent DAGs sequentially while producer jobs continue.
The inherited complete geometry is ordered (23,25); other dimensions need a
separate physical construction and are not accepted by this runner.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text())


def safe_search(score, counts, denominator=10**16, margin_ticks=1000):
    low, high = 0, 10**12
    while high-low > 1:
        middle = (low+high)//2
        row = score.moment(counts['m'], counts['W'], counts['child_multiplicities'],
                           Fraction(middle, denominator))
        if row['strictly_passes']:
            low = middle
        else:
            high = middle
    saving = Fraction(low-margin_ticks, denominator)
    assert saving > 0
    result = score.moment(counts['m'], counts['W'], counts['child_multiplicities'], saving)
    assert result['strictly_passes']
    return dict(grid_denominator=denominator, margin_ticks=margin_ticks,
                lower_grid_tick=low, upper_grid_tick=high,
                safe_saving=str(saving), verified_moment=result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dags', required=True, type=Path)
    parser.add_argument('--profiler', required=True, type=Path)
    parser.add_argument('--second', '--partner', dest='partner', required=True, type=Path)
    parser.add_argument('--axis', choices=['first','second'], default='first')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--limit', type=int, default=16)
    parser.add_argument('--previous', action='append', type=Path, default=[])
    parser.add_argument('--diverse', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    helper = ROOT/'agents/scout/code/fixed_controller_score.py'
    spec = importlib.util.spec_from_file_location('fixed_score', helper)
    score = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(score)
    partner = read_json(args.partner)
    expected_dimension = 23 if args.axis == 'first' else 25
    rows = [r for r in read_json(args.dags/'results.json')
            if r['h']==expected_dimension and not r.get('duplicate_exact_dag') and 'original_matching' in r]
    rows.sort(key=lambda r: (r['original_matching']['R'], r['id']))
    previous = {read_json(p)['id'] for directory in args.previous for p in directory.glob('h*.json')}
    # Exclude queued IDs as well as completed results to prevent concurrent duplicate profiling.
    for directory in args.previous:
        protocol_path = directory/'protocol.json'
        if protocol_path.exists():
            previous.update(read_json(protocol_path).get('inputs', []))
    rows = [row for row in rows if row['id'] not in previous]
    if args.diverse:
        buckets = {}
        for row in rows:
            buckets.setdefault((row['threshold'],row['association']),[]).append(row)
        rows = []
        while any(buckets.values()):
            for key in sorted(buckets):
                if buckets[key]:
                    rows.append(buckets[key].pop(0))
    # Keep different original histograms and tree/grouping structures. Mirror
    # circuits with identical grouping reversal and association are screened.
    seen, selected = set(), []
    for row in rows:
        signature = (row['threshold'], row['association'],
                     min(tuple(row['grouping']), tuple(reversed(row['grouping']))),
                     tuple(row['original_matching']['histogram']))
        if signature in seen:
            continue
        seen.add(signature)
        selected.append(row)
        if len(selected) >= args.limit:
            break
    protocol = dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    worker_pid=os.getpid(), inputs=[r['id'] for r in selected],
                    previous_runs=[str(p) for p in args.previous], selection='diverse' if args.diverse else 'low-roles',
                    wrapper_source=Path(__file__).read_text(),
                    input_partner=str(args.partner), axis=args.axis,
                    partner_sha256=hashlib.sha256(args.partner.read_bytes()).hexdigest(),
                    wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    score_sha256=hashlib.sha256(helper.read_bytes()).hexdigest(),
                    profiler=str(args.profiler), profiler_sha256=hashlib.sha256(args.profiler.read_bytes()).hexdigest(),
                    envelope='ORIGINAL matching only', native_geometry='ordered23/25 inherited data families',
                    scope='Exact finite controller arithmetic; semantic finite compiler and all-size integration require review.')
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    for row in selected:
        began = time.time()
        dag = args.dags/row['dag_file']
        fixed_path = Path(str(dag)+'.fixed_ij_profiles.json')
        reused = fixed_path.exists()
        if not reused:
            with (args.output/(row['id']+'.log')).open('w') as log:
                subprocess.run([str(args.profiler), str(dag), str(dag)+'.fixed.links'],
                               stdout=log, stderr=log, check=True)
        first = read_json(fixed_path)
        assert all(first[key] == row['original_matching'][key]
                   for key in ('h','v','R','loss','rank_sum'))
        counts = score.profile(first, partner) if args.axis=='first' else score.profile(partner, first)
        exact = safe_search(score, counts)
        result = dict(id=row['id'], dag_sha256=hashlib.sha256(dag.read_bytes()).hexdigest(),
                      fixed_profile=first, partner_profile=partner, axis=args.axis,
                      complete_controller=score.jsonable(counts), **exact,
                      reference_moment=score.moment(counts['m'],counts['W'],counts['child_multiplicities'],score.REFERENCE_A),
                      scope=protocol['scope'], existing_profile_reused=reused, elapsed_seconds=time.time()-began)
        (args.output/(row['id']+'.json')).write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(dict(event='complete_fixed_controller',pid=os.getpid(),id=row['id'],
                              safe_saving=exact['safe_saving'],seconds=result['elapsed_seconds'])),flush=True)


if __name__ == '__main__':
    main()
