# Phase D pilot, constrained decoding: "format-fixed" E0 and p50c on F1–F3

## Question

Phase D design baseline 5 asks: once format failures are removed by grammar-constrained decoding, do E0 and p50c show
editing signal?

## Setup

This run is identical to [20261103T-phaseD-pilot-e0](../20261103T-phaseD-pilot-e0/report.md) except for the output constraint:
- same 48 instances, prompts, 4 samples, seed 0 and non-thinking sampling;
- vLLM structured outputs restrict T0 to `ANSWER: A`…`ANSWER: D`;
- T1/T2 are restricted to a fenced edit block of 1–8 DSL statements (`DSL_REGEX` in [`wse/editor_pilot.py`](../../code/wse/editor_pilot.py));
- no free-text reasoning is possible.

Protocol: [protocol.json](protocol.json). Scoring: [`wse.pilot_rescore`](../../code/wse/pilot_rescore.py), strict, with
pairing against the unconstrained runs. Results: [results/rescore.json](results/rescore.json).

## Results

Mean recovery [95% bootstrap CI]; n = 64 per cell.

| Family / tier | E0 constrained | valid | full repair | p50c constrained | E0 unconstrained (strict) | T0 chance | heuristic |
|---|---|---|---|---|---|---|---|
| F1 / T0 | −0.88 [−1.21, −0.57] | 1.00 | 0.09 | −0.79 | −0.54 | −0.29 | 0.98 |
| F1 / T1 | +0.02 [0.00, 0.05] | 0.58 | 0.00 | +0.02 | +0.02 | | |
| F1 / T2 | −0.31 [−0.54, −0.12] | 0.88 | 0.00 | −0.20 | 0 (0% valid) | | |
| F2 / T0 | −0.03 [−0.18, 0.12] | 1.00 | 0.23 | −0.15 | +0.02 | −0.00 | 1.00 |
| F2 / T1 | −0.33 [−0.47, −0.17] | 0.84 | 0.14 | −0.42 | −0.15 | | |
| F2 / T2 | −0.01 | 0.95 | 0.00 | −0.02 | 0 | | |
| F3 / T0 | **+0.41 [0.24, 0.58]** | 1.00 | **0.56** | +0.38 | +0.37 | +0.05 | 0.47 |
| F3 / T1 | −0.03 | 0.23 | 0.00 | −0.03 | −0.01 | | |
| F3 / T2 | **+0.12 [0.04, 0.20]** | 0.92 | **0.11** | +0.10 | 0 | | |

### Answer choice and validity

- **T0 position bias.** E0's constrained T0 answers were D 92, C 72, B 21 and A 7 times out of 192, while the correct option's position is uniform.
- **T1 failures** under the constraint are out-of-range indices, for example `b3[24]` or `b1[32]`. The grammar fixes syntax, not semantics.

### Paired comparisons (constrained − unconstrained E0)

| Tier | Δ | 95% CI |
|---|---|---|
| T0 | −0.12 | [−0.24, −0.01] |
| T1 | −0.07 | [−0.13, 0.00] |
| T2 | −0.07 | [−0.15, 0.01] |

- Constraining makes outputs valid but, on average, *more harmful*: invalid outputs had been scored as harmless no-ops.
- p50c − E0 under the constraint: T0 −0.02, T1 −0.03, T2 +0.03, all with CIs spanning 0.

### Cost

One constrained run of 576 generations took about 4.5 s and 14–17k generated tokens per GPU, against 60–70 s unconstrained.

## Interpretation

- **Format was hiding harm, not hiding skill.** With valid outputs guaranteed, E0's edits are mostly wrong:
  - F1 is harmful at every tier.
  - F2 is neutral to harmful.
- **F3 (over-predicted class from a shifted bias) is the one family where E0 shows real editing signal:**
  - T0 +0.41, with 56% full repairs against a chance level of +0.05;
  - free-form T2 +0.12, with 11% full repairs.
  The cue is visible in the printed b3, where one entry is far larger than the rest, so this is "read the anomaly and subtract", not diagnosis from behaviour.
- **p50c is indistinguishable from E0 as an editor** with or without the constraint. This confirms the unconstrained pilot.
- **For the gate,** F3/T2 constrained is a usable primary cell:
  - E0 is between floor and ceiling at 0.12;
  - the heuristic reaches 0.47 and the oracle 1.0;
  - outputs are valid at 92%.
  T0 needs balanced option positions, or permutation averaging, to remove the strong position bias.

## Limitations

- 16 instances per family and one seed.
- The constraint removes any chance for the model to reason before answering. A "reason, then constrained answer" format was not tested.

## Artifacts

- `results/rescore.json` (primary numbers), `*_summary.json` (in-run scoring), `baselines_per_instance.json`.
- Generations and per-sample rows: `evidence/20261103T-phaseD-pilot-constrained/` (gzip text).
