# Q4 live oracle: fixed logical work and real transfers

Generated 2026-10-06T07:42:54.097848+00:00. All headline data are from the final v3 binary and fresh paired runs; earlier pilots are excluded.



**Research conclusion: FEASIBLE_LIVE_ORACLE_GAIN.** The unchanged Q4/100us serving baseline remains the real-use configuration. Clairvoyant replay is not a production replacement, newly generated text, or a model-quality result.



## Main controlled matrix

One saved tape per profile is repeated three times: timing repeatability, not three independent tasks. Both arms use the same experimental binary, recorded work, exact initial state, fixed warmup (4096 input / 64 output), and natural uncached prefill. Output normalization is 4096 visible recorded output IDs. Internal commit-position advances and end-window excess are retained and charged.



| Context | Tape input/output | Policy | Scope | Attempts/valid | Work hash match | Prefill s | Replay decode s | Replay-equivalent tok/s | Total wall s | Local % | CPU / mapped entries | Copy GB | Ready / late publications | Online planner ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 32k | 28378/4096 | REPLAY_CURRENT | 48 main layers / 3 classes | 3/3 | YES | 17.86 | 38.97 | 105.11 | 57.39 | 89.66 | 196,292 / 31,135 | 87.42 | 0 / 0 | 1.29 |
| 32k | 28378/4096 | REPLAY_ORACLE_FULL | 48 main layers / 3 classes | 3/3 | YES | 17.83 | 33.30 | 122.99 | 51.76 | 99.40 | 11,649 / 1,635 | 207.03 | 65,729 / 31 | 4,644.57 |
| 128k | 126715/4096 | REPLAY_CURRENT | 48 main layers / 3 classes | 3/3 | YES | 72.27 | 49.81 | 82.24 | 124.59 | 88.90 | 231,342 / 36,617 | 99.37 | 0 / 0 | 1.80 |
| 128k | 126715/4096 | REPLAY_ORACLE_FULL | 48 main layers / 3 classes | 3/3 | YES | 70.12 | 40.60 | 100.89 | 114.08 | 99.05 | 20,009 / 2,962 | 201.72 | 63,726 / 141 | 5,466.02 |
| 256k | 257781/4096 | REPLAY_CURRENT | 48 main layers / 3 classes | 3/3 | YES | 137.87 | 52.03 | 78.72 | 194.63 | 90.09 | 213,972 / 32,924 | 96.48 | 0 / 0 | 1.81 |
| 256k | 257781/4096 | REPLAY_ORACLE_FULL | 48 main layers / 3 classes | 3/3 | YES | 137.72 | 43.37 | 94.44 | 185.12 | 99.20 | 17,346 / 2,501 | 208.95 | 65,992 / 103 | 5,627.02 |




Ready/late in this table counts published admissions, not all routed entries; target-ready demand and later uses are in the raw funnel. Copy GB includes native completed publications, oracle completed copies and mandatory spare-restoration payload. Native pending-at-end bytes remain separately recorded. Planner time includes publication wait and overlaps other work: do not add timers.



| Context | Median paired TG gain | Median paired decode reduction | Median paired wall reduction | Ratio-of-medians TG gain |
|---|---|---|---|---|
| 32k | 17.01% | 14.54% | 9.81% | 17.01% |
| 128k | 22.69% | 18.50% | 9.05% | 22.69% |
| 256k | 14.51% | 12.67% | 2.00% | 19.97% |




| Context | Policy | Metric | Min | Median | Max |
|---|---|---|---|---|---|
| 32k | REPLAY_CURRENT | PP | 1,576.90 | 1,588.80 | 1,594.20 |
| 32k | REPLAY_CURRENT | decode_s | 38.34 | 38.97 | 39.52 |
| 32k | REPLAY_CURRENT | replay_equivalent_tok_s | 103.66 | 105.11 | 106.84 |
| 32k | REPLAY_CURRENT | wall_s | 56.96 | 57.39 | 58.13 |
| 32k | REPLAY_CURRENT | TTFT_s | 18.40 | 18.57 | 18.59 |
| 32k | REPLAY_ORACLE_FULL | PP | 1,586.60 | 1,592.00 | 1,595.50 |
| 32k | REPLAY_ORACLE_FULL | decode_s | 33.07 | 33.30 | 33.76 |
| 32k | REPLAY_ORACLE_FULL | replay_equivalent_tok_s | 121.34 | 122.99 | 123.86 |
| 32k | REPLAY_ORACLE_FULL | wall_s | 51.58 | 51.76 | 52.19 |
| 32k | REPLAY_ORACLE_FULL | TTFT_s | 18.42 | 18.43 | 18.49 |
| 128k | REPLAY_CURRENT | PP | 1,722.50 | 1,753.50 | 1,798.70 |
| 128k | REPLAY_CURRENT | decode_s | 48.67 | 49.81 | 49.81 |
| 128k | REPLAY_CURRENT | replay_equivalent_tok_s | 82.23 | 82.24 | 84.16 |
| 128k | REPLAY_CURRENT | wall_s | 121.31 | 124.59 | 127.70 |
| 128k | REPLAY_CURRENT | TTFT_s | 72.45 | 74.34 | 75.65 |
| 128k | REPLAY_ORACLE_FULL | PP | 1,770.80 | 1,807.10 | 1,812.60 |
| 128k | REPLAY_ORACLE_FULL | decode_s | 40.28 | 40.60 | 43.11 |
| 128k | REPLAY_ORACLE_FULL | replay_equivalent_tok_s | 95.02 | 100.89 | 101.68 |
| 128k | REPLAY_ORACLE_FULL | wall_s | 113.31 | 114.08 | 115.36 |
| 128k | REPLAY_ORACLE_FULL | TTFT_s | 72.22 | 72.68 | 73.69 |
| 256k | REPLAY_CURRENT | PP | 1,839.20 | 1,869.80 | 1,907.60 |
| 256k | REPLAY_CURRENT | decode_s | 49.52 | 52.03 | 52.95 |
| 256k | REPLAY_CURRENT | replay_equivalent_tok_s | 77.36 | 78.72 | 82.71 |
| 256k | REPLAY_CURRENT | wall_s | 188.89 | 194.63 | 198.23 |
| 256k | REPLAY_CURRENT | TTFT_s | 139.29 | 142.24 | 144.98 |
| 256k | REPLAY_ORACLE_FULL | PP | 1,859.50 | 1,871.80 | 1,920.30 |
| 256k | REPLAY_ORACLE_FULL | decode_s | 43.25 | 43.37 | 46.57 |
| 256k | REPLAY_ORACLE_FULL | replay_equivalent_tok_s | 87.95 | 94.44 | 94.71 |
| 256k | REPLAY_ORACLE_FULL | wall_s | 181.71 | 185.12 | 199.90 |
| 256k | REPLAY_ORACLE_FULL | TTFT_s | 138.30 | 141.79 | 153.30 |




## Logical clock and record/replay contract

Request 1 is the fixed warmup; request 2 is the taped workload. Identity is verifier window, model role (main / actual MTP catchup or draft), absolute position, speculative lane and layer. Main event = window * 48 + layer. Each invocation is the complete T-by-10 routing batch; no concurrent batch is converted to serial individual-expert computation. Main layers retain their normal dependency chain; draft, verify, commit and rollback retain the recorded schedule.

Actual MTP rounds compute native T-row KV-only catchup, including rejected lanes, then a full one-row routed MTP layer for accepted row a and each subsequent recorded draft. Catchup has no router/expert kernel; its invocation count and shape derive from T and draft_count. No catchup kernels are skipped.

The tape freezes input/output IDs, T, branch proposal/acceptance and draft-count schedule, routing IDs and float32 mixture coefficients, and all 12 sparse-attention selection lists. Causal masks follow unchanged positions/lane shapes. Dense layers, attention/KV/PLE/GDN, router computation, expert/shared kernels, head/draft work and rejected branches still compute normally. Overrides are applied only after native discrete decision computation. No hidden activations are replaced. Physical local/CPU/mapped grouping changes intentionally with residency.

Work SHA256 covers token/window/routes/coefficients/shapes and implicit dependency order, excluding timestamps and service placement. Initial resident slots, usage heat, native adaptation phase, GDN/PLE/HC_R, meaningful KV/QSA mappings and written canonical host prefix, and MTP state have a separate strict sidecar identity. Oracle transfers and five-slot withdrawals start inside timed decode, after this state check. Unwritten host tail and unused old MTP prefix are not meaningful state.



## Fidelity and overhead

| Short development mode | Actual input / output | Decode s | Request wall s | Scope |
|---|---|---|---|---|
| NATURAL_CONTROL, frozen original | 4096/256 | 2.1953 | 6.1720 | one reference |
| NATURAL_CONTROL, common v3 ordinary | 4096/256 | 2.2049 | 6.1787 | three paired fresh starts |
| CAPTURE, buffered diagnostics | 4096/256 | 2.3986 | 7.1197 | one record, excluded from speed controls |
| REPLAY_CURRENT, common v3 | 4096/256 | 2.2607 | 6.7797 | three paired fresh starts |


All 18 primary executions passed work/count/token/route/coefficient/shape checks and identical initial-state attestation. Replay-current guards showed zero natural router/coefficient/QSA/head disagreement. Natural versus replay-current short-workload median paired decode-time ratio = 1.0244; wall ratio = 1.0964. Original frozen-binary output matches all three experimental natural runs: True. These overhead results use the declared 256-output development workload, not the full 4096-output task.

Initial-state attestation is pre-decode setup, outside PP/TG but inside total request wall. The first 256K oracle attestation took 14.084 s versus 3.807 s for its paired control; it remains a valid, included timing observation. Oracle residency is inactive at that boundary, so this drift is not attributed to expert scheduling. See per-run setup times and median paired ratios; no post-hoc outlier exclusion.

Main sparse-attention logical selections and resolver/copy kernel launches are fixed, but native atomic CLOCK page placement can slightly change physical KV refill transactions. Available primary-device cumulative block-lookups agree; 256K first-pair RAM refills are 6075.9 versus 6075.7 MiB. Secondary-device refill counters are unavailable. This limits strict physical-service identity at streamed contexts; 32K has fully resident KV. See phase-a/KV-service-fidelity.md.

Forced output/MTP equality is enforced and is not correctness proof. Residency changes CPU Q8_K versus GPU Q8_1 activation quantization and summation, so natural numerical/head trajectories may diverge. Real Q4 expert tests against dequant reference passed all three byte classes; sampled real copied expert bytes, ownership, publication and cancellation tests provide separate safety evidence. Eight live activation components per routed invocation are compared against capture with first divergence and relative L2; native main-head top-1 agreement is also reported before overrides. These samples remained finite and are numerical diagnostics, not full tensor parity or task-quality evaluation.



## Scheduling, physical capacity and traffic

The oracle controls all 48 main routed layers, with K=24 ownership and 3.072/3.584/3.9936 MB physical classes. MTP keeps its unchanged all-resident expert cache. Five existing class-compatible slots are withdrawn inside timed decode: GPU0 has one of each class, GPU1 has the two classes present on its layers. This costs five active residents and 17,305,600 bytes of charged spare payload; original allocated VRAM does not increase. There is no P2P, remote expert execution or combined 48 GiB virtual pool.

| Context | Initial GPU0 residents/slots | Initial GPU1 residents/slots | Oracle active GPU0 | Oracle active GPU1 | Initial resident expert % |
|---|---|---|---|---|---|
| 32k | 6031 | 5510 | 6028 | 5508 | 46.96 |
| 128k | 5999 | 5477 | 5996 | 5475 | 46.70 |
| 256k | 5954 | 5432 | 5951 | 5430 | 46.33 |


Weights come from the immutable full-RAM arena, through pinned staging and asynchronous H2D copy streams with completion events. The victim remains live until a complete copy can publish at a safe routed-layer boundary. Current full-window demands protect victims. Slot identity and exclusive per-class transaction ownership are checked; this implementation uses single-owner worker state rather than an additional numeric generation counter. A promoted expert persists until a later justified exchange. Late copies fall back to the actual CPU/mapped path, never skipping or substituting experts.

Replay-current keeps original native adaptation. Oracle takes sole exchange authority in its scope while native causal heat accounting continues. Total native/oracle traffic is reported rather than only incremental oracle copies. Full-future next-use information guides victims; the rolling issue frontier is 64 main routed-layer invocations, and measured progress determines roughly 2–16 invocation lead. This is one feasible next-use/slack heuristic, not an optimal schedule or upper bound. Transfers are triggered by logical milestones, never recorded absolute seconds.

Request-comparable wall includes buffered trace flush, final asynchronous state commit, pending-copy drain and mandatory spare restoration. Native decode timing ends before the final commit/drain/restoration; their measured cost remains in total wall and is not hidden as free work. Request wall does not include fresh process loading or offline tape construction; these are separately preserved startup/recording/planning costs. The future index is built in RAM before request timing in both replay arms. Final persistent resident identity need not equal the initial set; fresh starts re-establish the exact initial state for the next arm.



The next funnel table uses attempt 1 only at each profile, so its count conservation is literal. These are oracle transaction counts; native published traffic is a separate column. All per-run funnels remain in analysis. Main performance and hardware tables use medians. No unlogged selection rejection is invented as zero.

| Context | Policy | Issued | Staged GB | Oracle completed GB | Native published GB | Published | Target-ready | Late | Resident demand uses | Victim-absent entries | Unused MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 32k | REPLAY_CURRENT | 0 | 0.00 | 0.00 | 87.42 | 0 | 0 | 0 | 0 | 0 | 0.00 |
| 32k | REPLAY_ORACLE_FULL | 65806 | 207.13 | 207.13 | 0.00 | 65806 | 65802 | 4 | 1085256 | 10036 | 6.14 |
| 128k | REPLAY_CURRENT | 0 | 0.00 | 0.00 | 99.37 | 0 | 0 | 0 | 0 | 0 | 0.00 |
| 128k | REPLAY_ORACLE_FULL | 62005 | 195.98 | 195.98 | 0.00 | 62005 | 61614 | 391 | 1230592 | 23252 | 261.12 |
| 256k | REPLAY_CURRENT | 0 | 0.00 | 0.00 | 96.48 | 0 | 0 | 0 | 0 | 0 | 0.00 |
| 256k | REPLAY_ORACLE_FULL | 61787 | 195.70 | 195.70 | 0.00 | 61787 | 61179 | 608 | 1157992 | 22072 | 466.94 |




| Context | Attempt-1 published | Reused in >=2 distinct invocations | Used after intended target | Distinct resident uses | Resident lifetime censored at end |
|---|---|---|---|---|---|
| 32k | 65806 | 48101 | 48101 | 837614 | 9330 |
| 128k | 62005 | 47408 | 47449 | 916555 | 9136 |
| 256k | 61787 | 45836 | 45915 | 878458 | 8795 |


Repeated invocation counts exclude duplicate lane entries inside one batch. Resident lifetimes ending with the request are right-censored. All copies in the tested full-future schedules completed and published; unused published bytes are distinct from unpublished bytes.

| Context | Median issue lead (invocations) | Median issue-to-target ms | Median staging ms | Median copy+host-wait ms | Median completion-to-publication ms |
|---|---|---|---|---|---|
| 32k | 47.00 | 25.339 | 0.125 | 0.242 | 0.269 |
| 128k | 33.00 | 21.175 | 0.253 | 0.246 | 0.331 |
| 256k | 34.00 | 21.930 | 0.215 | 0.245 | 0.347 |


## Decode progression and hardware

| Context | Policy | TG 0–512 | TG 512–1K | TG 1K–2K | TG 2K–4K | Final TG |
|---|---|---|---|---|---|---|
| 32k | REPLAY_CURRENT | 100.38 | 116.23 | 106.58 | 105.03 | 105.11 |
| 32k | REPLAY_ORACLE_FULL | 119.97 | 131.94 | 121.58 | 123.70 | 122.99 |
| 128k | REPLAY_CURRENT | 85.46 | 86.26 | 81.24 | 83.27 | 82.24 |
| 128k | REPLAY_ORACLE_FULL | 98.83 | 97.01 | 98.12 | 103.47 | 100.89 |
| 256k | REPLAY_CURRENT | 79.76 | 82.96 | 77.82 | 78.17 | 78.72 |
| 256k | REPLAY_ORACLE_FULL | 92.50 | 98.84 | 96.31 | 92.67 | 94.44 |


Intervals use complete verifier-window timestamps with boundary overshoot retained. They include actual MTP/draft/adaptation work. Per-interval local/CPU/mapped counts and MTP acceptance are preserved in analysis/*-progression.json; the frozen MTP trajectory is identical between policies.



| Context | Policy | VM CPU mean % | GPU0 mean % | GPU1 mean % | Peak decode RSS GiB | VRAM0 GiB | VRAM1 GiB | CPU steal mean % | Process CPU % (one core=100) | GPU0 / GPU1 power W |
|---|---|---|---|---|---|---|---|---|---|---|
| 32k | REPLAY_CURRENT | 47.57 | 53.02 | 52.62 | 76.79 | 23.28 | 23.46 | 5.09 | 721.52 | 153.21 / 166.81 |
| 32k | REPLAY_ORACLE_FULL | 15.28 | 58.00 | 63.61 | 76.80 | 23.28 | 23.46 | 0.65 | 228.96 | 165.71 / 184.19 |
| 128k | REPLAY_CURRENT | 46.51 | 54.20 | 50.51 | 78.66 | 23.28 | 23.46 | 8.11 | 675.47 | 148.43 / 160.58 |
| 128k | REPLAY_ORACLE_FULL | 17.22 | 56.88 | 60.38 | 78.66 | 23.28 | 23.46 | 1.70 | 251.67 | 161.58 / 178.60 |
| 256k | REPLAY_CURRENT | 44.25 | 53.00 | 51.41 | 80.34 | 23.28 | 23.47 | 9.48 | 630.08 | 150.00 / 161.69 |
| 256k | REPLAY_ORACLE_FULL | 16.18 | 56.28 | 60.40 | 80.35 | 23.28 | 23.47 | 1.88 | 229.27 | 162.32 / 178.50 |


CPU steal and startup/attestation drift are retained limitations, not exclusion criteria. Aggregate 1 Hz PCIe samples are separate from logical expert-copy bytes. They do not identify event-level DMA duration or saturation. Host staging/queue/completion/publication timestamps have scheduling and CUDA-wait contributions; overlapping timers are not summed. CPU expert arithmetic and mapped GPU execution remain distinct paths. Physical process I/O cannot be attributed to experts; host arena residence is verified independently.



CPU steal is systematically higher in the busier current arm (about 5–9% versus 0.7–1.9%). This may reflect VM scheduling sensitivity to the additional CPU demand; the data cannot identify all host activity. The measured paired gain is for this VM under retained conditions, not a hardware-only speed bound with steal eliminated.

| Context / attempt1 | Policy | CPU-positive invocations | Median completion span us | P95 span us | Summed spans s (overlapping) | Mapped-positive invocations |
|---|---|---|---|---|---|---|
| 32k | REPLAY_CURRENT | 52198 | 242.11 | 613.23 | 15.033 | 23362 |
| 32k | REPLAY_ORACLE_FULL | 3044 | 289.00 | 695.81 | 1.010 | 1189 |
| 128k | REPLAY_CURRENT | 58919 | 262.97 | 729.57 | 18.941 | 25169 |
| 128k | REPLAY_ORACLE_FULL | 7283 | 359.25 | 883.95 | 3.045 | 2865 |
| 256k | REPLAY_CURRENT | 58534 | 264.82 | 778.09 | 19.315 | 22805 |
| 256k | REPLAY_ORACLE_FULL | 8432 | 392.20 | 1,149.35 | 4.114 | 3183 |


These spans include activation quantization, host group/job construction and native CPU completion. They are not pure exposed waits, and can overlap GPU work. In representative 32K native timing, CPU work fell from 11.22 to 0.75 ms/window while planner rose from 0.21 to 3.77 ms/window and GPU-reach wait rose from 5.89 to 8.24 ms/window. The complete window fell from 30.23 to 25.84 ms. These native labels overlap; they are diagnostic evidence rather than an additive causal decomposition.

## Horizons and independent workload

The horizon unit is one future main-model verify routed-layer batch invocation; 48 invocations correspond to one complete main window. Offline horizons 1/4/16/64 and full future are separate capacity-only or transfer-modeled simulations, with no simulated TG. An early bounded simulation accidentally protected current-window demand outside H; repaired strict simulations restrict that privileged safety knowledge. The old safety-privileged output remains diagnostic evidence, not a valid bounded arm.

Both live full and H64 arms use the same 64-invocation incoming issue frontier. Full future additionally has longer victim next-use/lifetime knowledge, and utility queries beyond that issue frontier; H64 bounds both sides. Therefore the negative H64 result does not establish that incoming prediction alone must exceed 64 invocations. It particularly exposes the importance of victim/reuse knowledge and consequent admission choices.

One audited live H64 confirmation (both admission and victims bounded) took 42.766 s, 95.78 replay-equivalent tok/s. It issued 99,704 copies / 317.525 GB and caused 85,392 victim-absent routed entries. Full-future attempt 1 issued 65,806 copies / 207.126 GB and caused 10,036 victim-absent entries. The extra churn and victim damage explain why this tested shorter policy loses despite more admissions. It is a later single scoped measurement, not an extra fresh paired ranking against the three-attempt primary matrix. It measures this short-horizon heuristic, not an information-theoretic limit.

A substantive independent Python zipfile/archive source task was captured separately and replayed in three fresh counterbalanced pairs with actual copied-byte checks ON in every arm. Median paired throughput ratio = 1.1632; wall ratio = 0.9184. It is separate 1024-output diagnostic/application evidence, not mixed into the clean 4096 headline table. See phase-c/independent-v3-summary.json.



## Remaining misses and exposed work

Observed nonlocal demands are classified from live ownership/copy records in analysis/*-residual-misses.json. Victim-absent demand takes precedence; pending or complete-but-unpublished copies are separated from demand for which no admission was selected. Unlogged reasons such as worker busy versus utility rejection remain unknown. These categories do not estimate physical read bytes by multiplying routed entries by expert size.

| Context / attempt1 | Nonlocal entries | Victim absent | Copy pending | Complete not published | No observed admission |
|---|---|---|---|---|---|
| 32k | 13213 | 10036 | 1 | 0 | 3176 |
| 128k | 29639 | 23252 | 145 | 0 | 6242 |
| 256k | 33375 | 22072 | 311 | 0 | 10992 |


Victim absence dominates the remaining nonlocal entries in these full-future runs. This points to exchange scheduling/victim lifetime as remaining headroom, rather than widespread copy lateness. It does not prove a globally optimal policy or that an implementable predictor could reproduce it.

Actual target-ready demand and late-but-useful demand are retained in summary rows. Published-before-target admission is not synonymous with a useful demand hit: an admission can be evicted again before its target. Queue/staging/publication evidence and lifetime/repeated-use data are in event diagnostics. Extra H2D traffic is worthwhile only when the measured CPU/mapped critical path it removes exceeds these costs.



## Failures, repairs and limitations

The ledger preserves malformed tape validation, relative tape-path failure, compile and stale-symlink build repairs, the native adaptation counter offset after warmup, unfrozen QSA selection in v1, initial numerical-state attestation missing in v2, and the repaired bounded-simulation knowledge leak. v1/v2 pilot timing remains excluded from v3 headlines. No model weights or original runtime were changed.

Native suite: 66 PASS, 2 SKIP, 4 pre-existing missing legacy-fixture/mlock-limit failures. Targeted QSA and actual-Q4 math tests passed; the new state-contract fixture and real-copy scheduler fixture results are in tests/. This does not claim every upstream test passed.

The H64 request completed all work and produced its full valid timing/funnel before owned shutdown. SIGTERM to the frontend/native process group then exposed an upstream frontend double-close BrokenPipeError. The retained shutdown traceback is outside request timing, not a hidden inference failure; final process/GPU audit confirms cleanup. A post-analysis wrong independent label and missing matplotlib package were also preserved and repaired without rerunning inference.

Full future knows this tape ends after 4096 visible outputs; no guard tail was recorded. Tail victim reuse outside the tape is genuinely unknown in deployment. The schedule may exploit finite ending. Capacity-only zero-nonlocal simulation is optimistic; transfer-modeled feasibility is not measured throughput. One tape per profile plus one independent task does not prove universal performance or predictor attainability.



## What a future causal predictor should learn

The positive causal target is a useful, target-ready persistent exchange: near-term actual batch demand at sufficient logical lead, repeated residency lifetime, victim next-use/absence loss, and current staging/copy/publication queue feasibility. Generic expert popularity alone misses costly victim mistakes. A practical predictor must jointly decide whether to admit and which valuable resident to protect; oracle traffic is substantial and a cheap selective policy must avoid paying for low-value churn. Full-future results establish feasibility only for measured schedules/workloads.



## Reproduce and normal serving

All tools are preserved under scripts/ and launchers/. Experimental capture/replay tools verify identities, refuse GPU/port conflicts, have finite timeouts, create a new isolated reproduction directory after this campaign completes, and clean up only owned processes. Normal serving never selects a tape or oracle.



```bash
# Experimental; replace PROFILE with 32k, 128k or 256k
./launchers/experimental/capture-128k.sh
./launchers/experimental/validate-tape.sh --profile 128k
./launchers/experimental/replay-current-128k.sh
./launchers/experimental/replay-full-128k.sh
./launchers/experimental/replay-short-128k.sh

# Unchanged real-use Q4 / 100us control, default host 0.0.0.0
./launchers/control/start-32k.sh --host 0.0.0.0 --port 8080
./launchers/control/start-128k.sh --host 0.0.0.0 --port 8080
./launchers/control/start-256k.sh --host 0.0.0.0 --port 8080
./launchers/control/stop.sh
```

## Provenance and audit

| Run | State-attestation s | Tape lookup ms | Tape RAM MB | Initial bytes checked |
|---|---|---|---|---|
| v3-current-32k-attempt1 | 0.515 | 118.35 | 528.119592 | 623320868 |
| v3-current-32k-attempt2 | 0.570 | 419.49 | 528.119592 | 623320868 |
| v3-current-32k-attempt3 | 0.503 | 95.43 | 528.119592 | 623320868 |
| v3-oracle-32k-attempt1 | 0.557 | 426.45 | 528.119592 | 623320868 |
| v3-oracle-32k-attempt2 | 0.511 | 106.15 | 528.119592 | 623320868 |
| v3-oracle-32k-attempt3 | 0.512 | 115.42 | 528.119592 | 623320868 |
| v3-current-128k-attempt1 | 1.734 | 201.48 | 628.424108 | 1963148068 |
| v3-current-128k-attempt2 | 1.794 | 189.77 | 628.424108 | 1963148068 |
| v3-current-128k-attempt3 | 1.812 | 405.64 | 628.424108 | 1963148068 |
| v3-oracle-128k-attempt1 | 1.825 | 469.59 | 628.424108 | 1963148068 |
| v3-oracle-128k-attempt2 | 2.483 | 422.07 | 628.424108 | 1963148068 |
| v3-oracle-128k-attempt3 | 1.859 | 339.45 | 628.424108 | 1963148068 |
| v3-current-256k-attempt1 | 3.807 | 516.73 | 667.848212 | 3827046948 |
| v3-current-256k-attempt2 | 3.620 | 179.53 | 667.848212 | 3827046948 |
| v3-current-256k-attempt3 | 4.295 | 407.71 | 667.848212 | 3827046948 |
| v3-oracle-256k-attempt1 | 14.084 | 571.33 | 667.848212 | 3827046948 |
| v3-oracle-256k-attempt2 | 3.541 | 157.66 | 667.848212 | 3827046948 |
| v3-oracle-256k-attempt3 | 3.529 | 160.19 | 667.848212 | 3827046948 |


| Run | Sample bitwise equal | Sample relative L2 | Max sample absolute difference | First window/role/component | Native head top-1 agreement % |
|---|---|---|---|---|---|
| v3-current-32k-attempt1 | True | 0.00000 | 0.00000 | None | 100.000 |
| v3-current-32k-attempt2 | True | 0.00000 | 0.00000 | None | 100.000 |
| v3-current-32k-attempt3 | True | 0.00000 | 0.00000 | None | 100.000 |
| v3-oracle-32k-attempt1 | False | 0.03412 | 1.92905 | [0, 5, 0] | 99.607 |
| v3-oracle-32k-attempt2 | False | 0.03333 | 1.13124 | [0, 5, 0] | 99.695 |
| v3-oracle-32k-attempt3 | False | 0.03379 | 1.18690 | [0, 5, 0] | 99.695 |
| v3-current-128k-attempt1 | True | 0.00000 | 0.00000 | None | 100.000 |
| v3-current-128k-attempt2 | True | 0.00000 | 0.00000 | None | 100.000 |
| v3-current-128k-attempt3 | True | 0.00000 | 0.00000 | None | 100.000 |
| v3-oracle-128k-attempt1 | False | 0.03259 | 1.91598 | [0, 5, 0] | 99.463 |
| v3-oracle-128k-attempt2 | False | 0.03248 | 1.30411 | [0, 5, 0] | 99.523 |
| v3-oracle-128k-attempt3 | False | 0.03318 | 0.92330 | [0, 5, 0] | 99.344 |
| v3-current-256k-attempt1 | True | 0.00000 | 0.00000 | None | 100.000 |
| v3-current-256k-attempt2 | True | 0.00000 | 0.00000 | None | 100.000 |
| v3-current-256k-attempt3 | True | 0.00000 | 0.00000 | None | 100.000 |
| v3-oracle-256k-attempt1 | False | 0.03760 | 1.00376 | [0, 19, 0] | 99.287 |
| v3-oracle-256k-attempt2 | False | 0.03806 | 1.02164 | [0, 5, 0] | 99.094 |
| v3-oracle-256k-attempt3 | False | 0.03796 | 1.66115 | [0, 5, 0] | 99.191 |


Some copied control configs retain a historical pool-experiment annotation. Effective native command/environment and per-attempt oracle configuration are authoritative; configs/interpretation.json records the metadata erratum. Preliminary v1 short-overhead evidence informed the initial funnel; the final v3 overhead guard was measured after the main matrix and before interpretation. v3 added only pre-decode state attestation to the v2 computational substrate, but this order deviation is retained transparently.

Original serving source: 6f32ec070f23ced9f50e704d854d775da52591ab; binary SHA256 eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d. Final common experimental source: 117bc89b3bacbf263379c336557e6c8aa07aff5e; binary SHA256 30a31432b5aff51bcd4340900c13cad0c8487a832bfdb22d05f9157b88d5bdb3. Both use Strata0.1.39 ancestry, CUDA sm_89 and identical normal build options. Model revision38bb39ee97821de2c9009abb7e93950eec396e66 and existing ud-q4_k_xl-v0132 pack are unchanged.

Standalone measured-data figures are in analysis/plots/. Plotting dependencies are isolated in .analysis-venv with requirements-plotting.txt; they do not modify the frozen control environment. scripts/render_report.py recreates this report from the audited summaries, scripts/aggregate.py recreates CSV/JSON, and scripts/refresh_audits.py recomputes conservation/fidelity analyses. No learned predictor, helper comparison, pool/K/PCIe tuning, or ordinary free-generation oracle run was performed.

## Unfinished and future work

No required bounded phase remains unfinished due to the deadline; the campaign finishes early. A globally optimal variable-size schedule, a recorded guard tail, secondary-device exact KV DMA counters, full hidden-tensor parity and a deployable causal predictor were not established. The optional longer-output amortization test was not necessary after the full matrix and independent task answered feasibility. H64 was one negative scoped confirmation rather than a full context matrix. These are limitations, not hidden positive claims.

Start 2026-10-06 04:06:56 UTC; absolute deadline12:06:56 UTC; no substantial work after11:21:56 UTC. Actual completion, local research commit, launcher checks and no-owned-GPU-process audit are recorded in STATUS and final-audit artifacts. Previous campaigns and normal user launchers remain untouched. No push, PR, remote compute or weight changes.



FEASIBLE_LIVE_ORACLE_GAIN
