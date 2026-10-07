# Golden Swap Phase 4: publication wait attribution

Status: **PLANNED_NOT_STARTED**. No Phase 4 inference, build, or experimental
clock has started. This is a continuation of the Golden Swap investigation.

The execution document is [GOAL.md](GOAL.md). It defines one development tape,
six full replays in three CONTROL/TRACE pairs, a proposed four-hour execution
cap, an instrumentation overhead guard, uncertainty-aware dependency attribution,
and decision rules. The runtime policy remains Phase 3 history + first-use
transaction control + incoming-query memoization, with oracle incoming.

- [Machine-readable protocol](configs/protocol.json) and [run order](configs/run-order.json).
- [Source findings and implementation entry points](source-map.md).
- [Inputs and frozen references](input-manifest.json), [workspace](workspace.json),
  and [external artifact recovery](artifact-manifest.json).
- [Planning status](STATUS.md) and [validation/start instructions](reproduce.md).

On this host the external work directory is
`/srv/ai/work/rad/golden-swap-phase4-publication-wait/20261007T184009Z/`.
Use `RAD_WORK_ROOT` to select another recorded location. Execution writes a new
run namespace; the timestamp above records preparation, not the future start.

The planned question is whether residency publication acknowledgment reaches
the required GPU consumer path after accounting for shared/CPU/peer work. A
fixed-trace sensitivity estimate will not be reported as a measured speedup.
