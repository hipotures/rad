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
    unreviewed = []
    if native_candidates:
        path, row = max(native_candidates, key=lambda item: Fraction(item[1]['safe_saving']))
        candidate = Fraction(row['safe_saving'])*Fraction(99999,100000)
        unreviewed.append(candidate)
        context['current_finite_moment_frontier'] = dict(id=row['id'], saving=row['safe_saving'],
                                                       result=str(path.relative_to(ROOT)),
                                                       scope='Exact finite moment; a new producer still needs independent integration review.')
    joint_candidates = []
    for path in ROOT.glob('work/joint-profile-*/result.json'):
        row = read(path)
        if (row and row.get('status') == 'exact_joint_frozen_pool_search'
                and row.get('dimensions', [23,25]) == [23,25]
                and row.get('candidate_kappa')):
            joint_candidates.append((path, row))
    if joint_candidates:
        path, row = max(joint_candidates, key=lambda item: Fraction(item[1]['candidate_kappa']))
        unreviewed.append(Fraction(row['candidate_kappa']))
        context['current_joint_pool_frontier'] = dict(
            saving=row['saving'], candidate_kappa=row['candidate_kappa'],
            result=str(path.relative_to(ROOT)), pool_sizes=row['pool_sizes'],
            scope='Exact finite original23/25 pool moment; independent native/integration review remains separate.')
    accepted = read(ROOT/'joint-frame/runs/20261008T1854Z-accepted-future-horizon/protocol.json')
    if accepted and accepted.get('status') == 'CONDITIONAL TRANSFER ACCEPTED':
        context['best_reviewed_conditional_kappa'] = accepted['kappa']
        reviewed = Fraction(accepted['kappa'])
        context['candidate_status'] = 'Joint future-horizon/guarded live-reclamation finite witness and 47-row conditional transfer independently accepted under explicit inherited residual, full-payload, owned-copy, fixed-tape, native, analytic/recovery and eligible-prime hypotheses.'
        target = Fraction(accepted['saving'])*Fraction(99999,100000)
        unreviewed.append(target)
        context['open_stronger_cpu_transfer_target'] = dict(kappa=str(target),scope='Arithmetic target only; changed 38-row transfer and complete obligation mapping remain open.')
    new_joint = []
    paths = list(ROOT.glob('joint-frame/agents/scout/results/*complete-moment.json'))
    paths.append(ROOT/'joint-frame/runs/20261008T1854Z-accepted-future-horizon/complete-moment.json')
    for path in paths:
        row=read(path)
        if row and row.get('kappa') and row.get('saving'):
            new_joint.append((path,row))
    strip_cases = []
    duplicate_dags = 0
    seen_words = set()
    repeated_words = 0
    for path in ROOT.glob('work/joint-frame/root/**/result.json'):
        row=read(path)
        if not row:continue
        if row.get('status','').startswith('EXACT DUPLICATE'):
            duplicate_dags += 1
        elif row.get('safe_saving'):
            digest = row.get('word_sha256')
            if digest and digest in seen_words:
                repeated_words += 1
                continue
            if digest:
                seen_words.add(digest)
            strip_cases.append((path,row))
    context['completed_experiments']['new_joint_complete_independent_moments']=len(new_joint)
    context['completed_experiments']['new_strip_complete_word_profiles']=len(strip_cases)
    context['completed_experiments']['new_strip_exact_duplicate_dags_skipped']=duplicate_dags
    context['completed_experiments']['new_joint_repeated_physical_words_excluded']=repeated_words
    if new_joint:
        path,row=max(new_joint,key=lambda item:Fraction(item[1]['kappa']))
        unreviewed.append(Fraction(row['kappa']))
        context['current_joint_frame_frontier']=dict(saving=row['saving'],candidate_kappa=row['kappa'],
            W=row['controller']['W'],rank_mass=row['controller']['total_rank'],
            wrapped_scalar_xors=row['controller']['wrapped_scalar_xors'],result=str(path.relative_to(ROOT)),
            scope=('Finite word, rational profiles, complete moment and explicit framed dirty/adjoint conditional transfer accepted under named inherited contracts.' if accepted and row['kappa']==accepted['kappa'] else 'Finite word/rational profiles/moment and inherited47-row arithmetic PASS; mechanism-specific all-size review remains separate.'))
    context['best_unverified_kappa'] = str(max(unreviewed)) if unreviewed and max(unreviewed) > reviewed else None
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
