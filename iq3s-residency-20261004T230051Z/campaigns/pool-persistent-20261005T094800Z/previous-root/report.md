# IQ3_S expert-residency research

Status: COMPLETE. Recommendation: PROMISING_NEEDS_MORE_WORK.

Elapsed: 9.81 hours; hard deadline 2026-10-05T09:00:51+00:00.

The strongest scoped result is the existing 100us CPU-pool sleep option on the unchanged CURRENT executable: 178.5/154.0 tok/s at the two total-context limits, with median decode CPU about 28.0%/25.8%. This preserves output/MTP/capacity in the saved workload. Increased CPU-positive wakeup waits and substantial same-output batch variation elsewhere prevent a universal 15% claim. Normal production launchers are unchanged.

The residency/prediction branches were executed through bounded replay, training, timing and runtime confirmation. None establishes a portable live selective-residency win. Persistent router-guided admissions and cross-device scheduling remain explicit untested directions, not completed negatives.

## Clean measured confirmations

| Candidate | Total context | Actual input range | PP min / median / max | TG min / median / max | TTFT s | Wall s | MTP accepted % | Valid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CURRENT control | 32768 | 28378–28381 | 3567.2 / 4739.5 / 4779.1 | 153.3 / 155.9 / 157.8 | 6.129 | 32.775 | 86.12 | 3/3 |
| CURRENT control | 131072 | 126715–126719 | 3979.8 / 5985.2 / 6012.7 | 124.2 / 133.2 / 153.1 | 21.688 | 54.640 | 77.86 | 3/3 |
| Frequency | 32768 | 28378–28381 | 3627.0 / 4740.5 / 4757.8 | 134.6 / 144.9 / 150.6 | 6.125 | 34.364 | 81.36 | 3/3 |
| Frequency | 131072 | 126715–126719 | 4012.9 / 6007.4 / 6016.0 | 121.5 / 131.3 / 135.3 | 21.582 | 55.255 | 75.41 | 3/3 |
| Compatible selector | 32768 | 28378–28381 | 3545.3 / 4745.3 / 4754.9 | 136.7 / 150.2 / 167.8 | 6.115 | 33.362 | 84.85 | 3/3 |
| Compatible selector | 131072 | 126715–126719 | 4294.5 / 5994.7 / 6040.9 | 155.8 / 157.8 / 158.5 | 21.401 | 47.529 | 79.19 | 3/3 |
| Compatible heap repair | 32768 | 28378–28381 | 3589.9 / 4755.8 / 4764.0 | 143.3 / 163.5 / 164.9 | 6.121 | 31.149 | 84.85 | 3/3 |
| Compatible heap repair | 131072 | 126715–126719 | 4002.6 / 5959.7 / 5968.5 | 132.5 / 134.3 / 135.9 | 21.776 | 52.179 | 79.19 | 3/3 |
| Same-binary policy OFF | 32768 | 28378–28381 | 3521.2 / 4759.9 / 4759.9 | 169.2 / 174.5 / 179.7 | 6.106 | 30.296 | 86.12 | 3/3 |
| Same-binary policy OFF | 131072 | 126715–126719 | 3993.8 / 5974.8 / 6000.5 | 122.0 / 139.2 / 141.9 | 21.700 | 51.106 | 77.86 | 3/3 |
| Safe device plan | 32768 | 28378–28381 | 3583.2 / 4735.7 / 4769.7 | 151.5 / 152.3 / 157.1 | 6.130 | 32.999 | 86.12 | 3/3 |
| Safe device plan | 131072 | 126715–126719 | 4009.7 / 5989.8 / 6001.9 | 123.3 / 133.3 / 136.4 | 21.677 | 54.894 | 77.86 | 3/3 |
| Skip redundant host plan | 32768 | 28378–28381 | 3589.8 / 4758.3 / 4764.2 | 156.4 / 175.4 / 179.3 | 6.108 | 30.864 | 86.12 | 3/3 |
| Skip redundant host plan | 131072 | 126715–126719 | 4013.1 / 6014.4 / 6024.9 | 138.7 / 158.7 / 159.3 | 21.530 | 47.234 | 77.86 | 3/3 |
| Same-binary host plan OFF | 32768 | 28378–28381 | 3515.1 / 4776.7 / 4777.5 | 152.6 / 163.6 / 180.3 | 6.092 | 31.114 | 86.12 | 3/3 |
| Same-binary host plan OFF | 131072 | 126715–126719 | 4016.7 / 6030.8 / 6032.5 | 127.2 / 159.0 / 161.3 | 21.271 | 47.056 | 77.86 | 3/3 |
| Direct expert output rows | 32768 | 28378–28381 | 3586.6 / 4751.5 / 4755.3 | 155.9 / 158.1 / 166.0 | 6.105 | 32.362 | 86.12 | 3/3 |
| Direct expert output rows | 131072 | 126715–126719 | 4006.3 / 5993.6 / 6041.9 | 133.1 / 160.6 / 163.0 | 21.633 | 47.127 | 77.86 | 3/3 |
| Same-binary direct rows OFF | 32768 | 28378–28381 | 3563.6 / 4777.5 / 4780.2 | 157.3 / 169.5 / 172.4 | 6.077 | 30.225 | 86.12 | 3/3 |
| Same-binary direct rows OFF | 131072 | 126715–126719 | 4006.3 / 5951.5 / 6000.7 | 131.4 / 144.4 / 153.2 | 21.782 | 52.951 | 77.86 | 3/3 |
| Existing pool sleep100us | 32768 | 28378–28381 | 3570.1 / 4734.5 / 4767.4 | 178.2 / 178.5 / 178.6 | 6.136 | 29.069 | 86.12 | 3/3 |
| Existing pool sleep100us | 131072 | 126715–126719 | 4040.1 / 5919.7 / 6019.8 | 144.1 / 154.0 / 165.4 | 21.900 | 48.484 | 77.86 | 3/3 |

All figures above come from the raw paths in summary.json/summary.csv. The first measured request can include lazy graph capture under the same 64-output warmup. All attempts remain included; no favorable-run replacement or extra unchanged repetition was used.

Only CURRENT is the primary reference. Historical v0.1.38/helper campaigns are evidence sources, not additional fresh controls. Same inputs/settings and budgets are preserved, but serial batches occurred at different wall times. A cache policy can also alter the free-generation/MTP trajectory.

## Interpretation and memory budgets

Keep the frozen CURRENT layer split unless later confirmation establishes a robust latency benefit. The compatible-slot policy's first 128K result is interesting but not an isolated policy win: an exact-choice heap repair produced identical visible output/MTP/accounting and substantially different TG. The same-binary OFF guard also differed from the original control while retaining its output and counters. These falsification results prevent interpreting a single median as a portable 18.47% improvement. They do not prove any particular VM, driver or binary-layout cause.

The two context profiles are actual total limits, 32,768 and 131,072. Saved inputs contain 28,378–28,381 and 126,715–126,719 effective tokens, respectively; output is 4,096 plus the recorded reserve. Complete source lines were trimmed deterministically from the preserved repository-maintenance workloads. Actual input IDs and hashes are shared by all headline configurations. No hidden context increase, output reduction, suffix drafts or prompt reuse occurs.

At 32K, GPU0 has 10,240 expert slots/19,824,128,000 bytes and GPU1 has 8,477/18,323,200,000 bytes. At 128K these are 10,183/19,712,998,400 and 8,437/18,220,492,800. Thus the smaller limit releases only 57/40 slots and about 106/98 MiB of expert capacity, not a large new cache. INT8 KV at 32K is fully resident; 128K retains 32,768 KV tokens with streaming. Each device remains a separate 24 GiB budget. Exact size classes, resource checks and startup telemetry are retained.

The native routed arena is already preloaded into RAM. Expert promotions are RAM-to-GPU traffic, not evidence of SSD streaming. PLE traffic, physical process I/O and unknown logical expert-file counters must remain distinct. Predictors cannot gain capacity by treating the two GPU memories as one freely accessible pool.

## What the tail counters and waits mean

Local hits count routed token/expert entries in local VRAM. Reported hit rate uses hits plus admitted/refused CPU entries and excludes mapped/remote work. The all-demand denominator must include mapped entries. Distinct CPU jobs, routed entries and bytes are separate quantities, including experts computed for rejected MTP branches.

The bounded original traces contain 35,552 CPU plus 1,224 mapped entries at 32K, and 43,557 CPU plus 1,719 mapped entries at 128K. The original selector exactly reproduces observed promotions and final float32 heat. Admissions copy immutable weights asynchronously, withdraw victims before use, and publish incoming identities only after completion; pending publication can stall the next window.

Selected-layer GPU event diagnostics show resident grouped expert compute around 65–79 microseconds, empty plan/mapped launches around 8–9, and CPU-completion wait floors around 4–5. Mapped-positive groups are substantially slower (roughly 164–195 microseconds median). Most CPU work overlaps resident GPU computation, while some CPU-wait tails extend tens or hundreds of microseconds. Only three layers were sampled. These times cannot be added indiscriminately, multiplied by 48, or attributed wholly to misses.

The measured boundary transfer is around 19–20 microseconds with tiny host handoff gaps. GPU-reach/tail waits also include dense, KV and resident computation. One-Hz PCIe samples cannot identify individual miss bursts or prove critical-path saturation. Hardware isolated copy capability is much higher than observed 1–2 GB/s bursts; the relevant uncertainty is contended copy readiness and exposed waits.

## Policy replay, future references and learned scoring

The replay charges actual per-device byte/slot classes, queue readiness and publications. Static, recency, frequency, EMA, stale-first/FIFO (explicitly adapted from Least-Stale), Markov and a bounded EMA/bigram hybrid were completed. Frequency reduced fixed-trace nonlocals but was slower in both live confirmations. A global paper scheduler was not silently equated to Strata's same-layer adaptation.

A transfer-free capacity reference can remove all observed nonlocals, but requires about 42/59 GB of replacement traffic. A stronger future-aware next-use heuristic reaches 4/3 nonlocal entries with 18.7/25.5 GB under optimistic 12.6 GB/s assumptions. It is a feasible heuristic within its replay assumptions, not a proven optimum, bound or causal deployable predictor. At contended rates, publication waits grow substantially. An offline miss reduction is not a measured TG gain.

Expert-Jev-inspired linear, 16-unit MLP and temporal MLP scorers were trained locally on independent development episodes, with a separate calibration episode and three held-out tasks. They predict expected near-future use counts rather than an invalid softmax interpretation of independent expert-use probabilities. Training seeds, datasets, fitted normalization/calibration and checkpoints are retained. These bounded scorers did not justify runtime deployment after capacity/transfer costs; the temporal ablation was worse. This does not exhaust learned prediction. Open-Jev source was pinned and inspected; no proprietary method or published decision-task performance was attributed to the local numeric scorer.

Compatible same-GPU, byte-fitting cross-layer victims improve offline nonlocal counts modestly. Live results are workload/batch dependent. The heap repair reduces selector CPU cost by about 64% while preserving all 672 replay choices, but did not yield consistent end-to-end improvement. Its unfavorable result and the OFF guard are preserved, not discarded or retried.

## Router prediction and coordination correctness

The original CPU router diagnostic accidentally reused stale activation rows for all-local groups because the normal doorbell omits those unused CPU activations. Its mixed fresh/stale quality verdict was withdrawn. A separate diagnostic forces fresh copies and proves unchanged model output/routing. Full CPU gates and rank-32/rank-128 projections then expose the real cost/readiness tradeoff; the held-out low-rank candidates are mostly late at contended rates.

Native GPU projection fixes that scoring-cost blocker: existing BF16 gate/top10/publication takes approximately 16–19 microseconds. It predicts roughly 69–71% of next-layer top-10 membership in the repository traces and has exact agreement with the same fresh full-gate CPU projection on recorded activations. However, its roughly 244-microsecond lead is shorter than many full expert copies under contention. Independent one-blob readiness estimates are optimistic, not a feasible scheduler. Queue/victim/restoration replay of a temporary within-window scheme has little useful contended tail coverage; this specific negative does not close persistent or wider-horizon prediction.

The GPU all-local planning experiment revealed two correctness hazards: shared routed-ID overwrite and an independent PLE producer dependency. Stable per-layer IDs solve the first; explicitly waiting for CPU-produced PLE before layer 1 solves the second. Native delayed-producer tests reproduce the failure on both GPUs. Strict same-binary snapshots locate the original arithmetic divergence at window 3/layer 1, and show exact numerical parity after the fence. An initial snapshot-directory failure and its vacuous parity conclusion are retained and explicitly excluded.

The safe repaired version matches full 4096-token output, routing, MTP, execution paths, heat and resident sets in both diagnostic profiles. Its clean confirmation offers no meaningful gain. Auxiliary bytes and unchanged expert capacities are recorded. Removing redundant all-local host plan construction was subsequently completed as E019, without changing the actual router, expert mathematics or admission algorithm. E022 uses the exact same binary with that option OFF: at 128K, OFF reaches 159.0 tok/s versus ON 158.7. The earlier apparent 19% gain over the first control therefore is not an isolated benefit of host-plan suppression. The 32K ranges overlap, and paired effects have both signs.

## Wider lookahead, row ownership and idle workers

E020 tested ten same-device pairs with four/eight-layer lookahead, then froze horizon eight from development/calibration before examining holdout labels. This uses existing unmodified gate weights and does not cross the layer-split boundary or assume P2P. Exact slot classes, distinct in-flight reservations, earlier-layer victims, the existing promotion queue and victim restoration are charged. At the contended 1.8 GB/s scenario, rank-first covers 6.85%/8.82% of the warm benchmark tail; a heat guard covers 0%/1.96%. Some independent tasks incur substantial modeled restoration waits. These are simulated readiness/copy costs, not measured TG. They reject this bounded temporary-swap scheme as a live candidate, while persistent placement remains open.

E021 adds a fifth scoped event phase for GPU planning and demand-doorbell publication. Host plan suppression lowers the all-local plan-wait median from about 8.2 to 4.1 microseconds and host dispatch from roughly 2.1–2.6 to 0.25–0.33. However, the separately measured GPU planning/doorbell phase increases from about 7–10 to 10–11 microseconds. These selected-layer timings cannot be summed into a whole-model speedup. Instrumented throughput is excluded.

E023 writes expert results directly into their final output rows and copies only CPU-owned rows, removing the final redundant zero/copy/add. The ownership fixture covers both GPUs, T=1/T=4, G=1/G=2, all-GPU/all-CPU/mixed jobs and captured graph replay with exact expected values. The first diagnostic omitted first-head capture and is explicitly invalid for full numeric parity; a separate repaired diagnostic establishes output/router/cache/head parity. The clean candidate has TG medians 158.1/160.6. The exact-same-binary OFF guard E025 reaches 169.5/144.4: ON regresses 32K by 6.73% and retains a 128K median advantage of 11.22%, with overlapping ranges and mixed paired signs. It is preserved for follow-up, not selected as a universal residency improvement.

E024 changes only the existing `STRATA_POOL_SPIN_US` from the default 20,000 microseconds to 100. It uses the exact clean control executable, 15 workers, unchanged expert capacities and all frozen model/inference settings. Native sleep/wakeup stress reports 13,783 batches without missed jobs; real IQ parity, ten identical short outputs and full 4096-token diagnostic parity pass. Clean TG is 178.2/178.6/178.5 at 32K and 144.1/154.0/165.4 at 128K. Relative to the compatible same-binary E002 control, medians improve 14.50%/15.62% and request wall medians fall 11.31%/11.27%. Every paired visible output, MTP and normal routing counter is identical. This particular gain cannot be explained by a more favorable MTP trajectory or extra cache capacity.

The clearer mechanism result is CPU use: median per-run mean decode system CPU falls from 99.25%/97.86% to 28.04%/25.85%, at almost unchanged GPU utilization. The source documents that parked pool workers spin before sleeping, so VM-wide 100% CPU was not a measure of useful expert computation. The change has a cost: selected-layer CPU-positive completion-wait medians rise from about 4–6 to 59–72 microseconds; all-local floors remain about 4–5. This is a real wakeup tradeoff, not free CPU capacity. The instrumentation is separate, and no multiplication over 48 layers or sum of these medians is asserted.

The 100us setting is the strongest scoped follow-up. Batch timing variability remains material elsewhere, the 128K rate still increases across its three serial requests, and only one long repository-maintenance workload was used. A portable 15% speedup and behavior under more CPU-heavy miss patterns are not established. Keep the current normal launcher unchanged while evaluating this explicit option on independent workloads.

## Evidence limits and next decision

Native testing retains four known fixture/VM failures: missing Q2_0 PLE/legacy expert fixtures and the VM mlock restriction. Python tests pass (268, seven skipped), and real native IQ expert parity passes. No new correctness failure is waived. Short arithmetic/schema checks are narrow validation, not an LLM judge or a broad model-quality ranking.

All headline batches use one fresh server per profile, the same 4096-input/64-output warmup and three serial measured requests. The repeated payload nonces prevent reuse but are not independent task documents. Predictor development uses distinct short task episodes. Clean output hashes and diagnostic token/logit checks have different scope. Large same-output timing differences remain unresolved, so minor three-run advantages are not universal wins.

Recommendation: **PROMISING_NEEDS_MORE_WORK**. The unchanged layer-split architecture remains the reference; the existing 100us pool option is the most promising completed latency/CPU experiment, not a new selective-residency algorithm. First test it against default on a few independent code/math/structured tasks with paired fresh starts and the same capacities, charging its measured CPU wakeup tail. Do not re-run unchanged campaign points beyond the three-attempt limit.

For residency itself, the strongest open direction is a persistent, byte-aware same-device admission scheme using the measured eight-layer signal, with reader safety, copy completion and victim reuse proven before live execution. Its missing implementation is recorded as NOT_ATTEMPTED under the finite wall-time limit, not a completed negative. Cross-device scheduling also needs staging/activation/capacity accounting; no P2P or free gate duplication is assumed. No production deployment follows automatically from this research.

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


## Decode progression at available resolution

| Candidate | Profile | TG0–512 | TG512–1K | TG1K–2K | TG2K–4K | Engine final TG |
|---|---|---:|---:|---:|---:|---:|
| CURRENT control | 32k | 115.7 | 196.1 | 178.0 | 147.0 | 155.9 |
| CURRENT control | 128k | 110.2 | 164.7 | 147.8 | 138.1 | 133.2 |
| Frequency | 32k | 134.0 | 145.5 | 162.8 | 137.4 | 144.9 |
| Frequency | 128k | 109.9 | 139.1 | 128.0 | 134.6 | 131.3 |
| Compatible selector | 32k | 132.7 | 133.9 | 175.0 | 145.6 | 150.2 |
| Compatible selector | 128k | 148.4 | 151.8 | 154.7 | 163.3 | 157.8 |
| Compatible heap repair | 32k | 117.9 | 135.0 | 159.1 | 172.9 | 163.5 |
| Compatible heap repair | 128k | 130.0 | 139.2 | 133.2 | 137.6 | 134.3 |
| Same-binary policy OFF | 32k | 148.3 | 177.5 | 180.5 | 179.8 | 174.5 |
| Same-binary policy OFF | 128k | 119.9 | 149.8 | 127.8 | 142.6 | 139.2 |
| Safe device plan | 32k | 128.0 | 174.4 | 160.7 | 160.7 | 152.3 |
| Safe device plan | 128k | 118.3 | 132.5 | 124.8 | 140.5 | 133.3 |
| Skip redundant host plan | 32k | 140.8 | 172.9 | 168.3 | 176.0 | 175.4 |
| Skip redundant host plan | 128k | 149.8 | 177.5 | 149.3 | 161.3 | 158.7 |
| Same-binary host plan OFF | 32k | 128.2 | 186.1 | 180.1 | 167.8 | 163.6 |
| Same-binary host plan OFF | 128k | 148.7 | 180.7 | 148.2 | 160.2 | 159.0 |
| Direct expert output rows | 32k | 139.9 | 168.9 | 172.9 | 156.8 | 158.1 |
| Direct expert output rows | 128k | 151.4 | 182.3 | 150.4 | 161.9 | 160.6 |
| Same-binary direct rows OFF | 32k | 135.2 | 203.9 | 171.6 | 169.9 | 169.5 |
| Same-binary direct rows OFF | 128k | 123.9 | 142.6 | 143.9 | 151.1 | 144.4 |
| Existing pool sleep100us | 32k | 154.9 | 192.6 | 186.0 | 183.0 | 178.5 |
| Existing pool sleep100us | 128k | 142.8 | 167.8 | 146.3 | 161.5 | 154.0 |

Intervals are median approximate client-wall rates derived from one-Hz live generated counts; full sample brackets and lower/upper bounds are retained in analysis/decode-progression/summary.json. They are not exact engine per-token timing. Interval MTP/cache counters are unavailable in clean builds. Separate E003 diagnostics show early cache/MTP changes, but do not establish their isolated contribution to clean acceleration.

## Decode system telemetry

| Candidate | Profile | VM CPU mean median % | GPU0 / GPU1 mean median % | Peak VRAM0 / VRAM1 MiB | Peak RSS sum GiB |
|---|---|---:|---:|---:|---:|
| CURRENT control | 32k | 99.2 | 45.8 / 52.8 | 23832 / 23952 | 50.99 |
| CURRENT control | 128k | 97.9 | 47.6 / 53.1 | 23828 / 23952 | 52.76 |
| Frequency | 32k | 97.6 | 45.4 / 50.6 | 23832 / 23952 | 50.99 |
| Frequency | 128k | 97.6 | 47.3 / 51.2 | 23828 / 23952 | 52.75 |
| Compatible selector | 32k | 99.0 | 45.5 / 51.6 | 23832 / 23952 | 50.99 |
| Compatible selector | 128k | 98.2 | 46.3 / 52.6 | 23828 / 23952 | 52.75 |
| Compatible heap repair | 32k | 98.8 | 45.6 / 52.2 | 23832 / 23952 | 51.00 |
| Compatible heap repair | 128k | 97.5 | 46.9 / 51.4 | 23828 / 23952 | 52.76 |
| Same-binary policy OFF | 32k | 99.2 | 46.2 / 53.0 | 23832 / 23952 | 50.98 |
| Same-binary policy OFF | 128k | 97.7 | 47.4 / 52.2 | 23828 / 23952 | 52.76 |
| Safe device plan | 32k | 99.4 | 45.5 / 50.4 | 23834 / 23952 | 50.99 |
| Safe device plan | 128k | 97.9 | 47.0 / 51.2 | 23830 / 23952 | 52.76 |
| Skip redundant host plan | 32k | 99.4 | 44.8 / 52.6 | 23834 / 23952 | 50.99 |
| Skip redundant host plan | 128k | 98.7 | 46.9 / 52.9 | 23830 / 23952 | 52.76 |
| Same-binary host plan OFF | 32k | 99.4 | 45.5 / 53.7 | 23832 / 23952 | 50.99 |
| Same-binary host plan OFF | 128k | 98.9 | 46.0 / 53.1 | 23828 / 23952 | 52.76 |
| Direct expert output rows | 32k | 99.3 | 45.7 / 52.9 | 23832 / 23952 | 50.99 |
| Direct expert output rows | 128k | 99.0 | 47.8 / 52.6 | 23828 / 23952 | 52.75 |
| Same-binary direct rows OFF | 32k | 99.3 | 45.5 / 53.2 | 23832 / 23952 | 50.99 |
| Same-binary direct rows OFF | 128k | 97.6 | 45.8 / 52.4 | 23828 / 23952 | 52.75 |
| Existing pool sleep100us | 32k | 28.0 | 45.3 / 55.5 | 23832 / 23952 | 50.99 |
| Existing pool sleep100us | 128k | 25.8 | 47.3 / 55.0 | 23828 / 23952 | 52.76 |

System CPU uses VM-wide0–100%; process CPU in the raw derivation uses one core=100%. Shared mappings can be counted twice in RSS sums. Power/clocks/RAM/physical-read sample distributions are retained in analysis/system-phases/summary.json. Physical-read deltas are not logical expert reads. One-Hz PCIe dmon cannot identify individual critical-path bursts.

## Experiment ledger

| ID | Latest state | Evidence |
|---|---|---|
| E001 | COMPLETE_POSITIVE | [E001-evidence](experiments/E001-evidence/report.md) |
| E002 | COMPLETE_POSITIVE | [E002-controls](experiments/E002-controls/report.md) |
| E003 | COMPLETE_POSITIVE | [E003-diagnostics](experiments/E003-diagnostics/report.md) |
| E004 | COMPLETE_POSITIVE | [E004-replay](experiments/E004-replay/report.md) |
| E005 | COMPLETE_NEGATIVE | [E005-expert-jev](experiments/E005-expert-jev/report.md) |
| E006 | COMPLETE_NEGATIVE | [E006-frequency](experiments/E006-frequency/report.md) |
| E007 | COMPLETE_NEGATIVE | [E007-causal-signals](experiments/E007-causal-signals/report.md) |
| E008 | COMPLETE_POSITIVE | [E008-router-boundary](experiments/E008-router-boundary/report.md) |
| E009 | COMPLETE_POSITIVE | [E009-placement](experiments/E009-placement/report.md) |
| E010 | COMPLETE_MIXED | [E010-compatible-runtime](experiments/E010-compatible-runtime/report.md) |
| E011 | COMPLETE_POSITIVE_DIAGNOSTIC | [E011-miss-waits](experiments/E011-miss-waits/report.md) |
| E012 | COMPLETE_POSITIVE_DIAGNOSTIC | [E012-compatible-diagnostic](experiments/E012-compatible-diagnostic/report.md) |
| E013 | COMPLETE_MIXED | [E013-compatible-fast](experiments/E013-compatible-fast/report.md) |
| E014 | COMPLETE_MIXED | [E014-policy-off-guard](experiments/E014-policy-off-guard/report.md) |
| E015 | COMPLETE_NEGATIVE | [E015-lowrank-router](experiments/E015-lowrank-router/report.md) |
| E016 | COMPLETE_NEGATIVE | [E016-device-plan-ids](experiments/E016-device-plan-ids/report.md) |
| E017 | COMPLETE_POSITIVE_SIGNAL_COST_NOT_LIVE_POLICY | [E017-gpu-router](experiments/E017-gpu-router/report.md) |
| E018 | COMPLETE_NEGATIVE_CONTENDED_TEMPORARY_SCHEME | [E018-router-transactions](experiments/E018-router-transactions/report.md) |
| E019 | COMPLETE_MIXED | [E019-skip-local-host-plan](experiments/E019-skip-local-host-plan/report.md) |
| E020 | COMPLETE_BOUNDED_FEASIBILITY | [E020-wide-gate-lookahead](experiments/E020-wide-gate-lookahead/report.md) |
| E021 | COMPLETE_SCOPED_DIAGNOSTIC | [E021-device-plan-waits](experiments/E021-device-plan-waits/report.md) |
| E022 | COMPLETE_NEGATIVE_ATTRIBUTION | [E022-host-plan-off-guard](experiments/E022-host-plan-off-guard/report.md) |
| E023 | COMPLETE_MIXED | [E023-direct-parts](experiments/E023-direct-parts/report.md) |
| E024 | COMPLETE_SCOPED_CONFIRMATION | [E024-pool-wait](experiments/E024-pool-wait/report.md) |
| E025 | COMPLETE_MIXED | [E025-direct-parts-off-guard](experiments/E025-direct-parts-off-guard/report.md) |

## Reproduction and preservation

See launch-index.md for exact frozen start/stop/reproduce commands, states and source/binary/config identities. Diagnostic and unsafe historical variants are labeled; they are not production recommendations. Reproduction must use new versioned output directories and obey the recorded three-attempt limit within this campaign.

Existing model files, quantization, profiles, services, older source checkouts and campaigns remain untouched. New patches and local commits are unpublished. No normal launcher was switched.

Final source/binary/patch identities and model metadata checks are in git/final-provenance.json. Compiler/CUDA/driver/topology/build commands remain in git/. Python package versions/licenses/origin limits are recorded in git/python-dependencies-final.json. Small artifact hashes and large on-disk size/mtime records are in git/artifact-inventory.jsonl; the audit is analysis/final-audit.json.

Every completed runtime point has exactly three valid measured requests: 22 cells/66 requests, each with 4,096 output tokens and zero reuse. Warmups and diagnostic/negative attempts are separate. Executable launch commands are mapped to experiment IDs in launch-index.md. The shared Session startup backend was exercised in normal flows; thin aliases are additionally syntax/help validated, not all separately smoke-started.

Every stage separates measured results, fixed-trace simulations and untested proposals. The deadline bounds the investigation; untested alternatives are not claimed exhausted.
