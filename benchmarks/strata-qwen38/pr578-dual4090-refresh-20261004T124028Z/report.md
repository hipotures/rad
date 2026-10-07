# IQ3_S / PR #578 controlled dual RTX 4090 campaign

Frozen upstream main: `6f32ec070f23ced9f50e704d854d775da52591ab`. Runtime release: v0.1.39. Model revision: `ed59f92082b1e93c0e96d60a8b11aab089b52f09`.

PR #578 was integrated upstream manually at `4d20d25925374a9a3da7bb0e37e2aa4868d7e7bd`, although GitHub closes it without a merge marker. Both fresh checkouts use the same main; optimized expert-helper is selected by `--remote-expert-opt`. No second merge and no conflict resolution were necessary. Existing #646/#650 verifier changes are preserved.

Default-off boundary diagnostics exist on separate local commits, but headline runs use preserved UNMODIFIED upstream binaries. The predeclared3-fresh-server diagnostic ON/OFF study observed3.43% lower median ON, so debug instrumentation is excluded from final speed results. This difference is observational and does not prove causal overhead; all failed gates and raw data remain. Full cache progression dumps are separate diagnostic runs.

Primary/final speed results require three valid requests after equal warmup within each phase (primary64 output tokens; secondary lookup retry32 output tokens), MTP4/min-p0.5, INT8 KV, kv-resident32768, 15 pool workers, max context262144, greedy sampling, zero prefix reuse and suffix lookup OFF. Each 256-token replay retains the saved literal payload. Historical32K IDs and effective current-API higher-context IDs are checked against their saved hashes before submission; see the tokenizer-correction section. Invalid requests remain in raw and are omitted from valid medians.

## Primary 32K results

| Config | PP median | TG median | TG min/max | TTFT | MTP accepted/window | suffix accepted | CPU fallback entries | helper entries | cache overlap | CPU % | GPU0 % | GPU1 % | PCIe GPU0 RX / GPU1 RX MB/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LS-A INCOMPLETE (2/3 valid) | UNAVAILABLE | UNAVAILABLE | partial valid TG 107.80/142.60 | UNAVAILABLE | | | | | | | | | |
| LS-B | 4727.10 | 156.20 | 152.60/156.70 | 6.72 | 1.72 | 0.00 | 1135.00 | UNAVAILABLE | UNAVAILABLE | 68.10 | 40.00 | 54.00 | 2840.00/50.67 |
| PR-LS INCOMPLETE (2/3 valid) | UNAVAILABLE | UNAVAILABLE | partial valid TG 105.30/117.60 | UNAVAILABLE | | | | | | | | | |
| H-OLD | 2404.40 | 84.40 | 80.70/96.60 | 13.20 | 1.78 | 0.00 | 6263.00 | 10160.00 | UNAVAILABLE | 94.95 | 99.00 | 4.67 | 3386.75/27.75 |
| H-OPT | 2418.10 | 102.90 | 95.80/105.30 | 13.07 | 1.71 | 0.00 | 610.00 | 18555.00 | UNAVAILABLE | 76.65 | 99.50 | 5.67 | 3448.67/51.67 |
| H-OPT-FIXED | 2420.20 | 103.80 | 95.80/104.00 | 13.05 | 1.71 | 0.00 | 610.00 | 18555.00 | UNAVAILABLE | 76.55 | 99.50 | 6.00 | 3677.00/88.00 |

CPU fallback entries come from exact native decode cache lookups-minus-hits, verified against existing multi_entries counters in36 diagnostic requests and the source. This requires no debug instrumentation. Rounded distinct-miss and per-window estimates are retained separately in JSON. SplitDrive shares these counters across all stage GPUs; helper dispatch counts remain separately reported. Helper entries are exact reported dispatch counts where available. Hardware dmon PCIe is sparse at1Hz for short decode; returned bytes from helper logs are a separate logical transport measure. CPU system % spans all16 vCPU; process CPU % uses100% per core. UNAVAILABLE is never replaced by zero.

## Initial-cache fairness and progression

| Config | Primary physical capacity | Helper capacity | Initial GPU resident count | Initial overlap | Primary CLI budget | Frozen helper PCIe fraction |
|---|---:|---:|---:|---:|---:|---:|
| H-OLD | 8586 | 11796 | 20382 | 0 | 6567 | 0.37 |
| H-OPT | 8586 | 11796 | 20382 | 0 | 6567 | 0.37 |
| H-OPT-FIXED | 8586 | 11796 | 20382 | 0 | 6567 | 0.37 |

Layer-split allocation is unchanged in LS-A, LS-B, PR-LS and the final layer-split matrix: K25, GPU0 layers0-24 with10112 expert slots, GPU1 layers25-47 with8377 slots (18489 total). Auto predicted capacity is not substituted for actual startup allocation. Helper topology has8586+11796=20382 GPU-resident experts at startup. Both use the preloaded46.84GiB full expert arena in RAM.


| Diagnostic config | Startup overlap | After warmup overlap | After run1 / run2 / run3 overlap |
|---|---:|---:|---:|
| H-OLD-DIAG | 0 | 571 | 1706 / 2140 / 2072 |
| H-OPT-FIXED-DIAG | 0 | 0 | 0 / 0 / 0 |

Net ID-set changes are saved in cache-progression.json. Original helper keeps its initial helper set fixed while primary adaptation creates overlap; optimized helper replaced204/55/86 helper IDs across measured runs and held primary ID set unchanged in these diagnostics. These are boundary net replacements, not complete swap counts. Original after-warmup overlap571(4.84%), after-run3 overlap2072(17.57%); optimized zero at every observed boundary.

In separate diagnostics, CPU activation quantization median dropped from 29.75 ms to 1.71 ms per256-output request. Exact skipped-token count is unavailable; diagnostic timings are not headline speed.


Clean speed capacities are logged before warmup and checked for equality. Initial resident count/zero overlap follows the deterministic cache constructor with the identical complete profile/model/capacities, independently observed in paired startup diagnostics. Clean speed ID sets are NOT directly dumped; reference hashes belong to separate diagnostics, and initial_layout_basis explicitly distinguishes them. A capacity mismatch stops the candidate before warmup. Full-snapshot diagnostics show progression and are excluded from headline speed.

## Final context matrix

| Config | Actual context | PP median (min/max) | TG median (min/max) | TTFT | CPU fallback entries | helper entries | overlap | CPU % | GPU0 % | GPU1 % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H-OPT-FIXED-FINAL-TOKFIX | 63402 | 2410.80 (2403.60/2417.10) | 87.10 (81.30/88.20) | 26.58 | 281.00 | 29047.00 | UNAVAILABLE | 56.23 | 99.00 | 5.67 |
| H-OPT-FIXED-FINAL-TOKFIX | 127002 | 2388.60 (2371.40/2391.20) | 88.90 (83.30/92.70) | 53.44 | 559.00 | 21761.00 | UNAVAILABLE | 73.03 | 99.33 | 6.00 |
| H-OPT-FIXED-FINAL-TOKFIX | 259507 | 2332.10 (2331.60/2335.60) | 80.60 (77.20/81.40) | 111.80 | 330.00 | 26900.00 | UNAVAILABLE | 58.17 | 98.67 | 4.00 |
| H-OPT-FIXED-FINAL-TOKFIX-CLEAN32 | 31400 | 2407.70 (2279.50/2408.80) | 89.60 (89.10/96.20) | 13.20 | 436.00 | 18729.00 | UNAVAILABLE | 75.50 | 99.33 | 5.33 |
| LS-B-FINAL-TOKFIX | 31400 | 4601.00 (2156.00/4649.00) | 117.00 (113.80/119.10) | 6.96 | 1206.00 | UNAVAILABLE | UNAVAILABLE | 69.20 | 53.67 | 56.00 |
| LS-B-FINAL-TOKFIX | 63402 | 5388.40 (3187.90/5389.90) | 120.00 (114.60/139.50) | 12.03 | 904.00 | UNAVAILABLE | UNAVAILABLE | 87.00 | 44.00 | 50.00 |
| LS-B-FINAL-TOKFIX | 127002 | 5741.30 (3955.00/5744.90) | 118.00 (97.40/121.50) | 22.66 | 1210.00 | UNAVAILABLE | UNAVAILABLE | 69.25 | 43.00 | 50.00 |
| LS-B-FINAL-TOKFIX | 259507 | 5903.60 (4555.30/5906.70) | 137.20 (127.40/139.90) | 44.48 | 912.00 | UNAVAILABLE | UNAVAILABLE | 73.70 | 47.00 | 56.00 |

## Steady decode and secondary lookup

| Config | Output request | Valid runs | PP | TG median | TG min/max | TTFT | suffix accepted |
|---|---:|---:|---:|---:|---:|---:|---:|
| H-OLD-LOOKUP-ON-W32 | 256 | 3 | 2423.90 | 100.30 | 93.20/109.60 | 13.04 | 27.00 |
| H-OLD-STEADY2048 | 2048 | 3 | 2454.90 | 90.40 | 90.30/91.00 | 12.96 | 0.00 |
| H-OPT-FIXED-LOOKUP-ON-W32 | 256 | 3 | 2421.10 | 97.80 | 94.00/98.10 | 13.05 | 24.00 |
| H-OPT-FIXED-STEADY2048 | 2048 | 3 | 2458.30 | 74.90 | 74.40/75.90 | 12.93 | 0.00 |
| LS-B-LOOKUP-ON | 256 | 3 | 4683.10 | 137.20 | 115.00/139.40 | 6.86 | 29.00 |
| LS-B-LOOKUP-ON-W32 | 256 | 3 | 4716.30 | 134.30 | 118.40/140.80 | 6.81 | 24.00 |
| LS-B-STEADY2048 | 2048 | 3 | 4806.40 | 174.00 | 169.50/184.60 | 6.62 | 0.00 |

Lookup ON results are secondary and never combined with lookup OFF medians. An original-helper64-token warmup stopped naturally at51; its raw negative is preserved. All three secondary candidates were restarted with equal32-token warmup (LOOKUP-ON-W32). Therefore primary-to-secondary is not a controlled suffix-only A/B; compare configurations within each phase. Steady2048 uses explicitly disabled prompt cache, the same saved input and three requests per configuration. It is a separate workload, not a historical256-output A/B.

## Correctness and tests

Existing native/Python test results and actual failure classification are retained in environment.json, test-review.json, diagnostic-test-review.json and logs/. Any environmental skips/failures must be read with those records; this report does not claim every test passed when fixtures or memlock prevent execution.

Paired correctness cases recorded: 10. Malformed-output flags: 0. Input-token mismatches: 0. Full outputs/token IDs, first divergence and finish reasons: correctness/. Floating-point summation changes do not require bitwise parity. Free-generation positional token equality is not teacher-forced top1 agreement; KL/logits metrics are UNAVAILABLE unless a usable logits trace was actually captured.

## Concrete interpretation

Best complete32K layer split: LS-B, TG 156.20 tok/s, PP 4727.10. Best complete optimized helper: H-OPT-FIXED, TG 103.80, PP 2420.20. Original helper TG: 84.40. Optimized-helper TG change vs best layer split: -33.55%; vs original helper: 22.99%. These comparisons use warmup-matched, suffix-OFF data.

Primary/helper complementarity and post-warmup overlap must be assessed using the diagnostic table; startup overlap alone does not prove sustained complementarity. CPU quantization skips and per-run adaptation swap totals are UNAVAILABLE where upstream has no exact counter. Returning one weighted vector/token is confirmed in source and logical returned-byte statistics (footer rounded to0.1MiB), while total PCIe can include other runtime traffic. Higher helper hit count can increase total returned bytes even when reduction lowers bytes for the same helper work.

With only one helper, stripe/layer placement uses the same assignment path: the actual multi-helper placement branch is only active with at least two helpers. It is therefore not a meaningful A/B on this machine. Auto versus fixed capacities are compared using H-OPT and H-OPT-FIXED; primary CLI budget and resulting physical capacity are distinct quantities.

The replay/steady speed workload is code-agent repository material. Short math/prose correctness prompts do not establish stable mixed/math throughput; no cross-workload speed recommendation is inferred from them. The author’s reported dual4090 Mixed/Code rates are different workloads and are not controlled A/B with ours. No exact author benchmark scripts/payloads were available in the PR file list.

Author publication, retained separately from our measurements ([PR578](https://github.com/Niko1221/Strata/pull/578), saved git/pr.json):

| Author dual4090 v0.1.37 topology | Mixed TG | Code TG |
|---|---:|---:|
| Original helper | 88.07 | 85.15 |
| Auto layer split | 126.86 | 146.95 |
| Optimized helper | 143.35 | 197.58 |

These are author-reported values for other workloads/configurations, not our raw runs or a controlled comparison against our code-agent prompts. Our matched-capacity original/optimized comparison is reported separately above.

Historical v0.1.31/v0.1.38 replay and the preserved earlier PR578 campaign are HISTORICAL / NOT_CONTROLLED_A_B relative to this same-main experiment. See references/ and the unchanged ../pr578-dual4090/report.md. Their values are never counted as new repetitions.

## API tokenizer correction and preserved retry

The first matrix attempt completed32K, then failed the harness count assertion at64K: direct legacy tokenizer63400 versus API63402. This entire attempt is preserved separately and superseded. The harness now calls frozen upstream Service.encode_prompt, including#537 plain-text escaping of literal thinking tags. Payload text is unchanged; effective counts are31400/63402/127002/259507. Historical32K token IDs are unchanged; larger-context IDs reflect official API escaping and are saved identically for both finalists. The full matrix restarts under FINAL-TOKFIX labels. See tokenizer-review.json, api-tokenization-provenance.json, matrix-retry-policy.json and the negative provenance sidecar. No engine or weights changed.

Background-analysis review: a2.08-second summary-analysis invocation overlapped0.744s of helper32K-run1 decode and0.051s of run2 prefill. All three original helper32K requests are conservatively excluded/superseded; the complete32K cell is remeasured after the full matrix on a fresh server with the exact same context-prefixed warmup. Other context requests remain separate. See background-analysis-exclusions.json.

## Expert storage counter interpretation

The IQ3_S native expert arena is fully preloaded in RAM. ArenaExpertSource::blob is pointer arithmetic into that RAM and performs no file read. However, DONE/API ram_blobs/file_blobs/file_mb belong to the unused mmap/complement source and explicitly remain zero with arena; they are not an independent arena SSD read measurement. Logical expert file-read counts during arena decode are UNAVAILABLE. See expert-io-provenance.json and startup arena logs. Other PLE/model traffic is distinct from routed-expert streaming.

## Negative and excluded records

Invalid recorded requests in summary: 6. Diagnostic-only requests in summary: 24. Full raw request/stream/log/config files remain preserved. A cell with fewer than three valid repetitions is explicitly incomplete, and no three-run headline median is presented.


## Answers to the requested questions

1. Integration: already integrated on the frozen current main. Both binaries use the same source base; original/optimized helper is an OFF/ON flag A/B.
2. Conflicts: none; no second merge was applied. Local default-off diagnostic patch is recorded separately and excluded from final speed.
3. Tests: native72 each:66 passed,2 skipped,4 environmental failures (missing Q2_0 fixtures and memlock permission). Python268 each:OK,7 skipped after adding the same optional jsonschema dependency. This is not an all-tests-pass claim.
4. Stability: inspect the preserved negative records below. Selected finalists require3 valid requests/cell; no OOM/crash may be hidden.
5. Correctness:10 identical-input pairs,4 exact outputs and6 free-generation divergences; no nonfinite/garbled output. Both JSON cases valid. Two budget-limited code cases were extended to natural stop; binary-search examples and edge tests passed. No LLM judge or numerical logits-parity claim.
6. Primary32K median decode: layer split 156.20, original helper 84.40, optimized helper 103.80 tok/s.
7. Optimized helper vs layer split: -33.55% TG; vs original helper 22.99%. Same initial helper capacities and identical MTP/warmup within the primary phase.
8. Context progression: the final matrix and PP/TG ranges are printed above; each row is keyed by actual token count, not configured maximum.
9. Primary32K CPU fallback entries: original 6263.00, optimized 610.00; change -90.26%. These are routed entries, not distinct experts.
10. Complementarity: verified directly in separate diagnostic ID snapshots; headline runs do not enumerate ID sets.
11. Startup/after-warmup/after-run3 overlap: see exact diagnostic table. Percent denominator is helper resident count11796, not the combined cache.
12. Returned logical bytes32K: original 104018739.20, optimized 144703488.00; change 39.11%. Do not call this a total PCIe reduction: optimized helper handles more entries. The printed full-rows hypothetical includes all routed entries, including entries not computed by the helper. Hardware dmon RX/TX is separate and sparse.
13. CPU32K mean whole-VM utilization: split 68.10%, original 94.95%, optimized 76.55%. Peak values and process utilization appear in the system table. Process100% is one vCPU, not the entire16-vCPU VM.
14. GPU32K mean utilization0/1: split 40.00/54.00%; original 99.00/4.67%; optimized 99.50/6.00%.
15. Best complete32K topology: LS-B; production recommendation also requires the steady/context battery.
16. Workload dependence: measured speed uses saved code-agent/repository inputs. Short math/prose correctness cases are insufficient to choose a mixed/math throughput winner.
17. Stripe/layer: one helper follows the same placement path; a distinct A/B is not meaningful on this two-card system.
18. Auto/fixed optimized helper: auto TG 102.90, fixed 103.80; identical physical capacities. This small difference is not evidence that manually resizing the cache wins.
19. Candidate future optimization: prioritize helper ownership before assigning primary PCIe-mapped misses, so helper-resident experts are not consumed by the primary mapped path. The current controlled campaign does not implement this algorithm change; a separate preserved-original A/B and correctness check would be required.
20. Recommendation: KEEP_LAYER_SPLIT. Layer split wins both steady2048 decode and all four actual-context cells by more than5%, with higher PP and lower TTFT. Optimized helper improved the primary short32K batch over original helper, but regressed on steady2048 decode; it does not replace layer split for these measured workloads.

## System and transport metrics

| Config/context | CPU VM mean/peak % | Process mean/peak % | GPU0/1 power W | RSS GiB | RAM used GiB | VRAM0/1 GiB | Helper returned bytes/token | Helper wait ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H-OLD/31400 | 94.95/100.00 | 1512.40/1590.70 | 192.52/76.97 | 53.75 | 58.02 | 23.31/23.34 | 406323.20 | 31.00 |
| H-OLD-STEADY2048/31400 | 96.22/100.00 | 1527.63/1590.40 | 215.55/77.46 | 53.52 | 57.85 | 23.31/23.34 | 353075.20 | 153.00 |
| H-OPT-FIXED/31400 | 76.55/87.70 | 1213.55/1394.60 | 217.67/78.75 | 53.74 | 58.02 | 23.31/23.34 | 565248.00 | 119.00 |
| H-OPT-FIXED-FINAL-TOKFIX/63402 | 56.23/76.00 | 884.53/1203.80 | 206.81/68.07 | 53.99 | 58.25 | 23.31/23.34 | 596377.60 | 113.00 |
| H-OPT-FIXED-FINAL-TOKFIX/127002 | 73.03/89.40 | 1157.80/1413.70 | 216.41/70.81 | 54.23 | 58.64 | 23.31/23.34 | 612761.60 | 126.00 |
| H-OPT-FIXED-FINAL-TOKFIX/259507 | 58.17/82.60 | 923.80/1311.10 | 212.82/60.96 | 54.30 | 58.73 | 23.31/23.34 | 632422.40 | 159.00 |
| H-OPT-FIXED-FINAL-TOKFIX-CLEAN32/31400 | 75.50/92.30 | 1197.60/1451.50 | 209.57/78.93 | 53.76 | 58.05 | 23.31/23.34 | 570982.40 | 97.00 |
| H-OPT-FIXED-STEADY2048/31400 | 79.46/98.80 | 1256.54/1568.00 | 197.30/80.73 | 53.53 | 57.95 | 23.31/23.34 | 552755.20 | 852.00 |
| LS-B/31400 | 68.10/99.20 | 1084.25/1577.60 | 145.31/191.94 | 54.59 | 58.90 | 23.28/23.39 | UNAVAILABLE | UNAVAILABLE |
| LS-B-FINAL-TOKFIX/31400 | 69.20/97.50 | 1099.50/1546.10 | 135.44/178.10 | 54.59 | 58.91 | 23.28/23.40 | UNAVAILABLE | UNAVAILABLE |
| LS-B-FINAL-TOKFIX/63402 | 87.00/90.30 | 1390.90/1436.20 | 160.04/181.59 | 54.85 | 59.10 | 23.28/23.40 | UNAVAILABLE | UNAVAILABLE |
| LS-B-FINAL-TOKFIX/127002 | 69.25/93.20 | 1105.80/1476.90 | 143.40/167.77 | 55.15 | 59.47 | 23.28/23.40 | UNAVAILABLE | UNAVAILABLE |
| LS-B-FINAL-TOKFIX/259507 | 73.70/96.60 | 1174.70/1536.50 | 149.99/191.20 | 55.24 | 59.51 | 23.28/23.40 | UNAVAILABLE | UNAVAILABLE |
| LS-B-STEADY2048/31400 | 94.78/99.90 | 1507.65/1590.00 | 183.86/217.08 | 54.37 | 58.62 | 23.27/23.39 | UNAVAILABLE | UNAVAILABLE |

Each memory value is the median of per-request sampled peaks; raw records retain individual peaks. RSS is the server/engine process tree, RAM used is VM-wide. Short decode only has a few1Hz samples; steady2048 is more representative. Dmon totals are not a causal bus-traffic decomposition.


## Speculative-decode progression

| Config/context | MTP drafted | MTP accepted | Acceptance % | Accepted/window | Verify windows | Mean window ms |
|---|---:|---:|---:|---:|---:|---:|
| H-OLD/31400 | 214.00 | 166.00 | 77.57 | 1.78 | 93.00 | 32.61 |
| H-OLD-STEADY2048/31400 | 1646.00 | 1360.00 | 82.62 | 1.97 | 689.00 | 32.92 |
| H-OPT-FIXED/31400 | 211.00 | 162.00 | 79.08 | 1.71 | 95.00 | 26.82 |
| H-OPT-FIXED-FINAL-TOKFIX/63402 | 213.00 | 155.00 | 72.77 | 1.53 | 101.00 | 29.14 |
| H-OPT-FIXED-FINAL-TOKFIX/127002 | 219.00 | 147.00 | 67.12 | 1.35 | 109.00 | 27.93 |
| H-OPT-FIXED-FINAL-TOKFIX/259507 | 227.00 | 149.00 | 65.64 | 1.39 | 107.00 | 29.70 |
| H-OPT-FIXED-FINAL-TOKFIX-CLEAN32/31400 | 210.00 | 160.00 | 76.53 | 1.67 | 96.00 | 29.76 |
| H-OPT-FIXED-STEADY2048/31400 | 1669.00 | 1345.00 | 80.11 | 1.91 | 704.00 | 38.82 |
| LS-B/31400 | 214.00 | 163.00 | 76.64 | 1.72 | 95.00 | 17.29 |
| LS-B-FINAL-TOKFIX/31400 | 214.00 | 158.00 | 73.04 | 1.61 | 98.00 | 22.55 |
| LS-B-FINAL-TOKFIX/63402 | 216.00 | 154.00 | 71.89 | 1.50 | 103.00 | 20.12 |
| LS-B-FINAL-TOKFIX/127002 | 215.00 | 156.00 | 72.56 | 1.53 | 102.00 | 22.84 |
| LS-B-FINAL-TOKFIX/259507 | 222.00 | 156.00 | 72.22 | 1.56 | 100.00 | 19.33 |
| LS-B-STEADY2048/31400 | 1646.00 | 1380.00 | 83.84 | 2.06 | 669.00 | 17.22 |

Primary32K and final-matrix32K are separate batches and are not pooled. Matrix warmups add a context-specific nonce to the saved warmup; each finalist follows the same context/warmup order. Greedy outputs can diverge after floating-point/cache routing differences, so MTP acceptance and TG can change with the output trajectory even for identical input IDs. These are end-to-end speculative decode results, not a fixed-output kernel-only speed comparison.

## Steady-decode bottleneck evidence

| Config | TG | GPU-reach wait ms/window | CPU work ms/window | PCIe experts/layer-window | GPU0 RX MB/s | GPU1 RX MB/s |
|---|---:|---:|---:|---:|---:|---:|
| LS-B-STEADY2048 | 174.00 | 6.23 | 0.97 | 0.01 | 143.00 | 213.82 |
| H-OLD-STEADY2048 | 90.40 | 17.18 | 7.02 | 1.40 | 5073.95 | 46.18 |
| H-OPT-FIXED-STEADY2048 | 74.90 | 29.63 | 2.06 | 2.53 | 7910.16 | 172.23 |

Optimized-helper CPU misses fall, but primary GPU reach-wait and mapped-RAM PCIe work grow; GPU1 remains lightly utilized. This supports a primary dispatch/host-memory path limitation rather than expert SSD streaming. It does not prove the PCIe link is continuously saturated or that CPU utilization equals useful GEMV work; worker spinning and GPU coordination can contribute. The existing hardware campaign measured PHB/no P2P, approximately12.6GB/s pinned one-way GPU0 transfer, and approximately26.7GB/s aggregate dualH2D; those are distinct microbenchmarks. Our topology choice is supported by direct inference results, not by treating utilization alone as a bottleneck proof.

## Frozen finalist configurations

Exact server/engine command, environment and binary SHA are stored in configs/LS-B-FINAL-TOKFIX.json and configs/H-OPT-FIXED-FINAL-TOKFIX.json and in every canonical raw record. The layer-split candidate uses auto(K25), explicitpcie-frac0.28, expert-cache auto, prefill auto, MTP4/min-p0.5, suffix-draft0, INT8/kv-resident32768, workers15 and max-context262144. The helper uses primaryCLI6567/result8586 slots, helper11796 slots, pcie-frac0.37 and remote-expert-opt, with the same remaining settings. No resident-budget mode, speed projection, weight conversion or algorithm patch is enabled in headline runs.

## RECOMMENDATION

KEEP_LAYER_SPLIT

Layer split wins both steady2048 decode and all four actual-context cells by more than5%, with higher PP and lower TTFT. Optimized helper improved the primary short32K batch over original helper, but regressed on steady2048 decode; it does not replace layer split for these measured workloads.

All numbers in tables come from summary.json, whose raw_paths link canonical request records. Reproduce with analyze.py, then report-refresh.py; inspect independent audit-refresh.json for completion and fairness checks.
