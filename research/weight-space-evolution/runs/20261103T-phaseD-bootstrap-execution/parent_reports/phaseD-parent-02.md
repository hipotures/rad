## Sealed candidate

**`p-9378a8c33b6a`**
Complete lineage: **Gold → candidate**, with no intermediate parent.

Exact submitted recipe:
```python
reset()
n = "model.language_model.layers.11.self_attn.q_norm.weight"
a = gold(n).copy()
a[52] *= np.float32(1.5)
save(n, a)
```

Broker BF16 rounding changed **one entry: 1.1328125 → 1.703125**. Delta L2: **0.5703125**. Everything else remains Gold.

## Result: reduced severity, not useful repair

Selection used equal-family mean recovery across T2/T2P, averaging repeats.

- Candidate: **−0.062252**, reproduced in both evaluations.
- Near-Gold control: **−0.063835**, also reproduced.
- Difference: **+0.001583**.
- Candidate open-ended effective/full repairs: **0/832**.
- Regression frequency actually increased: **19.35% versus 19.11%**.

Thus, average damage severity decreased slightly, but **useful repair capability was not established**.

### Per-family recovery

| Family | T0 | T1 | T2 | T2P | Open-ended Δ vs control |
|---|---:|---:|---:|---:|---:|
| F1 | −.74130 | −.18964 | −.13340 | −.05929 | +.01243 |
| F2 | +.17204 | −.17416 | −.02615 | −.03346 | −.00741 |
| F3 | +.05511 | −.08166 | −.03014 | −.02779 | −.00230 |
| F4 | −.05052 | −.27085 | −.14731 | −.04049 | +.00361 |

F2 and F3 regressed relative to control.

## Numerical experiment record

All proposals independently started at Gold using `reset()`; submission applied BF16 rounding.

Let **Q** be the query-norm tensor above, **D** be `model.language_model.layers.12.linear_attn.dt_bias`, and **M** be `model.language_model.layers.11.mlp.down_proj.weight`.

| Recipe | Passes | Mean open-ended recovery |
|---|---|---:|
| `Q[52] *= 1.0625` | 1,12 | −.064853 |
| `Q[52] *= 1.25` | 2,15 | −.062737 |
| `Q[52] *= 0.75` | 3 | −.070249 |
| `D[11] -= 0.125` | 4,14 | −.063061 |
| `D[11] -= 0.5` | 5 | −.067419 |
| `D[11] += 0.5` | 6 | −.066733 |
| `M[196,1980] *= 1.0078125` | 7,11 | −.063835 |
| **`Q[52] *= 1.5`** | **8,13** | **−.062252** |
| `Q[52] *= 2` | 9 | −.065063 |
| `Q[[24,212,30,225,49,33,21,52]] *= 1.25` | 10 | −.065453 |

Rationale: test sparse attention discrimination, then context retention through the largest inspected layer-12 decay proxy, followed by magnitude/support-width controls. These mechanisms remain hypotheses.

The near-Gold control changed one smallest-magnitude nonzero M entry, with L2 **9.095×10⁻¹³**; it is **not exact Gold**.

## Limits and failures

- **15/30 dev passes**, **17/200 sandbox calls**, approximately **602 seconds**.
- Initial exploration used 12 passes. Three additional repeats were justified when the initially preferred candidate failed to reproduce its advantage.
- Failures retained: one sandbox tensor-export error; refused null-baseline evaluation; refused unchanged-Gold submission.
- Evaluator tokens: **78,763,517 prompt**, **1,339,989 generated**.
- Parent-token count was not exposed by lab.
- Every submitted evaluation finished before sealing. No select/test/transfer results were requested.
