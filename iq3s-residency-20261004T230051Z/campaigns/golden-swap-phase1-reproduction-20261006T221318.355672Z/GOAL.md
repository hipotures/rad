# Goal: Golden Swap Phase 1 — complete victim-return study, from existing traces to live replay

Execute the **entire Phase 1 in this single autonomous goal**: prepare the dataset, compare causal victim policies offline, select and integrate a finalist, validate it in live replay, analyze the results, and preserve a reproducible handoff.

The operator is not available to launch another goal after training or to approve each internal step. Internal gates are decisions you must make yourself. Do not finish with only a training report and a request for permission to run the benchmark. If the evidence supports integration, proceed directly. If it does not, investigate the failure and document a defensible negative conclusion rather than manufacturing a deployment candidate.

## 1. Research objective and scope

Earlier live-oracle studies demonstrated beneficial fixed-work residency schedules under the existing VRAM and real-transfer constraints. Restricting future knowledge about eviction victims destroyed much of that benefit. Golden Swap Phase 0 has now audited and recorded twelve natural workloads.

The specific question is:

> With incoming demand supplied by the existing oracle, can a small predictor using only causal information about resident experts make better eviction decisions and retain a useful fraction of the full-oracle benefit, after transfer, victim-return, planning and memory costs?

This is **oracle incoming + causal victim policy**, not a fully causal production scheduler. The full-oracle reference remains a feasible heuristic, not an optimal upper bound. A model that beats it on some task has not violated a bound.

Keep all required expert computations, routes and mixture coefficients. No tail dropping, changed top-k, approximate expert substitution, SSD tiering, extra VRAM, helper comparison, pool-spin tuning, K/PCIe tuning or incoming-predictor training. Do not reopen the broad Jev/Basal study. Use small numeric models; neither a large language model nor an external API is needed to label known trace futures.

Domain-specific success is legitimate. A benefit on coding tasks alone can justify a narrowly scoped next step. Do not demand an all-domain win, or select favorable tasks after looking at final results and call that a confirmed specialization.

## 2. One deadline and visible progress

**Hard maximum: 4 hours elapsed wall time.** Record UTC start, absolute deadline and monotonic elapsed time immediately. The deadline includes preparation, dependencies, training, builds, integration, all requests, repairs, reporting and cleanup. It does not reset after a restart or compaction.

At **T+3h20m**, stop starting substantial new measurements; reserve the last approximately 40 minutes for completion of owned work, analysis, audit and cleanup. Start no request that cannot plausibly finish with cleanup before the deadline. Finish earlier if the bounded study is complete. The four hours are a cap, not a target or a completion guarantee.

Use five internal progress steps, not separate user-launched phases:

1. STEP 1/5 — verify Phase 0 and construct causal features/labels.
2. STEP 2/5 — train, calibrate and compare bounded offline candidates.
3. STEP 3/5 — integrate one finalist and validate replay/safety.
4. STEP 4/5 — perform counterbalanced live-replay comparisons.
5. STEP 5/5 — regenerate results, audit, preserve reproducers and clean up.

Post a short user-visible update at every step start/end and approximately every 3–5 minutes at safe tool boundaries. Long commands must emit flushed heartbeat lines at least every 30 seconds, and you must poll rather than disappear into an unobservable long tool call.

Example:

```text
[PHASE 1 | STEP 2/5 START] 2 learned models, 4 development tasks | elapsed 00:28 | remaining 03:32
[HEARTBEAT] GBDT fit 1/2 complete | validation in progress | last progress 14s ago
[PHASE 1 | STEP 3/5] Finalist selected; integrating victim ranking | elapsed 01:11 | remaining 02:49
[PHASE 1 | STEP 4/5 | TASK 2/4 | BLOCK 1/3 | ARM LEARNED] mixed-chinook | decode active
[PHASE 1 | STEP 4/5 BLOCKED] Replay EOS validation failed; preserving tape and testing a minimal repair
```

Show elapsed time, remaining hard budget, current task/model/arm, completed and remaining work, and the next action. An ETA must be an evidence-based range or `unknown`. Step completion is not elapsed-time completion. Maintain atomic `progress.json`, readable `STATUS.md`, append-only `progress.jsonl` and a decision/attempt ledger.

Do not report `100% validated` when only training or structural trace checks finished. A campaign can finish with a negative or incomplete result; report that honestly.

## 3. Environment, evidence and preservation

Research root:

`/srv/ai/research/iq3s-residency-20261004T230051Z/`

Create a new directory:

`campaigns/golden-swap-phase1-<UTC_TIMESTAMP>/`

Locate the completed Phase 0 through its actual manifest/report, not an invented pathname. Its start was 2026-10-06T18:49:49Z and its status was PHASE0_READY. Read:

- Phase 0 report, benchmark manifest, runtime-budget files, prompt catalog, inventory and source-group splits.
- Trace schema/validators, twelve tape manifests, victim-return labels, descriptive feature availability and completion audit.
- `campaigns/q4-oracle-decomposition-20261006T100032Z/`, including source information restrictions, predictor specification, physical constraints and negative horizon results.
- `campaigns/q4-live-oracle-20261006T040656Z/`, including replay fidelity, safety, initial-state attestation and existing launchers.

The Phase 0 corpus contains approximately 97,123 observed native victim returns and 35,802 right-censored events. These are correlated events inside twelve tasks, not 132,925 independent tasks. All twelve are single requests with `tool_execution=false`; do not describe them as executed autonomous-agent benchmarks.

The twelve tapes passed structural validation, but Phase 0 did **not** run a new per-task live-replay fidelity matrix. It corrected validators for short-input QSA active width and EOS inside the final accepted verify window. Reuse and check those corrections before live measurement. Cancelled captures may not yield reusable tapes; do not silently accept partial files.

Freeze the original Golden Swap environment:

- Qwen3.8-Flash-Next UD-Q4_K_XL, expected revision `38bb39ee97821de2c9009abb7e93950eec396e66`.
- Original serving source `6f32ec070f23ced9f50e704d854d775da52591ab`.
- Original control executable `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/control/strata`.
- Original SHA256 `eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d`.
- Two RTX 4090 24 GiB; K=24; PCIe fraction=0.28; pool spin=100 us; 15 workers.
- MTP spec=4/min-p=0.5; INT8 KV; kv-resident=32768 where applicable; prefill=auto; suffix/reuse OFF; serial execution.

Use the verified replay/capture derivatives from the prior manifests as integration substrates, not an unrelated checkout. Phase 0 recorded with source `117bc89b3bacbf263379c336557e6c8aa07aff5e`; decomposition used a later derivative. Verify compatibility instead of assuming their source hashes are interchangeable. Record exact source/binary/build/config identities for every new mode.

Do not migrate to the issue-921 Strata 0.1.40 engine during this study. Do not modify normal launchers, old datasets, source snapshots, weights or previous results. Use isolated source/build directories. No sudo, driver/host/VM/clock/power changes, push, PR, paid services or private-data upload. User-space dependencies and relevant primary documentation are permitted when needed. Keep authored files, comments and reports in English; preserve original source data verbatim.

Check process/GPU ownership. Do not interrupt unrelated work. Training is CPU-only and must not overlap live measurements, builds or heavy analysis. Stop only owned processes, using identity-checked PIDs/process groups and finite timeouts.

# STEP 1/5 — causal dataset and test contract

## 4. Preserve the source-level split

Development:

- code-heg
- math-rational
- text-http
- mixed-build

Calibration:

- code-queue
- math-sensor
- text-tls
- mixed-fields

Reserved evaluation:

- code-archive
- math-inventory
- text-websocket
- mixed-chinook

Verify these against the Phase 0 manifest. Previously exposed source groups remain marked as exposed; they are not newly pristine external holdouts. Keep related documents/modules/variants together. A random split of windows or expert rows from the same episode is not an acceptable generalization test.

Development is for feature/model work; calibration is for operating-point selection; reserved evaluation is for a frozen candidate. Do not repeatedly tune against reserved evaluation. A disappointing held-out result must survive in the ledger. A source/code correctness repair may justify re-evaluation, but not relabeling the same data as unseen.

## 5. Features, labels and selection bias

Use recorded initial state, causal prefixes and actual native admissions/evictions. Available causal features can include layer/expert identity, exact byte class/device, recent use counts, last-use distance, history-based heat reconstructed from the verified update rule, burstiness, resident age and observed reload/eviction history.

Phase 0 did not expose complete dynamic heat, queue/protection state or all MTP subdivisions. Reconstruct a missing quantity only when the event stream and source semantics make it valid, and validate the reconstruction. Otherwise mark it unavailable and omit it; do not fill missing state with zeros, oracle data or invented counters.

Future next-use, future reuse counts, actual return times and full-future victim choices are **labels/evaluation data only**. They must never leak into runtime features, preprocessing, tie-breaking or cached scores. Test that replacing an unseen future suffix cannot change a causal victim score for the same observed prefix/state.

The observed eviction set was selected by the native policy. Training only on its actual victims may not cover the residents that the new policy will consider. Address this explicitly. Where state reconstruction permits, create decision-time candidate sets containing a bounded, representative sample of compatible residents, including retained residents, not just evicted ones. Record sampling probabilities/weights or describe the remaining selection bias. Do not generate a 24,576-by-24,576 Cartesian dataset.

Respect same-layer, same-device, class-compatible slot constraints. Exclude in-flight/currently protected residents using the verified safety mechanism. Resident age and eviction history depend on the policy: training-prefix state and simulated/live candidate state must be updated under their respective policies, not copied from the old baseline after placement diverges.

## 6. Target: future return risk, not popularity alone

Prefer a censored multi-horizon return-risk/survival target and, if supported, a cost-weighted eviction-loss proxy. A reasonable bounded starting horizon set is 1, 4, 16 and 64 **main verify windows**; add a longer horizon only if observations and budget justify it. Document conversions to routed-layer invocations: one full main window includes 48 such invocations. Do not confuse these units with H64 from the earlier oracle decomposition.

For a horizon H, a return before H is an observed positive. A negative requires observation through H without return. A trace ending sooner is censored, not negative. Use masks or a survival likelihood accordingly. Check event-boundary conventions and simultaneous batches. Do not invent an order among lanes of one routed batch.

A next-use timestamp is not exact counterfactual regret. Any modeled savings must distinguish measured cost estimates, assumed costs and unknowns. Include the possibility that a short return is cheap/overlapped and a rarer return is expensive; frequency alone is not an execution-time objective.

Save dataset schema, group splits, censoring masks, seeds, normalization and training scripts. Run a small end-to-end data/replay smoke test before a larger fit. Do not recapture twelve workloads simply to obtain a second copy of identical data.

# STEP 2/5 — bounded training and offline policy competition

## 7. Candidate budget

Use interpretable controls and at most three small learned candidates:

- Native/history victim preference and one cheap causal recency/frequency control.
- A linear/logistic multi-horizon or discrete-hazard model.
- One small boosted-tree model if a suitable dependency is already available or quickly installable.
- A tiny MLP only if justified by data, fit diagnostics and time; it may replace a blocked tree implementation rather than adding a lengthy branch.

These are candidates inside one campaign, not new operator tasks. Reuse existing training infrastructure. No broad hyperparameter grid, 1% threshold sweep, large semantic teacher or repeated hidden-size escalation. Use at most a few meaningfully different settings and a fixed recorded seed. Check class balance, leakage, censoring and learning curves before interpreting a failed fit as lack of signal.

Prediction weights remain frozen during live inference. Causal histories update dynamically; that is not online retraining. Share feature extraction/batch scoring where practical. Measure CPU inference, feature-building and selection latency, not merely model size. Do not assume every admission requires a full new model evaluation or that its cost is negligible.

## 8. Turn predictions into an actual decision

The policy must affect which eligible victim is selected or whether an exchange is rejected. Computing a score that does not influence the chosen action is not an implementation.

Keep the existing incoming issue frontier E=64 and oracle incoming candidate order/eligibility fixed for the principal comparison. Isolate the victim change; do not simultaneously add a new incoming-ranking algorithm and attribute the result solely to learned eviction.

Rank compatible resident candidates by estimated return risk/loss over the incoming action's relevant reuse interval, with a documented cost proxy. Include `NO_SWAP` as a real choice. A rejection does not skip required expert computation; the normal CPU/mapped path remains available.

Use a common deterministic exchange guard and the same physical scheduler across causal-victim variants. If adding a material veto, hysteresis or uncertainty fallback, retain a matched cheap-rule offline ablation so its effect is not confused with learned prediction. Do not add a new allocator, hard lease system or bandwidth-controller research campaign here. Preserve existing bounded copies/spares and measure churn.

Incoming future knowledge remains privileged. Victim features must not query victim future. Any oracle full-current-window protection inherited from the substrate must be explicitly declared as a common safety/information channel; do not advertise the whole system as deployable causal inference.

## 9. Offline evaluation and autonomous selection

Validate replay-current accounting against the tapes before trusting simulated comparisons. Use identical byte budgets, initial state, class constraints, reservations, native/oracle exchange ownership and finite-end handling. Do not optimize a simulator that cannot reproduce its baseline.

Report task-level and family-level prediction calibration, return-risk discrimination, censoring support and ranking diagnostics. For policies, prioritize modeled nonlocal demand/cost, copy bytes, victim absence, reloads/churn, readiness and overhead. A high classifier score or local hit rate alone is insufficient.

Do not call an offline modeled retention value measured TG or measured oracle-gain retention. Time a representative offline evaluation early; Phase 0's 27-second data scan was not a measured policy-evaluation runtime.

Select **one** runtime finalist using development/calibration, freeze its checkpoint, thresholds and fallback behavior, then evaluate reserved tasks. Choose a robust tradeoff rather than the best single prompt. A family-specific candidate is allowed when its scope was selected before final evaluation and the small number of source groups is acknowledged.

If all candidates lose, diagnose at least the leading plausible blocker: feature error, censoring, biased candidate population, stale policy-dependent state, bad cost proxy, under-admission or ineffective action ranking. Attempt a bounded repair when justified. Do not keep retuning on held-out results. If no candidate is safe or meaningfully promising after diagnosis, complete the report and stop; unnecessary live benchmarking is not required just to fill the deadline.

# STEP 3/5 — integrate and validate a finalist

## 10. Same-runtime integration

Integrate the frozen scorer into the existing safe oracle replay scheduler. Keep all 48 main routed layers and all three Q4 expert classes where already supported. Use the same charged five spare slots, memory budget, copy concurrency and completion/publication rules. MTP residency and ordinary settings remain unchanged.

The victim model is CPU-only during live inference. Candidate-owned host memory, feature work and planner overhead must be measured. No GPU model buffers or uncharged extra expert slots. Use a bounded nonblocking scoring path or documented synchronous cost; no unbounded queues or stale plans applied without validation.

Check current resident/slot identity and protection before committing. The immutable full-RAM expert backing remains intact. Never overwrite in-flight readers, publish incomplete copies, lose ownership, duplicate reservations or bypass a required fallback. Preserve request cancellation, final drain/restoration and next-request behavior.

Retain three modes in the same experimental binary where possible:

- `REPLAY_CURRENT`: unchanged native residency through the same replay substrate.
- `ORACLE_FULL`: the existing full-future incoming/victim reference.
- `ORACLE_IN_LEARNED_VICTIM`: same oracle incoming protocol with the causal victim policy.

An OFF/guard mode must reproduce the unmodified substrate. Replay-current keeps its normal capacity and adaptation; do not shrink it to hide the oracle's spare cost. All oracle modes use the same charged physical envelope.

## 11. Fidelity and safety gate

Validate the Phase 0 short-input QSA and final-EOS corrections through the real replay path. Check work fingerprints, actual committed/emitted token counts, main/MTP branches, routes, coefficients, shapes and initial-state contract. Do not treat enforced output identity as proof of natural-generation correctness.

Run relevant existing tests and small targeted checks for invalid predictions, NO_SWAP, duplicate candidates, protected victims, changing ownership, late completion, repeated spare reuse and cancellation. Validate sampled copied bytes against backing weights where supported. No new full-suite run is required if it would consume the campaign; report exactly what was tested and existing environment failures.

Use a development tape or short supported prefix for preflight. Do not reuse a final evaluation task as an unlimited debugging target. If replay behavior is wrong, localize the first failing event and fix it before timing; never hide a mismatch as harmless floating-point drift.

# STEP 4/5 — live confirmation without another user launch

## 12. Main matrix and time funnel

The target final task set is the four **reserved-evaluation** tasks, not the four development screening tasks:

- code-archive
- math-inventory
- text-websocket
- mixed-chinook

Use their existing tapes, actual context profiles and natural stopping points. The WebSocket tape ends at 1773 emitted tokens; use its real count, not a fictitious 2048 denominator. All four currently have 32K configured limits; do not call this a 128K occupancy test.

For each task compare the three modes above in three counterbalanced adjacent blocks:

`4 tasks x 3 modes x 3 attempts = 36 main requests`.

This provides contemporary current and full-oracle references for conditional learned-victim gain retention. Share each block's current/reference results across valid comparisons; do not double the baseline count per candidate or borrow old timing medians.

Phase 0's recorded component totals imply roughly 73 minutes of model operations for these four tasks at nine arms each, before new integration costs and timing changes. Treat that only as an estimate: the new model/scheduler, attestation, replay and host scheduling may change it. Recalculate after the first block and show the remaining budget visibly.

Do not run all twelve tasks through a three-policy, three-repeat live matrix. Use all twelve offline; reserve expensive live confirmation for this bounded final set.

Before measurements freeze block/task order and a deadline fallback order. If the full target no longer fits, preserve complete three-mode blocks and report partial coverage rather than dropping losing arms or repeatedly running only the fastest task. Never choose the fallback based on observed gains. A smaller valid result is preferable to a nominally complete corrupted matrix.

If time remains after the main set and reporting reserve, one predeclared 128K-profile transfer check may use `text-tls` with its approximately 81.7K actual input. It is calibration-source evidence, not an unseen test. At most three matched three-mode blocks; do not reconfigure old tapes or add 256K. No optional test may threaten completion of the main analysis or deadline.

## 13. Repetition and operating rules

At most **three measured attempts per unchanged point** in this campaign, including any matching screening attempts. No fourth run to replace an inconvenient value. Keep every invalid/error attempt. A real code/protocol repair creates a new version and must explain why earlier results are not directly comparable; it is not a device for bypassing the repetition limit.

Use the same fresh-server, saved warmup, natural prefill, initial-state attestation, tape and timing definitions across arms. Charge setup, online planner, real copies, drain and restoration correctly. Do not preload future expert weights during untimed setup. Future tape/index initialization follows the common validated substrate and is disclosed.

Use finite request/startup timeouts informed by Phase 0. A timeout aborts an owned process safely, not a required expert computation inside an apparently successful result. Captures interrupted at sixty seconds are not interchangeable fixed-work inputs. Measure full validated tape replay rather than equal wall-clock exposure per policy.

No concurrent training, builds, downloads, hashing, heavy diagnostics or other GPU tasks during headline timing. Record guest CPU/steal and per-GPU memory/utilization/power/clocks without changing settings. Counterbalancing reduces but does not eliminate VM drift. No favorable-run filtering or post-hoc steal correction.

# STEP 5/5 — interpretation, report and handoff

## 14. Required measurements

Per arm retain:

- Work/initial-state fingerprints, emitted recorded tokens, completed windows and main/MTP demand conservation.
- Replay decode time, replay-equivalent tok/s, prefill, total request wall, startup/warmup and cleanup components.
- Main local/CPU/mapped counts and shares with a common all-routed denominator; MTP separately.
- Issued/completed/published copy bytes, promotions, rejected exchanges, late demand, pending/unused work and repeated admissions.
- Observed victim-return/absence and reload counts, with finite-end censoring.
- Feature extraction, model scoring, candidate selection and online planner cost; host RAM and charged GPU capacity.
- CPU/steal, GPU telemetry, raw logs, errors and timeouts.

Unknown counters remain unknown. CPU expert entries differ in cost; local-share improvement alone is not success. Observed absence is not exclusive causal latency. Do not add overlapping CPU/GPU/planner timers or infer transfer saturation from average PCIe samples.

For matched block times, when the full oracle is faster than current, compute:

`retention = (T_current - T_learned) / (T_current - T_full)`.

Calculate per block, then summarize. A small/nonpositive denominator makes retention unstable or undefined. Do not clamp negative values or values above one. Report absolute time/TG changes as well. The full oracle must first demonstrate a benefit on each new task before there is a meaningful benefit to retain.

Show min/median/max, paired signs and median paired ratios, not only ratio-of-medians. Three repeats do not prove tiny gains or independent task-level generalization. Never compare raw totals from different amounts of model work.

## 15. Conclusions and limitations

Answer whether the predictor learned return-risk signal, whether that signal changed decisions usefully, and whether real replay benefited after overhead. Separate:

- Prediction success with poor scheduling.
- Reduced churn/traffic without latency improvement.
- A conditional learned-victim latency gain on specific tasks.
- Failure of the tested feature/model/cost choices.
- Integration, fidelity or deadline blockage.

Positive code-only results are worth retaining, but one archive task is not a validated claim about all Python or agent work. No tool execution occurred in these tapes. Short finite trajectories and the known dataset exposure limit generality. Any inherited oracle incoming/current-window safety privilege remains explicit.

The unchanged Q4/100us configuration remains the normal serving baseline. An oracle-incoming learned-victim result is a research milestone, not a production speedup or a fully causal Golden Swap implementation. Do not enable it in normal launchers.

## 16. Artifacts and end state

Preserve GOAL, STATUS/progress, DECISIONS, source-group splits, causal feature schema, censoring logic, training scripts/checkpoints, dataset manifests, offline results, candidate selection record, source patches/build hashes, safety/fidelity tests, run-order manifests, raw logs/tapes/references, CSV/JSON summaries, exact reproducers and final report.

Provide tested commands to regenerate the dataset/features, fit/evaluate the retained model, run each supported replay arm, and inspect progress. Scripts verify model/binary/checkpoint/config hashes, print effective settings, use timeouts and operate only on owned resources. No auto-update or rebuild in launchers. Preserve the original normal launchers unchanged.

Main table:

| Task/profile | Mode | Valid/attempts | Replay-equivalent tok/s min/median/max | Paired decode-time change | Full-gain retention | Wall s | Local % | CPU/mapped entries | Copy GB | Reload/victim absence | Scorer/planner cost |
|---|---|---|---|---|---|---|---|---|---|---|---|

End with one primary research conclusion:

- `CAUSAL_VICTIM_GAIN_WITH_ORACLE_INCOMING`
- `DOMAIN_SCOPED_CAUSAL_VICTIM_GAIN`
- `MECHANISM_IMPROVED_NO_CONFIRMED_LATENCY_GAIN`
- `NO_GAIN_IN_TESTED_CAUSAL_VICTIM_POLICIES`
- `INTEGRATION_OR_FIDELITY_BLOCKED`
- `INCONCLUSIVE`

Also state actual elapsed time, what was completed, what remains unmeasured, the strongest next experiment and exact reproduction commands. Stop owned servers, copiers, trainers and profilers; verify no owned GPU work remains. Keep all negative/partial evidence at the hard deadline.

**Complete the whole feasible research chain in this goal. Internal steps are for progress visibility and autonomous decisions, not requests for the operator to start another task.**