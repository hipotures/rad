# IQ3_S: CPU-pool validation and persistent residency

Completed 2026-10-05T13:14:56.933664+00:00. The bounded P0/P1/P2 protocol is complete before the 10-hour upper bound. The prior campaign and all raw data remain preserved. This does not mean every possible residency algorithm was exhausted.

## P0: independent workload validation

**1. Generalization:** fixed 100 µs helped the three tested workload families: a different repository/storage audit, exact interpolation and numerical reasoning, and an RFC-based operations handbook. There were 36 valid 4096-output requests: three families × two context profiles × two policies × three paired fresh starts. Math at 128K was approximately neutral; the other cells showed useful latency/TG gains.

| Family | Context | Default TG | 100 µs TG | Paired median TG Δ | Paired median wall Δ | VM CPU default / 100 µs |
|---|---|---:|---:|---:|---:|---:|
| code | 32k | 114.8 | 152.3 | +28.05% | -16.71% | 94.1% / 21.0% |
| code | 128k | 128.2 | 144.2 | +8.42% | -3.93% | 94.4% / 17.5% |
| math | 32k | 150.8 | 172.8 | +14.59% | -8.99% | 96.4% / 27.6% |
| math | 128k | 167.0 | 165.1 | +3.89% | -1.41% | 96.1% / 27.1% |
| prose | 32k | 118.4 | 166.1 | +40.62% | -20.19% | 95.3% / 21.6% |
| prose | 128k | 152.2 | 160.5 | +5.38% | -4.16% | 97.8% / 18.5% |

TG columns are independent cell medians. Delta columns are medians of the three paired ratios; these need not equal the ratio of cell medians.

**2. Workload characteristics:** parking idle workers reduces host contention when execution is mostly local. This mechanism is an inference from identical output/routing and lower CPU/staging costs, not isolation of every scheduler effect. The advantage shrinks when CPU-positive work and wakeup latency matter more.

**3. Cost under CPU-positive execution:** selected 32K math layers had median completion waits of about 5–6 µs by default versus 61–71 µs at 100 µs parking. Their p95 increased from roughly 98–160 to 293–387 µs. All-local completion floors stayed near 4–5 µs. One preserved math128 pair had TG −3.35% and wall +1.56%; one prose128 pair had wall +0.25%. End-to-end request latency, rather than lower CPU use alone, determined the decision. Extreme all-CPU and concurrent workloads are not certified.

**4. Correctness:** all 18 pairs retained identical actual input/output IDs, MTP, normal routing counters and capacities. Wait diagnostics were separate from headline binaries. See [P0 report](/srv/ai/research/iq3s-residency-20261004T230051Z/experiments/E026-pool-generalization/report.md).

## P1: frozen CPU-pool baseline

**5–6. Policy:** fixed `STRATA_POOL_SPIN_US=100`. The CURRENT source and executable are unchanged; no adaptive synchronization subsystem was needed and no dense threshold sweep was performed.

**7–8. Fresh-start standard-workload confirmation:**

| Context | Pool policy | PP median | TG median | TTFT median s | Wall median s | Decode VM CPU |
|---|---|---:|---:|---:|---:|---:|
| 32k | default | 3603.2 | 148.8 | 7.994 | 35.513 | 95.8% |
| 32k | sleep100us | 3613.2 | 166.9 | 7.989 | 32.478 | 26.8% |
| 128k | default | 3988.1 | 124.8 | 32.262 | 65.095 | 98.7% |
| 128k | sleep100us | 3985.6 | 144.2 | 32.346 | 60.740 | 29.6% |

Exactly three valid measured runs per point. The earlier 178.5/154.0 numbers came from a different shared-server protocol and remain historical. The fresh-start confirmation is not forced to match them. Min/median/max and all raw paths are in the CSV/JSON summaries.

**9. Stress/correctness:** 8000 targeted batches and 67,200 jobs covered bursts, idle periods, alternating CPU/local work, and repeated pool construction/destruction; outputs were checked. Original pool stress ran 20 seconds per policy, and real IQ native expert parity passed at layers 0/1/2/12. No lost jobs or deadlock was observed. No CPU-pool synchronization primitive changed; the tests are not a proof of all interleavings.

**10. Launch readiness:** the actual 128K launcher bound to `0.0.0.0`, became healthy, generated 64 tokens, and stopped cleanly. Exact launch commands appear below. See [P1 report](/srv/ai/research/iq3s-residency-20261004T230051Z/experiments/E027-pool-baseline/report.md).

## P2: persistent same-device expert residency

**11. Implementation:** completed in separate worktrees/builds, disabled by default. Admission retains experts across future demand; there is no immediate swap/restore. It keeps the original per-device variable-size physical slots and immutable RAM arena. Copies run asynchronously at the existing safe end-of-verify boundary and publish only after completion events. No experts or weights are substituted.

**12. Signals:** the existing native GPU gate/top10 at horizon eight, combined with observed EMA heat, recency, resident age, a byte-aware transfer penalty and a replacement margin. Predictions cover five target layers out of 48. Normalized gate confidence is not calibrated future probability. The final policy uses the predeclared 64-window utility horizon and 64 MiB/device batch budget; only one repair of the initial conservative policy was tested.

**13. Replay headroom:** the old future-informed placement reference reached 4/3 nonlocals versus CURRENT 36,776/45,276 at fixed capacity, but it is neither deployable prediction nor free latency savings. The corrected causal warmup replay of our policy produced 73,926/79,719 nonlocals and 3.941/4.809 GB of promotions. Modeled waits were 1.537/1.948 s at 1.8 GB/s and 0.027/0.053 s at 12.6 GB/s. These are sensitivities on a fixed trajectory, not TG forecasts.

H8 current-window any-branch membership was 35.2%/42.4%; membership in the next 16 windows was 60.1%/61.8%. These are different metrics from the prior next-layer prediction result. Warmup state, prediction heat, recency, pending reservations and byte constraints were explicitly audited.

**14–19. Live confirmation: same modified binary, OFF versus ON, identical inputs/settings/capacities, warmup 64 output, three fresh measured starts per cell, 4096 output:**

| Context | Residency | PP median | TG median | TTFT s | Wall s | CPU entries | PCIe entries | Decode VM CPU |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 32k | off | 3572.1 | 167.6 | 8.079 | 32.507 | 34264 | 1143 | 25.5% |
| 32k | on | 3571.2 | 160.5 | 8.077 | 33.598 | 64771 | 4921 | 33.2% |
| 128k | off | 3985.6 | 145.2 | 32.256 | 60.455 | 42755 | 1622 | 29.1% |
| 128k | on | 4221.3 | 138.1 | 30.496 | 60.151 | 74591 | 5917 | 34.8% |

| Context | Admissions | Copied GB | Useful | Repeated use | Wasted | Ready for future use | Late for future use | Victim entries |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 32k | 1765 | 3.530 | 1752 | 1739 | 15 | 1752 | 0 | 8900 |
| 128k | 2388 | 4.770 | 2344 | 2314 | 44 | 2344 | 0 | 14818 |

Each counter column is independently median-reduced across three runs; useful plus wasted medians need not equal the admissions median. Ready/late here refers to the first **subsequent** use after admission. The current-window target already executed before the safe copy boundary; those opportunities are not counted as early hits. Up to three admissions were still pending at the output cutoff in individual clean runs; they were not counted as ready or useful. The next request drains pending copies before prefill/decoding. Detailed prediction, enqueue, completion observation, lifetime, reuse and victim CSVs are preserved in the separate diagnostic experiment. Publication is a checked upper-bound observation of GPU completion; the exact GPU completion timestamp is unavailable.

- 32k: TG median ratio -4.24%, wall median ratio +3.36%; paired median TG -6.74%, paired wall +5.78%.
- 128k: TG median ratio -4.89%, wall median ratio -0.50%; paired median TG -5.39%, paired wall +1.78%.

**20. Why replay headroom did not turn into speed:** fewer promotion bytes came with more CPU/mapped expert work. The predictor is limited, the utility is approximate, capacity is fixed, and safe boundary admission cannot catch the first current-window target demand. Placement changes CPU/GPU rounding and the free-generation/MTP trajectory. The same-input comparison does not isolate a fixed-trace kernel speedup.

Copy submission/staging, exposed adaptation-thread join, and completion-event waits were measured separately with a diagnostic binary. They overlap and must not be summed into a fabricated TG forecast. Short pending-event waits alone do not establish cheap copies.

- 32k: PARITY_PASS; enqueue/staging 27.028 ms, exposed join 1.03 ms, pending publication 39.039 ms. Only 146/1793 admissions had a recorded router prediction; most admissions were driven by observed demand. Of these, 127 already missed after prediction and before enqueue. Median enqueue-to-checked-publication was 2346 µs. Useful admissions had median 67.0 routed entries of reuse.
- 128k: PARITY_PASS; enqueue/staging 30.517 ms, exposed join 3.315 ms, pending publication 59.607 ms. Only 201/2524 admissions had a recorded router prediction; most admissions were driven by observed demand. Of these, 168 already missed after prediction and before enqueue. Median enqueue-to-checked-publication was 2494 µs. Useful admissions had median 52.5 routed entries of reuse.

The initial conservative policy was rejected after one preserved 32K screen: 142.7 versus 179.7 TG and 18.9% longer request wall time. The repaired policy was frozen before the final matrix. No tuning continued until a favorable result appeared. See [replay report](/srv/ai/research/iq3s-residency-20261004T230051Z/experiments/E028-persistent-replay/report.md), [live report](/srv/ai/research/iq3s-residency-20261004T230051Z/experiments/E029-persistent-runtime/report.md), and [source safety](/srv/ai/research/iq3s-residency-20261004T230051Z/experiments/E029-persistent-runtime/analysis/source-safety.md).

## BEST REAL-PROMPT CANDIDATE

**21–22. Variant:** `p1-baseline`. Binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/control/strata`. SHA256: `eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d`. Source: `6f32ec070f23ced9f50e704d854d775da52591ab` in `/srv/ai/research/iq3s-residency-20261004T230051Z/src/control`.

Model revision: `ed59f92082b1e93c0e96d60a8b11aab089b52f09`. Existing IQ3_S GGUF/pack, PLE and MTP remain unchanged. Full frozen configurations: [32K](/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-baseline/32k.json), [128K](/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-baseline/128k.json).

Environment: `CUDA_VISIBLE_DEVICES=0,1 STRATA_SPLIT_TIMING=1 STRATA_DECODE_TIMING=1 STRATA_POOL_SPIN_US=100`.

Both RTX 4090, K=25, PCIe fraction 0.28, workers=15, normal MTP spec=4/min-p=0.5, INT8 KV, kv-resident=32768 where applicable, prefill=auto, suffix lookup OFF, reuse OFF, greedy serial execution. Total limits are 32768/131072, with about 28.38K/126.72K actual input plus the 4096-output budget and reserve. No 64K/256K test was run.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-baseline/start-32k.sh --host 0.0.0.0 --port 8080
# Stop the first server before starting the other profile:
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-baseline/stop.sh
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-baseline/start-128k.sh --host 0.0.0.0 --port 8080
```

These new research launchers leave normal user launchers unchanged. `reproduce.sh --experiment UNIQUE_NEW_DIRECTORY --attempt v1 --reproduction` replays saved requests after campaign completion, refuses overwrite, and does not extend the active deadline.

## PERFORMANCE

The defensible CPU-pool gain is the P1 default→100 µs paired comparison on the unchanged executable. P2 is a separate same-binary OFF/ON comparison. Timing variation between campaigns is preserved; a newer OFF result is not attributed to a source improvement without a controlled comparison. Full PP/TG ranges, MTP, CPU/GPU, VRAM, RAM and raw paths are in [summary.csv](/srv/ai/research/iq3s-residency-20261004T230051Z/summary.csv) and [summary.json](/srv/ai/research/iq3s-residency-20261004T230051Z/summary.json).

## CORRECTNESS

P0: 18/18 exact paired outputs/MTP/routing. P1: 6/6 exact pairs. P2: scoped finite-head/math/JSON checks passed, but 5/10 short-battery outputs are exactly identical; all differences and first diverging tokens are retained. Live promoted expert weights matched RAM exactly for 1793/2472 expert readbacks at 32K/128K. Slot owner/size/reservation invariants passed. Native suite: 62 PASS, 2 SKIP; four known fixture/environment failures explicitly excluded. Repaired v2 targeted suite: 15 PASS. No general quality judge or proof of every possible interleaving is claimed.

## NEGATIVE RESULTS

**23. Paths not to repeat without new evidence:** conservative v1 underadmission; this completed v2 traffic/nonlocal tradeoff, which was slower in decode; prior temporary swap/restore; bounded Expert-Jev, frequency, Markov and low-rank variants. Source validation and patch-anchor failures were preserved and repaired in separate versions before inference. No failed attempt is hidden.

**24. Strongest future direction:** persistent causal admission with broader calibrated demand/lifetime utility, measured exposed miss/copy costs, and a safe earlier promotion mechanism that avoids CPU CUDA calls inside a spinning verify graph. This experiment does not close all persistent residency. Cross-GPU redesign and new learned scorers are deferred research directions, not unfinished mandatory work.

## UNFINISHED DUE TO DEADLINE

None in the bounded P0/P1/P2 protocol. The campaign converged before its upper bound; no branch was started merely to consume time.

## Preserved evidence and end state

[P0](/srv/ai/research/iq3s-residency-20261004T230051Z/experiments/E026-pool-generalization/report.md), [P1](/srv/ai/research/iq3s-residency-20261004T230051Z/experiments/E027-pool-baseline/report.md), [P2](/srv/ai/research/iq3s-residency-20261004T230051Z/experiments/E029-persistent-runtime/report.md), [launch index](/srv/ai/research/iq3s-residency-20261004T230051Z/launch-index.md), [previous report](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/pool-persistent-20261005T094800Z/previous-root/report.md), [end state](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/pool-persistent-20261005T094800Z/end-state.json).

All raw, invalid and diagnostic data remain preserved. Owned Strata/training/profiling processes are stopped and both GPU compute-process lists are empty. Model/source provenance and previous archived report hashes were verified. No push, PR, driver/global configuration change, or model change occurred.

USE_P1_BASELINE
