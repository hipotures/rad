# Editor final report — session phaseC-seaquest-v3N-e3 (model output, condensed by operator)

> Operator notes: condition N (prose rules only). Self-reported minor deviations: one system `python3`/`grep` outside
> `LAB py` to extract a candidate id from `LAB status` output; one broken shell command attempted a devpass with an
> empty id (refused, no pass consumed). Interrupted by the API rate limit and resumed.

Submitted **p-593f8c8eb139** (14 W1 entries). 5/6 passes, 15/25 sandbox runs.

**Diagnosis.** Left/right logits −100: the sub stays at column 5 facing left (≈79% fire, 10% up, 11% down) and can
shoot only enemies from the left. Existing survival rules: avoids rows with central danger, stops firing with danger
in its own row, seeks divers in other rows, surfaces when oxygen < 30% (gauge (9,2) dark) with ≥1 diver ((9,8) lit).
Deaths are mostly collisions; 6 of 12 traced deaths happened while climbing to surface (oxygen ≈ 50–58), with
bouncing between rows 2–3. Forward passes: when the row above has danger, "up" is suppressed and a diver below pulls
the sub down (p 0.96–0.99); nothing tells it divers stop mattering once surfacing is due.

**Edit.** Diver units h1[9..15]: weight −6 from input (9,8,gauge) and +3 from (9,2,gauge) → a diver unit is switched
off when surfacing is due, so the sub holds its row and fires until the row above clears. Checked: downward escape
from danger in its own row still p = 1.0; diver seeking with no diver aboard preserved. Side effect: with oxygen
30–90% and no diver aboard the diver units are partly on without a diver (up/down/fire logits +≈16 together).

| Pass | Candidate | Change | Δ vs Gold | Note |
|---|---|---|---|---|
| 1 | p-439a914e5f39 | danger detectors widened to columns 7–8 + extra dodge | −14.3 [−17.3, −11.4] | shorter episodes |
| 2 | p-73467fce07c2 | b3 up/down −2 | −1.5 [−4.7, 1.7] | longer, fewer kills/step |
| 3 | p-7146d3cade78 | left target detectors ignore enemy bullets | −1.1 | 498/1,000 ties |
| 4 | p-593f8c8eb139 | diver attraction off when surfacing is due | +4.6 (53.3 → 57.9) | longer episodes |
| 5 | p-593f8c8eb139 | repeat | +4.2 [1.2, 7.1] | 482 better / 369 worse |

Uncertainty: modest gain (~8%); chosen after seeing pass 4, partially confirmed by pass 5; mechanism inferred from
12 traced episodes.
