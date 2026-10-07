# Goal: Q4 oracle decomposition — incoming demand versus victim lifetime

Act as an autonomous systems/ML performance researcher in the existing Strata laboratory. Analyze and execute a focused continuation of the completed live-oracle experiment. Reuse its validated replay infrastructure rather than restarting the residency project.

## 1. Research question

The previous experiment found a feasible faster schedule with future information, real transfers and fixed VRAM. Its bounded H64 schedule lost, but that comparison restricted several kinds of future knowledge simultaneously.

We now need to distinguish:

- **Incoming knowledge:** which nonresident expert will be needed, how soon, and how valuable retaining it will be.
- **Victim knowledge:** which resident expert can be evicted, when it will be needed again, and what loss its absence causes.

Determine which information restriction removes the measured benefit, how the two restrictions interact, and what a future causal predictor should actually learn. Do not train that predictor in this campaign.

This is an execution task with analysis and bounded experiments, not merely a discussion. Perfect future information is a research privilege, not a deployable solution. A horizon experiment measures this scheduler under its stated information budget; it does not establish an information-theoretic limit.

## 2. Deadline, autonomy and preservation

**Maximum: 6 hours elapsed wall time, including setup, analysis, builds, experiments and reporting.** Record UTC start/deadline and monotonic elapsed time. Do not reset the deadline after a failure, restart or context compaction. At T+5h15m stop starting substantial new work and reserve the final 45 minutes for reporting, reproducibility and cleanup.

Finish earlier when the bounded questions are answered. Do not stop at the first failed build, ambiguous result or losing schedule. Investigate the mechanism and make a bounded, hypothesis-driven repair when justified. Do not fill unused time with more repetitions or unrelated tuning.

You may inspect local source, use the internet for relevant primary documentation, install isolated user-space dependencies and compile experimental code. No sudo is available. Do not change drivers, host/VM configuration, CPU/GPU clocks, power limits, model weights, normal launchers, or upstream versions. No push, PR, paid external services or private-data upload. All new artifacts must be in English.

Check current process/GPU ownership before starting. Do not kill unrelated work or benchmark concurrently with another campaign. Preserve all old campaigns and create a new timestamped directory:

`/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-oracle-decomposition-<UTC_TIMESTAMP>/`

Every long-running process needs progress logging, a suitable timeout and owned-process cleanup. Preserve exit codes and failed attempts. No unbounded hangs, broad `pkill -f`, silent exception suppression or repeated speculative rewrites.

## 3. Mandatory starting evidence and frozen substrate

Read the completed campaign:

`/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-live-oracle-20261006T040656Z/`

Inspect its report, summaries, STATUS/DECISIONS, tape manifests, source patches, scheduler, fidelity checks, strict bounded-horizon repair, residual-miss reports, timing records and launchers. Follow actual artifact paths; do not infer missing files from names.

Important recorded facts to verify:

- Final common replay source: `117bc89b3bacbf263379c336557e6c8aa07aff5e`.
- Final common replay binary SHA256: `30a31432b5aff51bcd4340900c13cad0c8487a832bfdb22d05f9157b88d5bdb3`.
- Original serving source: `6f32ec070f23ced9f50e704d854d775da52591ab`.
- Original serving binary SHA256: `eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d`.
- Model: Qwen3.8-Flash-Next UD-Q4_K_XL, revision `38bb39ee97821de2c9009abb7e93950eec396e66`.
- Two RTX 4090 24 GiB; K=24; PCIe fraction=0.28; pool spin=100 us; 15 workers; MTP spec=4/min-p=0.5; INT8 KV; kv-resident=32768 where valid; prefill=auto; suffix/reuse OFF; greedy/serial.
- All 48 main routed layers and three physical expert classes are covered. Five existing class-compatible slots are charged as spares, not additional VRAM. MTP retains its unchanged resident cache.
- The full-future scheduler already uses a **64-invocation incoming issue frontier**, while consulting longer future information for victims and utility. Full future does not mean that copies are issued arbitrarily far ahead.
- The previous H64 restriction applied to both incoming and victim knowledge. Its 95.78 replay-equivalent tok/s result was one later scoped run, not a matched three-pair decomposition.

Retain the current runtime, memory envelope, copy concurrency, publication/reader safety, native-cache arbitration and all ordinary settings. No pool/helper/K/PCIe/MTP search, new quantization, new allocator or broad Jev/Basal/Markov comparison.

Create isolated source/build directories for necessary instrumentation and information controls. New comparisons must use the same new experimental binary. Prove the unrestricted mode matches the old algorithm and the ordinary/replay-current modes have not silently changed.

The old results are motivation and validation references, not fresh comparison arms.

## 4. Phase A — audit and separate the information channels

### A1. Define the logical horizon exactly

Use the existing logical clock: one horizon unit is **one main-model verify routed-layer batch invocation**. There are 48 such invocations per main verify window. Keep model role, window, layer, token position, speculative lane and batch shape in the event identity.

H64 therefore means 64 future routed-layer invocations, not 64 generated tokens or 64 verify windows. Keep each T-by-10 batch intact; do not manufacture serial per-expert execution. Define the inclusive/exclusive endpoint once and test it.

Wall-clock timestamps measure actual costs and readiness; they do not identify the event at which a transfer must start. Preserve logical triggers and real asynchronous completion.

### A2. Separate eligibility, incoming valuation and victim valuation

Audit every future-dependent query in candidate generation, scoring, victim selection, safety checks, reservations, queueing, publication and cancellation. Record its purpose and permitted horizon.

Use these three concepts explicitly:

- **E:** incoming eligibility/issue frontier. Preserve the existing maximum E=64.
- **I:** incoming future-demand and retention-utility horizon.
- **V:** resident-victim next-use/lifetime horizon.

An incoming expert is eligible only when its first relevant demand is visible within `min(E, I)`. Incoming reuse/value queries may inspect up to I. Victim-value queries may inspect up to V. FULL means the remaining recorded tape, not knowledge beyond its end.

The primary H64 decomposition holds E=64 in all oracle arms. Thus I=64 versus I=FULL keeps the same eligibility window but changes information about incoming value beyond it. This distinction is essential: a loss cannot automatically be blamed on insufficient copy lead.

For exploratory I=4 or I=16, eligibility also shortens. Label this coupling and separate timing failures from valuation failures. I=256 does not authorize copying 256 invocations early; E remains 64.

### A3. Prevent privilege leakage without weakening safety

Implement typed or otherwise auditable future-query views. The execution engine/evaluator may read the full tape to reproduce the workload; the scheduler policy must see only the information allowed to that decision role.

A bounded query that finds no use must return **unknown beyond H**, not “never used”. Define a causal fallback from observed history for censored candidates/victims. Keep that fallback fixed across ablations; do not silently use exact future next-use to break ties.

Prevent full-future information leaking through cached utility scores, victim-to-incoming role changes, precomputed global rankings, cancellation rules or tie-breaking. Log/assert query horizons in diagnostics.

Audit the earlier current-window protection leak. Actual current/in-flight readers must always be protected. Future tape demand outside an arm's horizon must not become a free policy hint. If the existing implementation relies on additional privileged future protection, explicitly parameterize it as a separate common channel and qualify the experiment, or repair the information boundary safely before claiming a strict bounded result. Never remove necessary synchronization to enforce an information budget.

Write source-level tests where only out-of-horizon future suffixes change. A bounded decision must not change unless the changed information is legitimately available through another declared channel. Test I and V separately, including after role changes. If counterfactual execution state differs, do not mistake that difference for an information leak.

Phase A deliverables: an information-channel map, exact horizon semantics, tests, and a frozen comparison protocol. Do not launch the final matrix before this contract is clear.

## 5. Phase B — small offline decomposition, then candidate freeze

Reuse the recorded tapes and validated replay/cost model. Do not repeat trace capture, the hardware study or the earlier broad policy competition unless an actual missing field blocks this experiment.

Start at 32K. Evaluate these oracle information budgets under the same scheduler:

| Arm | Incoming horizon I | Victim horizon V | Purpose |
|---|---|---|---|
| F/F | FULL | FULL | Reproduce feasible full-future reference |
| 64/F | 64 | FULL | Restrict incoming valuation only |
| F/64 | FULL | 64 | Restrict victim knowledge only |
| 64/64 | 64 | 64 | Joint restriction and interaction |

Add two sparse offline curves using H in `{4, 16, 64, 256, FULL}`: `(I=H,V=FULL)` and `(I=FULL,V=H)`. Deduplicate endpoints. Do not build the full 25-cell grid. Deterministic simulation needs one execution per unchanged point, not three identical repetitions.

Preserve physical classes, spare cost, initial state, native/external exchange authority, queues and timing assumptions. Do not select by cache hit rate alone. Report copy bytes, readiness, CPU/mapped demand, victim absence, repeated use, churn and modeled exposed cost. Unavailable causal costs stay unavailable. No simulated TG labeled as measured throughput.

Use offline results to diagnose which channel is limiting and select at most one additional informative horizon or one follow-up conditional slice. For example, if victim horizon dominates, inspect V=256 with I fixed instead of reopening all combinations.

A poor outcome may reflect mishandling censored next-use rather than insufficient information. When that occurs, preserve the original result and test one meaningful causal fallback repair. Do not keep feeding unknown values into an infinity sentinel and then declare the horizon fundamentally inadequate.

Freeze the algorithms, chosen horizons, unknown-value treatment and live run order before performance confirmation. No tuning against final timing results. A substantive repair creates a versioned experiment, not an excuse to discard an unfavorable run.

## 6. Phase C — matched live-replay ablations

### C1. Main 32K experiment

Use the recorded 32K workload and one common replay binary. The practical reference remains **REPLAY_CURRENT**, with its original native adaptation and capacity; do not reserve oracle spares in it merely to weaken the reference.

The main oracle comparison is F/F, 64/F and F/64. Include 64/64 as the fourth oracle arm when needed to measure the interaction; prefer this complete four-arm decomposition over guessing from the old single H64 result.

With REPLAY_CURRENT plus four oracle arms, the maximum basic matrix is:

`5 arms x 3 attempts = 15 live requests at 32K`.

Use three fresh-start counterbalanced blocks where practical. Every arm in a block uses the same tape, exact initial-state contract and fixed 4096-input/64-output warmup followed by natural uncached prefill. Reuse one tape for timing repeatability and state that these are not independent task samples.

Screening requests count toward the three-attempt limit when the point/protocol is unchanged. Do not exceed **three measured attempts per unchanged point in this campaign**. Keep invalids, timeout traces and slow observations. Do not add a fourth run to replace an inconvenient value. Genuine repair/version changes must be documented.

### C2. Context and task transfer

Only after the 32K decomposition is meaningful, select the most informative restriction or mixed finite-horizon policy for 128K and 256K. Compare it with contemporary REPLAY_CURRENT and F/F, at most three arms per profile, three attempts each. Do not repeat the entire horizon matrix at both larger contexts.

Keep total limits 32768, 131072 and 262144, the existing input tapes and 4096 recorded output normalization. Never enlarge context or shrink output to manufacture a comparison.

Where time permits, reuse the existing substantive Python zipfile/archive task as an independent-workload transfer check. It is previously observed evidence, not a newly untouched holdout. Retain its shorter-output and copied-byte-check settings identically across arms; report it separately. Do not claim generalization from repeatedly playing one tape.

If no meaningful distinction emerges at 32K, diagnose information controls, scheduling and timing before spending most of the budget on larger contexts. A clear limited conclusion is better than a large ambiguous grid.

### C3. Fidelity, safety and real costs

Preserve the final v3 work contract: token IDs, MTP proposals/acceptance/rollback and catchup, routes, float32 mixture coefficients, sparse-attention selections, shapes and dependencies. Dense/attention/KV/PLE/expert/router/head work still executes. No skipped computations, fabricated copy readiness or changed service path hidden in the work hash.

Check initial-state attestation and work fingerprints for every request. Require unrestricted-mode and replay-current guards; test forced wrong/late candidates, duplicate reservations, protected victims, completion-before-publication, cancellation and spare restoration whenever affected code changes.

The metric is **replay-equivalent tok/s**, not newly generated model output or validated translation/code quality. Forced output agreement is a contract check, not a correctness proof. Preserve numerical diagnostics and known physical KV-service limitations, including unavailable secondary-device DMA detail.

Charge real H2D/staging, online query/planning, spare withdrawals, queues, drain and restoration. Future-index preparation may remain outside timed decode as in the original oracle study, but report its cost and memory. Do not hide expert preloads in attestation or untimed setup. Oracle modes retain identical physical spare budgets; no added VRAM or different allocator.

## 7. Analyze the two channels and their interaction

For each matched block let:

- `T_current` be replay-current decode time;
- `T_full` be F/F decode time;
- `T_candidate` be the restricted arm's decode time.

When `T_current > T_full`, compute:

`gain_retention = (T_current - T_candidate) / (T_current - T_full)`.

This measures how much of the observed full-oracle decode-time saving remains. Calculate within matched blocks, then summarize. Do not mix historical controls or use a ratio of unrelated medians. Do not clamp negative retention or values above one; investigate them. If the denominator is negligible or nonpositive, mark retention unstable/undefined.

As a practical aid, an arm retaining roughly 80–90% of the benefit is interesting, but this is not a significance or equivalence test. Also report absolute milliseconds, copied bytes, CPU/mapped work and whole-request latency. A smaller useful gain with lower transfer cost may be preferable to maximum TG at excessive churn.

Compare F/F -> 64/F and F/F -> F/64. Use 64/64 to test whether simultaneous restrictions interact. Do not add the two losses as if the system were linear. If useful, report the descriptive matched interaction:

`T_64_64 - T_64_F - T_F_64 + T_F_F`.

Interpret it with timing variability and changed placement trajectories, not as a universal causal coefficient.

Count victim absence as observed demand while displaced, not a proven exclusive latency penalty. Distinguish global demand coverage from useful reuse of admitted experts and target-ready publication from an actual hit at the target. Track victims reloaded repeatedly, recurring promotions and candidates copied but evicted before use.

Full knowledge extends only to the recorded tape end. Preserve finite-end censoring; there is no recorded guard tail. Report an identically defined interior-window sensitivity from the same runs when practical, without choosing a favorable interval or excluding cleanup from whole-request time.

## 8. Timing variability is part of the interpretation

The previous study reported systematically higher CPU steal in replay-current than oracle and a large first-256K attestation delay. Retain those caveats; do not label the new gain hardware-only.

Use interleaved blocks and record CPU steal, process/VM CPU, affinity, other visible load, GPU clocks/utilization/power/temperature, initial-state attestation time and replay lookup cost. Do not change host configuration or clocks. No parallel builds, profiling, training, heavy hashing or unrelated GPU work during headline runs.

Report per-pair results and min/median/max. Three repetitions do not remove confounding or prove equivalence. Explain outliers without deleting them because they are slow. If uncertainty prevents ranking, say so rather than producing a precise horizon requirement.

Decode gains and total-request gains answer different questions. Long prefill may dilute a real decode saving. Separate those metrics, retain setup/cleanup accounting, and never sum overlapping timers into an invented throughput estimate.

## 9. Repair strategy and scope of the conclusion

When a result is surprising, ask in order:

1. Did the intended information restriction actually apply without leakage?
2. Did the same work and initial state execute safely?
3. Did unknown future values receive a defensible treatment?
4. Did the scheduler miss deadlines, churn, damage victims or coordinate poorly with native state?
5. Could timing variability or limited coverage explain the observed difference?

Preserve the failed version, write a concrete hypothesis and try a bounded repair or alternative diagnostic. Do not turn the campaign into an optimizer search until some arm wins. If a repair changes common scheduler behavior, revalidate the common reference and label the new comparison separately.

Do not infer that a deployable predictor must know an exact distant next-use merely because the oracle used it. The practical target may instead be calibrated eviction risk, durable hotness, expected reuse or uncertainty-aware retention. State what the evidence supports and what remains a hypothesis.

A loss for bounded I is not automatically a demand-prediction failure: distinguish eligibility/lead, incoming lifetime valuation and unknown-handling. A loss for bounded V is evidence about this scheduler's victim decisions, not proof that every short-history eviction policy fails.

Do not train Jev/MLP/Basal now. Produce a precise specification for a later predictor: candidate population, available causal features, target, horizon units, cost weighting and uncertainty behavior.

## 10. Required artifacts and final decision

Preserve GOAL, STATUS, DECISIONS, experiment ledger, information-channel map, feature/query audit, tests, offline tables, tapes/manifests, schedule definitions, raw logs, source patches, build identities, CSV/JSON summaries and final report. Scripts must remain in the repository, not only /tmp or shell history. Local commits are allowed; no push.

Provide tested commands for each retained replay arm and all supported profiles. Resolve binaries/configs explicitly, check hashes, detect conflicts and stop only owned processes. Preserve the existing normal Q4 launcher path; do not enable tape/oracle in real serving. Do not create new normal launchers merely to rename unchanged behavior.

The final report must include:

- Exact E/I/V semantics and evidence that future-query restrictions were enforced.
- The 32K asymmetric decomposition and any interaction result.
- Sparse offline horizon curves, clearly separated from live measurements.
- Selected 128K/256K and independent-task confirmation, with limitations.
- Gain retained, readiness, copy traffic, victim absence, CPU/mapped demand, planner cost and timing uncertainty.
- All repaired failures and negative results.
- The smallest tested sufficient information budget for each role, or an explicit statement that it remains unresolved.
- A specific next predictor/scheduler research target, not another generic algorithm list.

Main table:

| Profile/tape | E | I | V | Attempts/valid | Replay decode s | Replay-equivalent tok/s | Paired TG change vs current | Full-gain retention | Wall s | Copy GB | CPU/mapped entries | Victim-absent entries | Late demand | Online planner ms |
|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|

End with one primary conclusion, scoped to the measured workloads:

- `VICTIM_INFORMATION_DOMINATES`
- `INCOMING_INFORMATION_DOMINATES`
- `BOTH_CHANNELS_MATTER`
- `BOUNDED_INFORMATION_RETAINS_GAIN`
- `SCHEDULER_OR_CENSORING_LIMITS_INTERPRETATION`
- `INCONCLUSIVE`

The unchanged **Q4 / K24 / PCIe 0.28 / pool 100 us** remains the real-use baseline regardless of oracle outcome. Stop owned experiments, verify GPU cleanup and preserve all data before the deadline.

**Research standard:** identify what useful information the scheduler needs, not just which label wins a throughput table. Separate knowing what to load from knowing what to retain, charge real costs, repair flawed experimental assumptions, and leave a reproducible basis for the next causal predictor.