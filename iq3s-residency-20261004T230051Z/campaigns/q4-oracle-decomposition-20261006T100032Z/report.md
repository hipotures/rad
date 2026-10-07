# Q4 oracle decomposition: incoming demand versus victim lifetime

**Victim information dominates the loss in the tested first-feasible scheduler.** Full future improves all nine main matched decode pairs; restricting victim lifetime loses the gain, while the incoming retention utility is structurally inactive in this policy. This does not establish a universal information requirement.

The unchanged Q4/K24/PCIe0.28/pool100us normal serving baseline remains real-use configuration. This study is clairvoyant fixed-work replay, not a deployable generation speed or quality claim.

## Preserved work profiles

| Profile | Total context limit | Actual input | Recorded visible output | Verifier windows | Work SHA256 |
| --- | --- | --- | --- | --- | --- |
| 32k | 32768 | 28378 | 4096 | 1289 | 237ee8e7d981129238afaa1a754453d3ecee8087af0c9c1a3f2fc950f9b36fd9 |
| 128k | 131072 | 126715 | 4096 | 1533 | ba5432b95f973e50ad5cdb644e9667303231e3b46c551572face35b6c788fe7f |
| 256k | 262144 | 257781 | 4096 | 1628 | 4046f4345f2cf4344bc6c6d2fc066c8cb646e55821de72607161c1cacab666ab |

The same fixed tape is repeated three times per profile for timing repeatability. These are not three independent tasks. Required reserve remains inside each total-context limit.

## Main measured results

| Profile/tape | E | I | V | Attempts/valid | Replay decode s | Replay-equivalent tok/s | Paired TG change vs current % | Full-gain retention | Wall s | Copy GB | CPU/mapped entries | Victim-absent entries | Late target nonlocal demand | Online oracle planner ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 32k/current | n/a | n/a | n/a | 3/3 | 39.25 | 104.36 | 0.00 | 0.00 | 57.87 | 87.42 | 196,292/31,135 | 151,049 | unknown | n/a |
| 32k/FF | 64 | full | full | 3/3 | 34.08 | 120.19 | 15.17 | 1.00 | 52.56 | 204.67 | 13,190/1,821 | 11,736 | 59 | 5,307.31 |
| 32k/64F | 64 | 64 | full | 3/3 | 35.32 | 115.97 | 11.12 | 0.76 | 54.07 | 197.90 | 18,767/2,555 | 15,886 | 177 | 6,016.58 |
| 32k/F64 | 64 | full | 64 | 3/3 | 43.70 | 93.74 | -10.81 | -1.12 | 62.17 | 313.00 | 87,944/15,557 | 86,179 | 120 | 8,593.29 |
| 32k/6464 | 64 | 64 | 64 | 3/3 | 44.60 | 91.83 | -8.97 | -0.75 | 63.00 | 311.57 | 89,816/15,909 | 87,241 | 339 | 9,258.38 |
| 128k/current | n/a | n/a | n/a | 3/3 | 47.07 | 87.01 | 0.00 | 0.00 | 121.59 | 99.37 | 231,342/36,617 | 185,345 | unknown | n/a |
| 128k/FF | 64 | full | full | 3/3 | 42.21 | 97.04 | 11.24 | 1.00 | 113.68 | 202.05 | 19,771/2,900 | 19,736 | 156 | 6,808.04 |
| 128k/F256 | 64 | full | 256 | 3/3 | 50.60 | 80.94 | -7.37 | -0.80 | 125.64 | 320.74 | 85,820/15,522 | 85,759 | 317 | 9,645.44 |
| 256k/current | n/a | n/a | n/a | 3/3 | 51.32 | 79.81 | 0.00 | 0.00 | 193.90 | 96.48 | 213,972/32,924 | 168,745 | unknown | n/a |
| 256k/FF | 64 | full | full | 3/3 | 45.60 | 89.83 | 12.56 | 1.00 | 185.90 | 205.39 | 20,179/2,859 | 17,639 | 215 | 7,032.80 |
| 256k/F256 | 64 | full | 256 | 3/3 | 56.07 | 73.05 | -10.23 | -1.13 | 192.62 | 316.74 | 83,742/14,927 | 83,093 | 410 | 11,274.78 |

Medians use three valid attempts per point; all individual min/median/max and within-block ratios are in summary.json/CSV and analysis/paired-comparisons.json. Gain retention is (T_current-T_candidate)/(T_current-T_full), computed within block and not clamped. Negligible/nonpositive full savings are undefined. Copy GB includes native or oracle completed weight payload plus mandatory17,305,600-byte oracle restoration; metadata traffic is separate. Publication-before-target is not actual target-ready demand. Late target nonlocal demand requires observed CPU/mapped service at the intended target while the copy was unfinished. Victim absence is reconstructed for both authorities: native eviction starts at copy issue, oracle eviction at completed-copy publication; readmission ends absence. Native planning time is not represented by the tiny oracle-hook timer in REPLAY_CURRENT, so that table entry is n/a. Planner includes overlapping host query/publication activity and cannot be added to GPU/CPU timers.

## Full timing range

| Profile | Arm | Metric | Min | Median | Max |
| --- | --- | --- | --- | --- | --- |
| 32k | current | decode_s | 38.97 | 39.25 | 41.10 |
| 32k | current | replay_equivalent_tok_s | 99.67 | 104.36 | 105.10 |
| 32k | current | PP | 1,529.10 | 1,574.90 | 1,576.50 |
| 32k | current | wall_s | 57.71 | 57.87 | 60.32 |
| 32k | current | TTFT_s | 18.60 | 18.69 | 19.19 |
| 32k | current | attestation_ms | 510.75 | 522.42 | 545.29 |
| 32k | current | CPU_steal | 4.49 | 6.72 | 10.00 |
| 32k | FF | decode_s | 33.45 | 34.08 | 34.76 |
| 32k | FF | replay_equivalent_tok_s | 117.83 | 120.19 | 122.44 |
| 32k | FF | PP | 1,579.90 | 1,596.40 | 1,603.50 |
| 32k | FF | wall_s | 51.80 | 52.56 | 53.35 |
| 32k | FF | TTFT_s | 18.31 | 18.46 | 18.56 |
| 32k | FF | attestation_ms | 510.49 | 522.80 | 538.83 |
| 32k | FF | CPU_steal | 0.69 | 1.13 | 1.67 |
| 32k | 64F | decode_s | 33.91 | 35.32 | 40.05 |
| 32k | 64F | replay_equivalent_tok_s | 102.26 | 115.97 | 120.80 |
| 32k | 64F | PP | 1,550.30 | 1,550.40 | 1,567.30 |
| 32k | 64F | wall_s | 52.84 | 54.07 | 59.38 |
| 32k | 64F | TTFT_s | 18.73 | 18.91 | 18.94 |
| 32k | 64F | attestation_ms | 520.59 | 524.66 | 525.06 |
| 32k | 64F | CPU_steal | 1.78 | 1.96 | 2.31 |
| 32k | F64 | decode_s | 42.97 | 43.70 | 45.02 |
| 32k | F64 | replay_equivalent_tok_s | 90.98 | 93.74 | 95.33 |
| 32k | F64 | PP | 1,577.50 | 1,578.90 | 1,589.40 |
| 32k | F64 | wall_s | 61.57 | 62.17 | 63.63 |
| 32k | F64 | TTFT_s | 18.46 | 18.58 | 18.59 |
| 32k | F64 | attestation_ms | 513.17 | 514.42 | 516.64 |
| 32k | F64 | CPU_steal | 3.45 | 3.67 | 3.68 |
| 32k | 6464 | decode_s | 43.12 | 44.60 | 46.41 |
| 32k | 6464 | replay_equivalent_tok_s | 88.25 | 91.83 | 95.00 |
| 32k | 6464 | PP | 1,579.00 | 1,592.20 | 1,599.90 |
| 32k | 6464 | wall_s | 61.78 | 63.00 | 64.92 |
| 32k | 6464 | TTFT_s | 18.37 | 18.47 | 18.66 |
| 32k | 6464 | attestation_ms | 531.18 | 543.86 | 594.71 |
| 32k | 6464 | CPU_steal | 1.93 | 3.90 | 4.08 |
| 128k | current | decode_s | 46.87 | 47.07 | 48.71 |
| 128k | current | replay_equivalent_tok_s | 84.10 | 87.01 | 87.39 |
| 128k | current | PP | 1,696.60 | 1,754.70 | 1,819.80 |
| 128k | current | wall_s | 119.11 | 121.59 | 125.36 |
| 128k | current | TTFT_s | 72.00 | 74.69 | 76.63 |
| 128k | current | attestation_ms | 1,652.20 | 1,862.18 | 2,069.08 |
| 128k | current | CPU_steal | 3.51 | 3.55 | 7.23 |
| 128k | FF | decode_s | 40.46 | 42.21 | 42.32 |
| 128k | FF | replay_equivalent_tok_s | 96.79 | 97.04 | 101.23 |
| 128k | FF | PP | 1,821.30 | 1,825.80 | 1,827.30 |
| 128k | FF | wall_s | 112.43 | 113.68 | 114.24 |
| 128k | FF | TTFT_s | 71.42 | 71.44 | 71.69 |
| 128k | FF | attestation_ms | 1,757.60 | 1,816.17 | 1,849.34 |
| 128k | FF | CPU_steal | 1.27 | 1.41 | 2.03 |
| 128k | F256 | decode_s | 49.11 | 50.60 | 52.17 |
| 128k | F256 | replay_equivalent_tok_s | 78.51 | 80.94 | 83.40 |
| 128k | F256 | PP | 1,745.40 | 1,756.40 | 1,816.50 |
| 128k | F256 | wall_s | 121.05 | 125.64 | 126.32 |
| 128k | F256 | TTFT_s | 71.84 | 74.12 | 75.00 |
| 128k | F256 | attestation_ms | 1,687.21 | 1,814.18 | 1,871.84 |
| 128k | F256 | CPU_steal | 2.25 | 2.99 | 3.90 |
| 256k | current | decode_s | 50.33 | 51.32 | 51.33 |
| 256k | current | replay_equivalent_tok_s | 79.80 | 79.81 | 81.38 |
| 256k | current | PP | 1,851.50 | 1,859.10 | 1,942.50 |
| 256k | current | wall_s | 188.20 | 193.90 | 194.31 |
| 256k | current | TTFT_s | 136.81 | 142.94 | 143.45 |
| 256k | current | attestation_ms | 3,533.45 | 3,620.28 | 3,685.80 |
| 256k | current | CPU_steal | 7.74 | 8.56 | 10.21 |
| 256k | FF | decode_s | 44.71 | 45.60 | 47.55 |
| 256k | FF | replay_equivalent_tok_s | 86.14 | 89.83 | 91.62 |
| 256k | FF | PP | 1,847.00 | 1,900.60 | 2,002.70 |
| 256k | FF | wall_s | 181.82 | 185.90 | 189.21 |
| 256k | FF | TTFT_s | 134.14 | 140.24 | 144.39 |
| 256k | FF | attestation_ms | 4,084.80 | 4,259.13 | 4,846.76 |
| 256k | FF | CPU_steal | 1.31 | 1.63 | 1.91 |
| 256k | F256 | decode_s | 52.14 | 56.07 | 57.77 |
| 256k | F256 | replay_equivalent_tok_s | 70.91 | 73.05 | 78.55 |
| 256k | F256 | PP | 1,901.90 | 1,939.30 | 2,057.90 |
| 256k | F256 | wall_s | 187.42 | 192.62 | 193.84 |
| 256k | F256 | TTFT_s | 129.59 | 137.75 | 140.45 |
| 256k | F256 | attestation_ms | 3,543.39 | 4,266.88 | 4,384.65 |
| 256k | F256 | CPU_steal | 2.59 | 3.71 | 3.77 |

## Information boundaries and structural finding

E64 is the unchanged incoming issue frontier. At logical event n, bounded information ends at n+H inclusive. First incoming relevant demand is eligible only within min(E,I); incoming count/value reads at most I, resident next-use/count/initial donor/publication selection at most V. FULL stops at finite tape end. One unit is the whole main verify routed-layer T-by-10 invocation;48/window. Role/window/position/speculative lanes/batch shapes remain in the tape identity. No batch is serialized into individual expert demand.

Typed IncomingFutureView/VictimFutureView and query counters enforce separate views. Unknown beyond H is distinct from finite tape end and uses fixed causal heat-log fallback. No full-future cached scores or tie-breaking cross roles. Candidate enumeration reads only min(E,I). Common P=current-window safety protection reveals up to47 forward layer invocations and is explicitly retained in every arm. Therefore H4/H16 offline curves are conditional on P; H64 contains all forward P information. Full-index preparation in RAM is evaluator setup, not permission for policy leakage.

The default deadline scheduler **selects its first feasible candidate**. Its calculated incoming/victim reuse utility never ranks two feasible choices. I>=64 therefore leaves deterministic actions unchanged when V is fixed; it can reduce online count-loop work and change physical asynchronous progress. A null I64 effect does not show that incoming retention information is unnecessary in a future utility-ranking scheduler. The unchanged internal reuse-count cap is n+768 even for FULL; FULL victim next-use can inspect the remaining finite tape.

Source tests:1,205 old/new full decision checks, exact deterministic offline F/F=64/F, bounded suffix tests for incoming and victim decisions separately, role reclassification, inclusive endpoint/H+1 unknown, causal fallback branch activation. Full mode/default ordinary/current behavior is preserved; the common v2 diff changes only oracle information headers. See phase-a/.

## Sparse offline curves — not measured model throughput

| I | V | Nonlocal entries | CPU/mapped | Copies GB | Published | Target-ready entries | Victim absent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full | full | 2579 | 2262/317 | 217.44 | 69163 | 77788 | 2150 |
| 4 | full | 55985 | 50547/5438 | 150.01 | 47809 | 55809 | 41755 |
| 16 | full | 16248 | 14449/1799 | 200.07 | 63544 | 71863 | 12710 |
| 64 | full | 2579 | 2262/317 | 217.44 | 69163 | 77788 | 2150 |
| 256 | full | 2579 | 2262/317 | 217.44 | 69163 | 77788 | 2150 |
| full | 4 | 109298 | 93267/16031 | 655.30 | 197394 | 109627 | 92565 |
| full | 16 | 89940 | 76525/13415 | 653.47 | 196883 | 123126 | 77022 |
| full | 64 | 61127 | 51699/9428 | 383.14 | 121063 | 138908 | 53693 |
| full | 256 | 48656 | 41313/7343 | 367.44 | 116371 | 133105 | 42931 |
| 64 | 64 | 61127 | 51699/9428 | 383.14 | 121063 | 138908 | 53693 |

One deterministic execution per unchanged point; no25-cell grid. All3classes/48layers/same5chargedspares, E64, one modeled contended link/device. Inherited staging25GB/s, H2D13.2GB/s, publication45us, main0.57ms/invocation and MTP2.5ms/window are model assumptions. No exposed CPU/mapped latency model or simulated TG is fabricated. I4/I16 also shorten eligibility/lead.

One causal unknown repair H+640/(1+heat), derived from native .7/4-window EMA, was tested without tuning. It makes different choices in a targeted binding state but produces exactly unchanged32K modeled exchange traffic/demand. This negative is preserved; no live repair or additional fallback search. Churn cannot be blamed only on an infinity sentinel: bounded unknowns use causal heat, though that fallback remains an imperfect eviction-risk model.

## Matched interaction and gain retention

| 32K block | Descriptive interaction ms |
| --- | --- |
| 1 | 1,181.40 |
| 2 | -3,150.20 |
| 3 | -2,575.20 |

Interaction = T_64_64-T_64_F-T_F_64+T_F_F. This is descriptive, sensitive to changed placement trajectories/VM variability. Do not add the two losses as a linear universal law. Mechanically, I64 has no deterministic selection effect at fixed V; any small measured interaction needs timing/planner interpretation.

## Context/task transfer

F/F median replay-equivalent rates are 120.19 / 97.04 / 89.83 tok/s at 32K / 128K / 256K, versus current 104.36 / 87.01 / 79.81. Median within-block TG ratios improve by 15.17% / 11.24% / 12.56%; these are medians of paired ratios, not ratios of medians. Request-wall ratios improve by 9.17% / 6.51% / 2.63% respectively. The frozen follow-up I=FULL/V=256 loses every larger-context decode pair: median TG changes -7.37% at128K and -10.23% at256K. Its tiny 256K wall improvement (0.42%) accompanies worse decode and varying prefill, so is not a practical scheduler win. On the previously observed independent archive task F/F improves all three pairs (median +16.37% TG); V256 retains 39.44% of full time saving at the median, with range -54.49% to63.35%. That task has different CPU/miss characteristics and sampled byte-check costs; it is not an untouched holdout or quality evaluation.

Previously observed independent Python zipfile/archive task, 6991 input and 1024 recorded output tokens, total context 32768. This is task transfer, not a new untouched holdout. Every arm enables the same sampled copied-weight readback setting; readbacks occur only where oracle copies are actually issued. Their cost remains in request/decode timing. Fixed forced output does not evaluate task quality.

| Arm | Attempts | Replay-equivalent tok/s median | Wall median s | Paired TG change vs current % | Full-gain retention |
| --- | --- | --- | --- | --- | --- |
| F256 | 3 | 105.03 | 19.36 | 5.12 | 0.39 |
| FF | 3 | 115.76 | 18.53 | 16.37 | 1.00 |
| current | 3 | 99.91 | 19.92 | 0.00 | 0.00 |

## Fidelity, physical costs and uncertainty

All headline requests must pass tape fingerprint, token/MTP branch/commit/rollback/catchup schedule, routed IDs/float32 coefficients/QSA/shape/dependency counts and strict initial meaningful-state sidecar. Real dense/attention/KV/PLE/router/expert/head work computes before tape overrides. Forced output/MTP parity is not correctness proof. Selected real activation samples remain numerical diagnostics; CPU/GPU quantization/summation differ. Publication/copy ownership safety is checked separately.

All48main layers/all3physical classes share K24 and originalVRAM envelope. Five existing slots become charged spares inside decode; no expert prepopulate/setup benefit or extra GPU memory. MTP residency stays unchanged. Current retains native adaptation; oracle is sole exchange authority in its scope, preserving causal heat. Real pinned staging/H2D completion precedes legal publication; late demand still computes using CPU/mapped fallback. Native decode time ends before final commit wait, drain/restoration and buffered trace flush, exactly as the retained v3 serving timer does. All request-comparable wall includes these costs; cleanup timers are shown separately and never added as unrelated medians. A decode-only gain is not automatically a cleanup-inclusive request gain. Future index and tape loaded in RAM outside decode, online queries/copies charged.

Short ordinary/replay guard: median paired decode overhead 5.61%, wall overhead 11.42%; individual decode ratios .889..1.162. No performance-equivalence claim or unvalidated natural speed extrapolation. Common initial-state attestation remains pre-decode setup inside requestwall.

| Profile | Arm | VM CPU% | Process CPU% (1core=100) | CPU steal% | GPU0% | GPU1% | Local all-demand% | Future index setup ms | Tape lookup ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 32k | current | 47.63 | 711.13 | 6.72 | 53.03 | 52.28 | 89.66 | 52.64 | 160.79 |
| 32k | FF | 16.18 | 232.60 | 1.13 | 58.12 | 63.26 | 99.32 | 32.89 | 151.31 |
| 32k | 64F | 19.29 | 263.85 | 1.96 | 57.68 | 60.53 | 99.03 | 29.49 | 181.76 |
| 32k | F64 | 30.98 | 458.48 | 3.67 | 62.44 | 65.07 | 95.30 | 31.07 | 147.02 |
| 32k | 6464 | 31.25 | 461.37 | 3.90 | 61.57 | 63.53 | 95.20 | 43.71 | 212.58 |
| 128k | current | 45.56 | 683.11 | 3.55 | 54.10 | 50.88 | 88.90 | 55.17 | 179.79 |
| 128k | FF | 17.37 | 246.97 | 1.41 | 58.00 | 59.79 | 99.06 | 37.19 | 189.32 |
| 128k | F256 | 28.15 | 410.49 | 2.99 | 62.02 | 61.48 | 95.80 | 42.26 | 203.02 |
| 256k | current | 43.99 | 632.86 | 8.56 | 51.81 | 51.48 | 90.09 | 41.59 | 219.71 |
| 256k | FF | 17.08 | 244.49 | 1.63 | 56.53 | 59.49 | 99.08 | 47.21 | 357.25 |
| 256k | F256 | 27.06 | 378.72 | 3.71 | 60.34 | 60.95 | 96.04 | 48.83 | 224.98 |

Tape and future-index payload accounting (outside timed decode):

| Profile | Tape MB | Future event/count pair payload MB |
| --- | --- | --- |
| 32k | 528.12 | 12.98 |
| 128k | 628.42 | 14.07 |
| 256k | 667.85 | 14.71 |

Future-index payload counts two int32 fields per distinct expert/invocation. This is a lower-bound logical payload, not measured allocator RSS: vector slack, allocator metadata and tape temporary copies are not included. Full index is constructed for both replay policies; its role-specific access is still bounded.

CPU steal/load/affinity, GPU clocks/power/temperature/link state, RAM/VRAM and attestation costs remain in raw telemetry and analysis/*-system.json. No clocks/global settings changed, no parallel heavy work during speed runs.3 repetitions do not remove VM confounding. Physical streamed KV refill ordering may differ despite identical logical QSA and initial maps; primary native counters retained, secondary DMA detail unavailable.1Hz aggregate PCIe samples cannot establish event-specific bandwidth or saturation. CPU/mapped counts are distinct and all-routed denominators match. Overlapping timers are not summed.

The native child main-thread affinity is not the affinity of every thread. A read-only snapshot retained56 thread masks:15 one-core masks for the CPU pool on cores1 through15,13 on core0, and28 permitting cores0 through15. Source creates oracle workers before the later main-session pin. Generic thread names do not identify every role; no oracle-worker/core attribution is invented and no affinity was changed.

## Admission lifetime, tail sensitivity and smallest sufficient budget

At32K the full policy has median 11,736 observed victim-absent entries, versus 86,179 with V64 and 151,049 under native current. Full copies 204.67GB, V64 313.00GB, current 87.42GB. Thus this feasible gain pays more transfer traffic than current; it is not a cheap static-cache result. V64 achieves a higher local share than current yet slower decode, with more churn and online planning/publication. At128K V256 causes median 85,759 victim-absent entries versus 19,736 for full. Its copies are roughly321GB versus202GB, and oracle-planner counters 9.65s versus6.81s. These overlapping costs support the mechanism but do not isolate a unique critical-path penalty. Incoming64 slow attempt3 is retained: staging median272.6us versus 139.3us for its paired full attempt, more late publication and victim absence, despite valid query limits/work/state. Copy-with-host-wait medians remain similar. Unique VM/scheduling causation is unresolved. Readiness, distinct persistent reuse, native/oracle reload recurrence, right-censored survivors and finite-end interior sensitivity are reported separately; routed-lane multiplicity is not durable reuse.

Incoming: I=64 is the smallest tested budget reproducing deterministic F/F decisions at unchanged E64 in the offline model and source tests. Its live median retention is75.96%, range -25.67% to94.05%, so an 80–90% performance-sufficiency claim is unresolved. I4/I16 shorten eligibility as well as value information and therefore do not isolate incoming lifetime. Victim: neither V64 at32K nor V256 in the larger profiles is sufficient under the tested policy/fallback. FULL is the only tested passing reference; the smallest sufficient finite V remains unmeasured. This is not proof that a causal predictor needs exact whole-request next-use, nor that every short-history victim policy fails. Interaction has signs +1181/-3150/-2575ms across blocks, not a stable linear law.

| Profile | Arm | Issued | Published | Repeat admissions | Published before target | Actual target hit entries | Reused admissions | Unused GB | Evicted without observed use | Unused end-censored |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 128k | F256 | 100,756 | 100,756 | 79,430 | 100,451 | 118,240 | 73,647 | 0.218 | 70 | 1 |
| 128k | FF | 63,973 | 63,973 | 43,858 | 63,824 | 73,004 | 48,773 | 0.111 | 29 | 2 |
| 128k | current | 31,627 | 31,627 | 16,790 | unknown | unknown | unknown | unknown | unknown | unknown |
| 256k | F256 | 99,225 | 99,225 | 78,321 | 98,798 | 115,474 | 70,435 | 0.319 | 100 | 4 |
| 256k | FF | 64,937 | 64,937 | 45,117 | 64,728 | 73,870 | 48,001 | 0.157 | 50 | 1 |
| 256k | current | 30,670 | 30,670 | 16,121 | unknown | unknown | unknown | unknown | unknown | unknown |
| 32k | 6464 | 97,761 | 97,761 | 77,272 | 97,430 | 112,621 | 67,933 | 0.301 | 94 | 8 |
| 32k | 64F | 62,798 | 62,798 | 43,007 | 62,622 | 70,678 | 46,117 | 0.132 | 41 | 3 |
| 32k | F64 | 98,224 | 98,224 | 77,694 | 98,096 | 113,420 | 68,272 | 0.114 | 35 | 3 |
| 32k | FF | 65,000 | 65,000 | 45,079 | 64,944 | 73,273 | 47,616 | 0.046 | 13 | 2 |
| 32k | current | 27,893 | 27,893 | 13,721 | unknown | unknown | unknown | unknown | unknown | unknown |

Medians of separate funnel counts are descriptive, not one synthetic conserved transaction. Target-hit counts retain lane multiplicity; published/reused counts are admission actions. Unused-at-end is censored, never a never-use label. Candidate enumeration/rejection counts are unavailable, not zero. Native current has no oracle target/reuse intent; those specific metrics are unknown.

Middle50% of verifier windows (floor(W/4) through floor(3W/4), exclusive) was declared before timing; per-row interior windows/time/logical committed advances and paired ratios retained in summary.json. No favorable interval selection or cleanup exclusion from total wall. No guard tail; full oracle has finite4096-end privilege. Resident lifetimes at end are censored, not deployment never-used labels. Victim-absent entries are observed demand while displaced, not exclusive causal latency penalties. Actual hit at target and published-before-target counts are separate.

## Next predictor/scheduler target

One next research target: calibrated **victim-return risk / eviction regret for a proposed same-layer, same-class, same-device exchange**, conditional on an already visible incoming E64 action. Estimate whether demand for the displaced resident will return before ready incoming reuse amortizes copy and planning cost. Use causal usage, heat, recency, age, reload history, class, queue and protection state; retain uncertainty when future use is censored. A later causal system must independently supply incoming predictions and replace privileged whole-current-window P with safe available dependency state. Do not train a generic expert-popularity model or assume exact distant next-use is required. First instrument/use an effective net exchange ranking or veto: the present computed reuse utility never compares two feasible actions.

See analysis/predictor-specification.md for candidate population, causal features, risk/lifetime target, horizon units, cost weighting and uncertainty behavior. No predictor was trained. Do not infer that exact distant next-use is the only deployable target.

## Repairs and negative results

Bootstrap tracked .venv symlink and ELF/log directory-name collision were repaired without model/runtime changes. A copied development-manifest output field inherited64 from warmup although the immutable request always specified256; metadata was corrected with no inference retry. A missing copied FNV helper caused post-request audit failure; valid inference was re-audited without a retry. Source information-v1 repairs the old incoming endpoint convention and finite-end state; v2 adds one opt-in causal unknown repair. Main heat-log policy and all physical worker/math paths unchanged. Losing sparse horizons/repair and slow observations remain retained. Any additional failures are listed in ledger.jsonl and final audit, never discarded post hoc. No new trace capture, helper/pool/K/PCIe/MTP/quantization tuning.

## Reproduce and real use

Normal Q4 serving remains **../q4-live-oracle-20261006T040656Z/launchers/control/**. No new normal launcher was created or existing one altered. Replay wrappers under launchers/replay/ are explicitly experimental; e.g. `./launchers/replay/64F-128k.sh --check` verifies identity/config/model/tape only; without `--check` creates a new finite owned manual reproduction namespace. Other retained budgets current/FF/64F/F64/6464/F256 and profiles32k/128k/256k are documented in launchers/README.md. Actual measured coverage is the table, not every possible wrapper combination. Source/binary hashes are checked; no automatic builds or hidden expert preloads.

Common source **bbfea2955ec238f7e6406b11c74e577c996c4a8d**, binary **9068a7205c14884f6436274627a3c6d78ab707894a21eeb9847a488367cbcfef**, original serving source/binary identities in git/prior-identities.json. Model revision38bb39ee97821de2c9009abb7e93950eec396e66, pack/shard/MTP/profile provenance and fresh aux hashes in git/model-now-verified.json. Previous campaign data/models remain immutable. All raw data/scripts/patches/manifests retained; local commits only, no push orPR. Deadline start09:57UTC, cutoff15:12UTC, absolute15:57UTC2026-10-06. Final process/GPU cleanup and reproducibility evidence in analysis/final-audit.json.

VICTIM_INFORMATION_DOMINATES
