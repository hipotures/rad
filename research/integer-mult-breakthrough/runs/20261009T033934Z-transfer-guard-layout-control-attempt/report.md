# Guard-layout negative-control applicability failure

This one-worker bounded attempt exited 1 because its root rank-one case needs zero compaction swaps. Omitting a nonexistent return swap cannot change an endpoint, so requiring that control to reject was an incorrect coverage assertion. The tested factorization and guard omission/duplication controls passed before that assertion. This is a rejected checker attempt, not a counterexample to factorization.

The source is reconstructible by applying the fixed-grid recovery patch and then the control recovery patch. The resulting rejected SHA256 is `48324433aca0a1c3e9003b5e673d371b008f5d699a2314333fd2979ec95a90b0`. This preserved run reproduces an earlier unstamped smoke failure; its own actual launcher and process start timestamps remain explicit. No earlier timing has been invented. The next independent attempt is `20261009T033935Z-transfer-guard-layout-control-repair`.

The original protocol, failure receipt, launch, stdout and stderr remain unchanged. No accepted summary is supplied for this attempt. See [the guard-layout report](../../reports/transfers/guarded-slot-layout-transfer.md).
