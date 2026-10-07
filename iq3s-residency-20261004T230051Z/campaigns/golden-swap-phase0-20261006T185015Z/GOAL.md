# Goal: Golden Swap Phase 0 — workload audit, reusable corpus and runtime calibration

Execute **Phase 0 only** in the existing Strata research laboratory. Act as a researcher: inspect the actual data, reuse working infrastructure, diagnose failures and deliver a usable, time-budgeted benchmark corpus. Do not stop at a proposal.

## Objective

Before training any Golden Swap predictor, establish:

- What our existing requests actually contain, where the text came from and how it was lengthened.
- Which independent, meaningful workloads we can reuse or obtain from public sources.
- How long representative short episodes take, including prefill and operational overhead.
- Whether their routing traces are suitable for studying expert reuse, residency and future victim-return risk.
- Exactly how much subsequent offline screening and live comparisons will cost.

A benchmark that helps only code, or even a particular coding workload, can still be useful. Preserve domain-specific evidence. Do not assume a universal winner or select workloads because an oracle previously accelerated them.

**Do not train predictors, compare replacement algorithms, run an oracle performance matrix, implement Golden Swap, drop expert contributions, or change normal serving.** This phase prepares the evidence and the test infrastructure for those later decisions.

# Operating rules

## Time budget

**Hard maximum: 60 minutes elapsed wall time.** This includes discovery, downloads, harness repairs, starts, warmups, requests, trace flushing, analysis and cleanup. It is an upper bound, not a target.

Record UTC start/deadline and monotonic elapsed time immediately. The deadline does not reset after a failure, restart or context compaction.

Aim to complete audit, corpus assembly and harness preparation within approximately 20 minutes. Use the next approximately 30 minutes for bounded recordings and runtime calibration. At **T+50 minutes**, stop starting model requests and reserve the last 10 minutes for analysis, audit and cleanup. Finish earlier when the required evidence is ready.

Plan approximately **12 independent episodes: three per family**. Do not sacrifice provenance, independence or safety to reach that number. Define all suitable tasks in the manifest; if time permits fewer measurements, clearly distinguish measured, reused, estimated and unmeasured items. Cover every family before spending the remaining budget on additional episodes in one family.

## Visible progress — mandatory

Use exactly **five numbered steps inside Phase 0**. Call them `STEP 1/5` through `STEP 5/5`, not additional P0/P1/P2 phases.

The operator must be able to see your position without asking:

1. Announce the five steps and deadline at the start.
2. Post a brief user-visible update when each step starts and ends.
3. During model sampling, print a start and finish record for every episode, including its position in the sampling queue.
4. While a longer command runs, the runner must print a flushed heartbeat at least every 30 seconds. Poll long operations in bounded intervals rather than disappearing into one unobservable command.
5. During active work, provide a brief operator-facing progress update approximately every 3–5 minutes at safe tool boundaries. Do not interrupt inference or add synchronization merely to produce that update.
6. Report immediately when a blocker, protocol repair or projected overrun changes the plan.

Example log records:

```text
[PHASE 0 | STEP 1/5 START] Audit existing payloads | elapsed 00:00 | remaining 60:00
[PHASE 0 | STEP 1/5 DONE] 14 payloads audited; 5 source groups; 3 exclusions | elapsed 08:12
[PHASE 0 | STEP 4/5 | EPISODE 5/12 START] math-02 | profile 128K | request cap 240s
[HEARTBEAT] math-02 | prefill finished | decode 31s | output 1820 | last window 604 | remaining campaign 21:10
[PHASE 0 | STEP 4/5 | EPISODE 5/12 DONE] wall 108s | output-cap | trace validated | 7 episodes queued
[PHASE 0 | STEP 4/5 BLOCKED] Native request stopped making progress; preserving diagnostics and stopping owned process
[PHASE 0 | STEP 5/5 DONE] 12 defined; 10 calibrated; 9 replay-ready; 2 unmeasured | cleanup verified
```

Always show elapsed time, remaining hard budget, completed/remaining work and the next action. An ETA must be a measured range, or `unknown`; it must not be invented. Step count is not a time-completion percentage: step 4 may take longer than all earlier steps combined.

Maintain an atomic `progress.json`, readable `STATUS.md` and append-only `progress.jsonl`. Include last heartbeat, current activity, owned PID, current request state and blocker/recovery notes. Do not claim `100% ready` when tasks, traces or checks remain incomplete. A finished campaign may have a partial deliverable.

## Workspace, permissions and isolation

Research root:

`/srv/ai/research/iq3s-residency-20261004T230051Z/`

Create a new campaign:

`campaigns/golden-swap-phase0-<UTC_TIMESTAMP>/`

Keep code, manifests and reproducers in this repository, not only `/tmp` or shell history. Preserve old campaigns unchanged. Large traces may be Git-ignored but must remain on disk with hashes and stable paths. Local commits are allowed; no push or PR.

You may inspect public primary sources, download small justified data subsets and install/compile user-space dependencies in an isolated environment. No sudo. Do not change drivers, host/VM settings, clocks, power limits, affinity, model weights or normal launchers. Do not run paid services or upload private prompts/logs. Inspect repository material for secrets before using it as model input or exporting it.

All authored documentation, scripts, comments, manifests and progress records must be in English. Preserve authentic source data and recorded outputs verbatim; do not rewrite them to improve the benchmark's apparent quality.

Check GPU/process ownership first. Do not stop unrelated servers or another campaign. Use read-only/CPU preparation while blocked and report the conflict; the wall-clock budget still applies. No parallel GPU requests, compilation, heavy hashing or analysis during timed inference.

# STEP 1/5 — audit the actual workloads and baseline

## Read the existing evidence and follow real paths

Start from the relevant manifests, source payloads and builders in:

- `experiments/E026-pool-generalization/`
- `workloads/`
- `campaigns/q4-residency-v2-20261005T202441Z/`
- `campaigns/q4-live-oracle-20261006T040656Z/`
- `campaigns/q4-oracle-decomposition-20261006T100032Z/`
- `campaigns/upstream-921-spin-validation-20261006T131023Z/`

Locate the repository-maintenance, numerical/RFC and archive/zipfile requests, earlier training/calibration/holdout episodes, warmups and saved token arrays. Inspect any completed conditional-admission campaign only if it actually exists.

Reports describe real source families, but **a report is not the payload**. Open the request JSON and the script that constructs it. Decode saved input IDs with the correct tokenizer where text is missing. Do not treat a path mentioned in a report as proof that its contents were inspected.

For every distinct workload lineage record:

- Exact system/user messages and where the substantive source text starts and ends.
- Source document/repository/problem identity, revision, license and extraction method.
- Actual rendered token count and original text hash.
- How length was obtained: natural full source, coherent excerpt, concatenation, repetition, padding or truncation.
- Every nonce/identifier: its location, length and purpose. Do not silently strip it from historical evidence.
- Duplicated blocks, repeated documents, boilerplate and unrelated filler.
- Whether the output request is natural or artificially elongated, including the later Q4 book-length instruction.
- Whether this is a single prompt, an agent transcript/snapshot or an actual tool-execution episode.
- Existing trace availability, engine identity and previous use for training, calibration or evaluation.

Group semantic duplicates and shared source lineages. Different nonces, context lengths and excerpts from the same document are not independent tasks.

Random tokens or filler may remain useful as explicitly labeled synthetic stress tests. Keep them out of the natural predictor corpus rather than retroactively declaring every earlier measurement invalid.

Write `workload-audit.md` and `workload-inventory.json`. Create a readable `prompt-catalog.md` with each task's actual instruction, a representative source excerpt, length-building method and links to its complete local payload. The operator must be able to see what Qwen is being asked to do.

## Freeze the appropriate Q4 environment

Use the unchanged Golden Swap research control, **not the newer issue-921 engine merely because it was built more recently**:

- Qwen3.8-Flash-Next UD-Q4_K_XL.
- Expected model revision: `38bb39ee97821de2c9009abb7e93950eec396e66`.
- Original Strata 0.1.39 source: `6f32ec070f23ced9f50e704d854d775da52591ab`.
- Original executable: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/control/strata`.
- Original SHA256: `eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d`.
- Q4 layer split K=24; PCIe fraction=0.28; pool spin=100 us; 15 workers.
- MTP spec=4/min-p=0.5; INT8 KV; kv-resident=32768 where applicable; prefill=auto.
- Suffix lookup and prompt reuse OFF; greedy; one request at a time.

Verify these against existing launchers/provenance. The existing validated capture binary derived from this baseline may be used for recordings, with **current native residency, natural generation and no oracle/replay overrides**. Record its separate source/binary identity and instrumentation overhead. Do not label instrumented timings as clean-baseline measurements.

Reuse the existing capture path and verified Q4 model/PLE/MTP/profile files. No version migration, full rebuild, new kernels or memory-policy changes in Phase 0. A bounded harness repair is allowed; an unexpected binary mismatch must fail visibly, not trigger a fallback to an old or latest installation.

# STEP 2/5 — assemble a small, source-grounded corpus

## Four families, approximately twelve episodes

| Family | Representative work | Important distinction |
|---|---|---|
| Code/agent | Repository review, debugging or implementation reasoning | Code-themed text is not automatically an interactive agent run |
| Math/research | A substantive multi-step problem or numerical investigation | Do not demand hours of proof search |
| Text/translation | Document analysis, summarization or translation | Keep subtask and language tags; these may behave differently |
| Structured/mixed | Real log analysis, schema extraction, technical mixed-format work | Do not fabricate random JSON just to fill context |

Aim for three independent source/task groups per family. Reuse audited local material first. Add external data only to fill a concrete diversity or provenance gap.

Briefly inspect **at most four suitable public source collections** through official repositories/dataset cards. Download only the selected source texts/tasks and required metadata. Record source URL, revision, license, subset and task IDs. Do not install a full heavyweight benchmark environment, download an entire large corpus or run a repository-wide test suite merely to obtain a few prompts. Cap public discovery/download work at approximately five minutes inside the setup budget.

A task adapted from a public benchmark is a routing workload here, not an official benchmark score. Retain the source task separately from our wrapper. Record every adaptation and do not expose reference answers, gold patches or hidden tests in the model's input.

Prefer real substantive material and realistic instructions. No lorem ipsum, random padding, repeated paragraphs to reach a token target, or demands to repeat text forever. Inspect output samples for repetition/degeneration; preserve such cases and label them, not silently rerun them until attractive.

For agent-like work, prefer available genuine request/tool-result snapshots. Label `tool_execution=false` when tools are not actually run. A complete autonomous agent solving a repository issue is out of scope. Only reuse an already working bounded tool harness if its entire episode fits the same limits; no new agent framework in this hour.

## Contexts and dataset splits

Use **32K and 128K total-context profiles only** for new calibration. Preserve historical 256K material as an extended set; do not add fresh 256K runs in Phase 0.

Assign each core episode ONE profile, rather than twelve episodes times every context. Target approximately eight 32K and four 128K recordings, with family coverage at both limits where natural source length permits. Rotate profile assignment across split roles; do not make all holdouts 128K and all development tasks 32K.

The configured maximum is not actual occupancy. Report both. Keep enough room for the output cap and engine reserve. Use a coherent real excerpt when needed; a naturally shorter task remains shorter. Do not pad to a nominal target or call a 4K input a 32K-input benchmark.

Before examining routing outcomes, assign source-group-level roles: development, calibration and reserved evaluation. With three groups per family, one per role is a small starting design, not a statistically broad dataset. Keep every related excerpt/nonce/language version on the same side of the split. Mark previously used evaluation material as already exposed; do not call it a pristine holdout.

Infrastructure/timing calibration of reserved evaluation items is allowed under this fixed protocol. Do not use their routing outcomes to select features, tune policies or decide which domains to keep. Exclude them from later fitting scripts by default. Freeze task order and log objective eligibility decisions.

# STEP 3/5 — prepare a bounded recording/calibration runner

## Request size and stopping

The purpose is to observe a meaningful slice of real work, not force completion of the entire application, proof or translation.

For each episode predeclare:

- A maximum of **2048 or 4096 generated tokens**, chosen for the task before measurement.
- A **soft decode sampling target of approximately 60 seconds**, measured after generation begins, not from process launch.
- A **hard request wall deadline of 240 seconds**, including tokenization/prefill/decode.
- A desired ordinary request duration around **60–150 seconds**, not a mandatory minimum.

Stop at natural EOS, the token cap or the soft sample boundary, whichever comes first. Use the existing safe stop mechanism and flush the last complete logical window. Do not implement unsafe mid-kernel interruption. A short natural completion is not a protocol failure: retain it, classify it as short, and continue to a different preselected task rather than coercing filler.

Distinguish `NATURAL_EOS`, `OUTPUT_CAP`, `PLANNED_TIME_SLICE`, `HARD_TIMEOUT`, `ERROR` and trace usability. An intentional incomplete slice can supply valid routing data but does not mean the task was solved. A hard-killed or incomplete tape is not replay-ready without validation.

Use an owned-process graceful-stop timeout, then terminate only the owned process group if necessary. Leave cleanup time inside the campaign deadline. Startup and warmup need separate measured limits, initially no more than 180 seconds combined per fresh start; do not silently extend them or let them disappear from the cost estimate.

A time slice is for this calibration campaign. **Later A/B arms must replay the same completed logical prefix or use a frozen token/work budget.** Giving each policy sixty seconds and comparing raw expert counts would compare different amounts of work. Save the exact stop/window boundary and observed workload size now.

## Starts, warmup and repeat limits

Prefer the existing fresh-server, fixed 4096-input/64-output warmup protocol per independent episode. Record startup, warmup, prefill, decode, drain and shutdown separately.

If startup dominates, use a previously validated identical-state reset only if one already exists. Do not invent a reset or silently switch to a warm shared cache. Reduce the number of new calibrations before sacrificing interpretable initial state. Label any reused historical trace or warm-sequential sample with its actual protocol.

**One new recording per unchanged task/profile is the default.** Do not repeat a trace three times to create artificial training diversity. At most one small development-only capture/fidelity comparison is allowed if existing validation does not cover this path. At most two campaign-wide repaired-attempt slots may address objective failures. Retain every original attempt; no retries for low speed, inconvenient routing, natural EOS or an unhelpful result.

Freeze a round-robin family queue. Attribute no more than **10 minutes of model-operation wall time to one family**, including its starts/warmups/cleanup. This is a ceiling within the remaining total budget, not an entitlement to forty extra minutes after setup. Before every launch, check whether the likely request and cleanup can finish before T+50 minutes; otherwise defer it explicitly.

# STEP 4/5 — collect short natural trajectories and timing evidence

Use native generation with the current cache policy. No forced expert routes or privileged future data during recording. Reuse the existing complete trace format when practical; do not build another replay engine.

For each episode capture:

- Full prompt/messages, rendered input IDs and tokenizer identity; output text/IDs and finish reason.
- Request, main/MTP role, verify window, layer, batch shape, absolute positions and speculative lanes; include rejected speculative work.
- Routed expert IDs and coefficients where the validated schema provides them; expert device/size class.
- Local VRAM, CPU and mapped/nonlocal paths; initial residency and subsequent admissions/evictions.
- Causal usage/heat, last-use/residency timestamps in logical units, reload/eviction events and existing queue/protection fields where available.
- PP, TG, TTFT, phase wall times, committed tokens, verify windows and all-routed work count.
- H2D expert payload bytes, publication/reload counts and victim-absence observations when actually exposed.
- Lightweight CPU/steal, both GPUs' utilization/VRAM/power, RAM/RSS and swap telemetry.

Use logical event IDs for reuse/return analysis. Keep physical timing as a measured cost. Preserve batches rather than inventing serial ordering among simultaneously routed lanes.

Validate count/shape consistency, completed-window boundaries, token limits and checksums. Do not confuse unique experts, admission actions, expert jobs and token-expert entries. Local + CPU + mapped shares must use one documented denominator. Unknown counters remain null, not zero. Aggregate PCIe samples do not identify expert-copy payload bytes.

Annotate whether a record is `FULL_REPLAY_TAPE`, `ROUTING_TRACE_ONLY`, `TIMING_ONLY` or `INVALID_TRACE`, plus its validation status. Link existing verified compatible tapes instead of recapturing them merely to produce new files. Limit trace storage to approximately 12 GiB for this phase; stop adding recordings rather than deleting evidence or silently truncating event coverage.

A minute-long trace is finite. An expert not reused before the end is **right-censored**, not known never to return. Save observation-window bounds. Do not manufacture a future label near the end or cross independent requests as if they were one continuous trajectory.

Separate causal feature fields available before a decision from labels computed afterward. Next-use distance and future reuse counts belong in the labels/evaluation namespace, not runtime features. Do not claim eviction regret is exact ground truth merely from a next-use timestamp; counterfactual performance needs a separate model or experiment.

# STEP 5/5 — analyze diversity, price future experiments and hand off

## Trace diversity and suitability

Using the recorded data, report per task/family:

- Unique source groups and prior evaluation exposure.
- Output length, complete verifier windows, routed-entry volume and trace coverage.
- Local/CPU/mapped proportions, copies/reloads where observed.
- Expert-use distributions and useful overlap between tasks, preferably layer-aware.
- One or two lightweight similarity measures such as cosine or Jensen–Shannon divergence, with their definitions.
- Inter-use gaps, temporal burstiness, distinct-expert reuse distance and observed eviction-to-return intervals where available; do not conflate these quantities.
- Truncation/censoring, short-output and degeneration limitations.

Do not infer semantic independence from one routing-distance threshold. Similar routing does not prove two texts are duplicates; nonce changes do not make one document independent. Normalize demand comparisons by observed tokens/windows/entries as appropriate and keep task-level results.

This phase can show differing workload regimes. It **cannot identify which category benefits from Golden Swap**, because no candidate policy is tested. Do not announce a Python-specific speedup from locality alone.

## Runtime budget model

Produce `runtime-budget.md` and machine-readable estimates based on actual measured components:

`arm_cost = startup + warmup + tokenization/prefill + decode + trace/commit/drain + shutdown`

`campaign_cost = shared_setup + sum(cost_of_each_scheduled_arm) + analysis_and_cleanup_reserve`

Report separately:

- One-time corpus recording cost, including instrumentation and stored bytes.
- Offline dataset parsing/replay/evaluation cost: time an existing lightweight scan if useful; do not train a model just to estimate it.
- A small screening subset, approximately one development task per family.
- The full measured core suite, one pass per policy.
- A baseline plus one finalist, three paired repetitions: **six arms per selected task**.
- A baseline plus two finalists and one oracle reference, three repetitions: **twelve arms per selected task** if all four are run three times. Explain which compatible contemporary controls may legitimately be shared rather than multiplying full suites unnecessarily.

Give measured totals, estimated ranges and hard upper bounds separately. A single pilot provides no robust p95 or confidence interval. Do not average in unmeasured tasks as if they ran. Startup matters; sixty seconds of decode is not a sixty-second experiment. Diagnostic capture time is not automatically clean inference time.

Select a practical quick-screening subset using provenance, diversity, length and runtime criteria, not predicted oracle gain. If the complete future three-pair comparison would exceed the intended approximately two-hour budget, reduce its finalist task set transparently and retain the broader corpus for offline use. Repetitions are for timing uncertainty, not training diversity.

## Deliverables

Keep a versioned corpus snapshot or verified immutable references. Do not point at mutable files that later experiments may overwrite.

Required artifacts:

- `GOAL.md`, `STATUS.md`, `DECISIONS.md`, progress files and attempt ledger.
- `workload-audit.md`, `workload-inventory.json`, `prompt-catalog.md` and `public-sources.md`.
- `benchmark-manifest.json` with task/source-group IDs, family/subtask/languages, license/revision, payload hashes/paths, context limit, actual occupancy, output/stop rules, split/prior exposure, warmup/start-state protocol, measured phase times, estimates, trace type/paths/hashes, usability and reasons.
- `trace-summary.csv`, `runtime-budget.md`, `runtime-budget.json`, raw logs/tapes and schema/validation results.
- `report.md` and `reproduce.md`.
- Reusable scripts to inspect a prompt, run one bounded task, run the frozen screening/core queues, validate traces and print current progress.

The scripts must verify identities, enforce timeouts, preserve logs, detect conflicts and stop only owned processes. They must not rebuild/update automatically or change normal serving. Smoke-test only what is necessary; do not accidentally rerun the entire suite during audit.

Final table:

| Task | Family/subtask | Source group/split | Context limit / actual input | Output / stop reason | Startup + warmup s | Prefill s | Decode s | Total operating s | Local / CPU / mapped % | Trace status | Core / screening / deferred |
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|

Explicitly answer what the existing benchmark contained; which items were padded/duplicated; what new data was obtained; which tasks are genuinely independent; which are real agents versus snapshots; how long one pass and future paired matrices cost; and whether the traces are sufficient to BEGIN a small victim-return study. Do not claim sufficient diversity for universal generalization.

End with one status:

- `PHASE0_READY` — audited corpus, usable validated traces across the four families, runnable tools and honest runtime estimates are ready.
- `PHASE0_PARTIAL` — useful artifacts exist, but list missing coverage, traces or calibration explicitly.
- `PHASE0_BLOCKED` — identify the concrete prerequisite that prevented useful completion.

State actual elapsed time, defined/calibrated/trace-ready task counts, deferred items and exact inspection/reproduction commands. Stop owned processes and verify no owned GPU jobs remain.

**Stop here. Do not automatically begin Golden Swap training or another campaign.**