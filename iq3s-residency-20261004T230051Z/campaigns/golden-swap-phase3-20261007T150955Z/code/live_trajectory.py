"""Audit publication chronology from event/time state, never admission-vector order."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import numpy as np
from inspect_oracle import E, L

C = Path(__file__).resolve().parents[1]
SELECTION = ['trigger', 'target', 'layer', 'incoming']
PUBLICATION = ['published_at', 'layer', 'incoming', 'victim', 'slot', 'oldslot']


def record(row, generation):
    result = {key: int(row[key]) for key in SELECTION + ['published_at', 'victim',
        'slot', 'oldslot', 'status', 'bytes', 'uses', 'issue_ns', 'copy_end', 'publish_ns']}
    result.update(generation=generation, device=result['layer'] // 24,
        slot_class={3072000: 0, 3584000: 1, 3993600: 2}[result['bytes']])
    return result


def published(row):
    return int(row['publish_ns']) > 0 and int(row['published_at']) >= 0


def relationship(events, layers, frontier, common_prefix):
    """Temporal precedence in a matched proposal prefix is not causal sufficiency.

    Source contract: each hook's publication loop precedes incoming selection.
    Compare host timestamps only within one run, never between runs.
    """
    if frontier is None:
        return {'classification': 'UNRESOLVED_WITH_RETAINED_EVIDENCE', 'frontier': None,
                'reason': 'No observed divergence frontier to order against'}
    differences, prior, uncertain = [], [], []
    for generation in range(common_prefix):
        a, b = events[0][generation], events[1][generation]
        assert all(a[key] == b[key] for key in SELECTION)
        if published(a) == published(b) and all(a[key] == b[key] for key in PUBLICATION):
            continue
        visibility = []
        for arm, event, service in zip(['baseline', 'optimized'], [a, b], layers):
            at = int(event['published_at']) if published(event) else None
            same_order = at == frontier and int(event['publish_ns']) <= int(service[frontier]['plan_end'])
            visibility.append({'arm': arm, 'publication_event': at,
                'strictly_earlier_event': at is not None and at < frontier,
                'same_event_publication_before_selection_by_source': same_order,
                'record': record(event, generation)})
        before = any(v['strictly_earlier_event'] or
                     v['same_event_publication_before_selection_by_source'] for v in visibility)
        differences.append({'generation': generation, 'visibility': visibility,
                            'difference_before_frontier': before})
        if before:
            prior.append(differences[-1])
        elif any(v['publication_event'] == frontier for v in visibility):
            uncertain.append(differences[-1])
    classification = ('CONFIRMED_PUBLICATION_PRECEDES_DIVERGENCE' if prior else
                      'UNRESOLVED_WITH_RETAINED_EVIDENCE' if uncertain else
                      'CONFIRMED_PUBLICATION_DOES_NOT_PRECEDE_DIVERGENCE')
    return {'classification': classification, 'frontier': frontier,
        'matched_proposal_generations': common_prefix,
        'publication_differences': len(differences), 'differences_before_frontier': len(prior),
        'same_event_order_unresolved': len(uncertain),
        'prior_differences': prior,
        'first_differences_after_or_unpublished': [x for x in differences if not x['difference_before_frontier']][:4],
        'meaning': 'Temporal order of observed differing publications in matched proposal history; '
                   'not identification of causal candidate/worker/EWMA state. A negative result '
                   'excludes this observed precedence, not asynchronous readiness.'}


def compare(baseline, optimized):
    paths = [C / 'raw' / r['label'] / 'raw' for r in [baseline, optimized]]
    events = [np.fromfile(p / 'oracle-admissions.bin', E) for p in paths]
    layers = [np.fromfile(p / 'oracle-layers.bin', L) for p in paths]
    assert len(layers[0]) == len(layers[1])
    for rows in layers:
        assert np.array_equal(rows['event'], np.arange(len(rows)))
    service_position = next((i for i, (a, b) in enumerate(zip(*layers))
        if not np.array_equal(a['slots'][:int(a['n'])], b['slots'][:int(b['n'])]) or
           not np.array_equal(a['path'][:int(a['n'])], b['path'][:int(b['n'])])), None)
    service_event = int(layers[0][service_position]['event']) if service_position is not None else None
    selection_position = next((i for i, (a, b) in enumerate(zip(*events))
        if any(a[key] != b[key] for key in SELECTION)),
        min(map(len, events)) if len(events[0]) != len(events[1]) else None)
    prefix = selection_position if selection_position is not None else min(map(len, events))
    first, selection_event = None, None
    if selection_position is not None:
        pair = [record(rows[selection_position], selection_position)
                if selection_position < len(rows) else None for rows in events]
        selection_event = min(x['trigger'] for x in pair if x is not None)
        first = {'record_position_for_identity_only': selection_position,
                 'earliest_action_divergence_event': selection_event,
                 'baseline': pair[0], 'optimized': pair[1]}
    changed = []
    if service_position is not None:
        a, b = layers[0][service_position], layers[1][service_position]
        for lane in range(int(a['n'])):
            if a['slots'][lane] == b['slots'][lane] and a['path'][lane] == b['path'][lane]:
                continue
            expert, layer = int(a['ids'][lane]), int(a['layer'])
            related = []
            for arm, admissions, row in zip(['baseline', 'optimized'], events, [a, b]):
                observed = [(i, x) for i, x in enumerate(admissions)
                    if int(x['layer']) == layer and (int(x['incoming']) == expert or int(x['victim']) == expert)
                    and published(x) and int(x['publish_ns']) <= int(row['plan_end'])]
                observed.sort(key=lambda item: int(item[1]['publish_ns']))
                related.append({'arm': arm, 'through_event': service_event,
                    'service_plan_end_host_ns': int(row['plan_end']),
                    'publications': [record(x, i) for i, x in observed[-4:]]})
            changed.append({'lane': lane, 'expert': expert, 'layer': layer,
                'baseline_slot': int(a['slots'][lane]), 'optimized_slot': int(b['slots'][lane]),
                'baseline_path': int(a['path'][lane]), 'optimized_path': int(b['path'][lane]),
                'related_generations': related})
    readiness = []
    if selection_event is not None:
        for generation in range(prefix):
            flags = [int(x[generation]['copy_end']) > 0 and
                     int(x[generation]['copy_end']) <= int(row[selection_event]['begin'])
                     for x, row in zip(events, layers)]
            if flags[0] != flags[1]:
                readiness.append({'generation': generation,
                    'copy_completed_before_dispatch': dict(zip(['baseline', 'optimized'], flags)),
                    'scope': 'Host observation of copy completion, not complete worker-state or candidate audit'})
    digests = [{name: hashlib.sha256((p / name).read_bytes()).hexdigest()
                for name in ['oracle-admissions.bin', 'oracle-layers.bin']} for p in paths]
    return {'task': baseline['task'], 'block': baseline['block'],
        'state': 'LIVE_ASYNCHRONOUS_TRAJECTORIES_DIFFER' if first or changed else 'IDENTICAL_LIVE_TRAJECTORY',
        'same_required_work': baseline['work_sha256'] == optimized['work_sha256'],
        'raw_input_sha256': dict(zip(['baseline', 'optimized'], digests)),
        'first_service_divergence_event': service_event,
        'first_incoming_selection_divergence': first,
        'publication_vs_first_selection': relationship(events, layers, selection_event, prefix),
        'publication_vs_first_service': relationship(events, layers, service_event, prefix),
        'worker_completion_observations_at_first_selection': readiness,
        'first_service_changed_lanes': changed,
        'causal_attribution': 'UNRESOLVED_WITH_RETAINED_EVIDENCE',
        'scope': 'Chronology uses actual logical publication/trigger events and within-run host times. '
                 'Proposal-vector positions identify the shared generation prefix only. '
                 'Missing per-candidate decisions/worker-state/EWMA prevent exact causal attribution. '
                 'Deterministic policy parity and measured performance remain separate evidence.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=C / 'results/live-trajectory-diagnostics.json')
    args = parser.parse_args()
    runs = json.loads((C / 'results/live-attempts.json').read_text())
    result = []
    for task, block in sorted({(r['task'], r['block']) for r in runs}):
        group = {r['arm']: r for r in runs if r['task'] == task and r['block'] == block}
        row = compare(group['PLANNER_BASELINE'], group['PLANNER_OPT'])
        result.append(row)
        print('CHRONOLOGY', task, block, row['publication_vs_first_selection']['classification'], flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('CORRECTED CHRONOLOGY COUNTS', dict(collections.Counter(
        r['publication_vs_first_selection']['classification'] for r in result)), flush=True)
