# Golden Swap Phase 3: planner work and dependent GPU waits

**DECISION_PRESERVING_OPTIMIZATION_NO_CONFIRMED_PRACTICAL_GAIN**

Immutable incoming-query memoization removed about 97% of targeted recomputation and retained exact deterministic policy/work parity. Main median hook CPU fell 63–133 ms and measured dependent plan A waits fell 46–153 ms. No main task met the frozen >3% practical OPT/BASE timing criterion. Inventory/Chinook retain gains versus contemporary current; Archive/WebSocket do not change classification. This narrows the repeated-query bottleneck without proving that all planner work is overlapped or that policy economics alone dominate.

36/36 valid primary requests; 6/6 valid independent-source replays. Start 2026-10-07T15:09:55.841843+00:00; immutable deadline 2026-10-07T21:09:55.841843+00:00; regeneration elapsed 139.64 minutes. Source `f3b4f19157b39ae017e2fd91814c8f5728e3b1cc`; binary SHA256 `1bf524e32fd3233aeb3149231a4f48da1e52401b9f4686bd6669b1690033ae82`. Frozen Phase 2 source `c12a0b11f02ae7b635dc3c6a15ff14f37319ce22` / binary `46b53020499a8d9b859a59bcf723ab32b65f42b32ff5c6c4639dabf5be6d6aff`; logistic `065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e`. Pinned upstream base 6f32ec070f23ced9f50e704d854d775da52591ab, Qwen revision 38bb39ee97821de2c9009abb7e93950eec396e66; dependency/config/patch identities retained.

This is conditional fixed-work oracle-incoming replay with causal history victims, minimum first-use TC and privileged current-window protection. All main/MTP routing, coefficients, required expert computation and initial state stay fixed. CPU/GPU arithmetic may differ: forced output/work fingerprints do not establish natural-generation quality or bitwise mathematical equivalence. Q4/K24/PCIe0.28/pool100us/15workers/MTP4minp0.5/INT8KV/prefillauto/reuseOFF and ordinary serving remain unchanged. Five charged spares 17,305,600 B remain inside existing capacity.

## Existing evidence, before new inference

Phase 1/2 established premature eviction before first target/use as the original unused-copy mechanism, minimum TC removed it, post-use 48 lost useful service, inactive risk thresholds did not change actions, and no confirmed learned-scorer advantage existed. These are prior results, not new Phase 3 measurements. Phase 3 read 56 prior complete journals without modifying previous campaigns.

| Task | Input | Output | Windows | First-use distance invocations | Evicted lifetime invocations | Distinct uses/admission | Avoided entries/GB | Late publications |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| code-archive | 6983 | 2048 | 769 | 59.0 | 10006.5 | 11.0 | 1009.1 | 19.0 |
| math-inventory | 165 | 2048 | 766 | 58.0 | 11135.0 | 14.0 | 1102.1 | 18.0 |
| text-websocket | 30383 | 1773 | 636 | 57.0 | 8642.5 | 10.0 | 1072.8 | 26.0 |
| mixed-chinook | 1899 | 2048 | 548 | 45.0 | 5171.0 | 15.0 | 1412.4 | 41.0 |
| text-json-rfc8259 | 2699 | 2816 | 949 | 59.0 | 11198.0 | 14.0 | 1020.8 | 16.5 |

Inventory/Chinook had more repeated service than Archive/WebSocket; Chinook had the highest avoided lane demand per copied byte. Late publication was rare in all four, so missed target timing alone does not explain the prior task split. Input/context lengths also differ greatly: WebSocket is near32K while Inventory is165 tokens. These four trajectories cannot establish a universal domain classifier. Survivors are right-censored; evicted lifetime distributions are separate from survivor ages. See existing-data-analysis.json for all per-run queue/stage/copy/slack/return distributions and phase0-reuse-reference.json for retained batch reuse/burst definitions. Missing exact DMA duration, native intended target, GPU absolute clock alignment and exact prevented-admission identity are explicit.

## Optimization and logical parity

The whole negative admission decision depends on dynamic ownership, protection, history, queue state and the timing-derived lead. It is unsafe to memoize it as one value. The chosen smaller intervention caches only immutable incoming `(next target, lane count over768 invocations)` until the exact next lower occurrence leaves or upper occurrence enters. E64 enumeration and all mutable policy checks remain intact. Cache 491,520 B is charged in host state for all arms; preparation/request reset, rewind and exact lower/upper invalidations are counted. Full incoming only; finite-information views use the original path. No new victim-future queries, score features or weights.

26 deterministic OFF/ON task/scorer pairs cover all 12 corpus tapes plus existing RFC8259. Every evaluated candidate outcome/NO_SWAP hash, complete lifecycle bytes, logical admission payload/order/ownership and required work match.16 inherited development/calibration OFF points also match retained Phase 2 results. The dense cache fixture checks 491,520 exact reference queries, same-event policy-state changes, boundary additions/removals, rewinds and finite-horizon fallback. Native safety/ownership and 9 targeted tests passed; logistic 4,000 predictions/prefix 300 batches retain maximum errors 1.32e-7/1.18e-7.

The deterministic model fixes physical cadence. Live copies can become ready at different milestones and the inherited lead depends on measured copy/event timing. Live logical admission traces are therefore compared and reported, never claimed identical solely because aggregate work matches. All live requests must separately pass actual publication/slot/generation/work checks. See paired-blocks.json and the live-trajectory diagnostic for the first divergence and unchanged source dependencies.

## Timer semantics and instrumentation guard

Plan A is actual verifier-stream time spinning for the host-published GPU plan, measured inside the existing one-thread kernel with GPU globaltimer. Mapped B and CPU flags are separate later waits. No extra kernel launch or per-layer synchronization; request-end48B/device readback/reset is charged to whole wall after existing commit. Logical metadata96B total plus allocator granularity appears in VRAM telemetry; expert capacity is attested unchanged. Ready-flag floor in fixture0/1024ns;20ms blocking fixture passed on both GPUs. Device-plan skip paths are not profiled and remain disabled in the frozen configuration.

Host thread CPU measures the oracle host hook, excludes other copy workers; planner wall includes nested selection and publication acknowledgment waits. Victim selection wraps resident enumeration; feature/model work also includes separate reserve/guard scorer calls. GPU wait A can overlap shared/peer useful work; its sum is observed blocked dependency time and an upper bound on its isolated whole-request exposure, not additive exclusive latency. No cross-device absolute clock or sum of nested counters is used as exact stall. Current hook CPU is not full native planner CPU; host-plan journal includes native assembly, while adaptation outside it remains unassigned.

| Instrumentation pair | Profile ON/OFF decode change % | Completion wall change % |
| --- | --- | --- |
| 1 | -2.81 | -1.92 |
| 2 | 1.41 | 0.55 |

Two opposite-order development pairs did not trigger the predeclared >3% regression-in-both-pairs gate; this small N does not prove zero instrumentation cost. Frozen Phase 2 development decode19.2644s; new unprofiled OFF[19.7805, 19.7364]. Separate binary observation is behavioral/overhead sanity, not a headline stale control. Main arms share one binary and identical enabled wait instrumentation.

## Complete contemporaneous matrix

Four exposed fixed regression tapes x3 arms x3 counterbalanced adjacent blocks, seed 730071; RFC8259 x2 reversed blocks. Fresh server, saved 4096-input/64-output warmup, native prefill, exact recorded initial state, common tape/index setup and complete tape execution. Real copies, final commit/drain/restoration, readback, attestation and flush remain charged. Startup/warmup/shutdown are separate. WebSocket emits 1773, not 2048. RFC8259 is previously evaluated independent source, not a fresh holdout. Main inputs/outputs/windows/context occupancies are given in input-manifest.json.

| Task | Arm | Valid/attempts | Replay tok/s min/median/max | Decode median s | Completion wall median s | Local % | CPU/mapped entries | Copy GB | Oracle hook wall ms | Hook CPU ms | GPU plan A wait ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| code-archive | PLANNER_BASELINE | 3/3 | 96.57/96.84/99.44 | 21.1478 | 31.2814 | 96.70 | 36954/3085 | 30.529 | 1791.3 | 1316.5 | 2088.7 |
| code-archive | PLANNER_OPT | 3/3 | 96.63/97.00/97.72 | 21.1130 | 31.4001 | 96.69 | 37072/3097 | 30.470 | 1711.1 | 1229.3 | 1990.1 |
| code-archive | REPLAY_CURRENT | 3/3 | 96.21/96.62/97.83 | 21.1958 | 31.4573 | 94.17 | 63663/7164 | 34.128 | 1.6 | 54.4 | 300.7 |
| math-inventory | PLANNER_BASELINE | 3/3 | 99.48/100.51/104.58 | 20.3764 | 22.3712 | 96.67 | 38392/2846 | 33.479 | 1862.5 | 1346.6 | 2153.3 |
| math-inventory | PLANNER_OPT | 3/3 | 100.15/101.65/106.02 | 20.1479 | 22.1249 | 96.66 | 38482/2847 | 33.520 | 1817.2 | 1283.2 | 2106.8 |
| math-inventory | REPLAY_CURRENT | 3/3 | 96.32/96.39/96.83 | 21.2474 | 23.2385 | 93.70 | 69946/8034 | 36.374 | 1.6 | 56.5 | 298.9 |
| mixed-chinook | PLANNER_BASELINE | 3/3 | 109.18/112.20/112.37 | 18.2534 | 23.4244 | 94.46 | 51161/5811 | 38.076 | 2031.8 | 1400.7 | 2284.4 |
| mixed-chinook | PLANNER_OPT | 3/3 | 111.92/113.59/122.04 | 18.0303 | 23.1974 | 94.46 | 51166/5817 | 38.058 | 1916.3 | 1289.4 | 2158.1 |
| mixed-chinook | REPLAY_CURRENT | 3/3 | 101.63/102.30/117.70 | 20.0203 | 25.2026 | 89.25 | 93526/17007 | 35.650 | 1.1 | 40.3 | 262.8 |
| text-json-rfc8259 | PLANNER_BASELINE | 2/2 | 106.65/107.17/107.68 | 26.2772 | 33.3647 | 96.86 | 47382/3336 | 35.971 | 2217.8 | 1638.6 | 2603.6 |
| text-json-rfc8259 | PLANNER_OPT | 2/2 | 107.64/114.59/121.54 | 24.6655 | 31.7691 | 96.86 | 47316/3315 | 36.000 | 1692.1 | 1215.0 | 1976.6 |
| text-json-rfc8259 | REPLAY_CURRENT | 2/2 | 107.84/107.88/107.92 | 26.1021 | 33.2299 | 94.58 | 79422/8006 | 41.003 | 2.0 | 68.7 | 376.8 |
| text-websocket | PLANNER_BASELINE | 3/3 | 95.59/95.91/97.31 | 18.4860 | 40.3854 | 96.72 | 32209/2369 | 30.210 | 1685.3 | 1223.6 | 1937.6 |
| text-websocket | PLANNER_OPT | 3/3 | 97.19/97.46/100.89 | 18.1928 | 40.1715 | 96.73 | 32130/2370 | 30.179 | 1595.7 | 1123.3 | 1840.2 |
| text-websocket | REPLAY_CURRENT | 3/3 | 94.32/94.55/96.10 | 18.7529 | 40.6878 | 93.66 | 60227/6574 | 32.619 | 1.4 | 46.4 | 267.7 |

Copy GB includes completed ordinary payload plus mandatory restoration; sampled readback/metadata traffic is separate and charged in wall. Exact transaction partitions and reload/absence data are in live-attempts.json, not inferred from independent medians.

### Reconciled ordinary transaction outcomes

These are exact sums across the stated attempts, after per-run generation reconciliation; restoration is separate. Native completion is certified by publication, and any unpublished native completion remains explicitly unknown in the per-run records.

| Task | Arm | N | Generations | Completed GB | Published used GB | Unused evicted GB | No-use-yet end GB | Completed unpublished GB | Restoration GB | Chronological reloads | Victim-absent entries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| code-archive | PLANNER_BASELINE | 3 | 28980 | 91.5524 | 91.5493 | 0.0031 | 0.0000 | 0.0000 | 0.0519 | 13039 | 46240 |
| code-archive | PLANNER_OPT | 3 | 28932 | 91.4044 | 91.3952 | 0.0092 | 0.0000 | 0.0000 | 0.0519 | 12999 | 46255 |
| code-archive | REPLAY_CURRENT | 3 | 32466 | 102.3827 | 87.7710 | 8.9411 | 5.6706 | 0.0000 | 0.0000 | 15375 | 91647 |
| math-inventory | PLANNER_BASELINE | 3 | 31820 | 100.4177 | 100.4177 | 0.0000 | 0.0000 | 0.0000 | 0.0519 | 15003 | 54326 |
| math-inventory | PLANNER_OPT | 3 | 31843 | 100.4869 | 100.4869 | 0.0000 | 0.0000 | 0.0000 | 0.0519 | 15022 | 54405 |
| math-inventory | REPLAY_CURRENT | 3 | 34608 | 109.1205 | 96.0473 | 9.6230 | 3.4502 | 0.0000 | 0.0000 | 16872 | 100920 |
| mixed-chinook | PLANNER_BASELINE | 3 | 36578 | 114.1825 | 114.1825 | 0.0000 | 0.0000 | 0.0000 | 0.0519 | 14997 | 73953 |
| mixed-chinook | PLANNER_OPT | 3 | 36609 | 114.2782 | 114.2782 | 0.0000 | 0.0000 | 0.0000 | 0.0519 | 15024 | 74004 |
| mixed-chinook | REPLAY_CURRENT | 3 | 34263 | 106.9498 | 95.1601 | 8.1998 | 3.5899 | 0.0000 | 0.0000 | 12885 | 103419 |
| text-json-rfc8259 | PLANNER_BASELINE | 2 | 22820 | 71.9065 | 71.9065 | 0.0000 | 0.0000 | 0.0000 | 0.0346 | 11600 | 42217 |
| text-json-rfc8259 | PLANNER_OPT | 2 | 22839 | 71.9649 | 71.9649 | 0.0000 | 0.0000 | 0.0000 | 0.0346 | 11618 | 42100 |
| text-json-rfc8259 | REPLAY_CURRENT | 2 | 26066 | 82.0066 | 71.9366 | 8.1064 | 1.9636 | 0.0000 | 0.0000 | 14014 | 86782 |
| text-websocket | PLANNER_BASELINE | 3 | 28785 | 90.5506 | 90.5506 | 0.0000 | 0.0000 | 0.0000 | 0.0519 | 13586 | 40488 |
| text-websocket | PLANNER_OPT | 3 | 28784 | 90.5475 | 90.5475 | 0.0000 | 0.0000 | 0.0000 | 0.0519 | 13582 | 40457 |
| text-websocket | REPLAY_CURRENT | 3 | 31143 | 97.8558 | 82.8485 | 9.2059 | 5.8015 | 0.0000 | 0.0000 | 15099 | 90276 |

### Planner and guard work

Median per-run timers are nested: victim selection wraps its resident-enumeration loop; feature/model work is inside scorer calls during enumeration and also reserve/guard calls. Publication coordination is inside the oracle hook. Incoming candidate enumeration is not the resident-enumeration timer. These counters are not additive stall. Repeated logical veto opportunities remain intentional even when their expensive immutable query results are reused.

| Task | Arm | Enumeration ms | Selection ms | Publication ms | Candidate opportunities | Incoming-cost veto | Capacity veto | Risk veto |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| code-archive | PLANNER_BASELINE | 658.1 | 659.9 | 656.6 | 1708848 | 1699190 | 3821 | 0 |
| code-archive | PLANNER_OPT | 665.9 | 667.7 | 665.7 | 1696315 | 1686679 | 3649 | 0 |
| code-archive | REPLAY_CURRENT | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0 |
| math-inventory | PLANNER_BASELINE | 699.7 | 701.7 | 700.1 | 1743648 | 1733051 | 3865 | 0 |
| math-inventory | PLANNER_OPT | 708.8 | 710.7 | 709.9 | 1744653 | 1734056 | 3922 | 0 |
| math-inventory | REPLAY_CURRENT | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0 |
| mixed-chinook | PLANNER_BASELINE | 740.3 | 742.5 | 838.3 | 2084854 | 2072662 | 6237 | 0 |
| mixed-chinook | PLANNER_OPT | 732.4 | 734.6 | 811.1 | 2085020 | 2072836 | 6228 | 0 |
| mixed-chinook | REPLAY_CURRENT | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0 |
| text-json-rfc8259 | PLANNER_BASELINE | 817.2 | 819.4 | 795.0 | 2319399 | 2307989 | 4301 | 0 |
| text-json-rfc8259 | PLANNER_OPT | 653.6 | 655.4 | 650.1 | 2354799 | 2343379 | 4586 | 0 |
| text-json-rfc8259 | REPLAY_CURRENT | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0 |
| text-websocket | PLANNER_BASELINE | 656.2 | 657.9 | 652.5 | 1371749 | 1362151 | 3501 | 0 |
| text-websocket | PLANNER_OPT | 639.8 | 641.7 | 624.3 | 1365398 | 1355788 | 3541 | 0 |
| text-websocket | REPLAY_CURRENT | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0 |

| Task | Blocks | OPT/BASE decode % min/median/max | OPT/BASE wall % min/median/max | Decode gain signs | Wall gain signs | BASE/CURRENT decode % | OPT/CURRENT decode % | BASE/CURRENT wall % | OPT/CURRENT wall % | Optimization criterion | BASE/current criterion | OPT/current criterion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| code-archive | 3 | -1.18/0.22/2.52 | -0.85/0.55/1.90 | [False, True, False] | [False, True, False] | 0.05 | -0.82 | -0.03 | -0.34 | False | False | False |
| math-inventory | 3 | -2.13/-1.36/0.36 | -1.90/-0.84/0.39 | [False, True, True] | [False, True, True] | -4.17 | -5.17 | -3.73 | -4.82 | False | True | True |
| mixed-chinook | 3 | -8.06/-2.45/-1.07 | -6.38/-1.89/-0.71 | [True, True, True] | [True, True, True] | -6.92 | -9.20 | -5.44 | -7.23 | False | True | True |
| text-json-rfc8259 | 2 | -12.25/-6.10/0.04 | -9.68/-4.76/0.15 | [True, False] | [True, False] | 0.67 | -5.51 | 0.41 | -4.40 | False | False | False |
| text-websocket | 3 | -5.25/-1.31/-0.15 | -2.50/-0.37/0.21 | [True, True, True] | [True, True, False] | -1.66 | -2.99 | -1.16 | -1.52 | False | False | False |

Negative time changes are gains. Criterion frozen before main outcomes: median decode-time reduction>3%, faster in>=2/3 main blocks, median wall regression<=1%, and fewer than2 blocks with>3% wall regression. IndependentN2 is descriptive and not evaluated as a three-block criterion. Pair ratios retain shared-reference correlation; three repeats are not independent task generalization. All raw/slow observations are retained without CPU-steal correction.

| Task | Incoming recomputation removed % | Hook CPU removed ms | Hook wall removed ms | Plan A wait removed ms | Pairs |
| --- | --- | --- | --- | --- | --- |
| code-archive | 97.29 | 70.7 | 64.3 | 63.6 | 3 |
| math-inventory | 97.21 | 63.4 | 45.3 | 46.5 | 3 |
| mixed-chinook | 96.91 | 132.6 | 144.1 | 152.7 | 3 |
| text-json-rfc8259 | 97.46 | 423.6 | 525.7 | 627.1 | 2 |
| text-websocket | 97.00 | 100.3 | 89.7 | 97.4 | 3 |

Targeted evaluation means the expensive incoming next/count query pair. Candidate opportunities, cost-floor comparisons and logical veto scans continue, preserving policy coverage. Do not claim that all candidate enumeration disappeared. Cache lookups/hits/misses/invalidations and optional diagnostic lookup/recompute-maintenance timer are retained; maintenance timing is gated OFF for headline runs, so its zero counter means unmeasured, not free.

Some targeted work is visibly reflected in lower dependent-stream wait, so blanket H2 (mostly overlapped planner) is not established. H1 has partial CPU/wait evidence but no predeclared practical main-task latency success. H3 is consistent with the unchanged task classification, yet remaining victim selection and publication work could still be exposed. H4 is not observed in exhaustive fixed-cadence decision/query validation; live schedules differ after earlier publication visibility changes. Exact critical-path oracle/publication attribution remains bounded, not measured as a unique percentage. The unusually fast RFC8259 OPT block1 and Chinook block3 are retained: their CPU/planning/stream-wait changes are larger than the other pairs and sampled VM steal/operating conditions vary. They are not corrected, discarded, or used to select extra repeats.

## Independent continuous-tail check

RFC8259 uses 2699 input+2816 output, 949 verifier windows and 5515 committed context positions within 32768. Measured main boundary 2048 output/705 windows has 768 observed continuation tokens in the same request; all arms execute the complete tape.

| Block | Arm | Prefix observation span s | Prefix tok/s | Whole decode s | Whole wall s | Unused prefix survivor B | Later-used B | No observed tail use B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PLANNER_BASELINE | 19.8774 | 103.03 | 26.4039 | 33.4882 | 28160000 | 28160000 | 0 |
| 1 | PLANNER_OPT | 17.5536 | 116.67 | 23.1700 | 30.2473 | 31232000 | 31232000 | 0 |
| 1 | REPLAY_CURRENT | 19.8767 | 103.03 | 26.0924 | 33.2176 | 1383731200 | 865177600 | 518553600 |
| 2 | PLANNER_BASELINE | 19.6791 | 104.07 | 26.1506 | 33.2412 | 31232000 | 31232000 | 0 |
| 2 | PLANNER_OPT | 19.8139 | 103.36 | 26.1611 | 33.2909 | 31232000 | 31232000 | 0 |
| 2 | REPLAY_CURRENT | 19.9617 | 102.60 | 26.1118 | 33.2422 | 1383731200 | 865177600 | 518553600 |

Prefix observation spans are a separately defined boundary readout, not the native full-decode metric. Tail completion and mandatory work remain charged. No tail nonuse proves permanent nonuse. See paired results for the actual small N transfer check.

## Resources, repairs and limitations

Both devices VRAM/utilization/power/clocks/temperature/memory clocks/PCIe link generation and width, host RAM/swap, process CPU and steal are retained per request. No host changes, no overlapping compilation/training/heavy analysis during headline requests. Peak/resources and distribution fields are in live-attempts.json and complete telemetry gzip copies. Sampling does not identify DMA-only saturation.

Request-phase telemetry below includes prefill/decode/completion, separated from startup/warmup in phase-resource-diagnostics.json. CPU/steal columns are medians of per-run sampled medians; peaks are maxima across those run samples, not pooled medians or exclusive decode attribution.

| Task | Arm | System CPU % | Steal % | Peak steal % | Peak process RSS GiB | Peak VRAM MiB GPU0/1 | Peak power W GPU0/1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| code-archive | PLANNER_BASELINE | 34.00 | 3.70 | 21.80 | 76.38 | 23836/24028 | 230.9/217.7 |
| code-archive | PLANNER_OPT | 34.15 | 5.35 | 20.00 | 76.38 | 23836/24028 | 234.6/220.2 |
| code-archive | REPLAY_CURRENT | 37.65 | 4.40 | 20.10 | 76.36 | 23836/24028 | 234.3/217.3 |
| math-inventory | PLANNER_BASELINE | 36.20 | 5.90 | 19.90 | 76.36 | 23836/24026 | 174.5/192.4 |
| math-inventory | PLANNER_OPT | 35.40 | 4.30 | 19.20 | 76.36 | 23836/24026 | 174.4/192.6 |
| math-inventory | REPLAY_CURRENT | 42.35 | 7.45 | 24.00 | 76.34 | 23836/24026 | 168.5/187.9 |
| mixed-chinook | PLANNER_BASELINE | 43.65 | 6.35 | 21.30 | 76.28 | 23836/24026 | 161.2/176.3 |
| mixed-chinook | PLANNER_OPT | 43.80 | 4.85 | 25.20 | 76.27 | 23836/24026 | 168.2/185.4 |
| mixed-chinook | REPLAY_CURRENT | 49.65 | 7.55 | 25.60 | 76.26 | 23836/24026 | 168.9/184.9 |
| text-json-rfc8259 | PLANNER_BASELINE | 35.83 | 6.30 | 21.20 | 76.44 | 23836/24026 | 168.2/186.7 |
| text-json-rfc8259 | PLANNER_OPT | 34.47 | 4.50 | 20.60 | 76.44 | 23836/24026 | 177.5/197.1 |
| text-json-rfc8259 | REPLAY_CURRENT | 40.52 | 7.50 | 24.10 | 76.42 | 23836/24026 | 174.1/192.0 |
| text-websocket | PLANNER_BASELINE | 13.50 | 1.90 | 21.70 | 76.34 | 23836/24028 | 256.6/240.4 |
| text-websocket | PLANNER_OPT | 13.10 | 1.70 | 19.00 | 76.33 | 23836/24028 | 257.6/241.0 |
| text-websocket | REPLAY_CURRENT | 13.00 | 1.90 | 23.30 | 76.31 | 23836/24028 | 257.6/240.8 |

The unusually fast RFC8259 OPT block1 has request-phase sampled median steal 0.8%, versus 8.0% for its baseline; block2 OPT has 8.2%, versus 4.6% baseline. Chinook block3 baseline/OPT/current have 6.35%/2.8%/0.6%. These are measured confounders, not an exclusive explanation or a correction factor. GPU0 sampled median SM clock was 2790 MHz in these requests. All observations remain in the comparisons, including the large improvements.

Repairs retained: first raw simulator SHA comparison included an unmodeled host issue clock (all other fields/lifecycle identical); corrected normalization excludes only that clock. Initial scorer pickle check used an environment without sklearn; frozen Phase 1 environment passed unchanged. Administrative timeout argument placement failed before subprocess start. First integration server reached readiness but absent payload manifest prevented any warmup/request; copied frozen manifest and fresh attempt2 passed. Patch context whitespace is preserved through narrowly scoped Git attributes; CSV generators useLF. Progress heartbeat block retention was repaired for subsequent runners; frozen run order and completed counts remain authoritative. Additional actual repairs, if any, are in attempt-ledger.jsonl and completion-audit.json.

Confidence is high for exact conditional query/decision parity in deterministic validation and safe required live work. Timing confidence is descriptive: one VM, four already-exposed tapes, three repeats each, independent source previously evaluated,N2, and asynchronous readiness changes. Full oracle is historical context, not a new contemporary Phase 3 arm or an optimal upper bound. No fully causal incoming predictor, natural generation quality, longer contexts, tool execution or production deployment is established.

## Required answers and next experiment

1. Incoming next/count recomputation fell by median 97.286% Archive,97.208% Inventory,96.909% Chinook and96.996% WebSocket; RFC8259 median 97.456%. These are exact targeted query pairs, not all incoming scans or veto opportunities, which remain reevaluated. The >50% targeted-work mechanism gate passed.

2. All 26 deterministic OFF/ON task/scorer pairs preserve candidate outcomes/NO_SWAP hashes and full logical admission/lifecycle/ownership/work. 16 inherited OFF points match retained Phase 2 accounting/admission hashes. Live action/service traces differ in all14 blocks; in 14/14 an earlier publication visibility difference precedes the first incoming-selection divergence. This supports the allowed asynchronous readiness/lead explanation; exact attribution of every later difference is not recorded. Required work and actual slot/publication safety pass 42/42.

3. Median paired oracle-hook CPU removed: Archive 70.708 ms(5.371%), Inventory 63.358 ms(4.705%), Chinook 132.627 ms(9.197%), WebSocket 100.261 ms(8.194%). Individual pairs include small CPU regressions; remaining median optimized hook CPU is approximately 1.12–1.29s. RFC8259 median 423.585 ms is dominated by one unusually fast optimized run and is not robust N2 evidence.

4. Median paired measured verifier-stream plan A wait removed: Archive 63.614 ms, Inventory 46.483 ms, Chinook 152.720 ms, WebSocket 97.444 ms. This is actual downstream dependency blocking, not an exclusive oracle or whole-request critical-path fraction. Without shared/peer overlap alignment the isolated whole-request contribution is bounded between 0 and min(decode time,sum of observed plan A waits), recorded per run. No exact exposed percentage or sum of nested timers is claimed.

5. OPT/BASE median paired decode-time changes: Archive+0.218%, Inventory−1.355%, Chinook−2.448%, WebSocket−1.312%. Signs faster:1/3,2/3,3/3,3/3 respectively. None passes the predeclared >3% practical optimization criterion. RFC8259 changes−12.248% and+0.040%: the−6.104% median is inconsistent N2 evidence.

6. OPT/BASE median paired completion-inclusive wall changes: Archive+0.546%, Inventory−0.838%, Chinook−1.891%, WebSocket−0.371%. Copies, final drain/restoration, output/tape flush and wait-counter readback remain charged; startup/warmup/shutdown are separate. RFC8259 wall changes−9.678% and+0.150%; all full tails were executed.

7. Archive and WebSocket do not change practical classification: optimized/current median decode changes−0.817% and−2.987% respectively fail the >3% criterion. WebSocket was faster in3/3 blocks, but rounding−2.987% to3% must not turn a failed gate into a win. Archive has a mixed sign.

8. Inventory and Chinook retain the contemporary practical gain versus current. Baseline/current medians are−4.167% and−6.919%; optimized/current medians are−5.175% and−9.197%, with optimized faster 3/3 in both and acceptable wall. This is descriptive evidence on the fixed trajectories, not confirmed domain specialization or independent task generalization.

9. The measured current comparison improves descriptively on Inventory/Chinook and approaches the threshold on WebSocket, while Archive stays neutral. No additional main task crosses the frozen practical gate, so the optimization does not broaden the established practical scope. Historical full-oracle timings are not reused as contemporary controls or retention denominators.

10. Cheap history remains the appropriate common victim baseline for this planner study: Phase 2 found no confirmed logistic advantage, and frozen logistic retains all deterministic common-path/prefix/model parity here. No new live scorer competition was performed, so this does not establish universal history superiority or a new learned benefit.

11. No: this experiment is not sufficient to make causal incoming prediction the next primary step. It removes a small CPU component, leaves Archive/WebSocket below the practical criterion, and leaves substantial plan A dependency delay unattributed. Conditional incoming-oracle headroom remains, but the transfer/publication/planning bottleneck should be resolved before assuming a predictor will convert it into general latency value.

12. The single highest-value unresolved mechanism is how much remaining publication acknowledgment blocks the required plan A consumer, rather than overlapping useful shared/peer work. Optimized main hooks still pay median 624–811 ms publication coordination and measured plan A waits 1840–2158 ms. A bounded phase-correlated host/GPU dependency trace with unchanged scheduling can attribute publication readiness to the consumer and distinguish exposed coordination from policy economics; it precedes another scheduler change.

Strongest next experiment: On one development trajectory and its unchanged history+TC policy, correlate buffered publication start/acknowledgment and plan-ready milestones with the existing GPU consumer wait interval and shared/peer dependency edges. Measure the publication-attributable portion of remaining plan A stall with a bounded instrumentation guard. Do not change incoming information, scorer, scheduling, capacity or expert work; do not start causal incoming prediction until this exposure attribution is resolved.

No Phase 4 or causal incoming project is started. Ordinary serving remains the real-use baseline. Source patches, tested reproducers, all observations/omissions, fixed identities and publication audit are retained; large binary recovery limitations remain explicit.

Primary conclusion: **DECISION_PRESERVING_OPTIMIZATION_NO_CONFIRMED_PRACTICAL_GAIN**.
