#!/usr/bin/env python3
"""Independent thin composition of the accepted delayed binary complex graph.

Retains the previously frozen generic-bit/general-beta assembly reviewer.
Checks the new finite compiler, actual logical gate charge, complete dirty
boundary evidence and every new exact row. Imports no new producer.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import resource
import time

from review_general_beta_assembly import audit_primitive, audit_row
from review_semantic_bulk_assembly import complex_counts, require


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('certificate', 'previous', 'previous-review', 'complex-review',
                 'generic-inputs', 'output'):
        ap.add_argument('--'+name, type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh result path')
    start = time.monotonic()
    files = [args.certificate, args.previous, args.previous_review,
             args.complex_review, args.generic_inputs]
    hashes = {str(p): digest(p) for p in files}
    data, old, prior, changed, generic = [json.loads(p.read_text()) for p in files]
    require(prior['status'] == 'PASS independent complete generic-basis general-beta conditional assembly'
            and prior['input_sha256'][str(args.previous)] == digest(args.previous)
            and data['previous_complete_review_sha256'] == digest(args.previous_review),
            'Previously accepted complete assembly is not pinned')
    code = Path(__file__).parent
    for name, expected in prior['reviewer_source_sha256'].items():
        require(digest(code/name) == expected, 'Previously accepted reviewer changed: '+name)
    require(changed['status'] == 'PASS independent binary delayed-clone theorem and complete changed h28 witness'
            and data['changed_complex_independent_review_sha256'] == digest(args.complex_review),
            'New complex circuit has no independent finite and transfer acceptance')
    for name, expected in changed['source_sha256'].items():
        require(digest(code/name) == expected, 'New complex review source changed: '+name)
    for name, expected in data['source_sha256'].items():
        require(digest(code/name) == expected, 'Frozen thin producer source changed: '+name)
    require(data['unchanged_generic_root_inputs_sha256'] == digest(args.generic_inputs)
            and generic['status'] == 'PASS root independent generic-basis inputs and written theorem review'
            and data['generic_characteristic_certificate'] == old['generic_characteristic_certificate']
            and data['odd_bit_finite_audit'] == old['odd_bit_finite_audit'] == prior['unchanged_finite_identity'],
            'Unchanged finite bit graph or constructive generic basis differs')
    for path in files[1:4]:
        require(any(r['sha256'] == digest(path) for r in data['input_files'].values()),
                'Pinned thin composition input absent: '+str(path))

    full, small = changed['full'], changed['small']
    nc = complex_counts(full['counts'])
    require((nc['h'], nc['R']) == (28, 88377)
            and full['compiled_sha256'] == 'e7512bae1752999735d0478c295b89dd1d5ddc5b36e9b5de577f66b46598403f'
            and full['all_actual_source_gates_sinks_and_reverse_complements_admitted'],
            'New accepted actual binary circuit identity differs')
    logical, plan = full['complete_changed_logical'], full['actual_plan']
    c, q, links = logical['additions'], logical['designated_outputs'], plan['links']
    require((c, q, links, full['clones']) == (94966, 6552, 13141, 3932)
            and c+q-links == nc['R'] == plan['exact_roles']
            and logical['logical_frames'] == c+nc['v']
            and logical['all_changed_formal_coefficients_and_zeros_exact']
            and logical['all_formal_edges_admitted_by_independent_gram']
            and plan['all_equal_source_nondegenerate_nonalternating_intervals_exact'],
            'Actual addition/controller/frame reconstruction differs')
    macro = 3*nc['v']**2*(4*(c+nc['v'])+4*nc['v']+4)
    E = 64*(nc['W']+nc['m']+1)**3
    depth = 2*macro*nc['W']**2+4*nc['s']+4*nc['W']+4
    guard = full['guard']
    require(macro == guard['actual_grouped_scalar_gates'] == 13074237304128
            and E == guard['additive_E'] and depth == guard['exact_operation_depth_bound']
            and E-depth == guard['slack'] > 0 and macro > 6*nc['W'],
            'Literal new scalar charge replaced by a physical-role shortcut')
    dirty, shared = small['complete_dirty_basis'], small['complete_shared_exchange']
    require(dirty['complete_basis_dimension'] == 939
            and dirty['forward_identity_shear_and_inverse_exact']
            and dirty['includes_both_data_banks_all_side_and_central_scratch']
            and shared['all_dirty_banks_restored_exactly'] and shared['all_data_outputs_exact']
            and shared['middle_chronology_reversed_and_inverted'],
            'Complete changed dirty boundary and bank exchange missing')
    audit = data['changed_complex_finite_audit']
    require(audit['counts'] == full['counts'] and audit['compiled_sha256'] == full['compiled_sha256']
            and audit['actual_logical_additions'] == c and audit['links'] == links
            and audit['clones'] == full['clones'] and audit['actual_grouped_scalar_gates'] == macro
            and audit['exact_literal_depth'] == depth and audit['exact_guard_slack'] == E-depth
            and not audit['whole_rank_complex_calls_used']
            and audit['all_size_interval_theorem'] == changed['binary_interval_theorem'],
            'New complex interface evidence is inconsistent')

    old_best = max(old['witnesses'], key=lambda row: Q(row['parameters']['kappa']))
    require(Q(data['previous_accepted_kappa']) == Q(old_best['parameters']['kappa'])
            == max(Q(r['kappa']) for r in prior['rows']), 'Previous best exact witness differs')
    regressions = [{k: r[k] for k in ('complex_input', 'mode', 'prefix')} |
                   {'kappa': r['parameters']['kappa'], 'unchanged': True}
                   for r in old['witnesses']]
    require(data['accepted_general_beta_regressions'] == regressions,
            'Previously accepted eight rows were not retained exactly')
    primitive = data['generic_characteristic_certificate']['witness']
    native = audit_primitive(primitive, generic)
    rows = []
    for row in data['witnesses']:
        require(row['complex_input'] == 'delayed88377' and row['complex_counts'] == full['counts']
                and row['bit_counts'] == primitive['counts']
                and row['semantic_guard']['scalar_gates'] == macro,
                'New row does not use its accepted literal finite inputs')
        checked = audit_row(row, old_best, primitive)
        checked['complex_input'] = 'delayed88377'
        rows.append(checked)
    require({(r['mode'], r['prefix']) for r in rows}
            == set(product(('conservative', 'tight'), ('original', 'balanced'))),
            'Four complete new rows are required')
    # Uniform complex children shrink by m>=2, so their row-depth allowance
    # is one ceil(log2 e). Bit adapters temporarily reuse their Wb stock.
    nested_degree = Q(49*651+41)*(2+Q(1,25))
    require(nested_degree < 66000, 'Uniform nested product exceeds accepted row stock')
    result = dict(
        status='PASS independent complete delayed-complex generic-basis general-beta assembly',
        campaign='20261007T222521Z', generated_utc=datetime.now(timezone.utc).isoformat(),
        input_sha256=hashes, exact_primitive_audit=native, rows=rows,
        unchanged_finite_identity=data['odd_bit_finite_audit'],
        changed_complex_finite_audit=audit,
        uniform_nested_row_product=dict(bit_depth_per_log2=651, complex_depth_per_log2=1,
            degree_upper=str(nested_degree), reserved_degree=66000,
            reservation='W_complex^D_complex * W_bit^D_bit; bit prefix restored before next complex split'),
        reviewer_source_sha256={name: digest(code/name) for name in
            ('review_delayed_complex_general_beta.py', 'review_general_beta_assembly.py')},
        complete_conditional_assembly=True, whole_rank_complex_children=False,
        wall_seconds=time.monotonic()-start,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limitations=['Conditional written interfaces; giant generic basis/table/prime not instantiated',
                    'Separate setup, layout, record and strict absorption thresholds remain',
                    'No unconditional theorem, optimality or established novelty claim'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    for row in rows:
        print('PASS', row['mode'], row['prefix'], row['kappa'], flush=True)


if __name__ == '__main__':
    main()
