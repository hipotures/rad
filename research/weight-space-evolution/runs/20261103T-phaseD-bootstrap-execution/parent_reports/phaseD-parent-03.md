## Sealed candidate

**`p-41d9a0038798` (M100)**  
Complete lineage: **Gold → M100**, with `parent_id=null`. No imported patches.

**Outcome:** reduced aggregate harm, plus one reproducible full repair—not demonstrated broad repair capability.

### Exact winning recipe

```python
reset()
for layer in [0, 4, 8, 12, 16, 20]:
    n = f"model.language_model.layers.{layer}.linear_attn.dt_bias"
    x = gold(n).copy()
    mask = (x >= -5.0) & (x <= -1.0)
    x[mask] -= 1.0
    save(n, x)
```

Broker validation and BF16 rounding produced:
- **44 changed entries**
- **L2 delta:** `6.636915324119425`
- **Maximum absolute delta:** `1.015625`

Hypothesis: prolong intermediate recurrent memory to retain numerical evidence. No gradients, training, activation hooks, or prohibited tensors were used.

## Dev evidence

Exact-Gold evaluation was refused. The comparison is therefore a **near-Gold control**, changing layer-3 `self_attn.q_norm.weight[50]` from `-0.007049560546875` to `-0.00701904296875`.

Both M100 and control were evaluated twice; their respective dev summaries matched exactly.

| Metric | Control | M100 |
|---|---:|---:|
| Example-weighted mean recovery | −0.113748 | **−0.103243** |
| Macro mean recovery | −0.109891 | **−0.099635** |
| Overall regression rate | 30.65% | 30.77% |
| T2 effective repairs | 0/416 | **1/416** |
| T2P effective repairs | 0/416 | 0/416 |

M100 had the best mean recovery among tested candidates under both aggregations.

### Per-family mean recovery

| Family | T0 | T1 | T2 | T2P |
|---|---:|---:|---:|---:|
| F1 | −0.7306 | −0.1742 | −0.1403 | −0.0581 |
| F2 | 0.2032 | −0.1514 | −0.0105 | −0.0143 |
| F3 | 0.0821 | −0.0427 | −0.0264 | −0.0135 |
| F4 | −0.0727 | −0.2443 | −0.1416 | −0.0589 |

The single T2 repair was a **full F3 repair**. T1 yielded three full F2 repairs and one effective-but-not-full F3 repair. No other T2/T2P cells showed effective repair.

Important regressions:
- T2 regression rate increased from **20.91% to 21.63%**.
- T2P regression rate increased from **15.14% to 16.11%**.
- T2P mean recovery worsened from **−0.029864 to −0.034401**.

Thus, aggregate harm reduction must not be interpreted as reliable independent editing or feedback-based repair.

## Experiment recipes and outcomes

Every candidate independently started from Gold using `reset()`.

Definitions:
- **Q:** `self_attn.q_norm.weight`, layers `[3,7,11,15,19,23]`
- **L:** same tensor, layers `[11,15,19,23]`
- **D:** winning recipe’s six `dt_bias` tensors
- **R:** `mlp.down_proj.weight`, layers `[7,11,15,19]`
- `m = median(x)`
- For R, `rᵢ = L2(row i)` and `t = 1.5 × median(r)`; only rows with `rᵢ > t` change.

| Candidate | Exact intervention | Macro recovery |
|---|---|---:|
| Q10 | Q: `x − .10(x−m)` | −0.114499 |
| Q−10 | Q: `x + .10(x−m)` | −0.111744 |
| Control | One-coordinate change specified above | −0.109891 |
| M25 | D: subtract `.25` where Gold is in `[-5,-1]` | −0.105810 |
| R5 | R: multiply selected rows by `1−.05(1−t/rᵢ)` | −0.117162 |
| S20 | L: add `.20` where Gold `x>m` | −0.113561 |
| S−20 | L: subtract `.20` where Gold `x>m` | −0.108489 |
| **M100** | D: subtract `1.0` on the same mask | **−0.099635** |
| R−10 | R: multiply selected rows by `1+.10(1−t/rᵢ)` | −0.112103 |
| M50 | D: subtract `.50` on the same mask | −0.111981 |
| M200 | D: subtract `2.0` on the same mask | −0.105783 |
| MSlate | M100 plus S−20 restricted to layers `[19,23]` | −0.100604 |

Query calibration tested retrieval specificity versus distraction. MLP row interventions tested whether a consistent residual-channel outlier was disruptive or functional. Neither established broad repair improvements.

## Failures and resources

Retained failures:
1. Null-patch evaluation refused.
2. Gold inspection without explicit tensor exports failed.
3. Empty baseline submission refused.
4. Ten-tensor combined proposal refused; replaced by a reset eight-tensor proposal.
5. Seal request containing rationale refused; patch-only seal succeeded.

Resources:
- **14/30 full dev passes**, including two confirmation repeats
- **26/200 sandbox calls**, including the failed run
- Approximately **18 minutes** elapsed
- Evaluator totals: **73,503,430 prompt tokens**, **1,222,197 generated tokens**
- Parent-token accounting was not exposed through lab; no estimate is substituted.

All submitted evaluations finished before sealing. **M100 is sealed; no select feedback was requested or received.**
