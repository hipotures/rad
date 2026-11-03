# Phase D v2 pilot — Gold / p50c and protocol freeze (Workstream A)

Run ID `20261103T-phaseD-v2-pilot`; configuration in [protocol.json](protocol.json); results in
[results/editor_results_pilot.json](results/editor_results_pilot.json); frozen protocol in
[../../configs/phaseD_v2/protocol_v2_frozen.json](../../configs/phaseD_v2/protocol_v2_frozen.json).

## Benchmark v2 (what changed from v1)

v1 problems (see [../20261103T-phaseD-pilot-constrained/report.md](../20261103T-phaseD-pilot-constrained/report.md)):
a 3-rule heuristic solved F1 and F2, T0 had a strong position bias, and free-form output was mostly invalid.

| family | targets | core subtypes (dev/select/test) | held-out subtypes (transfer) |
|---|---|---|---|
| F1 dead/disabled units | random MLPs, d_in 16–24, 2–3 hidden layers of 24–48, 5–8 classes | dead_bias, in_scale, out_mute (2–4 units), mixed | sign_flip |
| F2 output/hidden mapping | same | out_perm, out_perm_w, hidden_swap | in_swap |
| F3 bias/activation | same | out_bias, out_bias_pair, hidden_bias, logit_scale | layer_bias |
| F4 policy repair | MinAtar Seaquest/Asterix exp5 hand networks, 300 paired test episodes | action_suppress, action_swap, unit_mute, unit_saturate | input_blind |
| F5 algorithmic transformers | 1-layer, d 32, 2 heads; modadd p∈{17,19,23}, reverse | — (held-out family) | head_mute, qk_flatten, mlp_mute, unembed_swap, embed_swap, pos_swap |

- **Hardening.** Defects are drawn larger and combined. Instances must have a gap of at least 0.10, a ceiling of
  at least 0.60, and an oracle of at least 0.95 to be accepted. Permutation, swap and bias-pair subtypes defeat
  the v1 rules.
- **Tiers.** T0 picks one of 4 complete edits. Every instance has 4 rotations, so the oracle sits once at every
  position. The distractors are consistent retargetings of the oracle. T1 is a named subtype with the oracle
  template's numbers blanked, constrained to the template regex. T2 is a free DSL edit constrained to the instance
  DSL regex. T2P is T2 plus one budgeted probe pass: a trial edit gets probe-set feedback, then a final edit is
  made.
- **Validity versus effectiveness.** Both are reported separately. Invalid edits are scored as no-ops.
- **Baselines per instance.** No-op (0), 8 matched random edits (same statements and indices, random values;
  draws identical to the oracle are excluded), a simple heuristic, an improved probe-search heuristic (Hungarian
  matching, norm outliers and so on, with a counted number of probe evaluations), and the oracle.
- **Splits.** Seeds are `sha256(version/split/family/subtype/index/attempt/salt)`. Test and transfer use a secret
  salt in `work/benchmarks/phaseD-v2/secret_salt.txt`; its sha256 `cc1e5683…c096` is committed. Public manifests
  are pilot, dev and select. Test and transfer publish only aggregates and a manifest hash. The evaluator refuses
  held-out splits without `--allow-heldout`.
- **Determinism.** `python -m wse.pd2_bench verify --split dev` regenerated 6 of 6 sampled instances
  byte-identically.

## Pilot results (95 instances, 1520 samples per editor)

Mean recovery [95% instance-bootstrap CI] / valid rate for E0 (Gold):

| family | T0 | T1 | T2 | T2P | simple heur. | improved heur. (probe evals) | random matched | T0 chance |
|---|---|---|---|---|---|---|---|---|
| F1 | −0.65 [−0.89, −0.41] / 1.00 | −0.13 / 0.62 | −0.16 / 0.51 | −0.04 / 0.66 | 0.22 | 0.55 (8.2) | −1.18 | −0.72 |
| F2 | 0.08 [−0.04, 0.18] / 1.00 | −0.15 / 0.73 | −0.06 / 0.61 | −0.01 / 0.66 | 0.27 | 0.50 (7.8) | −0.18 | 0.06 |
| F3 | 0.07 [−0.06, 0.18] / 1.00 | 0.08 / 0.53 | −0.03 / 0.57 | −0.01 / 0.68 | 0.35 | 0.84 (6.6) | −0.22 | 0.05 |
| F4 | 0.04 [−0.12, 0.19] / 1.00 | −0.09 / 0.75 | −0.02 / **0.43** | 0.00 / 0.55 | 0.08 | 0.45 (20.4) | −0.07 | 0.06 |
| F5 (transfer family) | 0.03 / 1.00 | −0.12 / 0.92 | −0.02 / 0.54 | −0.02 / 0.45 | 0.26 | 0.90 (10.6) | −0.30 | −0.01 |
| all | −0.10 | −0.08 | −0.06 | −0.02 | 0.24 | 0.68 | −0.42 | −0.12 |

Oracle recovery is 1.00 in every family. E0 overall is −0.062 [−0.097, −0.028]; its effective rate is 7% and its
regression rate 26%.

**p50c − E0, paired by instance × tier × sample:** −0.005 [−0.019, +0.010] (n = 1520). The difference is not
significant, and no cell is significantly better. p50c changes outputs — greedy agreement with Gold is 0.03 — but
not edit quality.

**T0 position bias.** E0 answers D 210 times out of 380 (A 15, B 49, C 106). Accuracy when the oracle is at A is
0.03; at D it is 0.55. Overall T0 accuracy is 0.245, against 0.25 chance. The balanced rotations turn the bias
into chance-level accuracy instead of a spurious advantage. The T0 recovery tracks the option set's chance value,
which is strongly negative in F1, where the distractors are harmful.

**Resources per editor on the pilot.** About 14 s of round-1 generation, 6 s of probe feedback (CPU scorer) and
6 s of round-2 generation, with about 74 k generated tokens. Scoring took about 30 s on the CPU, overlapping the
next job.

## Freeze decision (pre-registered rule applied mechanically)

`code/wse/pd2_freeze.py` applied the rule recorded in `protocol_v2_draft.json` before the pilot generations were
scored. The rule requires oracle ≥ 0.90, simple heuristic ≤ 0.60, T0 chance ≤ 0.40, E0 ≤ 0.80 and E0 valid ≥ 0.50.

- **Primary cells (15):** F1–F3 × {T0, T1, T2, T2P}; F4 × {T0, T1, T2P}.
- **Excluded:** F4/T2, because the E0 valid rate of 0.43 is below 0.50 and format would be the bottleneck. It is
  still reported as secondary.
- **Floor flags** (E0 ≤ 0.02, kept, so improvement must come from candidates): all cells except F2/T0, F3/T0,
  F3/T1 and F4/T0.
- **F5** is a transfer-only family and is not part of the primary endpoint.
- **Primary endpoint** on the test split: the paired candidate − E0 difference over the primary cells, with an
  instance-cluster bootstrap and Holm correction across candidates.
- **Manifests:** pilot 95, dev 104, select 104, test 200, transfer 92 instances. Hashes are in the frozen file.

## Interpretation

- **Measured.** Gold Qwen3.5-0.8B does not repair these networks. It is at or below no-op in every family and tier
  except chance-level T0. p50c does not change that. The benchmark therefore has a lot of headroom. The improved
  heuristic reaches 0.45–0.84 on the core families, and the oracle reaches 1.0.
- **Measured.** The probe pass (T2P) mostly reduces harm (regression rate 0.11 versus 0.16 for T2) rather than
  producing repairs.
- **Inference.** A four-parent study that starts from these editors will be measured from a floor. A useful
  candidate has to show a positive paired difference in floor cells. The large negative T0 chance in F1 means T0
  improvements there can come from avoiding harmful options as well as from picking the oracle. Per-cell reporting
  keeps these apart.
- **Limitation.** The pilot has 3–4 instances per subtype, so subtype-level estimates are noisy. Cell decisions
  rest on family-level means.

## Reproduction

```bash
cd research/weight-space-evolution/code
../work/envs/wse/bin/python -m wse.pd2_bench generate --split pilot      # instances -> work/benchmarks/phaseD-v2/pilot
Q=../work/queues/pilot; ../work/envs/vllm/bin/python -m wse.pd2_eval submit --queue $Q --editors E0,p50c --split pilot
CAMPAIGN=20261103T-phaseD-v2-pilot QUEUE=$PWD/$Q GPUS="0 1" scripts/run_pd2_workers.sh
../work/envs/wse/bin/python -m wse.pd2_report --campaign 20261103T-phaseD-v2-pilot --split pilot --out ../runs/20261103T-phaseD-v2-pilot/results
../work/envs/wse/bin/python -m wse.pd2_freeze --pilot ../runs/20261103T-phaseD-v2-pilot/results/editor_results_pilot.json --out-dir ../configs/phaseD_v2
```
