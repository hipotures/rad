# Golden Swap Phase 3

Planner cost, exposed wait, and decision-preserving optimization. This continues Golden Swap Phase 2; ordinary serving remains unchanged.

Status: compiled runtime and 26 deterministic task/scorer OFF/ON pairs passed; development integration/overhead checks active. Headline timing has not begun.

- [Goal](GOAL.md), [fixed clock](clock.json), [status](STATUS.md), [decisions](DECISIONS.md).
- [Planner dependencies and timer semantics](results/planner-dependencies.md).
- [Existing journal analysis](results/existing-data-analysis.json) and [CSV](results/existing-data-summary.csv).
- [Deterministic parity](tests/deterministic-parity.json), [frozen Phase2 OFF parity](tests/frozen-phase2-off-parity.json), [safety](tests/safety-outcomes.json).
- [Runtime identity](configs/runtime-identity.json), [source patches](patches/phase3.diff), [reproduction](reproduce.md), [run order](run-order.json).

Raw binary data/builds remain external in the recorded task workspace. Eligible completed text evidence is published with the repository gzip workflow at finalization. Reproduction checks are not claimed complete before their actual outcomes exist.
