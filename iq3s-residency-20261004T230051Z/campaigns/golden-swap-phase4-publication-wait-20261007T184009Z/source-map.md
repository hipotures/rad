# Inspected source and implementation constraints

Inspected read-only during planning, at source commit
`f3b4f19157b39ae017e2fd91814c8f5728e3b1cc`. Local source:
`/srv/ai/work/rad/golden-swap-phase3/20261007T150955Z/repos/runtime`.
File SHA256 identities are recorded in the input manifest. Line numbers below
are navigation aids for that revision, not an assertion about a future patch.

| File / approximate line | Observed implementation | Instrumentation consequence |
|---|---|---|
| `include/strata/research/q4_oracle.hpp:72` | Worker state 1 copies weights; state 4 updates two residency entries with separate four-byte H2D copies, records/synchronizes its completion event, then publishes state 5 | Distinguish weight staging/copy from later metadata publication. Host completion observation includes scheduling and driver effects |
| Same file, `publish()` at 97 | Requires copied state 3; rechecks expiry, cap, duplicate, compatible victim/protection and score; waits for worker state 5 before host ownership update | Place nested timestamps around validation, ack wait, and host commit; retain transaction generation and destination device |
| Same file, `host()` at 103 | Sequential publication loop over workers, then demand accounting and planning, all within the hook | A current device's dispatch can wait for another device's worker; both identities matter |
| `src/core/expert_source.cpp:2012` | Oracle hook precedes native resident/mapped plan assembly | Plan-A wait includes more than oracle publication |
| Same file, around 2103 | Plan counts/pointers are prepared, fence executes, then `P.publish(P.ctx)` runs before fetch/CPU work | Native plan construction and actual flag publication are separate producer milestones |
| `src/core/verify.cpp:1647` | `Verifier::publish_plan` fences and stores flag A | Record before/after the existing store without weakening ordering |
| Same file, 1048/1056/1072 | Existing timed kernels wait for A, B, and CPU completion, on the actual compute stream | Record per-invocation begin/end while retaining existing aggregate counters |
| Same file, 912–992 and 1084 | Shared expert branch can run on a separate stream, then joins before combination | Shared readiness can absorb plan-A savings; its active state and dependency must be recorded |
| Same file, 468 and 912 | `STRATA_VERIFY_PROFILE` is enabled by environment-variable presence; `prof_on_` disables the shared fork | Never enable this profiler, even by setting the variable to `0`, to obtain the principal trace |

Confirm the active layer-split handoff in the serving implementation during
Step 1. A helper/remote expert branch is different from the layer-split peer
dependency; do not enable the helper to measure the latter. Record inactive
branches as inactive, rather than inserting missing edges with zero durations.

The Phase 3 patch already timestamps wait begin/end in `%globaltimer` and sums
per-device totals. It does not retain per-event timestamps or align host and
device clocks. The new recorder must address both, plus graph replay indexing.
The existing broad verifier profiler must not be used as an implementation shortcut.

Read-only reusable campaign source includes `code/reproduce.py`, `code/live.py`,
`code/serve_capture.py`, `code/tape.py`, `code/transactions.py`, `code/safety.py`,
and `code/parity.py` in Phase 3. Several use campaign-relative output roots;
adapt/copy required authored code into the new campaign before execution.
Importing or invoking an old writer in place risks modifying completed evidence.

Recovery recipe: public Strata base
`6f32ec070f23ced9f50e704d854d775da52591ab` plus Phase 3
`patches/cumulative-from-original.diff`, with the `.venv` link excluded and the
pinned ggml dependency. See Phase 3 reproduce.md. Do not push the derivative
to the dependency's remote; preserve patches in RaD.
