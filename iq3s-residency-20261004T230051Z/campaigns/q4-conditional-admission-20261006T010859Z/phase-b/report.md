# Phase B — conditional admission and task-level holdout

The frozen logistic model (threshold p ≥ 0.12) qualified for experimental live testing through the explicitly documented numerical-aid judgment. Its pooled efficiency result passed, while the additional code-family guard failed. The failed guard remains preserved; no model or threshold was retuned on holdout.

The 12 independent task episodes comprise four code documents, four applied math problems and four structured/prose packets. Four whole tasks form development, two calibration and six holdout. The entire structured family is held out. Actual inputs are 162–6991 tokens and outputs 1024 tokens; long-context, 4096-output inference therefore extrapolates these conditions. Final four-window future-use labels are censored.

| Split | Unpublished traffic avoided | Next-four demand potential retained | Aggregate observed-use retention | Nonlocal ratio | Victim-absent ratio |
|---|---:|---:|---:|---:|---:|
| Calibration | 77.93% | 86.64% | 94.76% | 1.01348 | 0.87800 |
| Holdout | 73.76% | 85.38% | 90.16% | 1.01342 | 0.84847 |

| Holdout family | Unpublished traffic avoided | Next-four demand potential | Aggregate use retention | Nonlocal ratio |
|---|---:|---:|---:|---:|
| Code | 70.66% | 76.69% | 72.24% | 1.02200 |
| Math | 69.92% | 86.79% | 92.70% | 1.01419 |
| Structured | 75.27% | 87.20% | 92.54% | 1.01124 |

The post-hoc contiguous attribution audit retains 49,647 of 55,067 observed local entries (90.16%). Attribution ends at the first native-cache or other early touch; the aggregate use ratio happens to agree in this holdout set. Contiguous victim-absent observations fall 1790→1518. Neither ratio proves exclusive savings against a counterfactual adaptation policy. Next-four 'benefit' is future demand potential, not guaranteed resident or exposed-latency benefit. No fit, threshold or model selection changed during this audit.

H4 plus history/state has held-out average precision 0.57430, versus 0.54187 for history/state alone on the same already-H4-selected candidate set. This is a conditional-feature ablation, not a causal H4-versus-reactive runtime comparison. Publication precision is 35.10%, count recall 80.68%; 290 of 1501 target-ready publications are rejected.

The mandatory rule baseline and three coarse linear operating points are preserved. Selective rules and the conservative linear gate lose useful admissions; permissive rules leave most waste. No nonlinear model was justified. The auxiliary victim-hazard model has R² = −0.00436 and low rare-damage average precision; it is not deployed. Prospective and actual safe victims can differ.

The simulator uses fixed observed demand/native changes, the same byte class and capacity, and attribution bounded by native/early touches. It is not a deployable oracle, an exact counterfactual native-cache simulation or a TG forecast. The 0.25 ms/CPU-entry cost is a modeled sensitivity, not additive exposed request time. Measured Q4 staging/queue and H2D priors are recorded separately.

The ready-vector CPU scalar scorer costs 26.65 ns/action. This excludes history/feature extraction, candidate selection, GPU H4, synchronization and publication costs, which are paid and measured in live requests.

Evidence: [frozen selection](frozen-decision.json), [original strict result](holdout-decision.json), [explicit live gate](live-gate.json), [transaction details](../analysis/heldout-transaction-details.json), [contiguous reporting audit](../analysis/contiguous-holdout-audit.json), [features](../datasets/feature-definitions.md), [calibration/PR curves](../analysis/plots/admission-holdout.png).
