# Byte-aware replay evidence

Status: COMPLETE_POSITIVE for the bounded replay/headroom study. Baseline selection/publication accounting and measured-range cost sensitivities are completed. All results are fixed-trace simulations, not measured TG. Precision-repair exclusions are retained and labeled; see v4-sensitivity/repair-history.md.

The C++ selector reproduces every observed baseline promotion and final float32 usage for both main traces. Trace categories and startup slot/byte classes independently reconcile with live counters. Every policy keeps K=25, separate GPU0/GPU1 budgets, same-layer variable-size slot classes and immutable host backing. The aggregate copy queue includes 4.2 us issue overhead. Incoming entries publish only after modeled copy completion; the original blocking publication policy stalls the next window until all previous promotions are ready. Therefore lower modeled bandwidth increases wait rather than allowing unsafe late publication.

Future capacity-free replacement relaxes transfer timing completely. Future-nextuse uses true future demand, up to 96 swaps every window, a 16-window horizon and measured-range assumed transfer costs. It is a stronger feasible heuristic under those assumptions, not a proven optimum or deployable causal predictor. The earlier future-four-window count heuristic is weaker and does not establish a capacity bound.

| Profile | Policy | Nonlocal entries | Promotion GB | Modeled publication wait s |
|---|---|---:|---:|---:|
| 128k | current (v1, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 45276 | 14.373 | 0.355 |
| 128k | frequency (v1, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 42179 | 13.233 | 0.388 |
| 128k | least-stale-adapted (v1, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 84688 | 33.933 | 1.643 |
| 128k | recency (v1, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 47040 | 57.554 | 3.548 |
| 128k | static (v1, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 217880 | 0.000 | 0.000 |
| 32k | current (v1, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 36776 | 10.697 | 0.224 |
| 32k | frequency (v1, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 31573 | 12.042 | 0.361 |
| 32k | least-stale-adapted (v1, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 67123 | 25.747 | 1.150 |
| 32k | recency (v1, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 31410 | 42.644 | 2.480 |
| 32k | static (v1, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 231919 | 0.000 | 0.000 |
| 128k | future-capacity-free (v2, None, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 0 | 59.398 | 0.000 |
| 128k | future-feasible (v2, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 77709 | 54.708 | 3.330 |
| 128k | markov (v2, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 68899 | 5.682 | 0.068 |
| 32k | future-capacity-free (v2, None, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 0 | 42.114 | 0.000 |
| 32k | future-feasible (v2, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 63663 | 41.153 | 2.364 |
| 32k | markov (v2, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 62165 | 4.751 | 0.044 |
| 128k | future-nextuse (v3, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 3 | 25.480 | 0.288 |
| 128k | jev-linear (v3, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 51654 | 14.116 | 0.384 |
| 128k | jev-mlp (v3, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 65271 | 8.979 | 0.134 |
| 128k | jev-temporal-mlp (v3, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 58414 | 10.565 | 0.209 |
| 32k | future-nextuse (v3, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 4 | 18.694 | 0.198 |
| 32k | jev-linear (v3, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 41151 | 11.448 | 0.244 |
| 32k | jev-mlp (v3, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 55060 | 7.284 | 0.090 |
| 32k | jev-temporal-mlp (v3, 12.6, VALID_WITH_LEGACY_PRECISION_CAVEAT) | 48189 | 8.511 | 0.137 |
| 32k | current (v4-sensitivity, 1.8, INVALID_NUMERICAL_QUEUE) | 36777 | 10.697 | 4.977 |
| 32k | frequency (v4-sensitivity, 1.8, INVALID_NUMERICAL_QUEUE) | 31572 | 12.042 | 5.716 |
| 128k | current (v5-sensitivity, 0.5, VALID) | 45276 | 14.373 | 27.638 |
| 128k | frequency (v5-sensitivity, 0.5, VALID) | 42179 | 13.233 | 25.360 |
| 128k | future-nextuse (v5-sensitivity, 0.5, VALID) | 3 | 25.480 | 47.174 |
| 128k | current (v5-sensitivity, 1.8, VALID) | 45276 | 14.373 | 6.888 |
| 128k | frequency (v5-sensitivity, 1.8, VALID) | 42179 | 13.233 | 6.278 |
| 128k | future-nextuse (v5-sensitivity, 1.8, VALID) | 3 | 25.480 | 10.660 |
| 32k | current (v5-sensitivity, 0.5, VALID) | 36776 | 10.697 | 20.408 |
| 32k | frequency (v5-sensitivity, 0.5, VALID) | 31572 | 12.042 | 23.094 |
| 32k | future-nextuse (v5-sensitivity, 0.5, VALID) | 4 | 18.694 | 34.065 |
| 32k | current (v5-sensitivity, 1.8, VALID) | 36776 | 10.697 | 4.977 |
| 32k | frequency (v5-sensitivity, 1.8, VALID) | 31572 | 12.042 | 5.716 |
| 32k | future-nextuse (v5-sensitivity, 1.8, VALID) | 4 | 18.694 | 7.368 |

Frequency is selected for bounded live confirmation: fewer modeled nonlocals at both profiles with much less churn than recency. Least-Stale is explicitly a same-layer stale-first/FIFO adaptation, not the paper's global SpecMD implementation. The initial Markov selector shrinks score units relative to heat and must receive a normalized follow-up before closing that family.

Limitations: nonlocal CPU/mapped/resident compute remains held at the observed trajectory; selector Python wall time is reported but not included in a fake TG estimate. Actual source categories for new policies are unavailable. Cumulative promotion bytes count transfers, not SSD reads. Timing uses one host clock; no per-event CUDA synchronization is added. A full copy/computation interference sensitivity and live candidate test are required.

Repairs and failed attempts remain in v1/repair-history.md and the diagnostic reader repair record. Raw replay arrays are retained on disk and hashed in evidence.json. Reproduce with scripts/replay.py, the recorded trace prefix, rate and policy list; exact recorded commands are retained for v3 and follow-ups.

## Closing authoritative replay evidence

The peak-envelope figures below use the completed v6 numerical queue repair. Earlier attempts/tables remain retained with their precision caveats; v4 slow-rate data are invalid. Contended-rate sensitivity remains in v5-sensitivity.

| Profile | Policy | Nonlocal entries | Promotion GB | Useful GB | Unused GB | Victim demand | Modeled publication wait s |
|---|---|---:|---:|---:|---:|---:|---:|
| 32k | current | 36776 | 10.697 | 9.967 | 0.730 | 14487 | 0.2243 |
| 32k | frequency | 31572 | 12.042 | 10.846 | 1.197 | 16723 | 0.3605 |
| 32k | future-nextuse | 4 | 18.694 | 18.694 | 0.000 | 0 | 0.1976 |
| 128k | current | 45276 | 14.373 | 13.030 | 1.344 | 21323 | 0.3545 |
| 128k | frequency | 42179 | 13.233 | 11.865 | 1.369 | 22583 | 0.3880 |
| 128k | future-nextuse | 3 | 25.480 | 25.480 | 0.000 | 0 | 0.2883 |

Useful means a transferred expert is used subsequently in the fixed trace; it does not establish saved exposed latency. Victim demand counts entries while displaced, not a disjoint timing cost. The clairvoyant heuristic pays queue/slot/copy costs under the stated assumptions but has unavailable future labels. The separate transfer-free capacity reference relaxes timing and needs roughly42/59GB of replacement. No simulated metric is headline TG.
