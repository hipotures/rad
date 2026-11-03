# Editor final report — session phaseC-seaquest-v3S-e1 (model output, condensed by operator)

> Operator notes: condition S (source + permitted self-simulation). Self-reported minor deviation: `LAB devpass`
> output piped into host `python3 -c` to parse JSON (twice; no experimental effect). One sandbox run killed with
> rc 137 (attributed by the editor to memory; consistent with the CPU-time limit finding in protocol.json).
> Interrupted by the API rate limit and resumed.

Submitted **p-1bdd9d14fb09** (42 entries: 27 W2, 15 b2). 4/6 passes, 21/25 sandbox runs.

**Diagnosis (weights, hand-built probes, own simulator).** Column 5 facing left (no-op/left/right bias −100); ~79%
fire, ~21% up/down. h1: sub row, diver row, central danger row (columns ~2–8), surfacing unit (oxygen < 60 & diver),
left-danger units. h2: per-row fire/up/down units, finely balanced near tanh saturation; own-row danger suppresses
firing; danger in the target row vetoes with −3; danger two rows away only −0.3. Simulator Gold 50–56 (150–600 ep.).
Deaths (simulator, 300 ep.): fish 141, enemy sub 74, enemy bullet 69, oxygen 9, empty surfacing 6. 237 of 366
collision deaths (400 ep.) followed an up/down move with policy probability < 5% — the 10% sticky repeat carrying
the sub a second row into an enemy two rows away; the −0.3 lookahead veto does not prevent this.

**Edit.** A (two-row lookahead veto): 13 W2 entries −0.3 → −3.0 (danger detector row r∓2 → up/down unit for sub in
row r), 13 b2 entries compensated for the detector's resting value tanh(−3) (uncompensated version −44 to −51 in the
simulator). B (own-row gate): +3.0 from own-row danger detector to that row's up/down units (14 W2), b2 compensated
(15 b2 total), cancelling the lookahead veto when the own row is dangerous. Simulator: B adds +7.2 (1.8) on top of A.

| Pass | Candidate | Gold | Cand. | Δ (SE) | 95% CI |
|---|---|---|---|---|---|
| 1 | p-e54b98937b93 (A) | 50.86 | 67.20 | +16.34 (1.60) | [13.2, 19.6] |
| 2 | p-1bdd9d14fb09 (A+B) | 52.90 | 72.35 | +19.46 (1.75) | [16.0, 22.9] |
| 3 | p-1bdd9d14fb09 (A+B) | 54.08 | 70.57 | +16.49 (1.74) | [13.1, 20.0] |
| 4 | p-e54b98937b93 (A) | 53.27 | 67.34 | +14.07 (1.66) | [10.9, 17.0] |

Episode length: Gold ≈ 1,365, A ≈ 1,806, A+B ≈ 1,924. Rejected in the simulator: stronger own-row fire veto (≈ −1);
up from row 2 under own-row danger (≈ −1); trail-based early detection from behind (−11 to −20); surfacing at oxygen
< 80 (−6). Side effect: oxygen deaths 98 → 156 per 1,000 simulated episodes. A few discrete design values compared in
the simulator (−1.5 vs −3.0; +3).
