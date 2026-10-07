# Golden Swap Phase 2: useful transaction lifetimes and matched victim control

**DOMAIN_SCOPED_CONDITIONAL_REPLAY_GAIN**

Scorer comparison: **NO_CONFIRMED_SCORER_DIFFERENCE**. 48/48 main requests valid. Independent replay: 8/8 valid. Actual elapsed at regeneration: 184.69 minutes; start 2026-10-07T09:33:57Z; hard deadline 2026-10-07T15:33:57Z. No deadline reset. No deployment, push, PR or ordinary launcher change.

This is oracle incoming plus causal cheap/frozen-learned victim control with inherited privileged full-current-window protection. It is a conditional fixed-work replay study. All expert computations, coefficients, physical slots, main/MTP work, token/window dependencies and initial state are preserved. Different CPU/GPU arithmetic can produce different sampled activations and natural output; forced output equality does not establish natural quality or bitwise equivalence.

The original Phase1 unused payload mechanism is now established: generation-specific publication and service-slot reconciliation attributes 99.998328% of learned no-observed-use bytes to re-eviction before their first intended target. The new minimum control protects an admission until actual first local service and a later safe verifier milestone, or target+48 routed invocations. It caps protection at 16 per device/class, returns NO_SWAP safely, and uses the same five charged spares. No new victim-future queries or model features were added.

Confidence: high for generation/work/byte conservation and the observed original churn sequence; task-scoped timing confidence is limited by three repeated blocks per already evaluated tape. The two-block independent check is descriptive. Exact exposed-cost attribution, natural quality and production-causal generalization are unestablished.

## Primary measured table

Configured context is 32768 for all main cases. Actual input/output: archive 6983/2048, inventory 165/2048, WebSocket 30383/1773, Chinook 1899/2048. WebSocket's denominator is 1773. These are four previously evaluated fixed regression tasks, each repeated three times; repeats are not independent source groups or 128K/256K evidence.

Times and rates below are min/median/max; paired values are median within-block changes. Copy GB includes ordinary completed oracle payload or native published payload plus mandatory 17,305,600-byte restoration for active oracle modes. Sampled D2H identity reads and metadata are separate traffic charged in wall. Oracle planner includes selection/enumeration/publication; current oracle-hook is only a tiny hook, not full native planning.

| Task | Actual input | Emitted output | Verify windows | End committed context position | Tape MB | Configured limit |
|---|---|---|---|---|---|---|
| code-archive | 6983 | 2048 | 769 | 9033 | 315.11 | 32768 |
| math-inventory | 165 | 2048 | 766 | 2213 | 313.85 | 32768 |
| text-websocket | 30383 | 1773 | 636 | 32157 | 260.74 | 32768 |
| mixed-chinook | 1899 | 2048 | 548 | 3948 | 224.59 | 32768 |
| text-json-rfc8259 | 2699 | 2816 | 949 | 5515 | 388.80 | 32768 |

| Task/profile | Mode | Valid/attempts | Replay tok/s min/median/max | Paired TG change | Paired completion-wall change | Full-gain retention | Local % | CPU/mapped entries | Copy GB | Evicted-before-first-use GB | No-use-yet censored GB | Reload/victim absence | Oracle hook/planner / score ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| code-archive/32K input6983 | ORACLE_FULL | 3/3 | 115.56/115.68/117.99 | 10.09% | -7.55% | 1.00/1.00/1.00 | 99.86 | 1533/152 | 63.062 | 0.027648 | 0.006144 | 11005/858 | 1937.56/0.00 |
| code-archive/32K input6983 | ORACLE_IN_HISTORY_TC | 3/3 | 103.12/105.86/110.51 | 0.75% | -1.25% | -0.03/0.08/0.55 | 96.71 | 36894/3052 | 30.584 | 0.003072 | 0.000000 | 4356/15382 | 1415.05/94.62 |
| code-archive/32K input6983 | ORACLE_IN_LOGISTIC_TC | 3/3 | 97.98/100.50/105.39 | -2.88% | 3.52% | -0.79/-0.24/0.04 | 96.64 | 37525/3320 | 29.209 | 0.000000 | 0.000000 | 3991/15587 | 1754.94/201.83 |
| code-archive/32K input6983 | REPLAY_CURRENT | 3/3 | 103.48/105.01/105.07 | 0.00% | 0.00% | 0.00/0.00/0.00 | 94.17 | 63663/7164 | 34.128 | 2.980352 | 1.890202 | 5125/30549 | 0.88/0.00 |
| math-inventory/32K input165 | ORACLE_FULL | 3/3 | 117.76/122.28/123.98 | 22.46% | -17.59% | 1.00/1.00/1.00 | 99.86 | 1515/202 | 64.017 | 0.003072 | 0.000000 | 11373/112 | 1776.06/0.00 |
| math-inventory/32K input165 | ORACLE_IN_HISTORY_TC | 3/3 | 100.97/107.91/115.15 | 6.59% | -6.52% | 0.15/0.34/0.76 | 96.69 | 38167/2803 | 33.611 | 0.000000 | 0.000000 | 5034/18092 | 1564.92/101.87 |
| math-inventory/32K input165 | ORACLE_IN_LOGISTIC_TC | 3/3 | 105.83/106.09/114.81 | 9.27% | -8.74% | 0.41/0.42/0.64 | 96.65 | 38654/2871 | 32.265 | 0.000000 | 0.000000 | 4669/18174 | 1757.34/208.81 |
| math-inventory/32K input165 | REPLAY_CURRENT | 3/3 | 97.08/98.47/101.24 | 0.00% | 0.00% | 0.00/0.00/0.00 | 93.70 | 69946/8034 | 36.374 | 3.207680 | 1.150054 | 5624/33640 | 0.98/0.00 |
| mixed-chinook/32K input1899 | ORACLE_FULL | 3/3 | 121.58/129.96/132.43 | 19.79% | -12.09% | 1.00/1.00/1.00 | 98.83 | 10282/1777 | 93.300 | 0.061952 | 0.012288 | 19163/4315 | 2793.16/0.00 |
| mixed-chinook/32K input1899 | ORACLE_IN_HISTORY_TC | 3/3 | 116.24/116.78/125.43 | 8.34% | -6.10% | 0.30/0.68/0.82 | 94.49 | 50897/5755 | 38.166 | 0.000000 | 0.000000 | 5023/24634 | 1827.96/111.83 |
| mixed-chinook/32K input1899 | ORACLE_IN_LOGISTIC_TC | 3/3 | 122.93/127.88/130.50 | 15.67% | -10.08% | 0.72/0.82/1.53 | 94.50 | 50813/5689 | 36.725 | 0.000000 | 0.000000 | 4607/24200 | 1485.61/161.33 |
| mixed-chinook/32K input1899 | REPLAY_CURRENT | 3/3 | 107.80/107.80/110.56 | 0.00% | 0.00% | 0.00/0.00/0.00 | 89.25 | 93526/17007 | 35.650 | 2.733261 | 1.196646 | 4295/34473 | 0.65/0.00 |
| text-websocket/32K input30383 | ORACLE_FULL | 3/3 | 112.84/114.14/116.09 | 8.59% | -3.29% | 1.00/1.00/1.00 | 99.78 | 2119/187 | 58.326 | 0.021504 | 0.000000 | 9947/929 | 1964.30/0.00 |
| text-websocket/32K input30383 | ORACLE_IN_HISTORY_TC | 3/3 | 96.93/102.86/110.17 | -3.78% | 3.32% | -1.89/-0.50/0.66 | 96.75 | 31923/2341 | 30.336 | 0.000000 | 0.000000 | 4560/13434 | 1491.07/99.30 |
| text-websocket/32K input30383 | ORACLE_IN_LOGISTIC_TC | 3/3 | 97.79/102.90/111.17 | -0.29% | 0.67% | -1.71/-0.03/0.49 | 96.72 | 32166/2413 | 29.429 | 0.000000 | 0.000000 | 4334/13413 | 1640.98/201.39 |
| text-websocket/32K input30383 | REPLAY_CURRENT | 3/3 | 103.19/106.77/106.90 | 0.00% | 0.00% | 0.00/0.00/0.00 | 93.66 | 60227/6574 | 32.619 | 3.068621 | 1.933824 | 5033/30092 | 0.68/0.00 |

Criterion frozen before live results: median paired decode-time reduction >3%, faster in at least 2/3 blocks, median completion wall regression <=1%, and no >3% wall regression in two blocks. Aiding practical threshold, not significance. Retention=(Tcurrent−Tcandidate)/(Tcurrent−Tfull); undefined if full saving is nonpositive, unstable below 1% current decode time, never clamped. Full oracle is feasible, not an optimal upper bound.

| Task | Mode | Decode gain blocks | Wall gain blocks | TG min/median/max % | Wall min/median/max % | Criterion met |
|---|---|---|---|---|---|---|
| code-archive | ORACLE_IN_HISTORY_TC | 2 | 2 | -0.35/0.75/5.24 | -2.79/-1.25/1.14 | False |
| code-archive | ORACLE_IN_LOGISTIC_TC | 1 | 1 | -6.75/-2.88/0.36 | -0.10/3.52/4.24 | False |
| math-inventory | ORACLE_IN_HISTORY_TC | 3 | 3 | 2.54/6.59/18.62 | -15.17/-6.52/-0.94 | True |
| math-inventory | ORACLE_IN_LOGISTIC_TC | 3 | 3 | 7.48/9.27/13.41 | -10.33/-8.74/-5.06 | True |
| mixed-chinook | ORACLE_IN_HISTORY_TC | 3 | 3 | 5.14/8.34/16.35 | -11.99/-6.10/-2.69 | True |
| mixed-chinook | ORACLE_IN_LOGISTIC_TC | 3 | 3 | 14.03/15.67/21.06 | -13.85/-10.08/-9.58 | True |
| text-websocket | ORACLE_IN_HISTORY_TC | 1 | 1 | -9.22/-3.78/6.76 | -1.81/3.32/5.22 | False |
| text-websocket | ORACLE_IN_LOGISTIC_TC | 1 | 1 | -8.41/-0.29/4.00 | -1.56/0.67/3.71 | False |

## Reconciled transaction outcomes

Each request conserves exact ordinary completed bytes before aggregation. Used is an observed main routed service in this admission generation; MTP work remains separately accounted; a batch with multiple expert lanes counts once for distinct reuse. Native withdrawal is at copy issue, publication certifies completion, and native target identity is unavailable. Restoration and readback do not enter these partitions. End survivors, including native copies published after last routed service, are censored.

| Mode | Terminal outcome | Transactions | Exact bytes (sum of runs) |
|---|---|---|---|
| REPLAY_CURRENT | completed_unpublished | 0 | 0 |
| REPLAY_CURRENT | published_used_before_eviction | 115122 | 361826918400 |
| REPLAY_CURRENT | published_evicted_without_use | 11439 | 35969740800 |
| REPLAY_CURRENT | published_no_use_resident_at_end | 5919 | 18512179200 |
| ORACLE_FULL | completed_unpublished | 0 | 0 |
| ORACLE_FULL | published_used_before_eviction | 263716 | 831355187200 |
| ORACLE_FULL | published_evicted_without_use | 136 | 419328000 |
| ORACLE_FULL | published_no_use_resident_at_end | 19 | 58368000 |
| ORACLE_IN_HISTORY_TC | completed_unpublished | 0 | 0 |
| ORACLE_IN_HISTORY_TC | published_used_before_eviction | 126496 | 397728153600 |
| ORACLE_IN_HISTORY_TC | published_evicted_without_use | 3 | 9216000 |
| ORACLE_IN_HISTORY_TC | published_no_use_resident_at_end | 0 | 0 |
| ORACLE_IN_LOGISTIC_TC | completed_unpublished | 0 | 0 |
| ORACLE_IN_LOGISTIC_TC | published_used_before_eviction | 122151 | 382819020800 |
| ORACLE_IN_LOGISTIC_TC | published_evicted_without_use | 1 | 3072000 |
| ORACLE_IN_LOGISTIC_TC | published_no_use_resident_at_end | 0 | 0 |

Original Phase1 accounting and explanation status are in [diagnosis](results/diagnosis.md) and exact [per-run reconciliation](results/phase1-transaction-reconciliation.json). Learned original total:740,876,492,800 completed bytes,367,455,641,600 unused;367,449,497,600 evicted before target,6,144,000 late-unused. No unpublished, duplicate-retired, target-mismatch or end-censored learned unused bytes. Full original has122,880,000 unused end-survivor bytes; finite observation is not proof they never return.

## Direct history versus logistic

Both share incoming order/E64, lifecycle, cost guard, physical queues and current-window privilege. Ratios below are within the same blocks.

| Task | Blocks | History TG versus logistic % | History wall versus logistic % | History decode wins | History nonlocal | Logistic nonlocal | History GB | Logistic GB |
|---|---|---|---|---|---|---|---|---|
| code-archive | 3 | 4.87 | -2.70 | 3 | 39962 | 40845 | 30.584 | 29.209 |
| math-inventory | 3 | -4.60 | 4.25 | 1 | 40958 | 41525 | 33.611 | 32.265 |
| text-websocket | 3 | -0.88 | 1.46 | 1 | 34264 | 34579 | 30.336 | 29.429 |
| mixed-chinook | 3 | -9.10 | 7.62 | 1 | 56652 | 56502 | 38.166 | 36.725 |
| text-json-rfc8259 | 2 | -2.68 | 3.27 | 1 | 50718 | 51378 | 35.980 | 34.330 |

Scorer rule was frozen before the main matrix: descriptive >3% median direct decode advantage and matching sign in at least 8/12 blocks. Otherwise no confirmed difference. This does not imply deployment if both lose to current. A mechanism or gain common to both is attributable to oracle incoming/common control; learning adds only the direct matched scorer difference.

## Same-binary development OFF/ON ablation

Two opposite-order logistic pairs on development math-rational; same incoming, guards and capacity. The earlier compiled ON smoke remains an unpaired third ON attempt. No fourth ON or main point was run.

| Block | OFF decode s | ON decode s | ON TG versus OFF % | ON wall versus OFF % | OFF/ON copy GB | OFF/ON unused GB |
|---|---|---|---|---|---|---|
| 1 | 19.5858 | 18.5566 | 5.55 | -2.26 | 69.97/36.53 | 33.93/0.00 |
| 2 | 20.6300 | 19.0850 | 8.10 | -4.94 | 67.04/36.61 | 31.28/0.00 |

## Offline competition and guard opportunity costs

Development/code-heg, math-rational, text-http, mixed-build; calibration/code-queue, math-sensor, text-tls, mixed-fields. Each unchanged deterministic point evaluated once. Inherited full/OFF accounting reproduced exactly on all eight compatible tapes. Fixed cadence0.57ms/invocation, MTP2.5ms/window, staging25GB/s, H2D13.2GB/s and publication45us remain assumptions, not modeled TG or exclusive CPU time.

| Calibration scorer | TC | Post-use invocations | Nonlocal entries | Completed GB | Unused GB | Victim absence | Cap refusals | Risk vetoes |
|---|---|---|---|---|---|---|---|---|
| native | 0 | 0 | 165355 | 286.55 | 159.93 | 64944 | 0 | 0 |
| native | 1 | 0 | 163502 | 128.34 | 0.00 | 63755 | 26596 | 0 |
| native | 1 | 48 | 197939 | 116.71 | 0.00 | 68025 | 79912 | 0 |
| logistic | 0 | 0 | 167308 | 296.03 | 171.94 | 64544 | 0 | 0 |
| logistic | 1 | 0 | 164751 | 125.81 | 0.00 | 63375 | 26656 | 0 |
| logistic | 1 | 48 | 198532 | 114.37 | 0.00 | 66867 | 80593 | 0 |

Minimal treatment removed unused copies while preserving/improving nonlocal work for both scorers across all 8 development/calibration tasks. Post-use48 saved another roughly 9% transfer but raised calibration nonlocal demand about 21%; it was rejected before main outcomes. No further extension or joint-ranking intervention was selected. Risk thresholds 0.2/0.5 had identical action hashes across all 8 calibration scorer points; risk vetoes 0. The binding controls were incoming copy-cost floor, p16-weighted victim-cost guard, current-window and lifecycle protection, and the class protection cap. Veto counters count scans/opportunities, not unique dropped computations. Required CPU/mapped work always remains.

| Request | Max protected/class | Mean total protected | Duration median/max invocations | Nonlocal entries while active class at cap |
|---|---|---|---|---|
| code-archive-block1-ORACLE_IN_HISTORY_TC | 16 | 13.06 | 60/64 | 1859 |
| code-archive-block1-ORACLE_IN_LOGISTIC_TC | 16 | 12.10 | 59/64 | 1479 |
| code-archive-block2-ORACLE_IN_HISTORY_TC | 16 | 12.95 | 60/64 | 1831 |
| code-archive-block2-ORACLE_IN_LOGISTIC_TC | 16 | 12.23 | 59/64 | 1586 |
| code-archive-block3-ORACLE_IN_HISTORY_TC | 16 | 12.98 | 60/64 | 1819 |
| code-archive-block3-ORACLE_IN_LOGISTIC_TC | 16 | 12.18 | 58/64 | 1585 |
| math-inventory-block1-ORACLE_IN_HISTORY_TC | 16 | 13.72 | 58/64 | 1881 |
| math-inventory-block1-ORACLE_IN_LOGISTIC_TC | 16 | 13.37 | 59/64 | 1956 |
| math-inventory-block2-ORACLE_IN_HISTORY_TC | 16 | 13.86 | 59/64 | 1987 |
| math-inventory-block2-ORACLE_IN_LOGISTIC_TC | 16 | 13.58 | 60/64 | 2275 |
| math-inventory-block3-ORACLE_IN_HISTORY_TC | 16 | 13.93 | 59/64 | 2214 |
| math-inventory-block3-ORACLE_IN_LOGISTIC_TC | 16 | 13.41 | 59/64 | 2042 |
| mixed-chinook-block1-ORACLE_IN_HISTORY_TC | 16 | 18.95 | 45/64 | 4371 |
| mixed-chinook-block1-ORACLE_IN_LOGISTIC_TC | 16 | 18.95 | 47/64 | 5043 |
| mixed-chinook-block2-ORACLE_IN_HISTORY_TC | 16 | 19.38 | 46/64 | 5015 |
| mixed-chinook-block2-ORACLE_IN_LOGISTIC_TC | 16 | 18.75 | 47/64 | 4758 |
| mixed-chinook-block3-ORACLE_IN_HISTORY_TC | 16 | 19.13 | 46/64 | 4600 |
| mixed-chinook-block3-ORACLE_IN_LOGISTIC_TC | 16 | 18.96 | 47/64 | 5021 |
| text-json-rfc8259-block1-ORACLE_IN_HISTORY_TC | 16 | 12.74 | 60/64 | 1998 |
| text-json-rfc8259-block1-ORACLE_IN_LOGISTIC_TC | 16 | 12.45 | 61/64 | 2241 |
| text-json-rfc8259-block2-ORACLE_IN_HISTORY_TC | 16 | 12.68 | 60/64 | 1896 |
| text-json-rfc8259-block2-ORACLE_IN_LOGISTIC_TC | 16 | 12.22 | 60/64 | 1970 |
| text-websocket-block1-ORACLE_IN_HISTORY_TC | 16 | 14.77 | 56/64 | 1686 |
| text-websocket-block1-ORACLE_IN_LOGISTIC_TC | 16 | 14.65 | 57/64 | 1868 |
| text-websocket-block2-ORACLE_IN_HISTORY_TC | 16 | 15.28 | 59/64 | 2039 |
| text-websocket-block2-ORACLE_IN_LOGISTIC_TC | 16 | 14.81 | 58/64 | 2128 |
| text-websocket-block3-ORACLE_IN_HISTORY_TC | 16 | 15.12 | 58/64 | 1913 |
| text-websocket-block3-ORACLE_IN_LOGISTIC_TC | 16 | 14.97 | 59/64 | 2266 |

Class-cap concurrent nonlocal work identifies competing service exposure. It does not identify exact preventable admissions: worker occupancy, E64 eligibility and cost guard also constrain copying. The post-use ablation directly demonstrates lost useful admissions. Exact counterfactual regret from minimal cap/protection is unmeasured; no claim that every refusal was beneficial.

## Planner, payload efficiency and resources

Feature/model are nested inside selection, and selection/enumeration/publication inside oracle planner. Enumeration includes scorer time. History updates are separately timed outside the oracle-hook planner but inside request execution. Host-plan interval is sum(plan_end−begin) from actual routed-layer journals and overlaps oracle planning, native per-layer bookkeeping and plan publication. Native adaptation selection outside that interval is unassigned. No timer sum is presented as exclusive exposed stall, and current hook is not a zero-cost planning baseline. No performance optimization was added beyond bounded lifecycle bookkeeping; no optimization-induced decision change is claimed.

| Task | Mode | Avoided entries/completed byte | Avoided entries/GB | Host plan interval ms | Oracle planner ms | Feature ms | Model ms | History ms |
|---|---|---|---|---|---|---|---|---|
| code-archive | ORACLE_IN_HISTORY_TC | 0.000001009 | 1009.1 | 1531.41 | 1415.05 | 227.84 | 94.62 | 93.32 |
| code-archive | ORACLE_IN_LOGISTIC_TC | 0.000001027 | 1027.1 | 1885.76 | 1754.94 | 245.23 | 201.83 | 100.88 |
| math-inventory | ORACLE_IN_HISTORY_TC | 0.000001102 | 1102.1 | 1689.47 | 1564.92 | 237.58 | 101.87 | 96.99 |
| math-inventory | ORACLE_IN_LOGISTIC_TC | 0.000001130 | 1130.5 | 1884.33 | 1757.34 | 252.68 | 208.81 | 103.06 |
| text-websocket | ORACLE_IN_HISTORY_TC | 0.000001073 | 1072.8 | 1601.72 | 1491.07 | 234.28 | 99.30 | 86.34 |
| text-websocket | ORACLE_IN_LOGISTIC_TC | 0.000001096 | 1095.6 | 1760.08 | 1640.98 | 248.75 | 201.39 | 86.99 |
| mixed-chinook | ORACLE_IN_HISTORY_TC | 0.000001412 | 1412.4 | 1955.24 | 1827.96 | 261.32 | 111.83 | 75.89 |
| mixed-chinook | ORACLE_IN_LOGISTIC_TC | 0.000001470 | 1469.8 | 1580.71 | 1485.61 | 197.53 | 161.33 | 65.84 |

Entries are lane computations, not unique experts or exact exclusive latency. Native request wall includes native prefill, online planning/real transfers, state attestation, final commit/drain/restoration and output/tape flush. Startup/warmup/shutdown are retained separately. Telemetry contains CPU/steal, host RAM, swap snapshots and both GPUs VRAM/power/clocks/utilization; slow and high-steal observations are retained without adjustment. Large immutable backing is host RAM. Average GB/s does not prove peak PCIe saturation or headroom. DMA-only and precise exposed-wait attribution remain unknown.

| Mode (median of12 main runs) | Oracle planner ms | Selection ms (nested) | Enumeration ms (nested) | Feature ms (nested) | Model ms (nested) | Publication wait ms (nested) | Final drain ms | Restoration ms | Setup ms |
|---|---|---|---|---|---|---|---|---|---|
| REPLAY_CURRENT | 0.81 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 17.72 |
| ORACLE_FULL | 1959.48 | 0.00 | 918.93 | 0.00 | 0.00 | 823.13 | 0.00 | 1.42 | 15.60 |
| ORACLE_IN_HISTORY_TC | 1528.00 | 572.29 | 570.69 | 235.93 | 100.58 | 601.71 | 0.00 | 1.45 | 19.77 |
| ORACLE_IN_LOGISTIC_TC | 1683.25 | 723.90 | 721.52 | 238.18 | 193.39 | 585.77 | 0.00 | 1.47 | 15.86 |

| Mode (scan-count sums) | Copy-cost veto | Victim-cost veto | Risk veto | Lease victim veto | Class-cap refusal | Empty compatible selection | Expiry | Late abort | Published by target | Published late |
|---|---|---|---|---|---|---|---|---|---|---|
| ORACLE_IN_HISTORY_TC | 20969693 | 0 | 0 | 116771 | 56897 | 0 | 176 | 0 | 126195 | 304 |
| ORACLE_IN_LOGISTIC_TC | 21448921 | 149880 | 0 | 162846 | 57674 | 0 | 117 | 0 | 121935 | 217 |

Ready publication is not identical to actual target service. Generation-level target service and later repeated use are retained per request. Publication wait is a host coordination interval overlapping device work; it is not an exact exclusively exposed GPU stall. No nested timer columns are summed.

| Mode (12 main runs) | Startup median s | Warmup median s | Shutdown median s | Observed steal median % | Host peak RSS GiB | GPU0 peak MiB | GPU1 peak MiB |
|---|---|---|---|---|---|---|---|
| REPLAY_CURRENT | 76.10 | 7.51 | 4.86 | 4.30 | 76.56 | 23836.00 | 24028.00 |
| ORACLE_FULL | 69.09 | 7.60 | 4.51 | 0.40 | 76.58 | 23836.00 | 24028.00 |
| ORACLE_IN_HISTORY_TC | 67.09 | 7.63 | 4.90 | 2.02 | 76.58 | 23836.00 | 24028.00 |
| ORACLE_IN_LOGISTIC_TC | 69.58 | 7.59 | 4.66 | 1.95 | 76.58 | 23836.00 | 24028.00 |

Per-request CPU, both GPU power/clocks/utilization/PCIe state, system RAM and swap snapshots are retained in [resource summary](results/resource-and-stage-summary.json) and [CSV](results/resources.csv). Main swap total is 0 bytes. Steal is observed and not corrected away.

## Independent source and observed guard tail

Source/protocol were frozen before policy-result inspection: public RFC8259 sections2–9, ordinary parser/serializer audit, no answer material or tools. Capture native greedy, same continuous request,2699 actual input,2816 emitted output,2048 main prefix and768 observed tail. End committed context position5515 (initial progress figure5516 double-counted overlapping last prompt input and was corrected). Configured32768; no extension of near-full old tapes. All four arms execute full tape.

| Mode | Main observation-span s | Main tok/s | Whole native decode s | Whole tok/s | Completion wall s | Prefix unused survivors MB | Later tail-used MB | Still no observed tail use MB |
|---|---|---|---|---|---|---|---|---|
| ORACLE_FULL | 16.5025 | 124.10 | 22.0514 | 127.70 | 28.6967 | 84.99 | 84.99 | 0.00 |
| ORACLE_IN_HISTORY_TC | 19.3157 | 106.03 | 25.7039 | 109.56 | 32.7423 | 31.23 | 31.23 | 0.00 |
| ORACLE_IN_LOGISTIC_TC | 17.0119 | 120.39 | 22.6498 | 124.33 | 29.3540 | 27.65 | 27.65 | 0.00 |
| REPLAY_CURRENT | 19.0140 | 107.71 | 24.9545 | 112.85 | 31.8020 | 1383.73 | 865.18 | 518.55 |
| ORACLE_FULL | 16.8107 | 121.83 | 22.5461 | 124.90 | 29.3570 | 75.78 | 75.78 | 0.00 |
| ORACLE_IN_HISTORY_TC | 18.2486 | 112.23 | 24.5299 | 114.80 | 31.5237 | 31.23 | 31.23 | 0.00 |
| ORACLE_IN_LOGISTIC_TC | 19.6613 | 104.16 | 26.1292 | 107.77 | 33.1869 | 27.65 | 27.65 | 0.00 |
| REPLAY_CURRENT | 19.2004 | 106.66 | 25.4427 | 110.68 | 32.4148 | 1383.73 | 865.18 | 518.55 |

All prefix-unused oracle survivors were subsequently used in the observed tail: history31.232MB/block and logistic27.648MB/block; full75.776–84.992MB/block. Native current had1,383.7312MB of prefix-unused survivors per block, of which865.1776MB had observed tail use and518.5536MB did not. This directly demonstrates why prefix no-use is not automatically waste. Both transfer candidates won one whole-decode block and lost one; there is no consistent independent latency gain.

The prefix timer spans first tape observation begin through last main observation end; its boundary differs from native whole-decode timer. Full whole-run copies, tail, drain and restoration are charged in whole wall. Tail-use linkage follows the same admission generation and slot. Native prefix ownership is evaluated at the actual prefix observation-end timestamp, including any final-layer publication after plan construction. Two independent blocks are descriptive transfer evidence, not consistency/generalization proof; an observed finite tail is not infinite future.

## Safety, reproducibility and limitations

First compiled scorer/lifecycle/copy replay smoke preceded larger offline competition and main matrix. Real-copy fixture passed all active classes/devices and canonical RAM byte readbacks. Tests cover zero-copy cost rejection, first actual use, multiple lanes, same-event release/ownership invalidation, all-protected NO_SWAP, expiry, repeated generation/spare reuse, delayed/late copy, publication recheck, duplicate in-flight, cancellation/drain/restoration, next request and shutdown. Frozen logistic parity 4000 predictions maximum error1.32e−7; prefix parity 300 batches maximum error1.18e−7. Full-reference decision-equivalence 610 comparisons and role/suffix invariance passed. Nine relevant native tests passed, including QSA active width and expert/kernel/route/KV checks. Full unrelated test suite not rerun. Real main inventory short-input and WebSocket EOS replay fidelity validated.

Retained failure: information fixture first invocation lacked mandatory tape environment; corrected invocation passed without source/binary change. Initial build heartbeat helper had an ETA argument collision; monitoring repaired and original build evidence retained. No scientific measurement was replaced. A script syntax failure before offline evaluation was corrected without discarding a result. Small occupancy metadata correction did not change tape or policy. Detailed [completion audit](completion-audit.json) states actual missing attribution/recovery checks; it is not blanket PASS.

A repaired diagnostic assumption separated first-use release from expiry: unused intent can expire, and the resident can be served later while unprotected. Runtime decision and safety behavior did not change. The original assertion failure is retained in the analysis log.

See [exact reproduction](reproduce.md), [identities](configs/runtime-identity.json), [frozen selection](models/selection.json), [Phase2 patch](patches/phase2.diff), [attempt ledger](attempt-ledger.jsonl), [storage/recovery manifest](artifact-manifest.json) and [progress](STATUS.md). Raw tapes and journals remain external/local; compact outcomes and all authored scripts are in Git. Their recovery/backup limits are explicit. The local commit is not pushed under this goal; no off-host copy of the new campaign record is established. No automatic update/rebuild from live launchers. Original weights, serving binary/launchers and prior campaigns are verified intact.

## Decision and strongest next experiment

Original learned no-observed-use fraction was about49.6% of completed ordinary payload. New main history is0.002317% and logistic0.000802%; neither has any pre-target unused eviction. Remaining unused copies are late/expired outcomes, not a guarantee that protection eliminates every unsuccessful admission.

The treatment establishes useful residency and removes the original pre-first-use churn mechanism. Main gains are judged only by the frozen taskwise paired criterion; any task-scoped result applies to those recorded tapes, not a Python-wide, agent-wide or production speedup. Frozen learning is judged against common-control history directly; common lifecycle gains are not learning gains.

The strongest next experiment is a bounded common planner-cost optimization: retain E64/candidate coverage and every ownership/history/protection invalidation, cache rejected incoming cost decisions only while their complete state remains valid, and measure plan-publication wait plus request time with decision/work parity. The million-scale repeated cost-veto scans and remaining measured planner work motivate it; their exclusive latency contribution still needs that discriminating test. Incoming prediction and production-causal operation remain separate future problems. This campaign does not begin Phase3.
## Required decision answers

| Question | Evidence-based answer |
|---|---|
| 1. Original no-use causes | 99.998328% pre-target re-eviction; 0.001672% late-published unused. Completed-unpublished, target mismatch, duplicate retired and end-surviving censoring account for zero original learned no-use bytes; restoration and readback are excluded. Late arrival and eviction are reason codes within the terminal partition, not additive overlapping outcomes. |
| 2. Cold re-eviction | The publication→no-use→pre-target eviction sequence is confirmed generation by generation. Historically cold ranking without admission state is a supported implementation explanation; no isolated feature intervention proves it is the only causal ranking component. |
| 3. Minimal protection | New causal arms completed 780,559,462,400 ordinary bytes, of which 12,288,000 had no observed use. First local service releases at the next safe routed milestone, or intent expires. Capacity/protection vetoes and concurrent nonlocal exposure are retained; exact preventable competing admissions remain unmeasured. |
| 4. Extension | Post-use48 decreased calibration transfer roughly 9% further but increased nonlocal work about 21%; rejected on development/calibration. No additional extension or joint-ranking change was bundled into the treatment. |
| 5. Binding guard | Copy-cost floor, victim-cost term, current-window protection and lifecycle cap bind. Risk0.2/0.5 changed no calibration action hashes and produced zero risk vetoes there. Live per-run counters report actual conditions, rather than treating unused threshold changes as improvements. |
| 6. Matched scorer | NO_CONFIRMED_SCORER_DIFFERENCE; median direct history/logistic decode-time ratio 0.99444. The frozen descriptive preference rule requires both magnitude and block consistency. |
| 7. Learning increment | Only same-block history/logistic differences can be assigned to scorer choice. The original churn repair and oracle incoming are common. No confirmed incremental learned benefit is claimed when the direct frozen criterion fails. |
| 8. Payload efficiency | Per-task avoided CPU/mapped entries per ordinary completed byte are tabulated above against the current arm in each block. They are lane computations per byte, not measured exclusive latency. |
| 9. Planner attribution | Feature/model nest in selection and enumeration, which nest in planner; history is separate. Host plan intervals overlap oracle work. Native adaptation outside these intervals and exact exposed stall are unassigned. No unrelated performance optimization was introduced. |
| 10. Live timing | Frozen taskwise gain criterion met on: math-inventory, mixed-chinook. Full-reference retention, block signs, decode and completion wall are retained without clamping. Each task has its actual tape denominator. |
| 11. Independent tail | Two complete four-arm RFC8259 blocks execute2699 input/2816 output, with2048 main and768 continuous observed tail. Prefix survivors and subsequent generation-specific tail use are tabulated; this small finite check cannot establish generalization or infinite-future absence. |
| 12. Next experiment | Common planner cost-decision caching with full state invalidation and decision/work parity; measure exposed plan/publication waits and completion time. Repeated rejection scans motivate this specific test, without claiming all planner time is exposed or assuming PCIe saturation. |
