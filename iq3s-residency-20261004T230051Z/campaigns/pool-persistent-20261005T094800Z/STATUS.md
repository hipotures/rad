# Pool and persistent-residency follow-up

State: COMPLETE. Recommendation: USE_P1_BASELINE.

Completed: P0 independent-workload validation, P1 CPU-pool freeze and stress tests, P2 replay/live persistent residency, final reporting and cleanup.

P1 fixed 100 µs is the recommended real-prompt configuration. P2 is a completed negative performance result, not unfinished because of the deadline. The bounded policy study does not exhaust all possible residency algorithms.

The headline matrix contains 60 valid measured requests, with exactly three per point. Previous results and all failed/diagnostic attempts remain preserved.

Both GPU compute-process lists are empty; no owned Strata/training/profiling process remains. Source/binary identities, old archived hashes and 648 headline-related artifact hashes passed their audits.

Start: 2026-10-05T09:48:00+00:00. Absolute upper bound: 2026-10-05T19:48:00+00:00. Completed: 2026-10-05T13:11:18.443541+00:00, elapsed 3.39 h.

Pending: none in the bounded protocol. Next action: user real-prompt testing with variants/p1-baseline/start-32k.sh or start-128k.sh. No automatic additional research.
