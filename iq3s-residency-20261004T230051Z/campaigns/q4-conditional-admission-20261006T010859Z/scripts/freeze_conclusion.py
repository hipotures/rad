"""Freeze the decision from completed data, without inference or retuning."""
from campaign import C, load, save
import datetime

pairs = load(C/'analysis/live-paired-ratios.json')
independent = load(C/'analysis/independent-live.json')
off = load(C/'analysis/off-speed-guard.json')
contiguous = load(C/'analysis/contiguous-holdout-audit.json')
assert all(p['pairs'] == 3 for p in pairs) and len(independent) == 2
decision = {
    'frozen_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'recommendation': 'PROMISING_CONDITIONAL_ADMISSION',
    'production_baseline': 'KEEP_Q4_100US_BASELINE',
    'deployment_switch': False,
    'mechanism_success': True,
    'conclusion': (
        'Conditional admission rejects bad copies before staging and meets the pooled '
        'offline efficiency gate: unpublished bytes fall 73.76%, while 85.38% of '
        'next-four-window demand potential and 90.16% of observed contiguous '
        'local entries are retained. The latter attribution ends at the first '
        'native/early touch and is not a counterfactual exclusive-latency estimate. '
        'This is a mechanism result, not a deployment win. The 18-request matrix '
        'shows an apparent 32K application gain, a 128K tie and no 256K gain; '
        'independent code improves only 3.77% TG and structured text regresses '
        '3.56%. All ON comparisons change output/MTP trajectories. Crucially, '
        'the new binary with the algorithm OFF already reaches 106.7 TG versus '
        'earlier control 93.9 with identical output/MTP/routing/capacity. That '
        'single later-time guard exposes build/environment confounding and '
        'prevents crediting the apparent 32K gain to the gate. Retain the unchanged '
        'Q4 100us baseline for real use; preserve conditional launchers as experimental.'
    ),
    'remaining_bottleneck': (
        'Action validity remains the dominant copy problem: roughly two thirds '
        'of issued conditional copies are still unpublished. Victim utility is '
        'weakly predictable, and attributed nonlocal demand does not reliably '
        'fall versus control. Wrong predictions dominate; clean late counts '
        'increase at 256K (median 63), so publication timing also remains imperfect. '
        'Copy readiness is mostly adequate in clean runs; '
        'diagnostic late counts are instrumented and not headline estimates. '
        'Only five layers are affected. Output/MTP changes and demonstrated '
        'environment/build timing confounding prevent a causal throughput claim.'
    ),
    'single_best_next_experiment': (
        'Before another predictor or victim policy, run one predeclared, '
        'counterbalanced same-candidate-binary OFF-versus-conditional comparison '
        'at 32K, ideally with a preserved fixed token/spec-window replay and '
        'same routing/accounting. This removes the exposed build difference '
        'and separates gating cost from free-generation/MTP and scheduling noise. '
        'Do not add it to this completed campaign or repeat controls to seek a win.'
    ),
    'primary_paired_results': pairs,
    'independent_results': [
        {k: t[k] for k in ['task', 'median_paired_TG_ratio', 'median_paired_wall_ratio']}
        for t in independent
    ],
    'OFF_guard': off,
    'contiguous_holdout_reporting_audit': contiguous,
    'no_further_policy_or_performance_repetitions': True,
    'unfinished_due_to_deadline': [],
    'limits': [
        'Six held-out routing episodes are modest, not universal generalization.',
        'Training episodes have short actual inputs, 32K maximum context and 1024 output; primary long-context/4096 runs extrapolate these conditions.',
        'Fixed-native-schedule offline attribution is not a counterfactual cache oracle or exact exposed-latency model.',
        'The stricter code-family holdout guard failed and is explicitly preserved; no threshold was retuned.',
        'Predictor-only CPU percentage and exact exclusive miss/publication cost are unavailable.'
    ]
}
save(C/'decision.json', decision)
print('DECISION_FROZEN', decision['recommendation'], flush=True)
