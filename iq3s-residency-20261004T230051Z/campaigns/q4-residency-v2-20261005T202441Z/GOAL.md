# Goal: Q4 Residency v2 — joint expert admission, eviction and causal prefetch

Act as an autonomous systems/ML performance researcher. Execute this investigation in the existing Strata laboratory; do not stop at a proposal.

Improve **Qwen3.8-Flash-Next UD-Q4_K_XL** inference by choosing which experts occupy a fixed VRAM budget, predicting their future value, selecting safe eviction victims, and making useful promotions ready in time. The objective is lower end-to-end request latency and/or higher decode throughput, not a higher hit-rate counter alone.

Use three sequential phases:

1. **Phase A — establish trustworthy Q4 traces, costs and achievable headroom.**
2. **Phase B — compare causal policies, including Expert-Jev-inspired scoring, with joint admission/victim selection.**
3. **Phase C — implement and validate the strongest viable candidates in live inference.**

The pool-spin study is already complete. Do not repeat it or the helper comparison.

## 1. Time, autonomy and stopping

**Hard maximum: 10 hours elapsed wall time**, including inspection, downloads, builds, training, tests, analysis, reports and cleanup. Record start time and the absolute deadline immediately. Preserve them across context compaction/resumption. The deadline does not reset when a subprocess or experiment restarts.

At **T+9h15m**, stop starting substantial new experiments. Reserve the last 45 minutes for consolidation, runnable launchers, audit and cleanup. Finish earlier when the bounded investigation has answered its questions; do not add work merely to fill ten hours. Conversely, one failed implementation or weak initial predictor is not grounds to end the whole investigation.

Suggested allocation, not a rigid timetable: roughly two hours for A, two to three for B, the remainder for C and reporting. Reuse existing infrastructure rather than spending most of the budget rebuilding it. A useful new idea may replace a less informative planned branch; document the decision.

You may research online, inspect papers/source, clone repositories, download justified dependencies or auxiliary checkpoints, compile tools, install packages into isolated user environments, train small predictors and modify experimental code. **No sudo is available.** Find user-space alternatives to missing tools; do not bypass permission boundaries.

Keep all new code, comments, documentation and reports in English. Do not use paid APIs/compute or upload private prompts, traces or credentials. Do not push, open PRs, change drivers/global host configuration, reboot, modify Qwen weights/quantization, or replace normal user launchers. Never kill unrelated processes to make the machine idle.

## 2. Frozen Q4 baseline and evidence

Research root:

`/srv/ai/research/iq3s-residency-20261004T230051Z/`

Mandatory starting sources:

- `campaigns/q4-pool-spin-20261005T184831Z/`: latest selected Q4 pool policy; read `report.md`, summaries, configs, launchers and provenance.
- `campaigns/q4-multigpu-20261005T164628Z/`: completed Q4 layer-split/original-helper/optimized-helper comparison, including 256K payloads/configs.
- Prior IQ3_S reports and E028/E029 persistent-residency experiments. Locate archived reports through the existing ledger; do not assume the mutable root report still describes the earlier campaign.
- Prior replay/router/coordination experiments, especially E004, E005, E015, E017, E018 and E020.
- The existing `VM hardware and MoE residency data-movement study`, its cost model, scheduler envelope and measurement code. Locate its actual paths from local records.

Read relevant raw data and source, not only conclusions. Missing artifacts must be reported and reconstructed only where justified; a summary is not a substitute for unavailable raw traces.

### Baseline to preserve

- Model: **UD-Q4_K_XL**, using the already installed Q4 files and their recorded profile/PLE/MTP dependencies.
- Runtime: frozen **Strata 0.1.39/P1**, not the old 0.1.32 installation.
- Two RTX 4090 24 GiB, `CUDA_VISIBLE_DEVICES=0,1`.
- Layer split **K=24**; PCIe fraction **0.28**.
- **`STRATA_POOL_SPIN_US=100`**, 15 pool workers.
- MTP spec=4, spec-min-p=0.5; INT8 KV; kv-resident=32768 where valid.
- Prefill=auto; suffix lookup OFF; prompt reuse/cache OFF; greedy; one request at a time.

Expected executable:

`/srv/ai/research/iq3s-residency-20261004T230051Z/builds/control/strata`

Expected SHA256:

`eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d`

Expected source:

`6f32ec070f23ced9f50e704d854d775da52591ab`

Verify these against the Q4 campaign. Inspect the actual running native child process, not only the Python frontend or shell script. Record executable, command, relevant environment, frontend revision, config, model identity and effective runtime settings. Audit inherited experiment flags. Fail visibly on an unexpected binary/model instead of silently falling back to another installation.

**Do not copy the IQ3_S model revision, expert profile or pack paths into the Q4 config.** Verify Q4-specific provenance. Separate worktrees/builds are allowed for candidates; baseline and candidates must share the same frozen source ancestry and compatible build settings. No automatic update during startup.

The latest pool-spin summary selected 100 us as the practical baseline: 500 us was nominally faster but below the predeclared 3% materiality threshold and used substantially more CPU. This was not proof of statistical equivalence or a universal optimum. Do not retune it here.

Historical orientation from that study:

| Total limit | Actual input | PP | TG | TTFT | Wall | Decode CPU |
|---:|---:|---:|---:|---:|---:|---:|
| 32768 | 28378–28381 | 1852.4 | 97.0 | 15.47 s | 57.74 s | 48.8% |
| 131072 | 126715–126719 | 2075.2 | 80.2 | 61.61 s | 112.77 s | 48.4% |

These are not performance targets. The earlier multi-GPU campaign reported different PP/TG, including approximately 87.8 TG at 256K. Inspect restart/warmup history, payloads, graph capture, timing definitions and configs before comparing campaigns. Do not diagnose a regression from different headline medians alone.

## 3. Contexts, workloads and memory fairness

Test **32768, 131072 and 262144 total context limits**. These include input, output and required runtime reserve. No 64K profile, hidden context enlargement, new RoPE scaling or reduced output budget.

Primary confirmations use **4096 output tokens**. Reuse the pool study's actual 32K/128K input families and the multi-GPU study's approximately 257783-token 256K input where compatible. Verify rendered token IDs and the exact reserve with the real tokenizer. Preserve identical input IDs within each paired comparison.

100 us was selected in the latest study at 32K/128K. For 256K, carry it forward as the fixed campaign setting and measure its baseline; do not claim a separate 256K spin optimum was established.

Read actual Q4 per-device expert bytes, slot-size classes, dense/MTP/KV/scratch allocations and free-memory reserve. Approximately 11.4K experts resident is orientation, not an allocation rule. Record the exact values for every profile.

No added GPU memory is allowed. Predictor buffers, gate copies, staging and reservations must fit in the same total resource envelope. Charge any reduction in expert capacity. Distinguish same-total-memory practical comparisons from matched-capacity mechanism diagnostics. Two GPUs are not a freely accessible 48 GiB pool. Keep K and PCIe fraction frozen.

Auxiliary learned/semantic predictors must run **CPU-only during live inference**. Reusing Qwen's existing router on its GPU is a separate, explicitly measured mechanism, not permission to load Basal/Open-Jev onto the serving GPUs. Offline training may use a GPU only between clean measurements, with its memory/processes released afterward.

## 4. Lessons from the IQ3_S failure: mandatory starting knowledge

Prior persistent residency was implemented and ran; it was not merely a simulation. However, it lowered decode TG by about 4–5%. Many promoted experts were subsequently used repeatedly, while CPU/mapped demand and damage from evicted experts increased.

Only roughly 8% of admissions in the diagnostic samples had a recorded router prediction; most were reactive. Many predicted experts had already missed before enqueue. Copies issued at the safe end-of-verify boundary could not satisfy the earlier current-window demand. Readiness measured at the first later use did not mean successful prefetch before the original target deadline.

Therefore this investigation must answer both:

- **Is the incoming expert worth more than the resident expert or victim set displaced?**
- **Can the promotion complete before the particular demand we intended to accelerate?**

Q4's different slot sizes and lower residency justify reconsidering algorithm families, but not copying old scores, checkpoints, thresholds or timing assumptions. Do not assume its approximately 10% nonlocal demand represents 10% of execution time, or that approximately 50% CPU is entirely useful computation.

# PHASE A — Q4 ground truth, cost attribution and headroom

## A1. Establish controls and diagnostic traces

Use preserved artifacts where compatible and collect only the missing Q4 evidence. Establish clean controls for the chosen fresh-start protocol at all three limits. Baseline probes used for a completed comparison must not be repeated indefinitely.

Inspect the real Q4 expert loader/kernels and cache implementation. Do not assume IQ3_S-specific layouts or CPU kernels apply. Trace demand including rejected speculative work, not just emitted tokens.

Useful fields include request/window/layer/expert, byte size and owner GPU; resident/mapped/CPU path; demand timestamp; prediction availability; admissions and actual victims; enqueue/completion/publication; in-flight slot generation; future reuse and eviction. Preserve initial heat/residency and warmup state. Sample only if the estimator and its limitations are explicit.

The all-demand denominator must include local, CPU and mapped/remote routed entries. Keep unique jobs, token/expert entries, bytes and logical file reads separate. Displayed UI hit rate may have a different denominator. Inspect every counter used in conclusions.

Separate diagnostic builds from clean speed measurements. Buffer traces, avoid synchronous logging per event and do not add a global device synchronization to every layer. Source-level events are acceptable when a profiler is unavailable. Respect distinct clock domains and distinguish observed publication from exact copy completion.

Measure representative **exposed** costs: CPU-positive wait, mapped execution, resident computation, H2D staging/copies, publication/join and boundary handoff. Do not add overlapping timers, multiply a few selected-layer medians by all layers, or interpret GPU utilization as FLOPS utilization. Reuse existing hardware envelopes but validate Q4-sized contended transfers; peak isolated bandwidth is not an inference budget.

## A2. Validate replay before comparing policies

Adapt the existing replay to Q4. Replay the current policy first and reconcile demand, admissions, byte budgets and residency evolution against the recorded run. Report mismatches rather than trusting a simulator with the wrong baseline.

Model actual per-GPU slot classes, queue order/readiness, in-flight reservations, victim withdrawal, delayed publication and startup state. Remaining resident experts and copy sources must not disappear from accounting. Joint replacement of several smaller victims, if proposed, is a real allocator change: charge its implementation and fragmentation, not just the byte sum.

Use two distinct future-informed references where feasible:

1. **Capacity-only optimistic reference:** timing restrictions explicitly relaxed.
2. **Transfer-aware feasible future-informed schedule:** same capacities with queue, copy and readiness constraints, evaluated across measured plausible transfer costs.

A heuristic is not a proven optimum or upper bound. A weak heuristic's failure is not evidence that no useful policy exists. If using an optimizer, report feasible value and bound/gap. Do not treat zero-cost clairvoyance as a deployable predictor or offline miss elimination as measured TG.

Quantify temporal reuse, capacity pressure, churn, victim demand and potentially avoidable exposed latency. The useful working set can exceed VRAM over time without needing simultaneous residency, but the replacements still cost time and bandwidth.

## A3. Phase decision

Write a Phase A report distinguishing placement opportunity, prediction/readiness opportunity and irreducible or unmeasured costs. Do not use arbitrary miss-rate thresholds such as “oracle must reach 99%” to decide whether research is worthwhile. A smaller reduction in expensive exposed misses can matter more than a larger reduction in overlapped work.

Proceed to Phase B whenever meaningful headroom remains plausible. If evidence suggests little headroom, validate the reference and cost assumptions before closing live implementation. A negative scheduling heuristic alone cannot justify skipping the entire learned/causal investigation.

# PHASE B — causal policy competition and joint transaction scoring

## B1. Candidate families

Evaluate bounded representatives in the shared replay/harness, not a Cartesian product of every possibility. Give each family an explicit status and retained result. Q4 is new evidence for revisiting these families.

| Family | What to test |
|---|---|
| Current/static | Current adaptive behavior and an unchanged development-only profile reference |
| Cheap history | Recency, frequency/EMA and a clearly identified stale-based policy |
| Transitions | Markov/co-occurrence or a compact history-conditioned scorer |
| Router/MTP | Causal lookahead at a few justified horizons such as H1/H4/H8, plus available speculative signals |
| **Expert-Jev-inspired** | Linear and small MLP joint-utility scorers; one bounded temporal extension when justified |
| Hybrid | Router or learned information combined with cheap history, victim protection and transfer budget |
| Basal semantic prior | Optional bounded CPU-only evaluation when semantic information may add value beyond routing history |

**Expert-Jev is a required research branch, not a forgotten optional name.** Train/evaluate at least a meaningful linear and small MLP candidate unless a concrete documented data/tool/headroom blocker prevents it. Do not conclude that learned scoring is impossible because the earlier 16-unit IQ3_S scorer failed. Inspect data coverage, targets, learning curves and inference cost before increasing complexity.

Primary design references to inspect and pin:

- `https://github.com/Zefan-Cai/Open-Jev`
- `https://github.com/rkinas/basal`
- Fate: `https://arxiv.org/abs/2502.12224`
- SpecMD / Least-Stale: `https://arxiv.org/abs/2602.03921`

Use locally preserved pinned sources first. Verify exact algorithms/names against primary material before claiming an implementation. Open-Jev and Basal are decision-model references, not ready-made predictors of this Qwen's expert IDs. Record code borrowed and licenses. A locally trained tiny scorer must be labeled Expert-Jev-inspired, not the published Jev model.

For Basal, a semantic/domain prior must be mapped to Q4 demand using actual traces. Polish-language ability is not proof of expert prediction. Measure CPU latency and contention; do not assume shared-state scoring is supported equally by every CPU backend. Do not spend the campaign downloading a large semantic model without a bounded hypothesis.

## B2. Score both sides, not just probability of use

Define a causal, horizon-specific **net replacement benefit**, for example:

`delta_utility(action) = E[request time without action - request time with action | information available now] - predictor/selection overhead`

This is a target definition, not permission to fabricate a latency oracle. An implementable approximation must account for incoming reuse, victim reuse, CPU/mapped fallback alternatives, exposed transfer/readiness costs and churn. Avoid counting the same victim penalty or copy cost twice. Express which quantities are measured, estimated or unavailable.

Prediction targets may include expected demand count, time-to-next-use, reuse before eviction and conditional victim loss. Multiple experts may be useful simultaneously: use appropriate count/multilabel/ranking targets, not a global softmax interpreted as independent use probabilities. Raw gate confidence is not calibrated future-demand probability.

Keep the current placement unless an exchange has sufficient predicted net benefit. Investigate hysteresis, protected hot residents, bounded probationary residency or reserved admission budget where supported. Any reserve reduces available resident capacity and must be charged. Persistent admission means retaining useful experts, not automatic immediate restoration or indefinite pinning.

Use one state encoding to score many resident/incoming candidates where practical. Prefer cheap numeric features and a low-frequency planner plus inexpensive drift monitor. Drift triggers should consider all-demand misses and cost, not an ambiguous UI hit-rate decline alone. Test whether additional semantic features actually improve held-out net benefit.

## B3. Causality, coverage and honest readiness

Distinguish lookahead measured in layers from windows, tokens and microseconds. Record both signal time and the target demand deadline. Future-layer true router outputs cannot become available before that computation. MTP signals can be used only once produced; later accept/reject decisions cannot leak backward.

Count separately prediction-driven, reactive and profile-driven admissions. Report covered layers and demand fraction. A five-layer pilot cannot claim whole-model prediction quality.

Separate target-ready hits, late-for-target but useful-later admissions, never-used copies, harmful victim misses and pending/cancelled transfers. Track prediction-to-enqueue and enqueue-to-completion/publication independently. A copy issued after its target executed is not a successful early prefetch even if reused next window.

Use matched diagnostic ablations: common scheduler with prediction disabled versus enabled, and a reactive utility policy versus its predictive extension. This should reveal whether a gain comes from prediction, improved eviction or simply altered admission frequency.

## B4. Training and cost controls

Use independent task/document/episode splits for development, calibration and holdout. Nonces or neighboring windows from one repository document are not independent tasks. Fit normalization, calibration and hyperparameters without holdout leakage. Mark right-censored future-use labels near trace ends rather than calling them nonuse.

Reuse available code/math/prose tasks; add a small reproducible independent Q4 trace set if necessary. Record coverage limitations. Do not claim translation/Polish benefits without corresponding held-out data. Save datasets/manifests, seeds, splits, checkpoints and training/evaluation scripts.

Online scoring is CPU-only. Start with a modest additional CPU budget; approximately 1–10% of VM CPU is a design range, not free capacity or a latency guarantee. Measure feature extraction, GPU-to-CPU reads if needed, scoring, selection, memory, thread contention and shared RAM traffic. Use a bounded queue; inference must never wait indefinitely for the predictor. Stale plans may be skipped safely.

Select at most **two runtime finalists**, preferably one strong cheap policy and one learned/router/hybrid policy when both justify integration. Train/test a few meaningful alternatives, not progressively larger models until one overfits the benchmark. Preserve all bounded negative results and write the Phase B decision before final testing.

# PHASE C — runtime implementation, correctness and controlled confirmation

## C1. Implement minimally and safely

Use separate source worktrees/build directories. Reuse the existing safe cache machinery where possible, but fix the documented late-admission and victim-value weaknesses instead of renaming the old policy.

Initially preserve same-device layer ownership and K=24. Asynchronous RAM-to-VRAM promotion is permitted; arbitrary cross-GPU expert execution is not required. A narrow alternate-placement idea may be investigated only with explicit transfer/ownership/capacity accounting and enough time for safety checks. Do not reopen the broad helper matrix.

Earlier promotion is valuable only if safe. Audit stream/event dependencies, native driver calls, graph capture and CPU-produced PLE dependencies. Do not insert blocking CUDA API work into a path where an active GPU graph is waiting for that same host thread. Prove the required ordering with a minimal test before running a long request.

Protect in-flight readers, shared routed IDs, slot ownership/generation, variable blob bounds, source lifetime, duplicate promotions and publication-after-completion. Handle cancellation, pending work at request end, prefill borrowing, the next request and shutdown. Prediction changes storage/readiness only: no skipped/substituted experts, changed top-k, approximate weights or silent routing changes.

Give candidates an OFF mode. Validate it against the original Q4 control. A same-binary OFF/ON guard isolates the feature better than two unrelated executables, but also charge disabled-code/buffer overhead against the original frozen control. Do not artificially shrink the practical baseline to make the candidate look favorable.

## C2. Correctness before speed claims

Run relevant existing tests plus targeted Q4 byte/layout/kernel and async ownership tests. Include deliberately wrong predictions, delayed producers/copies, all-local and mixed/CPU-heavy bursts, repeated slot reuse and shutdown/cancellation. Read back sampled promoted experts to verify exact backing weights in diagnostic runs.

Use paired short code/math/prose/structured prompts and available fixed-input numeric diagnostics. Some free-generation divergence can follow legitimate CPU/GPU summation differences; do not automatically classify every difference as harmless. Localize suspicious first divergences and preserve input/output IDs, MTP and routing.

Bit-identical output is expected for an OFF control or a pure scheduling-only change when arithmetic is unchanged. Do not fabricate KL/top-1 metrics without a valid logits harness. No LLM judge substitutes for runtime/numeric validation. Preserve and label missing-fixture/environment failures instead of reporting a falsely green suite.

## C3. Benchmark funnel and repetition limit

Start with diagnostic/replay checks, then bounded 32K runtime screening. Diagnose a slowdown before rejecting the mechanism. Complete each predeclared finite protocol, including analysis; correctness/safety/deadline stops are allowed and must be labeled.

For a viable finalist, complete baseline/candidate confirmation at **32K, 128K and 256K**, with a frozen 4096-output protocol and matching input IDs. Use three paired fresh-start replicates per point, fixed equal warmup and a predeclared interleaved/counterbalanced order. Record actual cache state and graph-capture readiness. Do not compare warmed serial candidates with cold controls.

**At most three measured attempts per unchanged point in this campaign.** Count screening measurements if they use that exact protocol. Deterministic replay needs one execution. No extra runs after an unfavorable result, no dense 1% scans, no large grids. Invalid attempts remain invalid; do not hide them or retry indefinitely. A real code/protocol repair gets a new version and explanation, not merely a renamed batch.

With one finalist, the basic paired matrix is 18 requests; OFF guards and an independent held-out confirmation may add clearly justified cells. Do not duplicate compatible controls unnecessarily. Support a general recommendation with at least one independent task family where feasible; otherwise limit the claim to the measured workload. If no candidate is safe/promising enough for live testing, report why rather than inventing a runtime win.

Natural EOS/tool termination is retained as application behavior but does not satisfy fixed-4096 throughput. Report incomplete cells and application latency separately. Do not force favorable continuation or change prompts only for one arm.

No concurrent builds, training, profiling, heavy hashing or unrelated GPU tests during headline measurement. Bound all subprocesses, show progress markers and use owned-PID cleanup. A process that hangs must time out with evidence; no unbounded shell/browser/benchmark commands.

## C4. Measure and decide

For every run retain PP, TG, TTFT, wall time, actual input/output, finish reason, MTP proposed/accepted/windows, output hashes and effective settings. Distinguish total generated tokens from a completed usable answer.

Report all-routed local/CPU/mapped shares and counts; promotions/bytes; useful, late, unused and pending admissions; victim damage; queue/publication waits; predictor cost; RAM/VRAM and per-GPU telemetry. Unknown counters are unavailable, not zero. One-Hz PCIe samples do not identify expert-transfer events.

Separate cumulative/interval speed, median cell values and median paired ratios. Three runs do not establish statistical equivalence or tiny universal wins. Keep the prior **3% practical materiality threshold** as a decision aid, not a significance test; show ranges and paired signs. Prefer the unchanged control when benefit is not convincingly useful after costs.

A live reduction in misses with worse latency is a negative performance result. A decode win with a prefill regression is a tradeoff. Do not extrapolate total-context limits as actual input sizes or calculate whole-request time by adding unrelated medians. Preserve measured wall time as the practical reference.

# Preservation, recovery and final handoff

## 5. Workspace and reproducibility

Create a new timestamped campaign under the existing research repository:

`/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-residency-v2-<UTC_TIMESTAMP>/`

Use new experiment IDs without overwriting E028/E029 or any Q4 study. Preserve a copy of this goal, start/deadline, `STATUS.md`, `DECISIONS.md`, ledger, phase reports, summaries, configs, raw logs, diagnostics, traces, datasets/checkpoints, patches, dependency locks and analysis scripts.

Scripts belong in the repository, not only `/tmp` or shell history. Keep isolated writable source/build outputs for different variants. Shared read-only weights/dependencies are fine. Large files may be Git-ignored but must remain on disk with manifests. Record source/binary/model hashes and licenses; commit research code locally, never weights or secrets.

Each safe finalist and the unchanged Q4 control need preserved `start-32k.sh`, `start-128k.sh`, `start-256k.sh`, `stop.sh` and reproduction commands. Freeze settings in versioned configs. Launchers verify identity, print resolved settings, detect collisions and never rebuild/update automatically. Default bind is localhost; allow explicit host/port overrides. Actually smoke-test advertised launchers through their real startup path. Unsafe variants retain diagnostic reproducers, not production recommendations.

## 6. Failure handling and phase reports

On failure: retain evidence, identify the exact blocking step, distinguish experiment error from mechanism failure, repair in a separate version when justified, and continue. Do not create endless numbered harnesses or suppress exit codes. Use finite timeouts and cleanup for builds, servers, requests, training and tests.

Poor results must survive in the ledger. Complete their bounded analysis; do not delete them or terminate an entire algorithm family from one weak parameter choice. Equally, do not spend the whole deadline rescuing one nonessential tool. An alternative measurement method may answer the question.

Write Phase A before B, and Phase B selection before C. Update status after each meaningful experiment so compaction cannot lose the objective, baseline or remaining time. Mark COMPLETE_POSITIVE, COMPLETE_NEGATIVE, MIXED, BLOCKED, INVALID_PROTOCOL, NOT_ATTEMPTED or INCOMPLETE_DEADLINE honestly.

## 7. Final report and stopping state

Deliver one root report with:

- Verified baseline/protocol and an explanation or explicit limitation for differences from historical Q4 timings.
- Q4 headroom by context, reference assumptions, prediction timing and exposed-cost limitations.
- The full policy ledger, explicitly including Expert-Jev linear/MLP, temporal disposition, router/Markov/history/hybrid and Basal disposition.
- Held-out evaluation, CPU cost and transaction-level admission/victim outcomes.
- Live OFF/ON and practical original-control comparisons, correctness scope, negatives and repaired failures.
- Exact start/stop/reproduce commands, source/binary/checkpoint/config identities and total wall time.
- Untested directions distinguished from disproven mechanisms; one strongest next experiment if warranted.

Main table:

| Context | Variant | Valid/attempts | PP | TG min/median/max | TTFT | Wall | CPU % | All-demand local % | CPU/mapped entries | Promotion GB | Victim damage | Predictor cost |
|---|---|---:|---:|---|---:|---:|---:|---:|---|---:|---|---|

Finish with exactly one primary recommendation:

- `USE_Q4_RESIDENCY_V2`
- `KEEP_Q4_100US_BASELINE`
- `WORKLOAD_DEPENDENT`
- `PROMISING_NEEDS_MORE_WORK`
- `INCONCLUSIVE`

The unchanged Q4 baseline must remain runnable even when all candidates lose. Do not switch normal user launchers. Stop owned servers/training/profilers, verify no owned GPU jobs remain, and preserve partial evidence at the deadline.

**Research standard:** Q4 offers a new workload regime, not a guaranteed win. Learn whether better information, safer earlier scheduling or better eviction decisions can convert fixed-capacity headroom into actual latency savings. Demonstrate the mechanism and its cost; do not optimize the scoreboard or the number of benchmark rows.