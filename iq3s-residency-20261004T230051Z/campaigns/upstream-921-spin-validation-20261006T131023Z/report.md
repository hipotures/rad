# Strata issue #921: default 20 ms versus 100 µs pool spin

On this single dual-4090 / 16-vCPU Ryzen 9 7950X3D KVM platform, 100 µs increased median paired decode throughput in all four cells: IQ3_S +10.98% at 32K and +10.03% at 128K; UD-Q4_K_XL +7.12% and +7.04%. There were 12 valid interleaved pairs per cell, 47/48 TG wins for 100 µs, and 48/48 bit-identical output trajectories with identical MTP and normal routing counts. Mean guest decode CPU fell by median paired 67–82%. One valid Q4 128K math pair regressed by 6.29%; it remains included. This supports lowering an unnecessarily long spin on this platform, while leaving universal default safety unestablished.

Campaign started **2026-10-06T13:10:23Z**; monotonic start **440143.63s**. Absolute deadline **2026-10-06T21:10:23Z**; substantial-start cutoff **2026-10-06T20:25:23Z**. Report rendered **2026-10-06T17:58:35.445490+00:00**, elapsed **4.804h**. Immutable timing file: `timing.json`.

## Source and binary

Latest release at start was **v0.1.40.1**, source **82f46a8c8f475f001ad76d92f58f4a4f8ffb0253**. Release notes say Python/server fixes only, unchanged engine. Local `git diff v0.1.40 v0.1.40.1 -- src include CMakeLists.txt cmake third_party` is empty. v0.1.40 source is 1cbcacbcae2953f3be9edc46369f0c875bc6ab8b. Clean detached upstream clone; no native changes. The same binary served both arms: `/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/upstream-921-spin-validation-20261006T131023Z/build/strata`, SHA256 **09f70d953f6d0009bdd555d06b72363aa9442fdb6f8f1a25250c6bf6a578dd94**.

GGML/llama.cpp pin: **3cf03257f219afbe7334045ff7c6a06ac68c627d**, downloaded using `gh api` and preserved as a hashed tarball. Compiler/toolkit/build commands, CMake cache, compile commands and full build log are retained. Release build, Linux CUDA, sm_89, native CPU features, static GGML, GGML OpenMP off, optional HIP MMQ off, native tests off. CMake defaults otherwise unchanged. CUDA runtime **13040**. Compiler: `g++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0`. Toolkit: `Build cuda_13.4.r13.4/compiler.38855100_0`. Python dependencies are frozen in the environment inventory.

The source still defines `kSpinBeforeSleep{20}` in `include/strata/kernels/cpu/pool.hpp:214`; `src/kernels/cpu/pool.cpp:437` reads `STRATA_POOL_SPIN_US` as microseconds. A uses the real default with the variable absent; B sets exactly 100. Every actual native environment was checked and hashed by key; the spin key was the only within-pair difference. PR #949 was closed/unmerged at start, and no pool-tasks option is present in the released native source. No task-granularity tuning or residency patches.

## Hardware and scope

One physical machine: **2×RTX 4090 24 GiB**, **Ryzen 9 7950X3D**, **16 guest vCPUs**, approximately 161 GiB guest RAM, no swap, KVM virtualization. NVIDIA driver 615.71.09; CUDA 13.4 runtime/toolkit. Topology PHB; CUDA peer access unavailable in both directions. Guest-visible PCIe is x8 on both GPUs: idle sysfs reports 2.5 GT/s, with maximum 16 GT/s x16 capability; measured decode samples report Gen4 x8. Complete topology, negotiation and clocks are retained in inventory and per-phase telemetry. Native main thread is pinned by Strata to CPU 0; all 16 CPUs are available to the guest, and this campaign did not change affinity, clocks, power limits, governor, VM or host settings. Worker behavior is the released default. Kernel: `Linux gpu 7.0.0-34-generic #34-Ubuntu SMP PREEMPT_DYNAMIC Wed Sep  2 14:29:37 UTC 2026 x86_64 GNU/Linux`.

Only expert-pool demand regimes differ: IQ3_S K25 versus UD-Q4_K_XL K24. Both are on this same GPU-heavy platform. We do not claim validation on a second machine, a CPU-only system, or a less GPU-resident platform.

## Frozen protocol and workload eligibility

Each cell targets 12 valid adjacent A/B pairs, with six AB/six BA, and 2 AB/2 BA in each family. Seed 92110020261006 plus cell index. First 10 have five AB/five BA and code/math/prose 4/3/3; full 12 have 4/4/4. The fixed round-robin cell order is IQ3_S 32K, Q4 32K, IQ3_S 128K, Q4 128K for each pair number; the paired arms always run adjacently. Exact orders are saved before measurement. Pair is the experimental unit.

Each arm: verify idle GPUs and exact identities/settings; launch a fresh server; verify resolved native config/environment/capacity; identical saved 4096-input/64-output warmup; one greedy 4096-output measured request; lightweight telemetry; stop owned server/engine; verify no residual owned/GPU jobs. Fresh processes prevent inherited adaptive-tier history. Same max-context=32768 or 131072, PCIe fraction=0.28, pool-workers=15, MTP spec=4/min-p=0.5, INT8 KV, requested KV-resident=32768, prefill=auto, suffix lookup off, prompt cache/reuse off, serial execution. Effective KV residency is recorded separately: in 32K, the engine reports 0 because the requested residency bound is not needed; 128K resolves it normally. No hidden K/MTP/worker/PCIe changes.

Payloads reuse the frozen E026 real repository, numerical-library and RFC source families, with three saved nonce variants per family/context; the fourth repetition reuses variant 1. Actual service-rendered input arrays and output arrays are retained, with hashes. This design repeats fixed corpora and does not represent a random sample of all code/math/prose workloads.

Q4 output-length qualification: the original saved code 32K variant 1 naturally stopped at 3788 before any B request. The entire original pair was objectively invalidated under the predeclared 4096 criterion and remains preserved. A common book-length instruction was then appended to **all** Q4 measured families, profiles and variants, with no source-text trim or sampling/config change, and frozen before any valid Q4 pair. Q4 and IQ3 therefore use slightly different completion instructions; each within-model A/B uses exactly the same IDs. No prompt was selected by 100 µs gain. One of the two predeclared Q4 32K replacement slots was used. Ledger lists any additional objective invalidations.

Startup/warmup/measured graph-capture messages are retained. No heavy profiling during headline requests. Built-in `STRATA_DECODE_TIMING=1` and `STRATA_SPLIT_TIMING=1` are identical in both arms. Append-only frontend ID capture performs no per-token disk I/O or timestamping; two cheap /proc snapshots delimit observed decode. The first completed IQ3 pair used owned-group SIGTERM; later pairs signal the server first for its normal native QUIT path. Both members of every pair use the same shutdown path; all cleanup checks passed.

## Primary paired results

| Regime | Context | Valid pairs | A default TG median | B 100us TG median | Median paired TG Δ | Median paired wall Δ | CPU A | CPU B | Median paired CPU Δ | B wins / pairs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| IQ3_S | 32768 | 12 | 155.25 | 172.60 | +10.98% | -6.30% | 93.14% | 16.92% | -81.25% | 12/12 |
| Q4 | 32768 | 12 | 105.60 | 114.60 | +7.12% | -4.09% | 96.15% | 29.30% | -69.58% | 12/12 |
| IQ3_S | 131072 | 12 | 143.60 | 160.40 | +10.03% | -4.83% | 94.28% | 16.21% | -82.28% | 12/12 |
| Q4 | 131072 | 12 | 101.85 | 107.00 | +7.04% | -2.83% | 96.94% | 31.40% | -67.24% | 11/12 |

| Regime | Context | Workload | Pairs | TG paired median Δ | Wall paired median Δ | CPU paired median Δ | Identical outputs |
|---|---:|---|---:|---:|---:|---:|---:|
| IQ3_S | 32768 | code | 4 | +20.39% | -11.63% | -81.34% | 4/4 |
| IQ3_S | 32768 | math | 4 | +10.51% | -6.21% | -78.54% | 4/4 |
| IQ3_S | 32768 | prose | 4 | +9.03% | -6.05% | -82.09% | 4/4 |
| Q4 | 32768 | code | 4 | +7.27% | -4.29% | -69.58% | 4/4 |
| Q4 | 32768 | math | 4 | +12.97% | -8.07% | -62.82% | 4/4 |
| Q4 | 32768 | prose | 4 | +3.52% | -1.63% | -70.84% | 4/4 |
| IQ3_S | 131072 | code | 4 | +13.71% | -7.38% | -82.31% | 4/4 |
| IQ3_S | 131072 | math | 4 | +7.01% | -1.98% | -78.54% | 4/4 |
| IQ3_S | 131072 | prose | 4 | +12.05% | -3.45% | -82.86% | 4/4 |
| Q4 | 131072 | code | 4 | +9.46% | -3.59% | -67.27% | 4/4 |
| Q4 | 131072 | math | 4 | +7.61% | -2.59% | -65.46% | 4/4 |
| Q4 | 131072 | prose | 4 | +6.46% | -2.09% | -68.19% | 4/4 |

| Regime | Context | Local % A/B | CPU entries A/B | Mapped entries A/B | MTP % A/B |
|---|---:|---:|---:|---:|---:|
| IQ3_S | 32768 | 99.01/99.01 | 23,681/23,681 | 680/680 | 74.41/74.41 |
| Q4 | 32768 | 96.05/96.05 | 92,999/92,999 | 8,350/8,350 | 68.87/68.87 |
| IQ3_S | 131072 | 99.04/99.04 | 22,681/22,681 | 573/573 | 73.36/73.36 |
| Q4 | 131072 | 94.53/94.53 | 122,879/122,879 | 13,486/13,486 | 70.34/70.34 |

TG/PP are native request rates; wall and TTFT are client-observed. CPU columns are per-request mean guest active CPU during decode, excluding idle, iowait and steal; steal is reported separately. Ratios are **median of B/A within pairs**, not ratios of medians. Negative wall/CPU changes are savings. Routing table uses median request counts and a common denominator: local VRAM + CPU fallback + mapped/nonlocal GPU = all routed. Local percentages are all-demand shares, not physical capacity percentages. MTP percentages are accepted/proposed.

## Distributions and small-sample support

| Cell | TG paired range | TG ratio IQR (Q25–Q75) | Median paired 95% bootstrap | Exact sign-flip p | AB/BA paired TG medians |
|---|---:|---:|---:|---:|---:|
| IQ3_S-32k | +0.46% to +30.41% | +8.07% to +16.31% | +7.91% to +16.95% | 0.000488 | +11.63% / +10.66% |
| Q4-32k | +1.53% to +20.92% | +2.52% to +12.77% | +2.49% to +13.16% | 0.000488 | +4.31% / +10.88% |
| IQ3_S-128k | +1.55% to +21.70% | +7.75% to +13.14% | +7.51% to +13.83% | 0.000488 | +9.08% / +11.18% |
| Q4-128k | -6.29% to +13.21% | +4.87% to +10.55% | +3.91% to +10.71% | 0.003906 | +9.83% / +6.79% |

A secondary order-randomization reference preserves the actual constraints: six AB/six BA, two AB/two BA per family, and five AB/five BA in the first ten. It enumerates 108 allowed assignments of labels to observed chronological second/first log TG differences. This reference assumes a sharp no-effect null and no unmodeled cross-pair interference; OS cache, thermal and host effects can remain. It was documented in `analysis-plan-addendum.json` after the first code pairs began and before math/prose measurements, retaining the original analysis and all primary metrics. It is supporting analysis, not a replacement for medians.

- IQ3_S-32k: constrained-order two-sided reference p=0.018519 over 108 assignments.
- Q4-32k: constrained-order two-sided reference p=0.018519 over 108 assignments.
- IQ3_S-128k: constrained-order two-sided reference p=0.018519 over 108 assignments.
- Q4-128k: constrained-order two-sided reference p=0.037037 over 108 assignments.

All raw-arm TG, wall, CPU, PP and TTFT min/max/Q25/Q75/IQR values, paired ratios and ratios of arm medians are in `summary.csv` and `summary.json`; every exact pair row is in `pairs.csv`. The TG sign-flip test enumerates all 2^N sign assignments of log(B/A), using absolute mean log-ratio and a two-sided tail. Its null requires exchangeable paired log differences; counterbalanced temporal order reduces but cannot eliminate drift. Bootstrap: 20000 paired resamples, percentile 95%, fixed seed 921100 plus cell index. Small N, repeated fixed corpora, and possible temporal dependence limit interpretation. No token or telemetry sample is treated as an independent observation. Medians and signs are primary; p-values are supporting description, not a binary default-setting decision.

## CPU demand, trajectory and system drift

Q4 provides a genuine CPU-positive comparison: median CPU fallback entries rise from IQ3_S 23,681 to Q4 92,999 at 32K (3.93×), and from 22,681 to 122,879 at 128K (5.42×). Median CPU experts per layer-window are 0.28/0.28 for IQ3_S versus 1.00/1.385 for Q4 at 32K/128K; CPU entries per layer-window are 0.31/0.30 versus 1.16/1.625. Q4 physical capacity is 46.68–46.94% of 24,576 experts, whereas its routed local share remains 94.53–96.05%; IQ3_S physical capacity is 75.75–76.13% and routed local share approximately 99%. These are distinct denominators. Descriptive CPU-demand quartiles have median experts/layer-window 0.27, 0.415, 1.00 and 1.555, with paired TG gains +11.10%, +9.32%, +3.52% and +9.51%. Benefit persists at the highest observed genuine CPU demand, but is not a monotone function of demand. Model, context, K and workload covary; these bins do not estimate a causal slope. No regression model was fitted.

The five setup-level questions: (1) IQ3_S remains clearly beneficial at +10–11%, though the pooled median does not reproduce 15%. (2) Q4 does not regress in either pooled cell; one valid math request regresses. (3) Aggregate CPU-section timing increases in all cells (+55–62% paired in IQ3_S, +19–21% in Q4), so a coordination/execution cost is visible, but isolated wake-up cost is not identified. No family has a negative median. (4) This does not establish that one global 100 µs default is unsafe; neither does it establish universal safety. The individual regression is retained as a limitation. (5) The positive pooled TG/wall medians and large CPU savings support the view that 20 ms is unnecessarily long for these workloads on this hardware.

All 48 valid pairs have identical actual input and output IDs. MTP proposals, accepted proposals, verify windows, local VRAM entries, CPU fallback entries, mapped/nonlocal entries and total routed counts each match in 48/48 pairs; expert capacities and native manifests match except for the spin variable. The 24 existing same-variant A–A/B–B comparisons are also bit-identical, without extra reruns. Thus observed timing differences cannot be explained by different generated tokens or the captured MTP/routing workload. This is a fixed observed trajectory within each pair, while trajectories differ across models, contexts and saved variants. Timing itself varies across repeated identical workloads; for example IQ3_S 32K code default TG changes from 135.9 to 119.7 tok/s between its two existing variant-1 repetitions, while B changes from 157.2 to 156.1. We do not turn repeated tokens or telemetry samples into independent observations.

Decode steal ranges across valid requests from 1.426% to 10.905%. Cell median A/B steal is IQ3_S 32K 4.67/4.51%, IQ3_S 128K 3.91/3.78%, Q4 32K 3.56/5.72%, and Q4 128K 2.77/6.89%. The sole TG regression is Q4 128K math pair 2, AB: 120.8→113.2 tok/s, TG −6.29%, wall +7.07%, with steal 1.68→8.84%. Its aggregate native CPU section increases 5.80→8.72 ms/window. Both CPU scheduling/wake coordination and VM/host interference are plausible; these measurements cannot isolate their contributions. Steal is not assumed exogenous: the spin policy could itself affect VM scheduling. No steal adjustment, timing exclusion or rerun was used. Both AB and BA subsets have positive cell medians. Request-mean GPU clocks stay approximately 2775–2790 MHz on GPU 0 and 2804–2805 MHz on GPU 1; temperatures span approximately 44–51 °C. Guest used RAM spans 55.2–82.8 GiB, native RSS 50.8–77.9 GiB, and measured swap is zero. This bounds observed drift without proving a controlled host environment.

| Cell | CPU steal median A/B | CPU steal range A/B | CPU experts/layer-window A/B | CPU entries/layer-window A/B |
|---|---:|---:|---:|---:|
| IQ3_S-32k | 4.671/4.507% | 2.358–10.382/2.083–7.089% | 0.280/0.280 | 0.310/0.310 |
| Q4-32k | 3.558/5.721% | 1.588–4.983/3.015–10.905% | 1.000/1.000 | 1.160/1.160 |
| IQ3_S-128k | 3.905/3.782% | 2.244–9.417/1.426–5.445% | 0.280/0.280 | 0.300/0.300 |
| Q4-128k | 2.771/6.889% | 1.678–4.791/3.946–9.407% | 1.385/1.385 | 1.625/1.625 |

| Cell | Native process CPU median A/B | Native CPU section ms/window A/B | Native host section ms/window A/B | Median paired CPU-section change |
|---|---:|---:|---:|---:|
| IQ3_S-32k | 97.56%/17.33% | 0.900/1.420 | 1.685/1.620 | +61.92% |
| Q4-32k | 98.81%/31.47% | 4.195/5.475 | 4.035/4.240 | +20.64% |
| IQ3_S-128k | 97.37%/16.63% | 0.885/1.430 | 1.600/1.465 | +55.04% |
| Q4-128k | 98.94%/34.68% | 5.815/6.935 | 4.650/4.760 | +19.45% |

Native process CPU uses `/proc/PID/stat` user+system tick differences divided by observed decode wall time and 16 vCPUs. Guest active CPU uses aggregate `/proc/stat` busy/total tick differences, with steal separate. These are separate guest accounting estimates, not quantities to add. The native CPU section is generally longer with 100 µs while total TG improves; this identifies an aggregate coordination/execution tradeoff, without isolating its cause.

MTP/routing parity counts and first output-divergence indices are in the audit/pair files. The repeated variant 1 checks compare A-against-A and B-against-B without extra reruns; `summary.json` lists them. For identical outputs and routing/MTP counters, timing differences cannot be explained by a changed generated trajectory. Any divergent pairs remain in the primary application-level free-generation analysis, with no correctness claim inferred from unequal text.

No exact per-worker spin/sleep counters are exposed. The retained CPU_completion_ms_per_window field is the native CPU dispatch/completion section plus remote/peer finish paths, normalized by verify windows. Its source definitions are preserved in provenance/native-cpu-timing-definition.txt and provenance/native-decode-timing-definition.txt. It does not isolate wake-up cost; overlapping stage timers are not additive. CPU utilization alone is not evidence of useful expert work; normal fallback entries and per-layer-window demand counters provide the workload measure. Mapped RAM versus remote GPU subcounts are aggregated where the released counter does not separate them. Graph captures are observed messages, not exhaustive CUDA graph-state instrumentation.

## GPU and memory telemetry

| Cell | Arm | GPU 0 decode util/power/VRAM | GPU 1 decode util/power/VRAM | GPU 0/GPU 1 prefill util | Native RSS | Guest RAM |
|---|---|---:|---:|---:|---:|---:|
| IQ3_S-32k | A | 48.0%/176.7W/23830MiB | 51.4%/203.9W/23950MiB | 27.3%/34.4% | 50.8GiB | 55.3GiB |
| IQ3_S-32k | B | 46.9%/183.6W/23830MiB | 53.6%/214.9W/23950MiB | 28.6%/33.8% | 50.8GiB | 55.3GiB |
| Q4-32k | A | 51.9%/161.2W/23836MiB | 51.2%/180.5W/24026MiB | 38.3%/44.7% | 76.1GiB | 81.0GiB |
| Q4-32k | B | 50.8%/168.8W/23836MiB | 53.3%/189.9W/24026MiB | 39.4%/44.7% | 76.1GiB | 81.0GiB |
| IQ3_S-128k | A | 47.3%/174.8W/23832MiB | 52.6%/201.2W/23950MiB | 40.5%/46.5% | 52.5GiB | 57.1GiB |
| IQ3_S-128k | B | 46.7%/182.9W/23832MiB | 53.4%/211.7W/23950MiB | 42.7%/45.8% | 52.6GiB | 57.1GiB |
| Q4-128k | A | 52.9%/160.4W/23834MiB | 51.9%/177.9W/24026MiB | 59.5%/62.8% | 77.8GiB | 82.8GiB |
| Q4-128k | B | 52.1%/165.8W/23834MiB | 53.0%/185.3W/24026MiB | 59.0%/61.3% | 77.8GiB | 82.8GiB |

These are medians of each request's mean 1 Hz phase samples, with samples wholly inside observed phase bounds. Request means, clocks, temperatures, power, VRAM, PCIe widths/generations and RSS/RAM/swap are in `requests.csv`; full raw samples, event flags and PSI remain in telemetry. Prefill bounds extend to the first observed native output token; decode bounds run from that token through native DONE, omitting the first-token work from CPU integration. Native decode timing remains the primary TG clock. GPU utilization sampling does not resolve individual kernels. No GPU power, clock or governor settings were changed. The installed CUDA 13.4 NVML header labels observed clock-event bit 0x400 as reliability policy limiting clocks; the definitions and raw flags are preserved. This does not identify the host policy or prove a cause of a paired timing difference.

## Figures

[Paired throughput and CPU changes](figures/paired-results.png); [CPU demand relationship](figures/cpu-demand.png). Exportable SVG/PDF versions are in `figures/`.

## Required interpretation

1. **Did IQ3_S reproduce the original approximately 15% class of gain?** It reproduced a clear throughput benefit, with smaller pooled central estimates: +10.98% at 32K and +10.03% at 128K. The original 15% point should not be presented as the new median. Code-family medians are +20.39% and +13.71%; paired bootstrap intervals include gains near 15% for 32K, but do not guarantee the historical result.

2. **What is the new median paired gain with 10+ interleaved pairs?** At 12 pairs per cell: IQ3_S 32K +10.98%, IQ3_S 128K +10.03%, Q4 32K +7.12%, Q4 128K +7.04%. These are medians of individual B/A TG ratios, not ratios of arm medians.

3. **How stable is the sign of improvement?** 100 µs wins TG in 12/12, 12/12, 12/12 and 11/12 pairs for IQ3_S 32K/128K and Q4 32K/128K respectively: 47/48 overall. IQ3_S 32K spans +0.46% to +30.41%, IQ3_S 128K +1.55% to +21.70%, Q4 32K +1.53% to +20.92%, and Q4 128K −6.29% to +13.21%. Magnitude varies substantially; both order subsets favor B in median.

4. **How much CPU does 100 µs save?** Median paired guest decode CPU reductions are 81.25%/82.28% for IQ3_S 32K/128K and 69.58%/67.24% for Q4. Raw request medians move 93.14→16.92%, 94.28→16.21%, 96.15→29.30%, and 96.94→31.40% of guest CPU. These are guest active CPU percentages excluding steal, not isolated spin counters. Native process CPU estimates independently fall from roughly 98–99% to 17–35% of the 16-vCPU capacity.

5. **Does Q4 still benefit with much more real CPU expert work?** Yes in both pooled cells: +7.12% and +7.04% TG, with −4.09% and −2.83% paired request wall changes. Normal CPU fallback demand is roughly 3.9×/5.4× IQ3_S at 32K/128K. CPU utilization savings are therefore observed while doing genuine expert work, rather than inferred from utilization alone.

6. **Is Q4 neutral, positive or negative?** Positive in the pooled medians at both contexts, with all family medians also positive. Individual near-neutral outcomes and the one −6.29% regression remain visible. This does not establish uniformly better latency on every request.

7. **Does 128K behave materially differently from 32K?** Median TG gains are similar within each model: IQ3_S differs by 0.95 percentage points and Q4 by 0.08 points. End-to-end wall savings are smaller at 128K because long prefill dominates more of the request: IQ3_S −6.30%→−4.83%, Q4 −4.09%→−2.83%. Q4 128K has greater real CPU demand and the only observed TG regression. These context comparisons also change the saved input corpus length and output trajectory; they are not an isolated context-only experiment.

8. **Does any code/math/prose family show a repeatable regression?** No family has a median regression in TG or request wall time. The twelve family TG medians range from +3.52% to +20.39%, each based on four pairs. Q4 128K math has one negative pair and three positive pairs; its median is +7.61%. Four fixed-workload pairs are descriptive and cannot exclude rare or workload-specific regressions.

9. **How often are outputs and token IDs identical?** 48/48 valid paired outputs are bit-identical in the actual token ID arrays; all paired inputs match. The 24 preplanned same-variant A–A/B–B repeat comparisons also match. No extra reruns were performed to achieve identity.

10. **Can timing differences be attributed to MTP or routing trajectory?** The captured trajectories do not explain the differences: proposals, acceptance counts, verify windows and every normal routing counter match exactly within all 48 pairs. Aggregate timing still includes GPU/CPU coordination, host scheduling and other execution costs that were not isolated.

11. **How much CPU steal and system drift remains?** Guest decode steal spans 1.426–10.905%, with materially higher B medians in Q4. GPU clocks are stable within the observed request-mean ranges, temperatures stay approximately 44–51 °C and swap remains zero. Exact repeat workloads exhibit timing variation. Counterbalancing reduces order bias but cannot remove VM scheduling, cache or thermal effects; no post hoc drift correction or exclusions were made.

12. **What evidence supports keeping 20 ms?** One valid CPU-positive Q4 128K math request favors default TG by 6.29%, and B's aggregate native CPU dispatch/completion sections are generally longer. Wake coordination and VM scheduling costs are not isolated. These are reasons to preserve caution for latency-sensitive or untested CPU-demand regimes; the pooled results do not show a performance advantage for 20 ms on this platform.

13. **What evidence supports lowering the default?** All four primary medians favor 100 µs, 47/48 TG signs favor it, both order subsets and all family medians favor it, and guest decode CPU drops by 67–82% while exact MTP/routing work remains unchanged. This is substantial evidence that 20 ms is unnecessarily long for these tested workload regimes on this hardware.

14. **Does the data support a per-phase or adaptive policy instead?** It motivates investigating such a policy, but does not establish its superiority. Native CPU dispatch/completion sections increase while total TG improves, and PP/TTFT medians are nearly neutral. No phase-specific or adaptive spin arm was tested, so these results cannot select an adaptive algorithm or its thresholds over a global 100 µs setting.

15. **What claims are unsupported because this is one VM?** Cross-machine validation, universal default safety, behavior on CPU-constrained or CPU-only machines, other GPU/NUMA/topology combinations, concurrent serving, other worker counts, task granularities, models or spin values, and a causal wake-up mechanism are not established. Fixed repeated corpora and possible temporal dependence also limit inferential generality beyond these paired requests.

## Prefill and first-token results

| Cell | PP median A/B (tok/s) | Median paired PP change | TTFT median A/B (s) | Median paired TTFT change |
|---|---:|---:|---:|---:|
| IQ3_S-32k | 2066.4/2048.1 | -0.02% | 13.835/13.984 | -0.17% |
| Q4-32k | 1409.2/1413.2 | -0.20% | 20.400/20.298 | +0.23% |
| IQ3_S-128k | 3068.6/3006.6 | +0.75% | 41.581/42.504 | -0.55% |
| Q4-128k | 2160.3/2112.7 | +0.02% | 59.362/60.605 | +0.10% |

PP and TTFT are separate outcomes. The total request wall includes prompt rendering/prefill and decode; a TG gain need not yield an equal wall-time gain at 128K. Family-level PP/TTFT distributions are in the JSON. No per-phase spin setting was tested.

## Reproducibility and exclusions

Valid A/B pairs: **48**. Bit-identical outputs: **48/48**. Objective invalidated pairs: **1**. Every attempted original/replacement directory is preserved; no timing- or trajectory-based exclusions. `invalid-pair-ledger.json` gives reasons, evidence hashes and replacement links. Minimum 10/maximum 12 per cell and the two-replacement bound are audited.

`scripts/analyze.py --require-complete` regenerates statistics and tables from raw arms. `scripts/render_report.py` creates this report and the unposted comment from those same tables and frozen interpretation. `scripts/audit.py` verifies binary/source/full model hashes, input/output IDs, counts/orders/families, all actual environments/configs, exclusions, serial execution, owned cleanup, reporting deadline and shared table text. See `reproduce.md` for one-cell/full-campaign commands. Initial and repaired runner copies, all saved v1/v2 payloads, frozen orders, build/source/environment provenance, raw streams/logs/telemetry, exact input/output arrays, summary CSV/JSON, script versions and final audit are preserved. No push, PR or GitHub posting.

Evidence summary: The requested 12-pair, counterbalanced medians favor 100 µs in both a highly GPU-resident CPU-light regime and a substantially more CPU-positive regime at both contexts, with large CPU savings and exact observed work parity. The conclusion supports a lower default for the measured platform and workloads; it is not a recommendation for universal safety or an upstream merge. The preserved individual regression and VM scheduling variation remain material limitations.

SUPPORTS_LOWER_DEFAULT
