"""Document bounded findings after raw transactional accounting is complete."""
import json
import statistics
from pathlib import Path

from owned import C


def load(path):
    return json.loads(Path(path).read_text())


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                       '| ' + ' | '.join(['---'] * len(headers)) + ' |']
                      + ['| ' + ' | '.join(map(str, row)) + ' |' for row in rows])


def main():
    summary = load(C / 'summary.json')
    assert len(summary['rows']) == 33
    assert all('victim_accounting' in r for r in summary['rows'])
    assert len(load(C / 'analysis/mechanism-summary.json')) == 42
    cells = {(c['profile'], c['arm']): c for c in summary['cells']}
    def median(profile, arm, key):
        return cells[profile, arm]['metrics'][key]['median']
    for profile in ['32k', '128k', '256k']:
        assert cells[profile, 'FF']['paired']['TG_ratio_vs_current']['min'] > 1.03
    assert cells['32k', 'F64']['paired']['TG_ratio_vs_current']['max'] < 1
    for profile in ['128k', '256k']:
        assert cells[profile, 'F256']['paired']['TG_ratio_vs_current']['max'] < 1
    decision = {
        'headline': '**Victim information dominates the loss in the tested first-feasible '
                    'scheduler.** Full future improves all nine main matched decode pairs; '
                    'restricting victim lifetime loses the gain, while the incoming '
                    'retention utility is structurally inactive in this policy. '
                    'This does not establish a universal information requirement.',
        'transfer_interpretation':
            'F/F median replay-equivalent rates are 120.19 / 97.04 / 89.83 tok/s at '
            '32K / 128K / 256K, versus current 104.36 / 87.01 / 79.81. Median '
            'within-block TG ratios improve by 15.17% / 11.24% / 12.56%; these '
            'are medians of paired ratios, not ratios of medians. Request-wall '
            'ratios improve by 9.17% / 6.51% / 2.63% respectively. '
            'The frozen follow-up I=FULL/V=256 loses every larger-context decode '
            'pair: median TG changes -7.37% at128K and -10.23% at256K. Its tiny '
            '256K wall improvement (0.42%) accompanies worse decode and varying '
            'prefill, so is not a practical scheduler win. '
            'On the previously observed independent archive task F/F improves '
            'all three pairs (median +16.37% TG); V256 retains 39.44% of full '
            'time saving at the median, with range -54.49% to63.35%. '
            'That task has different CPU/miss characteristics and sampled byte-check '
            'costs; it is not an untouched holdout or quality evaluation.',
        'mechanism_interpretation':
            f'At32K the full policy has median {median("32k","FF","victim_absent_entries"):,.0f} '
            f'observed victim-absent entries, versus '
            f'{median("32k","F64","victim_absent_entries"):,.0f} with V64 and '
            f'{median("32k","current","victim_absent_entries"):,.0f} under native current. '
            f'Full copies {median("32k","FF","copy_GB"):.2f}GB, V64 '
            f'{median("32k","F64","copy_GB"):.2f}GB, current '
            f'{median("32k","current","copy_GB"):.2f}GB. Thus this feasible gain pays '
            'more transfer traffic than current; it is not a cheap static-cache result. '
            'V64 achieves a higher local share than current yet slower decode, with '
            'more churn and online planning/publication. At128K V256 causes median '
            f'{median("128k","F256","victim_absent_entries"):,.0f} victim-absent entries '
            f'versus {median("128k","FF","victim_absent_entries"):,.0f} for full. '
            'Its copies are roughly321GB versus202GB, and oracle-planner counters '
            '9.65s versus6.81s. These overlapping costs support the mechanism but '
            'do not isolate a unique critical-path penalty. '
            'Incoming64 slow attempt3 is retained: staging median272.6us versus '
            '139.3us for its paired full attempt, more late publication and victim '
            'absence, despite valid query limits/work/state. Copy-with-host-wait '
            'medians remain similar. Unique VM/scheduling causation is unresolved. '
            'Readiness, distinct persistent reuse, native/oracle reload recurrence, '
            'right-censored survivors and finite-end interior sensitivity are '
            'reported separately; routed-lane multiplicity is not durable reuse.',
        'sufficient_budget':
            'Incoming: I=64 is the smallest tested budget reproducing deterministic '
            'F/F decisions at unchanged E64 in the offline model and source tests. '
            'Its live median retention is75.96%, range -25.67% to94.05%, so an '
            '80–90% performance-sufficiency claim is unresolved. I4/I16 shorten '
            'eligibility as well as value information and therefore do not isolate '
            'incoming lifetime. Victim: neither V64 at32K nor V256 in the larger '
            'profiles is sufficient under the tested policy/fallback. FULL is the '
            'only tested passing reference; the smallest sufficient finite V '
            'remains unmeasured. This is not proof that a causal predictor needs '
            'exact whole-request next-use, nor that every short-history victim '
            'policy fails. Interaction has signs +1181/-3150/-2575ms across blocks, '
            'not a stable linear law.',
        'next_target':
            'One next research target: calibrated **victim-return risk / eviction '
            'regret for a proposed same-layer, same-class, same-device exchange**, '
            'conditional on an already visible incoming E64 action. Estimate '
            'whether demand for the displaced resident will return before ready '
            'incoming reuse amortizes copy and planning cost. Use causal usage, '
            'heat, recency, age, reload history, class, queue and protection state; '
            'retain uncertainty when future use is censored. A later causal system '
            'must independently supply incoming predictions and replace privileged '
            'whole-current-window P with safe available dependency state. '
            'Do not train a generic expert-popularity model or assume exact distant '
            'next-use is required. First instrument/use an effective net exchange '
            'ranking or veto: the present computed reuse utility never compares '
            'two feasible actions.',
        'conclusion': 'VICTIM_INFORMATION_DOMINATES',
    }
    (C / 'analysis/final-decision.json').write_text(json.dumps(decision, indent=2) + '\n')
    rows = []
    for cell in summary['cells']:
        group = [r for r in summary['rows'] if r['label'] in cell['rows']]
        def med(fn):
            return statistics.median(fn(r) for r in group)
        oracle = cell['arm'] != 'current'
        rows.append([
            cell['profile'], cell['arm'],
            f'{med(lambda r:r["victim_absent_entries"]):,.0f}',
            f'{med(lambda r:r["victim_accounting"]["chronological_victim_reloads"]):,.0f}',
            f'{med(lambda r:r["victim_accounting"]["victims_reloaded_repeatedly"]):,.0f}',
            f'{med(lambda r:r["actual_target_admission_hit_entries"]):,.0f}' if oracle else 'n/a',
            f'{med(lambda r:r["persistent_lifetimes"]["admissions_with_repeated_distinct_invocations"]):,.0f}' if oracle else 'n/a',
            f'{med(lambda r:r["persistent_lifetimes"]["resident_lifetime_right_censored_at_end"]):,.0f}' if oracle else 'n/a',
        ])
    mechanism = table(['Profile','Arm','Victim-absent entries','Victim reloads',
                       'Victims reloaded >=2 times','Actual target-admission hit entries',
                       'Admissions reused in >=2 invocations','End-censored admissions'], rows)
    text = '# Phase C — matched live information ablations\n\n'
    text += decision['headline'] + '\n\n' + decision['transfer_interpretation'] + '\n\n'
    text += '## Transactional mechanism\n\n' + mechanism + '\n\n'
    text += decision['mechanism_interpretation'] + '\n\n'
    text += '## Information sufficiency\n\n' + decision['sufficient_budget'] + '\n\n'
    text += '## Admission accounting and scope\n\n'
    text += ('Every main and task-transfer request passes the exact tape/state/query/ownership '
             'checks. All48 main layers and3classes are covered. Initial five donor withdrawals '
             'and restoration are charged only to oracle, inside decode/request respectively. '
             'Native current keeps original capacity/adaptation. Completed payloads, publications, '
             'target-local use and later distinct reuse are different funnel stages. '
             'Native/oracle absent demand is rebuilt from chronological journals and checked '
             'against actual service slots for every routed batch. Scope-specific empty oracle '
             'journals in current do not mean zero native churn; only the comparable victim '
             'journal is used for that comparison. No timing outlier exclusion or fourth attempt.\n\n')
    text += ('The inherited native decode timer stops before final commit wait, drain, restoration '
             'and buffered trace flush. Whole request wall includes them. Tape/index setup and '
             'attestation remain separately reported. Short ordinary/replay overhead is uncertain '
             '(median+5.61% decode, +11.42% wall); fixed-work forced tokens do not establish '
             'ordinary quality or deployable TG. Main-thread affinity is not every-thread '
             'affinity; retained56-thread snapshot documents this. CPU steal differs across '
             'arms and secondary KV DMA service is incompletely observed.\n\n')
    text += '## Next causal target\n\n' + decision['next_target'] + '\n\n'
    text += 'No real-serving baseline change. No model/source upgrade, helper, pool/K/PCIe/MTP tuning or learned training.\n\n'
    text += decision['conclusion'] + '\n'
    (C / 'phase-c/report.md').write_text(text)
    (C / 'analysis/transactional-mechanism.md').write_text(
        '# Comparable transactional accounting\n\n' + mechanism + '\n\n'
        'All medians are derived from the preserved per-attempt journals. '
        'Victim-absent demand is an observation, not exclusive causal latency. '
        'Readmission resets absence; initial spare donors are separate.\n')
    predictor = C / 'analysis/predictor-specification.md'
    text = predictor.read_text().replace(
        'This specification is provisional until live results. It is not a trained predictor or a production change.',
        'This specification follows the completed bounded live experiment. It is not a trained predictor or a production change.')
    text += ('\n## Observed decision basis\n\n' + decision['sufficient_budget'] + '\n\n'
             'Observed absent demand, future-conditioned displacement duration and eventual '
             'readmission provide training labels only after the action. Negative labels near '
             'tape end remain censored without a guard tail. Weight losses by measured class '
             'copy payload and observed CPU/mapped costs with timer-overlap caveats; do not '
             'convert each miss into an assumed exclusive millisecond cost. A future learner '
             'requires new task-level calibration/holdout episodes, not these timing replicas.\n')
    predictor.write_text(text)
    with (C / 'DECISIONS.md').open('a') as stream:
        stream.write('\n## Final bounded conclusion\n\n' + decision['headline'] + '\n\n'
                     + decision['sufficient_budget'] + '\n\n'
                     'Keep unchanged normal Q4/100us serving. No predictor implementation follows automatically.\n')
    print('RESULT_REPORTS_WRITTEN', decision['conclusion'], flush=True)


if __name__ == '__main__':
    main()
