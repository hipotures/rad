# Golden Swap Phase 4: publication wait attribution

Status: **COMPLETED — INSTRUMENTATION_OR_FIDELITY_BLOCKED**. Fidelity and
trace identity passed; quantitative neutrality failed the symmetric gate.
All six v2 requests and the earlier two v1 requests are preserved. No Phase 3
GPU campaign rerun and no automatic Phase 5.

Read the [report](report.md), [final results](results/final/analysis.json),
[completion audit](completion-audit.json), and [reproduction](reproduce.md).
The narrow post-notify opportunity is at most0.065–0.240% on recorded TRACE
trajectories; ideal opportunity bounds reach2.74–4.14%, with zero lower bounds
and incomplete graph coverage. These are not uninstrumented-request estimates.

- [Frozen brief](GOAL.md), [protocol](configs/protocol.json), [run order](configs/run-order.json).
- [Phase 3 erratum](../golden-swap-phase3-20261007T150955Z/corrections/publication-chronology-20261007/erratum.md).
- [Actual execution clock, freeze and ledger](runs/20261007T194914Z/clock.json).
- [Source map](source-map.md), [active dependencies](dependency-model.md), [trace schema](configs/trace-schema.json).
- [Inputs](input-manifest.json), [artifact recovery](artifact-manifest.json), [evidence budget](configs/evidence-budget.json).
- [Status](STATUS.md), [machine progress](progress.json), [append-only progress](progress.jsonl).

`workspace.json` and protocol-history/v1 preserve preparation state; their null
clock is historical, not the execution clock. Actual work root on this host:
`/srv/ai/work/rad/golden-swap-phase4-publication-wait/20261007T184009Z/`.
Original large inputs remain immutable. Complete text/journal exports are under
evidence/; exact tape and activation bytes have no identified off-host backup.
Normal launchers, weights, and prior measurement records are unchanged.
