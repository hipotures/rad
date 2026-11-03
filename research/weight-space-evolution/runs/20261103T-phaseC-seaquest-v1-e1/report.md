# Phase C — bounded direct-edit session on MinAtar Seaquest — report

**Outcome: negative/inconclusive.** The editor's submitted edit did not significantly improve Gold on held-out
episodes. The harness flow (Gold → sandboxed analysis → validated patch → paired dev passes → submission → held-out
verification with controls) ran end to end.

## Setup
- Gold: upstream exp5 hand-written Seaquest network (600-32-32-6 tanh, 803 non-zero weights), evaluator validated
  against the published score (`../20261103T-minatar-evaluator-validation/`).
- Editor: Claude Opus 5.5 as a separate Claude Code subagent ([prompt](editor_prompt.txt)); brief
  `configs/phaseC_seaquest_brief.md`; budgets: 6 paired dev passes (≤ 300 episodes), 25 sandbox runs, ≤ 2,000 entries.
- Used: 5 of 6 passes, 16 of 25 sandbox runs, ~11 min editor wall time (680 s), 33 editor tool calls,
  ≈ 160k subagent tokens. 3 candidates proposed, all hand-derived from weight analysis.

## Editor's diagnosis (its claims; partly supported by dev data)
Gold never moves sideways (left/right logits fixed at −100), fires left from column 5, dodges/approaches rows by
danger/reward channels, and climbs when oxygen < 60 with ≥ 1 diver. Score ≈ survival (corr. 0.98 with length);
≈ 6–8% of episodes die at steps 141–152, right after the first low-oxygen climb; moving the trigger shifts this
cluster (editor's measurement). Full report: [editor_final_report.md](editor_final_report.md).

## Candidates and development feedback (paired, 300 episodes each)

| Pass | Candidate | Entries | Δ vs Gold (SE) | 95% CI |
|---|---|---|---|---|
| 1 | Gold only | – | mean 49.8 | – |
| 2 | B `p-38e02409d21a` climb trigger oxygen < 60 → < 40 (W1 unit 24, 2 entries) | 2 | −0.38 (3.31) | [−7.2, 6.1] |
| 3 | C `p-a745712c1f39` danger units treat column 7/8 differently | 24 | −12.7 (2.9) | [−18.3, −6.9] |
| 4 | D `p-2c6337e46fac` attack units ignore lone enemy bullets | 63 | −6.2 (2.5) | [−11.2, −1.2] |
| 5 | B again (new seeds) | 2 | +3.56 (3.36) | [−3.0, 10.0] |

## Held-out verification (1,000 new episodes, seeds 2,028,941,483 … +999 drawn after submission)

| Arm | Mean (SE) | Δ vs Gold (paired SE) | 95% CI | Mean length |
|---|---|---|---|---|
| Gold | 50.30 (1.34) | – | – | 1,354 |
| **Candidate B** | 52.14 (1.41) | **+1.83 (1.89)** | [−1.95, 5.68] | 1,490 |
| Flip (Gold − Δ) | 47.35 (1.30) | −2.96 (0.50) | [−3.94, −2.04] | 1,288 |
| permuted_0 / _2 | 49.94 / 50.49 | −0.36 / +0.18 | both include 0 | 1,344 / 1,360 |
| gaussian_2 | 49.92 | −0.39 (0.32) | [−1.01, 0.26] | 1,347 |
| gaussian_0, permuted_1, gaussian_1 | 50.30 | exactly 0 (no behavioural change) | – | 1,354 |

Verdict (`results/heldout.json`): candidate beats Gold at 95%: **no**; beats the best control: **no**.
Candidate vs flip: +4.79 (SE 1.88, CI [1.16, 8.54]).

## Interpretation
- **Measured:** edit B lengthens episodes (+10%) but its score gain is not significant in either dev or held-out
  data (pooled dev ≈ +1.6 ± 2.4; held-out +1.8 ± 1.9). C and D were clearly harmful on dev and were not submitted.
- **Supported:** the targeted dimension (oxygen surfacing threshold) is causally relevant — reversing the edit
  significantly lowers the score, while random edits of the same size and L2 do not change it. So the editor found a
  real lever but not a demonstrated improvement; the editor's own explanation (longer survival offset by a lower
  reward rate because difficulty ramps with surfacing) is a hypothesis consistent with the data.
- **Control design lesson:** in this sparse hand-written network, 3 of 6 "random matched" controls changed nothing
  (they hit weights fed by inputs that never fire or units with no downstream path). Future controls should sample
  positions among *active* weights (non-zero downstream influence) to be informative.
- **Power:** the edit changes 95% of episodes (paired-difference SD ≈ 60), so ~1,000 paired episodes resolve only ≈ ±3.7 points;
  dev passes of 300 resolve ≈ ±6.5. Small-lever edits need larger dev passes to be selected reliably.

## Limitations / deviations
- One editor session only (n = 1); no conclusion about editor capability in general.
- The submission was executed by the operator (logged as `operator_note`) because the editor lost access after the
  external compatibility path was removed mid-session; pass 6 was unused.
- The subagent's own shell was restricted by instruction, not by technical isolation; its proposed code ran in the
  sandbox, but its claimed adherence (no reading other files) is self-reported. The held-out seeds did not exist
  until after submission, so held-out validity does not depend on that.
- The editor model (Claude Opus 5.5) differs from the "Codex Sol" role named in AGENTS.md.

## Evidence
- `results/heldout.json`, `results/patches/*.json` (patch records and exact sparse deltas), `editor_scripts/`
  (all editor-written Python), `editor_final_report.md`.
- Session log (every lab call incl. code/outputs), state, pass summaries and per-episode held-out data:
  `../../evidence/20261103T-phaseC-seaquest-v1-e1/` (gzip, `pack-text`).
