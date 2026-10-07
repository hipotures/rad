# Golden Swap Phase 4: publication acknowledgment and consumer wait

Status: **PLANNED_NOT_STARTED**. This document is the execution brief for a later,
explicit start. Preparing this directory does not start its clock, build the
runtime, or authorize an automatic follow-on campaign. Once asked to execute
this brief, carry the bounded experiment through implementation, validation,
measurement, analysis, cleanup, commit, push, and remote verification without
asking the operator to launch each internal step.

## 1. Objective and decision

Determine how much of the remaining GPU plan-A dependency wait is associated
with the host waiting for an expert residency-map publication acknowledgment,
and how much of that delay reaches the request's dependent execution path.
Keep the existing history victim rule, first-use protection, and Phase 3
incoming-query memoization fixed. The output is a defensible attribution and
one recommended next intervention, including a negative or unresolved result.

The project objective is useful local MoE execution time. This experiment
establishes whether publication coordination deserves an optimization before
investing in a causal incoming predictor. A reduction inferred from a fixed
trace is a conditional diagnostic estimate, not a measured acceleration.

Questions to answer:

1. At each actual GPU plan-A wait, what was its host producer doing?
2. How much waiting overlaps publication acknowledgment, other oracle work,
   native plan construction, or an unresolved host scheduling gap?
3. Within acknowledgment, what is known about worker wakeup, metadata submit,
   completion observation, and return to the host? Which intervals remain mixed?
4. How much could shorten the recorded dependent path after accounting for
   shared work, CPU/mapped completion, and inter-device handoff?
5. Is the estimate precise and unperturbed enough to choose a next experiment?

## 2. Starting evidence and hypotheses

Read the [Phase 3 report](../golden-swap-phase3-20261007T150955Z/report.md),
[dependency audit](../golden-swap-phase3-20261007T150955Z/results/planner-dependencies.md),
[development guard](../golden-swap-phase3-20261007T150955Z/tests/development-guard.json),
[reproduction](../golden-swap-phase3-20261007T150955Z/reproduce.md), and
[Phase 2 report](../golden-swap-phase2-20261007T093357Z/report.md).
Use [input-manifest.json](input-manifest.json) for the exact retained files.

Established in Phase 3: about 97% of the targeted incoming queries were reused,
but main median host CPU savings were only 63–133 ms and no main task passed the
greater-than-3% incremental practical gain gate. Optimized main requests still
had median publication coordination of 624–811 ms and plan-A waits of
1,840–2,158 ms. Those ranges are historical motivation, not additive costs or
fresh controls for this experiment. The development tape already has a working
end-to-end replay. No confirmed logistic advantage warrants another scorer study.

The inspected source at Phase 3 commit
`f3b4f19157b39ae017e2fd91814c8f5728e3b1cc` establishes this producer chain:

```text
expert_pool_dispatch_multi
  -> q4_oracle.host
     -> publish completed promotions
        -> worker writes two residency-map entries and observes CUDA completion
        -> host receives acknowledgment and updates its residency/generation state
     -> incoming planning
  -> native GPU plan construction
  -> Verifier::publish_plan / flag A
  -> GPU wait-A completes -> required resident expert computation
```

The weight payload has completed before `publish()` enters this acknowledgment
path. Do not label all acknowledgment time as expert-weight DMA. A host hook
can publish a worker belonging to the other device: record producer and worker
devices separately. Preserve all real ownership and reader checks.

Hypotheses, with none presumed true:

| ID | Explanation | Distinguishing evidence |
|---|---|---|
| H-PUB | Publication acknowledgment materially delays required execution | Identified producer edge, robust wait overlap, and material fixed-trace path contribution after competing dependencies |
| H-OTHER | Other host planning or scheduling dominates plan-A delay | Non-publication producer intervals account for most attributable delay; publication contribution has a small upper bound |
| H-HIDDEN | Publication blocks a stage but is largely hidden by other required work | Stage overlap is substantial while shared/CPU/peer dependencies absorb its modeled path effect |
| H-OBS | Instrumentation, clock uncertainty, or missing edges prevent attribution | Failed overhead/coverage gate or wide attribution bounds; report the missing evidence |

## 3. Frozen runtime and workload

Use a separate derivative of the verified Phase 3 source. Reconstruct it from
the public Strata base and the retained cumulative patch if the local checkout
is unavailable. Never edit Phase 3 source/build/output in place. Record the new
source, cumulative patch, binary SHA256, build commands, and all configuration
hashes. All measured arms use this one new binary.

Keep Qwen3.8-Flash-Next **UD-Q4_K_XL**, revision
`38bb39ee97821de2c9009abb7e93950eec396e66`; two RTX 4090 24 GiB; K=24;
PCIe fraction=0.28; pool spin=100 us; 15 workers; MTP spec=4/min-p=0.5;
INT8 KV; kv-resident=32768; native prefill=auto; suffix/reuse OFF; serial replay.
Keep all 48 main layers, routes, coefficients, token/window shapes, MTP work,
three expert byte classes, and five charged spares (17,305,600 bytes).
Full immutable expert backing stays in RAM.

Both arms retain full oracle incoming, E64 incoming eligibility/order, the
inherited privileged current-window safety input, cheap history/native victim
scoring, minimum first-use transaction control, post-use interval=0,
threshold=0.5, the assumed 160 us cost operating point, and planner memo ON.
Victim-future access must remain zero. This continues conditional oracle replay;
neither causal production readiness nor natural-generation quality is tested.

The sole inference task is the previously exposed **math-rational** development
tape. It was selected because Phase 3 already validated its replay and wait
instrumentation, not because of a new timing result. Its source is the retained
E026 numerical/CPython fractions workload, PSF-2.0, no executed agent tools.

| Quantity | Frozen value |
|---|---|
| Configured total context | 32,768 |
| Actual input / emitted output | 10,943 / 2,048 tokens |
| Main verifier windows / routed-layer invocations | 653 / 31,344 |
| Main routed lane entries / MTP routed entries | 1,146,240 / 18,480 |
| Tape bytes | 267,625,660 |
| Tape SHA256 | `7aaf9c90db0394577b96a7ef8a09e75d07d590ac30623f3f75f41774dae899a5` |
| Initial-state sidecar SHA256 | `bef7b3ed1546b7e8898c6584327d16f4e394efb5f457a67973d40fcd2b8bce4d` |

Verify the header, work and sidecar fingerprints before execution. Reuse the
saved 4,096-input/64-output warmup. Every attempt gets a fresh server, native
prefill, and the complete tape, including final commit, drain, restoration,
observation/trace flush, and clock/readback overhead. Record actual terminal
context position from execution, not an assumed input-plus-output sum.
These are repeated observations of one development trajectory, not generalization.

## 4. Five execution steps and resource envelope

The proposed execution cap is **4 hours** from explicit execution start,
including reading, dependency setup, build, repair, fixtures, measurements,
analysis, publication, and cleanup. Record UTC start/deadline and monotonic
start immediately at that time; never inherit a prior campaign clock or use the
directory timestamp as the start. At T+3h15 stop starting substantial work;
reserve at least 45 minutes for finalization. Finish earlier if decisive.

| Step | Work and exit evidence | Planning allowance |
|---|---|---|
| 1/5 | Verify inputs/source, map real producer/consumer and shared/peer edges, freeze trace schema | 25 min |
| 2/5 | Minimal buffered instrumentation, clock/coverage fixtures, safety/parity gates | 90 min |
| 3/5 | Six requests in saved paired order; first pair doubles as end-to-end smoke | 30 min |
| 4/5 | Reconstruct intervals/dependency graph, uncertainty, overhead and attribution | 45 min |
| 5/5 | Reproduce analysis, audit, archive, cleanup, commit/push/verify | 50 min |

Allowances sum to the cap and are estimates, not measured future runtimes.
Phase 3's five new-binary development runs took 109–146 seconds each including
startup/warmup/shutdown; six comparable requests suggest 11–15 minutes of
execution before repair or added instrumentation. Re-estimate after the first
pair. Do not start another request without its timeout plus cleanup reserve.

Use atomic `progress.json`, readable `STATUS.md`, append-only `progress.jsonl`,
`DECISIONS.md`, and an attempt ledger in a fresh `runs/<execution-UTC>/` namespace.
Show step, version, block/arm, completed/remaining work, elapsed, remaining
budget, next action, and measured ETA range or `unknown`. Emit flushed process
heartbeats every 30 seconds; poll at bounded intervals; send user updates at
safe boundaries. Avoid device synchronization for progress.

No concurrent inference, compilation, training, downloads, or heavy analysis/
hashing during timing. Record per-phase CPU/steal, RAM/swap, both GPUs' memory,
utilization, power, and clocks without changing settings. Never kill a process
using only an old PID file; verify owned PID, creation time, command and group.

## 5. Minimal instrumentation contract

Inspect [source-map.md](source-map.md) before implementation. In particular,
**leave `STRATA_VERIFY_PROFILE` unset**: source uses its presence to enable
`prof_on_`, which disables shared-stream fork/join overlap. Setting it to `0`
still enables it. Reusing that profiler would confound this experiment.
Existing pool text tracing and broad stage profiling also remain disabled.

Introduce an opt-in detail switch (proposed name
`STRATA_Q4_PUBLICATION_TRACE`, not implemented at planning time). Preserve the
existing aggregate wait instrumentation in both arms. Instrument the existing
wait kernel and producer locations with preallocated bounded buffers. No
per-event file writes, device-wide synchronization, new polling thread, mutex
contended by every event, or changed fences/stream dependencies.

Required observations:

| Scope | Buffered milestones |
|---|---|
| Host dispatch | Hook entry/exit; publication call entry/exit; precise acknowledgment wait begin/end; subsequent incoming planning; native plan build; before/after actual flag-A store |
| Copy worker | Command available/observed; metadata-submit begin/end; existing CUDA-completion observation; ack state store/notify; transaction generation and worker device/class |
| GPU | Per-invocation wait A/B/CPU begin/end in the existing wait kernel; resident/mapped computation and combine boundaries needed for dependency reconstruction |
| Other dependencies | Actual shared branch fork/completion/join and layer-split handoff/consumer readiness; inactive branches explicitly recorded |
| Integrity | Sequence/record counts, overflow, clock domain, sampling mask, and missing/unsupported events |

Use host monotonic timestamps in one declared clock domain; store thread CPU
separately if needed. A CUDA event observed complete on the host is not the
exact end of DMA. Do not invent a DMA-only duration from it. Worker notification
to wakeup can be bounded with before/after stamps; retain those bounds.

Identify each consumer with request generation, main/MTP role, verifier/device,
window, global layer, token-group bounds, and flag/ring generation. Flags reset
and values repeat: a raw ring value, timestamp proximity, layer, or expert ID
alone cannot identify the consumer. Link each acknowledgment to its admission
generation and host dispatch; distinguish publication of expert residency from
publication of the GPU execution plan. Support zero/multiple publications per
hook and a worker on a different device. Never collapse lane entries into copies.

Record GPU timestamps in their own device domains. Repeated graph launches
must write distinct request/window slots; never retain only the last replay of
a captured pointer. Guard overflow and reset at warmup/request boundaries.
If graph capture prevents a safe request-indexed recorder, repair the recorder
before inference rather than introducing a new per-window barrier.

Allocate at most 64 MiB additional host trace storage and 8 MiB per GPU as an
upper bound, using the smallest sufficient record layout. Allocate the same
buffers in both arms before timing, inside existing headroom; attest identical
expert capacities and spares to Phase 3. If allocation changes capacity or fails,
reduce the trace layout before running. Do not remove expert slots to fit it.
Read back and flush after existing safe completion and charge this to wall time.

For shared/combine endpoints, prefer stores inside existing kernels. Any extra
stamp launch must be listed and covered by the overhead guard; it may not
serialize a fork, change stream priority, or reuse the scheduling-changing
profiler. Unsupported endpoint coverage stays unknown.

## 6. Clock and attribution method

Never subtract raw host and GPU timestamps or assume both GPUs share a clock.
At already safe request boundaries, take bounded calibration samples per GPU:
host times bracketing submission/completion of a device stamp bound when that
stamp occurred. Use start/end samples, check drift/residuals, and propagate
mapping uncertainty. Freeze a small calibration count before the first pair;
use the same work in both arms and charge it. No new decode-wide barrier.

Treat an affine mapping as an empirically checked assumption, not a guaranteed
clock identity. If VM scheduling makes brackets too wide, keep interval bounds
or logical happens-before evidence. Do not replace uncertainty with midpoint
subtraction. Do not add repeated full requests just to obtain prettier clocks.

For each wait A, construct disjoint producer-state intervals: publication
acknowledgment; other publication checks; remaining oracle/history/planning;
native plan construction; dispatch/wakeup or unresolved gap. Nest worker phases
inside acknowledgment and never add them twice. Intersect intervals with the
mapped GPU wait, propagating clock bounds. Report observed overlap separately
from dependency-based path contribution.

Build an offline dependency graph from measured producer/consumer edges,
in-stream order, shared branch joins, CPU/mapped flags, and inter-device handoff.
The baseline graph must reproduce the recorded completion span to within 1%
of decode time, with every residual/unmeasured edge explicit. Remove duplicate
overlapping intervals by union; never sum stalls from two devices as wall time.
Represent a blocking wait as a readiness constraint on its producer and
consumer. Do not add the wait duration as another compute node after already
accounting for the producer that caused it. Validate this on synthetic fork/join
fixtures before interpreting a runtime graph.

Compute a **fixed-trace sensitivity interval** by shortening only acknowledgment
readiness, from unchanged duration to the earliest known completed-weight
predecessor, while retaining recorded model work, admission decisions and
dependencies outside that acknowledgment subgraph. This idealizes the metadata
and notification operations within the subgraph; list those operations rather
than double-counting their host wait as independent work. Propagate using
maximum predecessor completion at joins. Also report a tighter scenario that
retains measured metadata-service constraints when those are actually known.
Zero acknowledgment is an idealized upper opportunity, not a safe executable
policy: some metadata work is required.
Missing competing edges force a wider bound, including zero when necessary.
Do not move downstream readiness earlier merely by subtracting one timer from
decode. Record CPU/mapped and shared-path masking explicitly.

Distinguish three outputs: measured host acknowledgment time; measured/bounded
consumer overlap; and modeled change to recorded completion. Even a precise
modeled contribution does not establish an achievable speedup or unchanged
policy under a future asynchronous publication implementation.

## 7. Fixtures before complete replay

Run compiled native fixtures before the six-request sequence. Reuse relevant
Phase 3/2 safety cases, with actual outcomes recorded:

- Known ready-flag and delayed-producer cases on both GPUs; delay belongs only
  in the fixture. Test acknowledgment fully before wait, fully inside wait,
  and hidden behind a longer shared dependency; verify recovered bounds.
- Request reset, repeated ring values/windows, multiple token groups, graph
  replay indexing, warmup versus measured request, MTP labels, zero/multiple
  publications and cross-device worker association.
- Missing event, buffer overflow, ambiguous clock mapping, duplicate generation,
  and missing peer/shared edge must fail coverage or widen bounds, never yield
  an attractive exact attribution. Test the offline graph on known small forks.
- OFF/ON deterministic scheduling parity on this tape: candidate/NO_SWAP,
  generation/lifetime, work, ownership and byte outcomes match under the same
  simulated completion schedule. No new victim-future calls.
- Existing safe copy completion, publication recheck, protected victim/reader,
  class/device bounds, repeated spare use, all-protected NO_SWAP, cancellation,
  final drain/restoration, next-request reset and sampled bytes for active classes.

Require model/tape/work/route/coefficient/shape/initial-state checks in the real
end-to-end replay. Structural validation alone is insufficient. The first
OFF/ON pair is also the live smoke; it counts toward the attempt caps. Freeze
the binary/config/schema before that pair; retain its valid measurements even
if slow. Do not run an uncounted matching preflight or final reproduction.

## 8. Paired request order and overhead gate

The two arms are identical except for detailed recording:

| Arm | Phase 3 optimized history+TC | Aggregate wait counters | New detailed trace |
|---|---|---|---|
| CONTROL | ON | ON | OFF |
| TRACE | ON | ON | ON |

Use [configs/run-order.json](configs/run-order.json): block 1 CONTROL→TRACE,
block 2 TRACE→CONTROL, block 3 CONTROL→TRACE. Six requests total. This is an
instrumentation comparison, not another current/full-oracle/scorer matrix.
No additional source task, long-context matrix, delay injection during replay,
or publication scheduling change is included.

At most three attempts per unchanged task/binary/settings/measurement point,
including smoke, invalid startup, failed and reproduction attempts. Record all
attempts. A genuine repair receives a new substantive version, an explanation
and a fresh paired order; no mixing binary versions within a pair. Permit at
most one instrumentation repair and at most 12 inference attempts across this
execution, all under the same clock. Invalid evidence stays invalid, not deleted.
Do not rerun a valid point to improve signs or remove CPU steal.

After the first pair, inspect fidelity, event association, gross overhead and
remaining budget. If unsafe or overflowed, stop inference and repair. If either
decode or completion-wall overhead exceeds 10%, diagnose before continuing.
Complete the three pairs if safe and usable; do not stop on an attractive trace.

Declare detailed instrumentation acceptable for quantitative attribution only
when median paired decode and completion-wall increases are each at most 3%,
fewer than two pairs exceed 5% on either metric, and no pair differs by more
than 10% in absolute value on either metric. A large speedup can also indicate
scheduling perturbation. Check workload/transaction distributions and first
visibility divergence in addition to timing; low overhead alone is insufficient.
These are small-N engineering gates, not a test proving zero overhead.

Clock/coverage requirements for a quantitative result:

- No corrupted/aliased event identities, trace overflows or unsafe publication.
- All expected wait-A records and completed publication generations reconcile;
  deterministic unsupported paths are explicitly excluded from denominators.
- At least 99% of observed wait-A time is linked to the correct producer event;
  unknown intervals remain in the total and in conservative bounds.
- Clock uncertainty, missing competing dependencies, and graph residual must
  be propagated. A precise material/small classification requires its bounds
  to stay on the same side of the declared threshold, not merely a point estimate.

If only two complete pairs survive caps/deadline, report a partial descriptive
result; do not claim the three-pair decision rule passed. After 45 minutes on a
nonessential instrumentation blocker, switch to a bounded logical/interval
diagnostic or report the blocker rather than consume the reporting reserve.

## 9. Analysis, decision rules and deliverables

For each run report actual input/output/windows; prefill, decode, tok/s,
completion-inclusive wall, startup/warmup/shutdown; all existing work and
transaction counters; per-device wait A/B/CPU; host phase CPU/wall; metadata
versus expert payload; trace memory/readback bytes; CPU/steal and GPU telemetry.
Archive exact configuration and binaries' identities. Unknown is not zero.

For each complete pair compute TRACE/CONTROL decode and wall changes. Report
all values and min/median/max; retain slow observations. For the three TRACE
runs report per-device and whole-request attribution bounds, counts, phase
percentiles, longest waits, coverage/uncertainty, and graph reconciliation.
Do not use historical full-oracle times as a new gain-retention denominator.

The following are prioritization rules, not performance claims:

| Primary conclusion | Required evidence | Next action to recommend |
|---|---|---|
| PUBLICATION_ON_OBSERVED_DEPENDENCY_PATH | All gates pass; fixed-trace sensitivity lower bound exceeds 3% of decode in every TRACE run | Design one safe publication-coordination optimization, then measure it with same-policy controls |
| PUBLICATION_SMALL_ON_TESTED_TRAJECTORY | Gates pass; idealized contribution upper bound is below 1% in every TRACE run | Prioritize the largest measured remaining host/CPU/mapped component, with its uncertainty |
| PUBLICATION_MOSTLY_HIDDEN_ON_TESTED_TRAJECTORY | Publication overlaps wait A substantially, but complete competing edges bound path contribution below 1% in every TRACE run | Investigate the dependency that absorbs it; retain stage-versus-wall distinction |
| ATTRIBUTION_INCONCLUSIVE | Intermediate/variable bounds, insufficient valid pairs, or incomplete clock/dependency coverage | State one smallest missing measurement |
| INSTRUMENTATION_OR_FIDELITY_BLOCKED | An unrepaired fidelity, indexing, capacity or overhead failure prevents interpretable traces | Preserve failures and the minimal repair required |

For the hidden classification, predeclare substantial overlap as a lower bound
of at least 20% of total wait-A time in every TRACE run. Otherwise use the small
classification. Thresholds are engineering choices fixed before measurement.
Do not claim this one development trajectory represents all domains or decide
that incoming prediction is valuable solely because publication is small.

Preserve: versioned protocol/schema/source map, input and large-artifact
manifests, patches and obtainable dependency bases, fixtures with failures and
repairs, run order and ledger, raw traces, compact CSV/JSON tables, an annotated
timeline with uncertainty, report, audit, and exact reproduction commands.
Analysis must regenerate from immutable raw files into a fresh output namespace.
Use retained runs for reproduction; a fourth matching live replay is prohibited.

Follow root AGENTS.md for storage and Git. Completed JSON/JSONL/log/txt evidence
gets whole-file gzip copies strictly below 10 MiB, with originals unchanged and
omissions recorded. Model weights, binaries and original binary tapes remain
external with recovery status; the existing tapes have no identified independent
off-host backup. Do not describe hashes as backups.

At completion stop only identity-checked owned processes; verify GPU/port cleanup
and preserved normal launchers/weights/prior campaigns. Commit task-owned changes,
run the staged archive audit, push to `hipotures/rad`, and verify the remote SHA
before claiming publication. Report actual deviations, partial counts, elapsed
time and one strongest next experiment. Do not automatically start Phase 5.

## 10. Start instructions

Use [reproduce.md](reproduce.md) to validate this planning package without GPU
execution. When explicitly asked to begin the experiment, record a fresh clock
and execute Steps 1–5 above inside this campaign and its declared external
workspace. Instrumentation and the new inference runner still need to be
implemented in Step 2; this planning package does not claim that a Phase 4
benchmark command or compiled instrumented binary already exists.
