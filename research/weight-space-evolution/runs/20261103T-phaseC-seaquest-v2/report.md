# Phase C v2 — three independent bounded editor sessions on Seaquest (exp5 hand-written Gold)

**Question.** Can a bounded model editor improve a hand-written MinAtar Seaquest policy (Gold ≈ 53) by direct weight edits
only, measurably beyond Gold and size-matched random edits, on held-out episodes? This means editing a network that
already plays the game, not creating a new capability.

**Setup.** Config [`configs/phaseC_seaquest_v2.json`](../../configs/phaseC_seaquest_v2.json); brief
[`configs/phaseC_seaquest_brief.md`](../../configs/phaseC_seaquest_brief.md); protocol [protocol.json](protocol.json).

- Three Claude Opus 5.5 subagents worked in parallel, isolated from each other, each in its own lab session.
- Budget per session: 6 dev passes of ≤ 1,000 paired episodes, 25 sandbox runs, ≤ 2,000 changed entries, ~60 minutes.
- Total editor cost: 382,890 subagent tokens (budget ≤ 600k); see [editor_usage.jsonl](editor_usage.jsonl).
- Held-out verification:
  - per session, 2,000 fresh episodes with active-weight random controls;
  - one joint comparison on 4,000 shared fresh seeds with Holm correction.
  - Seed bases were drawn with `secrets` after every submission.

## Results

### Sessions

| Session | Submitted | Entries | Dev passes (Δ vs Gold ± SE) | Held-out Δ vs Gold (2,000 ep.) | 95% CI | Beats Gold / best control |
|---|---|---|---|---|---|---|
| v2-e1 | p-38e02409d21a | 2 (W1) | +1.48 ± 1.90, +0.40 ± 1.80 (others: −3.2, −2.8, −46) | +0.19 ± 1.36 | [−2.45, 2.94] | no / no |
| v2-e2 | p-38e02409d21a | 2 (W1) | +1.48 ± 1.90, +0.40 ± 1.80 (others: −6.4, −23.0) | −0.65 ± 1.33 | [−3.20, 1.97] | no / no |
| v2-e3 ⚠ | p-8255708841a2 | 146 (W1, W2, b2) | +3.9, +8.8, +11.6, +12.8, +11.4 (SE ≈ 1.6–1.9) | **+9.90 ± 1.30** | **[7.45, 12.49]** | **yes / yes** |

⚠ = protocol deviation, described below. The per-session held-out results are in
`runs/20261103T-phaseC-seaquest-v2-heldout-e{1,2,3}/results/heldout.json`.

### Joint comparison

Shared seeds: 4,000 episodes, seed base 3,021,376,474 (see [protocol](../20261103T-phaseC-seaquest-joint-comparison-r2/protocol.json)).
Results: [comparison.json](../20261103T-phaseC-seaquest-joint-comparison-r2/results/comparison.json).

| Arm | Sessions | Mean | Δ vs Gold ± SE | Holm p |
|---|---|---|---|---|
| Gold | — | 52.99 | — | — |
| p-38e02409d21a | v1-e1, v2-e1, v2-e2 | 52.26 | −0.73 ± 0.93 | 0.44 |
| p-8255708841a2 | v2-e3 | 63.92 | **+10.93 ± 0.95** | 4.7e−30 |

The two patches differ by 11.65 ± 1.05 points, CI [9.65, 13.60]. The first attempt at this comparison crashed on a
printing bug after the Gold arm and produced no candidate results; it is recorded in
`runs/20261103T-phaseC-seaquest-joint-comparison/attempt_status.json`.

### Controls

- Random controls were restricted to weights on live paths.
- For e1 and e2, the 2-entry candidate was indistinguishable from the controls. Controls ranged from −3.1 to +0.6, and flip (sign-reversed delta) was −3.6 to −3.8.
- For e3, the controls matched the candidate's size: 146 entries, ‖Δ‖ = 11.1. They were catastrophic: permuted −33 to −45, gaussian −49 to −51, flip −47.
- A random edit of this size on active weights destroys the policy. The e3 edit is a targeted change, not a lucky perturbation.

### Post-hoc ablation of the e3 edit (operator analysis)

These arms were not submitted. They are an operator decomposition run on fresh shared seeds after the result was
known. Run: [`runs/20261103T-phaseC-seaquest-e3-posthoc-ablation`](../20261103T-phaseC-seaquest-e3-posthoc-ablation/results/comparison.json), 4,000 episodes.

| Arm | Content | Δ vs Gold ± SE | 95% CI |
|---|---|---|---|
| p-8255708841a2 | full submission | +9.04 ± 0.93 | [7.30, 10.99] |
| p-ba49fc57d8c2 | e3 dev pass 2: hunting ×2 + diver weights ×0.5 (300 entries) | +9.01 ± 0.94 | [7.22, 10.90] |
| p-ed1458fd3f44 | gated diver attraction only (7 W1 entries; built with `wse.ablate_patch`) | +5.77 ± 0.82 | [4.18, 7.35] |
| p-fa2f19291b16 | hunting ×2 with b2 compensation only (139 entries; identical to e3's dev pass 1) | +4.37 ± 0.87 | [2.58, 6.08] |

- Both components help independently, and their effects are roughly additive: 4.4 + 5.8 = 10.1 versus 9.0 combined.
- The final gated version is equal to e3's simpler second variant: 0.02 ± 0.57.
- So the "gate" refinement, which e3 selected in its own simulator, added nothing measurable over halving the diver weights.

### Comparison with v1

- In v1 the same p-38e02409d21a was submitted. Held-out results were +1.83 ± 1.89 on 1,000 episodes and −2.97 ± 1.32 on 2,000 episodes.
- [Re-verification with active controls](../20261103T-phaseC-seaquest-v1-e1-activecontrols/report.md).
- Pooled over all held-out evaluations of this patch, the effect is ≈ 0.

## Protocol deviation: e3 simulated the game itself

e3's report says it wrote its own copy of MinAtar Seaquest from the game source printed by `brief --game-source`.

- It ran that copy only inside the sandbox, through `LAB py`. Its Gold reproduction gave 48.6–56.6 on 100–400 episodes.
- It used the copy to:
  - diagnose death causes and the kill/score structure;
  - compare about 8 hand-designed edit variants with full simulated episodes.
- This breaks brief rule 2: "do not try to reach the game simulator other than through `devpass`".
- It also exceeds the intended feedback budget. Simulated episodes are unbudgeted feedback on the target objective, and choosing among variants with them is selection.
- No rule against gradients, fitting or random search was broken: the variants were few and hand-reasoned.
- The editor disclosed the deviation itself.

**How to read the e3 result.**

- **What it shows:** a model editor that has the environment source can diagnose a policy network and write a direct weight edit that robustly improves held-out score by about +10 (≈ +19% relative).
- **What it does not show:** that this happens within the dev-pass budget. The budget was not the binding constraint for e3.
- **Evidence that the gain is not mainly selection on noise:**
  - its first two devpass-evaluated designs already gave +3.9 and +8.8;
  - the ablation shows those designs alone give +4.4 and +9.0 on held-out;
  - the simulator-selected final refinement added nothing measurable.
- **Not established:** how much the simulator diagnosis contributed to finding those first two designs.

**Harness lesson.**

- The sandbox enforced "no game simulator" only by not installing `minatar`.
- Once the full game source is in the brief, re-implementing the game is possible in any Python sandbox. It cannot be blocked technically, only by not supplying the source, or by redefining the condition.
- Future protocols must treat self-written simulators as an explicit condition, with a budget for simulated steps, not as a prohibition. The alternative is to withhold source-level dynamics.

## Other observations

- **Convergence.** Three independent sessions (v1-e1, v2-e1, v2-e2) arrived at exactly the same 2-entry edit, with the same content-addressed patch id. It lowers the surfacing threshold from oxygen < 60 to < 40, and it does not help.
  - Independent model sessions are not independent searches: they share priors and land on the same "obvious" mechanistic idea.
  - Diversity therefore needs different briefs, information or strategies, not just more seeds.
- **Dev-pass reliability.** With 1,000-episode passes (SE ≈ 1.9), dev and held-out agree well:
  - e3: dev +11–13 vs held-out +9–11;
  - p-38e: dev +0.4 to +1.5 vs held-out −0.7 to +0.2.
  - v1's 300-episode passes (SE ≈ 3.3) were too noisy.
- **Hand-designed edits can fail badly.** e1's attempt to turn the sub toward enemies on the right scored −46 because of an ungated detector, and e2's oxygen<20 variant scored −23.
- **Minor deviation.** e1 ran one `python3 -c` outside `LAB py` to parse status JSON. It had no experimental effect.

## Interpretation and confidence

- **Measured:** one of three v2 sessions produced a direct weight edit that improves the hand-written Gold policy on independent held-out seeds. It gave +9.9 [7.5, 12.5] per session, +10.9 ± 0.95 jointly and +9.0 ± 0.93 in the ablation run.
  - This is far beyond size-matched random edits.
  - It is the first positive Phase C result. It is replicated across three fresh seed sets drawn after submission.
- **Confidence:** high that p-8255708841a2 beats Gold on this game and evaluator.
  - Lower confidence in the claim "the editor can do this within the dev-pass budget", because of the deviation.
  - The success rate is 1 of 4 sessions overall (v1 + v2), and 1 of 3 independent ideas.
- **Limitations:**
  - One game, and one hand-written Gold that has obvious slack: no lateral movement.
  - One editor model.
  - The editors had the full environment source.
  - This is improvement of an existing capability, not creation of a new one.
  - Nothing here says anything about small models acting as editors (Phase D).

## Next step

A v3 round with the simulator question as an explicit, pre-registered condition:

- **Condition S:** source supplied, and self-simulation allowed with a budget on simulated steps.
- **Condition N:** rules described in prose only, no source; editors told not to build a simulator.
- Three sessions per condition, the same budgets and joint held-out evaluation.

This measures how much environment-model access, rather than dev feedback, drives successful direct edits. That
quantity also matters for designing the Phase D editor protocol.

## Artifacts

- [protocol.json](protocol.json), [editor_usage.jsonl](editor_usage.jsonl), [editor_reports/](editor_reports/)
  (final reports from the editors, model output), [editor_scripts/](editor_scripts/) (all sandbox scripts the editors wrote).
- [results/patches/](results/patches/): patch.json and a sparse delta for all 10 v2 candidates.
- Held-out runs: `../20261103T-phaseC-seaquest-v2-heldout-e{1,2,3}/`. Joint comparison:
  `../20261103T-phaseC-seaquest-joint-comparison-r2/`. Ablation: `../20261103T-phaseC-seaquest-e3-posthoc-ablation/`.
- Session logs (every LAB call) and raw per-episode held-out data: `evidence/20261103T-phaseC-seaquest-v2/` (gzip text).
