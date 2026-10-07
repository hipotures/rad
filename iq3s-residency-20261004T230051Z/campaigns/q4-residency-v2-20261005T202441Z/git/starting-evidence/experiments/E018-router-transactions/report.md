# E018: bounded temporary placement feasibility

This fixed-trajectory model charges the full target promotion and restoration of the displaced expert, actual physical slot classes, a shared transfer queue, and baseline promotion traffic. Victims belong to completed earlier layers on the same GPU; at most one admission per recorded prediction point. The baseline resident set is restored before the next window. No model router or expert weights change.

Two predeclared admission rules: first predicted nonresident expert, and the same rule with causal EMA>=2 and gain>=1.5. Five same-device prediction points, first64windows, two benchmark requests and six independent tasks. This is a specific ephemeral placement schedule, not the optimum or a test of every persistent policy.

| Episode | Policy | CopyGB/s | Admissions | Ready-tail% | H2DMB | RestoreMB | Modeled restorewaits |
|---|---|---:|---:|---:|---:|---:|---:|
| 32k | rank-first | 1.8 | 40 | 1.19 | 78.95 | 88.12 | 0.000 |
| 32k | rank-first | 12.6 | 40 | 30.95 | 78.95 | 88.12 | 0.000 |
| 32k | heat-guarded | 1.8 | 2 | 0.00 | 4.15 | 4.51 | 0.000 |
| 32k | heat-guarded | 12.6 | 2 | 3.57 | 4.15 | 4.51 | 0.000 |
| 128k | rank-first | 1.8 | 54 | 0.69 | 105.73 | 118.89 | 0.198 |
| 128k | rank-first | 12.6 | 54 | 17.36 | 105.73 | 118.89 | 0.000 |
| 128k | heat-guarded | 1.8 | 4 | 0.00 | 8.29 | 9.01 | 0.000 |
| 128k | heat-guarded | 12.6 | 4 | 3.47 | 8.29 | 9.01 | 0.000 |
| dev-code | rank-first | 1.8 | 63 | 0.00 | 123.98 | 138.93 | 0.043 |
| dev-code | rank-first | 12.6 | 63 | 26.67 | 123.98 | 138.93 | 0.000 |
| dev-code | heat-guarded | 1.8 | 4 | 0.00 | 7.78 | 8.86 | 0.000 |
| dev-code | heat-guarded | 12.6 | 4 | 2.50 | 7.78 | 8.86 | 0.000 |
| dev-math | rank-first | 1.8 | 50 | 0.00 | 99.99 | 110.95 | 0.083 |
| dev-math | rank-first | 12.6 | 50 | 16.93 | 99.99 | 110.95 | 0.000 |
| dev-math | heat-guarded | 1.8 | 3 | 0.00 | 6.53 | 6.99 | 0.000 |
| dev-math | heat-guarded | 12.6 | 3 | 2.12 | 6.53 | 6.99 | 0.000 |
| cal-prose | rank-first | 1.8 | 127 | 0.00 | 253.21 | 258.33 | 13.131 |
| cal-prose | rank-first | 12.6 | 127 | 21.36 | 253.21 | 258.33 | 0.000 |
| cal-prose | heat-guarded | 1.8 | 45 | 0.00 | 90.55 | 92.19 | 3.631 |
| cal-prose | heat-guarded | 12.6 | 45 | 11.34 | 90.55 | 92.19 | 0.000 |
| hold-code | rank-first | 1.8 | 72 | 0.00 | 141.62 | 149.09 | 0.259 |
| hold-code | rank-first | 12.6 | 72 | 23.76 | 141.62 | 149.09 | 0.000 |
| hold-code | heat-guarded | 1.8 | 8 | 0.00 | 16.28 | 16.79 | 0.000 |
| hold-code | heat-guarded | 12.6 | 8 | 4.46 | 16.28 | 16.79 | 0.000 |
| hold-structured | rank-first | 1.8 | 79 | 0.00 | 158.80 | 161.66 | 0.428 |
| hold-structured | rank-first | 12.6 | 79 | 28.29 | 158.80 | 161.66 | 0.000 |
| hold-structured | heat-guarded | 1.8 | 8 | 0.00 | 16.69 | 16.79 | 0.086 |
| hold-structured | heat-guarded | 12.6 | 8 | 5.85 | 16.69 | 16.79 | 0.000 |
| hold-math | rank-first | 1.8 | 97 | 0.00 | 193.25 | 196.94 | 3.847 |
| hold-math | rank-first | 12.6 | 97 | 22.54 | 193.25 | 196.94 | 0.000 |
| hold-math | heat-guarded | 1.8 | 23 | 0.00 | 46.77 | 47.39 | 1.353 |
| hold-math | heat-guarded | 12.6 | 23 | 9.54 | 46.77 | 47.39 | 0.000 |

The12.6GB/s case is an isolated optimistic sensitivity;1.8GB/s is a conservative contended scenario. Observed CPU target-dispatch timestamps are optimistic readiness deadlines. The original trajectory and baseline promotion times remain fixed: model delays are not fed back into future execution. Restore waits cannot be added to unrelated timer totals or presented as a measured request slowdown.

Decision: no live implementation of this temporary scheme. It does not demonstrate that persistent or longer-horizon gate prediction is impossible. The cheap signal is useful evidence; queue deadlines and full-slot management remain the blocker. Scripts/protocol/choices/raw references retained in v1.
