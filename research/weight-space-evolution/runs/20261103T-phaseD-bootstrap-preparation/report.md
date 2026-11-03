# Phase D parent-to-editor bootstrap: preparation

Date: 2026-11-03. Status: prepared specifications; awaiting explicit model/token/spending approval. **No parent was launched, no candidate was created, and no held-out scoring was run.** The research objective remains open.

## Scope and existing evidence

The initial goal is complete ([summary](../../reports/summary.md)); its original brief is preserved at
[initial_goal_completed.md](../../reports/initial_goal_completed.md). The new [GOAL.md](../../GOAL.md) specifies
parent-to-editor bootstrapping only. The v2 pilot, persistent-swap and end-to-end reports were reviewed with the
frozen protocol. Existing patches have no select-confirmed improvement in editing ability; p25c's apparent dev
improvement failed select confirmation. This motivates independent selection and final evaluation.

## Prepared material and budget proposal

Four fresh-conversation specifications have distinct lineage namespaces, seed labels, scratch directories and
initial search approaches. All start at the same immutable Gold, with no exchange of histories, candidates or
feedback. Approaches are procedural variation, not assigned domain specializations. Identical content-addressed
patches must be counted as duplicates. No actual session exists yet.

The proposal is 30 full v2 dev passes and 200 sandbox runs per parent; 375,000 input plus 125,000 output/reasoning
tokens (500,000 total), USD 50 and four hours per parent. Across four parents: 120 passes, 800 sandbox runs,
2,000,000 tokens and USD 200. Local evaluator allowance: four GPU-hours. Every retry/failure counts. The full
104-instance pass follows the current v2 readiness estimate rather than the older design's tentative 64-instance
cap; this changes a proposed execution budget, not benchmark content or scoring. Model/provider/effort and price
table are deliberately unset, approval is null and paid launch is disabled. These are proposals, not cost forecasts
or enforced provider-side limits.

## Verification

- Frozen protocol, manifests, benchmark/evaluator code and integration registry match the committed source lock.
- All 595 instance payload pairs match their committed hashes: pilot 95, dev 104, select 104, test 200, transfer 92.
  Verification hashes existing files; it neither regenerates nor evaluates private instances.
- Salt matches its frozen commitment, is owner-read-only, and is never emitted. Private split directories are
  owner-only and their files read-only; local private manifests are owner-read-only. Permissions alone cannot
  isolate another process running as the same user. The parent must never receive a host workspace shell.
- Gold passes the full registered file checksum and read-only checks. No weights were modified or downloaded.
- Four regenerated dev prompt views omit raw instances, oracle metadata, baselines and T0 answer-key fields.
  Only task prompts and decoding constraints are exported. None of these views is a host-access permission grant.
- Existing numerical sandbox selftest passes all eight checks, including no network, invisible topic/private
  paths, read-only Gold, writable scratch, no secret environment, torch or MinAtar. This validates numerical-code
  execution only; a future model/tool transport still needs an independent fail-closed test.
- 17 tests pass in 25.38 s, including corruption rejection, duplicate identity rejection, source-drift rejection
  and proof that a missing salt is not silently regenerated. Frozen benchmark tests also pass.
- Two RTX 4090 GPUs are visible to PyTorch; current environment and UUIDs are recorded in
  [environment.json](results/environment.json). No GPU worker was started. Existing measured throughput remains
  the scheduling evidence: one persistent worker per discovered UUID, with direct swapping and reload fallback.

## Launch prerequisites and limitations

1. Explicit operator approval of the exact frontier model/revision/effort and token/USD caps. No model is silently
   substituted. Verify actual pricing and applicable provider terms after selection and before calls.
2. Identify a private persistent salt backup. The previously documented recovery gap remains; no off-topic copy
   was made, no backup destination was invented, and no secret was committed. Loss of the salt breaks recovery of
   these held-out identities.
3. Implement and validate the selected transport's operator-side broker: dev-only submissions, atomic per-session
   budgets, worst-case token/cost reservation, sandbox call limits, lineage ownership, filtered dev feedback and
   full provenance. The low-level evaluator queue is an operator interface, not a safe parent interface.
   The preparation tool does not call a provider or implement this broker. Never attach these parents to an
   unrestricted workspace agent. The current evaluator uses the frozen registry path: campaign registration must
   use a separately retained adapter/binding without overwriting frozen files.
4. Preserve the frozen primary statistical endpoint. The earlier design's tentative heuristic superiority margin,
   ordinary-task regression threshold and resource-matching details are not fully preregistered by v2. Resolve
   those broader gate criteria before launching, or explicitly restrict conclusions to the frozen endpoint.

After approval and transport validation, seal one candidate per parent; operator-only select confirmation is used
once with no feedback or replacement. Independently evaluate the fixed set, E0 and controls on test/transfer once,
including negative candidates. Report per-family/tier recovery, validity, effective/regression rates, valid-only
results, resource costs and transfer. A reduction in harmful edits is not proof of newly created repair ability.

## Recovery and publication

[reproduce.md section 11](../../reproduce.md#11-phase-d-parent-bootstrap-preparation-no-paid-calls) gives the exercised
preflight and test commands. Authored source is [bootstrap_prepare.py](../../code/wse/bootstrap_prepare.py);
[configuration](../../configs/phaseD_bootstrap/) records budget, sessions and hashes. Compact evidence is in
[results/](results/); complete gzip copies are published in
[the preparation evidence archive](../../evidence/20261103T-phaseD-bootstrap-preparation/). No private benchmark
payloads, salt, prompt-view payloads, model weights or credentials are included. Preparation does not establish
bootstrap success. Recommended next step: explicit approval and resolution of the recorded launch prerequisites.
