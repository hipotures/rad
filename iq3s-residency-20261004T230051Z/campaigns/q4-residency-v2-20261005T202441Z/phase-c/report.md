# Phase C — live Q4 residency validation

KEEP_Q4_100US_BASELINE — Retain the unchanged Q4/100us control. History raises primary median paired TG by1.9%,3.7%,2.9% at32/128/256K, but median paired whole-request reductions are only1.1%,1.9%,1.0%, below the3% practical aid. Its32K third attempt regresses and held-out results are mixed/noisy. Early persistent promotion is implemented and target-ready copies are observed, but it provides no consistent end-to-end gain and spends most staged bytes on unpublished candidates. All ON primary outputs diverge from control; identical control output/MTP/routing still shows substantial short-task timing variability. Do not switch the reference on these small application-level differences.

The primary27-point matrix is complete; two separate4096-output OFF guards, nine independent1024-output held-out application requests and diagnostic prediction/history cases are preserved separately. No fourth primary repetition or performance-based retry. Three attempts are not a statistical significance test.

A fixed 4096-token output ending with finish_reason=length means the budget was exhausted. It is not proof that the application produced a complete usable answer. The raw application_status, text, IDs and finish reasons remain preserved; no automatic quality ranking is inferred from throughput.

|Total limit|Variant|Valid/attempts|Actual input median|PP|TG min/median/max|TTFT s|Wall s|Decode VM CPU %|All-demand local %|CPU/mapped entries|Reported promotion GB|Victim damage|Predictor/selection cost|
|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---|---|---|---|
|32768|control|3/3|28379|1610.3|106.8/109.9/110.1|17.70|54.96|46.9|90.02|195875/30119|unavailable clean|diagnostic only|native; unavailable clean|
|131072|control|3/3|126716|1789.2|90.7/92.4/93.0|71.36|115.99|44.9|89.45|221528/35296|unavailable clean|diagnostic only|native; unavailable clean|
|262144|control|3/3|257783|2092.7|83.5/85.9/90.9|123.70|168.77|43.4|90.09|213972/32924|unavailable clean|diagnostic only|native; unavailable clean|
|32768|history-v2|3/3|28379|1602.9|98.3/112.0/114.5|17.81|54.35|50.7|89.53|196422/31740|45.41|diagnostic only|150.79ms/request|
|131072|history-v2|3/3|126716|1790.6|95.0/95.8/96.4|71.13|113.81|48.8|88.75|232786/37861|55.90|diagnostic only|170.91ms/request|
|262144|history-v2|3/3|257783|2099.3|87.9/91.2/93.5|123.32|168.25|44.0|90.35|211147/31080|48.49|diagnostic only|181.60ms/request|
|32768|early-v1|3/3|28379|1608.3|89.3/105.7/106.7|17.73|56.45|45.4|90.54|185488/28008|+18.44 predictive; native unavailable|diagnostic only|187.01ms/request|
|131072|early-v1|3/3|126716|1793.6|89.5/90.4/93.8|70.91|116.20|46.1|88.99|227866/36913|+20.74 predictive; native unavailable|diagnostic only|205.83ms/request|
|262144|early-v1|3/3|257783|2099.7|83.6/84.2/84.5|123.31|172.25|46.4|88.35|244873/40761|+21.10 predictive; native unavailable|diagnostic only|190.91ms/request|

History bytes include native history-selector exchanges; early bytes are additional staged copies and exclude native adaptive traffic plus6.144MB request-end reserve restoration. Clean speed has no per-admission victim counter. Unknown values remain unavailable, not zero. Raw paths, ranges, capacity checks, MTP and system phases are in summary.json/CSV.

## Paired request ratios

|Variant|Total limit|Pairs|TG ratio min/median/max|Wall ratio min/median/max|Identical output pairs|
|---|---:|---:|---|---|---:|
|history-v2|32k|3|0.9204/1.0191/1.0400|0.9759/0.9889/1.0556|0|
|history-v2|128k|3|1.0281/1.0366/1.0562|0.9752/0.9812/0.9920|0|
|history-v2|256k|3|1.0233/1.0286/1.0922|0.9730/0.9900/1.0757|0|
|early-v1|32k|3|0.8361/0.9618/0.9691|1.0216/1.0271/1.1313|0|
|early-v1|128k|3|0.9686/0.9967/1.0086|0.9874/0.9974/1.0144|0|
|early-v1|256k|3|0.9263/0.9732/1.0120|0.9995/1.0189/1.0812|0|

## Coarse decode progression

|Variant|Total limit|0–512 tok/s|512–1024|1024–2048|2048–4096|
|---|---:|---:|---:|---:|---:|
|control|32768|104.9|114.6|110.1|108.4|
|control|131072|89.5|92.6|88.4|92.6|
|control|262144|83.1|85.6|85.8|87.1|
|history-v2|32768|101.8|116.5|113.9|115.5|
|history-v2|131072|89.9|95.7|97.2|97.7|
|history-v2|262144|86.2|88.6|89.9|92.2|
|early-v1|32768|102.5|107.0|107.1|105.0|
|early-v1|131072|88.0|92.9|91.8|93.2|
|early-v1|262144|85.4|85.3|83.3|83.7|

These are medians of per-run interpolated actual-ID counter intervals at about 1 Hz. The first boundary uses TTFT and the final boundary includes request cleanup. They are diagnostic progression estimates, not exact native-window timings or separate headline repetitions.

## System telemetry

|Variant|Total limit|Decode CPU %|GPU0 decode %|GPU1 decode %|GPU0 decode W|GPU1 decode W|RSS GiB|
|---|---:|---:|---:|---:|---:|---:|---:|
|control|32768|46.9|53.9|52.9|156.0|173.3|76.2|
|control|131072|44.9|54.8|49.7|153.5|169.4|78.0|
|control|262144|43.4|53.3|52.4|155.9|169.9|79.6|
|history-v2|32768|50.7|49.8|52.6|155.9|173.9|76.2|
|history-v2|131072|48.8|52.4|51.0|155.2|172.3|78.0|
|history-v2|262144|44.0|50.6|51.6|159.0|175.7|79.6|
|early-v1|32768|45.4|53.3|52.4|154.7|171.3|76.2|
|early-v1|131072|46.1|53.3|51.3|152.8|167.5|78.0|
|early-v1|262144|46.4|55.7|49.7|151.7|164.9|79.6|

All 27 primary requests report zero logical expert-file blobs and 0.0 decimal MB during decode. These are request deltas taken after prefill; the native MB field is rounded to one decimal place. An exact file-byte counter is unavailable. These counters describe logical expert-file reads, not aggregate OS I/O. Direct full-arena CPU/mapped accesses are not all counted by the CS-T RAM-blob counter: zero RAM blobs does not mean zero RAM expert work. See summary.json/expert_file_reads_decode.


Ratios pair the same preserved input IDs.256K controlrep1 was completed earlier in Phase A; it is compatible but not temporally counterbalanced. The other two256K pairs are fresh/interleaved. Output/MTP can diverge after placement changes, so these are application-level free-generation ratios, not pure fixed-trajectory cache speedups.3% is a practical materiality aid, not a statistical test.

## Independent held-out application

hold-code is a complete independent inventory/SQL task excluded from development/calibration,72 actual input IDs,1024-output common budget,32K total limit. It is not a second128K document benchmark.

|Variant|Completed1024 / attempts|PP|TG min/median/max|Wall median s|VM CPU %|
|---|---:|---:|---|---:|---:|
|control|3/3|117.3|92.5/109.3/109.3|9.99|40.9|
|history-v2|3/3|116.6|94.9/96.7/111.6|11.22|46.1|
|early-v1|3/3|117.0|92.3/107.5/108.3|10.14|41.1|

## Transaction outcomes and matched scheduler ablation

|Diagnostic|Issued|Published|Copy GB|Unpublished GB|Local entries after admission|Victim-absent entries*|
|---|---:|---:|---:|---:|---:|---:|
|early-diagnostic|5917|917|18.18|15.36|24411|3176|
|early-reactive-diagnostic|2293|387|7.04|5.86|13922|1631|

History diagnostic: 14954 promotions, 46.60GB; 13807 observed used and 1147 not observed used before trace end; 12913 used across multiple windows; 121362 victim-absent entries. Exact demand/class/slot evolution validates against the buffered trace; clean/diagnostic parity is recorded rather than presumed.

*Victim absence is descriptive, not an exclusive causal latency counter. Near-end unused copies are right-censored. Early event tracking can miss native eviction/readmission between observations and excludes demand damage from the two initial spare withdrawals; that damage is unavailable separately and remains included in whole-request routing/latency. Reactive copies issue after their original miss; later ready publication is not prefetch of that earlier demand. Prediction-enabled readiness proves copy completion before target-plan release, not an exact GPU deadline timestamp. Equal warmup budgets/capacities do not imply identical warmed resident sets after ON divergence. The pilot covers five of48 layers, only3.072MB class. Details and clock/readiness distributions are in prediction-ablation.json/history-transactions.json.

## Correctness, footprint and progression

Both existing68-case suites have62PASS,2SKIP and the same four known fixture/environment failures as the original: ple_parity,platform_memory_test,expert_parity,pool_test. Relevant native Q4_K/Q5_1,Q4_K/Q8_0,Q5_K/Q8_0,router/cache/pool_stress tests pass. This is not an entirely green suite. Thirty seeded selector C++/Python states pass. The ordering proof runs200cycles/device with an active graph waiting on a separate host planner, concurrent main-thread stream synchronization, independent pinned copies/metadata and byte readback.

Failure details are retained in JUnit: ple_parity requires an unavailable legacy Q2_0 GGUF fixture; expert_parity and pool_test require unavailable pack/full/experts.bin fixtures; platform_memory_test cannot mlock its resident allocation under the existing memlock limit. No fixture model download or global limit change was made.

Each candidate in OFF mode matches original input/output IDs, MTP and routing on four short prompts and its separate 4096-output guard. ON first divergences are preserved; no logits/KL/top-1 harness or universal bitwise/quality claim. Exact sampled promoted backing bytes pass, including forced-wrong predictions. Predictions delayed by 5000 us remain safely late and unpublished. Intentional client cancellation drains and a subsequent fixed 64-output request succeeds.

Physical slot classes and per-GPU ownership stay fixed. Early worker resources are created before auto sizing, existing verifier scratch/gates are reused, and one existing3.072MB spare/device is charged during decode. No virtual48GiB pool or remote execution. Current-demand victims are protected; publication follows completion. Reserve setup affects TTFT and restoration affects request wall outside the native decode timer.

Progression is derived from1Hz actual generated-ID counters, never SSE-message count. Interpolated0–512/512–1K/1K–2K/2K–4K rates have sampled timing uncertainty and a request-wall endpoint including cleanup. Exact interval hit/MTP counters are unavailable. Aggregate PCIe samples cannot attribute individual expert transfers or prove saturation. See analysis/live-run-details.json.

## Repaired and negative results

Patch-application failures and analysis/parser preflights remain preserved. Healthy zero-non-finite summaries were initially misclassified by a substring checker; analysis was repaired without replaying any request or changing runtime. Reproducer preflight also found a one-server loop inconsistent with the primary protocol; it was corrected to a fresh server and fixed warmup for each of three attempts before any reproduction was run. No headline request was repeated for either repair. A negative run or outlier is never excluded for low TG. Learned linear/MLP/temporal finite-capacity under-admission and the narrow five-layer projection are evaluated as implemented, not proof that all learned residency policies fail.

## Decision

Retain the unchanged Q4/100us control. History raises primary median paired TG by1.9%,3.7%,2.9% at32/128/256K, but median paired whole-request reductions are only1.1%,1.9%,1.0%, below the3% practical aid. Its32K third attempt regresses and held-out results are mixed/noisy. Early persistent promotion is implemented and target-ready copies are observed, but it provides no consistent end-to-end gain and spends most staged bytes on unpublished candidates. All ON primary outputs diverge from control; identical control output/MTP/routing still shows substantial short-task timing variability. Do not switch the reference on these small application-level differences.

KEEP_Q4_100US_BASELINE
