"""Locate live OFF/ON trajectory divergence; separate readiness evidence from conjecture."""
import numpy as np
from common import *
from inspect_oracle import E, L

def record(row):
    return {key: int(row[key]) for key in ['trigger', 'target', 'published_at', 'layer', 'incoming', 'victim', 'slot', 'oldslot', 'status', 'bytes', 'uses']}

def compare(baseline, optimized):
    paths = [C / 'raw' / r['label'] / 'raw' for r in [baseline, optimized]]
    admissions = [np.fromfile(p / 'oracle-admissions.bin', E) for p in paths]
    layers = [np.fromfile(p / 'oracle-layers.bin', L) for p in paths]
    assert len(layers[0]) == len(layers[1])
    service_diff = next((i for i, (a, b) in enumerate(zip(*layers)) if not np.array_equal(a['slots'][:int(a['n'])], b['slots'][:int(b['n'])]) or not np.array_equal(a['path'][:int(a['n'])], b['path'][:int(b['n'])])), None)
    keys = ['trigger', 'target', 'layer', 'incoming']
    selection_diff = next((i for i, (a, b) in enumerate(zip(*admissions)) if any(a[k] != b[k] for k in keys)), min(map(len, admissions)) if len(admissions[0]) != len(admissions[1]) else None)
    first = None
    if selection_diff is not None:
        first = {'index': selection_diff, 'baseline': record(admissions[0][selection_diff]) if selection_diff < len(admissions[0]) else None, 'optimized': record(admissions[1][selection_diff]) if selection_diff < len(admissions[1]) else None}
    publication_difference = next((i for i, (a, b) in enumerate(zip(*admissions)) if a['published_at'] != b['published_at']), None)
    earlier_readiness_difference = publication_difference is not None and (selection_diff is None or publication_difference < selection_diff)
    first_publication = {'index':publication_difference,'baseline':record(admissions[0][publication_difference]),'optimized':record(admissions[1][publication_difference])} if publication_difference is not None else None
    changed = []
    if service_diff is not None:
        a, b = layers[0][service_diff], layers[1][service_diff]
        for lane in range(int(a['n'])):
            if a['slots'][lane] == b['slots'][lane] and a['path'][lane] == b['path'][lane]:
                continue
            expert = int(a['ids'][lane]); layer = int(a['layer'])
            lane_record = {'lane': lane, 'expert': expert, 'layer': layer, 'baseline_slot': int(a['slots'][lane]), 'optimized_slot': int(b['slots'][lane]), 'baseline_path': int(a['path'][lane]), 'optimized_path': int(b['path'][lane]), 'related_generations': []}
            for arm, events, row in zip(['baseline', 'optimized'], admissions, [a, b]):
                relevant = [record(x) for x in events if int(x['layer']) == layer and (int(x['incoming']) == expert or int(x['victim']) == expert) and int(x['trigger']) <= service_diff]
                lane_record['related_generations'].append({'arm': arm, 'through_event': service_diff, 'records': relevant[-4:]})
            changed.append(lane_record)
    evidence = 'IDENTICAL_LIVE_TRAJECTORY' if service_diff is None and baseline['logical_live_admissions_sha256'] == optimized['logical_live_admissions_sha256'] else 'LIVE_ASYNCHRONOUS_TRAJECTORIES_DIFFER'
    return {'task': baseline['task'], 'block': baseline['block'], 'state': evidence, 'same_required_work': baseline['work_sha256'] == optimized['work_sha256'], 'first_service_divergence_event': service_diff, 'first_incoming_selection_divergence': first, 'first_publication_event_difference_index': publication_difference, 'first_different_publication':first_publication,'publication_visibility_changed_before_first_incoming_selection_divergence':earlier_readiness_difference,'first_service_changed_lanes': changed, 'scope': 'Observed chronological differences, not exact deterministic state replay. Earlier different publication visibility is positive evidence for the asynchronous schedule explanation. Different publication/worker readiness and measured copy/event-derived lead are permitted dependencies in the unchanged policy. Exact fixed-cadence candidate and lifecycle parity is independently proved. No per-candidate decision trace or copy/event EWMA was recorded in headline mode, so attribution of every first live selection divergence to one timing variable remains unresolved; no live trajectory equality is inferred from work equality.'}

if __name__ == '__main__':
    no_gpu(); runs = load(C / 'results/live-attempts.json'); result = []
    with Heartbeat('live trajectory diagnosis', 5):
        for task, block in sorted({(r['task'], r['block']) for r in runs}):
            group = {r['arm']: r for r in runs if r['task'] == task and r['block'] == block}
            result.append(compare(group['PLANNER_BASELINE'], group['PLANNER_OPT']))
    save(C / 'results/live-trajectory-diagnostics.json', result)
    print('LIVE TRAJECTORY AUDIT', len(result), flush=True)
