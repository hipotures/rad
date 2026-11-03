# Editor final report — session phaseC-seaquest-v3N-e1 (model output, condensed by operator)

> Operator notes: condition N (prose rules only). Self-reported minor deviation: `LAB status` piped once into host
> `python3` to extract a candidate id (failed, no effect). A 7th devpass was refused by the harness (budget enforced).
> Interrupted by the API rate limit and resumed.

Submitted **p-2efb8ec9bc87** (candidate F, 108 entries). 6/6 passes, 18/25 sandbox runs.

**Diagnosis.** Fixed rule set: noop/left/right biases −100 (column 5, facing left); h1 row/diver/central-danger/
left-enemy detectors + h1[24] gauge unit (oxygen < 60 & diver aboard); h2 per-row fire/up/down with up blocked into
central danger. Score ∝ survival (r = 0.98; ~0.037 kills/step; length 1,365–1,445); traced deaths cluster at oxygen
55–56 right after ascent starts; ~6% of episodes end before step 150; vertical wandering ~21% of steps (12%/12% up/down
in empty scenes); seeking pull toward shootable enemies decays quickly (0.35, 0.12, 0.04, 0.01 for 0–3 rows).

**Edit F.** b3[5] +2 (fire bias; wandering ~24% → ~4%); W2 from h1[25..31] to up/down units h2[8..14], h2[16..23]
(92 entries) with slower decay (0.35, 0.20, 0.12, 0.08, 0.05, 0.03, 0.02, 0.01); b2 offsets on those 15 units.

| Pass | Candidate | Change | Δ vs Gold (SE) | 95% CI |
|---|---|---|---|---|
| 1 | gold | baseline, 3 traces | Gold 50.86 | – |
| 2 | A p-adfbbf2635e8 | earlier right-side detection (32 W1) | −9.9 (1.6) | [−13.0, −6.7] |
| 3 | B p-78ee02022218 | stronger danger block (30 W2/b2) | −4.5 (1.4) | [−7.2, −1.9] |
| 4 | E p-8e94a29d57ea | fire bias +2 only | +0.44 (1.64) | [−2.7, 3.6] |
| 5 | F p-2efb8ec9bc87 | E + longer-range seeking | +1.74 (1.58) | [−1.4, 4.8] |
| 6 | G+F p-16cf5e240c8b | F + no up-moves from row 3 except ascent | −6.0 (1.7) | [−9.3, −2.5] |

Uncertainty: F rests on one non-significant pass after five candidates (selection); expected held-out gain 0 to +2.
