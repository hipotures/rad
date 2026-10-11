#!/usr/bin/env python3
"""Preserve finite-screen negatives and rare source-dependent profile leads."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path


BASELINE = [21, 17] + [1] * 9


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def entropy(widths):
    return sum(w * math.log(w) for w in widths)


def majorized(widths):
    a, b = sorted(widths, reverse=True), sorted(BASELINE, reverse=True)
    a += [0] * (max(len(a), len(b)) - len(a))
    b += [0] * (len(a) - len(b))
    return all(sum(a[:i]) <= sum(b[:i]) for i in range(1, len(a) + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--derived-root', type=Path, required=True)
    ap.add_argument('--cohorts', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    cfg = json.loads(args.cohorts.read_text())
    baseline_entropy = entropy(BASELINE)
    groups = []
    for cohort in cfg['cohorts']:
        orders, inputs, leads = [], [], []
        indices = set()
        for shard in cohort['shards']:
            root = args.derived_root / shard
            summary = json.loads((root / 'summary.json').read_text())
            assert summary['source_family_size'] == 4073300
            assert summary['status'].startswith('COMPLETE FINITE')
            inputs.append({'summary': str(root / 'summary.json'), 'sha256': digest(root / 'summary.json')})
            for receipt in summary['completed_receipts']:
                index = receipt['index']
                assert index not in indices
                indices.add(index)
                path = root / f'swap-{index:04d}.json'
                assert digest(path) == receipt['sha256']
                data = json.loads(path.read_text())
                assert data['source_pairs_completed'] == 4073300
                assert data['field_full_rank_pairs'] == [4073300, 4073300]
                classes = data['agree']['profile_classes']
                covered = sum(c['count'] for c in classes)
                assert covered == data['two_field_agree_full_rank_pairs']
                assert all(sum(c['runs']) == 47 for c in classes)
                gain = sum(c['count'] * entropy(c['runs']) for c in classes) / covered - baseline_entropy
                violations = [c for c in classes if not majorized(c['runs'])]
                improving = [c for c in classes if entropy(c['runs']) > baseline_entropy + 1e-10]
                orders.append({'index': index, 'receipt_sha256': receipt['sha256'],
                               'covered_field_agreement_pairs': covered,
                               'unresolved_field_disagreements': data['field_profile_disagreements'],
                               'profile_classes': len(classes), 'mean_entropy_gain_float': gain,
                               'majorization_violations': len(violations),
                               'improving_entropy_classes': len(improving)})
                if improving or violations:
                    leads.append({'index': index, 'swap': data['swap'], 'receipt': str(path),
                                  'receipt_sha256': receipt['sha256'],
                                  'majorization_violation_classes': violations,
                                  'positive_entropy_gain_classes': improving})
        assert len(orders) == cohort['expected_orders']
        best = max(orders, key=lambda row: row['mean_entropy_gain_float'])
        groups.append({'cohort_id': cohort['id'], 'inputs': inputs, 'orders': orders,
                       'completed_order_count': len(orders),
                       'source_pairs_screened': len(orders) * 4073300,
                       'field_matrices_screened': len(orders) * 2 * 4073300,
                       'heterogeneous_orders': sum(row['profile_classes'] > 1 for row in orders),
                       'best_whole_order_mean_entropy_gain_float': best['mean_entropy_gain_float'],
                       'best_whole_order_index': best['index'],
                       'whole_order_positive_entropy_gain_count': sum(row['mean_entropy_gain_float'] > 1e-10 for row in orders),
                       'source_dependent_leads': leads})
    result = {'utc': datetime.now(timezone.utc).isoformat(),
              'classification': 'DISCOVERY: scoped fixed-order screen and rare source-dependent leads',
              'source_sha256': digest(__file__), 'cohort_config_sha256': digest(args.cohorts),
              'baseline_front_runs': BASELINE, 'unchanged_middle_width': 481,
              'score': 'Float mean of sum(w log w) over full-rank two-field-agreement source pairs; positive gain indicates a lower first-order recurrence moment. This is a discovery ranking, not a rigorous moment or exponent certificate.',
              'cohorts': groups,
              'total_source_pairs_screened': sum(row['source_pairs_screened'] for row in groups),
              'total_field_matrices_screened': sum(row['field_matrices_screened'] for row in groups),
              'limitations': ['Two-field profile agreement does not prove rational zero minors.',
                              'Field disagreements are unresolved here and remain in the raw receipts.',
                              'Rare per-pair improvements disprove a blanket per-pair majorization claim.',
                              'No source-pair-dependent permutation or routing is free: it needs a new paid nonseparable controller/producer proof.',
                              'No universal optimality, all-size recurrence, dirty-address implementation or multiplication exponent is claimed.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    assert args.output.stat().st_size < 1024 * 1024
    print(json.dumps({'classification': result['classification'],
                      'source_pairs_screened': result['total_source_pairs_screened'],
                      'field_matrices_screened': result['total_field_matrices_screened'],
                      'cohorts': [{'id': x['cohort_id'], 'orders': x['completed_order_count'],
                                  'heterogeneous': x['heterogeneous_orders'],
                                  'best_mean_gain': x['best_whole_order_mean_entropy_gain_float'],
                                  'lead_orders': len(x['source_dependent_leads'])} for x in groups]}))


if __name__ == '__main__':
    main()
