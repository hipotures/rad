# Fresh-activation CPU router study

Status: COMPLETE_NEGATIVE (CPU versions only).

The original host activation capture was unavailable/stale for all-local groups. The real kernel reproducer confirms that rule. Fresh diagnostic copies preserve the actual inference outputs while making numeric signals valid.

| Episode | Rank | Top10 precision | Nonlocal recall | Ready recall12.6GB/s | Ready recall1.8GB/s | CPU bytes |
|---|---:|---:|---:|---:|---:|---:|
| dev-code | 0 | 69.83% | 59.85401459854015 | 5.882352941176471 | 3.676470588235294 | 31457280 |
| dev-code | 32 | 47.91% | 19.708029197080293 | 16.176470588235293 | 0.7352941176470589 | 2359296 |
| dev-code | 128 | 63.28% | 39.416058394160586 | 7.352941176470588 | 3.676470588235294 | 9437184 |
| dev-math | 0 | 71.98% | 45.2 | 4.4 | 4.4 | 31457280 |
| dev-math | 32 | 47.03% | 20.4 | 14.8 | 1.6 | 2359296 |
| dev-math | 128 | 64.71% | 34.4 | 4.0 | 1.6 | 9437184 |
| cal-prose | 0 | 70.77% | 64.57142857142857 | 7.428571428571429 | 3.142857142857143 | 31457280 |
| cal-prose | 32 | 46.11% | 41.0 | 34.714285714285715 | 3.5714285714285716 | 2359296 |
| cal-prose | 128 | 63.68% | 55.57142857142857 | 26.285714285714285 | 3.2857142857142856 | 9437184 |
| hold-code | 0 | 70.81% | 57.08661417322835 | 5.118110236220472 | 2.3622047244094486 | 31457280 |
| hold-code | 32 | 46.75% | 22.04724409448819 | 17.716535433070867 | 1.968503937007874 | 2359296 |
| hold-code | 128 | 64.07% | 43.7007874015748 | 9.84251968503937 | 4.724409448818897 | 9437184 |
| hold-structured | 0 | 66.84% | 50.18867924528302 | 2.2641509433962264 | 2.2641509433962264 | 31457280 |
| hold-structured | 32 | 38.48% | 14.339622641509434 | 10.18867924528302 | 0.7547169811320755 | 2359296 |
| hold-structured | 128 | 59.26% | 31.32075471698113 | 4.150943396226415 | 1.509433962264151 | 9437184 |
| hold-math | 0 | 69.98% | 52.690582959641254 | 2.4663677130044843 | 1.1210762331838564 | 31457280 |
| hold-math | 32 | 46.88% | 31.614349775784753 | 22.6457399103139 | 0.2242152466367713 | 2359296 |
| hold-math | 128 | 63.12% | 39.01345291479821 | 6.726457399103139 | 0.8968609865470852 | 9437184 |
| 32k | 0 | 70.82% | 58.035714285714285 | 0.9009009009009009 | 0.0 | 31457280 |
| 32k | 32 | 47.50% | 22.321428571428573 | 15.315315315315315 | 0.0 | 2359296 |
| 32k | 128 | 64.47% | 41.07142857142857 | 0.0 | 0.0 | 9437184 |
| 128k | 0 | 68.50% | 44.73684210526316 | 5.319148936170213 | 4.25531914893617 | 31457280 |
| 128k | 32 | 46.24% | 18.94736842105263 | 14.893617021276595 | 1.0638297872340425 | 2359296 |
| 128k | 128 | 61.86% | 27.894736842105264 | 13.297872340425531 | 3.723404255319149 | 9437184 |

Do not put these CPU predictors into the hot path: optimistic ready-tail recall is limited and false nonresident proposals cost transfers/victims. Measure GPU gate cost/availability before dismissing router lookahead as a whole.

Rank frozen before holdout: {'state': 'FROZEN_BEFORE_HOLDOUT', 'selected_rank': 128, 'criterion': 'Highest dev/calibration warm optimistic ready true-nonlocal recall at measured contended1.8GB/s; ties favor smaller rank. This is not a promotion utility or runtime acceptance criterion.', 'eligible_episodes': ['dev-code', 'dev-math', 'cal-prose'], 'scores': {'32': 0.027624309392265192, '128': 0.029465930018416207}, 'heldout_accessed': False, 'caveat': 'Both predeclared ranks remain in heldout tables; no further rank/threshold tuning.'}.

Same-input first-head/output/accounting parity: {'32k': {'all_output_ids_identical': True, 'all_router_entries_identical': True, 'all_T_identical': True, 'all_accepted_identical': True, 'first_head_bit_identical': True, 'first_head_max_abs_difference': 0.0, 'initial_usage_identical': True, 'final_usage_identical': True}, '128k': {'all_output_ids_identical': True, 'all_router_entries_identical': True, 'all_T_identical': True, 'all_accepted_identical': True, 'first_head_bit_identical': True, 'first_head_max_abs_difference': 0.0, 'initial_usage_identical': True, 'final_usage_identical': True}}.

Per-layer costs/readiness and false proposal counts are in summary.json. No diagnostic TG is a headline result.

Six short independent tasks provide separated dev/calibration/holdout, not broad agentic quality coverage.
Fresh forced copies repair unavailable host inputs but perturb timing and add mapped traffic.
CPU numeric cost includes projection/top10, not CPU-expert contention, capture or admission selection.
One-blob readiness ignores competing proposals, full slots and victim damage; it is not a feasible speed forecast.
Old full router-quality/readiness aggregates were withdrawn; real old output and boundary timings remain preserved.
No new auxiliary model downloaded; original weights and routing untouched.
