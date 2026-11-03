# Phase C v3 — environment-model access: source + self-simulation (S) vs prose rules only (N)

## Question

How much does access to an environment model help a bounded model editor improve the hand-written Seaquest policy
(exp5 Gold, ≈ 53) by direct weight edits? Condition S gives the full game source and allows a self-written simulator;
condition N gives prose rules only. This is improvement of an existing capability, not creation of a new one.

## Pre-registration and setup

The design was pre-registered and committed (78c82458b) before any session started:
[protocol.json](protocol.json). Configs: [`configs/phaseC_seaquest_v3S.json`](../../configs/phaseC_seaquest_v3S.json) and
[`configs/phaseC_seaquest_v3N.json`](../../configs/phaseC_seaquest_v3N.json).

| | Condition S | Condition N |
|---|---|---|
| Brief | [v3S](../../configs/phaseC_seaquest_brief_v3S.md) | [v3N](../../configs/phaseC_seaquest_brief_v3N.md) |
| Game context | full MinAtar 1.0.15 game source | prose rules and input/output encoding only, hash-checked |
| Simulator | self-written simulator inside `LAB py` allowed | forbidden by instruction |
| Editor prompt | [editor_prompt_S.txt](editor_prompt_S.txt) | [editor_prompt_N.txt](editor_prompt_N.txt) |

Common to both conditions:
- Three independent Claude Opus 5.5 subagent sessions per condition, all six run in parallel.
- Budgets as in v2: 6 dev passes of ≤ 1,000 paired episodes, 25 sandbox runs, ≤ 2,000 changed entries, ~60 minutes.
- Per-session held-out: 2,000 fresh episodes with active-weight controls.
- Joint comparison: 4,000 shared fresh seeds (seed base 3,086,250,462), with the v2-e3 patch as a reference arm and Holm correction.

**Execution incident.** All six sessions were stopped by an account API rate limit after 2–4 sandbox runs. Only N-e2
had used a dev pass, and no session had submitted. Each was resumed about 2 hours later from its own transcript, with an
identical operator message giving the same rules, its remaining budgets and ~50 minutes. The wall-clock budget was
therefore effectively reset, and the pause may have changed how the sessions proceeded.

## Results

### Per-session held-out (2,000 fresh episodes; Δ = candidate − Gold, paired)

| Session | Patch | Entries | Dev passes (Δ) | Held-out Δ ± SE | 95% CI | W / L / T | Success* |
|---|---|---|---|---|---|---|---|
| S-e1 | p-1bdd9d14fb09 | 42 (W2, b2) | +19.5, +16.5 | **+18.97 ± 1.20** | [16.69, 21.30] | 1181 / 664 / 155 | yes |
| S-e2 | p-011e6d1a4b4c | 9 (W2, b2, W3, b3) | +4.34, +4.16 | **+4.07 ± 0.46** | [3.21, 4.96] | 247 / 81 / 1672 | yes |
| S-e3 | p-e16dae33cb40 | 1 (b3) | +2.62, +5.16 | **+3.96 ± 1.15** | [1.64, 6.18] | 933 / 919 / 148 | yes |
| N-e1 | p-2efb8ec9bc87 | 108 (W2, b2, b3) | +1.74 | +0.77 ± 1.17 | [−1.49, 3.15] | 962 / 910 / 128 | no |
| N-e2 | p-38e02409d21a | 2 (W1) | −1.30 | +0.12 ± 1.33 | [−2.51, 2.87] | 963 / 938 / 99 | no |
| N-e3 | p-593f8c8eb139 | 14 (W1) | +4.6, +4.2 | **+4.54 ± 1.05** | [2.44, 6.64] | 940 / 742 / 318 | yes |

\* Pre-registered success criterion: the 95% CI is above 0 and above the best active-weight control. Per-run files are in
`../20261103T-phaseC-seaquest-v3-heldout-{S,N}-e{1,2,3}/results/heldout.json`.

Notes on the controls:
- Most size-matched random edits are harmful, many catastrophically (−15 to −54).
- For the 1-entry S-e3 patch, several controls are exact no-ops (Δ = 0.0); an example is changing b3 for left/right, where the bias is −100 ± 2.

### Joint comparison (4,000 shared fresh seeds, Holm-adjusted)

Results: [comparison.json](../20261103T-phaseC-seaquest-v3-joint-comparison/results/comparison.json). Gold scored 52.75.

| Arm | Condition | Mean | Δ vs Gold ± SE | 95% CI | Holm p |
|---|---|---|---|---|---|
| p-1bdd9d14fb09 | S-e1 | 70.97 | **+18.22 ± 0.87** | [16.59, 19.93] | 7e−97 |
| p-8255708841a2 | v2-e3 (reference) | 63.12 | +10.36 ± 0.92 | [8.52, 12.14] | 1e−28 |
| p-e16dae33cb40 | S-e3 | 57.74 | +4.99 ± 0.79 | [3.53, 6.52] | 1e−9 |
| p-011e6d1a4b4c | S-e2 | 57.63 | +4.88 ± 0.34 | [4.25, 5.53] | 8e−47 |
| p-593f8c8eb139 | N-e3 | 57.16 | +4.41 ± 0.75 | [2.97, 5.87] | 2e−8 |
| p-2efb8ec9bc87 | N-e1 | 54.40 | +1.64 ± 0.83 | [0.06, 3.33] | 0.10 |
| p-38e02409d21a | N-e2 | 53.89 | +1.14 ± 0.94 | [−0.68, 2.94] | 0.23 |

- S-e1 beats every other candidate by 7.9 to 17.1 points; the SEs of those differences are 0.9–1.0.
- p-38e02409d21a's held-out estimates so far are +1.83, −2.97, +0.19, −0.65, +0.12 and +1.14. They are consistent with an effect of ≈ 0.

### By condition (descriptive; n = 3 per condition)

| | S (source + self-simulation) | N (prose only) |
|---|---|---|
| Sessions meeting the success criterion | **3 / 3** | 1 / 3 |
| Mean held-out Δ (per-session runs) | +9.0 | +1.8 |
| Mean held-out Δ (joint run) | +9.4 | +2.4 |
| Distinct ideas | 3 different mechanisms | 3, one being the recurring p-38e02409d21a |
| Dev passes used | 4, 2, 2 | 6, 5, 5 |
| Subagent tokens (reported) | 117k, 95k, 92k | 135k, 97k, 117k |

**Statistics.** With 3 sessions per condition, 3/3 vs 1/3 is not significant: Fisher exact one-sided p = 0.2. The direction is
consistent with v2, where the only success also came from a self-simulating session. The difference in effect size is
driven by S-e1.

## The successful edits

All three S successes were found as specific failure modes in the editor's own simulator and then fixed with
bias-compensated circuit edits:

- **S-e1, +18.** Sticky actions cause deaths. 237 of 366 simulated collision deaths followed a move with policy probability below 5%: the 10% sticky repeat carries the sub two rows into an enemy.
  - The edit strengthens the existing two-row lookahead veto from −0.3 to −3.0 (13 W2 entries) and adds an own-row gate that cancels this veto when the sub's own row is in danger (14 W2 entries).
  - The 15 b2 entries are compensated so the network's resting state is unchanged.
- **S-e2, +4.** From rows 0 and 1, Gold moves down with p = 1.0 even with an enemy below, because the down bias of 244 wins when all units are inactive.
  - The edit adds two "down-veto" units in unused h2 neurons (9 entries), with a bias shift that cancels them out when inactive.
- **S-e3, +4.** In idle states the logits make "down" about 87% likely. The edit lowers one bias: b3[4] goes from 244 to 242.

The N success came from forward probes plus traces, without a simulator:
- **N-e3, +4.5.** Divers below pull a blocked ascent back down, so the edit gates the diver detectors with the "surface now" gauge cells (14 W1 entries).
- This is close in spirit to v2-e3's diver gating, which gave +5.8 alone in the v2 ablation.

## Interpretation and confidence

**Measured.** Under identical budgets:
- All three source+simulation sessions produced direct edits that robustly improve held-out score, by +4 to +19.
- One of three prose-only sessions did, by +4.5.
- The best edit, S-e1's 42 entries, raises Gold from ≈ 53 to ≈ 71, which is +35% relative. It is far beyond size-matched random edits.

**Supported inference.** An executable environment model lets the editor attribute failures to concrete mechanisms (for
example "sticky repeat into an enemy two rows away"). Weight reading, hand-built probes and three traced episodes per
pass rarely reveal those mechanisms. The S sessions also needed fewer dev passes: their selection happened in the
simulator.

**Confidence.**
- High that the four successful patches improve this Gold on this evaluator.
- Low to moderate that S > N in general: n = 3 per condition and one editor model.
- In addition, the rate-limit interruption, the sandbox CPU-limit bug (below) and the editors' minor rule deviations affected both conditions.

**Limitations.**
- One game, and one hand-written Gold with obvious slack: no lateral movement, and decisions balanced near tanh saturation.
- One editor model, with no transfer to other targets tested.
- Nothing here bears on small models as editors (Phase D).

## Harness findings during v3

- **The sandbox CPU limit was too strict, in all rounds v1–v3.**
  - Cause: `RLIMIT_CPU = timeout + 5` CPU-seconds counts all threads. With 4 BLAS threads, multi-threaded numpy runs were killed (rc 137) after ≈ 31 s of wall-clock time instead of 120 s.
  - Evidence: session v3S-e2, runs 8–10.
  - It was fixed after v3 by scaling the limit by the thread count. A 40-s 4-thread computation now completes.
  - It applied equally to all conditions, but it limited the simulation size available to S sessions.
- **Minor deviations, all self-reported and without experimental effect.**
  - Host `python3` was used to parse `LAB` JSON output in S-e1, N-e1 and N-e3.
  - N-e2 lost a dev pass to its own chained-command error.
- **Compliance check.** A keyword search of all N-session scripts found no simulator code (spawn/enemy-movement logic). S-session scripts contain simulators, as permitted.

## Next step

1. Re-run the condition comparison with more sessions per condition (≥ 6) after the CPU-limit fix, and possibly with a second editor model, to estimate the S − N gap with useful precision.
2. Alternatively, accept the finding and move to Phase D. There, the editor protocol should grant a budgeted environment model explicitly and count simulated steps as a resource. The p-1bdd9d14fb09 patch is a ready-made "strong edit" reference for Phase D editor-evaluation targets.

## Artifacts

- [protocol.json](protocol.json) contains the pre-registration, execution notes and harness findings.
- [editor_usage.jsonl](editor_usage.jsonl); [editor_reports/](editor_reports/) holds the condensed final reports (model output); [editor_scripts/](editor_scripts/) holds all scripts the editors wrote, including the S simulators.
- [results/patches/](results/patches/) holds patch.json and sparse deltas for all 16 v3 candidates.
- Held-out: `../20261103T-phaseC-seaquest-v3-heldout-*`. Joint: `../20261103T-phaseC-seaquest-v3-joint-comparison/`.
- Session logs and raw per-episode data: `evidence/20261103T-phaseC-seaquest-v3/` (gzip text).
