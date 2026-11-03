# Re-verification of Phase C v1 candidate B with active-weight controls — report

**Outcome: candidate B (`p-38e02409d21a`) is not an improvement.** On a fresh 2,000-episode held-out set it scores
**−2.97 ± 1.32 vs Gold (95% CI −5.58 … −0.36)**.

| Arm (2,000 paired episodes, seeds in `protocol.json`) | Mean | Δ vs Gold (SE) | 95% CI | identical episodes |
|---|---|---|---|---|
| Gold | 54.45 | – | – | – |
| Candidate B | 51.48 | −2.97 (1.32) | [−5.58, −0.36] | 98 |
| Flip (Gold − Δ) | 50.66 | −3.79 (0.43) | [−4.60, −3.01] | 1,689 |
| permuted_0/1/2 (active weights) | 53.52 / 52.89 / 53.95 | −0.92 / −1.55 / −0.50 | | 1,011 / 873 / 1,400 |
| gaussian_0/1/2 (active weights) | 52.05 / 52.28 / 52.13 | −2.40 / −2.17 / −2.32 | all exclude 0 | 1,201 / 714 / 1,363 |

- Combined with the first held-out check (+1.83 ± 1.89 on 1,000 episodes), the inverse-variance pooled effect is
  ≈ −1.4 ± 1.1: no evidence of improvement; the two estimates differ by z ≈ 2.1 (plausibly sampling variation).
- Active-weight controls now always change behaviour (v1 unrestricted controls were 50% exact no-ops) and are mostly
  harmful: random perturbations of live weights degrade this hand-written policy. "Beats random edits" is therefore a
  weak bar here; the relevant comparator is Gold.
- Both directions of the oxygen-threshold edit (B and its flip) lower the score: Gold's threshold appears to be near a
  local optimum along this axis.

Command: `python -m wse.heldout --session phaseC-seaquest-v1-e1 --out-dir runs/<this run> --raw-dir work/raw/<this run>
--episodes 2000 --control-seeds 3 --active-controls --workers 2`.
