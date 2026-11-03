# Broker-to-evaluator two-GPU smoke

Operator-authored transport validation only, not parent bootstrap evidence. Four separate session-bound brokers
created distinct one-entry Gold-rooted controls using `wse.bootstrap_smoke`, then admitted dev jobs. E0 ran under
the same frozen protocol. All five full dev jobs completed; both workers exited zero and final Gold audits passed.
Wall time was 211.0003 s including engine initialization. See results/smoke.json for per-cell outcomes, resource
counts, patch IDs and UUID allocation. Reproduce once with the command in reproduce.md section 12; the driver
refuses overwrite. Control generation is the exact numerical recipe in code/wse/bootstrap_smoke.py. Raw output
rows and worker metadata are published as gzip evidence. No select/test/transfer evaluation or parent session ran
in this smoke. Existing input-manifest and Gold registry identities apply; no new downloads occurred.
