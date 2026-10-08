# Regular-phase Laurent inverse: a reusable analytic candidate

Status: written analytic interface and parameter mechanism. The weighted
Laurent estimate below is proved directly. This report owns the local analytic
interface; the coordinating agent now supplies the separate
[conditional full composition](../../../reports/conditional-composition.md),
including shifted-box acquisition and sparse exceptional access. The earlier
barriers below record the obligations that motivated those later schedules.

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

### Sharper finite regular-phase radius

For local numerical controls a stronger weight is useful. Assume `u*rho>=1`
and define `A_star=pi*u*(rho-2*abs(beta))-ln(4)`. If `A_star>0`, then

```
|t_h|*exp(A_star*|h|)
 <=4^(-|h|)*exp[-pi*u*rho*|h|*(|h|-1)],  h!=0.
```

The weighted perturbation norm is at most
`2*sum_(h>=1)4^-h*exp[-pi*u*rho*h*(h-1)]<2/3`.
Indeed the first term is1/2 and the entire remaining tail is below1/1536
using `pi>3` and `exp(6)>256`. Therefore its inverse norm is below three,
and the infinite inverse kernel has tail at most `3*exp(-A_star*R)`.
This proof needs no near-identity physical-matrix condition `u*theta>=1`.
It applies only to a wrap-free stationary phase and a positive A_star;
it does not remove phase exceptions or a local window's boundary residual.

For `(s,t,u)=(4093,4096,4)`, beta0=0, maximum recentring distance64 and radius20, the illustrative
floating evaluations give `A_star≈11.19` and a one-axis full chirp reserve
`pi*u*theta*lambda^2≈37.73` nats, or54.43 bits. The conservative kernel
tail plus this full reserve is roughly267 bits. Thus a q256 local numerical
control is plausible with these parameters, provided its additional finite
kernel, rounding and boundary budgets are included. These parameters have
`u*theta<1` and do NOT instantiate the campaign's all-size near-I regime.
The actual origin beta, rather than beta0=0 for every cell, must be used.
For a core of length64 and20-position halos, recentring at the core midpoint
makes the maximum retained source distance52. A left-end origin would instead
reach distance84 and would require a larger chirp reserve. A recentred beta
must change with the chosen midpoint; these distances are not free phase
translations.

The unweighted inverse norm may be bounded separately by its exponentially
small regular perturbation. Selecting the stronger spatial weight above
does not alter the inverse-kernel L normalization described below.

The authored [kernel API](../code/regular_laurent_kernel.py) constructs the
infinite stationary inverse by a finite Neumann sum. Every intermediate
convolution support is retained through the last power; cropping occurs only
when emitting the final radius. Its receipt separates the omitted input
Gaussian band, the remaining Neumann powers and the final weighted inverse
tail. The phase beta is computed from integer periods and the actual origin.
Returned b_h acts from input column i+h to output row i; ordinary polynomial
convolution therefore uses b_-h.

An independent layout caller retained a first genuine two-dimensional signed
packed control in
[packed-laurent-inverse-initial-partial.json](../../layout/results/packed-laurent-inverse-initial-partial.json).
It uses source periods4093/4091, target4096, origins1364/818, core side64 and
radius28. Its complete retained input distances are[-60,59]; the SUM of both
axis chirp reserves is charged at128 bits. All4096 packed outputs agree with
the complete cyclic inverse reference to maximum error4.70e-126. Four global
reference vector solves retain independently recomputed residuals and all-
alias tails. Removing the output chirp produces error0.0312. The input is a
rank-two tensor, while the packed convolution actually processes every input
record and four signed integer products. This is high-precision numerical
evidence for one regular core, outside u*theta>=1; it is not an interval proof
or an all-size implementation. The receipt separately labels the global
phase-boundary replacement checked by its numerical oracle.

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

### Inverse-kernel normalization and prefix rounding

Individual inverse Laurent coefficients need not contract: even the central
coefficient can exceed one. To generate their tensor product constructively,
suppose each axis has the stronger eventual weighted bound
`r_(A,i)<=1/(4*d^2)`, which holds for the long-digit campaign parameters.
Then every coefficient obeys

```
|b_(i,h)| <= 1/(1-r_(A,i)) <= 1+1/d^2 = L.
```

Normalize each one-axis coefficient by the SAME rational `L=1+1/d^2`.
Its weighted coefficient l1 norm is also at most one, so the exact normalized
axis convolution contracts that norm. Generate tensor prefixes
by multiplying one normalized factor at a time, rounding to `P` fractional
bits and clamping to `[-1,1]` after each multiplication. Clamping preserves
the error bound because the exact normalized prefix lies in that interval.
For each output coefficient the propagated rounding error is at most
`d*2^-P`; the construction still uses `O(lambda^d)` multiplications in total,
not `d*lambda^d`, when each axis has at least two entries.

Restore the common scalar `L^d` once for the complete tensor kernel. For
`d>=2`, `L^d<=exp(1/d)<2`, so this requires one guard bit, not d independent
guard bits. Including the final scalar multiplication gives a coefficient
error bounded by `(2*d+1)*2^-P` before the separately charged chirp reserve.
For a generated tensor page with at most `lambda^d` coefficients, its total
unweighted coefficient error is at most
`lambda^d*(2*d+1)*2^-P`. Thus include
`d*ceil(log2 lambda)+ceil(log2(2*d+1))` guard bits in P before the separately
charged chirp reserve. This remains `O(Q)` for the campaign parameters.
Restoring the common scalar needs at most one additional scalar product
per generated coefficient, not d coefficient-generation passes.
The exact rational setup for `L^d` has `O(d*log d)` bits, which is below Q
under the campaign's `Q=Theta(d^18)` choice. Fixed-tape scalar setup and
rounded scalar multiplication must still be paid in their corresponding
rows. This normalization argument does not assume an exact denominator
of `dP` bits for every tensor prefix.

The common-L correction and its one-bit reserve were independently proposed
by the campaign scout on 2026-10-08. The forward Gaussian factors already
contract without this inverse-specific normalization.

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

These parameter examples enforce the inverse-specific locality and chirp
conditions only. The inherited source transform additionally needs
u^2*theta>=2Q. For the first theta choice that requires Q at least a fixed
multiple of d^(6+2B), and for the second it requires d^(8+2B). Thus the
displayed smaller powers with zeta<1 cannot be transferred unchanged to the
complete source algorithm. The later composition uses its separate
lambda_I=Theta(d^8), theta=Theta(d^-16), Q=Theta(d^18) choice and checks the
source condition explicitly.

## Historical algorithmic barrier and later resolution

The completed bulk inverse assembles halos in `d` full-volume passes. Reusing
that assembly preserves the `O(Vd)` row even if local arithmetic becomes one
recursive multiplication. An arbitrary binary coordinate router also does
not grant an arbitrary nonlinear duplicated-key sort. Fast acquisition of
all halo boxes, true globally shifted boxes, or physically contiguous sparse
repair patches needs a new paid tape schedule. This was an unresolved barrier
when the local mechanism was first written. The coordinating agent's linked
composition now supplies its joint scans, shifted grids and source-closed
repairs. Its multiplication claim and review status remain in that full
ledger; this local report alone does not supply them.

Attribution: the exact recentred Gaussian factorization is from Swapnil Jain's
public segmented-inverse note pinned above; the complete phase-cell/local
boundary transfer and semantic exact-child guard are from completed RaD
research. The weighted Laurent estimate is derived here directly. The scout
independently suggested its same weighted-Banach argument during this CPU
campaign. No worldwide novelty or external peer-review claim is made.
