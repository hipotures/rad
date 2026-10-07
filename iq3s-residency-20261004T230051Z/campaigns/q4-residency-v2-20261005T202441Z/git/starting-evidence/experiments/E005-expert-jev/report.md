# Expert-Jev-inspired numeric scorers

Status: COMPLETE_NEGATIVE for the predeclared linear/MLP/temporal replay evaluation. This does not close all learned/predictive methods. The small models score explicit expert candidates; no released Open-Jev language backbone runs beside IQ3_S. Open-Jev revision and MIT origin are recorded in sources.json.

Development tasks: code and mathematics. Calibration: independent prose task. Holdout: transactional code, structured JSON and polynomial mathematics. Whole episodes are separated; observed state updates are causal; labels are next-four-window counts including rejected speculative branch work. Two development tasks are a small sample, so generalization is limited. The main long repository-maintenance requests were not used to fit predictors.

The target is log1p expected count under an inverse-sampling-weighted squared objective, not a softmax or probability that exactly one expert is used. Mean/std are fitted only on development rows. The affine count calibration uses calibration prose only and clamps negatives. Raw sampled data, sampling indices, checkpoints, seeds and hashes remain in v1.

| Held task | EMA coverage | Linear | MLP | Temporal MLP |
|---|---:|---:|---:|---:|
| hold-code | 98.767% | 98.775% | 98.455% | 98.331% |
| hold-structured | 99.057% | 99.052% | 98.720% | 98.637% |
| hold-math | 99.062% | 99.050% | 98.827% | 98.738% |

Capacity-ranking coverage is a cost-free proxy. Finite-copy replay is also completed at both profiles and increases nonlocal entries for all three learned scorers. Linear ranking essentially duplicates EMA; the MLP and temporal features are weaker. Temporal ablation therefore has an explicit measured disposition.

| Scorer | Parameter bytes | Training s | Checkpoint SHA256 |
|---|---:|---:|---|
| linear | 216 | 0.0425 | `b4f84d60ce7d9f09ef64fbb108ca00320b2666de9765c0b7d37efb61ca562664` |
| mlp | 1128 | 0.6498 | `b5dc7f64e22927bc88a5398066c03385c0c66285a6ae783be07dfc083646bd8c` |
| temporal-mlp | 1432 | 0.6924 | `c4dffa12831c8282c06d8ff39a00573d8aeccea91d32dab015fbb0021dfe3625` |

Numeric full-candidate inference is approximately 0.29 / 0.65 / 0.75 ms for linear / MLP / temporal. These are CPU numerical scoring costs only; feature extraction, state updates, selection, transfer timing and contention are not included. No deployable runtime overhead or TG gain is claimed. Additional GPU predictor memory is zero in replay; live memory/cost remains untested.

Next decision: test the simple frequency policy live, normalize the transition baseline, and investigate legitimately available token/router signals. Do not train a large model or claim a universal negative conclusion from this small dataset.
