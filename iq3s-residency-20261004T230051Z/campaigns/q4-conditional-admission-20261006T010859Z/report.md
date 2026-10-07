# Q4 Residency v3 — conditional admission before copy

Conditional admission rejects bad copies before staging and meets the pooled offline efficiency gate: unpublished bytes fall 73.76%, while 85.38% of next-four-window demand potential and 90.16% of observed contiguous local entries are retained. The latter attribution ends at the first native/early touch and is not a counterfactual exclusive-latency estimate. This is a mechanism result, not a deployment win. The 18-request matrix shows an apparent 32K application gain, a 128K tie and no 256K gain; independent code improves only 3.77% TG and structured text regresses 3.56%. All ON comparisons change output/MTP trajectories. Crucially, the new binary with the algorithm OFF already reaches 106.7 TG versus earlier control 93.9 with identical output/MTP/routing/capacity. That single later-time guard exposes build/environment confounding and prevents crediting the apparent 32K gain to the gate. Retain the unchanged Q4 100us baseline for real use; preserve conditional launchers as experimental.

Recommendation: **PROMISING_CONDITIONAL_ADMISSION**. The unchanged Q4 100 µs production reference remains available, and normal user launchers were not changed.

## Protocol and provenance

The control is Strata 0.1.39, source `6f32ec070f23ced9f50e704d854d775da52591ab`, binary SHA256 `eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d`. The conditional candidate has source `0266e540087acb98acd183546edeab3164aee8fd`, binary `dd52147462545bcfd5e30bd252a1ae83a92e890a5b03790720168c24b5772ffc`. It reuses early-v1 parent `78a6559ec8ef6cc0db57ecd0ff4091a945ec8a7f` in a separate local worktree/build.

Both builds use CUDA/sm_89 Release and the same control build options. Actual ggml CPU translation-unit sources and compilation flags match; linked libraries match. This rules out a different CPU compiler path as an explanation for the live timing difference. [Build commands](git/builds/conditional-v1/commands.json), [CPU build audit](git/CPU-build-flags-audit.json), [patch](patches/conditional-v1.diff), [hardware](git/environment.json).

The existing UD-Q4_K_XL revision is `38bb39ee97821de2c9009abb7e93950eec396e66`. Pack `/srv/ai/models/strata/packs/ud-q4_k_xl-v0132` is only the preserved model-pack name; no old runtime was selected. Native GGUF shards, profile and MTP were reused without downloads or weight changes. [Model identity](git/model.json).

Frozen common settings: K=24, PCIe fraction=0.28, pool spin=100 µs, workers=15, MTP spec=4/min-p=0.5, INT8 KV, kv-resident=32768, prefill=auto, suffix lookup=0, prompt reuse=0, greedy, serial execution. Each primary attempt uses a fresh server, the same 4096-input/64-output warmup and one measured 4096-output request. There are exactly three valid requests per cell, 18 in total. Actual input IDs match in all nine pairs; actual warmup counts match.

Physical startup expert capacities (GPU0/GPU1) are 6031/5510 at 32K, 5999/5477 at 128K and 5954/5432 at 256K, identical between arms. Conditional decode has two fewer active experts because of its existing spares. The total context limits are 32768/131072/262144. Actual inputs around 28.38K/126.72K/257.78K leave room for 4096 generated tokens and the engine reserve. The first 12 completed points were preserved when an order audit found that 256K would always start control first. At a request boundary, the driver was safely paused with its refuse-overwrite guard; no request was interrupted or repeated. Only the final six planned points were reordered, so every context includes both arm orders. [Original/corrected order](phase-c/order-repair.json), [plan](phase-c/matrix-plan.json), [raw IDs/configs](analysis/live-records.json).

The scheduler still uses the existing two 3.072 MB spares, one per GPU, costing two active experts during decode. Physical capacity, same-device ownership and five target layers (9,16,29,36,42) are unchanged. Publication still requires completed copy and an actually safe victim. The gate runs before enqueue, source access and staging; rejected actions create no expert-copy traffic. No extra expert VRAM, remote execution or mathematical expert substitution was introduced.

Start: 2026-10-06 01:08:59 UTC. Experiment cutoff: 08:28:59 UTC. Absolute deadline: 09:08:59 UTC. Work stopped earlier after the declared protocol reached a defensible conclusion. No broad policy search was reopened.

## LIVE RESULTS

| Context | Variant | PP | TG | Wall s | Local % | CPU entries | Nonlocal entries | Issued | Rejected before copy | Copied GB | Unpublished GB | Published useful | Victim absent* | Feature+gate ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 32k | control | 1,577.3 | 93.9 | 61.79 | 90.02 | 195,875 | 225,994 | — | — | — | — | — | — | — |
| 32k | conditional | 1,608.9 | 108.4 | 55.40 | 90.01 | 191,601 | 221,566 | 2,171 | 3,925 | 6.669 | 4.424 | 731 | 3,179 | 42.410 |
| 128k | control | 1,786.3 | 90.7 | 116.79 | 89.45 | 221,528 | 256,824 | — | — | — | — | — | — | — |
| 128k | conditional | 1,790.3 | 90.0 | 116.46 | 88.91 | 230,241 | 267,797 | 2,097 | 4,790 | 6.442 | 4.077 | 770 | 3,444 | 45.781 |
| 256k | control | 2,103.5 | 87.4 | 169.91 | 90.09 | 213,972 | 246,896 | — | — | — | — | — | — | — |
| 256k | conditional | 2,071.3 | 86.1 | 173.12 | 90.21 | 209,629 | 242,479 | 1,749 | 5,340 | 5.373 | 3.293 | 677 | 3,013 | 46.228 |

All headline values are medians of three valid runs. Local percentage uses all routed entries; nonlocal=CPU+mapped, summed per run before taking the median. GB is decimal. Disabled/unavailable counters are “—”, not fabricated zeros. *Victim absence is observed demand, not proven additional damage against a counterfactual native schedule. Protected-victim rejection subtypes, separate candidate-selection time and predictor-only CPU percentage were not independently logged; they remain unavailable, not zero. Feature+gate excludes the inherited early-history scorer and GPU H4 path, whose cost is also paid in wall time.

| Context | Variant | Actual input | PP min/median/max | TG min/median/max | TTFT median s | MTP accept % |
|---|---|---|---|---|---|---|
| 32k | control | 28378–28381 | 1,569.0/1,577.3/1,581.4 | 93.3/93.9/98.2 | 18.17 | 84.29 |
| 32k | conditional | 28378–28381 | 1,600.1/1,608.9/1,618.7 | 103.5/108.4/110.5 | 17.71 | 84.29 |
| 128k | control | 126715–126719 | 1,782.3/1,786.3/1,788.5 | 89.1/90.7/91.7 | 71.48 | 73.33 |
| 128k | conditional | 126715–126719 | 1,775.5/1,790.3/1,792.8 | 89.6/90.0/92.1 | 71.06 | 73.57 |
| 256k | control | 257781–257783 | 2,090.4/2,103.5/2,117.0 | 83.3/87.4/90.8 | 123.08 | 69.31 |
| 256k | conditional | 257781–257783 | 2,037.6/2,071.3/2,087.9 | 86.1/86.1/87.1 | 125.57 | 70.13 |

Every primary run generated 4096 recorded output IDs with reuse=0. TTFT is time to first visible content/reasoning token; wall excludes startup and warmup. No primary OOM, crash, early EOS or invalid request was discarded.

| Context | Paired median TG delta % | Paired median wall delta % | Paired nonlocal delta % | Same output IDs /3 |
|---|---|---|---|---|
| 32k | 12.53 | -8.44 | 2.03 | 0/3 |
| 128k | 0.56 | -0.32 | 6.28 | 0/3 |
| 256k | -1.49 | 1.89 | -4.51 | 0/3 |


Outputs and MTP trajectories can diverge when expert execution moves between existing CPU/GPU floating-point paths. Consequently these are controlled-input application-latency measurements, not fixed-output-trajectory speedups. Exact first divergence, offered/accepted drafts, verify windows and warmup parity are preserved in [paired evidence](analysis/live-pairs.json). Historical v2 speed values are not current controlled timing arms.

| Context | Variant | VM CPU % | Process CPU % | GPU0 % | GPU1 % | Power0 W | Power1 W | RX0 MB/s | RX1 MB/s | Peak RSS GiB |
|---|---|---|---|---|---|---|---|---|---|---|
| 32k | control | 49.6 | 710.0 | 52.7 | 51.9 | 148.9 | 161.8 | 2,744.0 | 1,600.1 | 76.22 |
| 32k | conditional | 46.4 | 715.2 | 53.0 | 51.7 | 154.0 | 170.1 | 3,833.2 | 2,109.6 | 76.24 |
| 128k | control | 45.4 | 695.0 | 55.0 | 50.8 | 152.6 | 167.0 | 2,986.3 | 1,604.4 | 77.98 |
| 128k | conditional | 45.3 | 703.3 | 54.4 | 49.1 | 151.9 | 165.9 | 3,356.0 | 1,869.8 | 78.00 |
| 256k | control | 42.7 | 660.8 | 52.4 | 52.4 | 156.0 | 170.1 | 2,559.0 | 2,138.4 | 79.63 |
| 256k | conditional | 42.3 | 651.1 | 52.9 | 51.8 | 154.0 | 169.1 | 2,389.3 | 1,644.1 | 79.65 |

Telemetry is sampled at about 1 Hz without PSS polling. Process CPU uses 100%=one core; VM CPU is normalized to all vCPUs. Summed RSS may include shared pages. Sampled PCIe includes all subsystems, not just expert traffic or critical-path waits. Prefill/decode VRAM, RAM available, power and TX are retained in [records](analysis/live-records.json). Rounded unique CPU-job means are separate from exact branch-entry counts. [Reported timing/costs](analysis/reported-timing-costs.json) retain overlapping CPU completion, host and GPU timers without claiming an exact compute/spin decomposition.

| Clean conditional context | Wrong median | Late min/median/max | Target-censored min/median/max |
|---|---|---|---|
| 32k | 1,437 | 1/2/3 | 0/1/1 |
| 128k | 1,323 | 0/4/43 | 0/0/1 |
| 256k | 1,009 | 0/63/64 | 0/0/0 |

Clean timing misses increase at 256K (median 63), so publication readiness is not perfect. Wrong candidates still dominate unpublished actions. Exact per-run counts are preserved; separate column medians are not an additive per-request funnel. Instrumented diagnostic late counts below are a different measurement.

**Attribution warning:** the apparent 32K ON gain is not established as a gate speedup. The candidate-OFF guard below already gains 13.63% TG with identical output/MTP/routing against the earlier control. Both build identity and noncontemporaneous environmental variation therefore remain timing confounds. At 128K the practical comparison is tied; at 256K there is no gain.

## Candidate-OFF timing guard

A single later-time 32K/4096 request using the new candidate binary with both mechanisms OFF has TG 106.7, versus 93.9 for the preserved primary control replicate 1. Exact full-length IDs/MTP/routing/capacity parity: True. The ratio 1.1363 is diagnostic only: this is not a contemporaneous replicated timing A/B and cannot isolate code layout from environmental drift. No fourth production-control repetition was run. This guard also checks whether a later experimental build without its algorithm can already appear faster. [Declaration](phase-c/ablation-plan-v2.json), [result](analysis/off-speed-guard.json).


## ADMISSION FUNNEL

| Diagnostic arm | Eligible | Rejected | Issued | Completed | Published | Target-used | Reused later | Staged GB | Published GB | Unpublished GB | Victim absent | Victim changed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H4-unfiltered | — | — | 6002 | 6002 | 1043 | 1043 | 764 | 18.438 | 3.204 | 15.234 | 3353 | 21 |
| reactive-only | — | — | 2293 | 2293 | 387 | 387 | 345 | 7.044 | 1.189 | 5.855 | 1583 | 23 |
| conditional | 6,007 | 3,766 | 2241 | 2241 | 758 | 758 | 630 | 6.884 | 2.329 | 4.556 | 3286 | 14 |

These traces use the same 32K input and 4096 output budget, with buffered diagnostic logging and canonical weight readbacks excluded from headline speed. Trajectories can differ, so cross-arm publication counts are not a fixed-trajectory recall estimate. Later-use attribution ends at the first observed native-cache touch or another early publication touching that expert; subsequent readmission is not credited as exclusive early residency benefit. Victim absence remains observational. H4 unfiltered reuses the Phase A trace rather than repeating it. OFF preserves control mathematics/capacity; reactive-only, H4 unfiltered and conditional flags are distinct. [Transaction traces and attribution](analysis/diagnostic-ablations.json).

## FAILURE REASONS

The original 4996 historical wrong-or-superseded outcomes remain underidentified: 15.347712 GB, plus four separately known late copies (0.012288 GB). The new diagnostic matches clean-v2 early replicate 1, but not the old diagnostic trajectory. We do not transfer newly observed labels to those historical actions.

| New matched diagnostic reason | Count | GB | % issued |
|---|---|---|---|
| prediction-wrong | 4959 | 15.234048 | 82.622 |
| became-resident-before-publication | 0 | 0.000000 | 0.000 |
| late-for-original-target | 0 | 0.000000 | 0.000 |
| request-ended-before-target | 0 | 0.000000 | 0.000 |
| no-safe-victim | 0 | 0.000000 | 0.000 |
| target-ready-persistent | 1043 | 3.204096 | 17.378 |

Prediction-wrong dominates count and bytes. Once issued, the worker cannot be superseded by another proposal; duplicates/inflight actions are prevented before issue. Early-v1 reserves no specific victim at enqueue, so “victim became protected” is not a defined failed-copy reason. A safe actual victim is selected at the target and can differ from the prospective victim. No generation-mismatch branch exists. Nineteen near-end actions have censored future-reuse labels, separate from known target outcomes. [Full category/source audit](phase-a/report.md), [12 episode counts/bytes](analysis/episode-failure-reasons.json).

| Diagnostic arm | Observed outcome | Count | GB | % issued |
|---|---|---|---|---|
| H4-unfiltered | prediction-wrong | 4959 | 15.234048 | 82.622 |
| H4-unfiltered | target-ready-persistent | 1043 | 3.204096 | 17.378 |
| reactive-only | prediction-wrong | 1835 | 5.637120 | 80.026 |
| reactive-only | target-ready-persistent | 387 | 1.188864 | 16.877 |
| reactive-only | became-resident-before-publication | 70 | 0.215040 | 3.053 |
| reactive-only | pending-retired | 1 | 0.003072 | 0.044 |
| conditional | prediction-wrong | 1442 | 4.429824 | 64.346 |
| conditional | target-ready-persistent | 758 | 2.328576 | 33.824 |
| conditional | late-for-original-target | 41 | 0.125952 | 1.830 |

The reactive trace additionally exposes 70 candidates that became native-resident before publication and one pending-retired action with an unobserved target (right-censored). The conditional trace has 41 late copies under instrumentation; this is not a clean-runtime deadline-miss estimate. These cases describe their own trajectories, not the historical 4996 aggregate.

## HELD-OUT RESULTS

Data comprise 12 independent tasks: four distinct code/module documents, four fully specified authored applied-math problems and four distinct authored structured/prose packets. Actual inputs range from 162 to 6991 tokens, with a 32768 maximum context; each generated 1024 tokens. The primary 28K/126K/257K inputs and 4096-output history therefore extrapolate the training conditions. Development has four tasks; calibration two; sealed holdout six, including the entire structured family. Neighboring document slices were not split across partitions. Exact task sources, input/output IDs, trace hashes and near-end censoring are in the [manifest](datasets/manifest.json) and [task splits](datasets/tasks.json).

The mandatory rule baseline and logistic model use causal H4 confidence/rank/margin, completed usage history, candidate state and prospective victim features. Logistic L2=1 and Platt calibration were frozen at p≥0.12 before holdout. Only three coarse rule and three coarse linear operating points were evaluated. No nonlinear model was justified; no holdout refit, threshold adjustment or unrelated parameter tuning was performed. [Feature definitions and unavailable quantities](datasets/feature-definitions.md).

Publication precision is 35.10%, count recall 80.68%, and PR average precision 0.5743, versus 0.5419 for history/state-only features on the same H4 candidate set. Confusion matrix: {'TP': 1211, 'FP': 2239, 'FN': 290, 'TN': 6293}. 107 near-end actions were excluded from future-use labels, not treated as negatives.

Unpublished traffic falls from 26.210304 to 6.878208 GB (−73.76%). The gate retains 85.38% of next-four-window demand benefit and 90.16% of observed later uses. It loses 290 of 1501 target-ready publications. Attributed nonlocal demand rises 250000→253356 (+1.34%). CPU entries rise 224423→227534; mapped entries 25577→25822. Retained victim-absent observations fall 1795→1523.

The pooled practical gate passes, but code holdout is weaker: only 72.24% later-use retention and +2.20% nonlocal demand. The original extra 2% per-family guard therefore failed. That false decision remains preserved. The user's numerical-aid judgment clause allowed experimental live testing of the SAME frozen p=0.12 candidate because the pooled gate passed; it did not justify retuning on holdout. [Strict result](phase-b/holdout-decision.json), [explicit decision](phase-b/live-gate.json).

Victim-damage prediction is weak: auxiliary R²=-0.0044, damage average precision=0.0390. This head was not deployed. The actual safe victim can differ from the victim scored at origin. Rules either retain too much waste or lose useful admissions; the conservative linear point also loses too much benefit. Negative thresholds/models remain preserved.

Offline transactions are fixed-native-schedule attribution, with same byte class/capacity and censoring at native touches. They are not a deployable oracle, an exact counterfactual adaptation simulation or a TG forecast. Measured Q4 staging/queue and H2D priors are 0.293449 ms and 0.25535 ms; a 0.25 ms/CPU-entry sensitivity is explicitly modeled, not an additive exposed-latency measurement. The hot ready-vector scalar costs 26.65 ns/action; full live history, features, selection and synchronization cost are reported separately. [Costs and curves](analysis/heldout-transaction-details.json), [calibration plot](analysis/plots/admission-holdout.png), [frozen traffic data](analysis/frozen-traffic-curve.csv).

## INDEPENDENT APPLICATION VALIDATION

| Held-out attribution | Issued | Staged GB | Target-ready | Unpublished GB | Wrong/resident | Late | Observed uses* | Victim absent* | Nonlocal | CPU | Mapped |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H4 unfiltered | 10033 | 30.821376 | 1501 | 26.210304 | 8336 | 196 | 55067 | 1795 | 250000 | 224423 | 25577 |
| Frozen conditional | 3450 | 10.598400 | 1211 | 6.878208 | 2139 | 100 | 49647 | 1523 | 253356 | 227534 | 25822 |

The frozen gate rejects 6583 evaluated actions before copy. 107 near-end actions are censored/excluded separately. Modeled net cost improves by 2834.994 ms versus unfiltered, under the explicitly approximate/overlapping priors; this is not measured request latency. *Aggregate event observations are checked against contiguous attribution below. Scorer-only cost is 26.65 ns/ready-vector action; it excludes full runtime feature/selection and queue costs.

Post-hoc attribution audit with the SAME frozen model and threshold retains 49647 of 55067 observed contiguous local entries (90.16%). Attribution stops at the first native or other early touch. This agrees numerically with the earlier aggregate event-use ratio in this heldout set, but does not prove exclusive avoided work against a counterfactual cache policy. Contiguous victim-absent observations fall 1790→1518. Next-four-window 'benefit' is future demand potential, not guaranteed resident or exclusive latency benefit. No fit, threshold or selection was changed by this reporting audit. [Strict contiguous audit](analysis/contiguous-holdout-audit.json).

**code-4**: median paired TG +3.77%, request wall -2.61%. Three fresh pairs; unchanged input IDs; maximum 1024 output; no rewritten tasks or favorable retries. Natural input lengths and termination are preserved. These short real tasks use a 128K-capacity server but are not 128K-input benchmarks.

**structured-4**: median paired TG -3.56%, request wall +3.37%. Three fresh pairs; unchanged input IDs; maximum 1024 output; no rewritten tasks or favorable retries. Natural input lengths and termination are preserved. These short real tasks use a 128K-capacity server but are not 128K-input benchmarks.

| Task | Variant | Actual input | Actual output range | PP | TG | TTFT s | Wall s |
|---|---|---|---|---|---|---|---|
| code-4 | control | 6991 | 1024–1024 | 764.0 | 102.1 | 9.19 | 19.24 |
| code-4 | conditional | 6991 | 1024–1024 | 777.0 | 107.1 | 9.03 | 18.58 |
| structured-4 | control | 172 | 1024–1024 | 129.3 | 98.5 | 1.35 | 11.75 |
| structured-4 | conditional | 172 | 1024–1024 | 129.3 | 93.4 | 1.35 | 12.29 |


Outputs, actual input/output counts, MTP, first divergence and raw request paths: [independent evidence](analysis/independent-live.json). These whole tasks were not fitted or calibrated; their earlier diagnostic routing episodes were part of sealed holdout, not new unseen sources. This limits the strength of a universal generalization claim. Within-policy control outputs, MTP and routing are identical across repetitions, yet structured-task TG ranges from 89.7 to 101.2. That timing spread is independent of admission changes; its physical cause is not established. [Stability evidence](analysis/independent-within-policy-stability.json).

## CORRECTNESS AND NEGATIVE RESULTS

Ten real CUDA scheduler/byte tests pass: good/bad prediction, rejection before enqueue with no staging, duplicate, native-resident candidate, protected victim, late/delayed copy, pending cancellation and next request, repeated spare reuse, request-end restoration and shutdown with pending work. Diagnostic requests compare the first 16 copied experts against canonical RAM bytes. HTTP cancellation with an artificial 5 ms copy delay drained successfully, and the next 64-token request completed.

The OFF build preserves exact output, MTP, routing and full capacity on two short tasks. ON produces no detected NaN and passes sampled byte checks; the code task first diverges at output token 33, while the math output is identical but MTP differs. This is correctness evidence against corruption, not proof of bitwise parity or a quality ranking. [Safety](tests/scheduler/result.json), [OFF/ON](phase-c/small-correctness.json), [cancellation](phase-c/cancellation.json).

Native suite: 62 pass, two skip, four unchanged fixture/environment failures out of 68 tests. `ple_parity` requires a missing Q2_0 PLE shard; `expert_parity` and `pool_test` require missing `pack/full/experts.bin`; `platform_memory_test` cannot mlock under the current limit. These are not new correctness failures, and the suite is not all green. [Exact failure output](tests/native-failure-causes.json). Dependency/path/NumPy-serialization preflight failures were preserved and repaired before measurements. The intentional order-checkpoint driver exit was a protocol guard, not an engine crash; no measured run was repeated. No negative threshold, holdout failure or unfavorable performance point was erased.

## Answers to the 20 research questions

1. **What did wrong-or-superseded contain?** The historical aggregate is underidentified. The new clean-matched trace contains 4959 wrong predictions and 1043 target-ready publications; independent episodes also expose late copies.
2. **Which reason dominated by count?** Prediction-wrong.
3. **Which dominated by bytes?** Prediction-wrong; every staged action is 3.072 MB.
4. **How predictable were useful admissions?** Held-out AP 0.5743, precision 35.10%, recall 80.68% at the frozen threshold.
5. **What did H4 add beyond history?** A modest AP gain on the same H4-selected candidate set. This feature ablation does not by itself establish a causal speedup versus a reactive scheduler.
6. **How predictable was victim damage?** Weakly; the auxiliary R² is negative and rare-damage AP low. The victim head was not deployed.
7. **How much wasted traffic was rejected?** Held-out unpublished bytes avoided: 19.332096 GB. Live pre-enqueue rejects and copied bytes are in the main table/funnel.
8. **How many useful admissions were lost?** 290 of 1501; count recall 80.68%, weighted next-four benefit 85.38%. Code is weaker.
9. **Did total nonlocal work change?** Offline attributed nonlocal entries rise 1.34%; live paired ratios vary by context and output trajectory. No universal miss-reduction claim.
10. **Did CPU fallback change?** Offline CPU entries rise 224423→227534; live exact CPU counts are in the table. CPU percentage is not a causal decomposition.
11. **Did copied GB change?** Yes, versus unfiltered early copies. The unchanged production control adds no early-copy traffic, so the candidate does not reduce added copies relative to OFF.
12. **What was predictor CPU cost?** Hot scalar 26.65 ns/action; full feature/gate and inherited-history timers are retained. Predictor-only CPU percentage is unavailable. Wall time pays all costs.
13. **Did TG improve at 32k?** Median paired TG +12.53%, wall -8.44%; three pairs, with output/MTP divergence documented.
14. **Did TG improve at 128k?** Median paired TG +0.56%, wall -0.32%; three pairs, with output/MTP divergence documented.
15. **Did TG improve at 256k?** Median paired TG -1.49%, wall +1.89%; three pairs, with output/MTP divergence documented.
16. **Did request wall improve?** See the paired wall table; prefill dominates long-input requests and decode gains cannot be evaluated alone.
17. **Did it generalize?** Independent task evidence is separated above. No universal claim follows from twelve diagnostic episodes or one favorable trajectory.
18. **Did output/MTP diverge?** All paired input IDs match; output/MTP and warmup-output checks are retained. Live speed comparisons are application-level.
19. **What is the remaining bottleneck?** Action validity remains the dominant copy problem: roughly two thirds of issued conditional copies are still unpublished. Victim utility is weakly predictable, and attributed nonlocal demand does not reliably fall versus control. Wrong predictions dominate; clean late counts increase at 256K (median 63), so publication timing also remains imperfect. Copy readiness is mostly adequate in clean runs; diagnostic late counts are instrumented and not headline estimates. Only five layers are affected. Output/MTP changes and demonstrated environment/build timing confounding prevent a causal throughput claim.
20. **What is the single best next experiment?** Before another predictor or victim policy, run one predeclared, counterbalanced same-candidate-binary OFF-versus-conditional comparison at 32K, ideally with a preserved fixed token/spec-window replay and same routing/accounting. This removes the exposed build difference and separates gating cost from free-generation/MTP and scheduling noise. Do not add it to this completed campaign or repeat controls to seek a win.

## RUN COMMANDS

Retained unchanged control, one server at a time:

```bash
cd /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-conditional-admission-20261006T010859Z/launchers/control
./start-32k.sh --host 0.0.0.0 --port 8080
./start-128k.sh --host 0.0.0.0 --port 8080
./start-256k.sh --host 0.0.0.0 --port 8080
./stop.sh
```

Separate safe experimental candidate, subject to the recommendation above:

```bash
cd /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-conditional-admission-20261006T010859Z/launchers/conditional
./start-32k.sh --host 0.0.0.0 --port 8080
./start-128k.sh --host 0.0.0.0 --port 8080
./start-256k.sh --host 0.0.0.0 --port 8080
./stop.sh
```

Launchers verify binary/source/model identity, print the complete config and refuse GPU/port conflicts. They never rebuild automatically. `reproduce.sh --profile 128k --port 18144` is enabled only after campaign completion and uses three fresh servers with identical warmup, not three requests on one adaptive cache. [Six actual launcher smokes](analysis/launcher-smokes.json). Normal user launchers remain unchanged.

## Final audit and unfinished work

Prior v2 files remain unchanged; full model SHA256 values match preserved hashes. No owned Strata, training or profiling process remains; both GPU compute lists are empty. [Process/provenance audit](analysis/final-audit.json), [previous-campaign hashes](git/prior-v2-final-verification.json), [full model hashes](git/model-final-fullhash-verification.json). Research/source commits are local only, with no push or PR.

Unfinished due to deadline: none in the bounded protocol. Exact exclusive critical-path cost, invisible native-cache interactions, unseen source generalization and future victim protection remain measured/model limitations, not invented zeros. No further residency implementation is started automatically.

PROMISING_CONDITIONAL_ADMISSION
