# Dependency audit and bounded optimization

Phase 2 `plan()` repeats E64 first-feasible incoming enumeration for idle workers. Each nonresident candidate asks the immutable incoming index for the next occurrence after current and lane demand in `[current+1,min(end,current+768)]`. Cost floor is `(bytes/25e9+bytes/13.2e9)/160e-6`. For 3,072,000 bytes it requires at least three lane entries. This is an assumed economic operating point, unchanged here.

A whole negative admission cache is unsafe: worker readiness, capacity, protection, ownership, causal history and timing-derived lead can change. Phase 3 instead memoizes only the exact `(next target, incoming lane count)` facts. Every dynamic residency/selection condition stays in its original order and is reevaluated. Both positive and negative query results can be reused. Thus this is a smaller common planner optimization rather than a cached NO_SWAP decision.

| Quantity | Dependencies | Invalidation |
|---|---|---|
| Incoming next/count memo | Immutable tape/index, key, current lower bound, 768-invocation upper bound; full incoming information | Earliest of next lower occurrence leaving at `current == target` or next upper occurrence entering at `current == occurrence-768`; rewind; prepare/request reset |
| Candidate enumeration | Worker device/class, lead (copy/event EMA), E64 movement, tape routes, actual residency | Every plan call; never memoized |
| Incoming copy floor | Byte class, unchanged staging/H2D and 160us assumptions, memoized count | Exact incoming-count boundary; byte classes/config immutable |
| Victim choice | Event, ownership, protection, current-window routes, causal scorer version/resident heat | Inherited Phase 2 cache unchanged; ownership/protection changes invalidate as before |
| Risk and victim-cost guard | Selected victim, causal features, supplied target, threshold | Evaluated as before; not memoized |
| Protection/cap | Actual admission generations, first service, next safe milestone, expiry, class occupancy | Every selection/publication milestone |
| Copy/publication | Queue state, completed physical copy, current ownership, compatible victim, protection, expiry | Every publication recheck; unchanged |

The memo is bounded to 24,576 entries, 491,520 host bytes (five 32-bit fields per entry). No new victim-future access or future weights. Full incoming only: finite-information modes fall back to uncached role-typed queries. No persistent cache crosses requests or prepared indexes. Immutable future changes require `prepare()`; no runtime mutation of future is permitted.

Counters distinguish lookup/hit/miss, lower/upper/rewind invalidation and reset. An optional diagnostic timer measures lookup/miss maintenance including underlying recomputation; it is disabled for headline timing. No claim of exclusive cache-maintenance CPU time is made. Separate request-scoped thread CPU time measures the oracle host hook; wall planner includes worker acknowledgments and overlaps inference.

Timer nesting follows the actual source: `selection_ns` wraps `victim()`, including cache validation and the resident-enumeration loop; `enumeration_ns` covers only that resident loop. It is not the incoming E64 candidate scan. Feature/model timers are inside scorer calls during that loop and also reserve/guard calls. Publication acknowledgment is inside the host-hook wall interval. The host CPU timer excludes reservation/setup before `host()` and copy workers. These intervals must not be summed as exposed stall or treated as one identical scope.

# Wait instrumentation

Opt-in `STRATA_Q4_WAIT_PROFILE=1` substitutes the existing one-thread flag wait kernel with one reading `%globaltimer` immediately before/after the spin. Same stream, one kernel launch, same fence, no new routed-event synchronization. Device-local counters sum elapsed ns and count for plan A, mapped B and CPU completion flags. Six 64-bit counters/device = 96 bytes total of logical counter payload (allocator granularity is included in VRAM telemetry); expert capacity/spares unchanged. Request-end readback/reset occurs after existing final commit and is charged to completion wall. Ordinary serving defaults OFF.

Plan A measures actual delay of the dependent verifier stream awaiting the host-published GPU plan, including native plan assembly/host scheduling. It is not solely oracle planner execution. Mapped B and CPU waits occur later and can reflect other required work. Do not sum these with nested host timers. A delay on an active stage stream is an observed blocked dependency; its isolated contribution to whole-request critical-path time remains bounded by overlap with shared/peer work. No CPU/GPU absolute clock alignment is asserted. Copy times retain host-synchronization intervals, not DMA-only duration. Device-plan skip paths are deliberately not profiled; frozen profile must verify they are disabled.

OFF/ON deterministic simulation hashes all evaluated candidate outcomes and plan results including busy/cap NO_SWAP; admission/lifecycle binary journals prove identity of logical copies/publications/ownership and actual required work. Live scheduling may differ when faster host work changes physical readiness and the inherited timing-derived lead. Those differences must be declared rather than mislabeled stale-cache parity success.
