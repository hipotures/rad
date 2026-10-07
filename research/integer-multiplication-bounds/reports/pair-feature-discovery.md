# Pair-feature fitting-matrix discovery

This bounded numerical branch found no new low-rank fitting matrix. It
provides a smaller exact affine ansatz, calibrated CPU/GPU projections,
and a known reduced-rank positive control. A floating low-rank fitting
matrix would still require an exact rational lift and a separate rational
label/frame and multiplication transfer; none is claimed here.

## Exact ansatz

For source and target triples `S,T` on an `h>=6` ground, put
`M(S,T)=sum_{ab subset S} b_ab,T`. Requiring zero when
`|S intersect T|=1` gives, for `i in T` and `a,b outside T`,

```text
b_ab + b_ia + b_ib = 0.
```

Subtract the equations for two inside points. At least three outside
points force their cross-coefficient differences to vanish. Therefore
there are values `u_a` such that every cross coefficient is `b_ia=u_a`
and every outside coefficient is `b_ab=-u_a-u_b`. The three inside
coefficients are arbitrary subject to their sum being one, enforcing
`M(T,T)=1`. These conditions characterize the whole pair-feature ansatz.

Let `k=h-3` and, for an outside point `a`, define
`r_a=sum_{i in T} b_ia-sum_{b outside T,b!=a} b_ab`.
The Euclidean nearest affine projection has

```text
u_a = r_a/(k+1) - sum_b r_b/((k+1)(2k+1)),
w_ab = b_ab + (1-sum_inside b)/3          for ab subset T.
```

The cross/outside formulas above reconstruct the projected column.
An independent dense least-squares solve checks this projection on all
twenty `h=6` target columns and verifies every required zero and diagonal
constraint. CPU and both GPU projections and spectral rank truncations
also agree within their recorded tolerances.

The exact known matrix

```text
b_ab,T = (3*(1_T(a)+1_T(b))-2)/12,
M(S,T) = (|S intersect T|-1)/2
```

belongs to the ansatz. Its coefficient matrix has rank `h` when `h!=9`,
and rank eight at `h=9`: the constant vertex mode vanishes there. The
rank-eight `h=9` fixture is only a numerical positive control. Its ambient
form is degenerate and it does not satisfy the retained motif transfer.

## Bounded numerical evidence

The new [search source](../code/pair_feature_search.py) alternates the
exact affine projection with a floating spectral low-rank projection,
or uses the Douglas-Rachford update. Both methods are discovery
heuristics. Seed 109 and noise standard deviation .05 were declared.

| Case | Method | Iteration cap / outcome | Best maximum rank residual |
|---|---|---|---:|
| h6, rank6 CPU exact baseline | Douglas-Rachford | Control passes immediately | 3.89e-16 |
| h8, rank8 exact baseline, both GPUs | Douglas-Rachford | Controls pass immediately | 4.72e-16 |
| h9, rank8, perturbed known fixture | Douglas-Rachford | Iteration 175, control recovered | 3.40e-12 |
| h8, rank7 | Douglas-Rachford | 2,000 cap; tolerance not reached | .036001 |
| h24, rank23 | Douglas-Rachford | 2,000 cap; tolerance not reached | .217435 |
| h24, rank23 | Alternating | 2,000 cap; tolerance not reached | .080289 |

The h24 runs took approximately fifteen wall seconds each, on different
GPUs, with peak host RSS below 702 MiB per process. The affine candidate
always satisfies the fitted zero/diagonal constraints to rounding error;
the reported residual measures the remaining distance from rank 23.
Iteration indices start at zero; each command's cap is its final index.
An unsuccessful run implies no nonexistence or lower-bound theorem.
The alternating residual was still improving at the declared cap, so
the bounded failure does not establish stagnation.

Compact summaries, all checked tolerances, exact source hashes and
iteration histories are retained. Best coefficient NPZ files remain
external, with sizes/hashes and deterministic-seed recovery instructions;
identical floating bytes across GPU/runtime versions are not promised.
No failed numerical matrix is promoted to an accepted label certificate.
