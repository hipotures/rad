# Weight-space evolution — summary of the initial goal (2026-11-03)

This report covers GOAL completion criterion 4. It separates what was reproduced, what was partially reproduced, what
was measured anew, and what remains untested. The details are in the linked run reports.

## Completion criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Verified upstream audit, pinned provenance | Met | [phaseA_upstream_audit.md](phaseA_upstream_audit.md), [input-manifest.json](../input-manifest.json) |
| 2 | Minimal patch/harness flow with tests | Met: 20 tests | [`code/wse/`](../code/wse/), [`code/tests/`](../code/tests/) |
| 3 | Executed bounded validation case | Met: Phase C v1–v3 and the Phase D pilots | runs below |
| 4 | Factual report (this file) | Met | — |
| 5 | Durable committed and pushed source, results, reproduction | Met | [reproduce.md](../reproduce.md), [artifact-manifest.json](../artifact-manifest.json) |

## Reproduced (exact)

- **Upstream edits rebuilt from public Gold.** p10c, p25c and p50c rebuild bit-exactly from Qwen/Qwen3.5-0.8B @ 2fc0636, with matching patch hashes, tensors and entry counts ([run](../runs/20261103T-p50c-reconstruction/report.md)).
- **MinAtar evaluator.** It matches the published exp5 hand-written network scores ([run](../runs/20261103T-minatar-evaluator-validation/report.md)).

## Partially reproduced

- **p50c behavioural effect on MATH-500.** Tested on 100 of 500 problems, 2 samples each:
  - Gold scored 6.5% and p50c 47.5%, a paired difference of +41 pp [33, 49].
  - Upstream reports 6.2% and 45.0% on the same problems.
  - The full benchmark was not re-run ([run](../runs/20261103T-p50c-math500-bounded-r2/report.md)).

## Measured anew (Phase C: frontier editor, direct weight edits of a Seaquest policy)

The editor improves an *existing* capability; it does not create a new one. Held-out results use fresh seeds drawn after
submission, are paired against Gold, and include size-matched controls on active weights.

| Round | Result |
|---|---|
| v1 (1 session) | No improvement: the 2-entry edit scored −2.97 ± 1.32 on re-verification ([report](../runs/20261103T-phaseC-seaquest-v1-e1/report.md)) |
| v2 (3 sessions) | 2 sessions converged on the same no-effect edit. 1 session scored +9.9 [7.5, 12.5], but with a protocol deviation: it built its own simulator ([report](../runs/20261103T-phaseC-seaquest-v2/report.md)) |
| v3, preregistered (3+3 sessions) | Source plus self-simulation: 3/3 sessions succeed (+19.0, +4.1, +4.0). Prose rules only: 1/3 (+4.5). Best edit: Gold 53 → 71 ([report](../runs/20261103T-phaseC-seaquest-v3/report.md)) |

## Measured anew (Phase D pilot: a small model as editor, no parents)

- **E0 (Qwen3.5-0.8B) has almost no editing skill on damaged-MLP targets:**
  - free-form edits at floor;
  - thinking mode always truncated at 4k tokens;
  - with constrained decoding, outputs are valid but mostly harmful.
- **The one exception is F3** (shifted output bias): choice +0.41 against chance +0.05, free-form +0.12.
- **p50c** removes looping (truncation 87.5% instead of 100%) but does not improve editing.

Reports: [pilot](../runs/20261103T-phaseD-pilot-e0/report.md), [constrained](../runs/20261103T-phaseD-pilot-constrained/report.md).

## Untested hypotheses (explicitly not established)

- That a parent can, by direct edits only, make a small model a better editor of other networks (the Phase D gate). It was designed ([design](phaseD_bootstrap_gate_design.md)) but not run.
- Specialization, population dynamics, recursive or cross-editing improvement.
- Creating a *new* capability by direct weight editing. Everything shown here improves or unblocks existing behaviour.
- Generality beyond one game, one hand-written Gold and one editor model.
- The size of the S-versus-N gap: with n = 3 per condition, the 3/3 versus 1/3 difference is not significant (p = 0.2).

## Known limitations and incidents

- **Sandbox CPU limit.** It was effectively about 31 s instead of 120 s in rounds v1–v3. It was fixed after v3.
- **API rate limit.** It interrupted all six v3 sessions, which were then resumed.
- **Minor editor deviations.** Some editors parsed JSON outside the sandbox. They self-reported it and it had no experimental effect.

## Next steps (require a new goal and, for parents, operator budget approval)

1. Revise the Phase D task matrix:
   - harden F1/F2, which a 3-rule heuristic solves;
   - balance T0 option positions;
   - add F4/F5;
   - allow executable probe passes.
2. Re-pilot E0 on the revised matrix and freeze the tiers and thresholds in Git.
3. Get operator approval of parent budgets, then run the gate (4 parents).
