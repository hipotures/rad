# MinAtar evaluator validation — report

**Outcome: pass.** Statistical agreement with the published exp5 scores (different episode seeds).

| Game | Ours (1,000 ep.) | Published | z |
|---|---|---|---|
| Seaquest `hand.npz` | 53.13 ± 1.35 (mean length 1,413) | 53.11 ± 1.36 (1,412) | +0.01 |
| Asterix `hand.npz` | 52.82 ± 1.06 (855) | 53.18 ± 1.02 (858) | −0.24 |

Both the means and the mean episode lengths agree, which supports the observation mapping, sticky-action handling
and sampling. 1,000 Seaquest episodes took 11 s with 4 worker processes (≈125k steps/s total). Breakout was not run
(mean length ≈ 7,400 steps; slower and not needed). Per-episode seed determinism is covered by unit tests.
