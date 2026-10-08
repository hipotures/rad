# Regular-phase Laurent inverse: a reusable analytic candidate

Status: written analytic interface and parameter mechanism. The weighted
Laurent estimate below is proved directly. A complete fixed-tape multiplication
composition is not supplied. In particular, the required fast acquisition of
shifted boxes or sparse exceptional patches remains open.

## Weighted Laurent inversion away from a phase edge

Let `u=alpha^2`, `rho=1+theta`, and consider one wrap-free physical phase cell.
With a recentring coordinate `c` and `beta=beta_c`, its exact correction matrix
has entries `N_ij=D_i t_(j-i) D_j^-1`, where

```
D_j=exp(pi*u*theta*(j-c)^2),
t_h=exp(-pi*u*(rho*h^2+2*beta*h)).
```

Assume `|beta| <= 1/2-delta` for `delta>0`. For every nonzero integer `h`,

```
rho*h^2+2*beta*h
 >= (2*delta+theta)*|h|+rho*|h|*(|h|-1).
```

Define the weighted convolution norm
`||a||_A=sum_h |a_h| exp(A*|h|)` with `A=pi*u*delta`. It is
submultiplicative because `|h+k|<=|h|+|k|`. Writing `t=e_0+e`,

```
||e||_A <= 2/(exp(pi*u*delta)-1) = r_A.
```

If `r_A<1`, the absolutely convergent Laurent Neumann series
`b=sum_(k>=0)(-e)^*k` is a two-sided convolution inverse and
`||b||_A<=1/(1-r_A)`. Hence

```
sum_(|h|>R)|b_h| <= exp(-A*R)/(1-r_A).
```

This is a general inverse-kernel lemma, not a forward-bandwidth heuristic.
At `u*delta>=1`, using `pi>3` and `exp(3)>16` gives `r_A<2/15<1/2`,
so the denominator can conservatively be replaced by two.

The same weighted row-norm argument applies to every finite principal Toeplitz
block: weighting rows and columns by `exp(A*j)` or `exp(-A*j)` yields the
corresponding directional decay. A local principal inverse and the Laurent
inverse agree in core rows up to boundary residuals. Those residuals must be
charged; agreement of the symbols alone is insufficient.

## A conservative local-interface estimate

First truncate the exact Gaussian matrix at a width whose omitted row norm is
`eta`, obtaining `H`. Suppose `H` has gap `mu>0`, row norm at most two, and a
local window `I` stays inside the same physical phase cell. Its principal
matrix is `A_I=D T_I D^-1`. Let `B_D=log(max D/min D)`, and let the retained
core be at least distance `R` from the boundary support of `H_I,I^c`.

Weighted principal-inverse decay bounds a core-to-boundary row sum by
`2 exp(B_D-A*R)` when `r_A<1/2`. The exact global/local resolvent identity is

```
(H^-1 x)_I - A_I^-1 x_I
  = -A_I^-1 H_I,I^c (H^-1 x)_I^c.
```

Its core error is at most
`4 mu^-1 exp(B_D-A*R)||x||_infinity`. The term from replacing `N` by `H`
is at most `eta*||N^-1||*||H^-1||*||x||`, provided the perturbation is below
the retained gap. This explicitly separates the Gaussian tail, local boundary
residual and Laurent-kernel truncation.

Applying the truncated Laurent kernel to a zero extension of `x_I`, then
restricting to `I`, also induces a boundary residual. Scaling by `D` and `D^-1`
gives a conservative additional constant times
`mu^-1 exp(2B_D-A*R)||x||`. Therefore a sufficient radius is

```
R >= [Q*ln(2)+2B_D+ln(C*d/mu)]/(pi*u*delta),
```

with a fixed sufficiently large `C`, plus the physical truncation width.
The exact constant is not promoted here; the exponent mechanism follows from
this proved dependence. A complete implementation must specify the precise
rounding and boundary constants before an exact certificate is accepted.

## Full-tensor precision is a separate constraint

For `d` axes, diagonal scaling is `D_tensor=product_i D_i`. Its reserve is
the **sum** `sum_i B_(D,i)`. A per-axis statement `B_(D,i)=O(Q)` does not
show that a packed tensor convolution uses `O(Q)` bits; it can require `dQ`.
A sufficient uniform condition for core side `lambda` is

```
d*u*theta*lambda^2 = O(Q).
```

The input scaling can be chosen to contract. Tensor diagonal values are
constructive products of one-dimensional vectors and can be generated in a
recursion whose total output volume is dominated by its last level. The sum
of partial product counts is `O(lambda^d)` for `lambda>=2`, rather than
`d*lambda^d`. One local tensor diagonal page can be reused across boxes with
the same shape and axis parameters. This avoids a hidden per-coefficient
`d` factor in computing the weights.

If all exact normalized one-axis maps are contractions, tensor replacement
error is bounded by the sum of their individual errors. Alternatively, choose
`u*theta` eventually larger than a fixed multiple of `log d`; then the retained
global `N=I+E` estimate gives `d*||E||=o(1)`, so the tensor norms are bounded
by a constant. Neither condition follows from dimensionality alone.

## Regular/exception parameter mechanism

Let `delta=d^-B` and `u=Theta(Q/d)`. The regular radius is
`R=O(d/delta)`. With direct halo replication, take
`lambda=Theta(d^2/delta)` and `theta=Theta(delta^2/d^4)`. Then

```
d*R/lambda=O(1),
d*u*theta*lambda^2=O(Q),
u*theta=Theta(Q*delta^2/d^5).
```

Long digits with `Q=d^(5+2B+zeta)` for any fixed `zeta>0` make the last
quantity grow. The price is larger digit precision; `TQ=Theta(n)` still holds
after the digit split is changed consistently. This is compatible with
`epsilon<1` because the axis length remains exponential in
`b^(1-epsilon)` while these local parameters are polynomial in `b`.

To reduce uniform-grid boundary density to `O(1/d)`, take instead
`lambda=Theta(d^3/delta)`, `theta=Theta(delta^2/d^6)`, and
`Q=d^(7+2B+zeta)`. The resulting regular halo ratio is
`dR/lambda=O(1/d)` and the full-tensor chirp reserve is again `O(Q)`.
Constant shifted grids may repair most local face errors, but their movement
and residual sparse access are not yet proved.

Near `|beta|=1/2`, the regular estimate is unavailable. Such phases occupy
`O(delta)` of an axis. A physical inverse window can require
`R_exception=Theta(sqrt(Q/(u*theta)))`, while an exceptional pocket has
length `Theta(delta/theta)`. For the second parameter choice,

```
R_exception=Theta(d^(7/2)/delta),
exception pocket length=Theta(d^6/delta),
R_exception/lambda=Theta(sqrt(d)).
```

If only rare exceptional fields are enlarged, the one-axis volume increment
is `O(delta*sqrt(d))`; the replicated tensor volume remains bounded when
`d^(3/2)*delta=O(1)`. Choosing `B>5/2` even leaves the idealized enlarged
exceptional volume small enough for an extra `d` factor of arithmetic. This
last counting statement does **not** prove a sparse fixed-tape access bound.

## Unresolved algorithmic barrier

The completed bulk inverse assembles halos in `d` full-volume passes. Reusing
that assembly preserves the `O(Vd)` row even if local arithmetic becomes one
recursive multiplication. An arbitrary binary coordinate router also does
not grant an arbitrary nonlinear duplicated-key sort. Fast acquisition of
all halo boxes, true globally shifted boxes, or physically contiguous sparse
repair patches needs a new paid tape schedule. No improved end-to-end
`kappa` is claimed until that schedule and all surviving rows are supplied.

Attribution: the exact recentred Gaussian factorization is from Swapnil Jain's
public segmented-inverse note pinned above; the complete phase-cell/local
boundary transfer and semantic exact-child guard are from completed RaD
research. The weighted Laurent estimate is derived here directly. The scout
independently suggested its same weighted-Banach argument during this CPU
campaign. No worldwide novelty or external peer-review claim is made.
