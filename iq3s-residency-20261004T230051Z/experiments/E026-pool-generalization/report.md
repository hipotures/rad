# E026: P0 independent-workload pool validation

State: COMPLETE_SCOPED_VALIDATION. Decision: **P0-A**.

Scoped robust win: all three independent 32K workloads improve paired request latency by median 9–20%; code/prose128K improve approximately4%, math128K is neutral with one preserved+1.56% wall counterexample. There is no serious consistent miss-heavy regression across these workloads. All18 pairs preserve actual output IDs, MTP and routing. Fixed100us has a real CPU-positive wakeup cost (selected-layer median61–71us at32K,13–20us at128K versus4–6us default), but much less VMCPU contention and better overall latency in five of six cells. Freeze100us for P1, while making no universal claim for extreme CPU-positive workloads.

| Family | Context | Policy | Valid/attempts | PP | TG | TTFTs | Walls | Decode VMCPU% | CPUentries |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| code | 32k | default | 3/3 | 2458.1 | 114.8 | 11.702 | 47.403 | 94.1 | 20578 |
| code | 32k | sleep100us | 3/3 | 2459.2 | 152.3 | 11.696 | 38.588 | 21.0 | 20578 |
| code | 128k | default | 3/3 | 3539.8 | 128.2 | 36.404 | 68.336 | 94.4 | 23790 |
| code | 128k | sleep100us | 3/3 | 3548.4 | 144.2 | 36.386 | 64.788 | 17.5 | 23790 |
| math | 32k | default | 3/3 | 2238.7 | 150.8 | 12.818 | 39.970 | 96.4 | 30719 |
| math | 32k | sleep100us | 3/3 | 2258.3 | 172.8 | 12.725 | 36.375 | 27.6 | 30719 |
| math | 128k | default | 3/3 | 3390.9 | 167.0 | 37.939 | 62.465 | 96.1 | 31486 |
| math | 128k | sleep100us | 3/3 | 3380.2 | 165.1 | 37.990 | 62.880 | 27.1 | 31486 |
| prose | 32k | default | 3/3 | 1943.0 | 118.4 | 14.793 | 49.471 | 95.3 | 23484 |
| prose | 32k | sleep100us | 3/3 | 1958.6 | 166.1 | 14.666 | 39.480 | 21.6 | 23484 |
| prose | 128k | default | 3/3 | 3212.0 | 152.2 | 40.080 | 67.170 | 97.8 | 23011 |
| prose | 128k | sleep100us | 3/3 | 3314.2 | 160.5 | 38.551 | 63.969 | 18.5 | 23011 |

Actual input/output IDs and per-pair checks are in summary.json. Early endings excluded from fixed-length table, retained in application_metrics. Fresh-server paired3replicates; no extras or favorable retries.

Different documents/tasks and application latency matter; all natural EOS kept.

One-Hz phase boundaries use clientTTFT, not exactGPUkernel timing.

Actual engine outputIDs captured by common Python wrapper, enginebinary unchanged.

Wait timings unavailable in headline; diagnostic event binary separate.

No logical expert file-read counter inferred from physical processreadbytes.

## Controlled checks and scope

18 paired comparisons /36 clean requests; each fresh server, same saved4096-input64-output warmup, same actual service-rendered inputIDs and same executable. Parity mismatches: `{'same_actual_output_IDs': 0, 'same_MTP': 0, 'same_normal_routing': 0, 'same_capacity': 0}`. Every fixed-length valid point has exactly3 requests; no additional repetitions or favorable retries.

Independent tasks: real HEG repository/SQLite audit; CPython/NumPy polynomial/rational reasoning; official HTTP RFC operational prose. Complete immutable documents, tasks, payloads and actual inputIDs are in workloads/. Nonces differ between replicas but are identical between policies. This is not a universal claim for multilingual, extreme miss-heavy or concurrently CPU-loaded production traffic.

Natural stopping/invalid records are retained and excluded from fixed-length medians. Source control shutdown BrokenPipe traces after completed responses are the documented owned process-group cleanup, not an inference failure. Logical expert reads remain unavailable; physical counters are not substituted.

## CPU completion wait diagnostics

The CPU-heaviest family/profile was selected from clean median CPU entries per generated token, not assumed from task names. Same existing E021 event binary for default/100us; full4K buffers and selected layers2/24/40 only. Diagnostic throughput is excluded.

| Profile | Family | Layer | Category | Default median us | 100us median us | Default p95 us | 100us p95 us |
|---|---|---:|---|---:|---:|---:|---:|
| 32k | math | 2 | all-local | 5.12 | 5.12 | 8.19 | 7.17 |
| 32k | math | 2 | CPU-positive | 6.14 | 61.44 | 97.54 | 293.12 |
| 32k | math | 24 | all-local | 4.10 | 4.10 | 5.12 | 4.10 |
| 32k | math | 24 | CPU-positive | 5.12 | 66.56 | 134.96 | 364.34 |
| 32k | math | 40 | all-local | 4.10 | 4.10 | 5.12 | 4.10 |
| 32k | math | 40 | CPU-positive | 5.12 | 70.66 | 160.26 | 387.17 |
| 128k | math | 2 | all-local | 5.12 | 5.12 | 8.19 | 7.17 |
| 128k | math | 2 | CPU-positive | 6.14 | 18.43 | 70.96 | 110.90 |
| 128k | math | 24 | all-local | 4.10 | 4.10 | 4.10 | 5.12 |
| 128k | math | 24 | CPU-positive | 4.10 | 12.80 | 72.09 | 125.44 |
| 128k | math | 40 | all-local | 4.10 | 4.10 | 4.10 | 5.12 |
| 128k | math | 40 | CPU-positive | 4.10 | 20.48 | 80.38 | 126.46 |

These waits include event/kernel floors and overlap other streams. They cannot be multiplied by48 or summed into a synthetic request latency. Actual end-to-end wall/TG is the decision criterion. Full output/router/path/MTP diagnostic parity: `[{'profile': '32k', 'same_output_IDs': True, 'same_router_IDs': True, 'same_paths': True, 'same_MTP': True}, {'profile': '128k', 'same_output_IDs': True, 'same_router_IDs': True, 'same_paths': True, 'same_MTP': True}]`.

## Next phase

Freeze existing100us, run targeted wakeup stress and fresh paired standard-workload confirmation; reuse the P0 independent confirmations instead of exceeding3valid repetitions.

## Additional preserved checks

Strict diagnostics match output/window/router/path/cache/heat/slot-byte classes and first-head bits atbothprofiles. See diagnostic-v1/*/strict-parity.json. Existing runtime pipeline averages, without any new requests or instrumentation, are analyzed in [mechanism.md](mechanism.md).100us raises pool-completion work/waits in some stages while shorter GPU-reach and host-staging averages can improve overall latency; this supports a scheduling/host-contention explanation, not a cache-capacity change.
