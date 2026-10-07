# Pool and persistent-residency follow-up

State: COMPLETE. Recommendation: USE_P1_BASELINE.

Completed: P0 independent-workload validation, P1 CPU-pool freeze and stress tests, P2 replay/live persistent residency, final reporting and cleanup.

P1 fixed 100 µs is the recommended real-prompt configuration. P2 is a completed negative performance result, not unfinished because of the deadline. The bounded policy study does not exhaust all possible residency algorithms.

The headline matrix contains 60 valid measured requests, with exactly three per point. Previous results and all failed/diagnostic attempts remain preserved.

Both GPU compute-process lists are empty; no owned Strata/training/profiling process remains. Source/binary identities, old archived hashes and 648 headline-related artifact hashes passed their audits.

Start: 2026-10-05T09:48:00+00:00. Absolute upper bound: 2026-10-05T19:48:00+00:00. Completed: 2026-10-05T13:11:18.443541+00:00, elapsed 3.39 h.

Pending: none in the bounded protocol. Next action: user real-prompt testing with variants/p1-baseline/start-32k.sh or start-128k.sh. No automatic additional research.

<!-- q4-residency-v2-latest -->
## Q4 Residency v2 — complete

All three phases: COMPLETE_MIXED. Recommendation: KEEP_Q4_100US_BASELINE.

Completed 27/27 fixed-4096 primary attempts, OFF guards, independent application cases, transaction diagnostics, cancellation/drain tests and all nine advertised launcher smokes. No owned serving/training/profiling process remains.

Frozen Q4: Strata 0.1.39, K=24, PCIe=0.28, pool=100 us, workers=15. Previous data and normal user launchers remain untouched.

[Report](campaigns/q4-residency-v2-20261005T202441Z/report.md) · [Status](campaigns/q4-residency-v2-20261005T202441Z/STATUS.md) · [Selected launchers](campaigns/q4-residency-v2-20261005T202441Z/launchers/control/README.md)

Pending: none in the bounded protocol. Do not start a new research phase automatically.
<!-- /q4-residency-v2-latest -->

<!-- q4-conditional-admission-latest -->
## Q4 conditional admission v3 — complete

E033–E035: COMPLETE_MECHANISM_ONLY. Recommendation: PROMISING_CONDITIONAL_ADMISSION. Real-use production remains KEEP_Q4_100US_BASELINE.

Completed 18/18 primary requests, 12 application requests, matched ablations, safety tests and six launcher smokes. Previous v2/model hashes match; both GPUs are free.

[Report](campaigns/q4-conditional-admission-20261006T010859Z/report.md) · [Status](campaigns/q4-conditional-admission-20261006T010859Z/STATUS.md) · [Control launchers](campaigns/q4-conditional-admission-20261006T010859Z/launchers/control/README.md)

Pending: none in the bounded protocol. No further research starts automatically.
<!-- /q4-conditional-admission-latest -->

<!-- q4-live-oracle-20261006T040656Z -->

## Q4 live oracle — complete

18/18 controlled full-work requests passed. Full-future replay improves decode at 32/128/256K; one scoped H64 is negative from churn/victim damage. Research conclusion FEASIBLE_LIVE_ORACLE_GAIN; unchanged Q4/100us remains real-use. Both GPUs free, no owned inference/training/profiling processes.

[Report](campaigns/q4-live-oracle-20261006T040656Z/report.md) · [Status](campaigns/q4-live-oracle-20261006T040656Z/STATUS.md)

## Q4 oracle information decomposition

New isolated campaign: /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-oracle-decomposition-20261006T100032Z. Phase A/B complete; matched32K blocks running. Immutable UTC deadline15:57, cutoff15:12on2026-10-06. Previous serving/campaign results unchanged. See campaign STATUS.json for exact running attempt.

<!-- q4-oracle-decomposition-20261006T100032Z -->

Latest research campaign is complete: [q4-oracle-decomposition-20261006T100032Z](campaigns/q4-oracle-decomposition-20261006T100032Z/report.md). VICTIM_INFORMATION_DOMINATES, scoped fixed-work replay. 33 primary and 9 task-transfer requests retained; no fourth attempts. GPUs and owned processes are clear. Normal Q4 serving remains unchanged.
