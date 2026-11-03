## Sealed candidate

**`p-f6dc81f3da9a`**
Complete lineage: **Gold → sealed patch**, with no imported patches.

**Outcome: reduced harm, not demonstrated useful repair.** The null hypothesis remains unrefuted.

### Exact numerical recipe

Starting from `reset()`, for each layer in `[8,9,10,12,13,14]`:

```python
n = f"model.language_model.layers.{layer}.linear_attn.dt_bias"
a = gold(n).copy()
mask = (a > -5) & (a < -1)
a[mask] -= 0.125
save(n, a)
```

Absolute values were validated and rounded to BF16 by the broker. **64 changed entries across six tensors; ΔL2 = 0.998289553.** Hypothesis: slightly less linear-attention decay could improve retention of numerical evidence.

## Dev evidence

Selected candidate’s mean recovery:

| Family | T0 | T1 | T2 | T2P |
|---|---:|---:|---:|---:|
| F1 | −0.72647 | −0.19054 | −0.11413 | −0.06774 |
| F2 | +0.17216 | −0.16137 | −0.02946 | −0.02856 |
| F3 | +0.07774 | −0.04310 | −0.05335 | −0.02945 |
| F4 | −0.05052 | −0.25022 | −0.14158 | −0.06251 |

- Equal-cell mean recovery: **−0.106194**, versus **−0.114890** for the near-null control.
- T2/T2P mean recovery: **−0.065848**, versus **−0.066151**.
- **Zero effective or full T2/T2P repairs.**
- T2/T2P regression rates respectively: F1 **27.34% / 22.66%**, F2 **14.58% / 16.67%**, F3 **20.31% / 19.53%**, F4 **15.63% / 7.81%**.
- Recovery worsened versus near-null on F2/T2P, F3/T2, F3/T2P and F4/T2P, among other cells. No true Gold comparison was available.

## Search and counterfactuals

All recipes start independently at Gold; masks use Gold values.

- **N(s):** layer23 post-attention norm, largest32 coordinates, `w += s*(1+w)`.
- **Q(s,L):** q-norm, largest64 coordinates per layer in `L`, same formula.
- **D(s):** selected dt-bias mask above, `w += s`.

| Pass | Recipe | Mean recovery |
|---|---|---:|
| 1 | N(−.02) | −.109788 |
| 2 | N(+.02) | −.112100 |
| 3 | Near-null: norm23 `[0] += .0009765625` | −.114890 |
| 4 | Q(+.04, `[3,7,11,15,19,23]`) | −.117663 |
| **5** | **D(−.125), sealed** | **−.106194** |
| 6 | Q(−.04, same layers) | −.114554 |
| 7 | D(+.125) | −.109247 |
| 8 | N(−.10) | −.113635 |
| 9 | Q(+.04, `[19,23]`) | −.108006 |
| 10 | N(+.10) | −.117759 |
| 11 | D(−.375) | −.113375 |
| 12 | D(−.125) + N(−.02) | −.112587 |

Signed counterfactuals, amplitude tests, localization and composition did **not** establish broad useful repair.

**Failures retained:** null/Gold evaluation requests and empty/identity submissions were refused; one sandbox inspection failed because its Gold tensors were not exported. Recipes, rationales and returned per-cell results remain in the run record.

## Resources

- **12/30 dev passes; 23/200 sandbox calls**, including the failed run.
- **Elapsed: 894 seconds**.
- Evaluator tokens: **63,008,458 prompt; 1,071,571 generated**.
- Parent-token count was not exposed by lab.
- Every submitted evaluation finished before sealing. No select/test/transfer feedback was requested.
