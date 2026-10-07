# IQ3_S: three preserved dual-4090 configurations, 32K / 128K long decode

**Recommendation: BASELINE_CURRENT_LAYER_SPLIT.** The current K=25 / PCIe fraction 0.28 configuration wins median decode at both contexts with 4096 output tokens, and also wins prefill. This selects a conservative reference for residency research; it does not establish a universal winner for arbitrary long generations.

The primary matrix contains exactly 18 valid measured requests: three configurations × two contexts × three runs. Each cell starts a fresh server, performs the same 4096-input / 64-output warmup, then runs serially with zero prompt reuse. All primary measured outputs contain exactly 4096 tokens and finish by length. No tuning, runtime redesign, selective-residency implementation, model download/change, push or PR was performed.

## Main matrix

| Config | Actual prompt | PP tok/s | TTFT s | TG median | TG min/max | Hit % | MTP accepted/window | CPU fallback entries | Mapped-RAM PCIe entries | GPU0 % | GPU1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CURRENT | 31407 | 4776.3 | 6.73 | 143.4 | 136.3/161.5 | 98.7 | 2.16 | 28094 | 648 | 47.9 | 53.1 |
| V0138 | 31407 | 4652.5 | 6.90 | 126.8 | 107.1/154.0 | 98.9 | 1.90 | 25278 | UNAVAILABLE | 44.9 | 50.7 |
| HELPER | 31407 | 2433.7 | 13.05 | 129.2 | 123.5/153.0 | 99.1 | 1.97 | 12127 | UNAVAILABLE | 89.2 | 10.3 |
| CURRENT | 127028 | 5908.3 | 21.98 | 132.0 | 124.7/135.1 | 98.5 | 1.75 | 35910 | 1270 | 49.4 | 52.4 |
| V0138 | 127026 | 5687.6 | 22.86 | 96.5 | 96.3/108.7 | 98.6 | 1.84 | 32022 | UNAVAILABLE | 43.8 | 48.1 |
| HELPER | 127026 | 2372.5 | 54.05 | 106.9 | 105.2/143.2 | 98.6 | 1.82 | 19141 | UNAVAILABLE | 88.9 | 9.3 |

Each value is the median of three runs. Actual 32K inputs are 31,406 / 31,407 / 31,409. At 128K the current API consumes 127,028 tokens; the older APIs consume 127,026. The API difference is documented below. `summary.json` links every headline cell to canonical raw records; `summary.csv` also retains PP and TG min/median/max, memory, power, MTP totals and system metrics.

## Decode progression

| Config | Context | TG 0–512 | TG 512–1K | TG 1K–2K | TG 2K–4K | Final engine TG |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CURRENT | 32K | 125.5 | 149.0 | 144.8 | 141.3 | 143.4 |
| V0138 | 32K | 110.2 | 117.0 | 119.2 | 139.6 | 126.8 |
| HELPER | 32K | 114.8 | 118.7 | 146.3 | 140.2 | 129.2 |
| CURRENT | 128K | 112.1 | 132.9 | 146.4 | 132.4 | 132.0 |
| V0138 | 128K | 91.9 | 103.8 | 105.6 | 94.5 | 96.5 |
| HELPER | 128K | 106.2 | 101.3 | 114.6 | 110.1 | 106.9 |

Interval values are **approximate client-wall rates**, derived from 1 Hz API integer generated-token counts using bracketed linear interpolation. They are not exact engine per-token timing. Full checkpoints, cumulative rates, boundary uncertainty, and lower/upper bounds are in `analysis/progression.json`. Streaming/buffering and the first-emitted-content anchor also limit the initial interval. Ordinary live telemetry does not expose interval cache-hit or MTP counters; those remain unavailable.

At 32K, CURRENT and V0138 show a definite early-to-late increase in two of three runs when comparing the first 512 tokens against 2K–4K using the timestamp brackets. This is not uniform across all runs. The three late-interval medians are nearly tied, so the whole-run ranking is not proof of a steady-state ranking. At 128K the current configuration leads the late interval; rates do not consistently continue increasing from 1K–2K to 2K–4K. The data cannot assign the increases specifically to cache adaptation.

## Per-run routing, MTP and system evidence

| Raw record | TG | MTP accept % | Hit % | CPU entries | Mapped PCIe entries | Helper entries | CPU VM % | GPU wait ms/window | CPU work ms/window | GPU0 RX MB/s | GPU1 RX MB/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CURRENT-128K-run1 | 124.7 | 75.1 | 98.5 | 35910 | 1496 | UNAVAILABLE | 96.4 | 7.93 | 1.59 | 289.6 | 311.3 |
| CURRENT-128K-run2 | 132.0 | 79.0 | 98.3 | 40406 | 1270 | UNAVAILABLE | 96.7 | 7.83 | 1.95 | 511.6 | 496.0 |
| CURRENT-128K-run3 | 135.1 | 72.9 | 98.5 | 35159 | 1006 | UNAVAILABLE | 96.7 | 6.99 | 1.45 | 326.2 | 316.9 |
| CURRENT-32K-run1 | 161.5 | 85.0 | 98.5 | 32576 | 1127 | UNAVAILABLE | 95.7 | 6.78 | 1.61 | 166.0 | 229.6 |
| CURRENT-32K-run2 | 136.3 | 80.8 | 98.9 | 25643 | 588 | UNAVAILABLE | 96.4 | 8.11 | 1.31 | 598.1 | 136.9 |
| CURRENT-32K-run3 | 143.4 | 86.6 | 98.7 | 28094 | 648 | UNAVAILABLE | 97.5 | 8.14 | 1.53 | 201.8 | 157.0 |
| HELPER-128K-run1 | 105.2 | 72.8 | 98.6 | 22525 | UNAVAILABLE | 845605 | 94.2 | 15.42 | 2.79 | 293.5 | 266.1 |
| HELPER-128K-run2 | 106.9 | 77.3 | 98.9 | 16179 | UNAVAILABLE | 882281 | 95.1 | 16.03 | 2.72 | 244.6 | 148.0 |
| HELPER-128K-run3 | 143.2 | 78.7 | 98.6 | 19141 | UNAVAILABLE | 902730 | 97.7 | 12.21 | 2.61 | 362.9 | 247.7 |
| HELPER-32K-run1 | 123.5 | 82.1 | 98.6 | 20336 | UNAVAILABLE | 796439 | 94.3 | 13.95 | 2.73 | 185.5 | 183.0 |
| HELPER-32K-run2 | 129.2 | 79.2 | 99.4 | 9508 | UNAVAILABLE | 716945 | 89.8 | 12.84 | 2.05 | 116.4 | 135.3 |
| HELPER-32K-run3 | 153.0 | 87.9 | 99.1 | 12127 | UNAVAILABLE | 863511 | 95.1 | 12.40 | 2.49 | 166.7 | 239.8 |
| V0138-128K-run1 | 108.7 | 74.7 | 98.5 | 35995 | UNAVAILABLE | UNAVAILABLE | 97.3 | 8.63 | 1.65 | 443.9 | 346.1 |
| V0138-128K-run2 | 96.5 | 78.7 | 98.6 | 32022 | UNAVAILABLE | UNAVAILABLE | 97.1 | 11.27 | 1.69 | 638.1 | 267.6 |
| V0138-128K-run3 | 96.3 | 75.9 | 98.8 | 29340 | UNAVAILABLE | UNAVAILABLE | 96.8 | 10.98 | 1.59 | 224.4 | 255.9 |
| V0138-32K-run1 | 107.1 | 76.9 | 98.8 | 27709 | UNAVAILABLE | UNAVAILABLE | 96.3 | 9.41 | 1.42 | 283.6 | 141.9 |
| V0138-32K-run2 | 126.8 | 79.1 | 99.1 | 21770 | UNAVAILABLE | UNAVAILABLE | 95.2 | 8.29 | 1.08 | 174.4 | 172.2 |
| V0138-32K-run3 | 154.0 | 83.9 | 98.9 | 25278 | UNAVAILABLE | UNAVAILABLE | 95.6 | 6.69 | 1.23 | 140.1 | 418.5 |

CPU VM utilization is across all 16 vCPUs; process 100% means one vCPU. Decode CPU VM medians are approximately 94–97%, with peaks near 100%. Helper uses roughly 89% GPU0 and 9–10% GPU1, while layer split uses roughly 44–53% on each GPU. Higher utilization or cache hit rate alone does not identify the critical path.

## Frozen configuration and provenance

- **HELPER:** binary-source HEAD `ec511d128247ccf25a1ec94168481bd053d35dfd`; binary SHA256 `76439125285f7c5a26344ea55c9f17ea30df2b570d5670fee8a2513a513a0262`; source checkout `/srv/ai/strata-pr578-helper-priority`. Current source checkout HEAD `ec511d128247ccf25a1ec94168481bd053d35dfd` and status are recorded separately in `git/HELPER.json`. Source config: `/srv/ai/benchmarks/strata-qwen38/pr578-dual4090/configs/H-PRIORITY-FINAL-runtime.json`.
- **V0138:** binary-source HEAD `99f3dbd0b21d1401b3769e0c0d963913607f380b`; binary SHA256 `c0b9146a7c67ab3e68c4c2116420391535d8392c30475df2f758d36b58f91c37`; source checkout `/srv/ai/strata-v0.1.38`. Current source checkout HEAD `99f3dbd0b21d1401b3769e0c0d963913607f380b` and status are recorded separately in `git/V0138.json`. Source config: `/srv/ai/benchmarks/strata-qwen38/iq3s-v0138-2x4090/configs/IQ3S-v0138-runtime.json`.
- **CURRENT:** binary-source HEAD `6f32ec070f23ced9f50e704d854d775da52591ab`; binary SHA256 `871bb3b8ff217b6c53b517e3a5f77504e86c74877d6c717050e2034d3098840d`; source checkout `/srv/ai/strata-pr578-refresh-20261004-control`. Current source checkout HEAD `e15f4f0218c8e2e60ff42d61313c824ba82f6373` and status are recorded separately in `git/CURRENT.json`. Source config: `/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/configs/LS-B-FINAL-TOKFIX-runtime.json`.

HELPER is the actual preserved v0.1.38 + PR578 + local helper-priority build, commit `ec511d1`, not a reconstructed patch. Its exact patch/build evidence is in `git/helper-priority.*`. It retains CLI capacities 6567 / 11796, producing 8586 primary slots and 11796 helper slots. V0138 is the preserved clean v0.1.38 binary. CURRENT is the preserved **unmodified `strata-original` binary** at main `6f32ec0`, even though that checkout now separately contains a committed diagnostic patch. None of the diagnostic binaries were used.

Both layer splits are fixed explicitly to the historically selected K=25. Startup capacities are 10112 / 8376 for V0138 and 10112 / 8377 for CURRENT. No split, cache, MTP or prefill search was performed. All use the same IQ3_S revision `ed59f92082b1e93c0e96d60a8b11aab089b52f09`, pack `/srv/ai/models/strata/packs/iq3_s`, native GGUF shards, expert profile, and MTP pack `/srv/ai/models/strata/mtp/rt`. Original shard SHA256 evidence is copied to `git/IQ3_S-SHA256SUMS`; model sizes/mtime remained unchanged. The full routed-expert arena is preloaded in RAM, about 46.84 GiB.

Common settings: spec=4, spec-min-p=0.5, INT8 KV, kv-resident=32768, max-context=262144, workers=15, greedy temperature=0, suffix-draft=0, prompt-cache=0, prefill=auto, no concurrency. Fairness normalizations: V0138 previously left workers and suffix implicit; they are explicitly 15 and OFF here. Historically observed auto-probed PCIe fraction 0.37 is frozen explicitly for V0138 and HELPER; CURRENT retains 0.28. These are known configurations with intrinsic topology/runtime/PCIe differences, not a single-variable runtime-only A/B.

Every raw record retains the full engine command/config, source/binary identity, model revision, payload hash and input-ID provenance. Server command and relevant environment are also recorded in `live.json` / configs. Only ordinary preserved timing switches are enabled. PSS is read before/after requests, never at 1 Hz. Hardware, compiler/CUDA, topology, source delta and build caches/commands are in `git/`. Current diagnostic build-cache metadata is distinguished from the preserved original build commands.

## Payloads and token-ID parity

The original saved short-answer task stopped at 2036 output tokens. That request is preserved as invalid for fixed 4096 throughput. All final cells therefore use one shared, pre-existing 40-section repository-maintenance task from the previous steady2048 workload. The 32K body is preserved from that workload with the three saved nonce/system prompts. The 128K repository body is preserved unchanged; only its final task is replaced by the same long-output task. No source trimming was used to force a round token count.

At 32K, input IDs are identical across all three configurations for each repetition; the warmup is ID-identical too. At 128K, HELPER and V0138 consume identical IDs, but CURRENT escapes literal quoted thinking tags through upstream `Service.encode_prompt` (#537). The original 127000/127002 prompt counts become 127026/127028 after the shared task replacement. CURRENT versus older 128K is **TEXT_IDENTICAL / NOT_TOKEN_IDENTICAL**, not a silently claimed same-token A/B. Exact IDs and counts are in `tokenization.json`, `token-ids/`, and `analysis/token-comparison.json`. Greedy generated trajectories can diverge under floating-point/cache-routing differences, affecting MTP and throughput.

## Residual misses and PCIe bursts

Reported cache nonhits (lookups minus hits) count routed CPU fallback entries, not distinct expert miss events. Current offloaded-entry counters distinguish its mapped-RAM work; older exact offloaded counters are unavailable. Older logs still provide rounded PCIe experts per layer/window, saved in summary. Helper entries and helper return/wait totals are separate metrics. No unavailable counter is filled with zero.

At 128K, CURRENT has median GPU-reach wait 7.83 ms/window versus V0138 10.98 and HELPER 15.42; CPU-work timing is 1.59 / 1.65 / 2.72 ms/window. V0138 and CURRENT have similar aggregate MTP acceptance despite materially different TG. This supports investigating the residual dispatch/coordination/memory path, but is not a measured cost per miss or an isolated causal runtime result. Helper has fewer CPU fallback entries and slightly higher hit rates yet lower median TG: cache hit percentage alone does not rank the architectures.

Observed PCIe RX samples sometimes exceed 1–2 GB/s; peaks in the primary dataset range up to about 4.7 GB/s. `analysis/pcie-bursts.json` aligns 1 Hz dmon samples with nearby output-rate intervals and stores associations. Sparse whole-second timestamps cannot label bursts as expert admission, mapped execution, KV streaming, or another subsystem, nor prove they are on the critical path. KV streaming footer RAM-read totals are retained. No saturation claim: the independent hardware study measured about 12.6 GB/s pinned single-card H2D and 26.7 GB/s aggregate transfer capability.

Per-miss identities/layers, repeated miss IDs, admissions/evictions, interval hit/MTP counters and individual miss wait times are unavailable from these preserved speed binaries. No hot-path instrumentation was introduced. ArenaExpertSource accesses preloaded RAM by pointer; ordinary mmap/complement file counters do not independently measure arena expert SSD reads. Those logical expert-file metrics remain unavailable, not zero; PLE/model I/O is distinct.

## Optional 16K confirmation

A focused 32K CURRENT/HELPER extension was justified because the 2K–4K interval medians were only about 0.8% apart, despite an 11% whole-run gap. The same input/task, fresh server, and 4096/64 warmup were retained. CURRENT naturally stopped at 9689 tokens. HELPER completed one 16384-token request, then naturally stopped at 13174. All records are preserved. There is **no complete three-run 16K median and no controlled fixed-length 16K ranking**. No prompt rewriting or repeated search for favorable outputs was performed. `analysis/confirmation-decision.json`, `confirmation-results.json`, and `optional-progression.json` document the selection, failures and observed progression.

## Explicit answers

1. Fastest at 32K / 4096: CURRENT, median 143.4 tok/s (136.3–161.5).
2. Fastest at 128K / 4096: CURRENT, median 132.0 tok/s (124.7–135.1); current/older input-ID difference is disclosed.
3. Best prefill: CURRENT, 4776.3 tok/s at 32K and 5908.3 at 128K.
4. Best late decode: at 32K the approximate 2K–4K medians are tied within sampling uncertainty (CURRENT 141.3, HELPER 140.2, V0138 139.6). At 128K CURRENT leads (132.4 versus HELPER 110.1 and V0138 94.5). A 16K steady-state ranking is not established.
5. Early acceleration occurs in some runs, most clearly in two of three 32K runs of each layer-split variant; it is not uniform and does not establish ongoing acceleration beyond 4K.
6. The strongest direct measurement of acceleration is the generated-token timestamp progression with brackets. Aggregate MTP and GPU wait help explain cross-run variation; interval data cannot identify its cause as cache adaptation.
7. Within-request expert-hit increase is unavailable. Whole-request hit rates and between-run changes are available; these are not equivalent measurements.
8. Within-request MTP-acceptance changes are unavailable. Proposed/accepted totals, accepted/window and verify-window counts are saved per run.
9. PCIe bursts are observed, but their association with specific misses/adaptations is unproven at the available resolution. They are not labeled saturation.
10. Helper-priority is not faster than both layer splits by 4096-output medians here. It is slower than CURRENT at both contexts; it exceeds V0138 medians. Informal 89K/127K observations are not reused as controlled results.
11. Low helper utilization alone does not prove a critical-path problem. In this dataset helper has greater GPU-reach wait and CPU-work timing than CURRENT; helper-return waits are saved. The exact per-event critical path remains uninstrumented.
12. V0138 does not outperform CURRENT here: 126.8 versus 143.4 tok/s at 32K, and 96.5 versus 132.0 at 128K. V0138 is 11.6% and 26.9% lower, respectively. 128K is not literally token-identical.
13. There is no demonstrated current-runtime regression to explain. Source differences include helper integration, grouped-kernel/resident-plan work, KV/ring budgeting, CPU affinity/IQ gathers and API escaping. Explicit PCIe fractions also differ. Their causal contributions require separate ablations; none are claimed here.
14. Both configuration/runtime and free-generation/MTP trajectory effects remain. Similar 128K MTP acceptance with different GPU wait/TG suggests acceptance alone is insufficient. This is end-to-end greedy decode, not teacher-forced fixed-output kernel timing.
15. At 128K helper has about 32.07 s extra TTFT and is also slower during 4096-output decode (about 7.29 s extra by median-rate arithmetic). It does not compensate for slower prefill in this measured regime.
16. The focused 16K extension was justified by the late-interval ambiguity, but natural EOS prevented a complete fixed-length A/B. Additional different-workload research would be needed for a universal long-output ranking; this campaign does not manufacture one.
17. Residency-research reference: CURRENT frozen K=25 / PCIe fraction 0.28, config `configs/CURRENT.json`, original binary SHA 871bb3b8ff217b6c53b517e3a5f77504e86c74877d6c717050e2034d3098840d. No residency implementation starts after this report.

## Negatives, audit and end state

Three early-ending measured attempts are indexed in `summary.json` (one original-task 4096 validation, two optional 16K attempts). One valid optional 16K request is diagnostic only, not a three-run headline. The external collector nullable-live startup bug and loading-only restart are preserved in `raw/startup-telemetry-negative/`; that server was stopped before warmup or any request. Required measured telemetry is intact. Analysis-script corrections occurred after measurement and did not change raw request data.

`audit.json`: PASS. It verifies 18 primary runs, six cells, fixed output/reuse, equal warmup, hashes/counts, frozen settings/K, telemetry, unchanged models, and cleanup. All raw data and invalids remain. No benchmark server or Strata engine remains; both GPUs have no compute processes. No push, PR, model changes or selective-residency work.

## RECOMMENDATION

**BASELINE_CURRENT_LAYER_SPLIT**

For this shared repository workload, current K=25 / PCIe fraction 0.28 wins the 4096-output median TG at both 32K and 128K and has the best PP/TTFT. At 32K the late 2K–4K helper/split estimates are nearly tied, and the 16K A/B is incomplete due natural EOS; no universal long-generation winner is claimed. Use current as the conservative frozen research reference. The 128K API token-ID difference is explicitly documented.
