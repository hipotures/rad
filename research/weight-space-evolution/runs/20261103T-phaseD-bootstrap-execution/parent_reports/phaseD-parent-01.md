## Sealed candidate

**`p-a1a9a0be281a`**, irrevocably sealed. Lineage: **Gold → candidate**, with no imported patches.

**Result: reduced harm, not broad useful repair.** All submitted evaluations finished before sealing.

### Exact winning recipe

After `reset()`, use absolute Gold tensors from layer 11:
```python
p = 'model.language_model.layers.11.mlp.'
g = gold(p+'gate_proj.weight')
u = gold(p+'up_proj.weight')
d = gold(p+'down_proj.weight')
s = (np.sqrt(np.mean(g*g, axis=1))
   * np.sqrt(np.mean(u*u, axis=1))
   * np.sqrt(np.mean(d*d, axis=0)))
idx = np.argsort(s)[-36:]
w = d.copy()
w[:, idx] *= 0.9
save(p+'down_proj.weight', w)
```
Broker-rounded to BF16: **36,864 changed entries**, delta L2 **0.2134277144**.

Initial projection statistics showed heterogeneous channel norms. The tested hypothesis was that attenuating high static-gain MLP channels could improve precision; no activation-level mechanism was established.

### Dev evidence

Cell-count-weighted results across all four families and tiers:

| Metric | Near-Gold control¹ | Sealed |
|---|---:|---:|
| Mean recovery | −0.121904 | **−0.115513** |
| Regression rate | 31.07% | **30.53%** |
| Effective T2/T2P repairs | 0/832 | **0/832** |

Sealed mean recovery by family:

| Family | T0 | T1 | T2 | T2P |
|---|---:|---:|---:|---:|
| F1 | −.762775 | −.197987 | −.132525 | −.079866 |
| F2 | .172196 | −.168852 | −.018957 | −.012785 |
| F3 | .082535 | −.086607 | −.036590 | −.023428 |
| F4 | −.050516 | −.249992 | −.145247 | −.040489 |

Regressions versus control remain: F1 T1/T2 recovery worsened, F3 T2P worsened, and F2 T2 regression rate increased by 1.04 percentage points. No held-out or select evidence was accessed.

### Complete numerical search record

Define **H(layer, k, factor)** as the winning recipe above with those substitutions. Every proposal independently started from Gold using `reset()`.

| Pass | Recipe | Mean recovery |
|---|---|---:|
| 1 | H(23,36,.9) | −.124667 |
| 2 | Near-Gold control¹ | −.121904 |
| 3 | H(23,36,1.1) | −.119135 |
| **4** | **H(11,36,.9)** | **−.115513** |
| 5 | Layer23 down/o projections clipped elementwise to ±6×Gold column RMS | −.123576 |
| 6 | H(11,36,.75) | −.122488 |
| 7 | H(11,36,.9) + H(23,36,1.1) | −.117561 |
| 8 | H(23,36,1.5) | −.123120 |
| 9 | Layers15/19/23 q_norm: top64 `argsort(abs(Gold))` coordinates ×1.1 | −.115875 |
| 10 | Same q_norm coordinates ×.9 | −.129251 |
| 11 | H(11,36,.95) | −.120453 |
| 12 | H(11,358,.9) | −.117203 |

¹Layer23 `mlp.down_proj.weight[0,0] += 2**-14`; actual BF16 delta was `2**-13`. **Not an exact Gold baseline.**

Failures retained: initial statistics call referenced unexported tensors; `evaluate(null)` was refused; unchanged-Gold identity submission was refused. Clipping improved validity but worsened open-ended recovery. Amplification/query variants yielded isolated effective cases, not broad capability.

### Resources

- **12/30** dev passes; **19/200** sandbox calls.
- Elapsed: approximately **6.6 minutes**.
- Evaluator tokens: **63,009,110 prompt**, **1,073,250 generated**.
- Parent-token count was not exposed by lab; externally recorded.
- No gradients, training, optimizer fitting, prohibited tensor edits, or unmetered inference.
