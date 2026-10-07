# Goal: improve IQ3_S inference through expert selection, prediction and placement

Act as an autonomous systems/ML researcher. Investigate, implement and test ways to improve the best preserved Strata configuration on this machine by selecting, predicting and scheduling expert residency under a fixed VRAM budget.

**Hard deadline: 10 hours of elapsed wall time from starting this task, including setup, research, downloads, builds, experiments, analysis, reporting and cleanup.** Record the start and absolute deadline. Re-read this goal and the persistent status after context compaction or resumption; never reset the deadline. Reserve the final 30–45 minutes for consolidation. Use bounded subprocesses and stop only your own processes before the deadline.

Finish earlier only when the plausible paths have been investigated sufficiently to justify stopping. Otherwise, use remaining time to investigate supported follow-up ideas, repair weaknesses and strengthen the evidence. Do not stop at the first successful patch or first negative result.

This is an execution task, not merely a proposal or literature review. Produce runnable experiments and evidence, not promises of future work. Do not claim every possible approach has been exhausted when the time limit is the actual reason for stopping.

## 1. Objective, permissions and boundaries

The target is lower real request latency and/or higher useful decode throughput at **32K and 128K total context capacity**, with correct model execution. Expert-cache hit rate, GPU utilization and predictor accuracy are explanatory metrics, not the objective.

You may browse the internet, read papers and source, clone repositories, download research dependencies or justified auxiliary models, compile software, train small predictors, modify local experimental source, and run local tests. You have the user's permission for these task-scoped actions without asking about each ordinary step.

**There is no sudo.** Use virtual environments, user-space package installation, project-local prefixes, downloadable user-space tools or source builds. Missing packages, profiler permissions or unavailable binaries are problems to solve or work around, not reasons to terminate the investigation. Do not bypass privilege boundaries.

Preserve existing model weights, quantization, profiles, benchmark data, launchers, services and source checkouts. Use the existing IQ3_S model; do not redownload or retrain its weights. Do not reboot, change drivers, mounts or global VM settings, push commits, open a PR, publish private data, or use paid external compute/API services without separate authorization. Online research does not authorize uploading local prompts, traces or secrets. Downloads must have recorded origins, revisions and licenses; inspect code before executing it.

Local Git commits and separate worktrees are encouraged. All new code, comments, documentation, scripts and reports must be in English.

## 2. Evidence to inspect and the single reference configuration

Read the existing reports and follow their actual artifact references before doing new work:

- Latest three-way comparison: `/srv/ai/benchmarks/strata-qwen38/threeway-32k-128k-longdecode-20261004T212330Z/report.md`
- Same-main upstream/helper refresh: `/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/report.md`
- Earlier helper-priority experiment: `/srv/ai/benchmarks/strata-qwen38/pr578-dual4090/report.md`
- Locate the report titled `VM hardware and MoE residency data-movement study`, including its `cost-model.json`, `scheduler-envelope.json`, raw results and source. Discover its real location; do not invent one.

Inspect relevant configs, payloads/token IDs, manifests, analysis scripts and raw evidence, not only summary prose. Reuse the completed hardware measurements; do not repeat the entire microbenchmark campaign.

**Use one primary baseline: CURRENT layer split, K=25, explicit PCIe fraction 0.28.** The preserved v0.1.38 split and helper-priority are historical/architectural references, not two additional routine baselines. The normal experiment is CURRENT versus one candidate, at the same context limit.

Frozen CURRENT source: `6f32ec070f23ced9f50e704d854d775da52591ab`.
Preserved original binary SHA256: `871bb3b8ff217b6c53b517e3a5f77504e86c74877d6c717050e2034d3098840d`.

The recorded CURRENT source checkout later acquired a separate diagnostic commit. Do not confuse its current HEAD with the source of the preserved `strata-original` binary. Verify provenance; build new candidates and a clean control from the exact same frozen base in separate directories. If rebuilding changes the toolchain, remeasure the rebuilt control rather than attributing toolchain differences to your algorithm. Inspect upstream developments for ideas, but do not silently replace the baseline with latest main.

Reference model revision: `ed59f92082b1e93c0e96d60a8b11aab089b52f09`; existing pack: `/srv/ai/models/strata/packs/iq3_s`. Read exact paths and launch settings from the latest campaign's `configs/CURRENT.json` and manifests.

Historical CURRENT medians with 4096 output tokens were:

| Actual input | PP tok/s | TG tok/s | TTFT |
|---:|---:|---:|---:|
| approximately 31,407 | 4776.3 | 143.4 | 6.73 s |
| 127,028 | 5908.3 | 132.0 | 21.98 s |

These are historical orientation, **not mandatory target scores or fresh repetitions**. The old campaign used maximum context 262144. Establish the appropriately configured controls below before claiming new speedups.

Hardware reference: two RTX 4090 24 GiB, no NVLink and no direct CUDA P2P in the measured VM, 16 available vCPUs, approximately 161 GiB host RAM. The routed-expert arena is already preloaded in RAM. VRAM, not host RAM capacity, is the principal expert-residency budget here. Verify current availability without changing infrastructure.

## 3. Context limits and fair VRAM accounting

Only two production context profiles are in scope:

- `32k`: maximum total context **32768** tokens.
- `128k`: maximum total context **131072** tokens.

Total context includes the effective prompt, generated thinking/answer tokens, and any runtime-required reserve. Do not leave maximum context at 262144 while merely labeling requests 32K/128K. Do not benchmark 64K or 256K.

The main output budget is **4096 tokens**. Therefore historical inputs of approximately 31,407 or 127,028 do not fit unchanged with that output budget inside these limits. Prepare one reproducible payload family per profile, based on the saved repository-maintenance workloads. Use the real service tokenizer/chat rendering, budget output plus required speculative/special-token headroom, and verify admission before timing. With a 256-token additional reserve, example input ceilings are 28,416 and 126,720; determine the actual reserve from the runtime rather than assuming these are exact targets.

Trim/pad source material deterministically at documented boundaries and freeze the resulting text and effective token IDs. Do not truncate silently, change RoPE, shorten the output secretly or raise the context limit when a request does not fit. Reuse the same payloads for baseline and candidates. Short correctness/warmup inputs are allowed inside these two profiles.

First establish separate clean CURRENT controls at the two context limits. Keep K=25, PCIe fraction 0.28, MTP spec=4/min-p=0.5, INT8 KV, workers=15, prefill=auto, greedy temperature=0, suffix-draft=0, prompt-cache=0 and serial requests. Preserve `kv-resident=32768` where valid; document any mandatory compatibility adjustment and apply it equally.

Measure actual VRAM allocation, expert-cache bytes and slot-size classes after startup. A smaller context limit does **not guarantee** more cache slots, especially with capped/streamed KV. Do not assume a saving. Allow baseline auto-sizing to use the genuinely available budget, then freeze the measured per-context budgets for policy comparisons.

Candidate predictor state, scratch space, staging buffers and reservation costs must fit within the same total per-GPU resource envelope. Report any reduction in expert capacity. Distinguish practical same-total-memory comparisons from optional matched-expert-capacity diagnostics. Never call extra cache capacity a policy improvement, or count two disjoint 24 GiB memories as a freely accessible 48 GiB pool.

## 4. Persistent, separated research workspace

Create a new timestamped **local Git research repository** under a writable project/research directory. Record its absolute path immediately. Do not mix this work into an unrelated project or reuse an old benchmark directory.

Keep a root `GOAL.md` containing this full prompt, `README.md`, `STATUS.md`, `DECISIONS.md`, `experiments.jsonl` and `sources.json`. Keep reusable harness/analysis code versioned. Each experiment must have a stable ID and its own directory, for example `experiments/E007-jev-mlp/`.

Each experiment directory must preserve its hypothesis, protocol, configs, source revision/patches, build identity, dependency record, logs, raw outputs, traces/checkpoints when applicable, derived results and stage report. Never overwrite an earlier attempt with its repair. Use revision/attempt subdirectories and explain what changed.

Use separate source worktrees and build directories for clean control, diagnostics and each materially different runtime candidate. Do not share writable generated headers, mutable build outputs or an unpinned executable path between variants. Shared read-only weights and pinned dependencies are fine. Retain binaries needed to replay results, plus rebuild instructions and hashes.

**Do not leave research scripts only in `/tmp`, interactive shell history or ephemeral snippets.** Code that produced evidence must be saved in the repository before or immediately after use. Large raw data/builds may be Git-ignored but must remain on disk with manifests and stable links; do not commit model weights or secrets. Preserve local patches, dependency locks and fetched-source identities.

Every runnable variant must have executable launchers such as `start-32k.sh`, `start-128k.sh`, `benchmark-32k.sh`, `benchmark-128k.sh`, `reproduce.sh` and `stop.sh`, or equally clear equivalents. Freeze model/profile paths, binary, environment and parameters inside a versioned config loaded by the script. Print the resolved configuration at startup and verify hashes. No automatic rebuild/update during launch. Support safe explicit port overrides, detect collisions, and stop only owned processes. Give every variant a README containing copy-paste launch commands.

## 5. Research questions: do not assume the answer

Distinguish these possibilities:

**Policy/prediction headroom:** the same VRAM can hold a more useful time-varying expert set; current admission is slow, eviction is poor, or demand can be predicted early enough.

**Capacity tail:** even a well-informed policy cannot keep the needed working set resident under the same budget. However, all experts being needed eventually does not prove they must be resident simultaneously. Test temporal reuse and transfer feasibility before declaring a hard capacity limit.

**Execution/coordination limit:** boundary handoffs, mapped-host kernels, CPU/GPU synchronization, launch overhead, KV traffic or already-resident computation may dominate instead of cache misses.

**Placement/scheduling headroom:** a different distribution of expert storage or work across the two GPUs might reduce exposed latency. Expert parallelism is distinct from contiguous layer split; neither utilization percentages nor moving work alone establish a benefit.

Audit counter definitions in the source. The reported approximately 98.5–99% hit rate is not automatically the fraction of all expert demand served from local VRAM. Previous reports identify nonhits with CPU-fallback entries and report mapped-PCIe/helper work separately. Establish denominators and disjoint categories before modeling the tail.

Approximately 50% utilization on each GPU is not proof of 2× unused single-request performance. Likewise, 90% utilization does not imply a maximum 10% remaining speedup. Measure execution dependencies. Do not attribute the entire GPU-reach wait to misses or the GPU boundary, add overlapping timers as if disjoint, or substitute the small-message hardware round trip for actual runtime handoff latency.

## 6. Literature and the complete candidate tree, including Open-Jev

Review these primary sources and record pinned revisions/URLs and what you actually reused:

- Open-Jev: https://github.com/Zefan-Cai/Open-Jev
- Project background: https://zefan-cai.github.io/open-jev/story/
- Observed Open-Jev source snapshot: `bd4118882f733574a3250a4b65fe4d884130c08b`; inspect `README.md`, `jev/model.py`, and relevant scoring/training/calibration code. If using another revision, record it.
- Fate, cross-layer gate prediction: https://arxiv.org/abs/2502.12224
- SpecMD / Least-Stale: https://arxiv.org/abs/2602.03921

The intended reference is **Zefan-Cai/Open-Jev**, not a similarly named developer tool or a different repository. It is an independent Jev-inspired decision model, not a ready-made Strata cache predictor. Its relevant pattern is scoring explicit candidates without autoregressive answer generation; its implementation includes a scalar decision head and calibration. Do not claim access to proprietary Jev methods or transfer its published decision-task performance to expert prediction.

Our **Expert-Jev-inspired** branch is a new small local scorer trained on measured expert demand, not automatically the released Open-Jev language backbone placed alongside IQ3_S. Explicitly investigate a linear scorer and a small MLP; consider a temporal variant when the evidence supports it. Do not silently drop this branch in favor of only LRU/EMA. Even when runtime integration is unjustified, preserve a bounded replay evaluation or a specific, evidenced blocker.

Maintain a candidate ledger covering:

1. Existing Strata policy, frozen static profile, simple recency/frequency policies and EMA/decayed heat.
2. Least-Stale as actually specified in its source, with any adaptation clearly labeled.
3. Markov/transition/co-occurrence predictors.
4. Expert-Jev-inspired linear, MLP and potentially temporal scorers.
5. Fate-inspired cross-layer/router lookahead and MTP-derived signals.
6. Hybrids combining cheap history with learned or router-derived information.
7. Budget-aware placement, asynchronous promotion and, where justified, cross-GPU expert scheduling.

This is a research tree, not a compulsory large grid of runtime builds. Give each branch a documented disposition. Complete bounded experiments rather than abandoning them because one initial metric is worse. Follow useful new ideas from the literature/source, but record why they address the objective and what established comparison they replace.

## 7. Measure demand and the actual critical path

Inspect layer ownership, routing, CPU fallback, mapped-host execution, cache adaptation, variable expert sizes, prefill/decode, speculative verification, dense operations and KV movement in the actual source.

Obtain lightweight diagnostic traces linking `(request, window, token/branch, layer, expert)` to demand time, expert byte size, residency/placement, selected execution path, admissions/evictions, transfer issue/completion and execution dependencies where observable. Include work performed for rejected MTP drafts, not only accepted output tokens. Record when each predictor input first becomes available; true later-layer router results cannot be used before their computation.

Prioritize identifying exposed waits over collecting every possible counter. Separate GPU-boundary activation transfers, expert promotions, mapped-host reads and KV movement. Use events/ranges or another defensible timing method; respect distinct CPU/GPU clock domains. If a profiler is unavailable without root, use source-level buffered traces and carefully scoped timing. Avoid global synchronization per event.

Keep diagnostic builds/runs separate from clean headline measurements. Measure or bound instrumentation effects; incomplete evidence is not zero overhead. Validate counters against small known cases. Do not infer per-token rates or burst causes from 1 Hz telemetry alone.

Reuse the two benchmark payload families, but collect additional bounded, independent task traces for predictor development and holdout evaluation. Only the same two context profiles are allowed. Different nonces in the same document are not independent tasks. Record whether any diagnosis is limited to the repository-maintenance workload.

## 8. Replay, capacity tail and attainable headroom

Build a deterministic, byte-aware trace replay and first check that replay of the existing policy reproduces observed routing/cache accounting sufficiently well. Investigate discrepancies before trusting candidate projections.

Separate resident-set selection, admission/eviction, prediction and scheduling. Model per-GPU budgets, actual slot/size constraints, immutable host backing, transfer queues/completion, in-flight reservations, eviction victims, compulsory loads and predictor information timing.

Use two clearly distinguished future-aware references where feasible:

- An optimistic capacity-only reference with timing assumptions explicitly relaxed.
- A transfer-aware feasible future-informed schedule using measured costs and the same capacities.

A heuristic future-aware schedule is not a proven optimum or upper bound. A weak heuristic failing to improve does not close the research direction. If using a solver, record feasible objective and bound/gap. Equal-size textbook replacement results are not automatically optimal with variable bytes, transfer costs and deadlines.

Report miss/byte reduction separately from projected latency. A miss matters only to the extent that its cost is exposed rather than overlapped. Use the hardware cost models within measured ranges, with sensitivity analysis where runtime costs are uncertain. Validate important assumptions against actual inference. Never subtract all miss time or add CPU/GPU waits indiscriminately.

Test whether exchanges help despite full VRAM: useful lifetime, repeated expensive misses, victim reuse, per-layer budget imbalance, tail churn and promotions ready before demand. Moving experts between full GPUs does not create capacity unless duplication/other allocations actually change. A favorable offline schedule is not a measured TG gain.

## 9. Learned scoring and its real cost

For Expert-Jev-inspired methods, define an explicit target such as probability of use within a horizon, expected near-future use count, or estimated latency-saving utility. Features should primarily be cheap routing/history/cache state: layer/expert IDs, recency, decayed counts, co-occurrence, recent misses and legitimately available model signals.

Many experts can be needed within a horizon. Do not treat a softmax over all experts as independent probabilities that each will be used. Use appropriate multilabel/count/ranking objectives and explain calibration semantics. A ranking score need not pretend to be calibrated probability.

Train/evaluate with whole-task/document/episode separation and causal temporal boundaries. Overlapping windows or repeated benchmark prompts must not leak future labels into the test split. Fit preprocessing/calibration only on permitted splits. Declare whether online updates are causal. Save datasets or reconstructible manifests, seeds, splits, model checkpoints and training/evaluation scripts.

Compare learned scores against cheap baselines at the same capacity and transfer budget. Include feature extraction, state updates, scoring, selection, model memory and CPU/GPU contention in the budget. Prefer batched local numeric inference and infrequent updates when sufficient. A cheap drift monitor plus occasional heavier planner is a valid hypothesis, not a required design.

Do not put a multi-billion-parameter decision model or network call on every token's critical path by default. Auxiliary checkpoints may be investigated offline when justified, but a deployable candidate must pay its actual cost on the same two GPUs/VM. Training may use the GPUs between benchmark runs, never concurrently with clean measurements. Explore cheaper representations or scheduling before declaring the learned branch impractical.

## 10. Runtime experiments and architectural freedom

Implement minimal, reversible candidates when evidence makes a test worthwhile. Prefer a small shared policy interface so multiple scorers can use the same cache/scheduler backend. First preserve K=25/layer split; later examine placement/split interactions if supported by evidence. Do not repeat the entire old three-way campaign.

The core correctness invariant is **the model's actual router still selects the experts**. Prediction changes residency/readiness, not which experts mathematically execute. Wrong predictions must fall back safely. Do not silently skip experts, substitute resident experts, change routing weights/top-k, quantization or accuracy to increase TG.

Handle asynchronous slot publication only after copy completion, expert identity/generation validation, in-flight readers, eviction races, duplicate promotions, cancellation and speculative rollback. Clean eviction of immutable weights need not copy them back to RAM. Prediction must not monopolize the critical path with speculative transfers or unlimited churn.

Count buffers and predictor memory. Reuse staging when safe; enforce per-device capacity. Do not infer a universally safe transfer rate from peak PCIe bandwidth. Explore coarse achieved-rate/admission budgets and measure interference.

Cross-GPU/expert-parallel or hybrid ideas are allowed when locality/scheduling evidence justifies them, not only after a supposed oracle failure. Explicitly charge activation/result transfers, host staging, synchronization, dense-path changes and lost expert capacity. Check actual runtime support before combining flags. Do not assume P2P or simultaneous execution of dependent layers.

If an idea is initially slower, complete its declared bounded experiment, verify correctness/provenance and diagnose prediction, transfer, capacity and synchronization costs. Preserve it, including usable launchers. Repair in a new version and compare fairly. Never keep unsafe/corrupt execution running merely to finish a speed table.

## 11. Experimental discipline and the three-repetition limit

Use a funnel: source/trace diagnosis, inexpensive replay, bounded runtime screening, then full baseline/candidate confirmation in both context profiles. Avoid building a universal framework before testing the core mechanism.

**Never exceed three measured repetitions of the same unchanged benchmark point.** A point includes binary/config, context, payload family and warmup policy. Cheap screening can use fewer, clearly labeled exploratory. Final claims should use three valid runs where obtainable. Do not create renamed batches to collect extra repetitions of an unchanged point.

Keep every failed/early-ending attempt. If a three-attempt batch has fewer than three valid runs, mark it incomplete; do not run indefinitely to manufacture a median. A genuine harness/implementation correction or a shared workload replacement can create a new versioned experiment with its own predeclared bounded batch. Explain the change and retain the original failure. Do not retry because a valid measurement is inconveniently slow.

Predeclare warmup/restart policy and run order. Prefer at most three paired baseline/candidate replicates, each with an equivalent fresh start and the same short fixed warmup, when this is practical. Alternatively reproduce the earlier serial-three policy on both sides and explicitly distinguish cache history. Do not mix the two policies within a comparison. Reuse compatible controls; rerun only when conditions actually changed.

Use fixed 4096-output workloads for headline comparisons. Preserve natural EOS/tool termination as valid application behavior but incomplete fixed-length measurements. Do not disable EOS silently. A common-prefix analysis is diagnostic, not equivalent to a complete fixed-output benchmark. No automatic 16K extension.

Keep sampling, MTP, suffix/reuse, prompt IDs, output budget, workers and context identical within each A/B. Freeze a small development/confirmation suite before selecting a winner. Complete the predeclared confirmation on both profiles even if one profile looks unfavorable, unless correctness, safety or deadline prevents it; report that limitation.

**No 1% sweeps, adjacent-value scans or large Cartesian grids.** Use a few meaningfully separated values, trace-informed choices and coarse-to-fine refinement only when justified. Deterministic replay needs one execution, not three identical repetitions. Do not benchmark all permutations of every policy.

## 12. Metrics, correctness and interpretation

For each measured request retain actual input/output IDs or hashes, PP, TG, TTFT, end-to-end wall time, finish reason, MTP proposed/accepted and accepted-per-window, memory and clean command/binary identity. Distinguish generated reasoning tokens from a completed usable answer; a reasoning-only limit hit is not an application success.

Collect explanatory metrics at a justified cost: local/remote/mapped/CPU demand with denominators, promotion bytes and readiness, useful versus unused promotions, late predictions, eviction damage, churn, predictor/selector latency, per-GPU resource costs, and exposed waits. Save interval throughput with timing resolution/uncertainty. Unknown values remain unavailable, never zero.

Run relevant existing tests plus targeted async/cache tests and a short greedy battery covering code, math, prose and structured output before accepting a runtime candidate. Investigate numerical divergence; some routing/execution-order changes affect free generation, but not every difference is harmless. Where feasible use fixed-input logits or a small teacher-forced diagnostic. Do not fabricate KL/top-1 parity, and do not use an LLM judge as a substitute for numerical/runtime checks.

Free-generation speed includes output-trajectory and MTP effects. Record these and separate them from fixed-trace/kernel diagnostics. Fixed-trace replay also has limits when a policy changes numerical trajectories; validate the conclusion in live inference.

No background builds, training, heavy analysis, hashing or other campaigns during headline measurements. Use lightweight telemetry; no per-second PSS. Three runs do not establish tiny universal speedups or robust tail guarantees. Preserve outliers, report paired results and median/min/max, and do not sum or multiply unrelated medians into a claimed measured quantity.

## 13. Finish each stage, repair failures and use the remaining time

Before each experiment write its question, expected mechanism, changed variables, finite workload, budget, validity rules and completion criteria. After it, write observations, failures, interpretation, unresolved questions and the next decision. Update the root status/ledger after each meaningful stage so progress survives interruption.

Use explicit states such as PLANNED, RUNNING, COMPLETE_POSITIVE, COMPLETE_NEGATIVE, INVALID_PROTOCOL, BLOCKED, INCOMPLETE_DEADLINE and NOT_ATTEMPTED. A poor number is not grounds for deleting an experiment or skipping its analysis. Safety/correctness/time stops are legitimate but must not be mislabeled as completed negative research.

Diagnose build failures, missing libraries, unsupported tools, incorrect token budgets, API differences, telemetry problems, OOM, races and unexpected serialization. Use user-space alternatives, smaller staging, different instrumentation or a minimal reproducer as appropriate. Bound each repair attempt, then pursue another useful branch rather than getting trapped. Preserve both the failed and repaired versions.

Use the 10-hour budget adaptively. Inspect evidence and establish controls early; do not spend half the session rewriting tooling. Complete the inexpensive policy/learned-scorer comparisons, obtain at least one meaningful runtime experiment where feasible, and leave time for validation. If the core plan finishes early, explore the best evidence-backed idea or investigate a negative result, not more repetitions or cosmetic tuning.

Write reports incrementally. At the hard deadline, stop owned experiments, preserve partial results/checkpoints and issue the final report. Never extend the goal silently.

## 14. Required final deliverables

Deliver the research repository path, a root `report.md`, `summary.json`, `summary.csv`, the complete experiment ledger, source/dependency provenance, and a launch index. Every headline number must trace to preserved raw records and reproducible analysis code. Distinguish measured results, simulations, hypotheses and untested proposals.

The report must explain:

- The fresh 32K/128K baseline and whether smaller context limits actually released VRAM for experts.
- The meaning of hit/miss counters and evidence separating capacity tail, prediction/admission problems, communication, resident compute and synchronization.
- Oracle/reference assumptions, bounds or heuristic limitations, and reachable rather than free-transfer headroom.
- Results/status for every candidate family, explicitly including Expert-Jev-inspired linear/MLP and the temporal branch disposition.
- Which predictions arrived early enough; useful/wasted promotion bytes, victim cost, predictor overhead and net latency consequences.
- Baseline versus each confirmed candidate at both contexts: exact resource budgets, PP/TG/TTFT/wall time, valid/invalid counts, MTP and correctness caveats.
- Every failed or slower completed experiment, repairs attempted, retained artifacts and why it was not selected.
- Whether a workload-specific tradeoff or cross-GPU approach deserves further work, without reviving historical numbers as fresh A/B.
- Remaining uncertainty, strongest next experiment, total elapsed time and reasons for any incomplete branch.

Include a reproducibility table: experiment ID, source/patch/checkpoint/config, build path, status, and exact 32K/128K start, stop and reproduce commands. Test each runnable variant's launcher at least once during its normal smoke/benchmark flow. Do not advertise broken variants as ready; preserve their diagnostic reproducer instead.

Finish with one primary recommendation:

- `USE_BEST_CANDIDATE`
- `KEEP_CURRENT_LAYER_SPLIT`
- `WORKLOAD_DEPENDENT`
- `PROMISING_NEEDS_MORE_WORK`
- `INCONCLUSIVE`

Support it with the completed evidence, not the desire for a positive result. Keep all experimental variants available for later inspection/replay. No deployment or switch of the user's normal launcher without separate approval. At completion, stop your servers/training workers and verify the two GPUs are free of your processes; do not kill unrelated work.

**Research standard:** investigate the mechanism, not just the scoreboard. Try to falsify surprising gains and explain surprising losses. Complete and preserve finite experiments, repair genuine mistakes, and use new evidence to choose the next branch. The result should be both a defensible performance conclusion and a reusable laboratory for the next iteration.