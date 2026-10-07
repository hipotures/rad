# Phase A — what “wrong-or-superseded” means

The historical v2 diagnostic issued 5917 copies, published 917, classified 4996 as wrong-or-superseded and 4 as late. The 4996 records represent 15.347712 GB, but the old stream did not preserve actual target IDs. They remain **underidentified**: we cannot honestly split those exact historical actions into finer reasons.

A new buffered diagnostic adds explicit target outcome, actual routed IDs, slot state and native-cache changes without changing the early algorithm. It issued 6002 copies and published 1043. It matches the preserved **clean v2 early 32K replicate 1** in input IDs, output IDs, MTP and routing counters ([parity](clean-v2-parity.json)). It does not match the older diagnostic trajectory, so action-key matches are descriptive and are not used to relabel the original 4996.

| New reason | Count | GB | % of issued |
|---|---:|---:|---:|
| prediction-wrong | 4959 | 15.234048 | 82.622 |
| became-resident-before-publication | 0 | 0.000000 | 0.000 |
| late-for-original-target | 0 | 0.000000 | 0.000 |
| request-ended-before-target | 0 | 0.000000 | 0.000 |
| no-safe-victim | 0 | 0.000000 | 0.000 |
| target-ready-persistent | 1043 | 3.204096 | 17.378 |

**Prediction-wrong dominates both count and bytes.** Every action uses the same 3.072 MB class. Here, “prediction-wrong” means a completed, ready copy whose incoming expert was absent from all actual routed branch IDs at its intended target layer. It does not mean the expert is never used later.

The other requested categories require careful interpretation:

| Requested category | Evidence / applicability |
|---|---|
| superseded-by-newer-prediction | Impossible for an issued worker in this scheduler: its target and incoming identity stay fixed until retirement/publication. Later proposals see busy; they do not replace it. |
| duplicate-or-inflight | Prevented before issue by worker/residency checks. An unissued duplicate is not part of copied bytes. No fabricated count of all rejected upstream proposals. |
| victim-became-protected | No victim is reserved at enqueue in early-v1. The actual victim is selected at the target with current routed IDs excluded. Thus a prospective victim can change, but this is not a defined failed-copy reason. Explicit no-safe-victim would be reported if observed. |
| state-generation-mismatch | No such outcome branch exists in this implementation. The host planner owns residency; native changes are joined between windows. Not a hidden measured zero for arbitrary cache races. |
| became-resident-before-publication | Explicit target residency guard; not observed in the matched trace. Native adaptation is applied between windows rather than racing inside the origin-to-target interval. |
| deadline-missed | Separate late-for-original-target reason; zero in the matched trace, observed in independent diagnostic episodes. |
| right-censored | An unobserved target remains censored. Additionally, 19 near-end actions have censored future-reuse labels even though their target outcome may be known. They are not automatically future-use negatives. |
| other | Explicit no-safe-victim/request-end codes are retained. There is no unexplained generic “wrong” bucket in the new stream. |

Across the 12 independent task episodes, 19866 issued copies comprise 16849 prediction-wrong (84.813%, 51.760128 GB), 2725 target-ready publications (13.717%, 8.371200 GB), and 292 late (1.470%, 0.897024 GB). Buffered feature/demand logging and canonical readbacks can affect copy timing, so these are diagnostic reasons, not headline speed measurements.

The demand schema records every routed entry, not only unique experts: 336-byte demand record, 20-byte native-change record, and 48 causal features per issued event. Current branch demand protects actual victims. No runtime algorithm, model weights or production control was changed in Phase A. [Machine-readable audit](summary.json), [episode reasons](../analysis/episode-failure-reasons.json), [diagnostic source patch](../patches/reason-v1.diff).
