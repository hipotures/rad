"""Logical copy/publication/use funnel; no rerun and no latency fabrication."""
import json
import statistics
from pathlib import Path

from owned import C


def main():
    summary = json.loads((C / 'summary.json').read_text())
    rows = []
    for cell in summary['cells']:
        group = [r for r in summary['rows'] if r['label'] in cell['rows']]
        oracle = cell['arm'] != 'current'
        def median(fn):
            return statistics.median(fn(r) for r in group)
        rows.append({'profile': cell['profile'], 'arm': cell['arm'],
                     'issued': median(lambda r: r['copies']['issued'] if oracle else r['copies']['native_issued']),
                     'published': median(lambda r: r['copies']['published'] if oracle else r['copies']['native_published']),
                     'repeat_admissions_beyond_first': median(lambda r: r['victim_accounting']['repeat_admissions_beyond_first']),
                     'published_before_target': median(lambda r: r['ready_publications']) if oracle else None,
                     'actual_target_admission_hits': median(lambda r: r['actual_target_admission_hit_entries']) if oracle else None,
                     'reused_distinct_invocations': median(lambda r: r['persistent_lifetimes']['admissions_with_repeated_distinct_invocations']) if oracle else None,
                     'unused_GB': median(lambda r: r['unused_GB']) if oracle else None,
                     'evicted_without_observed_use': median(lambda r: r['persistent_lifetimes']['admissions_evicted_without_observed_use']) if oracle else None,
                     'unused_censored_at_end': median(lambda r: r['persistent_lifetimes']['unused_end_censored_admissions']) if oracle else None})
    value = {'rows': rows, 'candidate_opportunity_count': None,
             'missing_counter': 'Enumeration opportunities/rejection reasons are not exported; not zero.',
             'caveat': 'Medians of separate funnel counts are descriptive, not one synthetic conserved transaction. '
                       'Target-hit counts retain lane multiplicity; published/reused counts are admission actions. '
                       'Unused-at-end is censored, never a never-use label.'}
    (C / 'analysis/admission-funnel.json').write_text(json.dumps(value, indent=2) + '\n')
    print('ADMISSION_FUNNEL_DERIVED', len(rows), flush=True)


if __name__ == '__main__':
    main()
