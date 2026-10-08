#!/usr/bin/env python3
"""Refresh scientific completion counts without changing the reviewed result.

Parameter-grid combinations, prefix operations and experiment configurations
have different units and are reported separately. Partial JSON writes are
ignored until their complete object is available on the next observation.
"""
import argparse
import datetime
from fractions import Fraction
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def refresh():
    context_path = ROOT/'results/live-compute-context.json'
    context = read(context_path)
    if context is None:
        return
    configs = unique = completed_configs = completed_unique = 0
    for directory in ROOT.glob('work/changed-dag-*'):
        rows = read(directory/'results.json')
        if not isinstance(rows, list):
            continue
        configs += len(rows)
        hashes = {row.get('dag_sha256') for row in rows if row.get('dag_sha256')}
        unique += len(hashes)
        if (directory/'summary.json').exists():
            completed_configs += len(rows)
            completed_unique += len(hashes)
    moments = []
    for path in ROOT.glob('work/fixed-moment-*/h*.json'):
        row = read(path)
        if row and row.get('safe_saving'):
            moments.append((path, row))
    ordered = []
    for pattern in ('work/dag-orders-h*/h*.json', 'work/dag-orders-serial-*/step*/h*.json'):
        for path in ROOT.glob(pattern):
            row = read(path)
            if row and row.get('safe_saving'):
                ordered.append((path,row))
    weighted = []
    for path in ROOT.glob('work/scout/weighted*/**/axis*-seed*-noise*.json'):
        row = read(path)
        if row and row.get('safe_saving') and not row.get('duplicate_matching'):
            weighted.append((path,row))
    optimistic = []
    for path in ROOT.glob('work/optimistic-geometry-*/h*.json'):
        row = read(path)
        if row and row.get('safe_saving'):
            optimistic.append((path,row))
    context['completed_experiments']['changed_dag_configured_rows_observed'] = configs
    context['completed_experiments']['changed_dag_unique_hashes_observed'] = unique
    context['completed_experiments']['changed_dag_completed_generator_rows'] = completed_configs
    context['completed_experiments']['changed_dag_unique_complete_profiles'] = completed_unique
    context['completed_experiments']['complete_original_fixed_controller_profiles'] = len(moments)
    context['completed_experiments']['complete_ordered_leaf_controller_profiles'] = len(ordered)
    context['completed_experiments']['complete_distinct_weighted_matching_trials'] = len(weighted)
    context['completed_experiments']['complete_optimistic_geometry_profiles'] = len(optimistic)
    context['completed_parameter_combinations'] = 5501124
    context['complete_rounded_prefix_combinations'] = 3932160
    context['count_units'] = 'Parameter grid tuples, rounded prefix operations and configured experiment rows are separate counts.'
    reviewed = Fraction(context['best_reviewed_conditional_kappa'])
    native_candidates = moments+ordered+weighted
    if native_candidates:
        path, row = max(native_candidates, key=lambda item: Fraction(item[1]['safe_saving']))
        candidate = Fraction(row['safe_saving'])*Fraction(99999,100000)
        context['best_unverified_kappa'] = str(candidate) if candidate > reviewed else None
        context['current_finite_moment_frontier'] = dict(id=row['id'], saving=row['safe_saving'],
                                                       result=str(path.relative_to(ROOT)),
                                                       scope='Exact finite moment; a new producer still needs independent integration review.')
    if optimistic:
        path,row = max(optimistic,key=lambda item: Fraction(item[1]['safe_saving']))
        context['best_optimistic_geometry_saving'] = dict(saving=row['safe_saving'],result=str(path.relative_to(ROOT)),
                                                        scope='Coalesced data lower-cost screen; no actual geometry or kappa certificate.')
    context['metrics_updated_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    temporary = context_path.with_suffix('.tmp')
    temporary.write_text(json.dumps(context, indent=2)+'\n')
    temporary.replace(context_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    while True:
        refresh()
        if args.once:
            return
        time.sleep(60)


if __name__ == '__main__':
    main()
