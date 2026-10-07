"""Attach post-run transactional evidence without changing captured benchmark data."""
import csv
import json
from pathlib import Path
import numpy as np

from analyze import stat
from inspect_oracle import E

C = Path(__file__).resolve().parents[1]


def attach(row):
    label = row['label']
    def load(suffix):
        return json.loads((C / 'analysis' / (label + suffix + '.json')).read_text())
    victim = load('-victim-accounting')
    assert victim['state'] == 'PASS'
    row.setdefault('oracle_victim_absent_entries', row['victim_absent_entries'])
    row['victim_absent_entries'] = victim['victim_absent_entries']
    row['victim_accounting'] = victim
    target = load('-target-readiness')
    row['target_readiness'] = target
    row['late_target_nonlocal_entries'] = target['late_target_nonlocal_entries'] if row['policy'] != 'current' else None
    row['actual_target_admission_hit_entries'] = target['same_admission_hit_entries'] if row['policy'] != 'current' else None
    row['recurrent_exchanges'] = load('-recurrent-exchanges')
    row['persistent_lifetimes'] = load('-persistent-lifetimes')
    lifetime = row['persistent_lifetimes']
    arrays = np.load(C / 'analysis' / (label + '-persistent-lifetimes.npz'))
    admissions = np.fromfile(C / 'raw' / label / 'raw/oracle-admissions.bin', E)
    published = admissions['publish_ns'] > 0
    lifetime['admissions_evicted_without_observed_use'] = int(np.count_nonzero(
        published & (arrays['distinct_uses'] == 0) & (arrays['evicted_event'] >= 0)))
    lifetime['unused_end_censored_admissions'] = int(np.count_nonzero(
        published & (arrays['distinct_uses'] == 0) & (arrays['evicted_event'] < 0)))
    lifetime['scope'] = 'Oracle admission lifetimes only; empty current oracle journal is not zero native lifetime.'
    (C / 'analysis' / (label + '-persistent-lifetimes.json')).write_text(
        json.dumps(lifetime, indent=2) + '\n')
    row['residual_misses'] = load('-residual-misses')
    row['planner_scope'] = 'Oracle hook overhead only; ordinary native planning is separate' if row['policy'] == 'current' else 'Online oracle query/selection/publication; publication overlaps total planner'


def main():
    path = C / 'summary.json'
    value = json.loads(path.read_text())
    for row in value['rows']:
        attach(row)
    by_label = {r['label']: r for r in value['rows']}
    for cell in value['cells']:
        rows = [by_label[x] for x in cell['rows']]
        for key in ['victim_absent_entries', 'late_target_nonlocal_entries', 'actual_target_admission_hit_entries']:
            cell['metrics'][key] = stat([r[key] for r in rows])
    value['victim_metric_definition'] = 'Both policies: actual absent demand following an observed eviction, ending on readmission. Native eviction begins at copy issue; oracle eviction begins at completed-copy publication. Initial spare donors are separate. Not exclusive causal latency.'
    value['planner_metric_definition'] = 'Oracle counters are not a complete native-planner timing. Current oracle-hook overhead must not be interpreted as no native planning.'
    path.write_text(json.dumps(value, indent=2) + '\n')
    with (C / 'summary.csv').open() as stream:
        keys = csv.DictReader(stream).fieldnames
    keys += [k for k in ['late_target_nonlocal_entries', 'actual_target_admission_hit_entries', 'oracle_victim_absent_entries'] if k not in keys]
    with (C / 'summary.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(value['rows'])
    independent_path = C / 'phase-c/independent-summary.json'
    independent = json.loads(independent_path.read_text())
    for row in independent['rows']:
        attach(row)
    for cell in independent['cells']:
        rows = [r for r in independent['rows'] if r['arm'] == cell['arm']]
        cell['victim_absent'] = stat([r['victim_absent_entries'] for r in rows])
    independent_path.write_text(json.dumps(independent, indent=2) + '\n')
    print('TRANSACTIONAL_SUMMARY_COMPLETE', len(value['rows']), len(independent['rows']), flush=True)


if __name__ == '__main__':
    main()
