# Golden Swap Phase 3

Planner cost, exposed wait, and decision-preserving optimization. This continues Golden Swap Phase 2; ordinary serving remains unchanged.

Result: **DECISION_PRESERVING_OPTIMIZATION_NO_CONFIRMED_PRACTICAL_GAIN**. All 36 main and 6 RFC8259 requests are valid. Incoming query reuse is about 97%, but median main hook CPU savings are 63–133 ms and no task meets the predeclared >3% practical optimization criterion. Inventory/Chinook retain practical gains versus contemporary current; Archive/WebSocket do not change classification. Exact deterministic decisions remain equal; live asynchronous readiness differences are declared.

The [report](report.md) answers all twelve research questions. [Paired results](results/paired-blocks.json), [primary CSV](results/primary-table.csv), [phase resource diagnostics](results/phase-resource-diagnostics.json) and [completion audit](completion-audit.json) retain the evidence and limitations. The strongest next experiment attributes remaining publication coordination to the measured dependent-stream stall; no Phase 4 or causal incoming work starts here.

- [Goal](GOAL.md), [fixed clock](clock.json), [status](STATUS.md), [decisions](DECISIONS.md).
- [Planner dependencies and timer semantics](results/planner-dependencies.md).
- [Existing journal analysis](results/existing-data-analysis.json) and [CSV](results/existing-data-summary.csv).
- [Deterministic parity](tests/deterministic-parity.json), [frozen Phase2 OFF parity](tests/frozen-phase2-off-parity.json), [safety](tests/safety-outcomes.json).
- [Runtime identity](configs/runtime-identity.json), [source patches](patches/phase3.diff), [reproduction](reproduce.md), [run order](run-order.json).

Raw binary data/builds remain external in the recorded task workspace. Eligible completed text evidence is published with the repository gzip workflow at finalization. Reproduction checks are not claimed complete before their actual outcomes exist.
