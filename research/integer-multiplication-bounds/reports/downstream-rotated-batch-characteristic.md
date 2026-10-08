# Exact characteristics after a fixed tensor-axis choice

The accepted h51 R502265 bit network supports the strict primitive saving

`a=7995388610243433/10^24`

when one fixed tensor-axis choice exposes the middle and data residuals as
contiguous tensor blocks. This is a changed interchange construction. It
does not re-round the earlier uniform-rank estimate. The scalar graph,
physical roles and complementary rational frame ranks are unchanged.

The [producer](../code/downstream_rotated_batch_characteristic.py) chooses
the ambient basis order `(3,1,2)` before constructing every source, gate,
sink and canonical lower/lower Bruhat table. Simultaneous conjugation
preserves the complete common-frame shear on arbitrary payloads and dirty
scratch. It requires a new fixed rational factor table and potentially a
new fixed odd prime. No array-level basis adapter or arbitrary pivot
gather is inserted during execution. The separate h28 complex network and
its numerical precision guard retain their accepted definitions.

The [independent full transfer](review-global-axis-batching.md) proves
complete frame conjugation, the new fixed-prime scope, the tensor profiles,
componentwise arithmetic, constant-field tail handling and fixed-tape row
transfer. The [independent witness audit](review-global-axis-witnesses.md)
also accepts the explicit producer certificates, using independently
reconstructed moments and a positive-exponential characteristic bound.

Write `C=(R+h)*v^2`, `m=h^3` and `N=v^3`. The rotated middle residual is
`(I-P_t) tensor I_(h^2)`. All `h-1` base pivots, including its offdiagonal
block, lift to increasing contiguous children of width `h^2`. Its exact
rank-log moment is

`M_middle=C*h^2*(h-1)*log(h^2)`.

Joined residuals keep rank `m-2h`. The universal projection profile has
at least `m-4h` diagonal pivots in at most `4h+1` runs. The rotated protected
kernel `F tensor t_B tensor t_piA` supplies equally spaced forbidden
pivot columns, so their maximum run is `h^2-1`. Thus the uncapped joined
moment lower bound remains

`M_joined=C*(m-4h)*log((m-4h)/(4h+1))`.

The disjoint X stage3 `in->2` and Y stage3 `0->1` data families become
`(I-P_t3) tensor (I-(P_t1 tensor P_t2))`. Their canonical partial
permutation is the Kronecker product of the two rank-one-complement
profiles. For `k=h*a+b`, the suffix run lengths are the positive members
of `k, h^2-k-2, 1`, each repeated for every base pivot. With
`f(a)=C(h-a-1,2)`, the exact rank-log moment is

```text
M_data=2*v*(h-1)*sum_(a,b) f(a)*f(b)*[
    k*log(k)+(h^2-k-2)*log(h^2-k-2)].
```

The singleton has zero logarithm and zero-length terms are omitted. The
histogram rank sum is exactly `2*N*(h-1)*(h^2-1)`. All other pivots remain
individual children. Every child has rank at most `h^2`, so
`r*floor(e/m)<=e/h` and recursion depth is at most `ceil(log_h(e))`.

The total original rank sum is unchanged:

```text
W=453752231686250
s=60190685022033566875
D=W*m-s=2263379181875.
```

The producer encloses integer logarithms using exact rational series, then
rounds each endpoint outward onto the common dyadic denominator `2^256`.
This controls the size of the many-log tensor sum while retaining the
required inequality direction. For `L=log(m)_upper` and proved moment
lower bound `M`, its direct negative-exponential certificate is

`D-a*(W*m*L-M)-a^2*s*L^2/2>0`.

This follows from `exp(-x)>=1-x` and
`exp(-x)<=1-x+x^2/2` for every `x>=0`. It proves the strict grouped
characteristic `sum n_r*r^(1-a)<W*m^(1-a)` without substituting the old
uniform formula `1-log_m(s/W)`. A 96-step rational root bracket and a
downward `10^-24` grid choice are retained. No floating-point value enters
the threshold checks.

| Included physical families | Explicit producer a |
|---|---:|
| Rotated middle and joined | 7532289379611821/10^24 |
| Above plus universal data bound | 7720142940501247/10^24 |
| Above plus exact tensor data profiles | 7995388610243433/10^24 |

The universal-data row uses its replacement protected kernel, rather than
carrying the old third-axis holes across the basis cycle. Its explicit
witness has now passed the separate independent audit. The complete
assembly currently composes only the two-family and exact-tensor rows.

The [completed run](../runs/20261008T050504Z-downstream-rotated-batch-characteristic/protocol.json)
pins the independently accepted h51 finite input and all commands. Source
SHA256 is `5eb3a76b1670b414aa743922960c6cefacca2442af881eca610dfd79bc242f98`;
the 85,675-byte [certificate](../runs/20261008T050504Z-downstream-rotated-batch-characteristic/results/certificate.json)
has SHA256 `6d9bc88013f87e4f997ff44fe66ad95ffbde522412610d04e78c4944ff664705`.
The frozen producer's prospective status records its execution-time
review state; the later independent reviews supply the accepted transfer.

No numerical value of the giant new native factor table or odd prime is
claimed. Their deterministic fixed-program construction is an eventual
setup obligation, as in the original primitive. The fresh composed
assembly retains that obligation and the changed setup constant explicitly.
The original campaign start and historical deadline remain intact, with
the user's extension to 2026-10-08 10:00 UTC recorded in new protocols.
