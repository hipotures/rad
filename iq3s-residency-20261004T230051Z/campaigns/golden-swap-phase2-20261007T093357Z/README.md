# Golden Swap Phase 2

**DOMAIN_SCOPED_CONDITIONAL_REPLAY_GAIN**; **NO_CONFIRMED_SCORER_DIFFERENCE**. All 48 main and 8 independent-source replay requests are valid. First-use transaction control removes the original pre-target unused re-eviction mechanism. Inventory and Chinook satisfy the frozen paired timing criterion; archive/WebSocket do not. Independent two-block timing is inconsistent. Oracle incoming/current-window privileges remain, so this is conditional replay research, not deployment.

Start with the [report](report.md), [completion audit](completion-audit.json), [brief](GOAL.md), [protocol](protocol.md), [decisions](DECISIONS.md), [progress](STATUS.md) and [attempt ledger](attempt-ledger.jsonl).

Evidence: [Phase1 lifetime diagnosis](results/diagnosis.md), [per-run results](results/live-attempts.json), [paired blocks](results/paired-blocks.json), [direct scorers](results/history-versus-logistic.json), [offline competition](results/offline-competition.json), [calibration frontier](results/calibration-frontier.json), [development OFF/ON](results/development-ablation.json), [transaction schema](results/transaction-schema.json), [queue/expiry diagnostics](results/queue-and-timing-diagnostics.json), and [resource CSV](results/resources.csv).

Recovery: [exact bounded reproduction](reproduce.md), [storage manifest](artifact-manifest.json), [input provenance](input-manifest.json), [dependencies](configs/dependencies.json), [cumulative source patch](patches/cumulative-from-original.diff), [source reconstruction](tests/source-recovery.json), [ggml parity](tests/ggml-recovery.json), [scorer parity](tests/scorer-parity.json) and [tape checksum parity](tests/tape-validator-parity.json). Generated request/ID payloads, large tapes, binaries and journals remain external/local. Exact raw captures lack an independent backup destination; recovery limits are explicit.

Normal Q4 / K24 / PCIe 0.28 / pool 100 us serving remains unchanged. No training, upstream migration, host-setting change or Phase3 execution. Audit and cleanup completed; durable results are committed and published to the canonical GitHub repository.
