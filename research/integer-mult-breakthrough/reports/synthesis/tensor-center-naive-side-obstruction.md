# Product fitting center: naive side stock obstruction

The fitting kernel `K tensor K` permits a center-only component whose
closed full-width loss is `2q^2 h^2`. A separate dirty helper for every
nonzero entry of `I-K tensor K` makes that candidate fail the target for
every supported h. This is a scoped all-size obstruction; it does not
exclude shared side channels or a joint signed exchange.

For the five-subset kernel `K(t)=(t-1)(t-3)/8`, put

```text
v=C(h,5), q=C(h,2), N=v^2, m=h^2.
```

The tensor labels `s tensor t` have odd norm. If a distinct pair is
nonorthogonal, both base intersections are odd and at least one is a
distinct odd intersection. Its product coefficient vanishes. The
diagonal is1, so `K tensor K` has the required fitting zero pattern.
An invertible center basis `B tensor B` on N existing helpers and decoder
`D tensor D` gives the same early/late exact dirty echo as the one-axis
component, with `q^2` features. Its center-only rank is
`3Nm-2N+2q^2m`. All source/sink/dirty address operators and native scalar
gates would still need binding in a complete larger architecture.

The number of nonzero base K coefficients in each row is

```text
c(h)=C(h-5,5)+10C(h-5,3)+5(h-5)+1.
```

The product side has exactly `c(h)^2-1` nonzero entries per target. One
helper per entry therefore requires `M=N(c(h)^2-1)` side helpers and
`W=3N+M`. This grows as `O(v^4)`. No such graph or helper stock was
allocated for the preflight.

For a geodesic side helper that enters through its source line and meets
a sink at dimension d, the child widths are `1,d-1,m-d`. Concavity of
`r^(1-b)` for `0<b<1` shows that its moment is at least
`1+(m-1)^(1-b)`: concentrating the remaining rank into one child is
optimistic. Likewise combine each source/sink endpoint path into a
single `m-1` child. Retain every center helper entrance and the closed
feature release. The resulting **lower** moment profile is

| Width | Multiplicity |
| --- | ---: |
| 1 | `N+M` |
| m-1 | `3N+M` |
| m | `2q^2` |

Its rank is `Wm-2N+2q^2m`. It is a lower bound for this declared
chronology, not an attained improved profile.

For supported `7<=h<=12`, the center deficit is nonpositive because
`v<=qh`. For every `h>=13`, `c(h)>=c(13)=657`, `m>=169` and `ln(m)>1`.
The inequality `exp(z)>=1+z`, applied just to the M mandatory width-one
helper calls, gives the normalized moment

```text
Phi(b) >= 1 + [b M ln(m)-2N+2q^2m]/(Wm).
```

At `b=1/10000`, the sufficient positive numerator margin per N is

```text
b(657^2-1)-2 = 25728/625 > 0.
```

Therefore the target fails for all `h>=13`, even under the optimistic
profile. The smaller h cases cannot have a positive saving either. This
excludes a numerical sweep or enormous product-side allocation as a
useful next experiment under these premises.

[tensor_center_side_preflight.py](../../code/synthesis/tensor_center_side_preflight.py)
checks the integer identities, exact outward `ln(169)>1` and strict
moment exclusion on h13,16,20. The
[actual-time run](../../runs/20261009T015057Z-synthesis-tensor-side-preflight/report.md)
preserves the two-file stdlib source closure and immutable complete
arithmetic receipt. C independently accepted the analytic/source argument;
its separate receipt is owned by the transfers track.

Reproduce from the worktree root:

```bash
python3 research/integer-mult-breakthrough/code/synthesis/tensor_center_side_preflight.py \
  --output research/integer-mult-breakthrough/work/synthesis/<fresh-actual-UTC>-tensor-side-preflight/results
```

Shared/factorized side helpers, changed center release endpoints, a joint
signed exchange and different transfer architectures remain open. No
universal multiplier bound or new kappa is claimed.
