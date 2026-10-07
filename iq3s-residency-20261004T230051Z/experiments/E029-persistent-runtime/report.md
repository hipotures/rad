# E029: live persistent residency on the P1 baseline

The persistent mechanism worked within fixed per-device byte capacities, but reduced median decode throughput at both context profiles. The recommendation is to use P1 for real prompts. This is a completed negative performance result; it does not exhaust persistent residency policies.

The final matrix uses the same modified binary with residency OFF or ON: identical actual input IDs, settings, initial capacities, K=25, PCIe fraction 0.28, pool parking 100 µs, suffix/reuse OFF and greedy serial requests. Every point had three fresh-server replicates, the same 4096-input/64-output warmup, and 4096 measured output tokens. All 12 measured requests were valid.

| Profile | Policy | PP median | TG min / median / max | TTFT s | Wall s | MTP accept % | CPU entries | PCIe entries | Decode VM CPU % | GPU0 % | GPU1 % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 32k | off | 3572.1 | 166.2 / 167.6 / 197.1 | 8.079 | 32.507 | 81.1 | 34264 | 1143 | 25.5 | 45.9 | 55.0 |
| 32k | on | 3571.2 | 156.3 / 160.5 / 181.7 | 8.077 | 33.598 | 86.0 | 64771 | 4921 | 33.2 | 45.6 | 53.7 |
| 128k | off | 3985.6 | 142.8 / 145.2 / 158.8 | 32.256 | 60.455 | 76.0 | 42755 | 1622 | 29.1 | 46.7 | 54.6 |
| 128k | on | 4221.3 | 135.1 / 138.1 / 148.2 | 30.496 | 60.151 | 76.2 | 74591 | 5917 | 34.8 | 46.7 | 53.3 |

| Profile | Promotions | GB copied | Useful | Repeated | Wasted | Ready for future use | Late | Victim entries | Selector ms | Pending wait ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 32k | 1765 | 3.530 | 1752 | 1739 | 15 | 1752 | 0 | 8900 | 264.785 | 34.318 |
| 128k | 2388 | 4.770 | 2344 | 2314 | 44 | 2344 | 0 | 14818 | 273.196 | 53.053 |

Columns are independent medians, so useful plus wasted medians need not equal promotion medians. Ready/late means the first subsequent demand after admission, not the already executed target in the current window. Up to three copies remained pending at individual output cutoffs; these were not counted as ready/useful. The next request drains outstanding copies before prefill.

The OFF guard reproduced the original P1 output IDs, MTP and normal routing on all six pairs. ON changes CPU/GPU placement and can change floating-point rounding, generated text and the MTP trajectory. These are controlled same-input application measurements, not fixed-route kernel timing.

## Mechanism and safety

Native GPU gate/top10 signals at horizon eight cover five target layers. Admission combines this signal with observed heat, recency, resident age, a replacement margin and actual expert blob bytes. The final predeclared policy uses a 64-window utility horizon and 64 MiB/device batch budget. Victims and destinations must fit the existing physical slot class on the owning GPU; reservations cannot overlap.

Weights stay in the immutable system-RAM arena. Promotions issue asynchronously after completed verify readers, overlap commit/draft, and publish identity only after checked copy completion. A promoted expert remains resident across future uses; there is no restore after one use, D2H weight writeback, expert substitution or combined 48 GiB cache.

The available native suite passed 62 tests with two skips. Four known fixture/environment failures were explicitly excluded; they are not reported as passes. The repaired v2 targeted suite passed 15 tests. The ten-prompt greedy battery passed scoped finite-head/math/JSON checks; five outputs were exactly identical and all divergences are preserved. Real promoted VRAM weights matched immutable RAM for 1793/2472 experts, 3.609/4.949 GB, in separate post-timing audits. Shared selector/state tests checked owner, size, reservation and publication identity. These checks do not prove every interleaving or general quality parity.

## Copy diagnostics

One separate diagnostic run per profile retained exact output IDs, MTP and routing relative to clean ON replicate 1. Enqueue/staging, exposed adaptation-thread join and pending publication waits overlap; they must not be summed into a fabricated speed forecast. Exact GPU copy completion timestamps were unavailable: checked publication gives an upper-bound observation.

- 32k: PARITY_PASS, enqueue 27.028 ms, exposed join 1.030 ms, pending wait 39.039 ms. 146/1793 promotions had recorded router prediction; most used observed demand. 127 already missed after prediction and before enqueue. Median reuse was 67.0 routed entries per useful admission.
- 128k: PARITY_PASS, enqueue 30.517 ms, exposed join 3.315 ms, pending wait 59.607 ms. 201/2524 promotions had recorded router prediction; most used observed demand. 168 already missed after prediction and before enqueue. Median reuse was 52.5 routed entries per useful admission.

## Interpretation, failures and preserved evidence

Corrected warmup-chain fixed-trace replay produced 73,926/79,719 nonlocals versus CURRENT 36,776/45,276, while copying 3.941/4.809 versus 10.697/14.373 GB. Persistent reuse amortized individual promotions, but the policy retained a worse overall set of experts. Live CPU and mapped-PCIe work increased. The limited signal, approximate utility and admission after the first predicted demand constrain the result; free-generation/MTP changes also contribute. Lower traffic alone did not improve decode.

The initial conservative policy was rejected after one preserved 32K screen: 142.7 versus 179.7 TG, with 18.9% longer wall time. The single predeclared repair was then frozen for the final matrix. No tuning continued until a favorable outcome appeared. A float-validation error and two patch-anchor failures are preserved in separate source/build attempts; none generated headline measurements.

Future work should improve causal victim/lifetime utility and prediction coverage, and investigate an earlier safe copy mechanism that avoids host CUDA calls inside a spinning verify graph. Cross-GPU redesign and learned scoring were not required for this bounded conclusion.

Reproducible evidence: [summary JSON](summary.json), [CSV](summary.csv), [fairness audit](v2-fixed/fairness-audit.json), [source safety](analysis/source-safety.md), [correctness](analysis/correctness.md), [copy diagnostics](analysis/copy-diagnostic.json), and [build/patch commands](v2-fixed/build/commands.json). Each summary cell lists its raw paths; unavailable counters remain null.

Source: `93e31983c5735453e1f8be5fe143cb4a3f0538b9`. Binary SHA256: `bbcb31426701349e900ef621e187556ffdf9e1fc7d3d701beff080f60a923b19`. P1 and the previous research data remain unchanged.

USE_P1_BASELINE
