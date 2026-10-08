# Tensor packing and regular-phase inverse: status and elementary discriminator

## Status

This is a campaign hypothesis and a scoped mathematical lemma, not a completed multiplication composition. The scout proposed packing all axes of a local Gaussian/Laurent convolution into one Kronecker product. The inverse and layout agents are investigating numerical boundaries, exceptional phases and actual fixed-tape routing. The proposed application is distinct from reproducing the public one-axis segmented inverse. Kronecker substitution, Laurent inversion, weighted sequence algebras and decay of inverse matrices are classical tools; no priority is claimed for them.

## Why packing could change an analytic row

Let a local core have side `lambda=poly(log n)` and growing dimension `d=(log n)^epsilon`, with fixed `epsilon<1`. A tensor kernel of coordinate radius R can be encoded in a mixed-radix polynomial and multiplied with the input core. The complete convolution needs radix at least `lambda+4R` if the input includes its halo. The packed bit size is

`S=O(p*(lambda+4R)^d)`.

This is `n^o(1)` for polynomial p, lambda and R. The volume ratio is controlled only when

`((lambda+4R)/lambda)^d <= exp(4dR/lambda)=O(1)`.

Polynomial side lengths alone do not establish this. In particular, R comparable to lambda gives exponential replication in d and invalidates the route.

If the tensor product is genuinely a bounded-precision Laurent convolution and total child sizes sum to `O(n)`, recursively calling a multiplication routine on these strictly smaller children would charge

`O(n*(log S)^(1-kappa)) = O(n*(log n)^(epsilon*(1-kappa)+o(1)))`.

Its exponent is strictly below `1-kappa` for every fixed `epsilon<1`. This is the incentive for investigating the construction. It does not remove the separate prefix, physical routing, CRT alignment or exceptional-boundary rows automatically. A recursive call must be part of a proved terminating recurrence, not a free oracle for the desired bound.

## A regular-phase Laurent truncation lemma

Set `u=alpha^2`, `sigma=1+theta`, and assume `|beta| <= 1/2-delta`, where `delta>0`. The wrap-free Toeplitz symbol has coefficients

`t_h = exp(-pi*u*(sigma*h^2+2*beta*h))`, with `t_0=1`.

For every nonzero integer h,

`sigma*h^2+2*beta*h >= (theta+2*delta)*|h| + sigma*|h|*(|h|-1)`.

Use the weighted convolution norm `||v||_A=sum_h |v_h| exp(A|h|)` with `A=pi*u*delta`. The triangle inequality on integer indices makes this norm submultiplicative. Consequently

`rho = ||t-1||_A <= 2/(exp(pi*u*delta)-1)`.

When rho is below one, the inverse coefficients `b=(1+(t-1))^-1` exist by the norm-convergent Neumann series. They satisfy

`||b||_A <= 1/(1-rho)` and `sum_|h|>R |b_h| <= exp(-A*R)/(1-rho)`.

This directly gives an inverse-window estimate without relying on numerical Gohberg–Semencul stability. For d tensor factors, telescoping the difference of tensor products gives at most d times the one-axis tail multiplied by `(1-rho)^-(d-1)`. Require, for example, `rho<=1/(4d)` and include all physical chirp amplification and `log d` in the requested precision before selecting R.

The uniform claim at every phase is false without further work: at `|beta|=1/2`, the favorable factor delta disappears. A forward Gaussian window `O(sqrt(d))` does not justify the same inverse window. Nearest-neighbor paths in the inverse can require much longer truncation. This was reported promptly to the coordinator and inverse agent rather than silently using the forward window.

## Parameter compatibility proposed by the inverse agent

A regular/exception split uses `delta=d^-B`, `lambda=d^2/delta`, `theta=delta^2/d^4`, and `u=Q/d`, with sufficiently long digits, for instance `Q=d^(5+2B+zeta)` for fixed positive zeta. Up to fixed safety factors, the regular inverse window is `R=O(Q/(u*delta))=O(d/delta)`, so `dR/lambda=O(1)`. The combined d-axis chirp reserve is `d*u*theta*lambda^2=Q`, while `u*theta=d^zeta` grows. These algebraic compatibilities are encouraging, not a proof that the full machine meets its costs.

Near-edge phase pockets have coordinate density `O(delta)` and union density `O(d*delta)`. A claim that their cost is the density times a full one-axis cost still needs an actual sparse fixed-tape schedule and all dependency halos. It cannot be assumed from a RAM operation count. In particular, separately applying d operators to a masked array can still scan the entire array d times.

## Primary references and scope

- David Harvey and Joris van der Hoeven, [Integer multiplication in time O(n log n)](https://annals.math.princeton.edu/2021/193-2/p04), *Annals of Mathematics* 193 (2021), 563–617. Gaussian resampling and recursive short-convolution packing are prior foundations; this campaign does not claim to invent them.
- Martin H. Gutknecht and Marlis Hochbruck, [The Stability of Inversion Formulas for Toeplitz Matrices](https://people.math.ethz.ch/~mhg/pub/mhg-published/58-GutHoc95-LAA223-224.pdf), *Linear Algebra and Its Applications* 223/224 (1995), 307–324. Generic good conditioning of a Toeplitz matrix alone does not ensure stability of every Gohberg–Semencul evaluation. The relevant leading principal submatrix and division denominator must also be controlled. The public near-identity envelope permits a direct special-case repair: `||T-I||_infinity<0.087` implies `||T^-1-I||_infinity<0.087/0.913`, so the first generator entry is bounded away from zero.
- Stephen Demko, William F. Moss and Philip W. Smith, [Decay Rates for Inverses of Band Matrices](https://www.ams.org/mcom/1984-43-168/S0025-5718-1984-0758197-9/S0025-5718-1984-0758197-9.pdf), *Mathematics of Computation* 43 (1984), 491–499. Background on inverse decay; the weighted Laurent lemma above is proved directly for this special symbol and does not invoke a band-matrix theorem outside its hypotheses.
- David Harvey and Joris van der Hoeven, [Integer multiplication is at least as hard as matrix transposition](https://www.texmacs.org/joris/transpose/transpose.pdf), author-hosted current PDF accessed 2026-10-08. Its fixed-tape Bluestein/Kronecker machinery is relevant prior art for packing and address movement. The campaign has not verified a complete tensor-local application of it.

No direct quotations are used. The explicit lemma is elementary; primary references supply context, not a replacement for the missing composition proof.
