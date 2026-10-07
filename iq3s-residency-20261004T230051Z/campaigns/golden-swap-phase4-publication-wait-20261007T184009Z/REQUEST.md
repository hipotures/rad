/goal — Golden Swap: correct Phase 3 attribution, repair Phase 4 protocol, then execute Phase 4

You are the research execution agent for the RaD project.

Work as a researcher, not merely as an implementer.

This goal has three connected parts:

1. correct a specific post-hoc analysis problem in Golden Swap Phase 3 and document the correction without rerunning the Phase 3 GPU campaign unless new evidence proves that a rerun is actually necessary;
2. update the already prepared Golden Swap Phase 4 execution brief and protocol to remove two interpretation ambiguities identified during review;
3. once the corrected Phase 4 protocol is frozen and validated, **immediately execute Phase 4 through completion**.

Do not stop after editing documentation or preparing the experiment. Do not ask the operator to launch the tests separately.

Follow the repository `AGENTS.md` completely, including synchronization, research persistence, evidence handling, commit, push, and remote verification.

Do not introduce additional Git restrictions.

---

# Repository and existing work

Canonical repository:

`github.com/hipotures/rad`

This continues the existing Golden Swap investigation.

Relevant areas include:

- `iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase2-20261007T093357Z/`
- `iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase3-20261007T150955Z/`
- `iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase4-publication-wait-20261007T184009Z/`

Current Phase 4 state is planned but not started.

The prepared Phase 4 plan already contains useful source inspection, workload identity, run order, instrumentation constraints, a four-hour execution budget, and six planned CONTROL/TRACE replay requests.

Preserve that work. Repair it rather than replacing it gratuitously.

Before changing anything:

- synchronize safely with the canonical repository;
- read `AGENTS.md`;
- inspect the current Phase 3 report, analysis scripts and derived results;
- inspect the complete current Phase 4 `GOAL.md`, protocol, source map, manifests and validation receipt;
- verify that no newer repository state supersedes the facts in this goal.

If repository evidence contradicts this prompt, investigate and document the contradiction rather than blindly following stale text.

---

# PART A — Correct the Phase 3 live-trajectory attribution

## A1. Specific issue to investigate

The Phase 3 headline conclusion remains valid:

`DECISION_PRESERVING_OPTIMIZATION_NO_CONFIRMED_PRACTICAL_GAIN`

Do **not** reinterpret the entire Phase 3 campaign as invalid.

The issue concerns a narrower post-hoc explanatory claim in the live-trajectory analysis.

Inspect:

`golden-swap-phase3-20261007T150955Z/code/live_trajectory.py`

The current logic includes an inference equivalent to:

```python
earlier_readiness_difference = (
    publication_difference is not None
    and (
        selection_diff is None
        or publication_difference < selection_diff
    )
)
```

Here `publication_difference` and `selection_diff` are indices into admission-record arrays.

Those array indices are not themselves proof of chronological order between:

- the publication becoming visible; and
- the decision point at which incoming selection diverged.

A previously created admission record can be published later than a decision represented by a later record.

A retained example already appears to demonstrate the problem:

For `code-archive`, block 1, the diagnostic identifies:

- first differing incoming-selection records with triggers around event 10/11;
- a supposedly preceding differing publication with `published_at` around event 14/12.

Therefore the fact that the differing publication record has a lower array index than the differing selection record does **not** establish:

> publication visibility changed before the first incoming-selection divergence.

Treat this as an analysis bug/overclaim to audit, not as proof that asynchronous readiness was irrelevant.

## A2. Required correction

Reconstruct chronology using the strongest evidence actually available.

Use, as appropriate:

- logical routed-layer invocation/event index;
- admission trigger;
- target;
- actual `published_at`;
- publication timestamp if available;
- generation;
- slot;
- worker/device/class identity;
- ownership state;
- relevant service records;
- any retained host timestamps required to establish ordering.

Do not infer causation merely from vector position.

For each Phase 3 live BASE/OPT pair, classify the relationship between publication visibility and the first live selection/service divergence using a defensible state such as:

- `CONFIRMED_PUBLICATION_PRECEDES_DIVERGENCE`
- `CONFIRMED_PUBLICATION_DOES_NOT_PRECEDE_DIVERGENCE`
- `UNRESOLVED_WITH_RETAINED_EVIDENCE`

or equivalent precise terminology.

If several publication/state changes exist before the first divergence, inspect the relevant state rather than selecting the first differing record mechanically.

If retained evidence cannot identify the causal publication or worker-readiness change, say so.

Do not fabricate an exact attribution.

## A3. Preserve the original research record

Do not delete evidence of the original analysis.

Git history already preserves it, but the current research record should clearly expose the correction.

Appropriate actions may include:

- fixing `live_trajectory.py`;
- regenerating the derived Phase 3 live-trajectory diagnostic from immutable retained raw data;
- updating the Phase 3 report with a clearly labeled correction/erratum section;
- updating related compact result files if their meaning changes;
- recording the correction in `DECISIONS.md` or a dedicated correction note if useful.

Do **not** silently rewrite the historical interpretation.

State explicitly:

- what was wrong;
- what remains valid;
- what conclusion is weakened or withdrawn;
- what the corrected evidence supports.

Do not rerun the 42 Phase 3 timed requests merely to correct this analysis unless the raw evidence is genuinely insufficient for a required Phase 4 dependency.

If a Phase 3 rerun is unnecessary, do not perform one.

---

# PART B — Repair and freeze the Phase 4 protocol

The overall Phase 4 research direction is approved:

> determine how much remaining GPU plan-A dependency wait is attributable to residency-map publication acknowledgment and how much of that delay reaches the dependent request execution path.

Keep the existing narrow scope:

- one development trajectory: `math-rational`;
- history victim rule;
- first-use transaction control;
- Phase 3 incoming-query memoization ON;
- oracle incoming unchanged;
- same model/hardware/runtime configuration;
- three CONTROL/TRACE pairs;
- six total intended replay measurements;
- no causal incoming predictor;
- no scheduler redesign during the attribution experiment.

However, repair the following two protocol ambiguities before execution.

---

## B1. Separate intervention scenario from uncertainty interval

The current Phase 4 text mixes two different concepts:

1. the range of hypothetical publication-acknowledgment shortening being modeled;
2. uncertainty in the estimated timing effect of one specific hypothetical intervention.

If a modeled range explicitly includes the unchanged baseline duration, its lower possible speedup is trivially zero.

Such a range cannot simultaneously support a rule requiring:

> lower bound of improvement > 3%

unless the terms refer to different quantities.

Fix this before measurement.

### Required conceptual structure

Define at least:

### Baseline

Recorded execution with measured publication coordination unchanged.

### Primary realistic diagnostic intervention

A clearly specified fixed-trace counterfactual representing the smallest plausible removal of avoidable publication-coordination latency while retaining all known required metadata, safety, ownership, and dependency constraints.

Do not remove required work merely because it is inconvenient to model.

For this fixed intervention `c`, define something equivalent to:

```text
S_c = (T_recorded - T_counterfactual_c) / T_recorded
```

### Uncertainty interval

For that **same fixed intervention**, propagate:

- host/GPU clock mapping uncertainty;
- missing dependency-edge uncertainty;
- bracket uncertainty;
- unsupported path uncertainty;
- graph residuals;
- any timing ambiguity.

This produces something like:

```text
[S_c_min, S_c_max]
```

Decision thresholds should apply to this uncertainty interval for a defined scenario.

### Idealized opportunity upper bound

You may additionally retain a deliberately optimistic scenario, such as eliminating all acknowledgment delay after the earliest safe known predecessor.

Label it explicitly as an idealized opportunity bound, not an executable optimization.

Do not confuse:

- baseline-to-idealized intervention range;
with:
- uncertainty around one fixed intervention.

### Decision-rule consistency

Review the existing `<1%` and `>3%` classifications.

Ensure each threshold refers to a mathematically and semantically well-defined quantity.

If the old names:

- `PUBLICATION_ON_OBSERVED_DEPENDENCY_PATH`
- `PUBLICATION_SMALL_ON_TESTED_TRAJECTORY`
- `PUBLICATION_MOSTLY_HIDDEN_ON_TESTED_TRAJECTORY`

remain useful, keep them.

But rewrite their requirements so they cannot become logically impossible or self-contradictory.

---

## B2. Make the instrumentation perturbation gate symmetric

The current protocol correctly warns that a large TRACE speedup can itself mean instrumentation changed scheduling.

Make this an explicit executable decision rule rather than only prose.

A TRACE run should not be treated as quantitatively neutral merely because instrumentation makes execution faster.

Use a symmetric perturbation check.

For example, the protocol may require:

```text
abs(median paired TRACE/CONTROL decode change) <= 3%
and
abs(median paired TRACE/CONTROL completion-wall change) <= 3%
```

or another equally defensible predeclared formulation.

The exact rule is yours to choose, but it must detect systematic perturbation in either direction.

Also retain the existing protection against extreme single-pair changes.

Do not discard unexpectedly fast or slow traces.

If instrumentation systematically changes timing beyond the acceptable gate:

- preserve the measurements;
- investigate whether structural attribution remains usable;
- downgrade or widen quantitative attribution as required;
- do not rerun until results look neutral.

---

# PART C — Validate the repaired plan, then EXECUTE Phase 4

After Parts A and B:

1. regenerate/update the Phase 3 correction artifacts;
2. update Phase 4 `GOAL.md`, `configs/protocol.json`, validation scripts and any affected planning documents;
3. run the plan validator;
4. verify exact local frozen inputs where supported;
5. freeze the repaired Phase 4 protocol;
6. then **start a fresh Phase 4 execution clock and execute the experiment immediately**.

Do not stop after a successful plan-validation receipt.

Do not ask the operator whether to proceed.

---

# Phase 4 execution budget

Once Phase 4 execution begins, use a fresh immutable execution clock.

Hard Phase 4 execution budget:

**4 hours**

This clock starts only when substantive Phase 4 execution begins.

Do not inherit:

- the Phase 3 clock;
- the planning-directory timestamp;
- the time spent performing the Phase 3 correction;
- a prior failed campaign clock.

At approximately T+3h15m, stop starting substantial new experimental work and reserve the remaining time for:

- analysis;
- reproduction checks;
- report;
- evidence publication;
- cleanup;
- commit;
- push;
- remote verification.

Finish earlier if the question is decisively answered.

Do not consume time merely because budget remains.

---

# Phase 4 progress reporting

During execution use visible status:

`[PHASE 4 | STEP 1/5 START]`
`[PHASE 4 | STEP 1/5 DONE]`

through Step 5.

During inference report:

- block;
- arm;
- completed / planned requests;
- validity;
- elapsed Phase 4 execution time;
- remaining budget;
- next action.

For commands longer than approximately 30 seconds, emit heartbeats around every 30 seconds where practical.

Give a useful progress update every few minutes during long work.

---

# Phase 4 STEP 1/5 — Verify producer/consumer dependency model

Reinspect the active Phase 3-derived source.

Confirm the real runtime chain, including at least:

```text
expert copy completion
-> publication validation
-> residency-map metadata update
-> publication acknowledgment
-> host ownership/generation commit
-> remaining incoming/native plan construction
-> GPU plan publication / flag A
-> dependent verifier wait A
-> resident expert execution
```

Confirm whether a hook on one device can wait for publication work belonging to another device.

Confirm shared-stream and layer-split dependencies actually active under this exact frozen configuration.

Do not infer active edges from code paths that are disabled.

Record inactive paths explicitly as inactive.

Carry the corrected Phase 3 chronology lesson into this trace design: event identity and causal ordering must come from actual event/generation/timing state, not container or vector position.

---

# Phase 4 STEP 2/5 — Implement minimal buffered attribution tracing

Use a separate derivative of the verified Phase 3 runtime.

Do not alter Phase 3 source/build/results in place.

Keep all scheduling and policy semantics unchanged.

Preserve:

- Qwen3.8-Flash-Next UD-Q4_K_XL;
- model revision;
- 2× RTX 4090;
- K=24;
- PCIe fraction 0.28;
- pool spin 100 us;
- 15 workers;
- MTP spec=4 / min-p=0.5;
- INT8 KV;
- kv-resident=32768;
- prefill auto;
- suffix/reuse off;
- serial execution;
- five charged spares;
- full RAM expert backing;
- history victim control;
- minimum first-use TC;
- Phase 3 planner memo ON;
- oracle incoming;
- zero victim-future queries.

Do not enable scheduling-changing profiling.

In particular preserve the existing warning that:

`STRATA_VERIFY_PROFILE`

must remain **unset**, not set to `0`.

Implement the smallest instrumentation capable of associating:

### Host producer milestones

- oracle hook entry/exit;
- publication call entry/exit;
- publication acknowledgment wait begin/end;
- post-ack ownership update;
- remaining incoming planning;
- native plan construction;
- actual plan flag-A publication.

### Copy worker milestones

- publication command available;
- worker command observed;
- metadata update submit;
- CUDA completion observation;
- acknowledgment state publication;
- worker device/class/generation.

### GPU consumer milestones

- wait A begin/end for the actual consumer;
- relevant B/CPU waits if they mask completion;
- resident compute boundary as needed;
- shared branch completion/join where active;
- layer-split peer/handoff readiness where active.

Use bounded preallocated buffers.

No per-event file writes on the critical path.

No new device-wide synchronization.

No convenience barrier inserted just to align clocks.

No polling thread that changes scheduling materially.

No additional expert slots or capacity changes.

Record overflow and unsupported coverage explicitly.

---

# Clock-domain discipline

Do not directly subtract:

- host monotonic timestamps;
- GPU0 `%globaltimer`;
- GPU1 `%globaltimer`.

Establish bounded mappings at already safe boundaries.

Use a small fixed number of calibration observations, identical in CONTROL and TRACE.

Propagate uncertainty.

If the mapping is too noisy:

- keep interval bounds;
- use happens-before relationships;
- widen the attribution result.

Never replace uncertainty with an unjustified midpoint.

---

# Dependency reconstruction

For each wait-A event, identify what its host-side producer was doing.

Partition producer-side time without double counting into meaningful categories such as:

- publication acknowledgment;
- publication validation/commit outside acknowledgment;
- other oracle/history planner work;
- native plan construction;
- scheduler/wakeup gap;
- unknown.

Worker subphases inside acknowledgment remain subphases of acknowledgment.

Do not add them again as independent latency.

Build the dependency graph using actual:

- stream order;
- publication dependencies;
- shared branch fork/join;
- CPU/mapped readiness;
- peer/layer-split handoff;
- consumer wait.

A blocking wait is a readiness constraint, not an independent compute node added on top of its producer.

Validate graph reconstruction on synthetic or bounded known fork/join fixtures before trusting runtime attribution.

Require good reproduction of the recorded completion span or report residual uncertainty.

---

# Phase 4 STEP 3/5 — Six paired replay measurements

Use the existing frozen `math-rational` development tape.

Do not select another task based on timing.

The experiment remains:

- 3 CONTROL runs;
- 3 TRACE runs;
- same new binary;
- same workload;
- same policy;
- same buffers allocated where necessary;
- detailed trace switch is the only intended measurement difference.

Use the frozen order unless the repaired protocol provides a documented reason to change it:

```text
Block 1: CONTROL -> TRACE
Block 2: TRACE -> CONTROL
Block 3: CONTROL -> TRACE
```

The first complete pair is also the live smoke.

Do not perform an uncounted matching replay before it.

Record all attempts.

Do not rerun valid measurements merely because of unfavorable timing, CPU steal, or unexpected signs.

If a genuine instrumentation bug is found:

- preserve the failed evidence;
- make a substantive repaired version;
- do not mix versions within one pair;
- obey the protocol attempt cap.

---

# Instrumentation overhead gate

After the first pair, inspect:

- correctness;
- trace identity;
- buffer overflow;
- event coverage;
- scheduling perturbation;
- decode change;
- completion-wall change;
- work/transaction consistency.

For the final quantitative attribution gate, apply the repaired symmetric perturbation criterion.

A systematic large TRACE speedup is as suspicious as a systematic slowdown.

If timing perturbation exceeds the accepted range:

- do not call the instrumentation nonperturbing;
- retain the structural trace if useful;
- downgrade quantitative conclusions accordingly.

Do not tune instrumentation until timing happens to look favorable.

---

# Phase 4 STEP 4/5 — Attribution analysis

For each TRACE run report separately:

1. measured host acknowledgment time;
2. acknowledgment overlap with wait A;
3. producer/consumer linkage coverage;
4. uncertainty from clock mapping;
5. masking by shared work;
6. masking by CPU/mapped work;
7. masking by peer/layer-split dependencies;
8. unresolved host/scheduler gaps;
9. graph reconstruction residual.

Do not present:

```text
sum(publication wait)
```

as automatically equal to:

```text
request latency cost
```

Compute the repaired fixed-trace counterfactual scenarios from Part B.

At minimum distinguish:

### Primary constrained diagnostic scenario

Remove only the specifically defined avoidable coordination component while retaining known required metadata and safety dependencies.

Report:

```text
S_primary
```

with propagated uncertainty:

```text
[S_primary_min, S_primary_max]
```

### Idealized opportunity scenario

Move acknowledgment readiness to the earliest safe known predecessor allowed by the dependency evidence.

Report this separately as an upper-opportunity bound.

Do not describe it as directly achievable speedup.

If missing edges allow a zero contribution, preserve zero in the lower bound.

Unknown is not zero.

---

# Required Phase 4 interpretation

Use precise evidence-based conclusions.

Possible outcomes include:

### `PUBLICATION_ON_OBSERVED_DEPENDENCY_PATH`

Use only if:

- instrumentation gates pass;
- producer linkage is strong;
- the constrained primary scenario has a material path contribution;
- its uncertainty remains on the material side of the predeclared threshold.

### `PUBLICATION_SMALL_ON_TESTED_TRAJECTORY`

Use only if:

- instrumentation gates pass;
- even the relevant opportunity upper bound is clearly small.

### `PUBLICATION_MOSTLY_HIDDEN_ON_TESTED_TRAJECTORY`

Use only if:

- publication substantially overlaps wait A;
- another measured dependency absorbs most of that potential;
- the remaining path contribution is bounded small.

### `ATTRIBUTION_INCONCLUSIVE`

Use if:

- bounds straddle important thresholds;
- clock uncertainty is too large;
- dependency coverage is incomplete;
- different runs disagree materially.

### `INSTRUMENTATION_OR_FIDELITY_BLOCKED`

Use if:

- tracing changes execution too much;
- identities cannot be associated safely;
- capacity/scheduling is perturbed;
- traces overflow or alias;
- required correctness gates fail.

Do not force a positive publication result.

---

# Phase 4 STEP 5/5 — Synthesis, persistence, audit, cleanup

Produce a complete Phase 4 research record.

Include:

- corrected Phase 3 dependency note as prior context;
- final Phase 4 protocol;
- source/binary/model identities;
- exact instrumentation semantics;
- clock calibration method;
- instrumentation perturbation measurements;
- all six request outcomes;
- trace coverage;
- publication acknowledgment distributions;
- wait-A distributions;
- dependency graph;
- constrained counterfactual;
- idealized opportunity bound;
- uncertainty intervals;
- failures and repairs;
- limitations;
- recommended next experiment.

Preserve all negative results.

Use repository text-evidence publication workflow from `AGENTS.md`.

Large binary tapes/journals remain external according to repository policy.

Do not attempt to force oversized binaries into normal Git.

Record hashes and recovery status honestly.

Stop only identity-verified campaign-owned processes.

Verify GPU/port cleanup.

Verify ordinary serving launchers/configuration remain unchanged.

Run the required staged archive audit.

Commit and push all durable task-owned changes.

Verify the remote commit actually contains them.

Report the final remote SHA.

---

# Decision about what comes after Phase 4

Do not automatically start Phase 5.

The final report must answer:

1. Is the corrected Phase 3 live-divergence chronology now established or still unresolved?
2. Did the Phase 3 headline performance conclusion change?
3. Did TRACE instrumentation pass the symmetric perturbation gate?
4. What fraction of wait-A time overlaps publication acknowledgment?
5. How much of that overlap lies on the modeled dependent completion path?
6. What is the constrained primary counterfactual improvement interval?
7. What is the idealized opportunity upper bound?
8. Is publication coordination worth optimizing next?
9. If publication is mostly hidden, what dependency hides it?
10. If publication is small, what is now the largest measured remaining exposed mechanism?
11. Is it now justified to move to causal incoming prediction?
12. What single next experiment has the highest information value?

The final recommendation must follow from the measured evidence, not from the expectation that causal incoming prediction is necessarily next.

---

# Researcher autonomy

You may repair ordinary bugs, instrumentation problems, analysis errors, or documentation inconsistencies discovered during this goal.

You may make one bounded additional diagnostic experiment if it directly discriminates between the Phase 4 hypotheses and fits inside the execution budget.

For any deviation:

- state the hypothesis;
- explain why it is necessary;
- preserve the original evidence;
- preserve comparability;
- remain within scope.

Do not broaden this into:

- a new victim model;
- a new incoming predictor;
- a new scheduler;
- a multi-domain Phase 4 benchmark;
- production deployment.

Do not stop at the first technical problem if a bounded repair is possible.

Do not spend the remaining clock merely because time is available.

Complete the correction, repaired protocol, actual Phase 4 execution, analysis, repository publication, and cleanup in this one goal.
