# Q4 layer-split: controlled CPU-pool spin comparison

**24/24 valid measured requests**; each 4096 output, zero reuse, suffix lookup OFF. Four policies × two total context limits × three preserved payloads. Every measured request has a fresh process and the same 4096-input / 64-output warmup. No extra measured repetitions, tuning, rebuild or engine/model change.

| Spin policy | Context | PP tok/s | TG tok/s | TTFT s | Wall s | CPU VM % | VRAM/all hit % | CPU entries | PCIe entries | MTP accept % |
|---|---|---|---|---|---|---|---|---|---|---|
| 100us | 32k | 1852.4 | 97.0 | 15.47 | 57.74 | 48.8 | 90.0 | 195875 | 30119 | 84.3 |
| 100us | 128k | 2075.2 | 80.2 | 61.61 | 112.77 | 48.4 | 89.4 | 221528 | 35296 | 73.3 |
| 500us | 32k | 1844.0 | 99.4 | 15.53 | 56.79 | 70.9 | 90.0 | 195875 | 30119 | 84.3 |
| 500us | 128k | 2070.8 | 81.6 | 61.73 | 111.89 | 70.5 | 89.4 | 221528 | 35296 | 73.3 |
| 2000us | 32k | 1852.5 | 90.9 | 15.48 | 60.54 | 83.2 | 90.0 | 195875 | 30119 | 84.3 |
| 2000us | 128k | 2076.3 | 75.3 | 61.56 | 115.93 | 83.8 | 89.4 | 221528 | 35296 | 73.3 |
| default20ms | 32k | 1855.7 | 92.5 | 15.45 | 59.80 | 99.0 | 90.0 | 195875 | 30119 | 84.3 |
| default20ms | 128k | 2076.6 | 76.5 | 61.57 | 115.16 | 99.0 | 89.4 | 221528 | 35296 | 73.3 |

All cells show medians of three runs. CPU% is median of request decode sample means, across 16 vCPUs. VRAM denominator is **all routed entries**, including CPU and mapped/PCIe; the UI local/(local+CPU) statistic is not used for the headline. PCIe entries are logical mapped expert entries, not sampled physical bytes.

## Run ranges

| Policy | Context | PP min / median / max | TG min / median / max | TTFT min / median / max | Wall min / median / max |
|---|---|---|---|---|---|
| 100us | 32k | 1846.4 / 1852.4 / 1860.0 | 94.6 / 97.0 / 108.5 | 15.40 / 15.47 / 15.51 | 53.21 / 57.74 / 58.69 |
| 100us | 128k | 2072.1 / 2075.2 / 2075.2 | 79.2 / 80.2 / 80.5 | 61.57 / 61.61 / 61.69 | 112.45 / 112.77 / 113.34 |
| 500us | 32k | 1839.6 / 1844.0 / 1845.6 | 96.4 / 99.4 / 100.5 | 15.52 / 15.53 / 15.58 | 56.27 / 56.79 / 57.98 |
| 500us | 128k | 2070.3 / 2070.8 / 2071.0 | 80.0 / 81.6 / 83.2 | 61.72 / 61.73 / 61.74 | 110.94 / 111.89 / 112.95 |
| 2000us | 32k | 1847.6 / 1852.5 / 1856.2 | 90.1 / 90.9 / 94.3 | 15.44 / 15.48 / 15.51 | 58.88 / 60.54 / 60.87 |
| 2000us | 128k | 2074.6 / 2076.3 / 2076.4 | 73.1 / 75.3 / 77.1 | 61.53 / 61.56 / 61.61 | 114.71 / 115.93 / 117.55 |
| default20ms | 32k | 1842.1 / 1855.7 / 1856.4 | 89.8 / 92.5 / 95.4 | 15.44 / 15.45 / 15.55 | 58.35 / 59.80 / 61.08 |
| default20ms | 128k | 2074.3 / 2076.6 / 2078.4 | 73.5 / 76.5 / 78.8 | 61.51 / 61.57 / 61.62 | 113.49 / 115.16 / 117.28 |

Every numeric metric also has min/median/max in summary.csv and summary.json; the individual run measurements remain linked from summary.json.

## Paired ratios to 100us

| Policy | Context | TG delta % | Wall delta % | PP delta % | CPU delta % |
|---|---|---|---|---|---|
| 500us | 32k | 1.90 | -1.21 | -0.69 | 45.39 |
| 2000us | 32k | -6.29 | 4.85 | 0.01 | 70.50 |
| default20ms | 32k | -5.07 | 4.07 | -0.19 | 102.91 |
| 500us | 128k | 1.75 | -0.78 | -0.21 | 46.62 |
| 2000us | 128k | -6.11 | 2.80 | 0.05 | 72.52 |
| default20ms | 128k | -4.61 | 2.12 | 0.11 | 104.43 |

These are medians of per-input paired ratios, not ratios of separately aggregated medians. Three samples are insufficient for narrow confidence intervals; the predeclared meaningful margin is 3%, with inconsistent direction/overlapping variability treated conservatively. No favorable-run retry.

## Selection and answers

1. **32K:** 500us has the highest nominal median TG (99.4 versus 97.0 at 100us), but its median paired gain is only **1.90%** and paired wall improvement **1.21%**. The paired TG direction reverses on one payload; ranges overlap. Under the predeclared 3% margin this is a performance tie. Select 100us for its lower CPU cost.
2. **128K:** 500us has the highest nominal median TG (81.6 versus 80.2), but median paired TG gain is **1.75%** and wall improvement **0.78%**. This is also a tie at the predeclared margin. Select 100us; no material context reversal supports separate policies.
3. **Does Q4 need a longer spin than IQ3_S?** Not for this preserved workload: a longer spin is not required for a defensible Q4 baseline. This does not prove 100us optimal for every real-prompt domain; the historical IQ3_S campaign is motivation, not this experiment's control.
4. **CPU cost:** decode VM medians at 32K are 48.8/70.9/83.2/99.0% for 100/500/2000/default. At 128K they are 48.4/70.5/83.8/99.0%. Relative to 100us, 500us consumes approximately 45–47% more CPU for less than 2% paired TG gain; default roughly doubles CPU. PP differences are small and do not justify a separate prefill policy.
5. **Useful work versus spin:** the exact CPU fallback medians are 195,875 entries at 32K and 221,528 at 128K; mapped GPU entries are 30,119/35,296. Routing is identical between paired policies. The substantial CPU load at 100us is compatible with real expert computation. The additional load at longer spins with unchanged work is consistent with idle spinning/scheduling overhead, but exclusive compute/spin fractions were not measured. All logical expert-file reads during decode are zero; this is resident-RAM work, not expert SSD streaming.
6. **Wakeup cost:** aggregate CPU completion means are 13.50/14.45 ms at 100us versus 12.03/12.80 at 500us for 32K/128K. That is consistent with some parking/wakeup cost, but the timer also includes computation and overlap; conditional CPU-positive waits and all-local floors are unavailable. It does not translate into a material whole-request penalty here. Default has lower CPU-completion means yet worse overall TG, demonstrating why that component cannot rank policies alone.
7. **Q4 residency-v2 baseline:** freeze **STRATA_POOL_SPIN_US=100** at both contexts, with the same frozen 0.1.39 executable, K=24 / PCIe=0.28, workers 15, spec=4 / min-p=0.5, INT8 and all other unchanged settings. No residency implementation or extra policy test was started.

Frozen selection: **USE_100US**. Policies: {"32k": "100us", "128k": "100us"}. This is the CPU-pool prerequisite for Q4 residency-v2; no residency research was started.

## CPU, GPU and completion waits

| Policy | Context | Slots GPU0/GPU1 | Process CPU % | Prefill GPU0/GPU1 % | Decode GPU0/GPU1 % | Decode power GPU0/GPU1 W | Decode VRAM GPU0/GPU1 MiB |
|---|---|---|---|---|---|---|---|
| 100us | 32k | 6031/5510 | 698.4 | 52.6 / 59.4 | 52.6 / 51.9 | 150.4 / 165.1 | 23836.0 / 24028.0 |
| 100us | 128k | 5999/5477 | 678.4 | 56.0 / 61.5 | 55.0 / 49.5 | 148.0 / 159.6 | 23836.0 / 24028.0 |
| 500us | 32k | 6031/5510 | 1099.7 | 48.1 / 59.2 | 53.4 / 51.6 | 151.6 / 166.2 | 23836.0 / 24028.0 |
| 500us | 128k | 5999/5477 | 1092.4 | 56.5 / 57.6 | 54.7 / 50.3 | 148.4 / 161.8 | 23836.0 / 24028.0 |
| 2000us | 32k | 6031/5510 | 1310.3 | 52.6 / 58.1 | 55.9 / 49.3 | 148.1 / 160.8 | 23836.0 / 24028.0 |
| 2000us | 128k | 5999/5477 | 1319.8 | 55.9 / 57.9 | 58.2 / 46.5 | 145.4 / 156.2 | 23836.0 / 24028.0 |
| default20ms | 32k | 6031/5510 | 1571.0 | 48.6 / 54.9 | 54.6 / 50.3 | 147.5 / 161.0 | 23836.0 / 24028.0 |
| default20ms | 128k | 5999/5477 | 1571.4 | 57.0 / 60.7 | 54.2 / 49.1 | 146.1 / 156.7 | 23836.0 / 24028.0 |

Process CPU 100%=one core; it cannot be compared directly to VM CPU 100%=all 16 cores. Capacity is identical for every policy within a context. Source-defined default is `kSpinBeforeSleep{20}` in include/strata/kernels/cpu/pool.hpp; the default engine environment was verified to omit STRATA_POOL_SPIN_US, not assume a numerical override.

| Policy | Context | CPU completion ms | GPU-reach wait ms | CPU experts/layer-window | CPU entries/layer-window | Decode window ms |
|---|---|---|---|---|---|---|
| 100us | 32k | 13.500 | 5.420 | 2.53 | 2.99 | 31.680 |
| 100us | 128k | 14.450 | 5.940 | 2.52 | 3.01 | 33.750 |
| 500us | 32k | 12.030 | 5.870 | 2.53 | 2.99 | 31.070 |
| 500us | 128k | 12.800 | 6.310 | 2.52 | 3.01 | 32.730 |
| 2000us | 32k | 13.230 | 6.150 | 2.53 | 2.99 | 33.240 |
| 2000us | 128k | 14.260 | 6.690 | 2.52 | 3.01 | 35.350 |
| default20ms | 32k | 11.100 | 7.150 | 2.53 | 2.99 | 33.300 |
| default20ms | 128k | 11.650 | 7.680 | 2.52 | 3.01 | 34.810 |

The unchanged binary exposes aggregate request-scoped CPU completion time, including overlapped compute/wait. **Conditional CPU-positive completion waits, all-local wait floor, exact worker sleep/wake counts and exclusive spin/compute split are unavailable.** They are null, never replaced with zero. CPU% alone does not identify useful work. No new hot-path instrumentation, PSS polling or profiler was used.

## Correctness and protocol

Actual tokenizer/engine input-ID hashes match in all 18 policy-vs 100us pairs. Actual input counts: {"32k": [28378, 28379, 28381], "128k": [126715, 126716, 126719]}. Output IDs identical in **18/18** pairs; aggregate offered/accepted/windows identical in **18/18**; local/CPU/mapped/all routing counters identical in **18/18**. First divergence and each counter delta are preserved in analysis/parity.json. Full per-window MTP trajectory is not available; matching aggregates alone do not prove trajectory parity. All output ID arrays contain 4096 IDs, finish_reason=length. Warmup inputs/counts are identical for all 24 starts; warmup output hashes are also retained. No crash, OOM, invalid request or early EOS occurred. No concurrency.

Fresh start before each measured request deliberately removes cross-request adaptive-cache history. This differs from the prior Q4 campaign, which used one server and three sequential measured requests per cell. Its PP/TG values therefore are **historical, not the control for this pool experiment**. The first full-length prefill is timed in every new run; PP is not made artificially warm by treating another full request as warmup.

## Provenance and reproducibility

Binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/control/strata`; SHA256 `eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d`; clean source `6f32ec070f23ced9f50e704d854d775da52591ab`; engine 0.1.39 verified in every startup/API. No rebuild. Hardware/topology records are under git/. Model: existing Unsloth UD-Q4_K_XL, revision 38bb39ee97821de2c9009abb7e93950eec396e66, four native shards plus compat-BF16 pack. Pack directory suffix v0132 identifies model data, not an old executable. Complete model sizes/mtimes/prior verified SHA and current pack/profile/MTP hashes are in git/model.json. Routed arena 77,017,907,200 bytes stays in RAM; request expert-file counters are retained.

Common settings: K=24 / PCIe=0.28, workers 15, spec=4 / min-p=0.5, INT8, kv-resident=32768, prefill=auto, greedy, same MTP/profile/tokenizer, CUDA_VISIBLE_DEVICES=0,1. At 32K the effective streamed KV resident reports 0 because the full context fits; the argument is unchanged. Existing lightweight STRATA_SPLIT_TIMING/STRATA_DECODE_TIMING are equal in all arms. Only the pool override is intentionally varied. Complete commands/configs, actual child environments and capacities are preserved per request.

## Launch commands

```bash
cd /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-pool-spin-20261005T184831Z/launchers
./start-32k.sh --host 0.0.0.0 --port 8080
# or, one server at a time
./start-128k.sh --host 0.0.0.0 --port 8080
./stop.sh
```

Launchers verify frozen binary/source/model paths, retain the selected explicit pool policy (or explicitly scrub/unset the default), print complete resolved settings, refuse active GPU/Strata processes and port collisions, and stream live logs. Each start creates a separate timestamped manual directory. Previous Q4/IQ3 launchers remain untouched. `--check` validates without inference. `scripts/reproduce-analysis.sh` recomputes analysis/report/audit without benchmarking.

Final cleanup/provenance audit: analysis/audit.json. All raw data remain preserved. No push, PR, model change, residency, helper, 256K or unrelated experiment.

USE_100US
