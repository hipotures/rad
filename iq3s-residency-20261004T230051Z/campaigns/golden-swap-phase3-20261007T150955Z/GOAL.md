# /goal — Golden Swap Phase 3: Planner Cost, Exposed Wait, and Decision-Preserving Optimization

You are the research execution agent for the RaD project.

Work as a researcher, not merely as an implementer.

The objective is to determine whether a meaningful part of the remaining Golden Swap performance gap comes from repeated planner work and host/device coordination, and whether that cost can be reduced without changing the logical residency policy.

This is one complete research phase. Carry it through analysis, implementation, measurement, interpretation, documentation, repository persistence, commit, and push.

Follow the repository `AGENTS.md` for repository workflow, persistence, Git, evidence handling, and publication. Do not invent additional Git restrictions.

## Hard time budget

Maximum wall-clock research budget: **6 hours** from the start of the phase.

Use the time as a research budget, not as a target to consume.

At approximately **5h15m**, stop starting major new experiments. Use the remaining time to finish bounded validations, analyze retained evidence, write the report, audit artifacts, commit, push, and verify the remote commit.

If the research converges earlier, finish earlier.

## Progress reporting

Report progress visibly during execution.

Use:

`[PHASE 3 | STEP 1/5 START]`
`[PHASE 3 | STEP 1/5 DONE]`

and similarly through Step 5.

During live experiments also report the current:

- task
- block/pair
- arm
- completed / planned measurements
- elapsed time
- remaining research budget

For commands expected to run for more than roughly 30 seconds, emit a heartbeat approximately every 30 seconds where practical.

Give a brief meaningful progress update at least every 3–5 minutes during long execution.

Do not wait for user intervention between steps unless an actual external decision is required.

## Research context

This continues the existing Golden Swap investigation. Do not create a new unrelated research topic.

Start by synchronizing and reading the current repository state and `AGENTS.md`.

The relevant prior work includes at minimum:

- `iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/report.md`
- `iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase2-20261007T093357Z/report.md`
- `.../golden-swap-phase2-20261007T093357Z/results/diagnosis.md`
- `.../results/transaction-schema.json`
- `.../results/primary-table.csv`
- `.../results/queue-and-timing-diagnostics.json`
- `.../results/main-summary.json`
- `.../results/protection-opportunity-costs.json`
- `.../completion-audit.json`
- the Phase 2 source patch, analysis scripts, and reproduction instructions

Inspect source and retained evidence directly rather than relying only on this goal's summary.

Important established results from Phase 1 and Phase 2:

1. Oracle incoming still provides substantial theoretical/live replay headroom.

2. Phase 1 learned victim prediction contained real return-risk signal, but the live policy did not establish a latency gain.

3. Phase 2 established that **99.998328% of the original Phase 1 learned no-observed-use bytes were caused by publication followed by re-eviction before the intended first target/use**.

4. Minimal first-use transaction control removed that failure mechanism almost completely.

5. Extending protection for a fixed additional 48 routed-layer invocations after first use reduced transfer volume but materially increased nonlocal demand; do not repeat that experiment without new evidence.

6. Risk thresholds 0.2 versus 0.5 did not change retained calibration action hashes; do not spend this phase tuning an inactive threshold.

7. Matched cheap history and frozen logistic victim scoring produced:
   `NO_CONFIRMED_SCORER_DIFFERENCE`.

8. The taskwise Phase 2 timing criterion was met on:
   - `math-inventory`
   - `mixed-chinook`

   and not met on:
   - `code-archive`
   - `text-websocket`

   This is evidence on those recorded trajectories, not proof of domain specialization.

9. The independent RFC8259 continuous-tail experiment showed that prefix-unused survivors can subsequently be useful; finite end-of-tape nonuse must not automatically be labeled waste.

10. Phase 2 measured substantial planner activity. Median oracle planner time was roughly 1.5–1.7 seconds/request for causal TC modes, but feature/model/selection/publication timers are nested and may overlap GPU work. Their values must not be summed into a fictitious exposed latency.

11. There were roughly 21 million copy-cost veto scan opportunities across the 12 main requests for each causal policy, versus only roughly 120–126 thousand published admissions. Repeated negative evaluation is therefore a plausible optimization target.

12. The current cost guard still uses an assumed operating point of 160 us net benefit per routed entry. This is not a measured exclusive CPU fallback latency.

13. Exact exposed planner/publication stall remains unmeasured.

14. Incoming prediction is still oracle/privileged. Phase 3 must not begin a causal incoming predictor project.

## Primary research question

Determine:

> How much of the remaining Golden Swap performance cost is caused by repeated planner evaluation and exposed host/device coordination, and can that cost be reduced while preserving the logical scheduling decisions?

The phase must discriminate between at least these possibilities:

### H1 — implementation overhead is materially hiding policy benefit

Repeated planner evaluation and/or publication coordination lies on the critical path often enough that reducing it produces a measurable request/decode improvement.

### H2 — planner CPU work is mostly overlapped

Planner counters fall substantially after optimization, but request latency changes little because the removed work was not materially exposed.

### H3 — the remaining limitation is policy economics

Planner overhead can be reduced, but losing workloads remain neutral/negative because residency, transfer timing, victim damage, or nonlocal execution economics dominate.

### H4 — the proposed caching is not safely decision preserving

State dependencies are broader than expected and cached negative decisions become stale, changing logical actions or invalidating correctness.

Negative results are valuable.

## Experimental boundaries

Keep the scientific scope narrow.

Do **not** in this phase:

- train a new victim model;
- change the frozen logistic weights;
- add a new incoming predictor;
- change routing/top-k;
- skip or approximate expert computation;
- change model weights or quantization;
- change K=24;
- change PCIe fraction 0.28;
- change the 100 us pool spin policy;
- change MTP settings;
- change KV policy;
- add GPU memory capacity;
- redesign cross-GPU execution;
- add Tail Shedding;
- retune Phase 2 based on favorable main results;
- silently migrate ordinary serving to another Strata version.

Ordinary user serving must remain unchanged.

Use separate experimental source/build/runtime namespaces as required.

Preserve the five charged spare slots and existing physical capacity accounting unless a correctness repair proves that existing accounting is wrong.

## STEP 1/5 — Exploit existing evidence before running GPU experiments

First determine what can already be answered from retained Phase 0/1/2 evidence.

Do not rerun inference merely to regenerate quantities that can be reconstructed from existing journals, traces, telemetry, JSON, or gzip evidence.

Produce a compact cross-task analysis for at least the four Phase 2 main regression tapes and, where available, the independent RFC8259 tape.

Extract or derive, where supported:

- publication → first-use distance;
- admission resident lifetime;
- first-use protected lifetime;
- distinct routed-layer uses per admission;
- repeated admission/reload recurrence;
- victim-return distance;
- transactions/swaps per verifier window;
- copy bytes per useful admission;
- avoided nonlocal entries per copy byte;
- publication-to-target slack;
- target-ready versus late publication distribution;
- copy issue/stage/copy/publication timing distributions;
- class-cap/protection pressure;
- planner scan/opportunity counts;
- current local/CPU/mapped demand;
- any already-recorded burstiness/reuse-distance summaries from Phase 0 that remain comparable.

Treat censoring correctly.

Do not classify end-of-tape survivors as permanent nonuse.

Distinguish:

- request-domain differences;
- actual input/context-length differences;
- routing/residency trajectory differences.

With only four primary tapes, do not infer a universal workload classifier.

The goal is to determine whether existing evidence already explains part of the Inventory/Chinook versus Archive/WebSocket split and to identify which questions still require new measurements.

If a requested metric cannot be reconstructed, state exactly which missing field prevents it.

## STEP 2/5 — Identify repeated planner work and design a decision-preserving optimization

Audit the actual Phase 2 planner implementation and instrumentation.

Map the dependency state of each major rejection/selection decision.

The leading optimization hypothesis is:

> repeated incoming copy-cost rejection is recomputed many times while all state relevant to that negative decision is unchanged.

Investigate that hypothesis directly.

A likely intervention is caching negative copy/admission decisions until the complete state on which the decision depends becomes invalid.

However, do not blindly implement a cache because this goal suggests one.

If source inspection identifies a smaller or safer common planner optimization that addresses the same repeated work, you may use it.

The optimization must preserve the existing policy semantics.

Explicitly determine invalidation dependencies such as, where applicable:

- current routed-layer invocation / horizon movement;
- incoming future-use count window;
- resident/nonresident state;
- ownership generation;
- victim availability;
- protection state;
- protection-cap occupancy;
- causal history/scorer version;
- copy queue state;
- target/deadline;
- byte class/device;
- publication or expiry events.

Different cached quantities may legitimately have different invalidation rules.

Do not use one coarse cache key merely because it is easy.

Instrument cache:

- lookups;
- hits;
- misses;
- invalidations by reason;
- avoided scans/evaluations;
- retained evaluation count;
- cache memory;
- cache maintenance time.

Keep the implementation bounded and simple.

Do not introduce a broad new scheduler architecture.

## STEP 3/5 — Prove logical parity and instrument exposed wait

Before headline timing:

### A. Decision parity

Create a same-source/same-binary switchable OFF/ON implementation where practical:

- OFF = Phase 2 logical planner behavior;
- ON = optimized planner behavior.

For deterministic replay state, prove that the optimization preserves the logical decisions.

Compare at least:

- candidate acceptance/rejection;
- selected incoming expert;
- selected victim;
- NO_SWAP decisions;
- protection/cap decisions;
- logical admission order;
- logical completed copy payload where timing does not legitimately alter readiness;
- ownership transitions;
- required routed work.

Use hashes or structured decision traces rather than only final aggregate counters.

If exact parity fails, identify whether it is:

1. a correctness bug/stale cache;
2. a genuine timing-induced asynchronous schedule difference;
3. an instrumentation artifact.

Fix correctness failures before timing.

Do not redefine a parity failure as acceptable merely because performance improved.

### B. Critical-path instrumentation

Phase 2 has aggregate/nested timers but not exact exposed stall attribution.

Add the smallest reliable instrumentation that can answer:

> At the point where inference needs a plan, publication, or resident expert, how long is useful downstream work actually blocked because the planner/publication result is not ready?

Measure or bound, where architecturally possible:

- planner start/end;
- plan-ready time;
- copy-ready/completion time;
- publication eligibility;
- publication completion;
- dependent consumer readiness;
- actual host/device wait attributable to that dependency.

Prefer buffered or low-overhead instrumentation.

Do not add heavy tracing to the timed critical path unless necessary.

If exact GPU-exposed wait cannot be measured safely, establish defensible lower/upper bounds and explain the missing synchronization information.

Never derive exposed wait by summing nested timers.

### C. Instrumentation overhead guard

Before the main matrix, verify that the new binary with optimization OFF remains behaviorally equivalent to the frozen Phase 2 baseline.

Use a bounded development/reproduction check.

If new instrumentation itself materially perturbs timing, reduce it, gate it, or measure its overhead before proceeding.

## STEP 4/5 — Bounded interleaved live experiment

After correctness/parity gates pass, run a bounded live experiment.

### Primary policy

Use the matched cheap-history + minimal transaction-control policy as the primary Phase 3 planner target.

Reason: Phase 2 found no confirmed logistic advantage and history has the lower scoring cost.

This is a research choice for isolating common planner overhead, not a claim that history is universally superior.

The frozen logistic implementation must still pass offline/decision-parity checks where the common planner path applies.

A small live logistic sensitivity check is allowed if time remains and it does not compromise the primary matrix.

### Main regression tasks

Use:

- `code-archive`
- `math-inventory`
- `text-websocket`
- `mixed-chinook`

Primary same-binary arms:

- `PLANNER_BASELINE` — Phase 2 history+TC semantics, optimization disabled;
- `PLANNER_OPT` — identical policy, optimization enabled;
- `REPLAY_CURRENT` — contemporary current-policy reference.

Prefer **3 counterbalanced blocks per task** if the time budget allows.

This is 36 primary requests.

Do not add repetitions merely because one result is favorable or unfavorable.

### Independent source

Use the existing `text-json-rfc8259` continuous tape as an independent-source check.

Prefer **2 counterbalanced blocks** across:

- `PLANNER_BASELINE`
- `PLANNER_OPT`
- `REPLAY_CURRENT`

This adds 6 requests.

If a cleaner newly captured independent source is scientifically justified and cheap, it may be added only after the required matrix is complete and only within the fixed time budget.

Do not expand into a broad new corpus.

### Preserve exact workload comparability

Use the same completed logical replay prefix/work for within-task comparisons.

Do not compare runs truncated to equal wall time.

Keep all required expert computation and MTP work unchanged.

Record:

- actual input;
- emitted replay tokens;
- verify windows;
- work hashes;
- initial-state hashes.

### Primary measurements

For every timed request retain at least:

- decode time;
- replay-equivalent TG;
- completion-inclusive request wall;
- local / CPU / mapped entries;
- copy GB;
- admissions/publications;
- target-ready and late publications;
- victim absence/reloads;
- planner total time;
- selection/enumeration time;
- repeated cost-veto evaluations;
- cache hit/miss/invalidation statistics;
- publication coordination time;
- directly measured or bounded exposed planner/publication wait;
- CPU utilization/steal;
- GPU utilization/clocks/power;
- PCIe state;
- RAM/VRAM;
- correctness/decision parity status.

Do not correct results for CPU steal after the fact.

Retain anomalous runs unless they violate a predeclared validity rule.

### Phase 3 descriptive success criteria

Predeclare before inspecting main timing results.

#### Mechanism success

Require:

- exact logical decision parity in deterministic validation;
- no correctness or ownership regression;
- substantial reduction in repeated unchanged planner evaluations;
- measurable reduction in planner CPU work.

A useful target is at least **50% reduction in the targeted repeated evaluations**.

If less is achievable because correct invalidation is frequent, report that rather than weakening correctness.

#### Critical-path success

Evidence for H1 requires both:

- lower planner/exposed wait;
- lower request/decode time in matched pairs.

Do not call lower CPU planner time alone a latency success.

#### Timing result

Use paired within-block ratios.

For each main task report:

- median paired decode change;
- median paired completion-wall change;
- all block signs;
- range;
- baseline and optimized raw medians.

A practical descriptive gain may use a threshold around 3%, consistent with prior campaign conventions, but do not present three pairs as statistical proof.

Also report whether the optimization changes the prior Phase 2 classification:

- Inventory / Chinook positive;
- Archive / WebSocket neutral/negative.

Do not hide a workload because it remains negative.

### Interpretation gates

Interpret the result explicitly:

#### If planner work ↓, exposed wait ↓, and latency ↓

Conclude that implementation/coordination overhead was materially hiding Golden Swap benefit.

Quantify how much of the improvement is attributable to the optimized common planner path as far as the instrumentation supports.

#### If planner work ↓ strongly but exposed wait / latency do not

Conclude that the removed CPU work was mostly overlapped or non-critical.

Stop pursuing planner micro-optimization as the primary direction unless another clear exposed component remains.

#### If Inventory/Chinook improve but Archive/WebSocket remain neutral/negative

Investigate policy economics as the next likely bottleneck.

Use existing lifetime/reuse/slack analysis to identify the most discriminating next hypothesis.

#### If negative workloads become positive after planner optimization

This is strong evidence that prior task differences were partly implementation-overhead dominated.

Do not extrapolate beyond the tested tapes without independent confirmation.

#### If logical parity fails

Do not use the timing result as the headline Phase 3 result.

Repair or finish with a negative/inconclusive parity conclusion.

## STEP 5/5 — Synthesis, audit, reproduction, persistence

Produce a durable Phase 3 campaign record in the existing Golden Swap research area.

Do not create a disconnected research topic.

The final report must clearly separate:

- established prior facts;
- new Phase 3 measurements;
- derived conclusions;
- remaining hypotheses;
- unmeasured quantities.

Include at minimum:

1. exact source/binary/model identities;
2. Phase 2 baseline provenance;
3. existing-data analysis from Step 1;
4. planner dependency/invalidation model;
5. optimization design;
6. decision-parity evidence;
7. instrumentation semantics;
8. instrumentation-overhead check;
9. complete timed matrix;
10. paired results;
11. cache effectiveness;
12. critical-path/exposed-wait result;
13. resource telemetry;
14. failures/repairs;
15. limitations;
16. strongest next experiment.

Preserve negative results.

Do not overwrite Phase 1 or Phase 2 evidence.

Keep original Phase 2 results immutable.

Provide tested reproduction instructions.

Use the repository text-evidence publication workflow from `AGENTS.md` for eligible completed logs/JSON/text evidence.

Large binary tapes/journals remain external/local according to repository policy; record their hashes/locations/manifests rather than attempting to force oversized binary evidence into normal Git.

Run the repository archive/audit checks required by `AGENTS.md`.

Commit and push all durable task-owned work according to `AGENTS.md`, then verify the canonical remote contains the final commit.

Report the pushed commit SHA.

Ordinary serving configuration and launchers must remain unchanged unless an explicitly required reproducibility metadata update is necessary; do not deploy the experimental runtime.

## Researcher autonomy

You may:

- repair bugs discovered during this phase;
- improve instrumentation if the first design cannot answer the question;
- change the optimization strategy if source evidence disproves the initial caching hypothesis;
- run a small discriminating side experiment;
- implement one bounded original idea of your own if it directly helps answer the Phase 3 question.

When doing so:

1. state the hypothesis;
2. explain why the change is informative;
3. preserve the original comparison;
4. keep it within the same hard time budget;
5. do not silently broaden into Phase 4.

Do not stop at the first implementation failure.

Repair ordinary research/tooling issues autonomously when safe.

Do not spend large amounts of time polishing infrastructure that does not improve the evidence.

## Required final decision

End the Phase 3 report and final handoff with one primary evidence-based conclusion chosen or carefully formulated from the observed result, such as:

- `PLANNER_OVERHEAD_MATERIALLY_EXPOSED`
- `PLANNER_WORK_MOSTLY_OVERLAPPED`
- `PLANNER_OPTIMIZED_POLICY_ECONOMICS_REMAIN_LIMITING`
- `DECISION_PRESERVING_OPTIMIZATION_INCONCLUSIVE`
- another precise conclusion if the evidence demands it

Also answer explicitly:

1. How much repeated planner work was removed?
2. Did logical decisions remain identical?
3. How much planner CPU time was removed?
4. How much of that reduction was actually exposed on the inference critical path?
5. Did decode time improve?
6. Did completion-inclusive wall improve?
7. Did Archive/WebSocket change classification?
8. Did Inventory/Chinook retain or increase their gains?
9. Did current-vs-Golden-Swap practical advantage improve?
10. Is cheap history still the appropriate victim-side baseline?
11. Is there now enough evidence to proceed to causal incoming prediction?
12. If not, what single unresolved mechanism has the highest information-value next experiment?

Do **not** start Phase 4 or causal incoming prediction in this goal.

Stop after the Phase 3 conclusion, repository audit, commit, push, and verified handoff.