# Editor final report — session phaseC-seaquest-v3S-e2 (model output, condensed by operator)

> Operator notes: condition S (source + permitted self-simulation). Interrupted by the API rate limit and resumed.
> Reported harness anomaly: sandbox runs 9 and 10 were killed (rc 137) at ~31 s wall-clock although the stated limit is
> 120 s (investigated in the run report).

Submitted **p-011e6d1a4b4c** (9 entries: W2, b2, W3, b3). 2/6 passes, 12/25 sandbox runs.

**Diagnosis (weights, forward passes, own simulator).** Left/right logits −100 (b3, zero W3 columns): column 5, facing
left. h1 0–8 sub row, 9–15 divers by row, 16–23 danger near columns 4–6 per row, 24 "surface now", 25–31 left danger;
h2 0–7 fire, 8–15 up, 16–25 down, 26–31 unused. Own simulator reproduces Gold (51–55 on 200–1,500 episodes). Simulator
death analysis: ~90% collisions; ~2/3 of collision deaths on a sticky up/down move; deaths cluster near the surface
(row 1: 95, row 2: 76 … row 8: ~20 of 374). Specific flaw: from rows 0 and 1 Gold chooses "down" with p = 1.0 even
with an enemy at column 5 in the row below (down bias b3 = 244 wins when all units are inactive).

**Edit.** Two "down-veto" units in unused h2[26], h2[27]: unit 26 = row 0 ∧ danger in row 1 (W2[0,26] = W2[16,26] = 5,
b2[26] = −5); unit 27 = row 1 ∧ danger in row 2 (W2[1,27] = W2[17,27] = 5, b2[27] = −5); W3[26,4] = W3[27,4] = −50,
b3[4] 244 → 144 (inactive units cancel the bias change; active unit lowers "down" by 100).

| Source | Episodes | Δ vs Gold (SE) |
|---|---|---|
| own simulator | 500 / 1,500 / 1,000 | +2.9 (2.4) / +5.2 (1.4) / +1.5 (1.8) |
| dev pass 1 | 1,000 | +4.34 (0.69), CI [3.09, 5.67]; 131 better / 47 worse / 822 tied |
| dev pass 2 | 1,000 | +4.16 (0.67), CI [2.84, 5.49]; 127 / 41 / 832 |

Dropped (simulator only, never proposed): danger detection to columns 7–9 (−9 to −19); "two rows ahead" weights −0.3 →
−3 (≈ −50); fire bias +1/+2 (≈ +2.5, noisy), +4 negative; extra vetoes (−0.25 ± 2.1 vs submitted). About 8
hand-reasoned variants compared in the simulator (selection, as permitted in condition S). Untested bigger
opportunity: turning to shoot right-side enemies (no free h1 units).
