# Q4 UD-Q4_K_XL on the frozen Strata 0.1.39 baseline

Complete: **27 valid measured requests**, each with exactly **4096 output tokens**, plus nine identical 4096-input / 64-output warmups. All actual input-ID hashes match between methods for the corresponding run. Reuse and suffix lookup are zero. No measured run was repeated after three valid results. No engine rebuild, source patch, weight change, download, push or PR was performed.

The executable is `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/control/strata`; SHA256 `eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d`; clean source `6f32ec070f23ced9f50e704d854d775da52591ab`. The engine startup and API confirm **0.1.39**. `--version` is unsupported; its failure is preserved in `git/version.txt`. The Q4 pack directory has a `v0132` suffix because it is the previously packed model data, **not the runtime**. Earlier Q4 0.1.32 results are `INVALID_AS_CURRENT_CONTROL` and do not enter any table below.

Hardware: two RTX 4090, 16-vCPU Ryzen 9 7950X3D VM, approximately 161 GiB RAM, no swap, PHB topology and no NVLink. Full CUDA/build/driver/CPU/topology records are under `git/`. Common inference: `CUDA_VISIBLE_DEVICES=0,1`, `STRATA_POOL_SPIN_US=100`, workers 15, spec 4, min-p 0.5, INT8, KV resident 32768, prefill auto, greedy, suffix 0, prompt-cache 0, serial serving. At the 32K total limit, effective KV resident reports 0 because the whole 32K fits. Larger profiles stream KV with 32768 resident cells.

Model: Unsloth UD-Q4_K_XL, revision `38bb39ee97821de2c9009abb7e93950eec396e66`. Existing four GGUF shards and compat-BF16 pack were reused. Prior verified shard SHA256 values plus current sizes/mtimes and freshly hashed pack/profile/MTP files are in `git/model.json`. The full routed-expert arena is **77,017,907,200 bytes / 71.73 GiB** for 24,576 experts. There is no experts.bin. MTP and profile are exactly the P1 files.

## Controlled comparison

| Method | Total limit | Actual input | PP tok/s | TG tok/s | TG min–max | TTFT s | Wall s | Displayed hit % | PCIe/helper share % | CPU VM % | GPU0 % | GPU1 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer-split | 32k | 28379 | 2,574.6 | 96.2 | 92.2–99.5 | 11.18 | 55.57 | 91.0 | 1.4 | 50.1 | 54.1 | 52.0 |
| layer-split | 128k | 126716 | 3,248.9 | 93.0 | 89.3–94.0 | 39.27 | 83.27 | 91.0 | 1.4 | 44.7 | 55.6 | 51.5 |
| layer-split | 256k | 257783 | 3,294.7 | 87.8 | 86.2–89.5 | 78.77 | 125.39 | 91.1 | 1.3 | 43.4 | 53.7 | 51.8 |
| original-helper | 32k | 28379 | 1,404.3 | 58.0 | 57.4–59.1 | 20.39 | 91.72 | 80.8 | 17.4 | 48.6 | 100.0 | 11.2 |
| original-helper | 128k | 126716 | 1,467.8 | 53.6 | 53.5–53.9 | 86.62 | 163.10 | 79.1 | 18.0 | 44.9 | 100.0 | 12.7 |
| original-helper | 256k | 257783 | 1,445.8 | 48.8 | 48.8–53.0 | 178.84 | 262.69 | 78.4 | 19.7 | 43.8 | 100.0 | 12.8 |
| optimized-helper | 32k | 28379 | 1,404.2 | 48.6 | 48.3–49.4 | 20.38 | 105.09 | 89.7 | 51.0 | 25.4 | 95.9 | 9.3 |
| optimized-helper | 128k | 126716 | 1,468.2 | 45.0 | 43.2–45.7 | 86.59 | 179.78 | 89.5 | 49.7 | 20.9 | 96.0 | 9.3 |
| optimized-helper | 256k | 257783 | 1,446.1 | 44.8 | 42.1–45.4 | 178.81 | 273.76 | 91.0 | 47.2 | 19.5 | 96.0 | 9.5 |

Values are medians of three requests. CPU/GPU cells are medians of the per-request decode sample means. **Displayed hit = local / (local + CPU)**; it excludes PCIe and helper entries. The PCIe/helper column counts logical expert entries, not physical bandwidth. In layer split, local covers both stage caches; in helper mode, it is the primary cache. Actual local/all shares are shown below. Client wall and TTFT include frontend/tokenization/transport; PP/TG are the engine timers.

## BEST DECODE / BEST PREFILL / BEST OVERALL

| Profile | Best TG | Best PP | Shortest measured request |
|---|---|---|---|
| 32k | layer-split | layer-split | layer-split |
| 128k | layer-split | layer-split | layer-split |
| 256k | layer-split | layer-split | layer-split |

Overall practical choice for this workload: **layer-split**, based on the geometric mean of measured request times across the three profiles. This compares one sustained offline code/repository workload, not every real-prompt domain. The layer configuration was frozen before the final matrix: K=24, PCIe fraction .28. Four predeclared exploratory points were tested once: auto K24/.28, K22/.28, K26/.28, and K24/.37. The K22 improvement was below the predeclared 3% margin, so auto K24/.28 was retained. This was a bounded check, not exhaustive tuning.

## CPU / RESIDENCY

| Method | Profile | Slots GPU0/GPU1 | Initial resident % | Cache MiB GPU0/GPU1 | Local/all % | CPU entries | CPU/all % | MTP accept % | Accepted/window |
|---|---|---|---|---|---|---|---|---|---|
| layer-split | 32k | 6031/5510 | 47.0 | 18042/16462 | 89.7 | 196,292 | 8.9 | 84.6 | 2.15 |
| layer-split | 128k | 5999/5477 | 46.7 | 17940/16365 | 89.7 | 217,123 | 8.9 | 72.6 | 1.69 |
| layer-split | 256k | 5954/5432 | 46.3 | 17808/16230 | 89.9 | 216,575 | 8.8 | 70.6 | 1.56 |
| original-helper | 32k | 5358/7698 | 53.1 | 15999/23047 | 66.5 | 352,069 | 15.8 | 83.7 | 2.06 |
| original-helper | 128k | 5299/7696 | 52.9 | 15824/23044 | 65.1 | 406,887 | 17.2 | 76.0 | 1.82 |
| original-helper | 256k | 5222/7696 | 52.6 | 15594/23039 | 62.9 | 429,790 | 17.4 | 73.0 | 1.73 |
| optimized-helper | 32k | 5358/7698 | 53.1 | 15999/23047 | 43.8 | 112,068 | 5.1 | 84.0 | 2.10 |
| optimized-helper | 128k | 5299/7696 | 52.9 | 15824/23044 | 45.0 | 125,719 | 5.3 | 73.3 | 1.70 |
| optimized-helper | 256k | 5222/7696 | 52.6 | 15594/23039 | 48.0 | 115,476 | 4.8 | 72.8 | 1.69 |

IQ3_S P1 capacity reference: **18,717 slots at 32K (76.16%)** and **18,620 at 128K (75.76%)**, from the preserved `analysis/control-budgets-v2.json`. Q4 has materially fewer experts in VRAM. These are historical capacity references, not a controlled throughput comparison between quants. Cache MiB are rounded engine counters; native model byte classes are recorded separately.

Original and optimized helpers start with exactly identical primary/helper capacities for each context and no initial overlap by allocator construction. Primary and helper startup owners are excluded from each other in the unmodified source. Post-warmup/run3 ID-set overlap is **not exposed by this frozen binary**. Original adaptation can duplicate helper-owned experts; optimized adaptation is designed to preserve complementary ownership. We do not replace missing runtime overlap measurements with zero.

| Profile | Original CPU/all % | Optimized CPU/all % | CPU share reduction % | Optimized TG vs original % | Optimized TG vs split % |
|---|---|---|---|---|---|
| 32k | 15.8 | 5.1 | 68.0 | -16.2 | -49.5 |
| 128k | 17.2 | 5.3 | 69.3 | -16.0 | -51.6 |
| 256k | 17.4 | 4.8 | 72.6 | -8.2 | -49.0 |

CPU fallback entries are exact decode lookups minus local hits; distinct jobs can be fewer because windows reuse experts. Existing request-scoped timing lines include distinct-expert/entry averages, activation quantization, job submission and CPU completion time in `analysis/run-details.json`. High CPU use includes genuine expert fallback plus synchronization. Its exclusive compute/spin breakdown was not profiled, so a precise attribution percentage is unavailable. All arms use 100 µs parking; this campaign does not independently revalidate 100 µs against the old 20 ms behavior for Q4.

| Method | Profile | MTP accept % | Mean window ms | CPU process % (one core=100) |
|---|---|---|---|---|
| layer-split | 32k | 84.6 | 33.02 | 696.2 |
| layer-split | 128k | 72.6 | 28.94 | 688.3 |
| layer-split | 256k | 70.6 | 29.23 | 663.7 |
| original-helper | 32k | 83.7 | 52.59 | 667.9 |
| original-helper | 128k | 76.0 | 52.22 | 685.5 |
| original-helper | 256k | 73.0 | 54.47 | 672.8 |
| optimized-helper | 32k | 84.0 | 63.96 | 323.7 |
| optimized-helper | 128k | 73.3 | 61.35 | 302.3 |
| optimized-helper | 256k | 72.8 | 59.26 | 291.0 |

The window comparison separates MTP acceptance from the cost of doing the work. Similar acceptance with much slower windows supports a runtime-path explanation; after output divergence, routing and MTP trajectories can still contribute. GPU-reach wait includes coordination and mapped-memory/kernel execution, not just a pure GPU compute timer. Cumulative per-stage timing means cannot be summed into an independent request latency.

| Method | Profile | GPU-reach wait ms | CPU completion ms | Activation quantization ms | Distinct CPU experts/layer-window |
|---|---|---|---|---|---|
| layer-split | 32k | 5.39 | 14.61 | 0.62 | 2.73 |
| layer-split | 128k | 6.24 | 9.48 | 0.35 | 2.49 |
| layer-split | 256k | 6.76 | 9.43 | 0.33 | 2.40 |
| original-helper | 32k | 17.58 | 23.76 | 0.57 | 4.37 |
| original-helper | 128k | 21.99 | 19.73 | 0.35 | 4.57 |
| original-helper | 256k | 23.81 | 20.22 | 0.34 | 4.61 |
| optimized-helper | 32k | 42.22 | 10.54 | 0.21 | 1.52 |
| optimized-helper | 128k | 43.37 | 7.57 | 0.12 | 1.47 |
| optimized-helper | 256k | 42.66 | 6.87 | 0.11 | 1.31 |

These are medians of existing request-scoped engine timing means. CPU completion is host-observed completion latency, not exclusive CPU execution time; it can overlap GPU execution and other stages. Timing components therefore must not be added together to infer a wall-time breakdown. Exact worker sleep/wakeup and spin counts are unavailable on the frozen headline executable.

## GPU, transport and memory

| Method | Profile | Prefill GPU0/GPU1 % | Decode power W GPU0/GPU1 | Peak VRAM MiB GPU0/GPU1 | Decode temp C GPU0/GPU1 | Decode RX MB/s GPU0/GPU1 | Peak RAM used GiB |
|---|---|---|---|---|---|---|---|
| layer-split | 32k | 75.0/74.0 | 148.9/162.1 | 23,836/24,028 | 44.6/44.2 | 3,175.1/1,946.3 | 81.56 |
| layer-split | 128k | 86.8/93.2 | 156.7/173.6 | 23,836/24,028 | 45.8/47.2 | 3,200.8/1,387.1 | 83.33 |
| layer-split | 256k | 89.7/95.3 | 156.7/172.3 | 23,840/24,030 | 46.7/46.8 | 3,404.3/1,696.9 | 85.84 |
| original-helper | 32k | 99.6/0.7 | 178.1/79.3 | 23,884/23,902 | 46.5/45.2 | 8,672.9/36.3 | 81.33 |
| original-helper | 128k | 100.0/0.1 | 181.5/80.4 | 23,880/23,902 | 47.8/48.0 | 8,541.4/34.1 | 82.10 |
| original-helper | 256k | 99.4/0.1 | 179.6/79.1 | 23,882/23,900 | 47.3/42.4 | 8,599.7/34.5 | 85.39 |
| optimized-helper | 32k | 97.8/0.2 | 165.5/83.8 | 23,882/23,902 | 45.9/48.6 | 10,061.0/721.0 | 80.55 |
| optimized-helper | 128k | 99.8/0.0 | 167.9/84.0 | 23,880/23,902 | 46.7/48.4 | 9,771.1/585.6 | 82.30 |
| optimized-helper | 256k | 99.5/0.1 | 171.7/81.9 | 23,882/23,900 | 46.9/43.6 | 9,149.8/636.5 | 85.81 |

| Method | Profile | Helper computed entries/request | Helper returned MiB/request | Helper return bytes/output token | Helper host wait ms/request | Expert file blobs during decode |
|---|---|---|---|---|---|---|
| layer-split | 32k | not used | UNAVAILABLE | not used | UNAVAILABLE | 0 |
| layer-split | 128k | not used | UNAVAILABLE | not used | UNAVAILABLE | 0 |
| layer-split | 256k | not used | UNAVAILABLE | not used | UNAVAILABLE | 0 |
| original-helper | 32k | 236,732 | 2,311.8 | 591,821 | 412 | 0 |
| original-helper | 128k | 257,970 | 2,519.2 | 644,915 | 531 | 0 |
| original-helper | 256k | 291,362 | 2,845.3 | 728,397 | 616 | 0 |
| optimized-helper | 32k | 884,846 | 2,167.9 | 554,982 | 977 | 0 |
| optimized-helper | 128k | 929,410 | 2,356.5 | 603,264 | 1,358 | 0 |
| optimized-helper | 256k | 901,830 | 2,371.5 | 607,104 | 1,518 | 0 |

Helper counters include any prompt-tail work in the request, while hit/miss counters are explicitly decode-scoped. NVML/dmon RX/TX is sampled total card traffic: expert mapped reads, KV activity, cache copies and other transfers. It is not the logical helper return payload. Both RX and TX, mean/max, are in `analysis/run-details.json`. Low helper GPU utilization does not imply no critical-path cost: each layer still waits for its participating helper. Primary GPU utilization near 100% is not proof of arithmetic saturation; mapped-memory stalls can also keep a kernel active.

The engine DONE file counters are snapshotted at decode start. The reported expert-file reads are zero on this full-arena path, consistent with routed experts resident in RAM. Physical disk reads may be PLE and must not be interpreted as expert SSD reads. Exact per-subsystem critical-path bandwidth attribution was not measured. RAM uses system total-minus-MemAvailable; summed process RSS can double-count shared mappings. No PSS polling was used.

The helper frontend Monitor only exposes primary-GPU hardware. The existing speed sampler and PCIe dmon already query both GPUs. An additional 1 Hz NVML temperature collector was attached after this was discovered; original-helper32K run1 GPU1 temperature is unavailable and early partial coverage is recorded rather than fabricated. Its start/finish and CPU footprint are in `telemetry/temperature-monitor*.json`. No engine instrumentation was added.

## Prefill progression and realistic request time

| Method | Profile | PP run1/run2/run3 | Wall run1/run2/run3 s |
|---|---|---|---|
| layer-split | 32k | 1,512.1 / 2,574.6 / 2,579.0 | 61.46 / 55.57 / 52.30 |
| layer-split | 128k | 1,752.2 / 3,250.9 / 3,248.9 | 118.73 / 83.27 / 82.82 |
| layer-split | 256k | 2,285.8 / 3,294.7 / 3,295.8 | 161.32 / 124.53 / 125.39 |
| original-helper | 32k | 1,218.5 / 1,404.3 / 1,404.5 | 94.02 / 91.72 / 89.64 |
| original-helper | 128k | 1,407.3 / 1,468.1 / 1,467.8 | 166.94 / 162.51 / 163.10 |
| original-helper | 256k | 1,434.9 / 1,446.0 / 1,445.8 | 264.59 / 256.16 / 262.69 |
| optimized-helper | 32k | 1,216.8 / 1,404.2 / 1,404.3 | 106.32 / 105.09 / 104.65 |
| optimized-helper | 128k | 1,412.9 / 1,468.2 / 1,468.6 | 179.78 / 181.47 / 177.58 |
| optimized-helper | 256k | 1,422.0 / 1,446.1 / 1,446.4 | 273.76 / 268.93 / 275.93 |

The fixed 64-output warmup is identical for every cell. It does not guarantee all full-length prefill workspaces/cache behavior are already warm. Layer-split PP increases after the first full request, despite measured reuse=0. The table preserves that effect; medians alone should not be treated as cold first-request latency. All measured requests process their complete input.

| Method | 8K input + 2K output s | 32K input + 4K output s | 128K input + 4K output s | 256K input + 4K output s |
|---|---|---|---|---|
| layer-split | 24.47 | 55.31 | 84.39 | 126.22 |
| original-helper | 41.14 | 93.95 | 165.72 | 265.25 |
| optimized-helper | 47.97 | 107.62 | 180.30 | 272.71 |

Estimates use input/PP + output/TG, not additional measurements. The 8K case extrapolates PP from the 32K profile. Full nominal 32K/128K/256K inputs plus 4K output require larger total limits than those labels; the measured admissible input lengths are in the main table. This estimate omits frontend time and should not replace measured TTFT/wall.

## 256K

- layer-split: 128K→256K TG 93.0→87.8 (-5.6%); TTFT 39.27→78.77 s; wall 83.27→125.39 s.

- original-helper: 128K→256K TG 53.6→48.8 (-9.0%); TTFT 86.62→178.84 s; wall 163.10→262.69 s.

- optimized-helper: 128K→256K TG 45.0→44.8 (-0.4%); TTFT 86.59→178.81 s; wall 179.78→273.76 s.

256K uses about 257.78K actual input so 4096 output plus reserve fit within 262144. It is not a ~259K input mislabeled as fitting this output budget. Longer-input PP cost and KV streaming matter; different input prefixes/output trajectories mean the TG change cannot be isolated as pure KV cost. Primary KV hit/read counters from existing logs are preserved in run-details.json.

## FUTURE RESIDENCY RESEARCH

- 32k: 47.0% of routed experts fit in VRAM; 10.3% of decode entries are nonlocal. CPU handles 8.9% and mapped GPU execution 1.4%. Avoiding half the CPU entries would remove approximately 98,146 entries per 4096-output request, not half the request time.

- 128k: 46.7% of routed experts fit in VRAM; 10.3% of decode entries are nonlocal. CPU handles 8.9% and mapped GPU execution 1.4%. Avoiding half the CPU entries would remove approximately 108,562 entries per 4096-output request, not half the request time.

- 256k: 46.3% of routed experts fit in VRAM; 10.1% of decode entries are nonlocal. CPU handles 8.8% and mapped GPU execution 1.3%. Avoiding half the CPU entries would remove approximately 108,288 entries per 4096-output request, not half the request time.

This supports a Q4 residency investigation: larger expert blobs and substantial CPU/mapped work provide measurable headroom. It does not establish that prediction can convert it into speed. Admission traffic, victims, fixed same-device capacity and readiness must be charged. No predictor or new residency policy was implemented here. The Q4 optimized-helper arm does not show a practical gain in this workload. Older Q3 helper results use different pool/output/context settings, so a claim about quant-specific causal benefit would be `NOT_CONTROLLED_A_B`.

## Correctness and reproducibility

0/18 helper-versus-layer pairs have identical complete generated-ID arrays. First divergence and hashes are preserved in `analysis/output-parity.json`. Different FP summation order and adaptive paths can change greedy trajectories; this was not an LLM quality judgment or a claim of bitwise parity. All requests finish at the requested length, actual input IDs are verified, and no crash/OOM is hidden.

Each cell uses one fresh process, the same fixed warmup, then three serial requests; these are not three independent fresh-server replicates. Original and optimized helper initial capacities match exactly. Old IQ3_S/Q4 launchers and data remain unchanged. See `summary.json`, `summary.csv`, `configs/`, raw request/ID/status/engine files, lightweight telemetry, environment/model manifests and the final artifact audit. The launchers use frozen harness snapshots and verify the expected binary/source and model paths before start.

## LAUNCH COMMANDS

```bash
cd /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-multigpu-20261005T164628Z/launchers

./start-32k.sh --host 0.0.0.0 --port 8080
# or
./start-128k.sh --host 0.0.0.0 --port 8080
# or
./start-256k.sh --host 0.0.0.0 --port 8080

./stop.sh
```

Run one launcher at a time. Full configuration and live logs are printed; Monitor data remain persisted. `--check` verifies configuration without starting a server. Final cleanup evidence is in `analysis/audit.json`; both GPUs are free of campaign compute processes at completion.

USE_LAYER_SPLIT
