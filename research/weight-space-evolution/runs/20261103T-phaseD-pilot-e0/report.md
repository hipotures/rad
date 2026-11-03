# Phase D pilot — small Gold editor E0 (and p50c) on target families F1–F3

## Question and scope

This pilot covers Phase D prerequisite 3 ([design §9](../../reports/phaseD_bootstrap_gate_design.md)). It asks:
- Does E0 (Qwen3.5-0.8B, text-only export of the Phase A Gold) have measurable signal as a *weight editor* of other networks?
- On which families and tiers does it have that signal?
- How do non-agent baselines compare?

There are no parent sessions and no candidate editors, apart from one existing direct edit of E0: **p50c**, the Phase A
loop-removal edit. It is included as a natural "edited editor".

Protocol: [protocol.json](protocol.json). Code:
- [`wse/targets.py`](../../code/wse/targets.py): target generator;
- [`wse/edit_dsl.py`](../../code/wse/edit_dsl.py): edit DSL;
- [`wse/editor_tasks.py`](../../code/wse/editor_tasks.py): probe text, tiers and baselines;
- [`wse/editor_pilot.py`](../../code/wse/editor_pilot.py): generation and scoring;
- [`wse/pilot_rescore.py`](../../code/wse/pilot_rescore.py): offline strict/lenient rescoring, which gives the primary numbers.

## Setup

- **Targets.** 48 instances of a 20→32→24→6 ReLU classifier (1,644 parameters), 16 per family, drawn from the deterministic `pilot` split.
  - Base nets are trained on synthetic overlapping Gaussian-mixture data. The ceiling test accuracy is 0.78–0.87.
  - The defect lowers test accuracy by 13–35 points:
    - F1: 2–4 of the most important first-layer units are killed (b1 = −40);
    - F2: two output classes are swapped;
    - F3: one output bias is shifted by a 40–80th-percentile logit margin.
- **What the editor sees.** About 420 words of probes: tensor statistics, b1 and b3, h1 activation rates, class counts, the confusion matrix and mean logits on 192 labelled probe inputs.
- **Tiers.**
  - T0: choose 1 of 4 complete edits.
  - T1: fill in the numbers of the named family's template.
  - T2: free-form DSL.
- **Decoding.** vLLM with seed 0 and 4 samples per prompt, 576 generations per editor and mode.
  - Non-thinking: temperature 0.7, top-p 0.8.
  - Thinking: temperature 0.6, top-p 0.95. Maximum 4,096 tokens.
- **GPUs.** Two RTX 4090s ran concurrently, one per mode.
- **Scoring.**
  - Each sample is scored independently: test-set recovery = Δacc / (ceiling − damaged acc).
  - Invalid or missing answers count as no-op (0).
  - A thinking output without `</think>` counts as no answer.
  - "Strict" requires the whole edit block to parse; "lenient" skips unparseable lines (format repair, reported separately).
  - T0 answers are matched case-insensitively. The in-run summaries used a case-sensitive matcher; `results/rescore.json` supersedes them.

## Results

All numbers are mean recovery per (family, tier); n = 64 samples (16 instances × 4); strict parsing unless noted.
1.0 = full repair; 0 = no change; negative = the edit made the network worse.

| Family / tier | E0 no-think | p50c no-think | E0 think | p50c think | T0 chance | Heuristic | Oracle |
|---|---|---|---|---|---|---|---|
| F1 / T0 | −0.54 [−0.82, −0.29] | −0.26 | 0 (no answers) | 0 (2% answered) | −0.29 | 0.98 | 0.98 |
| F1 / T1 | +0.02 (lenient +0.09) | +0.01 | 0 | 0 (53% answered) | – | | |
| F1 / T2 | 0 (0% valid) | 0 | 0 | 0 | – | | |
| F2 / T0 | +0.02 | +0.04 | 0 | 0 | −0.00 | 1.00 | 1.00 |
| F2 / T1 | −0.15 (lenient −0.28) | −0.19 | 0 | −0.04 | – | | |
| F2 / T2 | 0 | 0 | 0 | 0 | – | | |
| F3 / T0 | **+0.37** (75% valid) | +0.29 | 0 | 0 | +0.05 | 0.47 | 1.00 |
| F3 / T1 | −0.01 | +0.06 | 0 | +0.04 | – | | |
| F3 / T2 | 0 | 0 (2% valid) | 0 | 0 | – | | |

- **Heuristic** is a non-agent baseline: the best of three rule-based repairs, selected on the probe set. The rules reset units that never activate to the median b1, swap the most-confused class pair, and lower the most over-predicted class's bias.
- **Random** 4-entry edits: about −0.02 to 0.

### Thinking mode and truncation

| | E0 | p50c |
|---|---|---|
| Truncated at 4,096 tokens | **100%** | **87.5%** |
| Answers produced (T1) | 0% | 20–66% |
| Generation tokens | 2.36M in 246 s | 2.28M in 236 s |

p50c reproduces its Phase A mechanism in a new task: fewer looping/unterminated reasonings. But the extra answers do not
repair anything.

### Paired p50c − E0, non-thinking

Pairing is instance × tier × sample, with identical prompts and seed.

| Tier | Δ recovery | 95% CI |
|---|---|---|
| T0 | +0.07 | [−0.01, 0.17] |
| T1 | +0.00 | [−0.06, 0.08] |
| T2 | 0 | — |

### Cost

- Non-thinking: 0.55–0.65M generated tokens per 576 generations, in 60–71 s.
- Thinking: about 2.3M tokens in about 240 s per GPU.
- Targets are built in about 0.7 s each on one CPU thread. Scoring is negligible.

## Interpretation

- **E0 has essentially no free-form editing ability.**
  - T2 is at floor for every family.
  - The usual T2 failure is copying the grammar help into the edit block, or writing prose.
  - In thinking mode it never finishes within 4k tokens.
- **The only above-chance signal is F3/T0: +0.37 against a chance level of +0.05.**
  - Choosing "lower the huge bias b3[c]" is visible directly in the printed b3, so this is likely a surface cue rather than diagnosis.
  - On F1/T0 E0 is below chance (−0.54 vs −0.29), which points to a systematic preference for a harmful option.
- **p50c does not make E0 a better editor.** It changes answer *availability* in thinking mode, not edit quality. This is a direct example of the design's warning: an edit's effect on a model's ordinary outputs is not the same as editing skill.
- **F1 and F2 are almost fully solved by a 3-rule heuristic** (0.98 and 1.00). As written, they cannot show that an editor beats non-agent baselines (gate criterion 2). F3 leaves room: the heuristic reaches 0.47 and the oracle 1.0.

## Consequences for the gate (to be frozen before any parent session)

1. **Drop T2 in its current form** (E0 and p50c are at floor). Keep T0, and T1 with format-constrained decoding: the design's baseline 5, "format-fixed E0", should become the default decoder for T1/T2.
2. **Replace or harden F1/F2** so that the heuristic baseline does not saturate them. Options:
   - several simultaneous defects;
   - defects in hidden layers, e.g. W2 column permutations or scaled units;
   - partial damage without clean signatures.
   Keep F3, and calibrate tiers so that E0 sits between floor and ceiling.
3. **Thinking mode needs more than 4k tokens, or a non-looping editor.** The 87.5–100% truncation makes thinking-mode editing unusable at this budget.
4. **The editor protocol should get an executable target simulator (probe passes), not only static probes.** Phase C v3 showed this is the main lever for the frontier editor: source plus self-simulation gave 3/3 successes, prose rules alone 1/3. Here that means letting the editor run its candidate edit on the probe set one or more times.

## Limitations

- 16 instances per family and one decoding seed.
- The prompt format was not tuned, and the probes are static.
- p50c is not an edit made to improve editing. It is only a convenient existing candidate.

## Artifacts

- `results/`:
  - `rescore.json` gives the primary numbers: strict/lenient, chance and pairwise.
  - `*_summary.json` is the in-run scoring (superseded for T0, see above). Per-sample rows: `evidence/20261103T-phaseD-pilot-e0-per-sample/`.
  - `baselines_per_instance.json`.
- Full generations, with prompts and outputs: `evidence/20261103T-phaseD-pilot-e0/` (gzip text).
