# Phase D parent-to-editor bootstrap execution

Status: all four parents completed and sealed; independent final evaluation is running. This report supersedes the
preparation report's approval-waiting status following explicit user steering on 2026-11-03. The original benchmark
protocol and its source remain unchanged.

The user withdrew the agent-proposed USD/token caps and instructed proceeding with existing Codex access.
Local CLI reports an existing ChatGPT login; gpt-6.1-sol / medium is the current configured model and is retained.
No new credential or separately configured billed service is introduced. Actual tokens are recorded; no independent
claim about subscription billing is made. Local experimental evaluation and sandbox caps ensure bounded comparable
searches; they are not payment approvals.

Implemented: SQLite-transaction admission and durable per-session counters; candidate ownership and immutable
sealing; dev-only queue admission; whitelist-filtered feedback; sandboxed numerical proposals with Gold integrity,
shape/dtype/finite/target checks; live candidate-registry adapter for the unchanged persistent evaluator; four-parent
supervisor; session-bound local stdio/socket tool transport and separate filesystem namespace for Codex. No parent
receives the repository, evaluator files, held-out data, salt, other conversations or queues.

A transport probe found that current CLI requires its code-mode host. Another found MCP tools require the explicit
`approval_mode = "approve"` setting for unattended local tool use. These were corrected and the fourth probe
successfully called the bounded lab status tool. Code Mode exposes an apply_patch builtin even with shell tools
disabled, so tool configuration alone is insufficient: the outer filesystem namespace hides all topic data.
Numerical code remains inside the stricter no-network numpy sandbox.

Configuration reference consulted: [OpenAI Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference),
accessed 2026-11-03. The provider configuration is exercised locally; documentation is not treated as proof of
isolation. Tests and the two-GPU synthetic control smoke establish the local tool path. Synthetic smoke edits are
operator-authored transport controls, not parent-created candidates or bootstrap evidence.

The original held-out salt remains unchanged, owner-read-only and absent from parent views. Its private persistent
backup destination is still unknown; this is a disclosed recovery gap, not an invented approval requirement.

Final parent results, independent select/test/transfer outcomes, resource measurements, negative findings and
reproduction material will be added after the supervised experiment finishes.

Infrastructure verification: 22 tests pass (75.68 s under concurrent GPU/CPU smoke load). The synthetic two-GPU smoke completed five full 104-instance dev jobs in 211.0 s including cold engine startup; both workers exited zero and their final Gold audits passed. No benchmark source, thresholds, manifest or decoding was modified.


The four fresh conversations launched after commit ebe8ab98e was pushed. The operator-only final procedure is
implemented before any held-out scoring: seal all four candidates, complete select confirmation without feedback,
then test and transfer on the fixed set. Two persistent engines continue across all three splits. Existing
upstream/random editor controls remain, and one candidate-matched random live-position delta control is generated
per sealed candidate with predetermined seeds. BF16 quantization can slightly alter control entry counts/norms;
report the measured mismatch rather than claiming exact size/norm equality. Holm correction retains all four
parent hypotheses, including failures; controls are secondary contrasts and do not redefine the primary family.

Lossless BF16-bit-pattern export and reconstruction pass a tiny two-generation fixture test (including deletion of
the original patches, recovery of both IDs, and rejection of a corrupted export). A bounded representative p50c
export reconstructs its exact content-addressed identity as well. Final lineage exports will preserve bytes, not
just machine-local IDs or a transcript-dependent recipe.


A dev anomaly was observed before held-out access: two repeated editor states on different GPU workers produced
some different outputs despite fixed seeds and prefix resets, whereas several other repeats agreed exactly. The
measured pairs are retained in results/dev_repeat_audit.json and complete rows in the eventual evidence archive.
This is narrower than a claim that the swap is incorrect: transition hashes pass, and the cause is not established.
It contradicts an unrestricted claim of bit reproducibility across concurrent workers. Final primary comparisons
therefore keep E0, all four parents and their matched random controls on one discovered GPU; the second GPU runs
legacy controls plus its own E0. A select-only Gold repeat must agree before held-out scoring begins. Scheduling
and a technical select diagnostic change no frozen instances, scoring, decoding, primary samples or statistical
endpoint. If the technical repeat fails, investigate before opening test/transfer rather than silently accepting
unreliable comparisons.


## Completed parent search

All four parent processes and both development evaluators exited zero. The supervised search lasted 1122.37 s;
53 full dev passes completed without failed evaluator jobs. There were 46 distinct accepted proposed patches and
85 sandbox calls. Each parent independently stopped within its fixed maximum budget after 12–15 dev passes and
sealed one Gold-rooted candidate. Terminal reports are retained in parent_reports/; they are the parents' own
interpretation, not independent confirmation. No held-out output was returned to a parent.

| parent | sealed patch | dev passes | sandbox calls |
|---|---|---:|---:|
| 01 | p-a1a9a0be281a | 12 | 19 |
| 02 | p-9378a8c33b6a | 15 | 17 |
| 03 | p-41d9a0038798 | 14 | 26 |
| 04 | p-f6dc81f3da9a | 12 | 23 |

The completed search archive retains all lab calls, failures, terminal conversation events and lossless deltas
for all 46 accepted patches, not only winners. Complete per-sample dev outputs are archived separately. Private
Codex login homes and account/session databases are excluded. The original provider snapshot revision is not
exposed; the configured model ID, effort, CLI version, conversation IDs, exact prompts via source/templates,
responses and actual usage are retained. Remote model re-execution is therefore not claimed bit reproducible.

Preserved evidence: [parent provenance](../../evidence/20261103T-phaseD-bootstrap-parent-provenance/) and
[dev measurements](../../evidence/20261103T-phaseD-bootstrap-dev/). The fixed final population and generated matched
controls are recorded before final outcomes in results/final_plan.json. Select-only Gold-repeat diagnostics and
independent test/transfer outcomes remain pending.
