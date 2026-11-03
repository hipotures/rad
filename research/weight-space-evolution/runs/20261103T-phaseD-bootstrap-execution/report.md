# Phase D parent-to-editor bootstrap execution

Status: infrastructure validated; parent experiment about to launch. This report supersedes the
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
