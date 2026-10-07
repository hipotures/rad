# Q4 Residency v2 — admission, eviction and causal prefetch

KEEP_Q4_100US_BASELINE — Retain the unchanged Q4/100us control. History raises primary median paired TG by1.9%,3.7%,2.9% at32/128/256K, but median paired whole-request reductions are only1.1%,1.9%,1.0%, below the3% practical aid. Its32K third attempt regresses and held-out results are mixed/noisy. Early persistent promotion is implemented and target-ready copies are observed, but it provides no consistent end-to-end gain and spends most staged bytes on unpublished candidates. All ON primary outputs diverge from control; identical control output/MTP/routing still shows substantial short-task timing variability. Do not switch the reference on these small application-level differences.

## Verified baseline and protocol

Qwen3.8-Flash-Next UD-Q4_K_XL, revision38bb39ee97821de2c9009abb7e93950eec396e66. Frozen Strata0.1.39 source6f32ec070f23ced9f50e704d854d775da52591ab; original binaryeca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d. K24,PCIe0.28,workers15,pool100us,spec4/min-p0.5,INT8,kv-resident32768 where valid,prefillauto,lookup/reuse0,greedy/serial.2×409024GiB,PHB/noNVLink/noP2P,16vCPU7950X3D,~161GiB/no swap. Model/pack/profile/PLE/MTP provenance and actual native commands/environments are retained under git/,configs/ and every raw attempt. Shared existing expert-profile is verified baseline input, not claimed Q4-exclusive training.

Fresh server per attempt, identical4096-input/64-output warmup, three rotated paired attempts per profile with4096 output.32/128 inputs preserve prior pool-study families;256 input leaves output/reserve rather than using259K input. Exact actual input IDs/hashes are checked with the real service tokenizer. Sources/builds are isolated; normal user launchers and weights remain untouched.

The older multi-GPU campaign used one server with sequential measured requests. The immediately preceding pool-spin study instead used the same fresh-process and fixed 4096-input/64-output warmup protocol as this campaign. Its six 100 us controls have exactly matching input/output IDs, MTP/window/routing counters, startup capacities, binary, model, launch arguments and relevant environment. Therefore the timing difference below cannot be assigned to a warmup-protocol difference. Its cause remains unassigned; identical visible counters do not identify an exclusive environmental cause. No historical median is used as a controlled residency speed comparison. The 256K 100 us setting is carried forward, not independently established as a spin optimum.

|Total limit|Previous pool study PP|Current control PP|Previous TG|Current TG|Previous wall s|Current wall s|
|---:|---:|---:|---:|---:|---:|---:|
|32768|1852.4|1610.3|97.0|109.9|57.74|54.96|
|131072|2075.2|1789.2|80.2|92.4|112.77|115.99|

This is historical sensitivity, not a controlled residency A/B. Contemporaneous controls were interleaved with the live candidates; no pool sweep was repeated. The compatible Phase A 256K control was retained, so no fourth primary control attempt was added. Full six-pair comparison: [historical-control-compatibility.json](analysis/historical-control-compatibility.json).

## Phase A — measured headroom

All nine Q4 traces reconcile every routed entry and exact current-selector slot evolution. All-demand includes rejected MTP branches,CPU,mapped and local work. Routed RAM arena77,017,907,200bytes/71.73GiB;24576 experts with native3.072/3.584/3.9936MB classes. Original resident allocation is roughly11.4K experts, not a universal configured constant. Decode logical expert-file reads are separately recorded, not inferred from aggregate disk counters.

|Profile|Actual input|All-demand local %|CPU entries|Mapped entries|Diagnostic promotion GB|Victim-absent entries*|
|---|---:|---:|---:|---:|---:|---:|
|32k|28378|89.66|196292|31135|87.42|151049|
|128k|126715|88.90|231342|36617|99.37|185345|
|256k|257781|90.09|213972|32924|96.48|168745|

*Descriptive observed absence, not an exclusive latency oracle. Capacity-only clairvoyance can eliminate misses with relaxed timing and hundreds ofGB of replacements; transfer-aware next-use is a feasible modeled heuristic, not an optimum/bound. Newly measured existing pinned-batch copies support~13.2GB/s/device. Original modeled joins3.055/3.641/3.409s are~6–7% below observed3.269/3.863/3.615s. Earlier separate staging must charge CPU memcpy/queues/publication; its rate is not free. Selected exposed CPU-positive waits and mapped execution are measured without summing overlapping timers or multiplying three layers by48. Full sensitivity/reuse/cost tables: [Phase A](phase-a/report.md).

## Phase B — complete family ledger

|Family|Status|Disposition|
|---|---|---|
|current|MIXED|Retained per-episode results; see Phase B for measured tradeoff and limits.|
|ema|MIXED|Retained per-episode results; see Phase B for measured tradeoff and limits.|
|frequency|COMPLETE_NEGATIVE|Retained per-episode results; see Phase B for measured tradeoff and limits.|
|hybrid-history|MIXED|Retained per-episode results; see Phase B for measured tradeoff and limits.|
|jev-linear|COMPLETE_NEGATIVE|Retained per-episode results; see Phase B for measured tradeoff and limits.|
|jev-mlp|COMPLETE_NEGATIVE|Retained per-episode results; see Phase B for measured tradeoff and limits.|
|jev-temporal-mlp|COMPLETE_NEGATIVE|Retained per-episode results; see Phase B for measured tradeoff and limits.|
|least-stale-inspired|COMPLETE_NEGATIVE|Retained per-episode results; see Phase B for measured tradeoff and limits.|
|markov|COMPLETE_NEGATIVE|Retained per-episode results; see Phase B for measured tradeoff and limits.|
|recency|MIXED|Retained per-episode results; see Phase B for measured tradeoff and limits.|
|static|COMPLETE_NEGATIVE|Retained per-episode results; see Phase B for measured tradeoff and limits.|
|static-development-only|COMPLETE_NEGATIVE|Independent held-out and long-document demand poorly served by2-task development profile; do not replace runtime profile.|
|native-router-H1/H4/H8|MIXED|H1 has stronger membership but most staged candidates late; H4 ready on dev but85% selected-nonresident predictions wrong; H8 weaker plus third spare.|
|early-linear-hybrid|MIXED|Charged2-spare H4 projection, immutable same-layer slot classes, guarded target publication and persistent retention; small miss reduction with high discarded copy traffic. Live test needed.|
|Basal-semantic-prior|NOT_ATTEMPTED|Only6 independent short task traces; no justified learned semantic-to-Q4-expert map. CPU EagerBackend run_shared flattens full forwards; large checkpoint cost not justified. No Polish/translation benefit claimed.|

The local Expert-Jev-inspired linear,32-unit MLP and bounded16-window temporal extension were trained CPU-only on complete dev-code/dev-math episodes, calibrated on cal-prose and evaluated on untouched hold-code/hold-math/hold-structured. Normalization/calibration never fit holdout. Targets are nonexclusive future counts with censored trace ends; joint finite-byte incoming/victim utility uses explicitly approximate costs, not a fabricated request-time oracle. Checkpoints,seeds,learning curves and inference/selection costs are retained. Cost-free held-out coverage does not predict finite-admission latency.

Learned policies reduced traffic by under-admitting and increased nonlocal work. Cheap history reduced long-trace copies with some extra misses; native H1 was often too late,H8 less accurate, andH4 had enough lead but a high conditional wrong-copy rate. The chosen live early pilot combines native H4 with CPU-only linear ranking/guarded victims, not a fully calibrated optimal transaction solver.

Basal semantic prior is NOT_ATTEMPTED: six short traces do not justify a semantic-to-Q4-expert map or large checkpoint download; its CPU EagerBackend shared path still flattens full forwards. No Polish/translation or published Jev-checkpoint benefit claimed. Primary sources pinned via gh/local material with licenses under sources/: Open-Jev,Fate,SpecMD/Least-Stale,Basal. Full decisions: [Phase B](phase-b/report.md).

## Phase C — controlled live results

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

## Frozen identities and memory envelope

|Variant|Source SHA|Binary SHA256|
|---|---|---|
|control|`6f32ec070f23ced9f50e704d854d775da52591ab`|`eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d`|
|history-v2|`9aff434de692ae16eeb05b9aa34064e31b095aba`|`1b449f2b68e4d18a839d16b9859535ca379e5808a28d1748a390e10b4b379eaf`|
|early-v1|`78a6559ec8ef6cc0db57ecd0ff4091a945ec8a7f`|`885609e9af4be0909017c9ffaa1052a2f21c4c91a228822ec53840e9a1899dc5`|

The CPU-only linear checkpoint is `checkpoints/linear.npz`, SHA256 `3c89b37a3b0a525c99eb5d57b8675aba6e92bbb0207b7da39e590b5d93dc5877`. Exported coefficient-header SHA256: `0e52b518080e80c0f4b2c6ca9d1de9e18fd41c02a49dbc88e237f34f16ef1927`. Exact commands, environment, compiler/CUDA flags, source patches and dependency locks remain under configs/, git/ and sources/.

|Profile|GPU0 physical slots|GPU0 cache GiB|GPU1 physical slots|GPU1 cache GiB|
|---|---:|---:|---:|---:|
|32k|6031|17.620|5510|16.077|
|128k|5999|17.520|5477|15.982|
|256k|5954|17.392|5432|15.851|

These exact baseline slot classes come from the validated traces. Clean startup capacities are checked per attempt. History preserves active capacity; early reserves one existing 3,072,000-byte slot on each owner GPU during decode, so active resident capacity is two experts lower. CUDA worker resources are initialized before auto sizing. Total-context limits include input plus output; they are not actual input counts.

Model pack: `/srv/ai/models/strata/packs/ud-q4_k_xl-v0132`; local UD-Q4_K_XL shards under `/srv/ai/models/strata/models/UD-Q4_K_XL/`. The pack-directory suffix does not select the runtime. Existing PLE, MTP and shared profile dependencies are explicit in each launcher config and `git/model.json`. The main model remains native GGUF; no new main-model experts.bin.

## Runnable handoff

The unchanged control and both safe experimental finalists have separate verified foreground launchers. All nine advertised32/128/256 paths actually reachedhealth/current native identity and generated the same64-output smoke; one wildcard-host override is exercised. They refuse hash/model/port/GPU conflicts and never rebuild/update.

```bash
cd /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-residency-v2-20261005T202441Z/launchers/control
./start-32k.sh
./start-128k.sh --host 0.0.0.0 --port 8080
./start-256k.sh
./stop.sh
./reproduce.sh --profile 128k --port 18140
```

Exact per-profile source/binary/env/config is in launchers/<variant>/*.json; logs and UI snapshots are under manual/. Reproduction starts three fresh servers, each with the same fixed warmup, and cannot add active-campaign repetitions. Experimental ON variants may diverge and are not universal production recommendations.

## Limits and next research

One bounded conditional-admission study on additional independent Q4 episodes: combine already available native-H4 gate confidence with numeric history to predict target-ready useful nonresident admissions and victim cost before enqueue. Keep the demonstrated safe two-spare scheduler and physical slot classes frozen. Train/calibrate on separate tasks, charge observed RAM staging/H2D/publication plus exposed CPU/mapped alternatives, and first require a held-out reduction in unpublished traffic without increased victim/nonlocal work. The current917/5917 publications and15.36GB unpublished of18.18GB staged copies identify admission validity as the narrow bottleneck. Do not immediately retrain a larger cosmetic MLP or infer gains from cost-free coverage.

Completed negatives remain in the ledger; optional untested semantic/longer-learning/alternate allocator directions are not disproven. No helper/pool retuning,weight change,driver/global change,push or PR. No experiment added to fill remaining time.

Start 2026-10-05T20:24:41+00:00; total elapsed 3.68h; hard deadline unchanged. Final audit confirms no owned serving/training/profiling GPU process remains. Raw/invalid/failure evidence and previous data are preserved.

KEEP_Q4_100US_BASELINE
