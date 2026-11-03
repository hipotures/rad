# Editor final report — session phaseC-seaquest-v3N-e2 (model output, condensed by operator)

> Operator notes: condition N (prose rules only). Pass 3 re-evaluated candidate A because the editor's own probe
> script called `reset()`, its `propose` was refused ("patch changes nothing") and its chained shell command still ran
> `devpass` on the newest existing id (editor-side error, not a harness fault). Interrupted by the API rate limit and
> resumed (see protocol.json).

Submitted **p-38e02409d21a** (edit C, best guess; no edit beat Gold on dev). 5/6 passes, 15/25 sandbox runs.

| Pass | Candidate | Gold | Cand. | Δ (SE) | 95% CI |
|---|---|---|---|---|---|
| 1 | gold, traces | 50.86 | – | – | – |
| 2 | A p-309bd39c143d (16 W1: zero reward weights at cols 7–8 in danger units 16–23) | 52.90 | 48.28 | −4.62 (1.54) | [−7.6, −1.6] |
| 3 | A again (wasted) | 54.08 | 47.83 | −6.25 (1.57) | [−9.3, −3.0] |
| 4 | C p-38e02409d21a (unit 24 gauge cell (9,2)→(9,1): surface at oxygen < 40) | 53.27 | 51.97 | −1.30 (1.90) | [−4.8, 2.6] |
| 5 | D p-d3c0762c03bc (6 W1: wait at row 0 until row 1 clear) | 51.96 | 49.10 | −2.85 (1.28) | [−5.3, −0.4] |

Diagnosis: hand-wired lookup (h1 0–8 sub row; 9–15 divers; 16–23 centre-weighted danger with reward channel
subtracted; 24 "diver aboard & oxygen < ~60"; 25–31 left-side enemies); left/right bias −100 → never moves sideways;
score ∝ survival (r = 0.98 with length, ~0.037/step). Hypothesis (7 traced deaths): ascent mode ~10× more dangerous
per step; unconfirmed. Could not identify a helping edit. Mild selection among 3 hand-designed edits; no rule breach
reported; trace statistics computed from logged data only (no simulator).
